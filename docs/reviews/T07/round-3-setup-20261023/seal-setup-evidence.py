"""Seal existing setup records after the independent report; execute no setup."""

import hashlib
import json
from pathlib import Path
import tarfile
from datetime import datetime, timezone


HERE = Path(__file__).resolve().parent


def pin(p):
    b = p.read_bytes()
    return {'path': str(p), 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}


def save(p, d):
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n')


assert not (HERE / 'setup-manifest.json').exists(), 'already sealed; no silent replacement'
audit = HERE / 'actual-setup-independent-audit.md'
assert audit.is_file(), 'independent post-setup report required'
execution = json.loads((HERE / 'execution-summary.json').read_text())
ticket = json.loads((HERE / 'setup-authorization.json').read_text())
assert all(r['status'] == 'SETUP_COMMANDS_EXIT0' and len(r['commands']) == 5 for r in execution['roles'])
audit_pin = pin(audit)
archive = HERE.with_suffix('.raw.tar.gz')
assert not archive.exists()
members, role_rows = [], []
with tarfile.open(archive, 'w:gz') as out:
    for role in execution['roles']:
        root, runtime = Path(role['root']), Path(role['runtime'])
        setup = runtime / 'setup'
        own_audit = {'role': role['role'], 'scope': 'post-setup static evidence and isolation only',
                     'result': 'PASS_STATIC_ACTUAL_SETUP_ONLY', 'aggregateAuditSHA256': audit_pin['sha256'],
                     'aggregateAuditBytes': audit_pin['bytes'], 'peerMaterialsIncluded': False,
                     'productValidationRuns': 0, 'oldRejectedVerificationNotLifted': True,
                     'externalStartAuthorized': False, 'processGate': 'PROCESS_FAIL / Pair 0 retained'}
        own_path = setup / 'role-setup-audit-receipt.json'
        assert not own_path.exists()
        save(own_path, own_audit)
        for p in sorted(setup.iterdir()):
            assert p.is_file() and not p.is_symlink()
            name = f"{role['role']}/setup/{p.name}"
            item = pin(p)
            members.append({'member': name, **item})
            out.add(p, arcname=name, recursive=False)
        im = json.loads((root / 'docs/reviews/T07/round-3-input/input-manifest.json').read_text())
        assert pin(Path(im['fullInputPath']))['sha256'] == im['fullInputSHA256']
        for c in role['commands']:
            assert c['realChildIntegerExit'] == 0 and c['operationalStop'] is None
            for stream in ['stdout', 'stderr']:
                assert pin(Path(c[stream]['path'])) == c[stream]
        role_rows.append({'role': role['role'], 'root': str(root), 'runtime': str(runtime),
                          'commands': role['commands'], 'frozenVectorSHA256': role['sourceVectorSHA256'],
                          'sourceFilesEachRootAndScratch': 1020, 'requiredInputItems': 236,
                          'fullInput': {'path': im['fullInputPath'], 'bytes': im['fullInputBytes'], 'sha256': im['fullInputSHA256']},
                          'roleInstalledFacts': pin(setup / 'role-installed-facts.json'),
                          'rolePostSetupAuditReceipt': pin(own_path),
                          'scratchDependenciesInstalled': False})
with tarfile.open(archive, 'r:gz') as inp:
    actual = inp.getmembers()
    assert len(actual) == len(members)
    index = {x['member']: x for x in members}
    for m in actual:
        assert m.isfile() and m.name in index
        b = inp.extractfile(m).read()
        x = index[m.name]
        assert len(b) == x['bytes'] and hashlib.sha256(b).hexdigest() == x['sha256']
base = pin(Path(ticket['pinnedExistingPython']['path']))
assert base['sha256'] == ticket['pinnedExistingPython']['sha256']
manifest = {'state': 'ACTUAL_SETUP_EXIT0_STATIC_AUDIT_PASS_NO_EXTERNAL_START',
            'sealedUTC': datetime.now(timezone.utc).isoformat(),
            'product': ticket['product'], 'reviewHEAD': ticket['reviewHEAD'], 'preparationCommit': ticket['preparationCommit'],
            'authorization': pin(HERE / 'setup-authorization.json'), 'independentActualSetupAudit': audit_pin,
            'independentActualSetupAuditsCompleted': 1, 'fullAuditReadByOwner': True,
            'roles': role_rows, 'rawArchive': pin(archive), 'rawArchiveRegularMembers': members,
            'everyArchiveMemberVerifiedExact': True,
            'ownerFiles': [pin(p) for p in sorted(HERE.iterdir()) if p.is_file()],
            'selfExcludedToAvoidHashCycle': True, 'basePythonReadOnlyPinAfter': base,
            'dependencySetupExecuted': True, 'sourceTestLocksAndHistoricalInputsUnchanged': True,
            'historicalFullInputWhitespaceWarningsPreserved': 16,
            'staticMetadataFirstErrorPreserved': pin(HERE / 'static-metadata-first-error.json'),
            'crossRoleRegularDependencyInodeIntersection': 0,
            'crossRoleMutableCacheHomeTmpXDGRegularInodeIntersection': 0,
            'oldRejectedVerificationNotLifted': True, 'productValidationRuns': 0,
            'externalTasks': 0, 'formalSends': 0, 'GUIReleased': True, 'externalStartAuthorized': False,
            'engineeringPassClaimed': False, 'processGate': 'PROCESS_FAIL / Pair 0 retained',
            'originalMP2P3StillPending': True, 'originalGoalUnchanged': True,
            'scopeLimit': 'Only exact dependency setup and static metadata/isolation accepted; no product execution, validation, packaging, GUI, reviewer task, or hold release.'}
save(HERE / 'setup-manifest.json', manifest)
print(json.dumps({'manifest': pin(HERE / 'setup-manifest.json'), 'archive': pin(archive), 'members': len(members), 'audit': audit_pin}, ensure_ascii=False))
