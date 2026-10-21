from pathlib import Path
from datetime import datetime,timezone
import os,stat,json,hashlib,time,traceback
D=Path(__file__).parent
LIST=D/'unhashed-system-cache-objects.json';OLD=D/'read-budget.json'
raw=LIST.read_bytes();oldraw=OLD.read_bytes()
assert len(raw)==24420 and hashlib.sha256(raw).hexdigest()=='a0a368c44eec7843270d9f65a517bf43fa546e3766aeeb3fceeea82b80c6f08c'
assert len(oldraw)==378 and hashlib.sha256(oldraw).hexdigest()=='32ef2836d14e348f6e5919eeade542d08322f48d109f2c01d6c88f657587bd42'
items=json.loads(raw);prior=json.loads(oldraw);assert prior['read_bytes']==2699211379
assert len(items)==81 and len({x['path'] for x in items})==81 and sum(x['bytes'] for x in items)==7046515706
assert all(x['path']==x['realpath'] and x['path'].startswith('/System/Volumes/Preboot/Cryptexes/OS/System/Library/dyld/dyld_shared_cache_arm64e') for x in items)
LIMIT=10737418240;BASE=2699211379;total=BASE;complete=[];failure=None
for name in ['dyld-delta-inputs.json','dyld-delta-read-events.jsonl','dyld-delta-complete-inventory.jsonl','dyld-delta-cumulative-read.json','dyld-delta-read-result.json']:
 assert not (D/name).exists(),'Preserve existing delta output '+name
now=lambda:datetime.now(timezone.utc).isoformat()
def signature(s):return {'device':s.st_dev,'inode':s.st_ino,'mode':oct(stat.S_IMODE(s.st_mode)),'bytes':s.st_size,'mtime_ns':s.st_mtime_ns,'ctime_ns':s.st_ctime_ns}
def dump(name,value):
 (D/name).write_text(json.dumps(value,indent=2)+'\n')
inputs={'started_utc':now(),'authorization':'dyld-delta-authorization.md','authorization_sha256':'b9da09643f78d64e506e20fd4c81d8b8a058c49134124b18b46e9580b449b95c','fixed_list_path':str(LIST),'fixed_list_bytes':len(raw),'fixed_list_sha256':hashlib.sha256(raw).hexdigest(),'old_budget_path':str(OLD),'old_budget_bytes':len(oldraw),'old_budget_sha256':hashlib.sha256(oldraw).hexdigest(),'base_read_bytes':BASE,'authorized_limit_bytes':LIMIT,'fixed_objects':81,'fixed_object_bytes':7046515706,'predicted_cumulative_bytes':9745727085,'inventory_item_count_unchanged':prior['inventory_items'],'directory_or_architecture_scan_performed':False,'data_read_accounting':'Prior cumulative bytes unchanged plus actual bytes returned by read for only the exact 81 authorized cache objects; supporting evidence/authorization reads are metadata, not new supply-body reads.'}
dump('dyld-delta-inputs.json',inputs)
with (D/'dyld-delta-read-events.jsonl').open('x') as events,(D/'dyld-delta-complete-inventory.jsonl').open('x') as inventory:
 def event(row):events.write(json.dumps(row)+'\n');events.flush()
 for i,item in enumerate(items):
  fd=None;count=0;h=hashlib.sha256();started=now();t=time.monotonic();rec={'ordinal':i+1,'path':item['path'],'expected_realpath':item['realpath'],'expected_bytes':item['bytes'],'started_utc':started}
  try:
   p=Path(item['path']);before=p.lstat()
   assert stat.S_ISREG(before.st_mode) and not stat.S_ISLNK(before.st_mode),'not a regular nonsymlink file'
   assert str(p.resolve(strict=True))==item['realpath'],'realpath changed'
   assert before.st_size==item['bytes'],'size differs from authorized fixed list'
   assert total+item['bytes']<=LIMIT,'insufficient remaining authorized read guard'
   rec['lstat_before']=signature(before);event(dict(rec,event='preflight-identity-matched',cumulative_read_bytes=total))
   fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW)
   assert signature(os.fstat(fd))==signature(before),'open identity changed'
   while count<item['bytes']:
    length=min(4*1024*1024,item['bytes']-count,LIMIT-total)
    assert length>0,'read guard exhausted'
    b=os.read(fd,length)
    if not b:raise OSError('unexpected EOF')
    count+=len(b);total+=len(b);h.update(b)
   assert total<LIMIT,'no budget remains to verify EOF'
   extra=os.read(fd,1);total+=len(extra)
   assert not extra,'file grew beyond authorized size'
   opened_after=os.fstat(fd);os.close(fd);fd=None;after=p.lstat()
   assert signature(opened_after)==signature(before) and signature(after)==signature(before),'pre/post file identity or metadata changed'
   rec.update(finished_utc=now(),elapsed_seconds=time.monotonic()-t,bytes_read=count,sha256=h.hexdigest(),lstat_after=signature(after),cumulative_read_bytes=total,status='COMPLETE_IDENTITY_AND_FULL_HASH')
   inventory.write(json.dumps(rec)+'\n');inventory.flush();complete.append(rec);event(dict(rec,event='complete'))
   dump('dyld-delta-cumulative-read.json',{'base_read_bytes':BASE,'new_actual_read_bytes':total-BASE,'cumulative_actual_read_bytes':total,'limit_read_bytes':LIMIT,'remaining_bytes':LIMIT-total,'completed_objects':len(complete),'pending_objects':len(items)-len(complete),'inventory_items_unchanged':prior['inventory_items']})
   if (i+1)%10==0 or i==80:print(json.dumps({'completed':len(complete),'cumulative_bytes':total,'remaining_budget':LIMIT-total}),flush=True)
  except Exception as exc:
   if fd is not None:os.close(fd)
   rec.update(finished_utc=now(),elapsed_seconds=time.monotonic()-t,bytes_read=count,partial_sha256=h.hexdigest(),cumulative_read_bytes=total,status='FIRST_FAILURE_STOPPED',error_type=type(exc).__name__,error=str(exc))
   failure=rec;event(rec)
   with (D/'dyld-delta-first-failure.json').open('x') as out:json.dump(rec,out,indent=2);out.write('\n')
   break
# Fixed input evidence is checked from bytes already held, not rewritten; no directory scanning or new objects added.
result={'finished_utc':now(),'expected_objects':81,'completed_objects':len(complete),'completed_object_bytes':sum(x['bytes_read'] for x in complete),'base_read_bytes':BASE,'new_actual_read_bytes':total-BASE,'cumulative_actual_read_bytes':total,'limit_read_bytes':LIMIT,'remaining_bytes':LIMIT-total,'inventory_items_unchanged':prior['inventory_items'],'all_81_pre_post_identity_and_hash_complete':len(complete)==81 and failure is None,'first_failure':failure,'pending_exact_paths':[x['path'] for x in items[len(complete):]],'status':'FIXED_81_CACHE_IDENTITY_HASH_COMPLETE' if len(complete)==81 and failure is None else 'STOPPED_INCOMPLETE','runtime_transitive_image_closure_proven':False,'postbuild_used_closure_proven':False,'approvals_changed':False,'old_evidence_overwritten':False}
dump('dyld-delta-read-result.json',result)
dump('dyld-delta-cumulative-read.json',{'base_read_bytes':BASE,'new_actual_read_bytes':total-BASE,'cumulative_actual_read_bytes':total,'limit_read_bytes':LIMIT,'remaining_bytes':LIMIT-total,'completed_objects':len(complete),'pending_objects':len(items)-len(complete),'inventory_items_unchanged':prior['inventory_items']})
print(json.dumps(result,indent=2),flush=True)
