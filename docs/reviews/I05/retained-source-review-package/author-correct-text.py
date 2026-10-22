#!/usr/bin/env python3
"""Correct only new authored text proof; do not rebuild archive or run product."""
import base64, datetime, hashlib, json, pathlib, subprocess, time
ROOT=pathlib.Path(__file__).resolve().parent;TREE=ROOT.parents[3];P="docs/reviews/I05/retained-source-review-package/"
REPO=pathlib.Path("/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio")
records=[];tool=[]
def sha(b):return hashlib.sha256(b).hexdigest()
def save(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def run(a,persist=True):
    t=time.monotonic();cp=subprocess.run(a,cwd=TREE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    r={"argv":a,"cwd":str(TREE),"exitCode":cp.returncode,"durationSeconds":time.monotonic()-t,
       "stdoutBase64":base64.b64encode(cp.stdout).decode(),"stderrBase64":base64.b64encode(cp.stderr).decode(),
       "stdoutBytes":len(cp.stdout),"stderrBytes":len(cp.stderr)}
    if persist:
        records.append(r);save(ROOT/"text-correction-command-log.json",{"records":records})
    else:tool.append(r)
    return cp,r
def main():
    cp,_=run(["git","rev-parse","HEAD"]);assert cp.returncode==0
    prior=cp.stdout.decode().strip();assert prior=="8d9afe71f472d9db055de76b3dcdbb956d7b8862"
    for name in ["author-finish.py","author-freeze.py"]:
        p=ROOT/name;b=p.read_bytes();p.write_bytes(b.rstrip(b"\n")+b"\n")
    p=ROOT/"readme.md"
    p.write_text(p.read_text()+"\n补充：初次Prettier受仓库ignore影响，exit0不能证明覆盖；原输出保留。后续text-correction-proof.json的显式 --ignore-path /dev/null 才是新作者文件格式检查。原author-build.py、author-finish-first.py作为首次失败作者器保留EOF，不清洗；完整base→packet whitespace仍保留其两项例外，另给精确排除两件后的检查，不称全量绿。\n",encoding="utf-8")
    names=["readme.md","coverage-matrix.md","coverage-matrix.json","zcode-glm53-input.md","minimax-m31flash-input.md",
           "current-policy-addendum.md","dispatch-requirements.json","retained-branch-queue.json","bootstrap-incidents.json"]
    paths=[str(ROOT/n) for n in names]
    prettier=str(REPO/"node_modules"/".bin"/"prettier")
    cp,_=run([prettier,"--ignore-path","/dev/null","--write",*paths]);assert cp.returncode==0
    cp,format_record=run([prettier,"--ignore-path","/dev/null","--check",*paths]);assert cp.returncode==0
    proof={"priorPacketCandidate":"25c52a5a6a4b284de7184fbda9d9bf2386512d46","priorProcess":prior,
      "firstWhitespace":"staged-whitespace-result.json exit2 preserved; nine newly authored EOF findings, not historical product failure.",
      "firstFormatterBoundary":"author-validation.json formatting string records the old exit0; default repo ignore meant it did not prove nine explicit paths formatted. Do not rely on it for formatting coverage.",
      "correction":"Existing local Prettier --ignore-path /dev/null explicit9 paths write/check; current two active helper EOFs normalized. Original first-failure author-build.py and author-finish-first.py unchanged.",
      "formatCheck":format_record,"archiveUnchanged":"84876346B/4bbbd798e6c7a67153db51e185c8795d9ac3509cc4442a81e2071bf319dfaa12",
      "noArchiveRebuildOrProductRecheck":True,"bundleReadback":"Existing author-validation payload/member/ref checks remain valid; no archive bytes changed.",
      "firstScriptCopyBoundary":"author-finish-first.py preserves v1 text via apply_patch copy, which may add a terminal LF. It is not asserted byte-identical to the originally executed helper. Original tool cat/traceback stay in conversation; no product source affected.",
      "finalPacketCandidate":"Assigned by new actual Git commit; communicated externally, no circular self SHA.",
      "taskCount":0,"independentPacketReview":"pending root"}
    save(ROOT/"text-correction-proof.json",proof)
    excluded={"candidate-complete-manifest.json","text-correction-command-log.json","final-packet-receipt.json"}
    members=[]
    for p in sorted(ROOT.rglob("*")):
        if p.is_file() and p.relative_to(ROOT).as_posix() not in excluded:
            b=p.read_bytes();members.append({"path":p.relative_to(TREE).as_posix(),"bytes":len(b),"sha256":sha(b)})
    save(ROOT/"candidate-complete-manifest.json",{"format":"i05-packet-candidate-complete-members/1","files":members,
      "count":len(members),"bytes":sum(r["bytes"] for r in members),
      "exclusions":sorted(excluded),"exclusionMeaning":"Self and evolving process-only log/receipt; all primary payload, author scripts, original first-failure receipts, previous packet manifest and staged whitespace receipt included. Candidate Git commits bind excluded process files."})
    cp,_=run(["git","add","--",P]);assert cp.returncode==0
    cp,full=run(["git","diff","--cached","--check"]);assert cp.returncode==0
    # Check full base→working index, preserving exactly two original helper EOF exceptions.
    cp,whole=run(["git","diff","--cached","--check","5f910b52c69d86a1076b2032e5d3c63e715947f3","--",P])
    assert cp.returncode==2
    cp,limited=run(["git","diff","--cached","--check","5f910b52c69d86a1076b2032e5d3c63e715947f3","--",P,":(exclude)"+P+"author-build.py",":(exclude)"+P+"author-finish-first.py"])
    assert cp.returncode==0
    save(ROOT/"text-correction-whitespace.json",{"currentDelta":full,"fullBaseToCandidate":whole,"onlyTwoOriginalAuthorHelperEOFExcluded":limited,
      "notClaimed":"Complete base diff is not whitespace green; original helper bytes retained."})
    # Remaining operations are exact tool-only self-binding records, no log mutation after stage.
    cp,_=run(["git","add","--",P+"text-correction-command-log.json",P+"text-correction-whitespace.json"],False);assert cp.returncode==0
    cp,_=run(["git","-c","core.hooksPath=/dev/null","-c","commit.gpgsign=false","commit","-m","docs(I05): correct explicit packet formatting scope and complete manifest"],False);assert cp.returncode==0
    cp,_=run(["git","rev-parse","HEAD"],False);assert cp.returncode==0;candidate=cp.stdout.decode().strip()
    m=json.loads((ROOT/"input-manifest.json").read_text())
    receipt={"packetCandidate":candidate,"sourceBase":m["base"],"sourceCandidate":m["candidate"],"sourceProcess":m["process"],"bundle":m["bundle"],
      "members":22492,"uniquePayloads":3006,"verifiedHardlinks":19486,"inputManifestSHA256":sha((ROOT/"input-manifest.json").read_bytes()),
      "completeCandidateManifestSHA256":sha((ROOT/"candidate-complete-manifest.json").read_bytes()),
      "prompts":{n:{"bytes":(ROOT/n).stat().st_size,"sha256":sha((ROOT/n).read_bytes())} for n in ["zcode-glm53-input.md","minimax-m31flash-input.md"]},
      "actualExternalTaskCount":0,"actualExternalTasks":[],"actualExternalReports":[],"independentPacketReview":"pending root fresh agent",
      "productExecution":False,"nativeAndHOLDTicket":"not signed; not executed","noPushPrMerge":True,
      "whitespace":"Current delta0; complete base→packet2 for original author-build/author-finish-first EOF, exact two exclusions0; all receipts retained.",
      "processSHA":"Reported externally from actual final process commit; self excluded."}
    save(ROOT/"final-packet-receipt.json",receipt)
    cp,_=run(["git","add","--",P+"final-packet-receipt.json"],False);assert cp.returncode==0
    cp,_=run(["git","-c","core.hooksPath=/dev/null","-c","commit.gpgsign=false","commit","-m","docs(I05): bind corrected complete packet candidate and prompt hashes"],False);assert cp.returncode==0
    cp,_=run(["git","rev-parse","HEAD"],False);assert cp.returncode==0;process=cp.stdout.decode().strip()
    cp,_=run(["git","status","--short"],False);assert cp.returncode==0
    print(json.dumps({"candidate":candidate,"process":process,"status":cp.stdout.decode(),"receipt":receipt,"finalExactToolCommandRecords":tool},ensure_ascii=False))
if __name__=="__main__":main()
