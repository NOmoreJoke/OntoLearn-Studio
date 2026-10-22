#!/usr/bin/env python3
"""R2 docs mapping author: only fixed Git/JSON/hash and new packet-prefix writes."""
import base64, hashlib, json, pathlib, subprocess, time
ROOT=pathlib.Path(__file__).resolve().parent;TREE=ROOT.parents[3]
PREFIX="docs/reviews/I05/retained-source-review-package/"
REVISION="1106f15629c41833be9c9604eb7bf02134fa0541"
MAIN="2cf0c3328de464e15a3fa9cdbfdf6aa88d0b4a64";C4="523c478d5f39671c4ac7c1ea6997e51d3047d58e"
A15="a15f1478e398fb3b58fd60b1421a9cad04fdb430";S43="43d56317f0bfbdfeec05efc583b306615ae54a30"
EXT=pathlib.Path("/Users/kyle/Documents/工作/知爻/本体/iteration-control/2026-10-21-weekly-release")
REPO=pathlib.Path("/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio")
records=[]
def sha(b):return hashlib.sha256(b).hexdigest()
def save(name,o):
    p=ROOT/name;assert not p.exists(),str(p)+" already exists"
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def cmd(argv):
    started=time.time();p=subprocess.run(argv,cwd=TREE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    r={"argv":argv,"cwd":str(TREE),"exitCode":p.returncode,"startedUnix":started,"stdoutBytes":len(p.stdout),
       "stdoutSHA256":sha(p.stdout),"stdoutBase64":base64.b64encode(p.stdout).decode(),
       "stderrBytes":len(p.stderr),"stderrSHA256":sha(p.stderr),"stderrBase64":base64.b64encode(p.stderr).decode()}
    records.append(r)
    (ROOT/"author-command-log-r2.json").write_text(json.dumps({"records":records},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    assert p.returncode==0
    return p.stdout
def tree(ref,paths=None):
    args=["git","ls-tree","-r","-z","-l","--full-tree",ref]
    if paths:args+=["--",*paths]
    out={}
    for line in cmd(args).split(b"\0"):
        if not line:continue
        meta,path=line.split(b"\t",1);mode,kind,oid,size=meta.decode().split();assert kind=="blob"
        out[path.decode()]={"gitBlob":oid,"bytes":int(size),"mode":mode}
    return out
def main():
    assert cmd(["git","rev-parse","HEAD"]).decode().strip()==REVISION
    assert not cmd(["git","diff","--cached","--name-only"]).strip()
    originals=tree(REVISION,[PREFIX]);preserved=[]
    for path,m in originals.items():
        b=(TREE/path).read_bytes()
        assert hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()==m["gitBlob"]
        preserved.append({"path":path,**m,"sha256":sha(b),"currentEqualsRevisionGit":True})
    report=ROOT/"independent-review-r1.md"
    assert report.stat().st_size==11850 and sha(report.read_bytes())=="a4cd549887845cb6788a3e54a48b27202046bc86200957116df13982f8a214c7"
    bundle=next(r for r in preserved if r["path"]==PREFIX+"frozen-inputs.tar.gz")
    assert bundle["bytes"]==84876346 and bundle["sha256"]=="4bbbd798e6c7a67153db51e185c8795d9ac3509cc4442a81e2071bf319dfaa12"
    save("prior-originals-preservation-r2.json",{"revisionBase":REVISION,"count":len(preserved),"files":preserved,
      "allPriorCurrentEqualsFixedGit":True,"priorPacket124PlusReviewRoot10":"Actual fixed prefix count above; no old file rewritten.",
      "archive":"Opaque SHA only; not decompressed, regenerated or repacked."})
    im=json.loads((ROOT/"input-manifest.json").read_text());by={(r["member"].split("/")[1],r["sourcePath"]):r for r in im["members"]}
    groups=[
      ("main-source-only",MAIN,["docs/prd/PRD-本体学习与落地Agent工作台.md",
       "docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md",
       "docs/reviews/I03/inputs/m0-review-and-update-plan-2026-10-19.md",
       "docs/architecture/0001-desktop-framework.md","docs/iterations/I01/ADR-0002-storage.md","docs/m0-checklist.md"]),
      ("reference-C4",C4,["docs/reviews/I05/round-1/full-review-input.md","docs/reviews/I05/round-2/full-review-input.md","docs/reviews/I05/round-3/full-review-input.md",
       "docs/reviews/I05/inputs-c1/I05-launch-prompt.md","docs/reviews/I05/inputs-c1/I05-resume-integrated-I04-20261021.md",
       "docs/reviews/I05/inputs-c1/goal-objective.md","docs/reviews/I05/inputs-c1/parallel-coordination.md",
       "docs/reviews/I05/inputs-c1/policy.md","docs/reviews/I05/inputs-c1/scope.md","docs/reviews/I05/inputs-c1/sources.json",
       "docs/reviews/I05/round-1/zcode-glm53.md","docs/reviews/I05/round-1/minimax-m31flash.md",
       "docs/reviews/I05/round-1/observed-terminals.json"])]
    mapping=[]
    for cohort,ref,paths in groups:
        actual=tree(ref,paths)
        for path in paths:
            r=by[(cohort,path)];m=actual[path]
            value=cmd(["git","cat-file","blob",m["gitBlob"]])
            assert len(value)==m["bytes"]==r["bytes"] and sha(value)==r["sha256"] and r["gitBlob"]==m["gitBlob"]
            mapping.append({"cohort":cohort,"archiveMember":r["member"],"sourceRef":ref,"sourcePath":path,
              "bytes":len(value),"sha256":sha(value),"gitBlob":m["gitBlob"],"readRequired":True})
    save("original-material-map-r2.json",{"revisionBase":REVISION,"bundleSHA256":bundle["sha256"],"originals":mapping,
      "activeM0":"snapshots/main-source-only/docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md",
      "M0AlternativeSameBytes":"snapshots/main-source-only/docs/reviews/I03/inputs/m0-review-and-update-plan-2026-10-19.md",
      "historicalI05Inputs":"All three real round1/2/3 full inputs plus seven inputs-c1 originals; no round4 invented.",
      "oldR1WrongLinks":"Historical only; do not follow R1 prompt/readme as R2 instructions."})
    md="# R2 原件精确映射\n\n活跃M0原件为主2cf的I01 inputs版本；I03 inputs副本逐字相同。历史I05必须读实际round1、round2、round3全文及inputs-c1七件，另读C1双报告与终态。不存在的旧round4指路不延用。每一行均核固定Git/blob/bytes/SHA与原bundle清单，无需重解包。\n\n| archive member | ref | bytes | SHA256 |\n|---|---|---:|---|\n"
    for r in mapping:md+="| "+r["archiveMember"]+" | "+r["sourceRef"]+" | "+str(r["bytes"])+" | "+r["sha256"]+" |\n"
    (ROOT/"original-material-map-r2.md").write_text(md,encoding="utf-8")
    delta=cmd(["git","diff","--name-only","-z",S43,A15]).decode().split("\0");paths=[p for p in delta if p];assert len(paths)==143
    actual=tree(A15,paths);carriers=["reference-integer-product","reference-integer-process","reference-date-product","reference-date-process"];shape=[]
    for path in paths:
        m=actual[path];locations=[]
        for cohort in carriers:
            r=by[(cohort,path)];assert r["gitBlob"]==m["gitBlob"] and r["bytes"]==m["bytes"]
            locations.append({"archiveMember":r["member"],"sourceRef":r["sourceRef"],"sourcePath":path,"gitBlob":r["gitBlob"],"bytes":r["bytes"],"sha256":r["sha256"]})
        assert len({r["sha256"] for r in locations})==1
        shape.append({"originalProcessRef":A15,"originalSourcePath":path,**m,"sha256":locations[0]["sha256"],"carriers":locations})
    save("shape-process-map-r2.json",{"originalProcessRef":A15,"relativeToProduct":S43,"processDeltaCount":143,"all143SamePathBlobInFourExistingCarriers":True,"items":shape,
      "SHAEvidence":"Existing bundle member SHA values independently rehashed in R1; R2 additionally checks exact source a15 Git blob/bytes and all four carrier blob identities. No new archive or false cohort added."})
    guidance=[]
    for name,path in {"AGENTS-current-r2.md":REPO/"AGENTS.md","developer-common-instructions-r2.md":EXT/"developer-common-instructions.md",
       "desktop-operation-policy-r2.md":EXT/"desktop-operation-policy-20261022.md","external-review-permissions-r2.md":EXT/"external-review-permissions.md"}.items():
        b=path.read_bytes();target=ROOT/"r2-guidance"/name;assert not target.exists();target.parent.mkdir(exist_ok=True);target.write_bytes(b)
        guidance.append({"path":"r2-guidance/"+name,"sourcePath":str(path),"bytes":len(b),"sha256":sha(b)})
    save("guidance-manifest-r2.json",{"files":guidance,"historicalGuidanceUnchanged":True})
    print(json.dumps({"priorFiles":len(preserved),"originalMapRows":len(mapping),"shapeRows":len(shape),"bundleSHA":bundle["sha256"],"commands":len(records)},ensure_ascii=False))
if __name__=="__main__":main()
