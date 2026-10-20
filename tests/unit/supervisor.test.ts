import { afterEach, describe, expect, it } from 'vitest'
import { createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { EngineError, EngineSupervisor } from '../../apps/desktop/src/main/engine'
import { v2Registry } from '@ontolearn/contracts/v2'

const registryPath = resolve('packages/contracts/v2/registry.json')
const registryHash = createHash('sha256').update(readFileSync(registryPath)).digest('hex')
const limits = {
  startupMs: 1000,
  handshakeMs: 1000,
  requestMs: 1000,
  totalMs: 2000,
  heartbeatMs: 1000,
  cancelGraceMs: 1000,
  maxFrameBytes: 262144,
  maxQueuedJobs: 32,
  maxConcurrentJobs: 2,
  maxPageItems: 100,
  maxPageBytes: 131072,
  maxWorkerMemoryBytes: 536870912,
}
const source = `
const {createInterface}=require('node:readline');
const mode=process.argv[1], hash=process.argv[2], limits=JSON.parse(process.argv[3]), capabilities=JSON.parse(process.argv[4]);
const session=require('node:crypto').randomUUID();
let held=[], count=0;
const output=(q,result, extra={})=>process.stdout.write(JSON.stringify({kind:'response',protocolVersion:2,id:q.id,engineSessionId:session,method:q.method,ok:true,result,...extra})+'\\n');
createInterface({input:process.stdin}).on('line',line=>{
const q=JSON.parse(line);
if(q.method==='hello') {
 if(mode==='nohello') return;
 if(mode==='badversion') return output(q,{},{ok:false,error:{code:'VERSION_INCOMPATIBLE',messageKey:'protocol.versionIncompatible',params:{supportedVersions:[2]},retryable:false},result:undefined});
 output(q,{selectedVersion:2,engineVersion:'0.1.0',engineSessionId:session,capabilities,limits,registryHash:mode==='badhash'?'0'.repeat(64):hash});return;
}
count++;
if(mode==='exit') return process.exit(7);
if(mode==='eof') return process.stdout.end();
if(mode==='heartbeat' && (q.method==='session.ping' || count>1)) return;
if(mode==='flood') {for(let n=0;n<3;n++) output({...q,id:'00000000-0000-4000-8000-000000000009'}, {status:'ok',engineVersion:'0.1.0'}); return; }
if(mode==='timeout' && count===1) return setTimeout(()=>output(q,{status:'ok',engineVersion:'0.1.0'}),160);
if(mode==='rawbad') return process.stdout.write('{"a":1,"a":2}\\n');
if(mode==='overflow') return process.stdout.write('a'.repeat(262145));
if(mode==='stderr') process.stderr.write('secret-path-token\\n'.repeat(20000));
if(mode==='error') return output(q,undefined,{ok:false,error:{code:'STORAGE_BUSY',messageKey:'storage.busy',params:{retryAfterMs:10},retryable:true}});
const result=q.method==='session.ping'?{nonce:q.params.nonce}:{status:'ok',engineVersion:'0.1.0'};
if(mode==='wrong') {output({...q,id:'00000000-0000-4000-8000-000000000009'},result);output(q,result,{engineSessionId:'00000000-0000-4000-8000-000000000002'});}
if(mode==='reorder') { held.push([q,result]); if(held.length===2) {for(const [a,b] of held.reverse()) output(a,b); held=[];} return; }
output(q,result);
if(mode==='duplicate' && count===1) output(q,result);
});
`
const supervisors: EngineSupervisor[] = []
function supervisor(
  mode = 'normal',
  options: ConstructorParameters<typeof EngineSupervisor>[1] = {},
) {
  const value = new EngineSupervisor(
    { packaged: false, appPath: resolve('apps/desktop'), resourcesPath: '' },
    {
      registryPath,
      startupMs: 1000,
      handshakeMs: 500,
      requestMs: 500,
      heartbeatMs: 1000,
      command: {
        command: process.execPath,
        args: [
          '-e',
          source,
          mode,
          registryHash,
          JSON.stringify(limits),
          JSON.stringify(v2Registry.v2Runtime),
        ],
      },
      ...options,
    },
  )
  supervisors.push(value)
  return value
}
afterEach(() => {
  for (const instance of supervisors.splice(0)) instance.stop()
})

describe('resident supervisor with real child stdio', () => {
  it('reuses one negotiated process and session across health requests', async () => {
    const instance = supervisor()
    const first = await instance.health()
    const session = instance.engineSessionId
    expect(first).toEqual({
      protocolVersion: 2,
      engineVersion: '0.1.0',
      status: 'ok',
      capabilities: v2Registry.v2Runtime.filter((c: string) => c === 'health'),
    })
    expect(await instance.health()).toEqual(first)
    expect(instance.engineSessionId).toBe(session)
    instance.stop()
    await expect(instance.health()).rejects.toMatchObject({ error: { code: 'ENGINE_EXITED' } })
  })
  it('correlates concurrent out-of-order requests with independent identities', async () => {
    const instance = supervisor('reorder')
    const a = '00000000-0000-4000-8000-000000000004'
    const b = '00000000-0000-4000-8000-000000000005'
    expect(
      await Promise.all([
        instance.request('session.ping', { nonce: a }),
        instance.request('session.ping', { nonce: b }),
      ]),
    ).toEqual([{ nonce: a }, { nonce: b }])
  })
  it.each(['wrong', 'duplicate'])('does not settle a request using %s responses', async (mode) => {
    const diagnostics: string[] = []
    let sawUnmatched!: () => void
    const unmatched = new Promise<void>((done) => {
      sawUnmatched = done
    })
    const instance = supervisor(mode, {
      onDiagnostic: (event) => {
        diagnostics.push(event)
        if (event === 'unmatchedResponse') sawUnmatched()
      },
    })
    await expect(instance.health()).resolves.toMatchObject({ status: 'ok' })
    await unmatched
    expect(diagnostics).toContain('unmatchedResponse')
    if (mode === 'duplicate')
      await expect(instance.health()).resolves.toMatchObject({ status: 'ok' })
  })
  it('preserves the validated four-field public producer error', async () => {
    const instance = supervisor('error')
    await expect(instance.health()).rejects.toMatchObject({
      error: {
        code: 'STORAGE_BUSY',
        messageKey: 'storage.busy',
        params: { retryAfterMs: 10 },
        retryable: true,
      },
    })
  })
  it.each(['rawbad', 'overflow', 'exit', 'eof', 'flood'])(
    'clears all concurrent pending after %s failure',
    async (mode) => {
      const instance = supervisor(mode)
      const outcomes = await Promise.allSettled([instance.health(), instance.health()])
      expect(
        outcomes.every(
          (outcome) => outcome.status === 'rejected' && outcome.reason instanceof EngineError,
        ),
      ).toBe(true)
      expect(instance.engineSessionId).toBeUndefined()
    },
  )
  it('rejects raw registry hash mismatch and incompatible-version response', async () => {
    await expect(supervisor('badhash').health()).rejects.toMatchObject({
      error: { code: 'INVALID_REQUEST' },
    })
    await expect(supervisor('badversion').health()).rejects.toMatchObject({
      error: { code: 'VERSION_INCOMPATIBLE' },
    })
  })
  it('times out handshake and clears its pending', async () => {
    await expect(supervisor('nohello', { handshakeMs: 20 }).health()).rejects.toMatchObject({
      error: { code: 'TIMEOUT', params: { phase: 'handshake' } },
    })
  })
  it('drops a timed-out response without using it to settle a fresh request', async () => {
    const diagnostics: string[] = []
    const instance = supervisor('timeout', {
      requestMs: 80,
      onDiagnostic: (event) => diagnostics.push(event),
    })
    await expect(instance.health()).rejects.toMatchObject({
      error: { code: 'TIMEOUT', params: { phase: 'request' } },
    })
    await expect(instance.health()).resolves.toMatchObject({ status: 'ok' })
    await new Promise<void>((done) => setTimeout(done, 100))
    expect(diagnostics).toContain('unmatchedResponse')
  })
  it('reserves a bounded heartbeat slot and fences a nonresponsive session', async () => {
    const instance = supervisor('heartbeat', { heartbeatMs: 20, requestMs: 1000, maxPending: 1 })
    await instance.health()
    await expect(instance.health()).rejects.toMatchObject({
      error: { code: 'TIMEOUT', params: { phase: 'heartbeat' } },
    })
    expect(instance.engineSessionId).toBeUndefined()
  })
  it('bounds stderr diagnostics and never forwards private content', async () => {
    const diagnostics: string[] = []
    const instance = supervisor('stderr', { onDiagnostic: (event) => diagnostics.push(event) })
    await instance.health()
    await instance.health()
    await new Promise<void>((done) => setTimeout(done, 20))
    expect(diagnostics).toEqual(['stderrDiscarded'])
  })
  it('rejects invalid method params locally without killing a healthy session', async () => {
    const instance = supervisor()
    await instance.health()
    await expect(instance.request('not-a-method', {})).rejects.toMatchObject({
      error: { code: 'INVALID_REQUEST' },
    })
    await expect(instance.request('health', { token: 'secret' })).rejects.toMatchObject({
      error: { code: 'INVALID_REQUEST' },
    })
    await expect(instance.health()).resolves.toMatchObject({ status: 'ok' })
  })
})
