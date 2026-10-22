import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';

export function coverageVerdict(results, required) {
 const missing=[];
 for(const item of required.actions){
  const matches=results.filter(r=>r.name===item.id);
  if(matches.length < (item.minimumRecords||1))missing.push(item.id);
  if(item.requiredVariants){
   const observed=new Set(matches.map(r=>JSON.stringify(item.requiredVariants.keys.map(k=>r[k]))));
   for(const variant of item.requiredVariants.values){if(!observed.has(JSON.stringify(variant)))missing.push(item.id+':'+JSON.stringify(variant));}
  }
 }
 // Unavailable required controls remain open; never silently turn them into pass.
 for(const item of required.openRequiredControls||[])missing.push(item.id);
 return {passed:missing.length===0,mandatoryUnverified:missing,unverifiedControls:required.unverifiedControls||[]};
}

async function queryCoverage(page,record){
 const check=(v,m)=>{if(!v)throw Error(m)};
 await page.getByRole('button',{name:'本体查询',exact:true}).click();
 await page.getByRole('button',{name:'重置当前页草稿',exact:true}).click();
 const choose=page.getByRole('combobox',{name:'选择对象',exact:true});
 const generate=page.getByRole('button',{name:'生成可见 SPARQL 草稿',exact:true});
 const text=page.getByRole('textbox',{name:'SPARQL',exact:true});
 const base='SELECT DISTINCT ?item ?field0 WHERE {\n  ?item a <https://stage.example/Sensor> .\n  OPTIONAL { ?item <https://stage.example/temperature> ?field0 . }\n}\nORDER BY ?item ?field0';
 await choose.selectOption({label:'传感器'});
 await page.getByRole('checkbox',{name:'温度',exact:true}).check();
 await generate.click();
 check(await text.inputValue()===base,'C4_FULL_SPARQL_BASELINE');
 record('c4-query-full-independent-text',{actual:await text.inputValue(),expected:base});
 const edited='ASK { <urn:c4:subject> <urn:c4:predicate> "edited" . }';
 await text.fill(edited); await text.blur();
 check(await text.inputValue()===edited,'C4_QUERY_CONTROLLED_EDIT');
 check(await page.getByRole('button',{name:'执行查询',exact:true}).isDisabled(),'C4_QUERY_EDIT_EXECUTED');
 record('c4-query-controlled-edit',{actual:await text.inputValue()});
 const template=page.getByRole('button',{name:'模板：未闭环高危告警',exact:true});
 check(await template.isEnabled(),'C4_EXISTING_TEMPLATE_UNAVAILABLE');
 await template.click();
 const templateExpected='SELECT DISTINCT ?item ?field0 ?field1 WHERE {\n  ?item a <https://stage.example/Alarm> .\n  ?item <https://stage.example/severity> ?condition0 .\n  FILTER (?condition0 = "High")\n  ?item <https://stage.example/status> ?condition1 .\n  FILTER (?condition1 = "Open")\n  OPTIONAL { ?item <https://stage.example/severity> ?field0 . }\n  OPTIONAL { ?item <https://stage.example/status> ?field1 . }\n}\nORDER BY ?item ?field0 ?field1';
 check(await text.inputValue()===templateExpected,'C4_EXISTING_TEMPLATE_FULL_TEXT');
 record('c4-template-existing-synthetic-vocabulary',{actual:await text.inputValue(),expected:templateExpected,vocabularyInjected:false});
 await page.getByRole('button',{name:'重置当前页草稿',exact:true}).click();
 await choose.selectOption({label:'传感器'});await page.getByRole('checkbox',{name:'温度',exact:true}).check();
 await text.fill(edited);await text.blur();
 await page.getByRole('button',{name:'添加条件',exact:true}).click();
 check(await page.getByLabel('条件 1 属性',{exact:true}).inputValue()==='','C4_CONDITION_DEFAULT');
 await generate.click();
 check(await text.inputValue()===edited,'C4_MISSING_PREDICATE_REPLACED_DRAFT');
 check(await page.getByText('无法生成查询。请选择有效对象、属性和 RDF 条件值。',{exact:true}).isVisible(),'C4_MISSING_PREDICATE_NOTICE');
 record('c4-query-missing-predicate-refused');
 await page.getByLabel('条件 1 属性',{exact:true}).selectOption({label:'温度'});
 const value=()=>page.getByLabel('条件 1 值',{exact:true});
 const operator=page.getByLabel('条件 1 运算符',{exact:true});
 const expectedWith=(condition)=>'SELECT DISTINCT ?item ?field0 WHERE {\n  ?item a <https://stage.example/Sensor> .\n'+condition+'\n  OPTIONAL { ?item <https://stage.example/temperature> ?field0 . }\n}\nORDER BY ?item ?field0';
 // Independent fixed operator table and fixed lexical "42" expectations.
 const expectations={eq:'=',ne:'!=',lt:'<',le:'<=',gt:'>',ge:'>='};
 for(const [op,symbol] of Object.entries(expectations)){
  await operator.selectOption(op);await value().fill('42');await generate.click();
  const expected=expectedWith('  ?item <https://stage.example/temperature> ?condition0 .\n  FILTER (?condition0 '+symbol+' "42")');
  check(await text.inputValue()===expected,'C4_OPERATOR_FULL_TEXT '+op);
  record('c4-query-value-operator',{operator:op,actual:await text.inputValue(),expected});
 }
 for(const op of ['exists','not-exists']){
  await operator.selectOption(op);check(await value().count()===0,'C4_EXISTS_HAS_VALUE_EDITOR');await generate.click();
  const expected=expectedWith('  FILTER '+(op==='not-exists'?'NOT ':'')+'EXISTS { ?item <https://stage.example/temperature> ?condition0 . }');
  check(await text.inputValue()===expected,'C4_EXISTS_FULL_TEXT '+op);
  record('c4-query-no-value-operator',{operator:op,actual:await text.inputValue(),expected});
 }
 await operator.selectOption('eq');
 await page.getByLabel('条件 1 RDF 类型',{exact:true}).selectOption('iri');
 await value().fill('urn:c4:valid');await generate.click();
 const validIri=expectedWith('  ?item <https://stage.example/temperature> ?condition0 .\n  FILTER (?condition0 = <urn:c4:valid>)');
 check(await text.inputValue()===validIri,'C4_RDF_IRI_VALUE');
 await value().fill('invalid iri >');await generate.click();
 check(await text.inputValue()===validIri,'C4_INVALID_IRI_REPLACED_DRAFT');
 check(await page.getByText('无法生成查询。请选择有效对象、属性和 RDF 条件值。',{exact:true}).isVisible(),'C4_INVALID_IRI_NOT_REFUSED');
 await page.getByLabel('条件 1 RDF 类型',{exact:true}).selectOption('literal');
 await value().fill('hello');await page.getByLabel('条件 1 语言',{exact:true}).fill('zh');
 await page.getByLabel('条件 1 数据类型',{exact:true}).fill('http://www.w3.org/2001/XMLSchema#string');
 await generate.click();check(await text.inputValue()===validIri,'C4_CONFLICTING_LITERAL_ACCEPTED');
 await page.getByLabel('条件 1 数据类型',{exact:true}).fill('');await generate.click();
 const language=expectedWith('  ?item <https://stage.example/temperature> ?condition0 .\n  FILTER (?condition0 = "hello"@zh)');
 check(await text.inputValue()===language,'C4_LANGUAGE_LITERAL_TEXT');
 record('c4-query-rdf-types-and-invalid-values',{validIri,language,invalidValuesRefused:true});
 await page.getByRole('button',{name:'删除条件 1',exact:true}).click();
 check(await page.locator('.query-condition').count()===0,'C4_CONDITION_DELETE');
 await choose.selectOption('');await generate.click();
 check(await text.inputValue()===language,'C4_EMPTY_CLASS_REPLACED_DRAFT');
 check(await page.getByText('无法生成查询。请选择有效对象、属性和 RDF 条件值。',{exact:true}).isVisible(),'C4_EMPTY_CLASS_NOT_REFUSED');
 check(await page.getByText('尚未取得实际执行结果。模板和草稿不会生成示例结果。',{exact:true}).isVisible(),'C4_QUERY_FABRICATED_RESULT');
 record('c4-query-condition-delete-empty-class-and-no-result');
}

async function behaviorCoverage(page,record){
 const check=(v,m)=>{if(!v)throw Error(m)};
 await page.getByRole('button',{name:'行为定义',exact:true}).click();
 await page.getByRole('button',{name:'重置当前页草稿',exact:true}).click();
 const group=(name)=>page.getByRole('group',{name,exact:true});
 const addCondition=page.getByRole('button',{name:'＋ 添加条件',exact:true});
 await addCondition.click();const condition=group('条件 1');
 await condition.getByLabel('条件对象 ID',{exact:true}).fill('urn:c4:condition-object');
 await condition.getByLabel('条件属性 ID',{exact:true}).fill('urn:c4:condition-property');
 await condition.getByLabel('值类型',{exact:true}).selectOption('number');
 await condition.getByLabel('比较 / 写入值',{exact:true}).fill('17');
 check(await condition.getByLabel('比较 / 写入值',{exact:true}).inputValue()==='17','C4_CONDITION_EDIT');
 await condition.getByLabel('条件类型',{exact:true}).selectOption('exists');
 check(await condition.getByLabel('比较 / 写入值',{exact:true}).count()===0,'C4_CONDITION_TYPE_CHANGE');
 await addCondition.click();await group('条件 2').getByLabel('条件类型',{exact:true}).selectOption('always');
 check(await group('条件 2').getByText('显式恒真；此项不附加对象或属性限制，同组其他条件仍须满足。',{exact:true}).isVisible(),'C4_ALWAYS_DISCLOSURE');
 await page.getByRole('button',{name:'移除条件 2',exact:true}).click();
 await page.getByRole('button',{name:'移除条件 1',exact:true}).click();
 check(await page.getByRole('button',{name:/^移除条件 /}).count()===0,'C4_CONDITION_DELETE');
 record('c4-behavior-condition-add-edit-type-delete');
 const addAction=page.getByRole('button',{name:'＋ 添加动作',exact:true});
 for(let i=1;i<=2;i++){
  await addAction.click();const action=group('动作 '+i);
  await action.getByLabel('动作类型',{exact:true}).selectOption('notify');
  await action.getByLabel('通知内容',{exact:true}).fill('c4-notice-'+i);
 }
 await group('动作 2').getByRole('button',{name:'上移',exact:true}).click();
 check(await group('动作 1').getByLabel('通知内容',{exact:true}).inputValue()==='c4-notice-2','C4_ACTION_MOVE_UP');
 await group('动作 1').getByRole('button',{name:'下移',exact:true}).click();
 check(await group('动作 1').getByLabel('通知内容',{exact:true}).inputValue()==='c4-notice-1','C4_ACTION_MOVE_DOWN');
 await group('动作 1').getByLabel('动作类型',{exact:true}).selectOption('create');
 await group('动作 1').getByLabel('新对象 ID',{exact:true}).fill('urn:c4:new-object');
 await group('动作 1').getByLabel('类 ID',{exact:true}).fill('https://stage.example/Sensor');
 check(await group('动作 1').getByLabel('新对象 ID',{exact:true}).inputValue()==='urn:c4:new-object','C4_ACTION_HOLDS_EDIT');
 await page.getByRole('button',{name:'移除动作 2',exact:true}).click();
 await page.getByRole('button',{name:'移除动作 1',exact:true}).click();
 check(await page.getByRole('button',{name:/^移除动作 /}).count()===0,'C4_ACTION_DELETE');
 record('c4-behavior-action-add-edit-reorder-delete');
 // One initial sample event is provided by the frozen component.
 await page.getByRole('button',{name:'＋ 添加样本事件',exact:true}).click();
 for(let i=1;i<=2;i++){
  const event=group('事件 '+i);
  await event.getByLabel('唯一事件 ID',{exact:true}).fill('c4-event-'+i);
  await event.getByLabel('事件类型',{exact:true}).fill('C4Synthetic');
  await event.getByLabel('事件内容（JSON 对象）',{exact:true}).fill('{"sequence":'+i+'}');
 }
 await group('事件 2').getByRole('button',{name:'事件上移',exact:true}).click();
 check(await group('事件 1').getByLabel('唯一事件 ID',{exact:true}).inputValue()==='c4-event-2','C4_EVENT_UP');
 await group('事件 1').getByRole('button',{name:'事件下移',exact:true}).click();
 check(await group('事件 1').getByLabel('唯一事件 ID',{exact:true}).inputValue()==='c4-event-1','C4_EVENT_DOWN');
 await page.getByRole('button',{name:'移除事件 2',exact:true}).click();
 check(await page.getByRole('button',{name:/^移除事件 /}).count()===1,'C4_EVENT_DELETE');
 record('c4-behavior-event-add-edit-reorder-delete');
 const payload=group('事件 1').getByLabel('事件内容（JSON 对象）',{exact:true});
 const validate=page.getByRole('button',{name:'检查本地结构',exact:true});
 await payload.fill('{broken');await validate.click();
 check((await page.getByRole('list',{name:'本地结构问题',exact:true}).innerText()).includes('事件内容须为有限大小的 JSON 对象'),'C4_INVALID_JSON_NOT_REFUSED');
 await payload.fill('{"constructor":"forbidden"}');await validate.click();
 check((await page.getByRole('list',{name:'本地结构问题',exact:true}).innerText()).includes('事件内容包含保留键'),'C4_RESERVED_KEY_NOT_REFUSED');
 await payload.fill('{}');await validate.click();
 const issues=page.getByRole('list',{name:'本地结构问题',exact:true});
 check(await issues.count()===0 || !(await issues.innerText()).includes('事件内容包含保留键'),'C4_CORRECTED_PAYLOAD_STALE_ERROR');
 check(await page.getByRole('button',{name:'在隔离副本中测试',exact:true}).isDisabled(),'C4_BEHAVIOR_EXECUTOR_ENABLED');
 check(await page.getByText('尚无可核验的运行结果',{exact:true}).isVisible(),'C4_BEHAVIOR_FABRICATED_RUN');
 record('c4-behavior-json-reserved-key-structure-no-run');
}
export async function run(c){
const {chromium}=await import(pathToFileURL(c.module));
const results=[],requests=[],errors=[];
let browser,context,firstFailure=null,ownedClosed=false;
const check=(ok,m)=>{if(!ok)throw Error(m)};
const record=(name,value={})=>results.push({name,...value});
async function controlCheck(page,locator,label){
 await locator.evaluate(el=>el.scrollIntoView({block:'center',inline:'nearest',behavior:'instant'}));
 await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
 const m=await locator.evaluate(el=>{
  const r=el.getBoundingClientRect();let clip={left:0,right:innerWidth,top:0,bottom:innerHeight};
  for(let p=el.parentElement;p;p=p.parentElement){const s=getComputedStyle(p),b=p.getBoundingClientRect();if(/hidden|clip|scroll|auto/.test(s.overflowX)){clip.left=Math.max(clip.left,b.left+p.clientLeft);clip.right=Math.min(clip.right,b.left+p.clientLeft+p.clientWidth)}if(/hidden|clip|scroll|auto/.test(s.overflowY)){clip.top=Math.max(clip.top,b.top+p.clientTop);clip.bottom=Math.min(clip.bottom,b.top+p.clientTop+p.clientHeight)}}
  const x=(r.left+r.right)/2,y=(r.top+r.bottom)/2,hit=document.elementFromPoint(x,y);
  return {rect:{left:r.left,right:r.right,top:r.top,bottom:r.bottom,width:r.width,height:r.height},clip,hit:!!hit&&(hit===el||el.contains(hit)),within:r.left>=clip.left-1&&r.right<=clip.right+1&&r.top>=clip.top-1&&r.bottom<=clip.bottom+1};
 });
 check(m.within,'CONTROL_CLIPPED '+label+' '+JSON.stringify(m));check(m.hit,'CONTROL_NOT_HITTABLE '+label+' '+JSON.stringify(m));return m;
}
try{
 browser=await chromium.launch({executablePath:c.browser,headless:true,chromiumSandbox:true,downloadsPath:path.join(c.out,'downloads'),tracesDir:path.join(c.work,'traces'),env:{...process.env,TMPDIR:path.join(c.work,'tmp'),TMP:path.join(c.work,'tmp'),TEMP:path.join(c.work,'tmp'),XDG_CACHE_HOME:path.join(c.work,'cache'),XDG_CONFIG_HOME:path.join(c.work,'config')}});
 context=await browser.newContext({acceptDownloads:true,viewport:{width:1440,height:1000}});
 await context.route('**/*',route=>{const u=route.request().url();if(/^(file:|data:|blob:)/.test(u))return route.continue();requests.push({url:u,blocked:true});return route.abort('blockedbyclient')});
 const page=await context.newPage();page.setDefaultTimeout(5000);page.on('pageerror',e=>errors.push(String(e)));
 await page.goto(pathToFileURL(c.index).href,{waitUntil:'load',timeout:15000});
 check(page.url()===pathToFileURL(c.index).href,'WRONG_OWN_PAGE');check((await page.title()).includes('阶段验收'),'WRONG_TITLE');
 check((await page.locator('meta[http-equiv="Content-Security-Policy"]').getAttribute('content')).includes("connect-src 'none'"),'CSP_CONNECT_POLICY');
 record('owned-launch',{session:c.session,url:page.url(),processOwnedLaunch:true,connectOrCDP:false});
 for(const width of [1440,390]){
  await page.setViewportSize({width,height:1000});
  for(const module of ['本体构建','本体查询','行为定义','离线学习']){
   await page.getByRole('button',{name:module,exact:true}).click();
   const m=await page.evaluate(()=>{
    const box=el=>{const r=el.getBoundingClientRect(),s=getComputedStyle(el);return {left:r.left,right:r.right,width:r.width,scrollWidth:el.scrollWidth,clientWidth:el.clientWidth,overflowX:s.overflowX}};
    const sels=['.stage-surface','.learning-grid','.learning-path','.learning-task','.learning-reference','.ontology-workbench','.query-layout','.behavior-columns'];
    return {document:document.documentElement.scrollWidth,body:document.body.scrollWidth,vw:innerWidth,boxes:sels.map(sel=>{const el=document.querySelector(sel);return el?{sel,...box(el)}:null}).filter(Boolean)};
   });
   check(m.document<=width&&m.body<=width,'DOCUMENT_OVERFLOW '+module);
   for(const b of m.boxes){check(b.left>=-1&&b.right<=width+1,'INNER_CONTAINER_CLIPPED '+module+' '+JSON.stringify(b));check(b.scrollWidth<=b.clientWidth+1,'INNER_CONTAINER_SCROLL_OVERFLOW '+module+' '+JSON.stringify(b))}
   const controls=page.locator('.stage-surface button:visible,.stage-surface input:visible,.stage-surface textarea:visible,.stage-surface select:visible,.stage-surface summary:visible');let controlResults=[];
   for(let i=0;i<await controls.count();i++){
    const el=controls.nth(i);if(await el.evaluate(e=>!!e.closest('.learning-path ol')))continue;
    const label=await el.evaluate(e=>e.getAttribute('aria-label')||e.textContent?.trim().slice(0,40)||e.id||e.tagName);
    controlResults.push({label,...await controlCheck(page,el,label)});
   }
   record('internal-layout',{width,module,...m,controls:controlResults});
   await page.screenshot({path:path.join(c.out,`${width}-${module}.png`),fullPage:true});
   if(width===390&&module==='离线学习'){
    const ol=page.locator('.learning-path ol'),last=ol.locator('li button').last();
    const before=await ol.evaluate(el=>({scroll:el.scrollLeft,client:el.clientWidth,width:el.scrollWidth,overflow:getComputedStyle(el).overflowX}));
    check(before.width>before.client&&/auto|scroll/.test(before.overflow),'PATH_NOT_BOUNDED_SCROLL');
    const firstGoal=await page.locator('.learning-task h2').innerText();
    await ol.evaluate(el=>{el.scrollLeft=el.scrollWidth});
    check(await ol.evaluate(el=>el.scrollLeft)>before.scroll,'PATH_SCROLL_DID_NOT_MOVE');
    const reach=await controlCheck(page,last,'390 last learning task');
    await last.click({timeout:3000});
    check((await page.locator('.learning-task h2').innerText())!==firstGoal,'LAST_TASK_SELECTION_DID_NOT_CHANGE');
    record('390-last-task-real-scroll-and-click',{before,reach,goal:await page.locator('.learning-task h2').innerText()});
   }
  }
 }
 await page.setViewportSize({width:1440,height:1000});
 await page.getByRole('button',{name:'本体查询',exact:true}).click();
 await page.getByRole('combobox',{name:'选择对象',exact:true}).selectOption({label:'传感器'});
 await page.getByRole('checkbox',{name:'温度',exact:true}).check();await page.getByRole('button',{name:'生成可见 SPARQL 草稿',exact:true}).click();
 const sparql=await page.getByRole('textbox',{name:'SPARQL',exact:true}).inputValue();check(sparql.includes('https://stage.example/Sensor')&&sparql.includes('https://stage.example/temperature'),'SPARQL_IRI');
 for(const name of ['执行查询','保存到项目（新查询）'])check(await page.getByRole('button',{name,exact:true}).isDisabled(),'UNCONNECTED_QUERY_ENABLED');record('query-real-draft-no-execution');
 await page.getByRole('button',{name:'本体构建',exact:true}).click();await page.getByRole('textbox',{name:'查找概念',exact:true}).fill('传感器');check((await page.getByRole('table').innerText()).includes('共 2 项'),'SEARCH');await page.getByRole('textbox',{name:'查找概念',exact:true}).fill('');
 await page.getByRole('button',{name:'查看 Sensor',exact:true}).click();await page.getByRole('button',{name:'类树',exact:true}).click();check((await page.getByRole('region',{name:'对象浏览',exact:true}).innerText()).includes('传感器'),'TREE');await page.getByRole('button',{name:'局部关系图',exact:true}).click();check((await page.getByRole('region',{name:'对象浏览',exact:true}).innerText()).includes('https://stage.example/Device'),'GRAPH');
 await page.getByRole('button',{name:'新建概念',exact:true}).click();await page.getByRole('textbox',{name:'英文标识',exact:true}).fill('ToolingAcceptanceDraft');check(await page.getByRole('button',{name:'预览定义修改',exact:true}).isDisabled(),'PREVIEW_ENABLED');record('ontology-real-edit-no-preview');
 await page.getByRole('button',{name:'行为定义',exact:true}).click();await page.getByRole('textbox',{name:'触发事件类型',exact:true}).fill('SyntheticTemperatureChanged');const count=await page.locator('.behavior-entry').count();await page.getByRole('button',{name:'＋ 添加条件',exact:true}).click();check(await page.locator('.behavior-entry').count()===count+1,'ADD_CONDITION');await page.getByRole('button',{name:/移除条件/}).last().click();check(await page.locator('.behavior-entry').count()===count,'REMOVE_CONDITION');check(await page.getByRole('button',{name:'在隔离副本中测试',exact:true}).isDisabled(),'BEHAVIOR_RUN_ENABLED');record('behavior-real-edit-no-run');
 await page.getByRole('button',{name:'离线学习',exact:true}).click();const tasks=page.getByRole('complementary',{name:'学习路径',exact:true}).getByRole('button');const goal=await page.locator('.learning-task h2').innerText();await tasks.nth(1).click();check(await page.locator('.learning-task h2').innerText()!==goal,'TASK_SWITCH');await page.getByRole('combobox',{name:'选择一个术语',exact:true}).selectOption({index:1});await page.getByText('查看技术定义',{exact:true}).click();await tasks.nth(0).click();
 const progress=await page.locator('.learning-progress').innerText();await page.getByRole('button',{name:'检查我的操作',exact:true}).click();check((await page.locator('.learning-feedback [role="status"]').innerText()).includes('此任务的检查暂不可用'),'CHECK_UNAVAILABLE');check(await page.locator('.learning-progress').innerText()===progress&&progress.includes('0'),'INVENTED_PROGRESS');record('learning-content-and-unavailable-check');
 await page.getByRole('combobox',{name:'离线学习步骤1结果',exact:true}).selectOption('符合预期');await page.getByRole('textbox',{name:'问题、期望与操作步骤',exact:true}).fill('tooling-owned-run synthetic feedback');
 for(const [name,file] of [['下载验收记录','feedback.json'],['下载合成样例','samples.json']]){const [d]=await Promise.all([page.waitForEvent('download'),page.getByRole('button',{name,exact:true}).click()]);await d.saveAs(path.join(c.out,file));}
 const feedback=JSON.parse(fs.readFileSync(path.join(c.out,'feedback.json'),'utf8')),samples=JSON.parse(fs.readFileSync(path.join(c.out,'samples.json'),'utf8'));
 check(feedback.notes==='tooling-owned-run synthetic feedback'&&feedback.checks['learning-0']==='符合预期'&&feedback.scope.includes('不代表正式业务通过'),'FEEDBACK_CONTENT');check(samples.synthetic===true&&samples.view.project==='synthetic-preview-only'&&samples.catalog.classes.length===3,'SAMPLE_CONTENT');record('two-real-json-downloads-parsed');
 await page.getByRole('button',{name:'本体构建',exact:true}).click();await page.getByRole('button',{name:'新建概念',exact:true}).click();const identifier=page.getByRole('textbox',{name:'英文标识',exact:true});await identifier.fill('ResetMe');await page.getByRole('button',{name:'重置当前页草稿',exact:true}).click();check(await identifier.inputValue()==='','RESET_DRAFT');check(await page.getByRole('textbox',{name:'问题、期望与操作步骤',exact:true}).inputValue()===feedback.notes,'RESET_ERASED_NOTES');await identifier.fill('SwitchMe');await page.getByRole('button',{name:'本体查询',exact:true}).click();await page.getByRole('button',{name:'本体构建',exact:true}).click();check(await identifier.inputValue()==='','SWITCH_DRAFT');await page.getByRole('button',{name:'离线学习',exact:true}).click();check(await page.getByRole('combobox',{name:'离线学习步骤1结果',exact:true}).inputValue()==='符合预期','RESET_ERASED_CHECK');await page.reload();check(await page.getByRole('textbox',{name:'问题、期望与操作步骤',exact:true}).inputValue()==='','RELOAD_NOTES');await page.getByRole('button',{name:'离线学习',exact:true}).click();check(await page.getByRole('combobox',{name:'离线学习步骤1结果',exact:true}).inputValue()==='未验','RELOAD_CHECK');record('reset-switch-reload-boundaries');
 await queryCoverage(page,record);await behaviorCoverage(page,record);
 const coverage=coverageVerdict(results,c.requiredCoverage);
 check(coverage.passed,'MANDATORY_COVERAGE_MISSING '+JSON.stringify(coverage.mandatoryUnverified));
 check(errors.length===0,'PAGE_ERRORS '+errors.join(';'));check(requests.length===0,'EXTERNAL_REQUEST_ATTEMPT');
}catch(e){firstFailure=String(e.stack||e);process.exitCode=1;}
finally{try{if(context)await context.close();if(browser)await browser.close();ownedClosed=true}catch(e){firstFailure=firstFailure||'OWN_CLOSE_FAILED '+e;process.exitCode=1}const coverage=coverageVerdict(results,c.requiredCoverage);fs.writeFileSync(path.join(c.out,'browser-result.json'),JSON.stringify({passed:!firstFailure&&coverage.passed,firstFailure,results,requests,errors,coverage,ownedClosed,onlyOwnObjectsClosed:true},null,2),{flag:'wx'});}

}
if(process.argv[1] && path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){await run(JSON.parse(fs.readFileSync(process.argv[2],"utf8")));}
