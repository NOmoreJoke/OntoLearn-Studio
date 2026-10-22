import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {spawn} from 'node:child_process';
const hash = b => crypto.createHash('sha256').update(b).digest('hex');
const fail = m => { throw new Error(m); };
const inside = (p, r) => p === r || p.startsWith(r + path.sep);
const overlaps = (a, b) => inside(a, b) || inside(b, a);
function absolute(p) {
  if (!p || !path.isAbsolute(p) || path.resolve(p) !== p) fail('NON_CANONICAL_ABSOLUTE_PATH');
  return p;
}
function noLinks(p, allowMissing = false) {
  absolute(p);
  let current = path.parse(p).root;
  for (const part of p.slice(current.length).split(path.sep).filter(Boolean)) {
    current = path.join(current, part);
    if (!fs.existsSync(current)) { if (allowMissing) continue; fail('MISSING_PATH: ' + current); }
    const s = fs.lstatSync(current);
    if (s.isSymbolicLink()) fail('SYMLINK_PATH: ' + current);
  }
  if (fs.existsSync(p) && fs.realpathSync(p) !== p) fail('PATH_ALIAS');
}
function regular(p) {
  noLinks(p);
  const s = fs.lstatSync(p);
  if (!s.isFile() || s.nlink !== 1) fail('NOT_UNLINKED_REGULAR_FILE: ' + p);
  return s;
}
function checkedJSON(p, expected) {
  regular(p); const data = fs.readFileSync(p);
  if (!/^[a-f0-9]{64}$/.test(expected || '') || hash(data) !== expected) fail('MANIFEST_SHA_MISMATCH');
  return JSON.parse(data);
}
function treeSize(root) {
  let total = 0, entries;
  try { entries=fs.readdirSync(root); } catch(e) { if(e.code==='ENOENT')return 0;throw e; }
  for(const e of entries){const p=path.join(root,e);let st;try{st=fs.lstatSync(p)}catch(error){if(error.code==='ENOENT')continue;throw error}total+=st.isDirectory()&&!st.isSymbolicLink()?treeSize(p):st.size;}
  return total;
}
function logsSize(root) {
  let total=0,entries;try{entries=fs.readdirSync(root)}catch(e){if(e.code==='ENOENT')return 0;throw e}
  for(const e of entries){const p=path.join(root,e);let st;try{st=fs.lstatSync(p)}catch(error){if(error.code==='ENOENT')continue;throw error}if(st.isDirectory()&&!st.isSymbolicLink())total+=logsSize(p);else if(e.endsWith('.stdout.log')||e.endsWith('.stderr.log'))total+=st.size;}
  return total;
}
function identity(p) { const s = regular(p); return {path:p, bytes:s.size, mode:s.mode & 0o777, dev:s.dev, ino:s.ino, sha256:hash(fs.readFileSync(p))}; }
const argv = process.argv.slice(2), args = {};
try {
  const names = ['authority','authority-sha256','input-root','input-manifest','input-manifest-sha256','work-root','output-root','dependency-root'];
  for (let i=0; i<argv.length; i+=2) {
    const k=argv[i]?.slice(2); if (!argv[i]?.startsWith('--') || !names.includes(k) || args[k] || !argv[i+1]) fail('INVALID_ARGUMENTS'); args[k]=argv[i+1];
  }
  for (const k of names) if (!args[k]) fail('MISSING_ARGUMENT: '+k);
  const authority = checkedJSON(absolute(args.authority), args['authority-sha256']);
  if (authority.schemaVersion !== 1 || !Array.isArray(authority.protectedRoots) || authority.protectedRoots.length < 1) fail('INVALID_AUTHORITY');
  const limits=authority.limits;
  if (!limits || !(limits.combinedScratchBytes > 0 && limits.capturedLogBytes > 0 && limits.browserTimeoutSeconds > 0)) fail('INVALID_LIMITS');
  const base=absolute(authority.allowedRunBase), input=absolute(args['input-root']), work=absolute(args['work-root']), out=absolute(args['output-root']), deps=absolute(args['dependency-root']);
  for (const p of [base,input,deps]) noLinks(p);
  const manifestPath=absolute(args['input-manifest']);
  if (!inside(manifestPath,input)) fail('MANIFEST_OUTSIDE_INPUT');
  const manifest=checkedJSON(manifestPath,args['input-manifest-sha256']);
  if (path.dirname(work)!==base || path.dirname(out)!==work || fs.existsSync(work) || fs.existsSync(out)) fail('NEW_DIRECT_RUN_AND_OUTPUT_REQUIRED');
  noLinks(work,true); noLinks(out,true);
  const protectedRoots=[...authority.protectedRoots.map(absolute),input,deps,args.authority,manifestPath];
  for (const p of protectedRoots) {
    noLinks(p);
    if (overlaps(work,p) || overlaps(out,p)) fail('PROTECTED_PATH_OVERLAP');
    // Compare actual ancestor identities too, instead of relying on textual case/Unicode spelling.
    const ps=fs.statSync(p);
    for (let q=path.dirname(work); ; q=path.dirname(q)) {
      const qs=fs.statSync(q); if (ps.dev===qs.dev && ps.ino===qs.ino) fail('PROTECTED_ANCESTOR_ALIAS');
      if (path.dirname(q)===q) break;
    }
  }
  if (!Array.isArray(manifest.sources) || manifest.sources.length!==34 || !manifest.build) fail('EXPECTED_34_SOURCES');
  const sourceFiles=[{rel:'entry.tsx',sha256:manifest.build.entrySha256},{rel:'shell.css',sha256:manifest.build.cssSha256},...manifest.sources.map(x=>({rel:'snapshot/'+x.path,sha256:x.sha256,bytes:x.bytes}))];
  const seen=new Set(); const before=[identity(manifestPath),identity(path.join(input,'index.html'))];
  if(before[1].sha256!==manifest.build.indexSha256)fail('ORIGINAL_INDEX_IDENTITY_MISMATCH');
  for (const x of sourceFiles) {
    if (path.isAbsolute(x.rel) || path.normalize(x.rel)!==x.rel || x.rel.split('/').includes('..') || seen.has(x.rel)) fail('INVALID_SOURCE_PATH'); seen.add(x.rel);
    const p=path.join(input,x.rel), record=identity(p);
    if (record.sha256!==x.sha256 || (x.bytes!==undefined && record.bytes!==x.bytes)) fail('SOURCE_IDENTITY_MISMATCH: '+x.rel);
    before.push(record);
  }
  const depRecords=['vite/package.json','@vitejs/plugin-react/package.json','react/package.json'].map(x=>identity(path.join(deps,x)));
  if (JSON.parse(fs.readFileSync(path.join(deps,'vite/package.json'))).version!==manifest.build.vite || JSON.parse(fs.readFileSync(path.join(deps,'react/package.json'))).version!==manifest.build.react) fail('DEPENDENCY_VERSION_MISMATCH');
  if (treeSize(base)>=limits.combinedScratchBytes) fail('COMBINED_SCRATCH_LIMIT');
  fs.mkdirSync(work); const workId=fs.statSync(work); fs.mkdirSync(out); fs.mkdirSync(path.join(work,'tmp')); fs.mkdirSync(path.join(work,'cache'));
  const copy=path.join(work,'source'); fs.mkdirSync(copy);
  for (const x of sourceFiles) { if(treeSize(base)+fs.statSync(path.join(input,x.rel)).size>limits.combinedScratchBytes || treeSize(work)+fs.statSync(path.join(input,x.rel)).size>64*1024*1024)fail('COPY_SCRATCH_LIMIT'); const dest=path.join(copy,x.rel); fs.mkdirSync(path.dirname(dest),{recursive:true}); fs.copyFileSync(path.join(input,x.rel),dest,fs.constants.COPYFILE_EXCL); fs.chmodSync(dest,fs.statSync(path.join(input,x.rel)).mode & 0o777); }
  const worker=path.join(work,'build-worker.mjs');
  fs.writeFileSync(worker,`import path from 'node:path';import fs from 'node:fs/promises';import {createHash} from 'node:crypto';
const c=JSON.parse(await fs.readFile(process.argv[2],'utf8'));const root=c.copy,dependencyRoot=c.deps;
const {build}=await import(path.join(dependencyRoot,'vite/dist/node/index.js'));const {default:react}=await import(path.join(dependencyRoot,'@vitejs/plugin-react/dist/index.js'));
await build({root,configFile:false,envFile:false,publicDir:false,cacheDir:path.join(c.work,'cache/vite'),define:{'process.env.NODE_ENV':JSON.stringify('production')},plugins:[react({babel:{babelrc:false,configFile:false}})],css:{postcss:{plugins:[]}},resolve:{alias:{'@ontolearn/contracts':path.join(root,'snapshot/packages/contracts/src/index.ts'),'react':path.join(dependencyRoot,'react'),'react-dom':path.join(dependencyRoot,'react-dom'),'zod':path.join(dependencyRoot,'zod')}},build:{outDir:path.join(c.out,'build'),emptyOutDir:true,lib:{entry:path.join(root,'entry.tsx'),name:'StageAcceptance',cssFileName:'browser',formats:['iife'],fileName:()=> 'bundle.js'},cssCodeSplit:false,minify:true}});
const js=(await fs.readFile(path.join(c.out,'build/bundle.js'),'utf8')).replace(/<\\/script/gi,'<\\\\/script');
let css;try{css=await fs.readFile(path.join(c.out,'build/browser.css'),'utf8')}catch{const f=(await fs.readdir(path.join(c.out,'build'))).find(x=>x.endsWith('.css'));if(!f)throw Error('CSS_MISSING');css=await fs.readFile(path.join(c.out,'build',f),'utf8')}
const hash=s=>createHash('sha256').update(s).digest('base64');
const html=\`<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'sha256-\${hash(js)}'; style-src 'sha256-\${hash(css)}'; img-src data:; connect-src 'none'; base-uri 'none'; form-action 'none'"><title>OntoLearn Studio · 阶段验收</title><style>\${css}</style></head><body><div id="root"></div><noscript>此阶段验收页需要浏览器启用 JavaScript。</noscript><script>\${js}</script></body></html>\`;
await fs.writeFile(path.join(c.out,'index.html'),html,{flag:'wx'});
console.log(JSON.stringify({indexSha256:createHash('sha256').update(html).digest('hex')}));
`,{flag:'wx'});
  const config=path.join(work,'build-config.json'); fs.writeFileSync(config,JSON.stringify({copy,deps,work,out}),{flag:'wx'});
  const command=[process.execPath,worker,config], start=Date.now(), samples=[];
  let reason=null, captured=0, peak=0, localPeak=0;
  const stdout=fs.openSync(path.join(work,'child.stdout.log'),'wx'), stderr=fs.openSync(path.join(work,'child.stderr.log'),'wx');
  const env={PATH:path.dirname(process.execPath),TMPDIR:path.join(work,'tmp'),TMP:path.join(work,'tmp'),TEMP:path.join(work,'tmp'),XDG_CACHE_HOME:path.join(work,'cache'),NO_COLOR:'1',NODE_ENV:'production'};
  const child=spawn(command[0],command.slice(1),{cwd:work,env,detached:true,stdio:['ignore','pipe','pipe']});
  const stop=m=>{if (!reason) reason=m; try{process.kill(-child.pid,'SIGTERM')}catch{};};
  for (const [stream,fd] of [[child.stdout,stdout],[child.stderr,stderr]]) stream.on('data',b=>{const room=Math.max(0,limits.capturedLogBytes-captured);if(room)fs.writeSync(fd,b.subarray(0,room));captured+=b.length;if(captured>limits.capturedLogBytes || logsSize(base)>limits.capturedLogBytes)stop('CAPTURED_LOG_LIMIT');});
  const tick=()=>{try { noLinks(work);const st=fs.statSync(work);if(st.dev!==workId.dev || st.ino!==workId.ino)stop('RUN_REPLACED');const total=treeSize(base),local=treeSize(work);peak=Math.max(peak,total);localPeak=Math.max(localPeak,local);samples.push({elapsedMs:Date.now()-start,combinedBytes:total,localBytes:local});if(logsSize(base)>limits.capturedLogBytes)stop('COMBINED_LOG_LIMIT');if(total>limits.combinedScratchBytes || local>64*1024*1024)stop('SCRATCH_LIMIT');if(Date.now()-start>limits.browserTimeoutSeconds*1000)stop('TIME_LIMIT');} catch(e){stop(String(e.message));}};
  const timer=setInterval(tick,100);tick();
  const killer=setInterval(()=>{if(reason)try{process.kill(-child.pid,'SIGKILL')}catch{}},1000);
  const exit=await new Promise(resolve=>{child.on('error',e=>{reason='SPAWN_ERROR: '+e.message;resolve(-1)});child.on('close',(code,signal)=>resolve(code ?? 'signal:'+signal));});
  clearInterval(timer);clearInterval(killer);fs.closeSync(stdout);fs.closeSync(stderr);tick();
  const after=before.map(x=>identity(x.path));if(JSON.stringify(before)!==JSON.stringify(after)) reason=reason||'SOURCE_CHANGED';
  const index=path.join(out,'index.html'); const indexSHA=fs.existsSync(index)?hash(fs.readFileSync(index)):null;
  if(indexSHA!==manifest.build.indexSha256)reason=reason||'INDEX_REPRODUCTION_MISMATCH';
  const report={tool:'build',argv:process.argv,cwd:process.cwd(),childArgv:command,childCwd:work,exit,reason,passed:exit===0&&!reason,indexSha256:indexSHA,expectedIndexSha256:manifest.build.indexSha256,before,after,dependencyIdentity:depRecords,authoritySHA256:args['authority-sha256'],samples,peakCombinedBytes:peak,peakLocalBytes:localPeak,capturedLogBytes:captured,limitsAreSamplingNotOSHardLimits:true,cleanup:'only owned child process group; no source deletion'};
  fs.writeFileSync(path.join(out,'build-manifest.json'),JSON.stringify(report,null,2)+'\n',{flag:'wx'});
  console.log(JSON.stringify({passed:report.passed,exit,reason,indexSha256:indexSHA,report:path.join(out,'build-manifest.json')}));
  process.exitCode=report.passed?0:1;
} catch(e) { console.error('BUILD_REFUSED_OR_FAILED: '+e.message);process.exitCode=1; }
