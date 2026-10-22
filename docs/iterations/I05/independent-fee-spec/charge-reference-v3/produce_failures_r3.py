"""New R3 evidence only. Does not execute the old reviewer or collector."""
from pathlib import Path
import json
import hashlib
import test_complete_failures_r3 as vectors
HERE=Path(__file__).resolve().parent
cases=[]
for label,data in vectors.CASES.items():
    result=vectors.run_case(label,data)
    cases.append({'id':label,'input':data,'invoice':result})
    print(label,result['state'],result['firstError'],flush=True)
out={'format':'i05-pure-full-entry-failure-programs/3','sourceSha256':hashlib.sha256((HERE/'reference.py').read_bytes()).hexdigest(),'sourceIndependentInputs':'independent-r2-adversarial.json (read-only; no collector executed)','cases':cases}
(HERE/'complete-failure-programs-r3.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
