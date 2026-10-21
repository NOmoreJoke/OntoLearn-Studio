// No browser/Electron/window. Static markup checks; not interaction/CSP evidence.
import ts from 'typescript'
import { createRequire } from 'node:module'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import path from 'node:path'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../..')
const require = createRequire(path.join(root, 'package.json'))
const original = {
  '.ts': require.extensions['.ts'],
  '.tsx': require.extensions['.tsx'],
  '.css': require.extensions['.css'],
}
const compile = (source, filename) =>
  ts.transpileModule(source, {
    fileName: filename,
    compilerOptions: {
      target: ts.ScriptTarget.ES2022,
      module: ts.ModuleKind.CommonJS,
      jsx: ts.JsxEmit.ReactJSX,
      esModuleInterop: true,
    },
  }).outputText
for (const extension of ['.ts', '.tsx'])
  require.extensions[extension] = (mod, filename) =>
    mod._compile(compile(readFileSync(filename, 'utf8'), filename), filename)
require.extensions['.css'] = () => {}
try {
  const source = `
      import assert from 'node:assert/strict'
      import { renderToStaticMarkup } from 'react-dom/server'
      import fixtures from './packages/contracts/v2/fixtures.json'
      import { QueryPage } from './apps/desktop/src/renderer/src/query/QueryPage'
      const id = (n) => '00000000-0000-4000-8000-' + String(n).padStart(12, '0')
      const hash = 'a'.repeat(64)
      const catalog = { classes: [], predicates: [] }
      const offline = renderToStaticMarkup(<QueryPage projectId={id(1)} catalog={catalog} />)
      for (const text of ['真实查询服务尚未接入', '草稿尚未持久化', '模板和草稿不会生成示例结果', '当前已提交输入', '断言事实＋当前推导结果']) assert(offline.includes(text), text)
      const metadata = {projectId:id(1), resultId:id(2),jobId:id(3),kind:'query',definitionId:'Q-01',inputSnapshotId:hash,inputProjectRevision:3,dependencyVector:{'facts:asserted':3},definitionSetDigests:{},implementation:{executionSemanticsVersion:'v1',engineVersion:'0.1.0',dependencyLockHash:hash},scope:'asserted',parametersHash:hash,state:'historical',staleReason:[],payloadStatus:'available',createdAtMs:1,historicalSelectionRequired:true}
      const binding = {projectId:id(1),resultId:id(2),inputSnapshotId:hash,scope:'asserted',parametersHash:hash,order:'ordinal+rowId:asc'}
      const page = {binding,rows:[{rowId:id(4),ordinal:0,cells:['<script>alert(1)</script>']}],nextCursor:null}
      const result = {metadata,page,columns:['告警'],executedSparql:'SELECT ?alarm WHERE { ?alarm a <urn:t04:Alarm> }'}
      const render = (r, projectId=id(1)) => renderToStaticMarkup(<QueryPage projectId={projectId} catalog={catalog} result={r} />)
      const html = render(result)
      assert(html.includes('&lt;script&gt;alert(1)&lt;/script&gt;'))
      assert(!html.includes('<script>'))
      assert(html.includes(hash) && html.includes('历史结果') && html.includes('本次实际执行的 SPARQL'))
      const empty = render({...result,page:{...page,rows:[]}})
      assert(empty.includes('不能据此证明业务事实不存在'))
      assert(empty.includes('筛选值'))
      const rejected = render(result,id(20))
      assert(rejected.includes('结果身份、范围或分页不匹配'))
      assert(!rejected.includes('alert(1)'))
      const evicted = render({...result,metadata:{...metadata,payloadStatus:'evicted'},page:null})
      assert(evicted.includes('载荷已回收') && evicted.includes(hash))
      const baseJob = fixtures.cases.find(entry => entry.name === 'response job.get').value.result
      const queryJob = { ...baseJob, capability:'query.execute',scope:'asserted',commitProgress:{mode:'none'},input:{...baseJob.input,scope:'asserted'},state:'running',finishedAtMs:null }
      const wrongJob = renderToStaticMarkup(<QueryPage projectId={id(1)} catalog={catalog} job={{...queryJob,capability:'reasoning.execute'}} onExecuteDraft={async()=>{}} onCancelJob={async()=>{}} />)
      assert(!wrongJob.includes('查询任务：') && !wrongJob.includes('取消查询'))
      assert(wrongJob.includes('<button>执行查询</button>'))
      const matchingJob = renderToStaticMarkup(<QueryPage projectId={id(1)} catalog={catalog} job={queryJob} onCancelJob={async()=>{}} />)
      assert(matchingJob.includes('取消查询') && matchingJob.includes('运行中'))
      const previousResult = renderToStaticMarkup(<QueryPage projectId={id(1)} catalog={catalog} job={{...queryJob,jobId:id(10)}} result={result} />)
      assert(previousResult.includes('此前查询结果；与上方当前任务属于不同运行'))
      const acknowledged = renderToStaticMarkup(<QueryPage projectId={id(1)} catalog={catalog} job={queryJob} cancellationRequest={{jobId:queryJob.jobId}} onCancelJob={async()=>{}} resultLoading />)
      assert(acknowledged.includes('取消请求已受理，等待真实任务终态。'))
      assert(acknowledged.includes('<button disabled="">取消查询</button>'))
      assert(acknowledged.includes('aria-busy="true"') && acknowledged.includes('正在读取固定结果页'))
      const unrelatedAck = renderToStaticMarkup(<QueryPage projectId={id(1)} catalog={catalog} job={queryJob} cancellationRequest={{jobId:id(20)}} onCancelJob={async()=>{}} />)
      assert(!unrelatedAck.includes('取消请求已受理，等待真实任务终态。'))
      assert(unrelatedAck.includes('<button>取消查询</button>'))
      console.log(JSON.stringify({probe:'T04 static SSR',checks:['offline-disabled','scope-visible','text-escaped','historical-identity','executed-query','empty-directions','project-rejection','evicted-identity','non-query-job-rejection','query-job-accepted','previous-result-labeled','cancel-ack-separate','cancel-ack-bound-to-job','result-loading-visible'],passed:true,boundary:'No browser interaction, CSP, real executor or persistence tested'}))
`
  const mod = { exports: {} }
  new Function(
    'require',
    'module',
    'exports',
    compile(source, path.join(root, 't04-ssr-probe.tsx')),
  )(require, mod, mod.exports)
} finally {
  for (const [extension, handler] of Object.entries(original)) {
    if (handler) require.extensions[extension] = handler
    else delete require.extensions[extension]
  }
}
