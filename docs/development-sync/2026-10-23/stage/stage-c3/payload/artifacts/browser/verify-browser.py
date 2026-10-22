"""Owned-process, offline browser acceptance. All writes are under a fresh owner-authorized run."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import selectors
import signal
import stat
import subprocess
import sys
import time


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value, missing=False):
    p = Path(value)
    require(p.is_absolute() and os.path.normpath(value) == value, 'CANONICAL_ABSOLUTE_PATH_REQUIRED')
    for q in [*reversed(p.parents), p]:
        try:
            s = q.lstat()
        except FileNotFoundError:
            require(missing, 'MISSING_PATH: ' + str(q))
            continue
        require(not stat.S_ISLNK(s.st_mode), 'SYMLINK_PATH: ' + str(q))
    if p.exists():
        require(str(p.resolve()) == value, 'PATH_ALIAS')
    return p


def within(a, b):
    return a == b or b in a.parents


def regular(p):
    canonical(str(p))
    s = p.lstat()
    require(stat.S_ISREG(s.st_mode) and s.st_nlink == 1, 'REGULAR_UNLINKED_INPUT_REQUIRED')
    return s


def identity(p):
    s = regular(p)
    return dict(path=str(p), bytes=s.st_size, mode=stat.S_IMODE(s.st_mode), dev=s.st_dev,
                ino=s.st_ino, sha256=digest(p.read_bytes()))


def load_checked(p, expected):
    regular(p)
    data = p.read_bytes()
    require(len(expected) == 64 and digest(data) == expected, 'INPUT_SHA_MISMATCH')
    return json.loads(data)


def size(root, strict=False):
    total = 0
    try:
        with os.scandir(root) as entries:
            for entry in entries:
                try:
                    info = entry.stat(follow_symlinks=False)
                except FileNotFoundError:
                    continue
                if stat.S_ISDIR(info.st_mode) and not stat.S_ISLNK(info.st_mode):
                    total += size(Path(entry.path), strict)
                else:
                    total += info.st_size
    except FileNotFoundError:
        return 0
    return total


def logs_size(root):
    total = 0
    try:
        with os.scandir(root) as entries:
            for entry in entries:
                try:
                    info = entry.stat(follow_symlinks=False)
                except FileNotFoundError:
                    continue
                if stat.S_ISDIR(info.st_mode) and not stat.S_ISLNK(info.st_mode):
                    total += logs_size(Path(entry.path))
                elif entry.name.endswith(('.stdout.log', '.stderr.log')):
                    total += info.st_size
    except FileNotFoundError:
        return 0
    return total


RUNNER = r'''import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const c=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
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
 check(errors.length===0,'PAGE_ERRORS '+errors.join(';'));check(requests.length===0,'EXTERNAL_REQUEST_ATTEMPT');
}catch(e){firstFailure=String(e.stack||e);process.exitCode=1;}
finally{try{if(context)await context.close();if(browser)await browser.close();ownedClosed=true}catch(e){firstFailure=firstFailure||'OWN_CLOSE_FAILED '+e;process.exitCode=1}fs.writeFileSync(path.join(c.out,'browser-result.json'),JSON.stringify({passed:!firstFailure,firstFailure,results,requests,errors,ownedClosed,onlyOwnObjectsClosed:true},null,2),{flag:'wx'});}
'''


def main():
    parser = argparse.ArgumentParser()
    for name in ['authority', 'authority-sha256', 'input-root', 'input-manifest',
                 'input-manifest-sha256', 'work-root', 'output-root', 'node',
                 'playwright-module', 'browser', 'session']:
        parser.add_argument('--' + name, required=True)
    args = vars(parser.parse_args())
    authority_path = canonical(args['authority'])
    authority = load_checked(authority_path, args['authority_sha256'])
    require(authority.get('schemaVersion') == 1 and authority.get('protectedRoots'), 'AUTHORITY_SCHEMA')
    limits = authority['limits']
    for key in ['combinedScratchBytes', 'capturedLogBytes', 'browserTimeoutSeconds']:
        require(isinstance(limits.get(key), int) and limits[key] > 0, 'AUTHORITY_LIMITS')
    base = canonical(authority['allowedRunBase'])
    source = canonical(args['input_root'])
    manifest_path = canonical(args['input_manifest'])
    require(within(manifest_path, source), 'MANIFEST_OUTSIDE_INPUT')
    manifest = load_checked(manifest_path, args['input_manifest_sha256'])
    work = canonical(args['work_root'], True)
    output = canonical(args['output_root'], True)
    require(work.parent == base and output.parent == work and not work.exists()
            and not output.exists(), 'NEW_DIRECT_RUN_AND_OUTPUT_REQUIRED')
    require(args['session'] == work.name and all(c.isalnum() or c in '-_' for c in args['session']),
            'SESSION_MUST_BE_FRESH_RUN_IDENTIFIER')
    dependencies = [canonical(args[x]) for x in ['node', 'playwright_module', 'browser']]
    for p in dependencies:
        regular(p)
    require(os.access(dependencies[0], os.X_OK) and os.access(dependencies[2], os.X_OK),
            'EXECUTABLE_UNAVAILABLE')
    protected = [canonical(x) for x in authority['protectedRoots']]
    protected += [source, manifest_path, authority_path, *dependencies]
    for p in protected:
        require(not (within(work, p) or within(p, work) or within(output, p) or within(p, output)),
                'PROTECTED_PATH_OVERLAP')
        ps = p.stat()
        for q in work.parent.parents:
            qs = q.stat()
            require((ps.st_dev, ps.st_ino) != (qs.st_dev, qs.st_ino), 'PROTECTED_ANCESTOR_ALIAS')
    require(len(manifest.get('sources', [])) == 34, 'EXPECTED_34_SOURCES')
    records = [identity(manifest_path)]
    entries = [('index.html', manifest['build']['indexSha256'], None),
               ('entry.tsx', manifest['build']['entrySha256'], None),
               ('shell.css', manifest['build']['cssSha256'], None)]
    entries += [('snapshot/' + x['path'], x['sha256'], x['bytes']) for x in manifest['sources']]
    seen = set()
    for rel, expected, expected_bytes in entries:
        require(not Path(rel).is_absolute() and '..' not in Path(rel).parts and rel not in seen,
                'SOURCE_PATH_INVALID')
        seen.add(rel)
        record = identity(source / rel)
        require(record['sha256'] == expected and (expected_bytes is None or record['bytes'] == expected_bytes),
                'SOURCE_IDENTITY_MISMATCH: ' + rel)
        records.append(record)
    deps_before = [identity(x) for x in dependencies]
    require(size(base) < limits['combinedScratchBytes'], 'COMBINED_SCRATCH_LIMIT')
    work.mkdir()
    work_id = work.stat()
    output.mkdir()
    for name in ['tmp', 'cache', 'config', 'traces']:
        (work / name).mkdir()
    runner = work / 'owned-browser-runner.mjs'
    runner.write_text(RUNNER)
    config = work / 'runner-input.json'
    config.write_text(json.dumps(dict(work=str(work), out=str(output), module=str(dependencies[1]),
                                     browser=str(dependencies[2]), index=str(source / 'index.html'),
                                     session=args['session'])))
    command = [str(dependencies[0]), str(runner), str(config)]
    env = {'PATH': str(dependencies[0].parent), 'TMPDIR': str(work / 'tmp'),
           'TMP': str(work / 'tmp'), 'TEMP': str(work / 'tmp'),
           'XDG_CACHE_HOME': str(work / 'cache'), 'XDG_CONFIG_HOME': str(work / 'config'),
           'NO_COLOR': '1'}
    start = time.monotonic()
    samples, reason, captured = [], None, 0
    child = subprocess.Popen(command, cwd=work, env=env, stdin=subprocess.DEVNULL,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    selector = selectors.DefaultSelector()
    stdout = (work / 'child.stdout.log').open('xb')
    stderr = (work / 'child.stderr.log').open('xb')
    selector.register(child.stdout, selectors.EVENT_READ, stdout)
    selector.register(child.stderr, selectors.EVENT_READ, stderr)
    terminated_at = None
    try:
        while selector.get_map() or child.poll() is None:
            for key, _ in selector.select(0.1):
                chunk = os.read(key.fileobj.fileno(), 65536)
                if not chunk:
                    selector.unregister(key.fileobj)
                    continue
                room = max(0, limits['capturedLogBytes'] - captured)
                key.data.write(chunk[:room])
                key.data.flush()
                captured += len(chunk)
            try:
                canonical(str(work))
                s = work.stat()
                require((s.st_dev, s.st_ino) == (work_id.st_dev, work_id.st_ino), 'WORK_REPLACED')
                total, local = size(base), size(work)
                elapsed = time.monotonic() - start
                samples.append(dict(elapsedSeconds=elapsed, combinedBytes=total, localBytes=local))
                if total > limits['combinedScratchBytes'] or local > 64 * 1024 * 1024:
                    reason = reason or 'SCRATCH_LIMIT'
                if elapsed > limits['browserTimeoutSeconds']:
                    reason = reason or 'TIME_LIMIT'
                if captured > limits['capturedLogBytes'] or logs_size(base) > limits['capturedLogBytes']:
                    reason = reason or 'LOG_LIMIT'
            except Exception as exc:
                reason = reason or str(exc)
            if reason and terminated_at is None:
                terminated_at = time.monotonic()
                try:
                    os.killpg(child.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
            if terminated_at is not None and time.monotonic() - terminated_at > 1:
                try:
                    os.killpg(child.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            if terminated_at is not None and time.monotonic() - terminated_at > 4:
                reason += '; pipe/process cleanup not confirmed'
                break
    finally:
        selector.close()
        stdout.close()
        stderr.close()
    try:
        exit_code = child.wait(timeout=2)
    except subprocess.TimeoutExpired:
        os.killpg(child.pid, signal.SIGKILL)
        exit_code = child.wait(timeout=2)
    after = [identity(Path(x['path'])) for x in records]
    require(records == after, 'SOURCE_CHANGED')
    result_path = output / 'browser-result.json'
    result = json.loads(result_path.read_text()) if result_path.is_file() else None
    report = dict(tool='verify-browser', argv=sys.argv, cwd=os.getcwd(), childArgv=command,
                  childCwd=str(work), exit=exit_code, reason=reason,
                  passed=exit_code == 0 and reason is None and bool(result and result['passed']),
                  firstFailure=reason or (result or {}).get('firstFailure'), before=records, after=after,
                  dependencyIdentity=deps_before, authoritySHA256=args['authority_sha256'],
                  samples=samples, peakCombinedBytes=max((s['combinedBytes'] for s in samples), default=0),
                  peakLocalBytes=max((s['localBytes'] for s in samples), default=0),
                  combinedBytesAfter=size(base), capturedLogBytes=captured,
                  limitsAreSamplingNotOSHardLimits=True,
                  cleanup='own process group only; normal browser close recorded in browser-result; '
                          'forced termination does not prove all descendants cleaned')
    with (output / 'launcher-report.json').open('x') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(json.dumps(dict(passed=report['passed'], exit=exit_code, reason=report['firstFailure'],
                          report=str(output / 'launcher-report.json'))))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as exc:
        print('VERIFY_REFUSED_OR_FAILED: ' + str(exc), file=sys.stderr)
        sys.exit(1)
