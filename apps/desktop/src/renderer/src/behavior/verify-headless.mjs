/** Run from this worktree root. Builds an isolated fixture, never starts Electron/Vite HMR. */
import assert from 'node:assert/strict'
import { createServer } from 'node:http'
import { mkdir, readFile, writeFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { build } from 'vite'
import react from '@vitejs/plugin-react'
import { chromium } from '@playwright/test'

const component = fileURLToPath(new URL('./BehaviorWorkspace.tsx', import.meta.url))
const output = path.resolve('test-results/t06-behavior-ui-r2')
const fixture = `
import React, {useMemo, useRef, useState} from 'react';
import {createRoot} from 'react-dom/client';
import {BehaviorWorkspace} from ${JSON.stringify(component)};
const draft={id:'B',name:'风险巡检',description:'设备出现高危告警时在隔离副本建单',trigger:'alarm',conditions:[{kind:'equals',object:'T1',property:'P',value:{kind:'boolean',value:false}}],actions:[{kind:'update',object:'T1',property:'P',value:{kind:'boolean',value:true}},{kind:'notify',message:'巡检通知'}],effect:'创建内部通知',enabled:true,priority:0,version:1};
const catalog={objects:['T1','W-test'],classes:['TestObject','Notification'],properties:[{id:'P',kind:'single'},{id:'links',kind:'multi'}],behaviorIds:[]};
function value(binding,mode,conditionKind='equals'){
  const state=['failed','cancelled'].includes(mode)?mode:mode==='history'?'completed':'candidate';
  const actionState=state==='completed'?'applied':['failed','cancelled'].includes(state)?'rolled_back':mode==='invalid'?'applied':'planned';
  const notificationState=state==='completed'?'recorded':['failed','cancelled'].includes(state)?'discarded':mode==='invalid'?'recorded':'candidate';
  return {binding,runId:'fixture-run',state,committed:state==='completed',freshness:mode==='history'?'historical':'current',freshnessDetail:mode==='history'?'历史输入快照，仅供查看':'',assertionVersion:'fixture-A1',inferenceVersion:'fixture-I1',semanticsVersion:'fixture-E1',
    conditions:[{eventId:'E1',behaviorId:'B',triggered:true,reason:conditionKind==='always'?'显式恒真，未附加对象条件':'冻结快照 T1.P=false'},{eventId:'E2',behaviorId:'B',triggered:false,reason:'条件不满足'}],
    actions:[{eventId:'E1',behaviorId:'B',index:0,kind:'update',state:actionState,detail:'T1.P=true'},{eventId:'E1',behaviorId:'B',index:1,kind:'notify',state:['failed','cancelled'].includes(state)?'skipped':actionState,detail:'关联 E1'}],
    diff:{added:[{object:'T1',property:'P',value:{kind:'boolean',value:true}}],removed:[{object:'T1',property:'P',value:{kind:'boolean',value:false}}]},
    notifications:[{eventId:'E1',behaviorId:'B',message:'<img src=x onerror=alert(1)>',state:notificationState}],error:state==='failed'?'conflict':null};
}
function Fixture(){
  const [mode,setMode]=useState('none');const [lastDraft,setLastDraft]=useState('');const [lastConditions,setLastConditions]=useState([]);const [receivedConditions,setReceivedConditions]=useState([]);const [runCount,setRunCount]=useState(0);const [project,setProject]=useState('fixture-project');const sampleRef=useRef(null);
  const services=useMemo(()=>mode==='none'?{}:{
    runSample:async(request)=>{sampleRef.current=request;setRunCount(count=>count+1);setReceivedConditions(request.draft.conditions);if(mode==='pending')await new Promise(r=>setTimeout(r,300));return value(request.binding,mode,request.draft.conditions[0].kind);},
    refreshResult:async(binding)=>({...value(binding,mode,sampleRef.current?.draft.conditions[0].kind),freshness:'stale',freshnessDetail:'夹具：上游行为版本已改变'}),
    cancelSample:async(binding)=>value(binding,'cancelled',sampleRef.current?.draft.conditions[0].kind)
  },[mode]);
  return <><aside style={{padding:16,background:'#fff8e8'}}>开发验证夹具 · 非引擎结果 · 不接入产品<nav style={{display:'flex',gap:8,flexWrap:'wrap'}}>{['none','candidate','failed','cancelled','history','pending','invalid'].map(x=><button key={x} onClick={()=>setMode(x)}>{'夹具 '+x}</button>)}<button onClick={()=>setProject('fixture-project-2')}>切换夹具项目</button></nav><output aria-label='宿主草稿'>{lastDraft}</output><output aria-label='宿主条件'>{JSON.stringify(lastConditions)}</output><output aria-label='送达条件'>{JSON.stringify(receivedConditions)}</output><output aria-label='测试调用次数'>{runCount}</output></aside><BehaviorWorkspace context={{projectId:project,inputVersion:'fixture-V1',behaviorVersion:'fixture-B1',scopeId:'fixture-isolated'}} catalog={catalog} initialDraft={draft} services={services} onDraftChange={value=>{setLastDraft(value.name);setLastConditions(value.conditions);}}/></>};
createRoot(document.getElementById('root')).render(<Fixture/>);
`
await build({
  configFile: false,
  plugins: [
    react(),
    {
      name: 't06-fixture',
      resolveId: (id) => (id.endsWith('virtual:t06-preview') ? '\0t06-preview.tsx' : undefined),
      load: (id) => (id === '\0t06-preview.tsx' ? fixture : undefined),
    },
  ],
  define: { 'process.env.NODE_ENV': JSON.stringify('production') },
  build: {
    outDir: output,
    emptyOutDir: true,
    minify: false,
    cssCodeSplit: false,
    lib: {
      entry: 'virtual:t06-preview',
      formats: ['es'],
      fileName: () => 'preview.js',
      cssFileName: 'preview',
    },
  },
})
await writeFile(
  path.join(output, 'index.html'),
  '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>T06 私有组件验证夹具</title><link rel="stylesheet" href="/preview.css"><body style="margin:0"><div id="root"></div><script type="module" src="/preview.js"></script></body></html>',
)
const server = createServer(async (request, response) => {
  const files = {
    '/': 'index.html',
    '/preview.js': 'preview.js',
    '/preview.css': 'preview.css',
  }
  const filename = files[request.url]
  if (!filename) {
    response.writeHead(404)
    response.end()
    return
  }
  try {
    response.setHeader(
      'Content-Type',
      filename.endsWith('.js')
        ? 'text/javascript'
        : filename.endsWith('.css')
          ? 'text/css'
          : 'text/html',
    )
    response.end(await readFile(path.join(output, filename)))
  } catch {
    response.writeHead(500)
    response.end()
  }
})
let browser
const evidence = { fixtureOnly: true, gui: false, checks: [], screenshots: [] }
try {
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve))
  const port = server.address().port
  browser = await chromium.launch({ headless: true })
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } })
  page.setDefaultTimeout(10000)
  const errors = []
  page.on('pageerror', (error) => errors.push(error.message))
  await page.goto(`http://127.0.0.1:${port}/`)
  const workspace = page.getByRole('region', { name: '把业务规则，写成可验证的行动。' })
  await workspace.waitFor()
  await page.getByLabel('唯一行为 ID', { exact: true }).focus()
  await page.keyboard.press('Tab')
  assert.equal(
    await page
      .getByLabel('行为名称', { exact: true })
      .evaluate((element) => document.activeElement === element),
    true,
  )
  assert.equal(
    await page.getByRole('button', { name: '在隔离副本中测试', exact: true }).isDisabled(),
    true,
  )
  assert.ok(await page.getByText('隔离执行能力待接入。', { exact: false }).isVisible())
  await page.getByLabel('唯一事件 ID', { exact: true }).fill('E1')
  await page.getByLabel('事件类型', { exact: true }).fill('alarm')
  await page.getByRole('button', { name: '检查本地结构', exact: true }).click()
  await page.getByRole('status').filter({ hasText: '本地结构检查通过' }).waitFor()
  evidence.checks.push('未接入服务禁用执行；本地检查有独立边界')
  const conditionType = () =>
    page
      .getByRole('group', { name: '条件 1', exact: true })
      .getByRole('combobox', { name: '条件类型', exact: true })
  await conditionType().selectOption('always')
  assert.equal(await page.getByLabel('条件对象 ID', { exact: true }).count(), 0)
  assert.equal(await page.getByLabel('条件属性 ID', { exact: true }).count(), 0)
  assert.equal(
    await page.getByLabel('宿主条件', { exact: true }).textContent(),
    '[{"kind":"always"}]',
  )
  await page.getByRole('button', { name: '移除条件 1', exact: true }).click()
  await page.getByRole('button', { name: '检查本地结构', exact: true }).click()
  await page
    .getByRole('list', { name: '本地结构问题', exact: true })
    .filter({ hasText: 'conditions' })
    .waitFor()
  await page.getByRole('button', { name: '＋ 添加条件', exact: true }).click()
  await conditionType().selectOption('always')
  await page.getByRole('button', { name: '检查本地结构', exact: true }).click()
  await page.getByRole('status').filter({ hasText: '本地结构检查通过' }).waitFor()
  evidence.checks.push('显式always无伪造对象字段且回调保真；空条件仍拒绝，重新选择always可验证')

  await page.getByRole('button', { name: '＋ 添加事实变更', exact: true }).click()
  await page.getByLabel('事实对象 ID', { exact: true }).fill('T1')
  await page.getByLabel('事实属性 ID', { exact: true }).fill('P')
  await writeFile(
    path.join(output, 'debug-structure.txt'),
    await page.locator('body').ariaSnapshot(),
  )
  await page
    .getByRole('group', { name: '事实变更 1', exact: true })
    .getByRole('combobox', { name: '值类型', exact: true })
    .selectOption('boolean')
  await page.getByRole('button', { name: '夹具 candidate', exact: true }).click()
  await page.getByRole('button', { name: '在隔离副本中测试', exact: true }).click()
  await page.getByText('候选计划 · 尚未提交 / 当前输入', { exact: true }).waitFor()
  assert.ok(
    await page.getByText('E1 / B · 触发 · 显式恒真，未附加对象条件', { exact: true }).isVisible(),
  )
  assert.ok(await page.getByText('E2 / B · 未触发 · 条件不满足', { exact: true }).isVisible())
  const actions = page
    .getByRole('heading', { name: '动作轨迹（服务返回顺序）', exact: true })
    .locator('..')
    .getByRole('listitem')
  assert.deepEqual(await actions.allTextContents(), [
    'E1 / B · 动作 1 · 更新属性 · 计划 · T1.P=true',
    'E1 / B · 动作 2 · 通知记录 · 计划 · 关联 E1',
  ])
  assert.equal(await page.locator('img').count(), 0)
  assert.equal(
    await page.getByLabel('送达条件', { exact: true }).textContent(),
    '[{"kind":"always"}]',
  )
  await page.getByLabel('行为名称', { exact: true }).fill('刷新必须保留的草稿')
  await page.getByRole('button', { name: '刷新此运行', exact: true }).click()
  await page.getByText('夹具：上游行为版本已改变', { exact: true }).waitFor()
  assert.equal(
    await page.getByLabel('行为名称', { exact: true }).inputValue(),
    '刷新必须保留的草稿',
  )
  assert.equal(
    await page.getByLabel('宿主草稿', { exact: true }).textContent(),
    '刷新必须保留的草稿',
  )
  assert.ok(await page.getByText('草稿或样本已修改；', { exact: false }).isVisible())
  evidence.checks.push(
    '事件事实变更可编辑；候选不冒充提交；完整触发/动作/通知文本安全；刷新保留草稿并标记旧依据',
  )

  await page.getByRole('button', { name: '夹具 invalid', exact: true }).click()
  await page.getByRole('button', { name: '刷新此运行', exact: true }).click()
  await page.getByRole('status').filter({ hasText: '已拒绝显示' }).waitFor()
  assert.ok(await page.getByText('候选计划 · 尚未提交 / 已过期', { exact: true }).isVisible())
  assert.deepEqual(await actions.allTextContents(), [
    'E1 / B · 动作 1 · 更新属性 · 计划 · T1.P=true',
    'E1 / B · 动作 2 · 通知记录 · 计划 · 关联 E1',
  ])
  await page.getByRole('button', { name: '在隔离副本中测试', exact: true }).click()
  await page.getByRole('status').filter({ hasText: '已拒绝显示' }).waitFor()
  await page.getByText('尚无可核验的运行结果', { exact: true }).waitFor()
  evidence.checks.push(
    '矛盾candidate+applied/recorded被拒；刷新保留上次有效结果，新请求不显示矛盾证据',
  )
  const countBeforeReserved = await page.getByLabel('测试调用次数', { exact: true }).textContent()
  for (const payload of ['{"__proto__":"first"}', '{"__proto__":"second"}']) {
    await page.getByRole('textbox', { name: '事件内容（JSON 对象）', exact: true }).fill(payload)
    await page.getByRole('button', { name: '在隔离副本中测试', exact: true }).click()
    await page
      .getByRole('list', { name: '本地结构问题', exact: true })
      .filter({ hasText: '保留键' })
      .waitFor()
    assert.equal(
      await page.getByLabel('测试调用次数', { exact: true }).textContent(),
      countBeforeReserved,
    )
  }
  await page.getByRole('textbox', { name: '事件内容（JSON 对象）', exact: true }).fill('{}')
  evidence.checks.push('同事件两份不同__proto__载荷均显示问题且不调用执行，未静默丢值')
  for (const [mode, expected] of [
    ['failed', '运行失败 · 本轮未提交 / 当前输入'],
    ['cancelled', '运行已取消 · 本轮未提交 / 当前输入'],
    ['history', '隔离副本已提交 / 历史结果'],
  ]) {
    await page.getByRole('button', { name: `夹具 ${mode}`, exact: true }).click()
    await page.getByRole('button', { name: '在隔离副本中测试', exact: true }).click()
    await page.getByText(expected, { exact: true }).waitFor()
  }
  evidence.checks.push('失败、已取消、历史状态分别展示，不生成假通过')
  await page.getByRole('button', { name: '夹具 pending', exact: true }).click()
  await page.getByRole('button', { name: '在隔离副本中测试', exact: true }).click()
  await page.getByRole('button', { name: '请求取消测试', exact: true }).click()
  await page.getByText('运行已取消 · 本轮未提交 / 当前输入', { exact: true }).waitFor()
  await page.waitForTimeout(400)
  assert.ok(await page.getByText('运行已取消 · 本轮未提交 / 当前输入', { exact: true }).isVisible())
  evidence.checks.push('实际组件取消入口等待确认；拒绝迟到完成覆盖取消')
  for (const width of [1440, 390]) {
    await page.setViewportSize({ width, height: 1000 })
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth))
    const filename = `width-${width}.png`
    await page.screenshot({ path: path.join(output, filename), fullPage: true })
    evidence.screenshots.push(filename)
    if (width === 390) {
      await page.screenshot({ path: path.join(output, 'viewport-390.png') })
      evidence.screenshots.push('viewport-390.png')
    }
  }
  await page.getByRole('button', { name: '切换夹具项目', exact: true }).click()
  assert.equal(await page.getByLabel('行为名称', { exact: true }).inputValue(), '风险巡检')
  await page.getByText('尚无可核验的运行结果', { exact: true }).waitFor()
  assert.deepEqual(errors, [])
  evidence.checks.push('1440/390无横向溢出；切项目清除旧结果并载入对应草稿；无pageerror')
  await mkdir(output, { recursive: true })
  await writeFile(path.join(output, 'evidence.json'), JSON.stringify(evidence, null, 2))
  process.stdout.write(JSON.stringify(evidence, null, 2) + '\n')
} finally {
  await browser?.close()
  await new Promise((resolve, reject) =>
    server.close((error) => (error ? reject(error) : resolve())),
  )
}
