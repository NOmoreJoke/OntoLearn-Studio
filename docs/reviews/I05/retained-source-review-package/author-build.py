#!/usr/bin/env python3
"""Prepare immutable I05 review inputs only. Never import or execute product code."""
import base64, datetime, gzip, hashlib, io, json, os, pathlib, subprocess, tarfile, time

ROOT=pathlib.Path(__file__).resolve().parent
TREE=ROOT.parents[3]
REPO=pathlib.Path("/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio")
EXT=pathlib.Path("/Users/kyle/Documents/工作/知爻/本体/iteration-control/2026-10-21-weekly-release")
BASE="5f910b52c69d86a1076b2032e5d3c63e715947f3"
MAIN="2cf0c3328de464e15a3fa9cdbfdf6aa88d0b4a64"
PROCESS="61f53dbe76262f5003065900a4e97d9a6130014b"
REFS={
"main-source-only":MAIN,"main-completion-process":PROCESS,
"reference-C4":"523c478d5f39671c4ac7c1ea6997e51d3047d58e",
"reference-profile-P1":"0475d0ec6c486a63c7e8f62f11f35181da6b2576",
"reference-strict-product":"3ef2f6952ed1a4f852da31c0bef7e8d8679752a5",
"reference-strict-process":"4be2360aac0e6ea06211731364a14beec683310d",
"reference-fullview-product":"6c1eec41091a997f898cb448bfc7d4000c154307",
"reference-fullview-process":"2d5cbc55a7e33c9c890f29bc4e2ff0eb8bebdad5",
"reference-directsteps-product":"8e8b5126c69534c6259d37b2d3e88f75ef935aa0",
"reference-directsteps-process":"fb99fbdc6d2630efe0c1107b93401667a808466d",
"reference-shape-product":"3bd19e347051627242197f15fce712c9c9dd6b8f",
"reference-shape-combination":"43d56317f0bfbdfeec05efc583b306615ae54a30",
"reference-integer-product":"91e98074a334931648e9b7c8f58a3b5e8f93a642",
"reference-integer-process":"ec85a09210790cf09154168462e662e00c5ef64f",
"reference-date-product":"6891a5842302859a531cf82767c5a482417bc274",
"reference-date-process":"f79a29f596b2444cba542a906c91727869014886",
}
LOG=ROOT/"author-command-log.json"
records=[]
def digest(b): return hashlib.sha256(b).hexdigest()
def write_json(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def gz_bytes(p,b):
    with p.open("wb") as f:
        with gzip.GzipFile(filename="",mode="wb",fileobj=f,mtime=0,compresslevel=9) as z: z.write(b)
def command(argv,label,cwd=REPO,stdin=None):
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    t=time.monotonic()
    cp=subprocess.run(argv,cwd=cwd,input=stdin,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
    path=ROOT/"command-streams"/(str(len(records)+1).zfill(3)+"-"+label+".stdout.gz")
    path.parent.mkdir(parents=True,exist_ok=True)
    gz_bytes(path,cp.stdout)
    rec={"argv":argv,"cwd":str(cwd),"startedUTC":started,"durationSeconds":time.monotonic()-t,
         "exitCode":cp.returncode,"stdinBase64":base64.b64encode(stdin).decode() if stdin else None,
         "stdout":{"losslessGzipPath":str(path.relative_to(ROOT)),"uncompressedBytes":len(cp.stdout),"sha256":digest(cp.stdout)},
         "stderr":{"bytes":len(cp.stderr),"sha256":digest(cp.stderr),"base64":base64.b64encode(cp.stderr).decode()}}
    records.append(rec)
    write_json(LOG,{"format":"lossless-author-commands/1","records":records,
       "bootstrapBoundary":"Earlier read-only tool-session inventory and author bootstrap are not retrospectively split into fabricated stdout/stderr; current author subprocesses preserve exact streams."})
    if cp.returncode: raise RuntimeError("command failed; original streams retained: "+label)
    return cp.stdout
def listing(ref,label):
    raw=command(["git","ls-tree","-r","-z","--full-tree",ref],label)
    out=[]
    for item in raw.split(b"\0"):
        if not item: continue
        meta,path=item.split(b"\t",1)
        mode,kind,oid=meta.decode("ascii").split()
        p=path.decode("utf-8")
        if kind!="blob": raise RuntimeError("unexpected non-blob entry "+p)
        if p.endswith((".sqlite",".sqlite3",".db")) or pathlib.PurePosixPath(p).name==".env" or "/.mimosa/" in "/"+p:
            raise RuntimeError("unapproved sensitive/runtime path "+p)
        out.append({"path":p,"mode":mode,"gitBlob":oid})
    return out

def main():
    assert TREE==pathlib.Path("/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-retained-source-review-package")
    assert command(["git","branch","--show-current"],"packet-branch",TREE).decode().strip()=="docs/I05-retained-source-review-package"
    assert command(["git","rev-parse","HEAD"],"packet-base",TREE).decode().strip()==BASE
    command(["git","status","--short"],"packet-initial-status",TREE)
    snapshots={label:listing(ref,"tree-"+label) for label,ref in REFS.items()}
    # completion archive includes only process delta; product source remains an isolated main snapshot.
    main_map={r["path"]:r["gitBlob"] for r in snapshots["main-source-only"]}
    snapshots["main-completion-process"]=[r for r in snapshots["main-completion-process"] if main_map.get(r["path"])!=r["gitBlob"]]
    unique=sorted({r["gitBlob"] for rows in snapshots.values() for r in rows})
    # One exact Git batch stream; it is preserved gzip losslessly, not shown or executed.
    batch=command(["git","cat-file","--batch"],"all-frozen-blobs",stdin=("".join(oid+"\n" for oid in unique)).encode("ascii"))
    pos=0; blobs={}
    for requested in unique:
        end=batch.index(b"\n",pos); header=batch[pos:end].decode("ascii").split();pos=end+1
        oid,kind,size=header
        assert oid==requested and kind=="blob"
        n=int(size); value=batch[pos:pos+n];pos+=n
        assert batch[pos:pos+1]==b"\n";pos+=1
        blobs[oid]=value
    assert pos==len(batch)
    members=[]; first={}
    out=ROOT/"frozen-inputs.tar.gz"
    with out.open("wb") as file:
      with gzip.GzipFile(filename="",mode="wb",fileobj=file,mtime=0,compresslevel=9) as zipped:
       with tarfile.open(fileobj=zipped,mode="w",format=tarfile.PAX_FORMAT) as tar:
        for label in REFS:
         for row in sorted(snapshots[label],key=lambda r:r["path"]):
            value=blobs[row["gitBlob"]]
            name="snapshots/"+label+"/"+row["path"]
            info=tarfile.TarInfo(name);info.uid=info.gid=0;info.uname=info.gname="";info.mtime=0
            info.mode=int(row["mode"],8)&0o777
            hardlink=None
            if row["gitBlob"] in first:
                info.type=tarfile.LNKTYPE;info.linkname=first[row["gitBlob"]];info.size=0;hardlink=info.linkname
                tar.addfile(info)
            else:
                info.size=len(value);tar.addfile(info,io.BytesIO(value));first[row["gitBlob"]]=name
            members.append({"member":name,"sourceRef":REFS[label],"sourcePath":row["path"],"gitBlob":row["gitBlob"],
                            "mode":row["mode"],"bytes":len(value),"sha256":digest(value),"hardlinkTarget":hardlink})
    del batch,blobs
    write_json(ROOT/"input-manifest.json",{"format":"i05-fixed-complete-inputs/1","base":BASE,"candidate":MAIN,"process":PROCESS,
      "bundle":{"path":"frozen-inputs.tar.gz","bytes":out.stat().st_size,"sha256":digest(out.read_bytes()),
      "layout":"Full immutable snapshots in isolated namespaces; identical Git blobs are tar hardlinks. No source versions merged. main-completion-process holds only six docs-only delta files.",
      "extractionPolicy":"Read-only; do not edit extracted hardlinks or execute snapshots. Review exact source refs and compare versions separately."},
      "cohorts":[{"label":k,"ref":REFS[k],"members":len(v)} for k,v in snapshots.items()],
      "uniqueGitBlobs":len(unique),"members":members,"manifestSelf":"Excluded; Git process commit and later external receipt bind this file."})
    diff=command(["git","diff","--binary","--full-index",BASE,MAIN],"candidate-full-diff")
    write_json(ROOT/"candidate.patch.json",{"format":"lossless-full-index-diff/1","base":BASE,"head":MAIN,"argv":records[-1]["argv"],
        "bytes":len(diff),"sha256":digest(diff),"encoding":"base64","data":base64.b64encode(diff).decode("ascii"),
        "meaning":"Complete Git base-to-source-candidate diff, no path exclusions."})
    for label in ["reference-C4","reference-profile-P1","reference-strict-product","reference-fullview-product","reference-directsteps-product","reference-shape-product","reference-shape-combination","reference-integer-product","reference-date-product"]:
        diff=command(["git","diff","--binary","--full-index",BASE,REFS[label],"--","apps","packages","scripts","tests",".github","uv.lock","package.json","package-lock.json"],"diff-"+label)
        write_json(ROOT/"reference-diffs"/(label+".json"),{"base":BASE,"head":REFS[label],"argv":records[-1]["argv"],
          "scope":"Source/test/config/harness/licenses under explicit roots; complete snapshot and original docs are in bundle.",
          "bytes":len(diff),"sha256":digest(diff),"encoding":"base64","data":base64.b64encode(diff).decode("ascii")})
    guidance={}
    for name,path in {
        "AGENTS-current.md":REPO/"AGENTS.md",
        "developer-common-instructions-current.md":EXT/"developer-common-instructions.md",
        "desktop-operation-policy-20261022.md":EXT/"desktop-operation-policy-20261022.md",
        "external-review-permissions-current.md":EXT/"external-review-permissions.md",
        "I05-source-package-source-only-root-closure.md":EXT/"I05-source-package-source-only-root-closure.md",
        "I05-profile-fixed-computation-root-readback-closure.md":EXT/"I05-profile-fixed-computation-root-readback-closure.md",
        "I05-profile-strict-restore-root-closure.md":EXT/"I05-profile-strict-restore-root-closure.md",
        "I05-production-fullview-root-closure.md":EXT/"I05-production-fullview-root-closure.md",
        "I05-directsteps-root-closure-and-shape-combination.md":EXT/"I05-directsteps-root-closure-and-shape-combination.md",
        "I05-shape-combination-root-closure.md":EXT/"I05-shape-combination-root-closure.md",
        "I05-shacl-integer-entry-root-closure.md":EXT/"I05-shacl-integer-entry-root-closure.md",
        "I05-date-component-root-closure.md":EXT/"I05-date-component-root-closure.md",
    }.items():
        b=path.read_bytes(); target=ROOT/"guidance"/name;target.parent.mkdir(exist_ok=True);target.write_bytes(b)
        guidance[name]={"sourcePath":str(path),"bytes":len(b),"sha256":digest(b)}
    write_json(ROOT/"guidance-manifest.json",guidance)
    # Full every-member readback: extractfile resolves same-archive hardlinks.
    manifest=json.loads((ROOT/"input-manifest.json").read_text())
    expected={r["member"]:r for r in manifest["members"]};seen=set()
    with tarfile.open(out,"r:gz") as tar:
        for info in tar:
            assert info.name in expected and info.name not in seen
            seen.add(info.name);value=tar.extractfile(info).read();r=expected[info.name]
            assert len(value)==r["bytes"] and digest(value)==r["sha256"]
            assert (info.islnk() and info.linkname==r["hardlinkTarget"]) or (info.isfile() and r["hardlinkTarget"] is None)
    assert seen==set(expected)
    write_json(ROOT/"author-validation.json",{"format":"packet-structure-validation/1","wholeBundleReadback":True,
      "memberCount":len(seen),"uniqueGitBlobs":len(unique),"allMemberBytesSHA256AndRefBindings":True,
      "fullBinaryDiffEncoding":"base64 JSON; exact subprocess stdout retained gzip",
      "productImportedOrExecuted":False,"testsOrModelsOrNativeExecuted":False,"externalReviewsDispatched":0,
      "scope":"Packaging/Git/hash/tar/JSON structure only; no product or runtime verdict.",
      "archiveReason":"Explicit root-authorized review package preserves entire fixed source/process trees, original requirements, tests, first Fail reports and evidence. Version namespaces avoid mixing mutually exclusive shared files."})
    print(json.dumps({"members":len(seen),"uniqueBlobs":len(unique),"bundleBytes":out.stat().st_size,"bundleSHA256":digest(out.read_bytes()),"commands":len(records)},ensure_ascii=False))
if __name__=="__main__": main()

