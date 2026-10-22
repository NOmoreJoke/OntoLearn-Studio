# coding: utf-8
"""C5 controller-authorized image preparation only. Copied bounded C4 setup utilities; no checker/helper/product execution or active receipt issue."""
import argparse,hashlib,json,os,selectors,signal,stat,subprocess,time,datetime
from pathlib import Path
if not __debug__:raise RuntimeError('OPTIMIZED_STARTUP_FORBIDDEN')
ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/'owner-evidence'
IMAGES=ROOT/'images'
SCRATCH=ROOT/'image-creation-scratch'
IMAGE_CAP=268435456
SCRATCH_CAP=134217728
PREPARED_CAP=67108864
TRUST_PATHS=['AGENTS.md','prompt.md','review-scope.md','check-inputs.py','run-tool.py','tooling/verify-browser-c4.py','tooling/owned-browser-runner.mjs','coverage-required.json','candidate.json','config/authority.json','config/runtime-config.json','config/resources.json','config/native-resources.json']
def checked_path(path):
    path = Path(path)
    assert path.is_absolute() and str(path) == os.path.normpath(str(path))
    for part in [*reversed(path.parents), path]:
        if os.path.lexists(part):
            assert not stat.S_ISLNK(part.lstat().st_mode), 'SYMLINK_PATH ' + str(part)
    return path


def identity(path):
    path = checked_path(path)
    before = path.lstat()
    assert stat.S_ISREG(before.st_mode) and before.st_nlink == 1
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, 'rb') as handle:
        opened = os.fstat(handle.fileno())
        assert (opened.st_dev, opened.st_ino) == (before.st_dev, before.st_ino)
        digest = hashlib.sha256()
        size = 0
        while True:
            block = handle.read(65536)
            if not block:
                break
            digest.update(block)
            size += len(block)
        after = os.fstat(handle.fileno())
    assert (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) == (
        after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns)
    assert size == before.st_size
    return {'bytes': size, 'sha256': digest.hexdigest(), 'mode': oct(stat.S_IMODE(before.st_mode)),
            'dev': before.st_dev, 'ino': before.st_ino, 'nlink': before.st_nlink,
            'reportedAllocatedBytes': before.st_blocks * 512}


def write_new(path, value):
    path = checked_path(path)
    data = (json.dumps(value, indent=2, ensure_ascii=True) + '\n').encode() if isinstance(value, dict) else value
    assert len(data) < 1048576, 'OWN_SINGLE_RECEIPT_LIMIT'
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
    with os.fdopen(fd, 'wb') as handle:
        handle.write(data)
    return identity(path)


def stat_tree(root):
    """Stat only; never follow/read/hash unknown bodies, including scratch/metadata."""
    root = checked_path(root)
    records = []
    seen_dirs = set()
    root_dev = root.lstat().st_dev

    def visit(directory):
        before = directory.lstat()
        key = (before.st_dev, before.st_ino)
        assert key not in seen_dirs and before.st_dev == root_dev
        seen_dirs.add(key)
        for child in sorted(directory.iterdir()):
            s = child.lstat()
            assert len(records) < 6000, 'FINITE_TREE_LIMIT'
            row = {'path': child.relative_to(root).as_posix(), 'bytes': s.st_size,
                   'mode': oct(s.st_mode), 'dev': s.st_dev, 'ino': s.st_ino,
                   'reportedAllocatedBytes': s.st_blocks * 512}
            assert not stat.S_ISLNK(s.st_mode) and s.st_dev == root_dev, 'LINK_OR_NESTED_DEVICE'
            if stat.S_ISDIR(s.st_mode):
                row['type'] = 'directory'
                records.append(row)
                visit(child)
            else:
                assert stat.S_ISREG(s.st_mode), 'NON_ORDINARY_PATH'
                row['type'] = 'file'
                records.append(row)
    visit(root)
    return records


def validate_input(root, expected_sha):
    root = checked_path(root)
    manifest_path = root / 'input-manifest.json'
    manifest_identity = identity(manifest_path)
    assert manifest_identity['sha256'] == expected_sha
    manifest = json.loads(manifest_path.read_text())
    assert manifest['selfFile'] == 'input-manifest.json' and manifest['exclusions'] == []
    expected = {}
    for row in manifest['files']:
        rel = Path(row['path'])
        assert not rel.is_absolute() and '..' not in rel.parts and rel.as_posix() == row['path']
        assert row['path'] not in expected and row['path'] != 'input-manifest.json'
        expected[row['path']] = row
    observed = stat_tree(root)
    files = {x['path'] for x in observed if x['type'] == 'file'}
    dirs = {x['path'] for x in observed if x['type'] == 'directory'}
    assert files == set(expected) | {'input-manifest.json'}, 'EXACT_FILE_SET'
    assert dirs == set(manifest['directories']), 'EXACT_DIRECTORY_SET'
    assert len(files) == len(expected) + 1 and len(dirs) == len(manifest['directories'])
    identities = {'input-manifest.json': manifest_identity}
    for rel, row in sorted(expected.items()):
        item = identity(root / rel)
        assert all(item[k] == row[k] for k in ['bytes', 'sha256', 'mode']), 'ROW_MISMATCH ' + rel
        identities[rel] = item
    assert len({(x['dev'], x['ino']) for x in identities.values()}) == len(files)
    observed_after = stat_tree(root)
    assert observed == observed_after, 'INPUT_STAT_CHANGED_DURING_READBACK'
    summary = {'inputRootObserved': str(root), 'fixedFilesIncludingManifest': len(files),
               'exactDirectories': len(dirs), 'inputManifestIdentity': manifest_identity,
               'logicalBytes': sum(x['bytes'] for x in identities.values()),
               'fileReportedAllocatedBytes': sum(x['reportedAllocatedBytes'] for x in identities.values()),
               'fullTrustChain': {k: identities[k] for k in TRUST_PATHS},
               'allDeclaredRowsBytesHashModeMatched': True, 'unknownBodiesReadOrHashed': False}
    return summary, identities


def monitor_space(enforce=True):
    image_bytes = 0
    scratch_bytes = 0
    unknown = []
    expected = {'stage-c5-zcode.dmg', 'stage-c5-minimax.dmg'}
    for item in stat_tree(IMAGES):
        if item['type'] != 'file':
            continue
        if item['path'] in expected:
            image_bytes += item['bytes']
        else:
            scratch_bytes += item['bytes']
            unknown.append(item)
    scratch = stat_tree(SCRATCH)
    scratch_bytes += sum(x['bytes'] for x in scratch if x['type'] == 'file')
    if enforce:
        assert image_bytes <= IMAGE_CAP, 'BOTH_IMAGES_LOGICAL_CAP'
        assert scratch_bytes <= SCRATCH_CAP, 'OBSERVED_OWN_SCRATCH_LOGICAL_CAP'
    return {'bothImageLogicalBytes': image_bytes, 'observedOwnScratchLogicalBytes': scratch_bytes,
            'imageDirectoryUnknownStatOnly': unknown, 'scratchStatOnly': scratch}


class SetupCommandFailure(RuntimeError):
    def __init__(self, receipt):
        self.receipt = receipt
        super().__init__(receipt['firstFailure'] or 'SETUP_COMMAND_FAILED')


def run_setup(name, argv, target, execution_seconds=180, drain_seconds=1):
    start = time.time()
    deadline = time.monotonic() + execution_seconds
    env = dict(os.environ)
    env['TMPDIR'] = str(SCRATCH)
    process = None
    selector = None
    buffers = {'stdout': bytearray(), 'stderr': bytearray()}
    failures = []
    observations = 0
    signal_attempted = False
    forced_pipe_close = False
    drain_deadline = None

    def fail(reason):
        if reason not in failures:
            failures.append(reason)

    def signal_owned_group():
        nonlocal signal_attempted
        if process is None or signal_attempted:
            return
        signal_attempted = True
        try:
            # This session/group was created by this Popen, even if its leader exited.
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        except Exception as error:
            fail('OWN_GROUP_SIGNAL: ' + repr(error))

    try:
        process = subprocess.Popen(argv, cwd=ROOT, env=env, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, start_new_session=True)
        selector = selectors.DefaultSelector()
        selector.register(process.stdout, selectors.EVENT_READ, 'stdout')
        selector.register(process.stderr, selectors.EVENT_READ, 'stderr')
        while selector.get_map() or process.poll() is None:
            now = time.monotonic()
            try:
                monitor_space()
                observations += 1
            except Exception as error:
                fail('SPACE: ' + repr(error))
            if now >= deadline:
                fail('SETUP_EXECUTION_TIMEOUT')
            if failures:
                signal_owned_group()
                if drain_deadline is None:
                    drain_deadline = now + drain_seconds
                if now >= drain_deadline:
                    forced_pipe_close = True
                    break
            timeout = min(0.2, max(0, (drain_deadline or deadline) - time.monotonic()))
            for key, _ in selector.select(timeout):
                chunk = os.read(key.fileobj.fileno(), 8192)
                if not chunk:
                    selector.unregister(key.fileobj)
                    key.fileobj.close()
                    continue
                buffer = buffers[key.data]
                remaining = 65536 - len(buffer)
                buffer.extend(chunk[:max(0, remaining)])
                if len(chunk) > remaining:
                    fail('SETUP_LOG_CAP')
    except Exception as error:
        fail(('POPEN: ' if process is None else 'SETUP_OR_CAPTURE: ') + repr(error))
    finally:
        if failures:
            signal_owned_group()
        if process is not None and process.poll() is None:
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                fail('OWN_LEADER_WAIT_TIMEOUT')
                signal_owned_group()
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    fail('OWN_LEADER_STILL_NOT_REAPED')
        if process is not None:
            for pipe in [process.stdout, process.stderr]:
                try:
                    if pipe is not None:
                        pipe.close()
                except Exception as error:
                    fail('PIPE_CLOSE: ' + repr(error))
        if selector is not None:
            try:
                selector.close()
            except Exception as error:
                fail('SELECTOR_CLOSE: ' + repr(error))
    exit_code = process.poll() if process is not None else None
    if process is not None and exit_code != 0:
        fail('CHILD_NONZERO_OR_UNREAPED_EXIT: ' + str(exit_code))
    try:
        post_space = monitor_space(enforce=False)
        if post_space['bothImageLogicalBytes'] > IMAGE_CAP:
            fail('POST_BOTH_IMAGES_LOGICAL_CAP')
        if post_space['observedOwnScratchLogicalBytes'] > SCRATCH_CAP:
            fail('POST_OBSERVED_OWN_SCRATCH_LOGICAL_CAP')
    except Exception as error:
        post_space = {'observationError': repr(error)}
        fail('POST_SPACE: ' + repr(error))
    log_writes = {}
    for channel, data in buffers.items():
        try:
            log_writes[channel] = write_new(target / (name + '.' + channel + '.log'), bytes(data))
        except Exception as error:
            log_writes[channel] = {'writeError': repr(error), 'capturedBytes': len(data)}
            fail('LOG_WRITE_' + channel + ': ' + repr(error))
    receipt = {'argv': argv, 'cwd': str(ROOT), 'processStarted': process is not None,
               'processId': process.pid if process is not None else None,
               'environmentProjection': {'TMPDIR': str(SCRATCH)},
               'startedUnix': start, 'finishedUnix': time.time(), 'startedAtUTC': datetime.datetime.fromtimestamp(start,datetime.timezone.utc).isoformat(), 'finishedAtUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'exitCode': exit_code,
               'firstFailure': failures[0] if failures else None, 'failuresObserved': list(failures),
               'finiteSpaceObservations': observations, 'postSpace': post_space, 'logWrites': log_writes,
               'ownGroupSignalAttempted': signal_attempted, 'forcedPipeClose': forced_pipe_close,
               'executionTimeoutSeconds': execution_seconds, 'postFailureDrainSeconds': drain_seconds,
               'leaderWaitSecondsPerAttempt': 2, 'notWholeDescendantsOrOSManagedScratchProof': True}
    try:
        write_new(target / (name + '.receipt.json'), receipt)
    except Exception as error:
        fail('COMMAND_RECEIPT_WRITE: ' + repr(error))
        receipt.update(firstFailure=failures[0], failuresObserved=list(failures),
                       receiptWriteError=repr(error))
    if failures:
        # Caller preserves this structured argv/exit even if a log/receipt write failed.
        raise SetupCommandFailure(receipt)
    return receipt, bytes(buffers['stdout']).decode('utf-8', errors='replace')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--preparation-sha256',required=True);args=parser.parse_args()
    prep_path=ROOT/'author-evidence/preparation-result.json';prep_id=identity(prep_path);assert prep_id['sha256']==args.preparation_sha256
    prep=json.loads(prep_path.read_text());assert prep['status']=='C5_ORDINARY_PREPARATION_ONLY' and prep['commandGrants']=={} and prep['actualGrants']=='UNKNOWN_WAIT_CONTROLLER'
    assert set(prep['parties'])=={'zcode','minimax'}
    for party,spec in prep['parties'].items():
        assert spec['preparedInputRoot']==str(ROOT/'prepared'/party/'volume-root/input')
        assert spec['taskRoot']==str(ROOT/'runtime'/party)
        assert spec['volumeRoot']=='/Volumes/OntoLearn-Stage-C5-'+party+'-20261023'
        assert spec['inputRoot']==str(Path(spec['volumeRoot'])/'input')
        assert spec['imagePath']==str(IMAGES/('stage-c5-'+party+'.dmg'))
        assert not os.path.lexists(checked_path(spec['imagePath'])) and not os.path.lexists(checked_path(spec['volumeRoot']))
        assert [p.name for p in (ROOT/'prepared'/party/'volume-root').iterdir()]==['input']
    for directory in [EVIDENCE,IMAGES,SCRATCH]:
        checked_path(directory);assert not directory.exists();directory.mkdir()
    result={'status':'INCOMPLETE','preparedIdentity':prep_id,'startedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'parties':{},'commandGrants':{},'actualGrants':'UNKNOWN_WAIT_CONTROLLER','rootReceiptIssuedByAuthor':False,'checkerOrHelperOrProductExecuted':False,'GUIOrModelTasksCreated':False,'external1557ResourceBodiesRead':False}
    try:
        sources={}
        for party,spec in prep['parties'].items():
            target=EVIDENCE/party;target.mkdir()
            summary,ids=validate_input(Path(spec['preparedInputRoot']),spec['manifestIdentity']['sha256'])
            assert summary['fixedFilesIncludingManifest']==spec['fixedFilesIncludingManifest']
            write_new(target/'source-pre-image-readback.json',summary);sources[party]=(summary,ids)
        assert sum(x[0]['logicalBytes'] for x in sources.values())<=PREPARED_CAP
        for party in ['zcode','minimax']:
            spec=prep['parties'][party];target=EVIDENCE/party;image=Path(spec['imagePath']);volume=Path(spec['volumeRoot'])
            partial={'status':'CREATE_ATTEMPTING','imagePath':str(image),'volumeRoot':str(volume),'createAttempted':True,'attachAttempted':False};result['parties'][party]=partial
            create,_=run_setup('create',['/usr/bin/hdiutil','create','-srcfolder',str(ROOT/'prepared'/party/'volume-root'),'-volname',volume.name,'-format','UDRO','-o',str(image)],target)
            image_id=identity(image);partial.update(status='CREATED_NOT_ATTACHED',image=image_id,create=create)
            assert not os.path.lexists(volume);partial.update(status='ATTACH_ATTEMPTING',attachAttempted=True)
            attach,out=run_setup('attach',['/usr/bin/hdiutil','attach','-readonly','-nobrowse','-mountpoint',str(volume),str(image)],target)
            rows=[line.split() for line in out.splitlines() if line.strip().startswith('/dev/disk')];own=[r for r in rows if r[-1]==str(volume)]
            assert len(own)==1
            summary,ids=validate_input(volume/'input',spec['manifestIdentity']['sha256'])
            write_new(target/'mounted-input-readback.json',summary)
            after,aids=validate_input(Path(spec['preparedInputRoot']),spec['manifestIdentity']['sha256']);assert aids==sources[party][1]
            for rel,ident in ids.items():assert all(ident[k]==sources[party][1][rel][k] for k in ['bytes','sha256','mode'])
            vs=volume.lstat();ins=(volume/'input').lstat()
            assert os.statvfs(volume).f_flag & os.ST_RDONLY and os.statvfs(volume/'input').f_flag & os.ST_RDONLY
            assert vs.st_dev==ins.st_dev and vs.st_dev!=Path(spec['taskRoot']).stat().st_dev
            assert identity(image)==image_id
            infra=[]
            for child in sorted(volume.iterdir()):
                s=child.lstat();infra.append({'path':child.name,'mode':oct(s.st_mode),'bytes':s.st_size,'dev':s.st_dev,'ino':s.st_ino,'bodyReadOrHashed':False})
            observation={'kind':'owner-observed-hdiutil-readonly-image','observedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'imagePath':str(image),'imageIdentity':image_id,'mountPoint':str(volume),'device':own[0][0],'readonly':True,'shadow':False,'overlay':False,'create':create,'attach':attach,'attachDeviceRows':rows,'volumeDev':vs.st_dev,'volumeIno':vs.st_ino,'inputDev':ins.st_dev,'inputIno':ins.st_ino,'inputManifestSHA256':spec['manifestIdentity']['sha256'],'exactInputFiles':summary['fixedFilesIncludingManifest'],'exactInputDirectories':summary['exactDirectories'],'volumeInfrastructureStatOnly':infra,'scope':'Finite own argv/source/current OS observation, not atomic lifetime or whole app sandbox proof.'}
            op=target/'mount-source-observation.json';oid=write_new(op,observation)
            partial.update(status='PASS_INFRASTRUCTURE_PRESEAL_ONLY',attach=attach,mountObservationPath=str(op),mountObservationIdentity=oid,mount={'mountPoint':str(volume),'device':own[0][0],'dev':vs.st_dev,'ino':vs.st_ino,'readonly':True,'shadow':False,'overlay':False},inputDev=ins.st_dev,inputIno=ins.st_ino,mountedSummary=summary,sourceSummary=sources[party][0],manifestSHA256=spec['manifestIdentity']['sha256'],commandGrants={},rootReceipt='UNKNOWN_CONTROLLER_ONLY')
        assert identity(prep_path)==prep_id
        result.update(status='PASS_TWO_RO_PRESEAL_ONLY',finishedAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),postSpace=monitor_space(),limits='Finite sampled own logical bytes only, no hard OS peak or whole descendants accounting; system TMP outside TMPDIR not proven.')
    except Exception as e:
        result.update(status='FAIL_PRESERVED_STOP',errorType=type(e).__name__,error=str(e))
        if isinstance(e,SetupCommandFailure):result['failedCommandReceiptFallback']=e.receipt
    finally:write_new(EVIDENCE/'preseal-result.json',result)
    print(json.dumps({'status':result['status'],'path':str(EVIDENCE/'preseal-result.json')}))
    return 0 if result['status']=='PASS_TWO_RO_PRESEAL_ONLY' else 1
if __name__=='__main__':raise SystemExit(main())
