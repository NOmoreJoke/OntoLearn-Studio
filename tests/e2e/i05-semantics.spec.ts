import { test, expect, _electron as electron, type Page, type TestInfo } from '@playwright/test'
import { spawn, execFile } from 'node:child_process'
import { createHash } from 'node:crypto'
import { readFile, writeFile } from 'node:fs/promises'
import { resolve, join } from 'node:path'
import { promisify } from 'node:util'
import type { JobView, SemanticRunOptions } from '@ontolearn/contracts'

const execute = promisify(execFile)
type Row = { rowId: string; ordinal: number; cells: Array<string | number | boolean | null> }
type FixtureMeta = {
  project: { projectId: string; projectRevision: number; inputSnapshotId: string }
  completed: Array<{
    job: JobView
    metadata: Record<string, unknown>
    payload: Record<string, unknown>
    rowsSha256: string
  }>
  queryText: string
  networkCanary: string
  assertedFactCount: number
  backgroundOperations: Array<{ operationId: string; definitionId: string }>
}
function canonical(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(canonical).join(',')}]`
  if (value !== null && typeof value === 'object')
    return `{${Object.entries(value)
      .sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0))
      .map(([k, v]) => `${JSON.stringify(k)}:${canonical(v)}`)
      .join(',')}}`
  return JSON.stringify(value)
}
const hash = (value: unknown) => createHash('sha256').update(canonical(value)).digest('hex')
function environment(fixturePath: string) {
  const env: Record<string, string> = Object.fromEntries(
    Object.entries(process.env).filter(
      (entry): entry is [string, string] => entry[1] !== undefined,
    ),
  )
  env.I04_TEST_FIXTURE = fixturePath
  delete env.ELECTRON_RUN_AS_NODE
  return env
}
const appArgs = (fixturePath: string) => [
  ...(process.env.ONTOLEARN_PACKAGED_EXECUTABLE ? [] : [resolve('apps/desktop')]),
  `--i04-test-fixture=${fixturePath}`,
]
async function prepare(testInfo: TestInfo) {
  const directory = testInfo.outputPath('isolated-sqlite-fixture')
  const result = await execute(
    resolve('.venv/bin/python'),
    ['scripts/prepare-i05-fixture.py', directory],
    { timeout: 45000, maxBuffer: 1048576 },
  )
  const fixturePath = result.stdout.trim()
  expect(fixturePath).toBe(join(directory, 'fixture.json'))
  const meta = JSON.parse(await readFile(join(directory, 'metadata.json'), 'utf8')) as FixtureMeta
  expect(meta.assertedFactCount).toBe(27)
  await testInfo.attach('i05-fixture-metadata', {
    path: join(directory, 'metadata.json'),
    contentType: 'application/json',
  })
  return { fixturePath, meta }
}
async function readResult(page: Page, job: JobView) {
  return page.evaluate(async (identity) => {
    const bridge = window.ontolearn!
    const metadata = await bridge.getResult(identity)
    if (!metadata.ok) throw new Error('result metadata unavailable')
    const rows: Row[] = []
    let cursor: string | null = null
    do {
      const response = await bridge.getResultPage({ resultId: identity, pageSize: 200, cursor })
      if (!response.ok) throw new Error('result page unavailable')
      rows.push(...(response.data.rows as Row[]))
      cursor = response.data.nextCursor as string | null
    } while (cursor)
    return { metadata: metadata.data, rows }
  }, job.resultRef!.resultId)
}
function leaf(rows: Row[], path: string): unknown {
  const pieces = rows
    .filter((row) => row.cells[0] === path)
    .sort((a, b) => Number(a.cells[2]) - Number(b.cells[2]))
  return JSON.parse(pieces.map((row) => row.cells[1]).join(''))
}
async function view(page: Page) {
  const response = await page.evaluate(() => window.ontolearn!.restoreTasks())
  if (!response.ok || !response.data.project) throw new Error('authorized task view unavailable')
  return response.data
}
async function waitJob(page: Page, jobId: string, state: string) {
  await expect
    .poll(
      async () => {
        const job = await page.evaluate((identity) => window.ontolearn!.getJob(identity), jobId)
        return job.ok ? job.data.state : 'unavailable'
      },
      { timeout: 12000 },
    )
    .toBe(state)
  const response = await page.evaluate((identity) => window.ontolearn!.getJob(identity), jobId)
  if (!response.ok) throw new Error('durable job unavailable')
  return response.data
}

test('I05 real named semantic operations, complete source pages, reload and explicit cancellation', async () => {
  const testInfo = test.info()
  test.skip(
    process.platform !== 'linux' || process.env.I05_SEMANTIC_E2E !== '1',
    'Run only on the explicitly isolated Linux semantic test display.',
  )
  test.setTimeout(90000)
  const { fixturePath, meta } = await prepare(testInfo)
  const application = await electron.launch({
    ...(process.env.ONTOLEARN_PACKAGED_EXECUTABLE
      ? { executablePath: process.env.ONTOLEARN_PACKAGED_EXECUTABLE }
      : {}),
    args: appArgs(fixturePath),
    cwd: resolve('apps/desktop'),
    env: environment(fixturePath),
  })
  try {
    const page = await application.firstWindow()
    const first = await view(page)
    expect(first.project).toEqual(meta.project)
    expect(first.jobs).toHaveLength(5)
    expect(await page.evaluate(() => Object.keys(window.ontolearn!))).toEqual(
      expect.arrayContaining(['runSavedQuery', 'runReasoning', 'runValidation']),
    )
    expect(
      await page.evaluate(() =>
        ['invoke', 'createJob', 'semanticStart'].some((key) => key in window.ontolearn!),
      ),
    ).toBe(false)
    const baseline = []
    for (const entry of meta.completed) {
      const result = await readResult(page, entry.job)
      expect(result.metadata).toEqual(entry.metadata)
      expect(hash(result.rows)).toBe(entry.rowsSha256)
      expect(result.metadata.inputSnapshotId).toBe(meta.project.inputSnapshotId)
      expect(result.metadata.scope).toBe(entry.job.scope)
      baseline.push({ jobId: entry.job.jobId, rowsSha256: hash(result.rows) })
      if (result.metadata.kind === 'query') {
        expect(leaf(result.rows, '/queryText')).toBe(meta.queryText)
        expect(leaf(result.rows, '/query/rows/0/0')).toBe('<urn:case:0:alarm/A01>')
      }
      if (result.metadata.kind === 'validation') {
        expect(leaf(result.rows, '/constraintsVersion')).toBe(1)
        expect(leaf(result.rows, '/report/conforms')).toBe(false)
        expect(leaf(result.rows, '/report/violations/0/focus')).toBe('<urn:case:0:equipment/003>')
        expect(leaf(result.rows, '/report/violations/0/sourceShape')).toBe(
          '<urn:ontolearn:NameProperty>',
        )
      }
      if (result.metadata.kind === 'reasoning') {
        expect(leaf(result.rows, '/reasoning/evidence/0/rule')).toBe('R-risk')
        expect(leaf(result.rows, '/reasoning/rules/0/0')).toBe('<urn:case:0:equipment/001>')
      }
    }
    const slowOperation = meta.backgroundOperations.find(
      (item) => item.definitionId === 'slow-count',
    )!.operationId
    const forbiddenOperation = meta.backgroundOperations.find(
      (item) => item.definitionId === 'forbidden-service',
    )!.operationId
    const slow = first.jobs.find((job) => job.operationId === slowOperation)!
    const forbidden = first.jobs.find((job) => job.operationId === forbiddenOperation)!
    await waitJob(page, slow.jobId, 'running')
    const failed = await waitJob(page, forbidden.jobId, 'failed')
    expect(failed.error).toEqual({
      code: 'NETWORK_FORBIDDEN',
      messageKey: 'semantics.networkForbidden',
      params: {},
      retryable: false,
    })
    expect(JSON.stringify(failed.error)).not.toContain(meta.networkCanary)
    const card = page.locator(`[data-job-id="${forbidden.jobId}"]`)
    for (const label of ['发生了什么：', '为什么发生：', '如何修复：', '相关知识：'])
      await expect(card).toContainText(label)
    await page.getByRole('link', { name: '模块规划' }).click()
    await page.getByRole('link', { name: '开发概览' }).click()
    const afterNavigation = await view(page)
    expect(afterNavigation.generation).toBe(first.generation)
    await page.reload()
    const restored = await view(page)
    expect(restored.generation).toBeGreaterThan(first.generation)
    expect(restored.project).toEqual(first.project)
    expect(restored.jobs.map((job) => [job.jobId, job.operationId])).toEqual(
      first.jobs.map((job) => [job.jobId, job.operationId]),
    )
    expect((await waitJob(page, slow.jobId, 'running')).error).toBeNull()
    for (const entry of meta.completed)
      expect(hash((await readResult(page, entry.job)).rows)).toBe(entry.rowsSha256)
    const derived = meta.completed.find((item) => item.metadata.kind === 'reasoning')!.metadata
      .resultId as string
    const options: SemanticRunOptions = {
      definitionId: 'Q01',
      scope: 'asserted+derived',
      inputSelection: 'current',
      inputSnapshotId: null,
      derivedResultId: derived,
    }
    const created: JobView[] = []
    for (const method of ['runSavedQuery', 'runValidation', 'runReasoning'] as const) {
      const response = await page.evaluate(
        async ({ method, options }) => {
          const bridge = window.ontolearn!
          if (method === 'runReasoning')
            return bridge.runReasoning({
              ...options,
              definitionId: 'all',
              scope: 'asserted',
              derivedResultId: null,
            })
          if (method === 'runValidation')
            return bridge.runValidation({ ...options, definitionId: 'V01' })
          return bridge.runSavedQuery(options)
        },
        { method, options },
      )
      expect(response.ok).toBe(true)
      if (!response.ok) throw new Error('real semantic admission failed')
      const job = await waitJob(page, response.data.jobId, 'succeeded')
      expect(job.inputSnapshotId).toBe(meta.project.inputSnapshotId)
      expect(job.operationId).not.toBe(slow.operationId)
      created.push(job)
      const actual = await readResult(page, job)
      expect(actual.metadata.kind).toBe(
        { runSavedQuery: 'query', runReasoning: 'reasoning', runValidation: 'validation' }[method],
      )
      expect(leaf(actual.rows, '/inputSnapshotId')).toBe(meta.project.inputSnapshotId)
      if (method === 'runSavedQuery') expect(leaf(actual.rows, '/queryText')).toBe(meta.queryText)
      if (method === 'runValidation')
        expect(leaf(actual.rows, '/report/violations/0/focus')).toBe('<urn:case:0:equipment/003>')
    }
    const cancellation = await page.evaluate(
      (identity) => window.ontolearn!.cancelJob(identity),
      slow.jobId,
    )
    expect(cancellation.ok).toBe(true)
    const cancelled = await waitJob(page, slow.jobId, 'cancelled')
    expect(cancelled.resultRef).toBeNull()
    expect(cancelled.operationId).toBe(slow.operationId)
    await page.reload()
    const final = await view(page)
    expect(final.project).toEqual(meta.project)
    expect(final.jobs.find((job) => job.jobId === slow.jobId)).toEqual(cancelled)
    const history = await page.evaluate(() =>
      window.ontolearn!.listJobs({
        filter: 'all',
        pageSize: 100,
        listSnapshotId: null,
        cursor: null,
      }),
    )
    expect(history.ok && (history.data.jobs as JobView[]).length).toBe(8)
    if (history.ok)
      expect(
        (history.data.jobs as JobView[]).filter((job) => job.operationId === slow.operationId),
      ).toHaveLength(1)
    const evidence = testInfo.outputPath('i05-semantic-bridge-evidence.json')
    await writeFile(
      evidence,
      JSON.stringify(
        { first, restored, baseline, created, failed, cancelled, final, history },
        null,
        2,
      ),
    )
    await testInfo.attach('i05-semantic-bridge-evidence', {
      path: evidence,
      contentType: 'application/json',
    })
  } finally {
    await application.close()
  }
})

// Native recovery is deliberately separate from Playwright Electron: renderer CDP
// is never attached, and the main inspector is closed before crash/hang injection.
const nativeHook = String.raw`
const {app,BrowserWindow}=require('electron')
const {writeFileSync}=require('node:fs')
const {execFileSync}=require('node:child_process')
const inspector=require('node:inspector')
const evidence={windows:[],events:[],inspectorClosed:false,hangMonitorEnabled:!app.commandLine.hasSwitch('disable-hang-monitor'),noSandboxSwitch:app.commandLine.hasSwitch('no-sandbox')}
const save=()=>writeFileSync(process.env.I05_NATIVE_EVIDENCE,JSON.stringify(evidence,null,2))
const fail=(error)=>{evidence.error=String(error);save();app.exit(1)}
const deadline=setTimeout(()=>fail('native I05 deadline'),75000)
let count=0
async function snapshot(window){
 const value=await window.webContents.executeJavaScript("(async()=>{\n  const bridge=window.ontolearn\n  let response=await bridge.restoreTasks()\n  if(!response.ok||!response.data.project||response.data.jobs.length!==5)throw new Error('missing semantic durable jobs')\n  const view=response.data\n  const slow=view.jobs.find(job=>job.input.definitionId==='slow-count')\n  const end=Date.now()+5000\n  let status=await bridge.getJob(slow.jobId)\n  while(status.ok&&status.data.state==='queued'&&Date.now()<end){await new Promise(done=>setTimeout(done,25));status=await bridge.getJob(slow.jobId)}\n  if(!status.ok||status.data.state!=='running')throw new Error('actual COUNT worker is not running')\n  view.jobs=view.jobs.map(job=>job.jobId===slow.jobId?status.data:job)\n  const results=[]\n  for(const job of view.jobs.filter(job=>job.state==='succeeded')){\n   const id=job.resultRef.resultId\n   const metadata=await bridge.getResult(id)\n   if(!metadata.ok)throw new Error('immutable metadata missing')\n   let cursor=null;const rows=[]\n   do{const page=await bridge.getResultPage({resultId:id,pageSize:200,cursor});if(!page.ok)throw new Error('immutable source page missing');rows.push(...page.data.rows);cursor=page.data.nextCursor}while(cursor)\n   results.push({jobId:job.jobId,metadata:metadata.data,rows})\n  }\n  if(results.map(item=>item.metadata.kind).sort().join(',')!=='query,reasoning,validation')throw new Error('three actual semantic producer outputs missing')\n  const history=await bridge.listJobs({filter:'all',pageSize:100,listSnapshotId:null,cursor:null})\n  if(!history.ok||history.data.jobs.length!==5)throw new Error('semantic history replayed or missing')\n  return {view,results,history:history.data,slowJobId:slow.jobId}\n })()")
 const stable=JSON.stringify(value.results)
 if(count>1){
  const initial=evidence.windows[0].snapshot
  if(stable!==JSON.stringify(initial.results))throw new Error('immutable semantic source or payload changed')
  if(JSON.stringify(initial.view.project)!==JSON.stringify(value.view.project))throw new Error('project/snapshot/revision changed')
  if(JSON.stringify(initial.view.jobs.map(job=>[job.jobId,job.operationId]))!==JSON.stringify(value.view.jobs.map(job=>[job.jobId,job.operationId])))throw new Error('semantic creation replayed')
  for(const job of value.view.jobs){const old=initial.view.jobs.find(item=>item.jobId===job.jobId);if(job.stateVersion<old.stateVersion||job.state==='cancelled')throw new Error('semantic state regressed or cancelled by recovery')}
 }
 value.resultsSha256=require('node:crypto').createHash('sha256').update(stable).digest('hex')
 return value
}
function observe(window,freshlyCreated=false){
 const ordinal=++count
 const entry={ordinal};evidence.windows.push(entry)
 window.webContents.on('render-process-gone',(_event,details)=>{evidence.events.push(details.reason);save()})
 window.on('unresponsive',()=>{evidence.events.push('unresponsive');evidence.awaitingDialog='hang';save()})
 const drive=async()=>{try{
  entry.snapshot=await snapshot(window);entry.visible=window.isVisible();save()
  if(ordinal===1){evidence.awaitingDialog='crash';save();window.webContents.forcefullyCrashRenderer()}
  else if(ordinal===2){
   window.show();app.focus({steal:true});window.focus()
   const end=Date.now()+3000
   while(!window.isVisible()||!window.isFocused()){if(Date.now()>end)throw new Error('native focus deadline');await new Promise(done=>setTimeout(done,25))}
   entry.focused=window.isFocused();entry.visible=window.isVisible();save()
   const focusId=execFileSync('xdotool',['getwindowfocus'],{timeout:2000}).toString().trim()
   const focusTitle=execFileSync('xdotool',['getwindowname',focusId],{timeout:2000}).toString().trim()
   const visibleIds=execFileSync('xdotool',['search','--onlyvisible','--name','.*'],{timeout:2000}).toString().trim().split('\n')
   entry.x11Focus={observer:'xdotool/XGetInputFocus',windowId:focusId,title:focusTitle,visible:visibleIds.includes(focusId)}
   if(!entry.x11Focus.visible||focusTitle!==window.getTitle())throw new Error('external X focus does not match visible application window')
   save()
   void window.webContents.executeJavaScript('for(;;){}').catch(error=>{if(!window.isDestroyed())fail(error)})
   setTimeout(()=>{if(window.isDestroyed())return;if(!window.isVisible()||!window.isFocused())return fail('native hang lost focus');window.webContents.sendInputEvent({type:'mouseDown',x:400,y:400,button:'left',clickCount:1});window.webContents.sendInputEvent({type:'mouseUp',x:400,y:400,button:'left',clickCount:1})},250)
  }else if(ordinal===3){
   if(evidence.noSandboxSwitch||!evidence.inspectorClosed||!evidence.hangMonitorEnabled||!evidence.events.includes('unresponsive')||!evidence.events.some(value=>['crashed','killed'].includes(value)))throw new Error('missing real native faults')
   const cancelled=await window.webContents.executeJavaScript('(async()=>{const bridge=window.ontolearn;const id='+JSON.stringify(entry.snapshot.slowJobId)+';const response=await bridge.cancelJob(id);if(!response.ok)throw new Error("explicit cancel failed");const end=Date.now()+5000;let job;do{job=await bridge.getJob(id);if(job.ok&&job.data.state==="cancelled")return job.data;await new Promise(done=>setTimeout(done,25))}while(Date.now()<end);throw new Error("semantic cancel deadline")})()')
   evidence.explicitCancellation=cancelled
   if(cancelled.resultRef!==null)throw new Error('cancelled query fabricated result')
   evidence.result='PASS';delete evidence.awaitingDialog;save();clearTimeout(deadline);app.quit()
  }else throw new Error('unexpected extra recovery')
 }catch(error){fail(error)}}
 if(freshlyCreated||window.webContents.isLoadingMainFrame()||!window.webContents.getURL())window.webContents.once('did-finish-load',drive)
 else void drive()
}
setTimeout(()=>{inspector.close();evidence.inspectorClosed=inspector.url()===undefined;save();app.on('browser-window-created',(_event,window)=>observe(window,true));for(const window of BrowserWindow.getAllWindows())observe(window)},150)
`

test('I05 native renderer crash and real unresponsive dialog retain immutable semantic outputs', async () => {
  const testInfo = test.info()
  test.skip(
    process.platform !== 'linux' || process.env.I05_NATIVE_ISOLATED !== '1',
    'Requires an explicitly isolated Linux display, openbox, xdotool and fresh real SQLite fixture.',
  )
  test.setTimeout(90000)
  const { fixturePath } = await prepare(testInfo)
  const directory = testInfo.outputPath()
  const evidencePath = join(directory, 'evidence.json')
  const hook = join(directory, 'native.cjs')
  await writeFile(hook, nativeHook)
  const executable =
    process.env.ONTOLEARN_PACKAGED_EXECUTABLE ?? resolve('node_modules/electron/dist/electron')
  const child = spawn(executable, ['--inspect=0', ...appArgs(fixturePath)], {
    env: { ...environment(fixturePath), I05_NATIVE_EVIDENCE: evidencePath },
    stdio: ['ignore', 'pipe', 'pipe'],
  })
  let stderr = ''
  let stdout = ''
  const nativeDialogs: { phase: string; windowId: string; title: string; visible: boolean }[] = []
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
              // The packaged main inspector can open before Electron has installed
              // its built-in module. Gate instrumentation on the real ready app.
              expression: `(async()=>{const load=process.getBuiltinModule('module').createRequire(process.execPath);const end=Date.now()+5000;while(Date.now()<end){try{if(load('electron').app?.isReady()){load(${JSON.stringify(hook)});return}}catch{}await new Promise(done=>setTimeout(done,25))}throw new Error('Electron main app did not become ready')})()`,
              awaitPromise: true,
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
            const found = await execute('xdotool', ['search', '--onlyvisible', '--name', '.*'])
            for (const id of found.stdout.trim().split('\n').filter(Boolean)) {
              const title = await execute('xdotool', ['getwindowname', id])
              if (title.stdout.trim() === 'OntoLearn Studio 窗口恢复') {
                dialogId = id
                break
              }
            }
          } catch {
            /* Native prompt has not mapped yet. */
          }
          if (dialogId) break
        }
        await new Promise((done) => setTimeout(done, 100))
      }
      if (!dialogId) {
        const inventory = await execute('xdotool', [
          'search',
          '--onlyvisible',
          '--name',
          '.*',
        ]).catch(() => ({ stdout: '' }))
        const windows = []
        for (const id of inventory.stdout.trim().split('\n').filter(Boolean)) {
          windows.push({
            id,
            name: (
              await execute('xdotool', ['getwindowname', id]).catch(() => ({ stdout: '' }))
            ).stdout.trim(),
          })
        }
        await test.info().attach('actual-native-window-inventory', {
          body: JSON.stringify(windows),
          contentType: 'application/json',
        })
      }
      expect(dialogId, `actual ${phase} native recovery dialog`).toBeTruthy()
      nativeDialogs.push({
        phase,
        windowId: dialogId!,
        title: (await execute('xdotool', ['getwindowname', dialogId!])).stdout.trim(),
        visible: true,
      })
      // The real native dialog defaults to “暂不恢复”. Move to the preceding
      // “重新打开窗口” button using GTK keyboard navigation; never stub its result.
      await execute('xdotool', ['windowactivate', '--sync', dialogId!])
      await execute('xdotool', ['key', '--clearmodifiers', 'shift+Tab', 'Return'])
    }
    await Promise.race([finished, deadline])
    const evidence = JSON.parse(await readFile(evidencePath, 'utf8'))
    expect(evidence.result).toBe('PASS')
    expect(evidence.windows).toHaveLength(3)
    expect(evidence.windows.every((window: { visible: boolean }) => window.visible)).toBe(true)
    expect(
      new Set(
        evidence.windows.map(
          (window: { snapshot: { resultsSha256: string } }) => window.snapshot.resultsSha256,
        ),
      ).size,
    ).toBe(1)
    expect(evidence.explicitCancellation.state).toBe('cancelled')
    expect(evidence.explicitCancellation.capability).toBe('query.execute')
    expect(evidence.inspectorClosed).toBe(true)
    expect(evidence.hangMonitorEnabled).toBe(true)
    expect(evidence.noSandboxSwitch).toBe(false)
    expect(evidence.windows[1]).toMatchObject({ visible: true, focused: true })
    expect(evidence.windows[1].x11Focus).toMatchObject({
      observer: 'xdotool/XGetInputFocus',
      visible: true,
    })
    expect(nativeDialogs.map((dialog) => dialog.phase)).toEqual(['crash', 'hang'])
    expect(nativeDialogs.every((dialog) => dialog.title === 'OntoLearn Studio 窗口恢复')).toBe(true)
    const verifiedEvidence = test.info().outputPath('i05-native-verified-evidence.json')
    await writeFile(
      verifiedEvidence,
      JSON.stringify(
        { ...evidence, nativeDialogs, dialogObserver: 'external xdotool visible-window inventory' },
        null,
        2,
      ),
    )
    await test.info().attach('i05-native-verified-evidence', {
      path: verifiedEvidence,
      contentType: 'application/json',
    })
    await test
      .info()
      .attach('i05-native-evidence', { path: evidencePath, contentType: 'application/json' })
  } finally {
    try {
      await test.info().attach('i05-native-final-evidence', {
        path: evidencePath,
        contentType: 'application/json',
      })
    } catch {
      /* A bootstrap failure may precede the first evidence write. */
    }
    await test.info().attach('i05-native-driver-log', {
      body: JSON.stringify({ stderr, stdout }),
      contentType: 'application/json',
    })
    clearTimeout(timer!)
    socket?.close()
    if (child.exitCode === null) child.kill('SIGKILL')
  }
})
