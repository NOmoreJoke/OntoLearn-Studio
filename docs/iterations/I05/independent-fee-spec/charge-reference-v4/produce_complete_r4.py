"""New artifacts only; no reviewer script execution or business oracle output."""
from pathlib import Path
import hashlib
import json
import test_complete_failures_r4 as vectors
HERE=Path(__file__).resolve().parent
items=[]
for label,data in {**vectors.CASES,**vectors.EXTRA}.items():
    p=vectors.run_case(label,data);items.append({'id':label,'input':data,'invoice':p})
    print(label,p['state'],p['firstError'],flush=True)
(HERE/'complete-entry-programs-r4.json').write_text(json.dumps({'format':'i05-pure-complete-entry-programs/4','sourceSha256':hashlib.sha256((HERE/'reference.py').read_bytes()).hexdigest(),'cases':items},ensure_ascii=True,indent=2)+'\n')
