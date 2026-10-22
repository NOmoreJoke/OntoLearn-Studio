# coding: utf-8
"""F1 repair only: six environment files and own metadata, no installations."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shlex
import subprocess

HERE=Path(__file__).parent
spec=importlib.util.spec_from_file_location('setup_helper',HERE/'bootstrap.py')
helper=importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
rows=[]
for item in helper.ITEMS:
    root=Path(item['tree'])
    session=root/'build/review-session'
    shellpath=session/'environment.sh'
    old=shellpath.read_bytes()
    metadata=session/'metadata'
    before={'files':len(list(metadata.iterdir())),'bytes':sum(p.stat().st_size for p in metadata.iterdir() if p.is_file())}
    _,values,clear=helper.env_for(root)
    shell='#!/bin/sh\n# Source only for this physical review tree.\n'
    shell+='unset '+' '.join(clear)+'\n'
    shell+='\n'.join('export '+k+'='+shlex.quote(v) for k,v in values.items())+'\n'
    shell+='cd '+shlex.quote(str(root))+'\n'
    shellpath.write_text(shell)
    env=dict(os.environ,I02_EVIDENCE='/foreign-not-written/c1-stale-evidence.json')
    command=['/bin/sh','-c','. "$1"; printf "%s" "$I02_EVIDENCE"','sh',str(shellpath)]
    p=subprocess.run(command,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    assert p.returncode==0 and p.stdout==str(session/'raw/c1-evidence.json') and not p.stderr
    new=shellpath.read_bytes()
    receipt={'tree':str(root),'finding':'F1/P2','beforeEnvironment':{'bytes':len(old),'sha256':hashlib.sha256(old).hexdigest()},
      'afterEnvironment':{'bytes':len(new),'sha256':hashlib.sha256(new).hexdigest()},'argv':command,
      'injectedInheritedI02_EVIDENCE':env['I02_EVIDENCE'],'stdout':p.stdout,'stderr':p.stderr,'exitCode':p.returncode,
      'metadataBefore':before,'metadataAfterBeforeThisReceipt':{'files':len(list(metadata.iterdir())),'bytes':sum(q.stat().st_size for q in metadata.iterdir() if q.is_file())},
      'receiptGrowth':'one new own metadata JSON after this snapshot; logical files/bytes, not OS operation count',
      'productExecuted':False,'dependencyReinstalled':False}
    helper.dump(metadata/'environment-isolation-repair.json',receipt)
    rows.append(receipt)
helper.dump(HERE/'F1-environment-repair.json',{'scope':'six environment files plus own repair metadata only','rows':rows,'productExecuted':False,'osActualMetadataOperations':None})
print(json.dumps({'repairedTrees':len(rows),'pureShellReadbacksPassed':len(rows),'productExecuted':False}))
