"""Archive already-completed actual observations; no product imports or evaluation."""

import hashlib
import json
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

tag, actual_path, candidate = sys.argv[1:]
actual = Path(actual_path)
out = Path(__file__).parent
archive = out / (tag + "-actuals.zip")
assert not archive.exists()
rows, members = [], []
families = defaultdict(Counter)
operations = Counter()
comparator_calls = Counter()
reaching_comparator = Counter()
main_reaching_comparator = Counter()
counter_coverage = Counter()
pure_reasons_not_executed = []
with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as bundle:
    for path in sorted(actual.rglob("*")):
        if not path.is_file():
            continue
        raw = path.read_bytes()
        member = str(path.relative_to(actual))
        bundle.writestr(member, raw)
        members.append(
            {"member": member, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
        )
        if path.name != "observation.json":
            continue
        record = json.loads(raw)
        families[record["family"]][record["assertion"]] += 1
        main = record["actual"]["main"]
        for label, value in record["actual"].items():
            operations[value["status"] + ":" + value.get("stage", "restored")] += 1
            counters = value.get("realComparatorCalls")
            counter_coverage["observed" if counters is not None else "unobserved"] += 1
            if counters is not None:
                for phase, count in counters.items():
                    comparator_calls[phase] += count
                    reaching_comparator[phase] += int(count > 0)
                    if label == "main":
                        main_reaching_comparator[phase] += int(count > 0)
        if record.get("pureReasonExecutedByThisEntry") is False:
            pure_reasons_not_executed.append({"family": record["family"], "id": record["id"]})
        rows.append(
            {
                "family": record["family"],
                "id": record["id"],
                "fixtureIndex": record["fixtureIndex"],
                "assertion": record["assertion"],
                "sourceSha256": record["sourceSha256"],
                "input": record["input"],
                "expected": record.get("expected"),
                "admittedEntryExpected": record.get("admittedEntryExpected"),
                "pureReasonExecutedByThisEntry": record.get("pureReasonExecutedByThisEntry"),
                "actual": {
                    name: {
                        k: v
                        for k, v in value.items()
                        if k
                        in {
                            "label",
                            "status",
                            "stage",
                            "reason",
                            "diagnostic",
                            "exceptionType",
                            "publicError",
                            "comparison",
                            "accepted",
                            "originalMatchCount",
                            "producedResultReturned",
                            "restoredResultReturned",
                            "originalLimitValues",
                            "originalUsageValues",
                            "retentionMeaning",
                            "realComparatorCalls",
                        }
                    }
                    for name, value in record["actual"].items()
                },
                "completeObservationMember": member,
                "completeObservationSha256": hashlib.sha256(raw).hexdigest(),
            }
        )
assert len(rows) == 1331
assert len({(r["family"], r["id"]) for r in rows}) == 1331
summary = {
    "candidate": candidate,
    "actualDirectory": str(actual.resolve()),
    "caseObservations": len(rows),
    "families": {k: dict(v) for k, v in families.items()},
    "operations": dict(operations),
    "comparatorCallCounters": dict(comparator_calls),
    "operationsReachingComparator": dict(reaching_comparator),
    "mainOperationsReachingComparator": dict(main_reaching_comparator),
    "callCounterCoverage": dict(counter_coverage),
    "pureReasonsNotExecutedByThisEntry": pure_reasons_not_executed,
    "archive": archive.name,
    "archiveBytes": archive.stat().st_size,
    "archiveSha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
    "archiveMembers": len(members),
    "uncompressedBytes": sum(r["bytes"] for r in members),
    "scope": "Real component observations only; no formal T01 Job/worker/Store/selected claim",
    "retention": "C/R counters and logical live/retained values are not physical memory/GC proof",
}
(out / (tag + "-actual-index.json")).write_text(
    json.dumps({"summary": summary, "cases": rows}, ensure_ascii=False, indent=2) + "\n"
)
(out / (tag + "-archive-members.json")).write_text(
    json.dumps({"summary": summary, "members": members}, ensure_ascii=False, indent=2) + "\n"
)
print(json.dumps(summary, ensure_ascii=False, indent=2))
