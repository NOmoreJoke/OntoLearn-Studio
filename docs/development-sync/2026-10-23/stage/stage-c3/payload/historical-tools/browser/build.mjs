import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {readFile,writeFile,mkdir,readdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
const root=path.dirname(fileURLToPath(import.meta.url));
const dependencyRoot=process.env.ONTOLEARN_BUILD_DEPENDENCIES||'/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio/node_modules';
const frozenManifest=JSON.parse(await readFile(path.join(root,'manifest.json'),'utf8'));
for(const source of frozenManifest.sources){const bytes=await readFile(path.join(root,'snapshot',source.path));if(bytes.length!==source.bytes||createHash('sha256').update(bytes).digest('hex')!==source.sha256)throw new Error('Frozen source mismatch: '+source.path);}
const {build}=await import(path.join(dependencyRoot,'vite/dist/node/index.js'));
const {default:react}=await import(path.join(dependencyRoot,'@vitejs/plugin-react/dist/index.js'));
await build({root,configFile:false,define:{'process.env.NODE_ENV':JSON.stringify('production')},plugins:[react()],resolve:{alias:{'@ontolearn/contracts':path.join(root,'snapshot/packages/contracts/src/index.ts'),'react':path.join(dependencyRoot,'react'),'react-dom':path.join(dependencyRoot,'react-dom'),'zod':path.join(dependencyRoot,'zod')}},build:{outDir:'build',emptyOutDir:true,lib:{entry:path.join(root,'entry.tsx'),name:'StageAcceptance',cssFileName:'browser',formats:['iife'],fileName:()=> 'bundle.js'},cssCodeSplit:false,minify:true}});
const js=(await readFile(path.join(root,'build/bundle.js'),'utf8')).replace(/<\/script/gi,'<\\/script');
const css=await readFile(path.join(root,'build/browser.css'),'utf8').catch(async()=>{const files=await readdir(path.join(root,'build'));return readFile(path.join(root,'build',files.find(f=>f.endsWith('.css'))),'utf8')});
const hash=s=>createHash('sha256').update(s).digest('base64');
const html=`<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'sha256-${hash(js)}'; style-src 'sha256-${hash(css)}'; img-src data:; connect-src 'none'; base-uri 'none'; form-action 'none'"><title>OntoLearn Studio · 阶段验收</title><style>${css}</style></head><body><div id="root"></div><noscript>此阶段验收页需要浏览器启用 JavaScript。</noscript><script>${js}</script></body></html>`;
await writeFile(path.join(root,'index.html'),html);
const manifest=JSON.parse(await readFile(path.join(root,'manifest.json'),'utf8'));manifest.build={entrySha256:createHash('sha256').update(await readFile(path.join(root,'entry.tsx'))).digest('hex'),cssSha256:createHash('sha256').update(await readFile(path.join(root,'shell.css'))).digest('hex'),indexSha256:createHash('sha256').update(html).digest('hex'),vite:JSON.parse(await readFile(path.join(dependencyRoot,'vite/package.json'),'utf8')).version,react:JSON.parse(await readFile(path.join(dependencyRoot,'react/package.json'),'utf8')).version};await writeFile(path.join(root,'manifest.json'),JSON.stringify(manifest,null,2)+'\n');console.log('Built offline file:',path.join(root,'index.html'));
