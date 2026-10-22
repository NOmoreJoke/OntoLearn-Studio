from pathlib import Path
import subprocess
root=Path(__file__).resolve().parent
code=r'''async page => {
const assert=(ok,message)=>{if(!ok)throw new Error(message)};
const results=[];
const errors=[];
page.on('pageerror',error=>errors.push(String(error)));
await page.getByRole('button',{name:'本体查询',exact:true}).click();
await page.getByRole('combobox',{name:'选择对象',exact:true}).selectOption({label:'传感器'});
await page.getByRole('checkbox',{name:'温度',exact:true}).check();
await page.getByRole('button',{name:'生成可见 SPARQL 草稿',exact:true}).click();
const sparql=await page.getByRole('textbox',{name:'SPARQL',exact:true}).inputValue();
assert(sparql.includes('https://stage.example/Sensor')&&sparql.includes('https://stage.example/temperature'),'query exact IRIs missing');
assert(await page.getByRole('button',{name:'执行查询',exact:true}).isDisabled(),'execute unexpectedly enabled');
assert(await page.getByRole('button',{name:'保存到项目（新查询）',exact:true}).isDisabled(),'save unexpectedly enabled');
results.push({check:'真实查询编写器生成草稿，执行/保存禁用',sparql});
await page.getByRole('button',{name:'本体构建',exact:true}).click();
await page.getByRole('textbox',{name:'查找概念',exact:true}).fill('传感器');
assert((await page.getByRole('table').innerText()).includes('共 2 项'),'ontology search exact result mismatch');
await page.getByRole('textbox',{name:'查找概念',exact:true}).fill('');
await page.getByRole('button',{name:'查看 Sensor',exact:true}).click();
await page.getByRole('button',{name:'类树',exact:true}).click();
assert((await page.getByRole('region',{name:'对象浏览',exact:true}).innerText()).includes('传感器'),'class tree missing');
await page.getByRole('button',{name:'局部关系图',exact:true}).click();
assert((await page.getByRole('region',{name:'对象浏览',exact:true}).innerText()).includes('https://stage.example/Device'),'graph superclass missing');
await page.getByRole('button',{name:'新建概念',exact:true}).click();
await page.getByRole('textbox',{name:'英文标识',exact:true}).fill('UserAcceptanceConcept');
assert(await page.getByRole('button',{name:'预览定义修改',exact:true}).isDisabled(),'preview unexpectedly enabled');
await page.getByRole('button',{name:'重置当前页草稿',exact:true}).click();
assert((await page.getByRole('textbox',{name:'英文标识',exact:true}).inputValue())==='','reset failed');
results.push({check:'本体搜索/类树/关系图/表单/重置；无预览服务'});
await page.getByRole('button',{name:'行为定义',exact:true}).click();
await page.getByRole('textbox',{name:'触发事件类型',exact:true}).fill('SyntheticTemperatureChanged');
const before=await page.locator('.behavior-entry').count();
await page.getByRole('button',{name:'＋ 添加条件',exact:true}).click();
assert(await page.locator('.behavior-entry').count()===before+1,'condition not added');
await page.getByRole('button',{name:/移除条件/}).last().click();
assert(await page.getByRole('button',{name:'在隔离副本中测试',exact:true}).isDisabled(),'behavior test enabled');
assert(await page.locator('.behavior-entry').count()===before,'condition not removed');
assert((await page.getByRole('textbox',{name:'触发事件类型',exact:true}).inputValue())==='SyntheticTemperatureChanged','behavior input failed');
results.push({check:'行为事件编辑/条件增删，缺真实服务'});
await page.getByRole('button',{name:'离线学习',exact:true}).click();
const tasks=page.getByRole('complementary',{name:'学习路径',exact:true}).getByRole('button');
await tasks.nth(1).click();
await page.getByRole('combobox',{name:'选择一个术语',exact:true}).selectOption({index:1});
await page.getByText('查看技术定义',{exact:true}).click();
assert((await page.locator('.learning-progress').innerText()).includes('0'),'learning progress invented');
results.push({check:'离线课程任务/术语切换，学习进度不伪造'});
await page.getByRole('combobox',{name:'离线学习步骤1结果',exact:true}).selectOption('符合预期');
await page.getByRole('textbox',{name:'问题、期望与操作步骤',exact:true}).fill('自动化验收：本地交互通过；真实业务服务未接。');
const [feedback]=await Promise.all([page.waitForEvent('download'),page.getByRole('button',{name:'下载验收记录',exact:true}).click()]);
await feedback.saveAs('output/playwright/feedback.json');
const [samples]=await Promise.all([page.waitForEvent('download'),page.getByRole('button',{name:'下载合成样例',exact:true}).click()]);
await samples.saveAs('output/playwright/samples.json');
results.push({check:'本地JSON验收记录与合成样例下载'});
for(const width of [1440,390]){
 await page.setViewportSize({width,height:1000});
 for(const name of ['本体构建','本体查询','行为定义','离线学习']){
  await page.getByRole('button',{name,exact:true}).click();
  const size=await page.evaluate(()=>({viewport:innerWidth,body:document.body.scrollWidth,html:document.documentElement.scrollWidth}));
  assert(size.body<=width&&size.html<=width,`overflow ${name} ${JSON.stringify(size)}`);
  await page.screenshot({path:`output/playwright/${width}-${name}.png`,fullPage:true});
  results.push({check:'布局无页面横向溢出',width,module:name});
 }
}
assert(errors.length===0,'page errors '+errors.join(';'));
return {passed:true,results,pageErrors:errors};
}'''
result=subprocess.run(['bash','/Users/kyle/.codex/skills/playwright/scripts/playwright_cli.sh','-s=ontolearn-stage-preview','run-code',code],cwd=root,text=True,capture_output=True)
(root/'output/playwright').mkdir(parents=True,exist_ok=True)
(root/'output/playwright/verification-output.txt').write_text(result.stdout+result.stderr)
print(result.stdout+result.stderr)
raise SystemExit(result.returncode)
