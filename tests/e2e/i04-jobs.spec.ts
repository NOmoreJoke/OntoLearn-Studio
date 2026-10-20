import { test, expect, _electron as electron } from '@playwright/test'
import { spawn, execFile } from 'node:child_process'
import { mkdtemp, readFile, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { resolve, join } from 'node:path'
import { promisify } from 'node:util'

const execute = promisify(execFile)
const fixturePath = process.env.I04_TEST_FIXTURE
const appArgs = () => [
  ...(process.env.ONTOLEARN_PACKAGED_EXECUTABLE ? [] : [resolve('apps/desktop')]),
  `--i04-test-fixture=${fixturePath}`,
]
function environment() {
  const env = { ...process.env }
  delete env.ELECTRON_RUN_AS_NODE
  return env
}

test('I04 reload re-queries the same durable jobs without creating or cancelling them', async () => {
  test.skip(!fixturePath, 'Requires a fresh trusted fixture backed by actual SQLite jobs.')
  const application = await electron.launch({
    ...(process.env.ONTOLEARN_PACKAGED_EXECUTABLE
      ? { executablePath: process.env.ONTOLEARN_PACKAGED_EXECUTABLE }
      : {}),
    args: appArgs(),
    cwd: resolve('apps/desktop'),
    env: environment(),
  })
  try {
    const page = await application.firstWindow()
    await expect(page.getByRole('region', { name: '后台任务状态' })).toBeVisible()
    const first = await page.evaluate(() => window.ontolearn!.restoreTasks())
    expect(first.ok && first.data.jobs.length).toBeGreaterThan(0)
    if (!first.ok) throw new Error('durable restore failed')
    expect(await page.evaluate(() => 'createJob' in window.ontolearn!)).toBe(false)
    await page.reload()
    await expect(page.getByRole('region', { name: '后台任务状态' })).toBeVisible()
    const next = await page.evaluate(() => window.ontolearn!.restoreTasks())
    if (!next.ok) throw new Error('durable restore after reload failed')
    expect(next.data.generation).toBeGreaterThan(first.data.generation)
    expect(next.data.jobs.map((job) => job.jobId)).toEqual(first.data.jobs.map((job) => job.jobId))
    for (const job of next.data.jobs) {
      const before = first.data.jobs.find((value) => value.jobId === job.jobId)!
      expect(job.operationId).toBe(before.operationId)
      expect(job.stateVersion).toBeGreaterThanOrEqual(before.stateVersion)
      expect(job.state).not.toBe('cancelled')
      const operation = await page.evaluate(
        (id) => window.ontolearn!.getOperation(id),
        job.operationId,
      )
      expect(operation.ok).toBe(true)
    }
    const denied = await page.evaluate(() =>
      window.ontolearn!.listJobs({
        projectId: '00000000-0000-4000-8000-000000000099',
        filter: 'all',
        pageSize: 20,
        listSnapshotId: null,
        cursor: null,
      } as never),
    )
    expect(denied.ok).toBe(false)
  } finally {
    await application.close()
  }
})

// Native recovery is deliberately separate from Playwright Electron: renderer CDP
// is never attached, and the main inspector is closed before crash/hang injection.
const nativeHook = String.raw`
const {app,BrowserWindow}=require('electron')
const {writeFileSync}=require('node:fs')
const inspector=require('node:inspector')
const evidence={windows:[],events:[],inspectorClosed:false,hangMonitorEnabled:!app.commandLine.hasSwitch('disable-hang-monitor')}
const save=()=>writeFileSync(process.env.I04_NATIVE_EVIDENCE,JSON.stringify(evidence,null,2))
const fail=(error)=>{evidence.error=String(error);save();app.exit(1)}
const deadline=setTimeout(()=>fail('native I04 deadline'),65000)
let count=0
async function snapshot(window){
 const response=await window.webContents.executeJavaScript('window.ontolearn.restoreTasks()')
 if(!response.ok||!response.data.project||!response.data.jobs.length)throw new Error('missing durable jobs')
 const view=response.data
 const operations=[]
 for(const job of view.jobs){const operation=await window.webContents.executeJavaScript('window.ontolearn.getOperation('+JSON.stringify(job.operationId)+')');if(!operation.ok)throw new Error('operation evidence unavailable');operations.push({operationId:job.operationId,marker:operation.data})}
 view.operationEvidence=operations
 if(count===1&&!view.jobs.some(job=>job.state==='succeeded'&&((job.commitProgress.mode==='atomic'&&job.commitProgress.marker)||(job.commitProgress.mode==='rounds'&&job.commitProgress.committedProgress))))throw new Error('fixture requires committed baseline job')
 if(count===1&&!view.jobs.some(job=>['queued','running'].includes(job.state)))throw new Error('fixture requires active background job')

 if(count>1){
  const previous=evidence.windows[0].view
  if(JSON.stringify(previous.jobs.map(j=>j.jobId))!==JSON.stringify(view.jobs.map(j=>j.jobId)))throw new Error('replayed or missing jobs')
  for(const job of view.jobs){const old=previous.jobs.find(j=>j.jobId===job.jobId);if(job.operationId!==old.operationId||job.stateVersion<old.stateVersion||job.state==='cancelled')throw new Error('durable state regressed');
   const commit=old.commitProgress,current=job.commitProgress
   if(commit.mode==='atomic'&&commit.marker&&JSON.stringify(commit)!==JSON.stringify(current))throw new Error('atomic commit evidence changed')
   if(commit.mode==='rounds'&&commit.committedProgress){if(current.mode!=='rounds'||!current.committedProgress||current.committedProgress.lastCommittedRound<commit.committedProgress.lastCommittedRound)throw new Error('round commit lost');if(current.committedProgress.lastCommittedRound===commit.committedProgress.lastCommittedRound&&JSON.stringify(current)!==JSON.stringify(commit))throw new Error('committed round evidence changed')}
  }
  for(const old of previous.operationEvidence){if(old.marker){const current=operations.find(item=>item.operationId===old.operationId);if(JSON.stringify(current.marker)!==JSON.stringify(old.marker))throw new Error('operation marker changed')}}
  if(view.project.projectRevision<previous.project.projectRevision)throw new Error('project revision regressed')
 }
 return view
}
function observe(window,freshlyCreated=false){
 const ordinal=++count
 const entry={ordinal};evidence.windows.push(entry)
 window.webContents.on('render-process-gone',(_event,details)=>{evidence.events.push(details.reason);save()})
 window.on('unresponsive',()=>{evidence.events.push('unresponsive');evidence.awaitingDialog='hang';save()})
 const drive=async()=>{try{
  entry.view=await snapshot(window);entry.visible=window.isVisible();save()
  if(ordinal===1){evidence.awaitingDialog='crash';save();window.webContents.forcefullyCrashRenderer()}
  else if(ordinal===2){
   window.show();app.focus({steal:true});window.focus()
   const end=Date.now()+3000
   while(!window.isVisible()||!window.isFocused()){if(Date.now()>end)throw new Error('native focus deadline');await new Promise(done=>setTimeout(done,25))}
   entry.focused=window.isFocused();entry.visible=window.isVisible();save()
   void window.webContents.executeJavaScript('for(;;){}').catch(error=>{if(!window.isDestroyed())fail(error)})
   setTimeout(()=>{if(window.isDestroyed())return;if(!window.isVisible()||!window.isFocused())return fail('native hang lost focus');window.webContents.sendInputEvent({type:'mouseDown',x:400,y:400,button:'left',clickCount:1});window.webContents.sendInputEvent({type:'mouseUp',x:400,y:400,button:'left',clickCount:1})},250)
  }else if(ordinal===3){
   if(!evidence.inspectorClosed||!evidence.hangMonitorEnabled||!evidence.events.includes('unresponsive')||!evidence.events.some(value=>['crashed','killed'].includes(value)))throw new Error('missing real native faults')
   evidence.result='PASS';delete evidence.awaitingDialog;save();clearTimeout(deadline);app.quit()
  }else throw new Error('unexpected extra recovery')
 }catch(error){fail(error)}}
 if(freshlyCreated||window.webContents.isLoadingMainFrame()||!window.webContents.getURL())window.webContents.once('did-finish-load',drive)
 else void drive()
}
setTimeout(()=>{inspector.close();evidence.inspectorClosed=inspector.url()===undefined;save();app.on('browser-window-created',(_event,window)=>observe(window,true));for(const window of BrowserWindow.getAllWindows())observe(window)},150)
`

test('I04 native renderer crash and real unresponsive dialog retain durable jobs', async () => {
  test.skip(
    process.platform !== 'linux' || process.env.I04_NATIVE_ISOLATED !== '1' || !fixturePath,
    'Requires an explicitly isolated Linux display, openbox, xdotool and fresh real SQLite fixture.',
  )
  test.setTimeout(90000)
  const directory = await mkdtemp(join(tmpdir(), 'i04-native-'))
  const evidencePath = join(directory, 'evidence.json')
  const hook = join(directory, 'native.cjs')
  await writeFile(hook, nativeHook)
  const executable =
    process.env.ONTOLEARN_PACKAGED_EXECUTABLE ?? resolve('node_modules/electron/dist/electron')
  const child = spawn(executable, ['--inspect=0', ...appArgs()], {
    env: { ...environment(), I04_NATIVE_EVIDENCE: evidencePath },
    stdio: ['ignore', 'pipe', 'pipe'],
  })
  let stderr = ''
  let stdout = ''
  let socket: WebSocket | undefined
  const finished = new Promise<void>((done, reject) => {
    child.on('error', reject)
    child.on('close', (code) =>
      code === 0 ? done() : reject(new Error(`native exit ${code}: ${stderr}\n${stdout}`)),
    )
  })
  void finished.catch(() => {})
  const endpoint = new Promise<string>((done) =>
    child.stderr.on('data', (chunk) => {
      stderr = (stderr + String(chunk)).slice(-65536)
      const match = stderr.match(/ws:\/\/127\.0\.0\.1:[^\s]+/)
      if (match) done(match[0])
    }),
  )
  child.stdout.on('data', (chunk) => {
    stdout = (stdout + String(chunk)).slice(-65536)
  })
  let timer: ReturnType<typeof setTimeout>
  const deadline = new Promise<never>((_done, reject) => {
    timer = setTimeout(() => reject(new Error(`native timeout: ${stderr}`)), 75000)
  })
  const bounded = <T>(value: Promise<T>) =>
    Promise.race([
      value,
      deadline,
      finished.then(() => {
        throw new Error('native exited before driver finished')
      }),
    ])
  try {
    socket = new WebSocket(await bounded(endpoint))
    const connected = socket
    await bounded(
      new Promise<void>((done, reject) => {
        connected.addEventListener('open', () => done(), { once: true })
        connected.addEventListener('error', () => reject(new Error('main inspector unavailable')), {
          once: true,
        })
      }),
    )
    await bounded(
      new Promise<void>((done, reject) => {
        connected.addEventListener('message', (event) => {
          const message = JSON.parse(String(event.data))
          if (message.id !== 1) return
          if (message.error || message.result?.exceptionDetails)
            reject(new Error(JSON.stringify(message)))
          else done()
        })
        connected.send(
          JSON.stringify({
            id: 1,
            method: 'Runtime.evaluate',
            params: {
              expression: `process.getBuiltinModule('module').createRequire(process.execPath)(${JSON.stringify(hook)})`,
            },
          }),
        )
      }),
    )
    connected.close()
    for (const phase of ['crash', 'hang']) {
      const end = Date.now() + 30000
      let dialogId: string | undefined
      while (Date.now() < end) {
        let evidence: Record<string, unknown> | undefined
        try {
          evidence = JSON.parse(await readFile(evidencePath, 'utf8'))
        } catch {
          /* Writer may be replacing this evidence file. */
        }
        if (evidence?.error) throw new Error(String(evidence.error))
        if (evidence?.awaitingDialog === phase) {
          try {
            const found = await execute('xdotool', [
              'search',
              '--onlyvisible',
              '--name',
              'OntoLearn Studio 窗口恢复',
            ])
            dialogId = found.stdout.trim().split('\n')[0]
          } catch {
            /* Native prompt has not mapped yet. */
          }
          if (dialogId) break
        }
        await new Promise((done) => setTimeout(done, 100))
      }
      expect(dialogId, `actual ${phase} native recovery dialog`).toBeTruthy()
      // The real native dialog defaults to “暂不恢复”. Move to the preceding
      // “重新打开窗口” button using GTK keyboard navigation; never stub its result.
      await execute('xdotool', ['windowactivate', '--sync', dialogId!])
      await execute('xdotool', ['key', '--clearmodifiers', 'shift+Tab', 'Return'])
    }
    await Promise.race([finished, deadline])
    const evidence = JSON.parse(await readFile(evidencePath, 'utf8'))
    expect(evidence.result).toBe('PASS')
    expect(evidence.windows).toHaveLength(3)
    expect(evidence.inspectorClosed).toBe(true)
    expect(evidence.hangMonitorEnabled).toBe(true)
    expect(evidence.windows[1]).toMatchObject({ visible: true, focused: true })
    await test
      .info()
      .attach('i04-native-evidence', { path: evidencePath, contentType: 'application/json' })
  } finally {
    try {
      await test.info().attach('i04-native-final-evidence', {
        path: evidencePath,
        contentType: 'application/json',
      })
    } catch {
      /* A bootstrap failure may precede the first evidence write. */
    }
    await test.info().attach('i04-native-driver-log', {
      body: JSON.stringify({ stderr, stdout }),
      contentType: 'application/json',
    })
    clearTimeout(timer!)
    socket?.close()
    if (child.exitCode === null) child.kill('SIGKILL')
  }
})
