#!/usr/bin/env python3
"""Freeze only new review-package documentation and evidence, no hooks or product."""
import base64, datetime, gzip, hashlib, json, pathlib, subprocess, time
ROOT=pathlib.Path(__file__).resolve().parent
TREE=ROOT.parents[3]
PREFIX="docs/reviews/I05/retained-source-review-package/"
def sha(b):return hashlib.sha256(b).hexdigest()
def save(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
records=[];final_tool_records=[]
def command(argv,label,persist=True):
    t=time.monotonic();started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    cp=subprocess.run(argv,cwd=TREE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
    r={"argv":argv,"cwd":str(TREE),"startedUTC":started,"durationSeconds":time.monotonic()-t,"exitCode":cp.returncode,
       "stdout":{"bytes":len(cp.stdout),"sha256":sha(cp.stdout),"base64":base64.b64encode(cp.stdout).decode()},
       "stderr":{"bytes":len(cp.stderr),"sha256":sha(cp.stderr),"base64":base64.b64encode(cp.stderr).decode()}}
    if persist:
       records.append(r);save(ROOT/"author-freeze-command-log.json",{"records":records,"finalProcessBindingBoundary":"Final process add/commit/revparse are tool-output records only to avoid circularly mutating their committed log."})
    else:final_tool_records.append(r)
    if cp.returncode:raise RuntimeError(label+" failed; exact streams retained")
    return cp.stdout
def main():
    assert command(["git","branch","--show-current"],"branch").decode().strip()=="docs/I05-retained-source-review-package"
    initial=command(["git","status","--short"],"status").decode()
    assert not command(["git","diff","--cached","--name-only"],"empty-index").strip()
    m=json.loads((ROOT/"input-manifest.json").read_text());v=json.loads((ROOT/"author-validation.json").read_text())
    assert v["memberCount"]==22492 and v["uniquePayloadMembers"]==3006 and v["verifiedHardlinks"]==19486
    dynamic={"author-freeze-command-log.json","author-freeze-receipt.json","packet-file-manifest.json"}
    files=[p for p in ROOT.rglob("*") if p.is_file() and p.relative_to(ROOT).as_posix() not in dynamic]
    manifest=[{"path":p.relative_to(TREE).as_posix(),"bytes":p.stat().st_size,"sha256":sha(p.read_bytes())} for p in sorted(files)]
    save(ROOT/"packet-file-manifest.json",{"scope":"All prepared packet files before candidate freeze, excluding self and future process-only freeze log/receipt. Git candidate binds self.","files":manifest,"payloadFiles":len(manifest),"payloadBytes":sum(r["bytes"] for r in manifest)})
    paths=[p.relative_to(TREE).as_posix() for p in files]+[PREFIX+"packet-file-manifest.json"]
    command(["git","add","--",*sorted(paths)],"stage-exact-prefix")
    staged=command(["git","diff","--cached","--name-only","-z"],"staged-paths").decode().split("\0")
    assert all(p.startswith(PREFIX) for p in staged if p) and "AGENTS.md" not in staged
    check=subprocess.run(["git","diff","--cached","--check"],cwd=TREE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    # Original fixed guidance copies may retain original whitespace; preserve exact
    # failure rather than normalize any historical input.
    check_record={"argv":["git","diff","--cached","--check"],"cwd":str(TREE),"exitCode":check.returncode,
       "stdoutBase64":base64.b64encode(check.stdout).decode(),"stderrBase64":base64.b64encode(check.stderr).decode()}
    save(ROOT/"staged-whitespace-result.json",check_record)
    command(["git","add","--",PREFIX+"staged-whitespace-result.json"],"stage-whitespace-receipt")
    command(["git","-c","core.hooksPath=/dev/null","-c","commit.gpgsign=false","commit","-m","docs(I05): freeze complete retained source review inputs"],"candidate-commit")
    candidate=command(["git","rev-parse","HEAD"],"candidate-ref").decode().strip()
    receipt={"candidateCommit":candidate,"sourceBase":m["base"],"sourceCandidate":m["candidate"],"sourceProcess":m["process"],
      "bundle":m["bundle"],"memberCount":v["memberCount"],"uniquePayloadMembers":v["uniquePayloadMembers"],"hardlinks":v["verifiedHardlinks"],
      "mainPromptSHA256":{n:sha((ROOT/n).read_bytes()) for n in ["zcode-glm53-input.md","minimax-m31flash-input.md"]},
      "inputManifestSHA256":sha((ROOT/"input-manifest.json").read_bytes()),"packetManifestSHA256":sha((ROOT/"packet-file-manifest.json").read_bytes()),
      "actualDesignatedTaskCount":0,"actualTasks":[],"actualReports":[],"independentPacketReview":"pending root fresh independent agent",
      "productRuntime":"not executed; all source-only/runtime/HOLD/native gates remain",
      "guidanceNotStaged":True,"initialStatus":initial,"stagedWhitespace":check_record,
      "authorStructureOnly":"22492 archive members;3006 payloads SHA256/Git blob identity;19486 hardlinks;all full snapshot pathsets;source61f6docs;27 finish commands",
      "firstFailures":"bootstrap ReferenceError, first random gzip hardlink readback interrupted130, first textual name-list quotation mismatch exit1 all preserved; corrected structural readback passed",
      "processCommitSelfBinding":"Final process commit communicated externally. Its exact add/commit/revparse stdout/stderr are emitted to tool output rather than mutate a committed receipt after the fact."}
    save(ROOT/"author-freeze-receipt.json",receipt)
    command(["git","add","--",PREFIX+"author-freeze-command-log.json",PREFIX+"author-freeze-receipt.json"],"stage-process",persist=False)
    command(["git","-c","core.hooksPath=/dev/null","-c","commit.gpgsign=false","commit","-m","docs(I05): bind source review packet candidate and author receipts"],"process-commit",persist=False)
    process=command(["git","rev-parse","HEAD"],"process-ref",persist=False).decode().strip()
    status=command(["git","status","--short"],"final-status",persist=False).decode()
    print(json.dumps({"candidate":candidate,"process":process,"status":status,"bundle":m["bundle"],"memberCount":v["memberCount"],
      "promptSHA256":receipt["mainPromptSHA256"],"inputManifestSHA256":receipt["inputManifestSHA256"],
      "packetManifestSHA256":receipt["packetManifestSHA256"],"stagedWhitespaceExit":check.returncode,"finalToolOnlyExactCommandRecords":final_tool_records},ensure_ascii=False))
if __name__=="__main__":main()

