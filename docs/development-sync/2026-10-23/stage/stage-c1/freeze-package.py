# -*- coding: utf-8 -*-
from pathlib import Path
import hashlib,json,datetime
from zoneinfo import ZoneInfo
root=Path(__file__).resolve().parent
rows=[]
for p in sorted((root/'payload').rglob('*')):
 if p.is_file():
  b=p.read_bytes();rows.append({'path':str(p.relative_to(root)),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
raw=(json.dumps({'schemaVersion':1,'label':'stage-acceptance-20261022-review-c1','files':rows},ensure_ascii=False,indent=2)+'\n').encode()
(root/'payload-manifest.json').write_bytes(raw)
sha=hashlib.sha256(raw).hexdigest()
c={'schemaVersion':1,'label':'stage-acceptance-20261022-review-c1','preparedAt':datetime.datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'payloadManifestSHA256':sha,'payloadFiles':len(rows),'browserIndexSHA256':'adff7f408e1844392d550a7e0a3bdacb5e1c1cd167b24d3b236a517456033a81','desktopSourceCommit':'5f910b52c69d86a1076b2032e5d3c63e715947f3','desktopZIP_SHA256':'a54ad42daed0713101eea9163eb3723c2ffea1feaedb8c54b880d1f1708bc163','currentGuidanceSHA256':'de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4','specifiedNewTasksCreated':False,'specifiedDualVerdict':'not_started','subjectScope':'Full new stage shell and packaging combination, exact existing source snapshots and evidence; no complete-product claim'}
(root/'candidate.json').write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n')
(root/'PAYLOAD-FILES.md').write_text('# Complete frozen payload file list\n\n| Path | Bytes | SHA-256 |\n| --- | ---: | --- |\n'+''.join('| '+r['path']+' | '+str(r['bytes'])+' | '+r['sha256']+' |\n' for r in rows))
print(sha,len(rows))
