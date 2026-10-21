import assert from 'node:assert/strict'
import path from 'node:path'
import {createRequire} from 'node:module'
import {pathToFileURL} from 'node:url'
const root='/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-behavior-ui'
const require=createRequire(path.join(root,'package.json'))
const {build}=await import(pathToFileURL(require.resolve('vite')).href)
const entry='virtual:t06-readonly-negative'
const source=['model','controller','presentation'].map(name=>`export * from ${JSON.stringify(path.join(root,'apps/desktop/src/renderer/src/behavior',name+'.ts'))};`).join('\n')
const built=await build({root,configFile:false,logLevel:'silent',plugins:[{name:'readonly-review',resolveId:id=>id.endsWith(entry)?'\0readonly.ts':undefined,load:id=>id==='\0readonly.ts'?source:undefined}],build:{write:false,minify:false,lib:{entry,formats:['es']}}})
const code=(Array.isArray(built)?built[0]:built).output.find(x=>x.type==='chunk'&&x.isEntry).code
const m=await import('data:text/javascript;base64,'+Buffer.from(code).toString('base64'))
const context={projectId:'P',inputVersion:'V1',behaviorVersion:'B1',scopeId:'scope'}
const catalog={objects:['T1'],classes:['TestObject'],properties:[{id:'P',kind:'single'}],behaviorIds:[]}
const draft={id:'X',name:'X',description:'PRD X',trigger:'E-B06',conditions:[],actions:[{kind:'update',object:'T1',property:'P',value:{kind:'boolean',value:true}}],effect:'update P',enabled:true,priority:0,version:1}
assert.deepEqual(m.validateDraft(draft,catalog),[{path:'conditions',message:'请填写完整且有效的值'}])
console.log('P2 unconditional behavior: rejected; no explicit always variant exists')
const value={binding:{...context,requestId:'req'},runId:'R',state:'candidate',committed:false,freshness:'current',freshnessDetail:'',assertionVersion:'A',inferenceVersion:'I',semanticsVersion:'E',conditions:[],actions:[{eventId:'E1',behaviorId:'X',index:0,kind:'update',state:'applied',detail:'T1.P=true'}],diff:{added:[],removed:[]},notifications:[{eventId:'E1',behaviorId:'X',message:'notification',state:'recorded'}],error:null}
assert.equal(m.resultSchema.safeParse(value).success,true)
const c=new m.BehaviorController(context,catalog,{...draft,conditions:[{kind:'exists',object:'T1',property:'P'}]},{runSample:async req=>({...value,binding:req.binding})})
c.editEvents([{id:'E1',type:'E-B06',payload:'{}',changes:[]}])
await c.run()
assert.equal(c.getSnapshot().result?.actions[0].state,'applied')
assert.equal(c.getSnapshot().result?.notifications[0].state,'recorded')
console.log('P2 inconsistent result: accepted and displayed',m.resultHeading(value),m.resultSections(value))
const input={id:'E1',type:'test',changes:[]}
const a=m.parseEvents([{...input,payload:'{"__proto__":"first"}'}])
const b=m.parseEvents([{...input,payload:'{"__proto__":"second"}'}])
assert.deepEqual(a,b)
assert.deepEqual(a.issues,[])
assert.deepEqual(a.events[0].payload,{})
console.log('P2 payload content loss:',JSON.stringify(a))
