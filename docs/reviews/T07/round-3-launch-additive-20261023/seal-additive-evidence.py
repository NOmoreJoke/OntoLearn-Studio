"""Package fixed role inputs and operator evidence; never dispatch a task."""

import hashlib
import json
from pathlib import Path
import tarfile


HERE = Path(__file__).resolve().parent


def pin(p):
    b = p.read_bytes()
    return {'path': str(p), 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}


def save(p, d):
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n')


assert not (HERE / 'additive-package-manifest.json').exists(), 'one fixed package only'
handoff = json.loads((HERE / 'operator-handoff.json').read_text())
assert handoff['state'] == 'INDEPENDENT_DELTA_PASS_READY_FOR_CONTROLLER_NO_GUI_START'
audit = HERE / 'additive-delta-independent-audit.md'
assert pin(audit) == handoff['independentDeltaAudit']['report']
for r in handoff['roles']:
    launch = Path(r['runtime']) / 'launch'
    for x in r['launchFiles']:
        assert pin(Path(x['path'])) == x
        owner_copy = HERE / f"{r['role']}-{Path(x['path']).name}"
        assert owner_copy.read_bytes() == Path(x['path']).read_bytes()
    m = json.loads((launch / 'own-launch-manifest.json').read_text())
    full = Path(m['fullInput']['path']).read_bytes()
    prefix = Path(m['addendum']['path']).read_bytes()
    old = Path(m['originalFullInput']['path']).read_bytes()
    assert full == prefix + old and full.endswith(old)
    assert m['originalRequiredItems'] == 236 and len(m['mandatorySupplementalFullEOF']) == 13
    for x in m['modelVisibleSetupFiles']:
        assert pin(Path(x['path'])) == x
    before = json.loads(Path(r['frozenVectorBefore']['path']).read_text())
    after = json.loads(Path(r['frozenVectorAfter']['path']).read_text())
    assert before['files'] == after['files']
    assert before['vectorSHA256'] == after['vectorSHA256'] == r['frozenVectorSHA256']
    for x in after['files']:
        actual = pin(Path(x['path']))
        assert actual['bytes'] == x['bytes'] and actual['sha256'] == x['sha256']
archive = HERE.with_suffix('.tar.gz')
assert not archive.exists()
files = [p for p in sorted(HERE.iterdir()) if p.is_file()]
members = []
with tarfile.open(archive, 'w:gz') as out:
    for p in files:
        assert not p.is_symlink()
        name = HERE.name + '/' + p.name
        members.append({'member': name, **pin(p)})
        out.add(p, arcname=name, recursive=False)
with tarfile.open(archive) as inp:
    actual = inp.getmembers()
    assert len(actual) == len(members)
    expected = {x['member']: x for x in members}
    for m in actual:
        assert m.isfile() and m.name in expected
        b = inp.extractfile(m).read()
        x = expected[m.name]
        assert len(b) == x['bytes'] and hashlib.sha256(b).hexdigest() == x['sha256']
manifest = {'state': handoff['state'], 'operatorOnly': True,
            'modelAttachmentPolicy': 'Each model receives only its own complete-launch-input and own launch/manifest/cover/ticket paths; never this aggregate archive, handoff or independent audit.',
            'product': 'f9a1157c2fff06c8bef17fa1ec44d8eb1ebacad3',
            'reviewHead': '7fd17f93ebb4b68bac69faec15cb657e60c90729',
            'priorSetupEvidenceCommit': '8c8478997ef3e33b627bec7fc55ca038cdf7a610',
            'operatorHandoff': pin(HERE / 'operator-handoff.json'),
            'independentDeltaAudit': handoff['independentDeltaAudit'],
            'roles': handoff['roles'], 'archive': pin(archive), 'archiveRegularMembers': members,
            'everyArchiveMemberVerifiedExact': True,
            'newCompleteInputsPrefixPlusExactOldSuffixVerified': True,
            'allOldSourceRequiredInputAndSetupPinsReverified': True,
            'noOriginalInputOrHistoricalWhitespaceChanged': True,
            'currentInstalledAndLimitedOrdinaryPermissionExplicit': True,
            'ordinaryCommandsSelected': [], 'ordinaryCommandsExecuted': 0, 'setupCommandsExecuted': 0,
            'noNewMandatoryValidationMatrix': True, 'oldRejectedVerificationNotLifted': True,
            'productRuns': 0, 'newExternalTasks': 0, 'formalSends': 0, 'GUIUsed': False,
            'GUIReleased': True, 'externalGUIStartAuthorized': False,
            'processGate': 'PROCESS_FAIL / Pair 0 retained', 'originalMP2P3UnchangedPending': True,
            'originalGoalUnchanged': True, 'selfExcludedToAvoidHashCycle': True}
save(HERE / 'additive-package-manifest.json', manifest)
print(json.dumps({'manifest': pin(HERE / 'additive-package-manifest.json'), 'archive': pin(archive), 'members': len(members)}, ensure_ascii=False))
