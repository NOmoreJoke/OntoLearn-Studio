"""Create declarative JSON schemas from literals; no runtime or target imports."""
import json
from pathlib import Path
P = Path(__file__).resolve().parent

def obj(properties, required=None):
    return {'type':'object','additionalProperties':False,'properties':properties,
            'required':list(properties) if required is None else required}
def arr(items, minimum=0, maximum=100000):
    return {'type':'array','items':items,'minItems':minimum,'maxItems':maximum}
def ref(name): return {'$ref':'#/$defs/'+name}
def const(v): return {'const':v}
def enum(*v): return {'enum':list(v)}
string={'type':'string','minLength':1,'maxLength':8192}
sha={'type':'string','pattern':'^[0-9a-f]{64}$'}
gitref={'type':'string','pattern':'^[0-9a-f]{40}$'}
path={'type':'string','minLength':1,'maxLength':2048,'pattern':r'^(?!/)(?!.*\\)(?!.*(?:^|/)\.\.(?:/|$)).+$'}
integer={'type':'integer','minimum':0}
file=obj({'path':path,'bytes':integer,'sha256':sha})
source=obj({'ref':gitref,'path':path,'bytes':integer,'sha256':sha,'gitBlob':gitref})
fingerprint=obj({'algorithm':const('i05-code-object-marshal-filename-normalized/1'),
    'sha256':sha,'pythonCacheTag':string,
    'domain':const('actual-loader-code; not source bytes or a build approval')})
archiveCode=obj({'archivePath':path,'archiveSha256':sha,'memberName':string,
    'memberKind':enum('PYZ-module','CArchive-script','external-pyc'),
    'rawMemberBytes':integer,'rawMemberSha256':sha,'fingerprint':fingerprint,
    'extractionMethodVersion':string,'extractorSource':source})
installed_source=obj({'kind':const('installed-distribution-source'),'distribution':string,
    'version':string,'artifactSha256':sha,'installedRelativePath':path,'bytes':integer,
    'sha256':sha,'record':file})
compiled=obj({'source':{'anyOf':[source,installed_source]},'compileMode':const('exec'),'dontInherit':const(True),
              'optimize':const(0),'fingerprint':fingerprint})
module=obj({'canonicalName':string,'sourceCompilation':compiled,'actualArchiveCode':archiveCode,
    'expectedLoaderClass':string,'codeEqual':const(True),
    'role':enum('canonical-module','canonical-probe')})
installedFile=obj({'installedRelativePath':path,'bytes':integer,'sha256':sha,
    'recordDigest':{'type':['string','null']},'recordSize':{'type':['integer','null'],'minimum':0},
    'role':enum('code','data','metadata','license','notice','native','other'),
    'disposition':enum('bundled','omitted-not-runtime-with-owner-review','build-only'),
    'omissionReason':{'type':['string','null']},'bundleMappings':arr(obj({'path':path,'container':enum('directory','PYZ','CArchive'),
        'memberName':{'type':['string','null']},'bytes':integer,'sha256':sha}),0)})
artifact=obj({'kind':enum('wheel','sdist'),'filename':string,'url':string,
    'bytes':integer,'sha256':sha,'lockPackageName':string,'lockVersion':string,
    'platformTag':string,'selectedByMarker':string})
dist=obj({'name':string,'version':string,'selectedArtifact':artifact,
    'requiresDist':arr(string),'activatedExtras':arr(string),
    'metadata':file,'record':file,'installedFiles':arr(installedFile,1),
    'licenses':arr(obj({'sourceFile':file,'bundleFile':file,'classification':string,
        'noticeObligationReview':string}),1),'completeRecordMapping':const(True)})
python=obj({'implementation':const('cpython'),'version':{'type':'string','pattern':r'^3\.12\.\d+.*$'},
    'hexversion':integer,'cacheTag':string,'magicHex':{'type':'string','pattern':'^[0-9a-f]{8}$'},
    'marshalVersion':const(4),'optimize':const(0),'dontInherit':const(True),
    'compilerExecutable':file,'byteorder':enum('little','big'),'abiflags':{'type':'string'},
    'platform':string,'architecture':string,'flags':obj({'debug':integer,'inspect':integer,
        'interactive':integer,'optimize':const(0),'dontWriteBytecode':integer,
        'noUserSite':integer,'noSite':integer,'ignoreEnvironment':integer,
        'isolated':integer,'safePath':{'type':'boolean'},'utf8Mode':integer})})
defs={'file':file,'source':source,'fingerprint':fingerprint,'module':module,
      'distribution':dist,'python':python}
props={
 'format':const('i05-source-package-parity-build/1'),
 'profileId':const('i05-source-package-parity-v1'),
 'composition':obj({'baseRef':gitref,'compositionRef':gitref,'dependencyRef':gitref,
    'wrapperRef':gitref,'consumerDeltaRef':gitref,'i05SourceAncestorRef':const('2cf0c3328de464e15a3fa9cdbfdf6aa88d0b4a64'),
    'supplierRef':const('6891a5842302859a531cf82767c5a482417bc274'),
    'supplierProcessRef':const('f79a29f596b2444cba542a906c91727869014886'),
    't01AdoptionRef':const('dd972b79adf4d378636a7d41a6b0e3e08c0d5ca1'),
    't01AdoptionProcessRef':const('79d63cc1f403ee857a3af2a98f8870db9a6a910d'),
    'ownerAcceptanceRecord':source,'cleanGuardedPaths':const(True)}),
 'build':obj({'buildId':string,'profileDescriptor':source,'writers':arr(source,4,4),
    'command':arr(string,3,256),'environmentPolicyVersion':string,
    'buildToolDistributions':arr(dist,1,32),'target':const('packages/engine/src/ontolearn_engine/semantic_source_package_probe.py'),
    'name':const('ontolearn-semantic-parity'),'mode':const('onedir'),
    'contentsDirectory':const('_internal'),'stderrReceipt':file,'stdoutReceipt':file,
    'actualExitCode':const(0)}),
 'python':ref('python'),
 'codeDomain':obj({'algorithm':const('i05-code-object-marshal-filename-normalized/1'),
    'marshalProtocol':const(4),'normalizedFilename':const('<i05-canonical-code>'),
    'normalization':const('recursively replace co_filename only on exact CodeType values in co_consts; preserve every other field; marshal.dumps(normalized(code),4); sha256'),
    'sourceCompile':const('compile(exact approved source bytes, actual source path, exec, dont_inherit=True, optimize=0) using the build interpreter'),
    'comparisonScope':const('same exact Python build/cache tag/optimization and algorithm; cross-loader/cache/version stability must be evidenced, never assumed'),
    'marshalReferenceStability':enum('measured-same-domain') }),
 'inputs':obj({'modules':arr(source,23,23),'resources':arr(source,4,4),'pyproject':source,
    'lock':source,'assets':arr(source,2,2),'inputCounts':obj({'datasets':const(320),
        'observations':const(417),'mathInputContexts':const(83),'originalOperations':const(106),
        'learningChecks':const(54),'productCases':const(50)}),
    'selectors':const(['full-v1','b1-semantic-1x-v1','b1-semantic-10x-v1'])}),
 'archives':arr(obj({'path':path,'bytes':integer,'sha256':sha,'kind':enum('PYZ','CArchive','external-pyc'),
    'inventory':arr(obj({'name':string,'kind':string,'bytes':integer,'sha256':sha}),1),
    'extractorSource':source,'inventoryComplete':const(True)}),1,64),
 'moduleBindings':arr(ref('module'),23,23),
 'bootstrapBinding':obj({'carchiveScript':archiveCode,'sourceCompilation':compiled,
    'entryGuardBeforeTypes':const(True),'delegatesToCanonicalProbe':const(True),
    'codeEqual':const(True)}),
 'dynamicChecker':obj({'name':const('ontolearn_contract_v2'),'sourceCompilation':compiled,
    'bundleFile':file,'loaderCode':fingerprint,'codeEqual':const(True),
    'objectAuthority':const('resources.CONTRACT; not an independently exec-created alias'),
    'sysModulesRegistrationRequired':const(False)}),
 'functionBindings':arr(obj({'name':enum('semantic.reason','semantic.query',
      'semantic.validate_shacl_text','Validator.run'),
    'moduleName':string,'codeConstIndexPath':arr(integer,1,100),'sourceCompilation':compiled,
    'expectedFunctionCode':fingerprint,'actualArchiveFunctionCode':fingerprint,'codeEqual':const(True)}),4,4),
 'distributions':arr(ref('distribution'),8,8),
 'runtimeComponents':arr(obj({'name':string,'version':string,'kind':enum('python','stdlib',
      'pyinstaller-bootloader','dynamic-library','platform-runtime'),
    'sourceArtifacts':arr(file,1),'bundleFiles':arr(file,1),'licenses':arr(file,1),
    'noticeReview':string}),1),
 'payloadFiles':arr(file,1),
 'exclusions':obj({'engineModules':arr(string,1),'archiveVerifiedAbsent':const(True),
    'extraContractResourcesAbsent':const(True),'oracleAssetsAbsent':const(True)}),
 'completion':obj({'state':const('archive-code-source-bound'),
    'runtimeParity':const('not-run-by-builder'),'externalOracle':const('not-run-by-builder'),
    'receiptLocation':const('external final-build-receipt.json; never hashed into this file'),
    'selfHashIncluded':const(False),'payloadManifestExcludes':const(['provenance/i05/source-package-parity-build.json']),
    'unknownRequiredEvidence':const([])})
}
schema={'$schema':'https://json-schema.org/draft/2020-12/schema',
    '$id':'urn:ontolearn:i05:source-package-parity-build:1',
    'title':'Proposed strict external build provenance; no actual build instance supplied',
    '$comment':'Schema shape plus mandatory cross-field/identity checks in offer section 4 are jointly normative. Required build evidence may not be replaced by unknown/null/source hashes.',
    **obj(props),'$defs':defs}
(P/'build-provenance.schema.json').write_text(json.dumps(schema,ensure_ascii=False,indent=2)+'\n')
receipt=obj({'format':const('i05-final-build-receipt/1'),'compositionRef':gitref,
    'embeddedProvenance':file,'executable':file,'directoryManifest':file,
    'directoryFiles':arr(file,1),'archiveWitnessManifest':file,'approvedProfile':source,
    'buildInputsStableBeforeAfter':const(True),'externalCollectorSource':source,
    'schema':file,'runtimeValidation':enum('not-executed','collected-pending-comparison','compared'),
    'runtimeEvidenceManifest':{'anyOf':[file,{'type':'null'}]},
    'nonClaims':const(['parent-package-not-proved','S1-not-proved','Job-H-not-proved',
        'target-OS-CI-human-develop-gates-remain'])})
receipt={'$schema':'https://json-schema.org/draft/2020-12/schema',
    '$id':'urn:ontolearn:i05:final-build-receipt:1',**receipt}
(P/'final-build-receipt.schema.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
x=json.loads((P/'input-identities.json').read_text())
profile={'format':'i05-semantic-profile-offer/1','status':'draft-owner-acceptance-pending',
    'id':'i05-source-package-parity-v1','baseRef':x['base'],'acceptedCompositionRef':None,
    'builderFlag':'--i05-source-package-parity','target':'packages/engine/src/ontolearn_engine/semantic_source_package_probe.py',
    'name':'ontolearn-semantic-parity','mode':'onedir','contentsDirectory':'_internal',
    'proposedOutputPrefix':'build/i05-semantic-parity/{approved-composition-ref}/{platform-id}/',
    'outputPrefixStatus':'proposal; root must reserve prefix/resources before execution',
    'sourceArgv':['python','-m','ontolearn_engine.semantic_source_package_probe','--semantic-source-package-probe','{exact-selector}'],
    'frozenArgv':['ontolearn-semantic-parity','--semantic-source-package-probe','{exact-selector}'],
    'selectors':['full-v1','b1-semantic-1x-v1','b1-semantic-10x-v1'],
    'canonicalModules':x['modules23'],'resources':x['resources4'],'assets':x['assets2'],
    'hiddenImports':[m['module'] for m in x['modules23']]+['prettytable','wcwidth','packaging'],
    'collectAll':['rdflib','pyshacl','owlrl','html5rdf'],
    'copyMetadata':['rdflib','pyshacl','pyparsing','owlrl','html5rdf','prettytable','wcwidth','packaging'],
    'excludeEngineModules':['ontolearn_engine.quality.definitions','ontolearn_engine.quality.planning',
        'ontolearn_engine.semantic_profile_probe','ontolearn_engine.semantic_probe','ontolearn_engine.semantic_samples',
        'ontolearn_engine.storage','ontolearn_engine.storage_probe','ontolearn_engine.worker','ontolearn_engine.coordinator',
        'ontolearn_engine.job_store','ontolearn_engine.protocol','ontolearn_engine.__main__'],
    'forbidCollectAllEngine':True,'forbidCollectDataEngine':True,'forbidContractsGlob':True,
    'frozenResourceRoot':'_MEIPASS/contracts','frozenAssetRoot':'_MEIPASS/provenance/i05/source-package-parity',
    'frozenLock':'_MEIPASS/provenance/uv.lock',
    'frozenBuildProvenance':'_MEIPASS/provenance/i05/source-package-parity-build.json',
    'buildProvenanceSchema':'build-provenance.schema.json','externalReceiptSchema':'final-build-receipt.schema.json',
    'openDeltas':['I05 explicit frozen consumer + loader binding + probe self pin via approved descriptor',
        'T03 four writer/dependency adoption/profile implementation; root combination approval',
        'installed distribution/resources/license/runtime mapping and actual archive evidence',
        'T05 independent oracle and source/frozen/parent finite validation tickets'],
    'executionAuthorization':False}
(P/'profile-descriptor.draft.json').write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n')
print('Wrote declarative draft profile and two schemas; no builder/consumer executed.')
