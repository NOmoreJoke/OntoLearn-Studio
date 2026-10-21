from pathlib import Path
import json, hashlib, os, shlex, re
r = Path('.').resolve()
d = r/'docs/reviews/T03/native-location-N0-build/host-core-build/second-core-build'
b = r/'build/native-location/n0/darwin-arm64/95ab1538f20fce33132dc179b738fec780d9e1b1d4eecc5061cb04fccddfd109/core'
lock = json.loads((r/'packages/native-location/toolchain-lock.json').read_text())
tc = lock['toolchains']['darwin-arm64']
known = {}
source_metadata=[]
source_visits=0
source_read_bytes=0
for name, descriptor in [('resource',tc['resourceInventory']),('sdk',tc['sdk']['inventory'])]:
    pin=descriptor['source']; raw=Path(pin['path']).read_bytes()
    assert len(raw)==pin['bytes'] and hashlib.sha256(raw).hexdigest()==pin['sha256']
    value=json.loads(raw); source_read_bytes+=len(raw)
    source_metadata.append({'name':name,'pin':pin,'files':len(value['files'])})
    for i,f in enumerate(value['files']):
        source_visits+=1
        witness={'category':name,'sourceMetadataPath':pin['path'],'sourceMetadataSHA256':pin['sha256'],'fileIndex':i,'pin':f}
        for path in set((os.path.normpath(f['path']),os.path.normpath(f['realpath']))): known.setdefault(path,witness)
assert source_visits==42772 and source_read_bytes==19367235
for i,f in enumerate(lock['source']['files']):
    absolute=os.path.normpath(str(r/f['path']))
    known[absolute]={'category':'source-b1c','sourceRef':lock['source']['ref'],'fileIndex':i,'pin':f}

def deps(raw):
    # Clang make-dependency escapes, not a shell command or JSON decoder.
    colon=None; escaped=False
    for i,c in enumerate(raw):
        if escaped: escaped=False;continue
        if c=='\\':escaped=True;continue
        if c==':':colon=i;break
    assert colon is not None
    s=raw[colon+1:]; words=[]; part=[];i=0
    while i<len(s):
        c=s[i]
        if c=='\\' and i+1<len(s):
            if s[i+1]=='\n':i+=2;continue
            if s[i+1]=='\r' and i+2<len(s) and s[i+2]=='\n':i+=3;continue
            part.append(s[i+1]);i+=2;continue
        if c.isspace():
            if part:words.append(''.join(part));part=[]
            i+=1;continue
        if c=='$' and i+1<len(s) and s[i+1]=='$':part.append('$');i+=2;continue
        part.append(c);i+=1
    if part:words.append(''.join(part))
    return words

all_deps={};dep_files=[];occurrences=0
for p in sorted(b.glob('CMakeFiles/location_*.dir/**/*.o.d')):
    words=deps(p.read_text());occurrences+=len(words)
    dep_files.append({'path':str(p),'entries':len(words),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    for literal in words:
        normal=os.path.normpath(literal if os.path.isabs(literal) else str(b/literal))
        all_deps.setdefault(normal,[]).append({'depfile':str(p.relative_to(b)),'literal':literal})
assert len(dep_files)==4 and occurrences<=5000 and len(all_deps)<=2000
used=[];unknown=[]
for path,locations in sorted(all_deps.items()):
    witness=known.get(path)
    item={'normalizedPath':path,'references':locations,'approvedWitness':witness}
    (used if witness else unknown).append(item)
# No unknown dependency payload is opened, resolved or hashed.
(d/'used-dependencies.json').write_text(json.dumps({'sourceMetadata':source_metadata,'sourceMetadataObjectsVisited':source_visits,'sourceMetadataReadBufferBytes':source_read_bytes,'depfiles':dep_files,'rawDependencyOccurrences':occurrences,'uniqueNormalizedDependencies':len(all_deps),'covered':used,'unmatched':unknown,'unmatchedPayloadReads':False,'coverageScope':'Literal/lexically normalized depfile paths versus approved regular/source pin identities. Compiler header reads are not independently measured; full runtime or linker closure is not implied.'},indent=2)+'\n')

external=json.loads((d/'external-build-output-manifest.json').read_text());by_output={x['path']:x for x in external['files']}
compiles=json.loads((b/'compile_commands.json').read_text());compile_rows=[]
for c in compiles:
    argv=shlex.split(c['command']);assert argv[0]==tc['executables']['cxx']['path']
    assert argv[argv.index('-arch')+1]=='arm64' and '-mmacosx-version-min=15.0' in argv and '-std=c++17' in argv
    assert argv[argv.index('-isysroot')+1]==tc['sdk']['root']
    assert not any('NL_WITH_NODE' in v or 'NAPI_VERSION' in v for v in argv)
    compile_rows.append({**c,'parsedArgv':argv})
links=[]
for name in ['location_core_test','location_child_probe']:
    path=b/f'CMakeFiles/{name}.dir/link.txt';command=path.read_text();argv=shlex.split(command)
    objects=[os.path.normpath(str(b/v)) for v in argv if v.endswith('.o')]
    assert objects and all(v in by_output for v in objects)
    links.append({'target':name,'path':str(path),'command':command,'argv':argv,'explicitObjectInputs':[by_output[v] for v in objects],'expandedLinkerArgvObserved':False,'selectedTbdAndArchiveMembersObserved':False})
compiler_info=(b/'CMakeFiles/4.4.4/CMakeCXXCompiler.cmake').read_text()
implicit={}
for key in ['CMAKE_CXX_IMPLICIT_LINK_LIBRARIES','CMAKE_CXX_IMPLICIT_LINK_DIRECTORIES']:
    m=re.search(r'set\('+key+r' "([^"\n]*)"\)',compiler_info);implicit[key]=m.group(1).split(';') if m else None
(d/'compile-and-link-evidence.json').write_text(json.dumps({'compileCommands':compile_rows,'linkDriverCommands':links,'implicitCompilerProbeObservation':implicit,'implicitObservationIsFinalArtifactTrace':False,'actualSelectedLinkerInputsClosure':'PENDING: final commands do not include -t/-map and no retry/trace was added. Preserve explicit objects and static artifact imports; do not infer selected stubs/archives or archive members.'},indent=2)+'\n')

summaries=[]
for name,format_path,library_path,load_path,symbol_path,undefined_path in [
 ('location_core_test',d/'inspection/location_core_test-file.stdout',d/'inspection/location_core_test-otool-L.stdout',d/'inspection-continuation/location_core_test-load-commands.stdout',d/'inspection-continuation/location_core_test-symbol-table.stdout',d/'inspection-continuation/location_core_test-undefined-symbols.stdout'),
 ('location_child_probe',d/'inspection-continuation/location_child_probe-file-format.stdout',d/'inspection-continuation/location_child_probe-linked-libraries.stdout',d/'inspection-continuation/location_child_probe-load-commands.stdout',d/'inspection-continuation/location_child_probe-symbol-table.stdout',d/'inspection-continuation/location_child_probe-undefined-symbols.stdout')]:
    format_text=format_path.read_text();loads=load_path.read_text();symbols=symbol_path.read_text();undefined=undefined_path.read_text()
    assert 'arm64' in format_text
    build=re.search(r'cmd LC_BUILD_VERSION\s+cmdsize \d+\s+platform (\S+)\s+minos (\S+)\s+sdk (\S+)',loads);assert build and build.group(2)=='15.0'
    deps_found=[];loaders=[];rpaths=[]
    for chunk in re.split(r'Load command \d+\n',loads):
        if re.search(r'cmd LC_LOAD_DYLIB\b',chunk):
            m=re.search(r'\n\s+name (.+) \(offset',chunk);assert m;deps_found.append(m.group(1))
        if re.search(r'cmd LC_LOAD_DYLINKER\b',chunk):
            m=re.search(r'\n\s+name (.+) \(offset',chunk);assert m;loaders.append(m.group(1))
        if re.search(r'cmd LC_RPATH\b',chunk):
            m=re.search(r'\n\s+path (.+) \(offset',chunk);assert m;rpaths.append(m.group(1))
    nl=[line.split()[-1] for line in symbols.splitlines() if re.search(r' external _nl_',line) and '(undefined)' not in line]
    summaries.append({'target':name,'formatOutput':format_text,'LC_BUILD_VERSION':{'platformLiteral':build.group(1),'minos':build.group(2),'sdk':build.group(3)},'importedDylibNames':deps_found,'dynamicLoaders':loaders,'rpaths':rpaths,'nlExternalSymbolsFromSymbolTable':nl,'undefinedSymbolLines':undefined.splitlines(),'symbolTableIsNotAddonOrRuntimeABICertification':True,'actualRuntimeLibrariesLoadedObserved':False})
assert len(summaries[0]['nlExternalSymbolsFromSymbolTable'])==11 and summaries[1]['nlExternalSymbolsFromSymbolTable']==[]
(d/'artifact-static-summary.json').write_text(json.dumps({'artifacts':summaries,'notExecuted':True,'minimum15IsBuildAndLoadCommandEvidenceOnly':True,'dependencyClosure':'PENDING final selected linker stubs/archives/embedded third-party code and runtime/target-OS behavior; no additional build or artifact execution authorized'},indent=2)+'\n')
(d/'used-analysis-counts.json').write_text(json.dumps({'approvedSourceObjects':source_visits,'sourceFileIdentityObjects':9,'depfileRawTokenVisits':occurrences,'uniqueBindingVisits':len(all_deps),'coveredUnique':len(used),'unmatchedUnique':len(unknown),'newSourceMetadataBytesRead':source_read_bytes,'parserInternalTraversalsExcluded':True,'dependencyPayloadHashReads':False},indent=2)+'\n')
print(json.dumps({'depfiles':len(dep_files),'occurrences':occurrences,'unique':len(all_deps),'covered':len(used),'unmatched':len(unknown),'sourceMetadataObjects':source_visits,'artifactExecution':False}))
