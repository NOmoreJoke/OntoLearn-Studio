#!/usr/bin/env python3
"""Finish only immutable packet structure checks; never run product code."""
import base64, datetime, gzip, hashlib, json, pathlib, subprocess, tarfile, time
ROOT=pathlib.Path(__file__).resolve().parent
TREE=ROOT.parents[3]
REPO=pathlib.Path("/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio")
def sha(b): return hashlib.sha256(b).hexdigest()
def save(p,obj): p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
records=[]
def command(argv,label,cwd=REPO):
    t=time.monotonic();started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    cp=subprocess.run(argv,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
    p=ROOT/"command-streams"/("finish-v2-"+str(len(records)+1).zfill(3)+"-"+label+".stdout.gz")
    with p.open("wb") as f:
      with gzip.GzipFile(filename="",mode="wb",fileobj=f,mtime=0) as z:z.write(cp.stdout)
    records.append({"argv":argv,"cwd":str(cwd),"startedUTC":started,"durationSeconds":time.monotonic()-t,
        "exitCode":cp.returncode,"stdout":{"path":str(p.relative_to(ROOT)),"lossless":"gzip","bytes":len(cp.stdout),"sha256":sha(cp.stdout)},
        "stderr":{"bytes":len(cp.stderr),"sha256":sha(cp.stderr),"base64":base64.b64encode(cp.stderr).decode()}})
    save(ROOT/"author-finish-v2-command-log.json",{"records":records})
    if cp.returncode:raise RuntimeError(label+" failed; original streams preserved")
    return cp.stdout
def main():
    m=json.loads((ROOT/"input-manifest.json").read_text())
    bpath=ROOT/m["bundle"]["path"]
    assert bpath.stat().st_size==m["bundle"]["bytes"] and sha(bpath.read_bytes())==m["bundle"]["sha256"]
    expected={r["member"]:r for r in m["members"]};seen=set();verified={};regular=links=0
    # Sequential stream: each actual payload read once, every backward hardlink
    # must bind a previously verified exact blob/hash/size. No random gzip seek.
    with tarfile.open(bpath,mode="r|gz") as tar:
      for ti in tar:
        assert ti.name in expected and ti.name not in seen
        seen.add(ti.name);r=expected[ti.name]
        assert ti.mode==(int(r["mode"],8)&0o777)
        if ti.isfile():
            value=tar.extractfile(ti).read()
            assert len(value)==r["bytes"] and sha(value)==r["sha256"]
            assert hashlib.sha1(b"blob "+str(len(value)).encode()+b"\0"+value).hexdigest()==r["gitBlob"]
            assert r["hardlinkTarget"] is None
            verified[ti.name]=(r["gitBlob"],r["bytes"],r["sha256"]);regular+=1
        else:
            assert ti.islnk() and ti.linkname==r["hardlinkTarget"] and ti.linkname in verified
            assert verified[ti.linkname]==(r["gitBlob"],r["bytes"],r["sha256"])
            verified[ti.name]=verified[ti.linkname];links+=1
    assert seen==set(expected)
    cohorts={}
    for r in m["members"]:cohorts.setdefault(r["sourceRef"],set()).add(r["sourcePath"])
    for cohort in m["cohorts"]:
        paths=set(filter(None,command(["git","ls-tree","-r","-z","--name-only",cohort["ref"]],"names-"+cohort["label"]).decode().split("\0")))
        actual={r["sourcePath"] for r in m["members"] if r["member"].startswith("snapshots/"+cohort["label"]+"/")}
        if cohort["label"]=="main-completion-process":
            delta=set(command(["git","diff","--name-only",m["candidate"],m["process"]],"completion-delta").decode().splitlines())
            assert actual==delta and len(actual)==6
        else:assert actual==paths
    patch=json.loads((ROOT/"candidate.patch.json").read_text());value=base64.b64decode(patch["data"],validate=True)
    assert len(value)==patch["bytes"] and sha(value)==patch["sha256"]
    for p in (ROOT/"reference-diffs").glob("*.json"):
        row=json.loads(p.read_text());v=base64.b64decode(row["data"],validate=True)
        assert len(v)==row["bytes"] and sha(v)==row["sha256"]
    queue=json.loads((ROOT/"retained-branch-queue.json").read_text())
    base=m["base"]
    for row in queue["additionalRetainedBranches"]:
        argv=["git","diff","--binary","--full-index",base,row["head"],"--","apps","packages","scripts","tests",".github","uv.lock","package.json","package-lock.json"]
        v=command(argv,"queued-diff-"+row["tree"])
        p=ROOT/"reference-diffs"/("queued-"+row["tree"]+".json")
        save(p,{"base":base,"head":row["head"],"argv":argv,"scope":"Retained branch source/test/config roots; queued separate review, not adopted into main.","bytes":len(v),"sha256":sha(v),"encoding":"base64","data":base64.b64encode(v).decode()})
        row["sourceDiff"]={"path":str(p.relative_to(ROOT)),"bytes":len(v),"sha256":sha(v)}
    save(ROOT/"retained-branch-queue.json",queue)
    guidance=json.loads((ROOT/"guidance-manifest.json").read_text())
    for name,r in guidance.items():
        v=(ROOT/"guidance"/name).read_bytes()
        assert len(v)==r["bytes"] and sha(v)==r["sha256"]
    for p in ROOT.rglob("*.json"):json.loads(p.read_text())
    # Explicitly format newly authored prose/matrix/dispatch only. Archived inputs,
    # raw stream gzip, lossless diff JSON, original manifests/receipts stay exact.
    prettier=REPO/"node_modules"/".bin"/"prettier"
    format_targets=["readme.md","coverage-matrix.md","coverage-matrix.json","zcode-glm53-input.md","minimax-m31flash-input.md",
        "current-policy-addendum.md","dispatch-requirements.json","retained-branch-queue.json","bootstrap-incidents.json"]
    formatting="not run: existing local formatter unavailable; no installation attempted"
    if prettier.is_file():
        paths=[str(ROOT/x) for x in format_targets]
        command([str(prettier),"--write",*paths],"format-authored",TREE)
        command([str(prettier),"--check",*paths],"format-check-authored",TREE)
        formatting="existing local Prettier explicit9 authored paths write/check exit0; no install/network"
    validation={"format":"packet-structure-validation/2","memberCount":len(seen),"uniquePayloadMembers":regular,"verifiedHardlinks":links,
       "everyActualPayloadBytesSHA256AndGitBlobIdentity":True,"allBackwardHardlinksBindPreviouslyVerifiedContent":True,
       "fullSnapshotPathSetsMatchExactGitRefs":True,"sourceProcessDeltaCount":6,"bundle":m["bundle"],"formatting":formatting,
       "candidateDiffBase64SHA":patch["sha256"],"queuedSourceDiffs":len(queue["additionalRetainedBranches"]),
       "scope":"Pure Git/hash/tar/JSON/formatter packet structure. No product imports, tests, probe/generator/model/native/DB/network/install/GUI execution.",
       "productRuntimePass":False,"externalReviewsDispatched":0,
       "firstReadback":"Interrupted exit130 during random gzip hardlink seeking; original author-build.py and actual tool traceback preserved. No source data changed.",
       "repair":"Single sequential tar stream; hash all actual payloads once and validate every exact backward hardlink, full member/ref inventory.",
       "bootstrapBoundary":"Early tool-only read-only inventory, author bootstrap ReferenceError and progress ls exit1 preserved without fabricating split streams."}
    save(ROOT/"author-validation.json",validation)
    print(json.dumps({"members":len(seen),"regular":regular,"hardlinks":links,"bundleBytes":bpath.stat().st_size,"commands":len(records),"formatting":formatting},ensure_ascii=False))
if __name__=="__main__":main()

