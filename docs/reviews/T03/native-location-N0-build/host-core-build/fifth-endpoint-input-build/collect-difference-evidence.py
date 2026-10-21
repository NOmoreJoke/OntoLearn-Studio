from pathlib import Path
import json, hashlib, os, re, shlex, stat
r=Path.cwd(); d=r/'docs/reviews/T03/native-location-N0-build/host-core-build/fifth-endpoint-input-build'
prior=r/'docs/reviews/T03/native-location-N0-build/host-core-build/diagnostic-fourth-input-build'
b=r/'build/native-location/n0/darwin-arm64/0d5223985fcd9761c60cee55d4c258af9b8204c8b0131df1535928cd1953c8fb/core'
lock=json.loads((r/'packages/native-location/toolchain-lock.json').read_bytes());tc=lock['toolchains']['darwin-arm64']
oldraw=(prior/'used-dependencies.json').read_bytes();old=json.loads(oldraw)
oldmap={x['normalizedPath']:x for x in old['covered']+old['unmatched']};assert len(oldmap)==877
aliasraw=(r/'docs/reviews/T03/native-location-N0-build/host-core-build/second-core-build/sdk-alias-catalog-bindings.json').read_bytes();aliases=json.loads(aliasraw)['aliasBindings'];assert len(aliases)==2
aliasmap={x['alias']['record']['path']:x for x in aliases}
source={os.path.normpath(str(r/x['path'])):{'category':'source-fc9853','sourceRef':lock['source']['ref'],'pin':x} for x in lock['source']['files']}

def deps(raw):
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

all_deps={}; depfiles=[];occurrences=0
for p in sorted(b.glob('CMakeFiles/location_*.dir/**/*.o.d')):
    raw=p.read_bytes(); words=deps(raw.decode()); occurrences+=len(words)
    depfiles.append({'path':str(p),'entries':len(words),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
    for literal in words:
        normal=os.path.normpath(literal if os.path.isabs(literal) else str(b/literal))
        all_deps.setdefault(normal,[]).append({'depfile':str(p.relative_to(b)),'literal':literal})
assert len(depfiles)==4 and occurrences<=5000 and len(all_deps)<=2000
added=sorted(set(all_deps)-set(oldmap));removed=sorted(set(oldmap)-set(all_deps))
# Select only actually new metadata records; byte SHA/substring scan is not full record parsing.
metadata_buffers={};selected=[]
def selected_original_pin(path):
    descriptor=tc['sdk']['inventory']['source'] if path.startswith(tc['sdk']['root']+'/') else tc['resourceInventory']['source']
    if descriptor['path'] not in metadata_buffers:
        raw=Path(descriptor['path']).read_bytes()
        assert len(raw)==descriptor['bytes'] and hashlib.sha256(raw).hexdigest()==descriptor['sha256']
        metadata_buffers[descriptor['path']]=raw
    raw=metadata_buffers[descriptor['path']]
    needle=('"path": '+json.dumps(path)).encode();assert raw.count(needle)==1, path
    pos=raw.index(needle);start=raw.rfind(b'{',0,pos)
    # Each approved four-pin object is small; no surrounding source array is decoded.
    text=raw[start:start+8192].decode();value,end=json.JSONDecoder().raw_decode(text)
    assert set(value)=={'path','realpath','bytes','sha256'} and value['path']==path
    witness={'category':'selected-original-supply-record','sourceMetadataPin':descriptor,'byteOffset':start,'pin':value,'recordJSONBytes':len(text[:end].encode())}
    selected.append(witness);return witness

used=[];unmatched=[];counts={'sourceCurrent':0,'priorDirect':0,'priorAliasCatalog':0,'newSelectedOriginalRecord':0}
for path,refs in sorted(all_deps.items()):
    if path in source:witness=source[path];counts['sourceCurrent']+=1
    elif path in aliasmap:
        a=aliasmap[path];witness={'category':'prior-alias-catalog','alias':a['alias'],'approvedRegularRecord':a['approvedRegularRecord'],'oldBindingEvidenceSHA256':hashlib.sha256(aliasraw).hexdigest()};counts['priorAliasCatalog']+=1
    elif path in oldmap and oldmap[path]['approvedWitness'] is not None:
        witness={'category':'prior-direct-used-witness','priorEvidencePin':{'path':str(prior/'used-dependencies.json'),'bytes':len(oldraw),'sha256':hashlib.sha256(oldraw).hexdigest()},'approvedWitness':oldmap[path]['approvedWitness']};counts['priorDirect']+=1
    elif path in added and path.startswith(tc['sdk']['root']+'/'):
        witness=selected_original_pin(path);counts['newSelectedOriginalRecord']+=1
    else:witness=None
    row={'normalizedPath':path,'references':refs,'approvedWitness':witness}
    (used if witness else unmatched).append(row)
(d/'used-dependencies.json').write_text(json.dumps({'priorEvidenceSHA256':hashlib.sha256(oldraw).hexdigest(),'rawDependencyOccurrences':occurrences,'uniqueNormalizedDependencies':len(all_deps),'depfiles':depfiles,'addedPaths':added,'removedPaths':removed,'coverageByProvenance':counts,'covered':used,'unmatched':unmatched,'unmatchedPayloadReads':False,'notAFullUnchangedSourceSidecarMappingRepeat':True,'coverageIsNotIndependentCompilerOpenTrace':True},ensure_ascii=False,indent=2)+'\n')
(d/'selected-new-dependency-records.json').write_text(json.dumps({'records':selected,'metadataBuffersRead':[{'path':path,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()} for path,raw in metadata_buffers.items()],'sourceRecordsDecoded':len(selected),'noHeaderPayloadOpened':True},ensure_ascii=False,indent=2)+'\n')

physical=[]
for a in aliases:
    path=a['alias']['record']['path'];expected=a['alias']['record'];pin=a['approvedRegularRecord'];ls=os.lstat(path);link=os.readlink(path)
    assert stat.S_ISLNK(ls.st_mode) and link==expected['linkname']
    target=os.path.normpath(str(Path(path).parent/link));assert target==pin['path']
    target_stat=os.stat(path);old_target=a['targetOriginalSupplyRecord']['record']
    assert stat.S_ISREG(target_stat.st_mode) and target_stat.st_size==pin['bytes'] and target_stat.st_dev==old_target['device'] and target_stat.st_ino==old_target['inode']
    physical.append({'path':path,'operations':['lstat','readlink','stat-follow-alias'],'lstat':{'device':ls.st_dev,'inode':ls.st_ino,'bytes':ls.st_size,'mode':oct(stat.S_IMODE(ls.st_mode)),'mtime_ns':ls.st_mtime_ns},'linkname':link,'lexicalTarget':target,'followStat':{'device':target_stat.st_dev,'inode':target_stat.st_ino,'bytes':target_stat.st_size,'mtime_ns':target_stat.st_mtime_ns},'approvedRegularPin':pin,'matchesOriginalCatalogLinknameAndTargetIdentity':True,'targetContentRehashedByThisCheck':False})
(d/'sdk-alias-current-identities.json').write_text(json.dumps({'twoOnly':physical,'originalCatalogEvidenceSHA256':hashlib.sha256(aliasraw).hexdigest(),'noHeaderPayloadOpened':True,'compilerActualOpenTraceObserved':False},ensure_ascii=False,indent=2)+'\n')

external=json.loads((d/'external-build-output-manifest.json').read_bytes());outputs={x['path']:x for x in external['files']}
compiles=json.loads((d/'generated/compile_commands.json.raw').read_bytes());compile_rows=[]
for c in compiles:
    argv=shlex.split(c['command']);assert argv[0]==tc['executables']['cxx']['path'] and argv[argv.index('-arch')+1]=='arm64' and '-mmacosx-version-min=15.0' in argv and '-std=c++17' in argv
    assert argv[argv.index('-isysroot')+1]==tc['sdk']['root'] and not any('NL_WITH_NODE' in x or 'NAPI_VERSION' in x for x in argv)
    compile_rows.append({**c,'parsedArgv':argv})
links=[]
for name in ['location_core_test','location_child_probe']:
    text=(d/f'generated/CMakeFiles/{name}.dir/link.txt.raw').read_text();argv=shlex.split(text);objects=[os.path.normpath(str(b/x)) for x in argv if x.endswith('.o')];assert objects and all(x in outputs for x in objects)
    links.append({'target':name,'command':text,'argv':argv,'explicitObjectInputs':[outputs[x] for x in objects],'expandedLinkerArgvObserved':False,'selectedTbdAndArchiveMembersObserved':False})
info=(d/'generated/CMakeFiles/4.4.4/CMakeCXXCompiler.cmake.raw').read_text();implicit={}
for key in ['CMAKE_CXX_IMPLICIT_LINK_LIBRARIES','CMAKE_CXX_IMPLICIT_LINK_DIRECTORIES']:
    match=re.search(r'set\('+key+r' "([^"\n]*)"\)',info);implicit[key]=match.group(1).split(';') if match else None
(d/'compile-and-link-evidence.json').write_text(json.dumps({'compileCommands':compile_rows,'linkDriverCommands':links,'implicitCompilerProbeObservation':implicit,'implicitObservationIsFinalArtifactTrace':False,'actualSelectedLinkerInputsClosure':'PENDING; no new -t/-map, rebuild or runtime.'},ensure_ascii=False,indent=2)+'\n')

inspection=json.loads((d/'inspection-plan.json').read_bytes());summaries=[]
for name in ['location_core_test','location_child_probe']:
    commands={x['label']:x for x in inspection['commands'] if x['target']==name}
    texts={label:(d/c['stdout']).read_text() for label,c in commands.items()};loads=texts['load-commands'];symbols=texts['symbol-table'];undefined=texts['undefined-symbols'].splitlines()
    assert 'arm64' in texts['file-format']
    v=re.search(r'cmd LC_BUILD_VERSION\s+cmdsize \d+\s+platform (\S+)\s+minos (\S+)\s+sdk (\S+)',loads);assert v and v.group(2)=='15.0' and v.group(3)=='27.0'
    imports=[];loaders=[];rpaths=[]
    for chunk in re.split(r'Load command \d+\n',loads):
        for cmd,field,values in [('LC_LOAD_DYLIB','name',imports),('LC_LOAD_DYLINKER','name',loaders),('LC_RPATH','path',rpaths)]:
            if re.search(r'cmd '+cmd+r'\b',chunk):
                m=re.search(r'\n\s+'+field+r' (.+) \(offset',chunk);assert m;values.append(m.group(1))
    nl=[line.split()[-1] for line in symbols.splitlines() if re.search(r' external _nl_',line) and '(undefined)' not in line]
    rename_symbol=[line for line in symbols.splitlines() if '_renamex_np' in line]
    if name=='location_core_test':assert '_renamex_np' in undefined and len(rename_symbol)==1 and '(undefined)' in rename_symbol[0] and '(from libSystem)' in rename_symbol[0] and '_rename' not in undefined and len(nl)==11
    summaries.append({'target':name,'formatOutput':texts['file-format'],'LC_BUILD_VERSION':{'platformLiteral':v.group(1),'minos':v.group(2),'sdk':v.group(3)},'importedDylibNames':imports,'dynamicLoaders':loaders,'rpaths':rpaths,'nlExternalSymbols':nl,'undefinedSymbols':undefined,'renamexNpSymbolTableLines':rename_symbol,'notExecuted':True})
(d/'artifact-static-summary.json').write_text(json.dumps({'artifacts':summaries,'renamexNpResolutionEvidence':'link exit0 + nm undefined external symbol annotated from libSystem; no runtime resolver/FS execution observed','minimumOSIsStaticEvidenceOnly':True,'selectedLinkerArchiveRuntimeClosure':'PENDING'},ensure_ascii=False,indent=2)+'\n')
counts_out={'priorUsedObjectsVisited':877,'currentSourceObjects':9,'actualDepfileTokenVisits':occurrences,'newUniqueDependencyBindingVisits':len(all_deps),'selectedNewSourceRecordsDecoded':len(selected),'aliasPhysicalMetadataOperations':6,'aliasBindingRecordsVisited':2,'sourceMetadataBufferReadBytes':sum(len(x) for x in metadata_buffers.values()),'full42772MappingPasses':0,'dependencyPayloadHashReads':False,'knownMainLogicalVisits':877+9+occurrences+len(all_deps)+len(selected)+6+2,'remainingSmallProcessObjectsIncludedIn15000OwnerPostbuildReserve':True,'actualOSIOBytes':None}
(d/'used-analysis-counts.json').write_text(json.dumps(counts_out,ensure_ascii=False,indent=2)+'\n')
assert not unmatched
print(json.dumps({'depfiles':len(depfiles),'rawTokens':occurrences,'unique':len(all_deps),'added':added,'removed':removed,'provenance':counts,'unmatched':len(unmatched),'selectedMetadataRecords':len(selected),'twoAliasCurrentIdentityMatched':True,'renamexNp':'undefined from libSystem','notExecuted':True,'mainLogicalVisits':counts_out['knownMainLogicalVisits']},ensure_ascii=False))
