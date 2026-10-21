from pathlib import Path
import hashlib
import json
import subprocess

PRIMARY = Path('/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-semantic-validation')
CONTROL = PRIMARY.parents[1] / 'iteration-control/2026-10-21-weekly-release'
OUT = Path(__file__).resolve().parent


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def git(*args):
    return subprocess.check_output(['git', *args], cwd=PRIMARY)


candidate_path = PRIMARY / 'docs/reviews/I05/candidate-4.json'
candidate = json.loads(candidate_path.read_bytes())
base, head = candidate['base'], candidate['head']
tracked = set(git('ls-tree', '-rz', '--name-only', head).decode().split('\0')) - {'', 'AGENTS.md'}
changed = set(git('diff', '--name-only', '-z', base, head).decode().split('\0')) - {''}
assert tracked == set(candidate['fullTrackedFilesExceptProtectedGuidance'])
assert changed == set(candidate['files'])
proc = subprocess.Popen(['git', 'cat-file', '--batch'], cwd=PRIMARY,
                        stdin=subprocess.PIPE, stdout=subprocess.PIPE)


def blob(ref, path):
    proc.stdin.write((ref + ':' + path + '\n').encode())
    proc.stdin.flush()
    header = proc.stdout.readline().split()
    assert header[1] == b'blob', (ref, path, header)
    raw = proc.stdout.read(int(header[2]))
    assert proc.stdout.read(1) == b'\n'
    return raw


checks = {}
for group in ['files', 'fullTrackedFilesExceptProtectedGuidance', 'executionInputs']:
    for path, expected in candidate[group].items():
        raw = blob(head, path)
        assert sha(raw) == expected, (group, path)
        assert (PRIMARY / path).read_bytes() == raw, ('workfile', group, path)
    checks[group] = len(candidate[group])
for path in candidate['executionInputs']:
    assert blob(head, path) == blob(candidate['verifiedProductAndTestsHead'], path), path
proc.stdin.close()
assert proc.wait() == 0

round4 = PRIMARY / 'docs/reviews/I05/round-4'
inputs = json.loads((round4 / 'input-manifest.json').read_bytes())
for path, expected in inputs['inputFiles'].items():
    raw = (PRIMARY / path).read_bytes()
    assert len(raw) == expected['bytes'] and sha(raw) == expected['sha256'], path
suffix = (round4 / 'full-review-input.md').read_bytes()[-34007:]
assert suffix == (PRIMARY / 'docs/reviews/I05/round-3/full-review-input.md').read_bytes()[-34007:]
assert sha(suffix) == inputs['originalRequirementsSuffixSha256']
originals = {}
for name in ['I05-launch-prompt.md', 'I05-resume-integrated-I04-20261021.md', 'goal-objective.md']:
    raw = (PRIMARY / 'docs/reviews/I05/inputs-c1' / name).read_bytes()
    assert suffix.count(raw) == 1, name
    originals[name] = {'bytes': len(raw), 'sha256': sha(raw)}

snapshots = json.loads((PRIMARY / 'docs/reviews/I05/inputs-c4/manifest.json').read_bytes())
for entry in snapshots['snapshots']:
    raw = (PRIMARY / 'docs/reviews/I05/inputs-c4' / entry['snapshot']).read_bytes()
    assert raw == Path(entry['source']).read_bytes(), entry['snapshot']
    assert len(raw) == entry['bytes'] and sha(raw) == entry['sha256']

evidence = PRIMARY / 'docs/reviews/I05/evidence/integrated-c4'
manifest_raw = (evidence / 'manifest.json').read_bytes()
manifest = json.loads(manifest_raw)
assert sha(manifest_raw) == candidate['acceptanceEvidenceManifestSha256']
assert manifest['memberCount'] == len(manifest['members']) == candidate['rawEvidenceMemberCount'] == 1254
assert manifest['productHead'] == candidate['verifiedProductHead']
assert manifest['productAndTestsHead'] == candidate['verifiedProductAndTestsHead']
assert sha((evidence / manifest['archive']).read_bytes()) == manifest['archiveSha256'] == candidate['rawEvidenceArchiveSha256']
audit = evidence / 'seal-audit'
audit_index = json.loads((audit / 'audit-manifest.json').read_bytes())
for entry in audit_index['files']:
    raw = (audit / entry['path']).read_bytes()
    assert len(raw) == entry['bytes'] and sha(raw) == entry['sha256'], entry['path']
assert (audit / 'audited-evidence-manifest.json').read_bytes() == manifest_raw
binding = json.loads((audit / 'audit-bindings.json').read_bytes())
assert binding['evidenceManifestSha256'] == sha(manifest_raw)
assert binding['archiveSha256'] == manifest['archiveSha256']
assert binding['productHead'] == candidate['verifiedProductHead']
assert binding['productAndTestsHead'] == candidate['verifiedProductAndTestsHead']
assert sha((audit / 'audit-manifest.json').read_bytes()) == json.loads((audit / 'copy-receipt.json').read_bytes())['originalAuditManifestSha256']

summary = {
    'scope': 'Read-only frozen inventory, dispatch inputs and existing independent audit binding; no product tests or 1254-member audit rerun',
    'base': base, 'head': head,
    'actualCheckoutHead': git('rev-parse', 'HEAD').decode().strip(),
    'actualBranch': git('branch', '--show-current').decode().strip(),
    'actualStatus': git('status', '--short').decode(),
    'postFreezeProcessDelta': git('diff', '--name-status', head, 'HEAD').decode(),
    'candidateSha256': sha(candidate_path.read_bytes()),
    'fullInputSha256': sha((round4 / 'full-review-input.md').read_bytes()),
    'verifiedInventories': checks,
    'executionBytesEqual40cAndFrozenAndWorktree': True,
    'suffixBytes': len(suffix), 'suffixSha256': sha(suffix), 'suffixEqualsRound3': True,
    'originalFullFilesPresentExactlyOnce': originals,
    'guidanceSnapshotsEqualCurrentSources': snapshots['snapshots'],
    'evidenceManifestSha256': sha(manifest_raw),
    'archiveCompressedBytesHashedOnly': manifest['archiveBytes'],
    'archiveSha256': manifest['archiveSha256'],
    'evidenceMemberCountIndexedOnly': manifest['memberCount'],
    'auditReportSha256': sha((audit / 'report.md').read_bytes()),
    'auditReportBytes': len((audit / 'report.md').read_bytes()),
    'auditIndexedFilesVerified': len(audit_index['files']),
    'actualTaskCountRecorded': candidate['actualTaskCount'],
    'actualObservedState': json.loads((round4 / 'observed-state.json').read_bytes()),
}
(OUT / 'readback.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({key: summary[key] for key in ['base', 'head', 'actualCheckoutHead', 'verifiedInventories', 'suffixBytes', 'suffixSha256', 'auditIndexedFilesVerified', 'actualTaskCountRecorded']}, ensure_ascii=False, indent=2))
