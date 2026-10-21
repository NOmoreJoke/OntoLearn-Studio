import fs from 'node:fs'
import path from 'node:path'
import crypto from 'node:crypto'
import vm from 'node:vm'
const repo = path.resolve('.')
const dir = path.join(repo, 'docs/reviews/T03/native-location-N0-build/host-core-build/metadata-optimization')
const code = fs.readFileSync('scripts/build-native-location.mjs', 'utf8')
const begin = code.indexOf('const lockPath =')
const end = code.indexOf('function verify(')
const context = { Buffer, path, crypto, root: repo }
vm.runInNewContext(code.slice(begin, end) + '\nglobalThis.parseMetadata = parseInventory;', context)
const parse = context.parseMetadata
const digest = (b) => crypto.createHash('sha256').update(b).digest('hex')
const pin = (p) => { const b = fs.readFileSync(p); return {path:p,realpath:fs.realpathSync(p),bytes:b.length,sha256:digest(b)} }
const lock = JSON.parse(fs.readFileSync('packages/native-location/toolchain-lock.json'))
const cases = []
for (const [name, p] of [['resource', lock.toolchains['darwin-arm64'].resourceInventory], ['sdk', lock.toolchains['darwin-arm64'].sdk.inventory]]) {
 const source = fs.readFileSync(p.source.path), records = fs.readFileSync(p.records.path)
 const v = parse(source, records, name)
 cases.push({name: name+'-full-fixed-metadata', expected:'accept', observed:'accept', files:v.files.length, sourceSha256:digest(source), recordsSha256:digest(records)})
}
const compact = JSON.stringify
const build = (files, roots=['/approved']) => {
 const prefix = '{"roots":'+compact(roots)+',"files":['; const suffix = ']}\n'
 const rows = files.map(compact)
 return {source:Buffer.from(prefix+rows.join(',')+suffix),records:Buffer.from(compact({format:'n0-inventory-records-v1',count:files.length,roots,prefix,suffix})+'\n'+rows.join('\n')+'\n')}
}
const f = {path:'/approved/a',realpath:'/approved/a',bytes:0,sha256:digest(Buffer.alloc(0))}
const base = build([f])
const specs = [
 ['zero-byte', base, true],
 ['json-string-escapes', build([{...f,path:'/approved/quote"slash\\unicodeé[x]',realpath:'/approved/quote"slash\\unicodeé[x]'}]), true],
 ['unmatched-bracket', build([{...f,path:'/approved/[',realpath:'/approved/['}]), true],
 ['duplicate-path',build([f,f]),false],
 ['root-escape',build([{...f,realpath:'/outside/a'}]),false],
 ['count-mismatch',{...base,records:Buffer.from(base.records.toString().replace('"count":1','"count":2'))},false],
 ['extra-blank-line',{...base,records:Buffer.concat([base.records,Buffer.from('\n')])},false],
 ['crlf',{...base,records:Buffer.from(base.records.toString().replaceAll('\n','\r\n'))},false],
 ['bom',{...base,records:Buffer.concat([Buffer.from([239,187,191]),base.records])},false],
 ['duplicate-key',(()=>{let s=base.source.toString().replace('"bytes":0','"bytes":0,"bytes":0');let z=base.records.toString().split('\n');z[1]=z[1].replace('"bytes":0','"bytes":0,"bytes":0');return {source:Buffer.from(s),records:Buffer.from(z.join('\n'))}})(),false],
 ['unknown-field',build([{...f,extra:true}]),false],
 ['oversize-row',build([{...f,path:'/approved/'+ 'a'.repeat(4100),realpath:'/approved/'+ 'a'.repeat(4100)}]),false],
 ['semicolon-path',build([{...f,path:'/approved/a;b'}]),false],
 ['record-drift',{...base,records:Buffer.from(base.records.toString().replace('"bytes":0','"bytes":1'))},false],
 ['roots-object',(()=>{const z=build([f]);return {...z,source:Buffer.from(z.source.toString().replace('["/approved"]','{"0":"/approved"}'))}})(),false],
 ['record-cap', {source:Buffer.alloc(16*1024*1024+1),records:base.records}, false],
]
const fixtures = path.join(dir,'fixtures'); fs.mkdirSync(fixtures,{recursive:true})
const cmake = fs.readFileSync('packages/native-location/CMakeLists.txt','utf8')
const functions = cmake.slice(cmake.indexOf('function(nl_get out)'), cmake.indexOf('nl_get(schema schemaVersion)'))
fs.writeFileSync(path.join(dir,'metadata-functions.cmake.raw'),functions)
for (const [name, data, accept] of specs) {
 let error=null; try { parse(data.source,data.records,name) } catch(e) {error=e.message}
 const observed=error===null; if(observed!==accept) throw new Error(name+': unexpected '+error)
 cases.push({name,expected:accept?'accept':'reject',observed:observed?'accept':'reject',error})
 // The >16MiB case is exercised in Node without creating another large fixture.
 if(name==='record-cap') continue
 const sourcePath=path.join(fixtures,name+'.source.json'), recordsPath=path.join(fixtures,name+'.records.jsonl')
 fs.writeFileSync(sourcePath,data.source);fs.writeFileSync(recordsPath,data.records)
 const miniLock=compact({supply:{source:pin(sourcePath),records:pin(recordsPath)}})
 fs.writeFileSync(path.join(fixtures,name+'.cmake'), 'cmake_minimum_required(VERSION 3.25)\n'+functions+'\nset(NL_JSON [==['+miniLock+']==])\nnl_inventory_metadata(rows "" supply)\nlist(LENGTH rows actual)\nmessage(STATUS "metadata-only rows=${actual}; physical supplier pin loop NOT RUN")\n')
}
const fullLock=compact({resource:lock.toolchains['darwin-arm64'].resourceInventory,sdk:lock.toolchains['darwin-arm64'].sdk.inventory})
fs.writeFileSync(path.join(dir,'full-metadata-only.cmake'),'cmake_minimum_required(VERSION 3.25)\n'+functions+'\nset(NL_JSON [==['+fullLock+']==])\nnl_inventory_metadata(resource_rows "" resource)\nnl_inventory_metadata(sdk_rows "'+lock.toolchains['darwin-arm64'].sdk.root+'" sdk)\nlist(LENGTH resource_rows a)\nlist(LENGTH sdk_rows b)\nmessage(STATUS "metadata-only resource=${a} sdk=${b}; physical supplier pin loop NOT RUN")\n')
fs.writeFileSync(path.join(dir,'node-metadata-validation.json'),JSON.stringify({cases,physicalSupplierReads:false,productMainOrCLIExecuted:false,functionsExtractedFromActualDriver:true},null,2)+'\n')
console.log(JSON.stringify({cases:cases.length,result:'pass',physicalSupplierReads:false}))
