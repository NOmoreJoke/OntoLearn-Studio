"""Independent stdlib document-only proof. No product imports/default evaluation/codecs."""
import base64
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path.cwd()
BASE = "6b94c152a8fca0f0e26d377b0e4d79ff4d64b8b5"
OLD = "0841ffbe7a4599fbea96f4ff998808f3f4e00972"
CAND = "92352c581d958300d566037e5df7a1cbde660f61"
PROC = "e2125ef17a901e70bd83b2e7d48373eba7bf6b92"
R = "docs/reviews/I05/d2-canonical-interface-design-r2/"
D = "docs/iterations/I05/d2-canonical-interface-design-r2/"
B = "docs/iterations/I05/d2-canonical-interface-design/"
checks = []
commands = []
def check(name, truth):
    checks.append({"id": name, "pass": bool(truth)})
def sha(b):
    return hashlib.sha256(b).hexdigest()
def command(argv, cwd=ROOT, retain=True):
    r = subprocess.run(argv, cwd=cwd, capture_output=True)
    row = {"argv": argv, "cwd": str(cwd), "exit": r.returncode,
           "stdoutBytes": len(r.stdout), "stdoutSHA256": sha(r.stdout),
           "stderrBytes": len(r.stderr), "stderrSHA256": sha(r.stderr),
           "stderrBase64": base64.b64encode(r.stderr).decode()}
    if retain:
        row["stdoutBase64"] = base64.b64encode(r.stdout).decode()
    else:
        row["stdoutImmutableObjectReference"] = argv[-1]
    commands.append(row)
    check("command-success-" + str(len(commands)), r.returncode == 0)
    return r.stdout
def git(ref, path, cwd=ROOT):
    return command(["git", "show", ref + ":" + path], cwd, False)
def read(path):
    return json.loads((ROOT / path).read_text())
def identity(member, ref, cwd=ROOT, path=None, snapshot=None):
    path = path or member["path"]
    b = git(ref, path, cwd)
    cur = (cwd / path).read_bytes()
    check("git-working-" + path, b == cur)
    check("size-" + path, len(b) == member["bytes"])
    check("hash-" + path, sha(b) == member["sha256"])
    if snapshot:
        check("snapshot-" + path, b == (ROOT / snapshot).read_bytes())
    return {"path": path, "bytes": len(b), "sha256": sha(b), "ref": ref,
            "currentEqualsFixedGit": b == cur}

check("branch", command(["git", "branch", "--show-current"]).decode().strip() == "docs/I05-d2-consumer-design")
head = command(["git", "rev-parse", "HEAD"]).decode().strip()
status = command(["git", "status", "--short"]).decode()
protected = read(R + "type-input-identity.json")["protectedInventory"]
check("protected-unique-205", len(protected) == len({m["path"] for m in protected}) == 205)
protected_results = [identity(m, BASE) for m in protected]
canonical = [m for m in protected if "/d2-canonical-interface-design/" in m["path"]]
check("protected-29-canonical", len(canonical) == 29)
for m in protected:
    if m not in canonical:
        check("historical176-" + m["path"], git(OLD, m["path"]) == (ROOT / m["path"]).read_bytes())
manifest_path = R + "type-directory-r2-manifest.json"
manifest = read(manifest_path)
new = list(manifest["files"]) + [{"path": manifest_path, "bytes": 5339, "sha256": "f6bbc95cef3d0b588739b7a332d50cf15e63d3aa0dda3736477fdbdff502a18c"}]
new_results = [identity(m, CAND) for m in new]
new.append({"path": R + "type-directory-r2-process-receipt.json", "bytes": 81542, "sha256": "b9a3246e11eee57489f46d09e82ed41e84da6136b80a0991ab8423d16a5162bd"})
new_results.append(identity(new[-1], PROC))
delta = command(["git", "diff", "--name-status", BASE, CAND]).decode().splitlines()
check("exact-candidate-22-additions", set(delta) == {"A\t" + m["path"] for m in new[:-1]})
check("process-single-addition", command(["git", "diff", "--name-status", CAND, PROC]).decode().strip() == "A\t" + new[-1]["path"])
recep_dir = Path("/Users/kyle/Documents/工作/知爻/本体/iteration-control/2026-10-21-weekly-release")
source_tree = Path("/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-canonical-interface-inventory")
input_results = []
for name, snap in [("I05-canonical-interface-inventory-D2-limited-reception-20261022.json", "docs/reviews/I05/d2-canonical-interface-design/fixed-inputs/"), ("I05-type-directory-two-doc-D2-reception-20261023.json", R + "fixed-type-inputs/")]:
    grant = json.loads((recep_dir / name).read_text())
    for m in grant["allowlist"]:
        input_results.append(identity(m, m["ref"], source_tree, snapshot=snap + Path(m["path"]).name))
check("only13-received-inputs", len(input_results) == 13)
for name, n, h in [("report.md",11122,"35b1d913c4baf3bbe07d3a582ae16fd9ed76479d77841e865b89b0ec5efc5b11"),("receipt.json",5188,"59e20cd2a31de65a0f4a220b20eafcf565cb2ca27295aef21900fc0e6b7da600")]:
    b = (ROOT / ("docs/reviews/I05/d2-canonical-interface-design/independent-r1-" + name)).read_bytes()
    check("formal-r1-"+name, len(b)==n and sha(b)==h)

facts=read(R + "fixed-type-inputs/type-directory.json")
fmap=read(D + "type-field-map.json")
blue=read(D + "proposed-type-records.json")
oldmap=read(B + "field-codec-bridge.json")
revision=read(D + "revision-delta.json")
for m in revision["baselineEightDesigns"]:
    identity(m, BASE)
check("17-source-classes", len(facts["records"]) == len(fmap["directories"]) == len(blue["records"]) == 17)
check("86-source-fields", sum(len(r["fieldsInSourceOrder"]) for r in facts["records"]) == len(fmap["fieldRows"]) == 86)
rows = {r["id"]: r for r in fmap["fieldRows"]}
check("86-unique", len(rows) == 86)
oldrows = {r["id"]: r for r in oldmap["fieldRows"]}
expected_row_order = []
field_evidence=[]
for i, (src, dst, proposed) in enumerate(zip(facts["records"], fmap["directories"], blue["records"])):
    cls=src["className"]
    names=[f["name"] for f in src["fieldsInSourceOrder"]]
    check(cls+"-class-id", dst["id"]=="helper:"+cls and dst["className"]==cls)
    check(cls+"-field-order", dst["orderedFields"]==names and proposed["requiredFields"]==names)
    check(cls+"-count", dst["fieldCount"]==src["fieldCount"]==len(names))
    check(cls+"-basis", dst["basisPointer"]=="/records/"+str(i) and proposed["basisPointer"]==dst["basisPointer"] and dst["basisRef"]=="d6ecbc887e1bf9acd5e98b18237d6740d2e61796")
    pin={k:src[k] for k in ["sourceRef","sourcePath","sourceBytes","sourceSHA256","classLine","classEndLine","decoratorSyntax","baseSyntax"]}
    check(cls+"-pin", dst["classSourcePin"]==pin)
    check(cls+"-not-wire-or-approved", dst["wireDiscriminator"] is None and dst["approvedProjectionMembershipProven"] is False)
    check(cls+"-new-proposed", proposed["status"]=="NEW-PROPOSED-NOT-ADOPTED" and proposed["originalWireDiscriminator"] is None and proposed["adoptedAdapterPin"] is None and proposed["registrationApprovedSetEquivalence"] is False)
    check(cls+"-blueprint-count", len(proposed["fieldBlueprints"])==len(names))
    for j,(s,bp) in enumerate(zip(src["fieldsInSourceOrder"],proposed["fieldBlueprints"])):
        rid="helper:"+cls+"/"+s["name"]
        expected_row_order.append(rid)
        row=rows[rid]
        for key in ["annotationSyntax","defaultSyntax","sourceLine"]:
            check(rid+"-"+key,row[key]==s[key])
        check(rid+"-order-and-name",row["sourceOrder"]==j and row["fieldName"]==s["name"] and row["className"]==cls and row["directoryId"]==dst["id"])
        check(rid+"-pointer",row["pureFactPointer"]=="/records/"+str(i)+"/fieldsInSourceOrder/"+str(j))
        check(rid+"-fact-pin", row["pureFactInput"]==revision["newFacts"][0])
        check(rid+"-product-pin-metadata",row["originalProductSourcePinMetadataOnly"]=={k:src[k] for k in ["sourceRef","sourcePath","sourceBytes","sourceSHA256"]})
        check(rid+"-blueprint",bp["name"]==s["name"] and bp["annotationExpressionShape"]==s["annotationSyntax"] and bp["declaredDefaultSyntax"]==s["defaultSyntax"] and bp["requiredEvenWithDeclaredDefault"] is True)
        check(rid+"-no-adopt",row["valueGrammarGate"] is False and row["requiredInProposedExport"] is True and "never evaluate or fill" in row["defaultPolicy"])
        check(rid+"-baseline-overlap",row["baselineRow"]==(rid if rid in oldrows else None))
        field_evidence.append({"id":rid,"sourceOrder":j,**s,"pureFactPointer":row["pureFactPointer"]})
check("full-field-order", [r["id"] for r in fmap["fieldRows"]]==expected_row_order)
overlap=set(rows)&set(oldrows)
check("27-overlap",len(overlap)==27 and overlap==set(fmap["replaceOnlyRowIds"]))
overlap_dirs={oldrows[r]["layout"] for r in overlap}
check("7-overlap-dirs",len(overlap_dirs)==7)
known=0
refined=[]
for rid in sorted(overlap):
    old=oldrows[rid]
    if old["existingAnnotation"] is not None:
        known+=1
        check(rid+"-old-known-annotation",old["existingAnnotation"]==rows[rid]["annotationSyntax"])
    else:
        refined.append(rid)
check("14-refined-not-guessed",len(refined)==14 and set(refined)==set(revision["oldUnknownAnnotationsRefined"]))
remaining=[r for r in oldmap["fieldRows"] if r["id"] not in overlap]
check("236-preserved-reference",len(remaining)==236 and fmap["untouchedBaselineRowsReference"]==revision["baselineEightDesigns"][1])
effective=remaining+fmap["fieldRows"]+fmap["reviewDeltaFieldRows"]
effective_dirs=[d for d in oldmap["directories"] if d["id"] not in overlap_dirs]+fmap["directories"]+fmap["reviewDeltaDirectories"]
check("325-effective-unique-rows",len(effective)==len({r["id"] for r in effective})==325)
check("64-effective-unique-directories",len(effective_dirs)==len({d["id"] for d in effective_dirs})==64)
check("10-new-type-directories59fields",len(fmap["directories"])-len(overlap_dirs)==10 and len(rows)-len(overlap)==59)

api=read("docs/reviews/I05/d2-canonical-interface-design/fixed-inputs/api-layouts.json")
p2dirs={d["id"]:d for d in fmap["reviewDeltaDirectories"]}
p2rows={r["id"]:r for r in fmap["reviewDeltaFieldRows"]}
sel="api:legacy-provenance/selectedFacts[*]"
mut="api:probe-production-observation/known-optional-branches"
check("pure-selected-wrapper-fact", "list of {triple,sources}" in api["layouts"][1]["selectedFacts"])
check("wrapper-fields",p2dirs[sel]["orderedFields"]==["triple","sources"])
check("wrapper-parent",p2dirs[sel]["parentField"]=="api:legacy-provenance/selectedFacts")
for name in ["triple","sources"]:
    check("wrapper-required-"+name,p2rows[sel+"/"+name]["requiredWhenParentInstanceExists"] is True)
links=fmap["parentInstanceLinks"]
check("selectedFacts-i-link",links[0]["parentField"]=="api:legacy-provenance/selectedFacts" and links[0]["childDirectory"]==sel and links[0]["selector"]=="selectedFacts[i]")
check("source-j-link",links[1]["parentField"]==sel+"/sources" and links[1]["selector"]=="selectedFacts[i].sources[j]" and links[1]["childDirectories"]==["legacy-selected-source:asserted","legacy-selected-source:rdfs","legacy-selected-source:rule"])
check("branch-link-targets-exist",set(links[1]["childDirectories"])<= {d["id"] for d in oldmap["directories"]})
check("mutation-pure-known-optional",api["layouts"][11]["optionalBranch"].startswith("mutation;"))
check("mutation-optional-not14threquired",p2dirs[mut]["orderedFields"]==["mutation"] and p2rows[mut+"/mutation"]["requiredWhenParentInstanceExists"] is False and p2dirs[mut]["requiredParentKeysUnchanged"]==13)
parent=next(d for d in oldmap["directories"] if d["id"]=="api:probe-production-observation")
check("ordinary13unchanged",parent["orderedFields"]==api["layouts"][11]["orderedKeys"] and len(parent["orderedFields"])==13)
policy=fmap["knownOptionalBranchPolicy"]["mutation"]
check("absent-distinct-from-null", "do not fill None" in policy["absent"] and "distinct from absence" in policy["presentNull"] and "legality unknown" in policy["presentNull"])
check("unknowninner-gated",all(r["originalValueGrammar"]=="not-closed-in-received-facts" and r["actualFieldObserved"] is False for r in p2rows.values()))
check("transitive-object-paths",all(any(x in p for p in blue["explicitUnclosedPaths"]) for x in ["ProfileValue.value","ComparisonEvidence.left/right","PreparedFiring.comparisons","PreparedFiringBatch.firings","native_result:dict"]))
authority=read(D+"authority-requests-update.json")
check("Q01-directory-only",authority["receivedDirectoryPart"]["status"]=="received-limited-pure-declarations" and authority["pendingRequests"][0]["actualReceivedPin"] is None)
check("all9-requests-pending",len(authority["pendingRequests"])==9 and all(q["actualReceivedPin"] is None and q["sourceFollowingAuthorized"] is False for q in authority["pendingRequests"]))
check("identity-role-only-body-unread",authority["policyRoleReceptionOnly"]["bodyRead"] is False and authority["policyRoleReceptionOnly"]["actualImplementationAdoption"] is False and authority["oldActualNullPinsNotBackfilled"] is True)
check("runtime-not-authorized",authority["runtimeAuthorized"] is False and authority["newCodecAdopted"] is False and authority["sameIssueAndLiveAuthorityStillFalse"] is True)
digest=read(D+"digest-bridge-update.json")
check("old16-retained-no-new",digest["all16ExistingRecipesAndOriginalPreimagesUnchanged"] is True and digest["newExistingDigestRecipes"]==[] and digest["implementationExpressionStillUnevaluated"] is True and digest["oldRowsSliceStill8192PythonCharacters"] is True)

# Controlled declarative metadata mutants. These are not product/schema/codec tests.
def metadata_matches(candidate):
    return [(r["id"],r["annotationSyntax"],r["defaultSyntax"],r["sourceOrder"],r["sourceLine"],r["pureFactPointer"]) for r in candidate] == [(r["id"],r["annotationSyntax"],r["defaultSyntax"],r["sourceOrder"],r["sourceLine"],r["pureFactPointer"]) for r in fmap["fieldRows"]]
mutants=[]
for label, key, value in [("default-text-is-not-null","defaultSyntax",None),("str-does-not-become-enum","annotationSyntax","Literal[guessed]"),("wrong-source-line","sourceLine",999999),("wrong-source-order","sourceOrder",999),("wrong-pointer","pureFactPointer","/records/16/fieldsInSourceOrder/99")]:
    modified=copy.deepcopy(fmap["fieldRows"])
    modified[0][key]=value
    rejected=not metadata_matches(modified)
    mutants.append({"id":label,"detected":rejected})
    check("metadata-mutant-"+label,rejected)
modified=copy.deepcopy(fmap["fieldRows"])
modified[-1]=copy.deepcopy(modified[0])
check("same86count-tail-loss-detected",not metadata_matches(modified) and len(modified)==86)

failed=[r for r in checks if not r["pass"]]
result={"format":"independent-r2-document-proof/1","scope":"fixed document delta only; human semantic findings separate","base":BASE,"candidate":CAND,"process":PROC,"observedHead":head,"observedStatus":status,"assertions":len(checks),"failed":failed,"checks":checks,"protected205":protected_results,"new23":new_results,"authorized13Inputs":input_results,"fieldEvidence86":field_evidence,"overlap27":sorted(overlap),"knownAnnotationsPreserved":known,"refined14":refined,"effectiveCounts":{"directories":len(effective_dirs),"rows":len(effective)},"metadataMutants":mutants,"commands":commands,"blobStdoutBoundary":"Git blob stdout bound by exact immutable ref:path bytesSHA, not copied as readable ungranted old content. All Git stderr retained separately in base64.","productOrOldCodecExecuted":False,"semanticCompletenessCertifiedByCount":False}
print(json.dumps(result,ensure_ascii=False,indent=2))
sys.exit(1 if failed else 0)
