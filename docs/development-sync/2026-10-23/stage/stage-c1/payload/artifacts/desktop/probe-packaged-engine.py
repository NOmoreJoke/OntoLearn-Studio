"""Run only the packaged Python engine; no Electron or GUI is launched."""
import json, os, select, subprocess, tempfile, uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parent
ENGINE=ROOT/'OntoLearn Stage Acceptance 20261022.app/Contents/Resources/engine/ontolearn-engine'
observations=[]
with tempfile.TemporaryDirectory(prefix='ontolearn-stage-acceptance-') as temp:
    env={key:value for key,value in os.environ.items() if not key.startswith(('ONTOLEARN_', 'PYTHON'))}
    env['ONTOLEARN_DB_PATH']=str(Path(temp)/'engine.sqlite')
    proc=subprocess.Popen([str(ENGINE)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env,text=True,bufsize=1)
    def request(method,params,session):
        value={'kind':'request','id':str(uuid.uuid4()),'protocolVersion':2,'engineSessionId':session,'method':method,'params':params}
        proc.stdin.write(json.dumps(value)+'\n');proc.stdin.flush()
        if not select.select([proc.stdout],[],[],20)[0]: raise RuntimeError('ENGINE_RESPONSE_TIMEOUT')
        result=json.loads(proc.stdout.readline())
        assert result['id']==value['id'] and result['ok'] is True
        observations.append({'method':method,'response':result})
        return result
    try:
        hello=request('hello',{'supportedVersions':[2],'clientId':str(uuid.uuid4())},None)
        session=hello['engineSessionId']
        for i in range(10):
            health=request('health',{},session)
            assert health['engineSessionId']==session and health['result']['status']=='ok'
        proc.stdin.close();proc.wait(timeout=20)
        assert proc.returncode==0
        stderr=proc.stderr.read();assert not stderr
    finally:
        if proc.poll() is None: proc.terminate();proc.wait(timeout=10)
probe=subprocess.run([str(ENGINE),'--storage-probe','--scale','1','--trial','0'],capture_output=True,text=True,timeout=90,check=True)
storage=json.loads(probe.stdout)
assert storage['scale']==1 and storage['triples']==18 and storage['result']==['urn:case:0:alarm/A01'] and storage['result']==storage['expected']
evidence={'packagedEngineExit':proc.returncode,'handshakeAndTenHealth':observations,'storageProbe':storage,'storageProbeExit':probe.returncode,'guiLaunched':False,'formalProjectDataUsed':False,'scope':'packaged CLI only; does not verify Electron UI, native recovery or business integration'}
(ROOT/'packaged-engine-probe.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'handshake':True,'healthReplies':10,'storageTriples':storage['triples'],'storageResult':storage['result'],'guiLaunched':False}))
