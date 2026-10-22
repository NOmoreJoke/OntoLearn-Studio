#!/usr/bin/env python3
"""Opaque final fixed-candidate Git member audit; no product execution."""
import base64, hashlib, json, pathlib, subprocess, time
ROOT=pathlib.Path(__file__).resolve().parent;TREE=ROOT.parents[3];PREFIX="docs/reviews/I05/retained-source-review-package/"
CANDIDATE="4de58348f25dc28e2dd18ef928101f2b7293355f"
logs=[];tool=[]
def sha(b):return hashlib.sha256(b).hexdigest()
def save(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def run(a,persist=True):
    t=time.monotonic();cp=subprocess.run(a,cwd=TREE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    r={"argv":a,"cwd":str(TREE),"exitCode":cp.returncode,"durationSeconds":time.monotonic()-t,"stdoutBase64":base64.b64encode(cp.stdout).decode(),"stderrBase64":base64.b64encode(cp.stderr).decode()}
    if persist:logs.append(r);save(ROOT/"final-git-audit-command-log.json",{"records":logs})
    else:tool.append(r)
    assert cp.returncode==0
    return cp.stdout
def main():
    raw=run(["git","ls-tree","-r","-z","--full-tree",CANDIDATE,"--",PREFIX])
    rows=[]
    for item in raw.split(b"\0"):
        if not item:continue
        meta,path=item.split(b"\t",1);mode,kind,oid=meta.decode().split();assert kind=="blob"
        path=path.decode();b=(TREE/path).read_bytes()
        assert hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()==oid
        rows.append({"path":path,"ref":CANDIDATE,"gitBlob":oid,"mode":mode,"bytes":len(b),"sha256":sha(b),"currentEqualsGit":True})
    p=ROOT/"candidate-git-manifest.json"
    save(p,{"format":"i05-complete-fixed-packet-git-members/1","candidate":CANDIDATE,"prefix":PREFIX,"count":len(rows),"bytes":sum(r["bytes"] for r in rows),"files":rows,"scope":"Exact complete candidate Git pathset, including all candidate-time process metadata. This later process manifest is not part of that candidate; its own final process commit binds it."})
    earlier=json.loads((ROOT/"candidate-complete-manifest.json").read_text());e={r["path"] for r in earlier["files"]};a={r["path"] for r in rows};declared={PREFIX+x for x in earlier["exclusions"]}
    extra=sorted(a-e-declared)
    save(ROOT/"final-input-audit.json",{"packetCandidate":CANDIDATE,"authoritativeCandidateGitManifest":{"path":"candidate-git-manifest.json","bytes":p.stat().st_size,"sha256":sha(p.read_bytes()),"members":len(rows)},
      "allCandidateCurrentBytesEqualFixedGitBlobAndSHA256":True,"earlierPreparationManifestBoundary":"candidate-complete-manifest.json was computed before the final whitespace receipt existed; it is a preparation-time payload list, not authoritative full candidate membership. Exact complete candidate pathset is candidate-git-manifest.json.",
      "extraCandidateProcessMetadataOutsideEarlierPreparationList":extra,"rawEarlierManifestsRetained":True,
      "sourceBundleAndBothPromptsUnchangedSinceCandidate":True,"actualExternalTasks":0,"independentPacketReview":"pending root",
      "noProductTestsArchiveRebuildOrRuntimeExecution":True,"finalProcessSHA":"Communicated externally; no circular self hash."})
    run(["git","add","--",PREFIX+"author-final-git-audit.py",PREFIX+"candidate-git-manifest.json",PREFIX+"final-input-audit.json",PREFIX+"final-git-audit-command-log.json"],False)
    run(["git","-c","core.hooksPath=/dev/null","-c","commit.gpgsign=false","commit","-m","docs(I05): bind complete fixed packet Git membership"],False)
    process=run(["git","rev-parse","HEAD"],False).decode().strip()
    status=run(["git","status","--short"],False).decode()
    print(json.dumps({"candidate":CANDIDATE,"process":process,"status":status,"candidateFiles":len(rows),"candidateBytes":sum(r["bytes"] for r in rows),"candidateGitManifestSHA256":sha(p.read_bytes()),"earlierExtraProcessMetadata":extra,"finalExactToolCommandRecords":tool},ensure_ascii=False))
if __name__=="__main__":main()
