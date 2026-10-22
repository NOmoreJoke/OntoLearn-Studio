"""Bounded author harness. Synthetic mutations never touch the frozen browser source."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import uuid
import threading

ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / 'authority.json'
SOURCE = ROOT.parent / '20261022_review_backlog/stage-review-package/payload/artifacts/browser'
NODE = Path('/usr/local/bin/node')
MODULE = ROOT.parents[1] / 'OntoLearn-Studio/node_modules/playwright/index.mjs'
BROWSER = Path('/Users/kyle/Library/Caches/ms-playwright/chromium_headless_shell-1234/chrome-headless-shell-mac-arm64/chrome-headless-shell')
DEPS = ROOT.parents[1] / 'OntoLearn-Studio/node_modules'
EVIDENCE = ROOT / 'evidence'
FIXTURES = ROOT / 'validation/browser-fixtures'


def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def usage(p):
    total = 0
    if p.exists():
        for entry in os.scandir(p):
            if entry.is_dir(follow_symlinks=False):
                total += usage(Path(entry.path))
            else:
                total += entry.stat(follow_symlinks=False).st_size
    return total


def input_identity():
    paths = [SOURCE / 'manifest.json', SOURCE / 'index.html', SOURCE / 'entry.tsx', SOURCE / 'shell.css']
    manifest = json.loads((SOURCE / 'manifest.json').read_text())
    paths += [SOURCE / 'snapshot' / x['path'] for x in manifest['sources']]
    return [{'path': str(p), 'sha256': sha(p), 'bytes': p.stat().st_size,
             'mode': p.stat().st_mode & 0o777} for p in paths]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--phase', choices=['boundaries', 'real'], required=True)
    parser.add_argument('--positive-only', action='store_true')
    parser.add_argument('--churn', action='store_true')
    args = parser.parse_args()
    authority = json.loads(AUTH.read_text())
    if sha(AUTH) != '5c68a8d00257149d9846ec4fb0dcba7fa13ea7922a8ab04c361b812f0efdc210':
        raise RuntimeError('AUTHORITY_CHANGED')
    base = Path(authority['allowedRunBase'])
    base.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(exist_ok=True)
    FIXTURES.mkdir(exist_ok=True)
    start_source = input_identity()
    results = []
    prefix = 'browser-' + args.phase + '-' + uuid.uuid4().hex[:8]

    def command(tool, name, source=SOURCE):
        work = base / (prefix + '-' + name)
        common = ['--authority', str(AUTH), '--authority-sha256', sha(AUTH),
                  '--input-root', str(source), '--input-manifest', str(source / 'manifest.json'),
                  '--input-manifest-sha256', sha(source / 'manifest.json'),
                  '--work-root', str(work), '--output-root', str(work / 'out')]
        if tool == 'build':
            return [str(NODE), str(ROOT / 'browser/build.mjs'), *common,
                    '--dependency-root', str(DEPS)], work
        return [sys.executable, str(ROOT / 'browser/verify-browser.py'), *common,
                '--node', str(NODE), '--playwright-module', str(MODULE),
                '--browser', str(BROWSER), '--session', work.name], work

    def replace(cmd, flag, value):
        cmd[cmd.index('--' + flag) + 1] = str(value)

    def run(name, cmd, expected, expected_failure=None, timeout=195):
        began = time.monotonic()
        proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, timeout=timeout)
        stdout = EVIDENCE / (prefix + '-' + name + '.stdout.log')
        stderr = EVIDENCE / (prefix + '-' + name + '.stderr.log')
        stdout.write_text(proc.stdout)
        stderr.write_text(proc.stderr)
        after = usage(base)
        record = dict(name=name, argv=cmd, cwd=str(ROOT), exit=proc.returncode,
                      expectedExit=expected, elapsedSeconds=time.monotonic() - began,
                      stdout=str(stdout), stderr=str(stderr), combinedBytesAfter=after,
                      capturesBytes=len(proc.stdout.encode())+len(proc.stderr.encode()))
        if proc.returncode != expected:
            record['unexpected'] = True
        if expected_failure:
            work = Path(cmd[cmd.index('--work-root')+1])
            report = work/'out/browser-result.json'
            failure = (json.loads(report.read_text()).get('firstFailure') or '') if report.exists() else ''
            record['firstFailure'] = failure
            record['expectedFailureMarker'] = expected_failure
            if expected_failure not in failure:
                record['unexpected'] = True
        results.append(record)
        print(json.dumps({k:record.get(k) for k in ['name','exit','expectedExit','elapsedSeconds','combinedBytesAfter','unexpected','firstFailure']}), flush=True)
        return not record.get('unexpected')

    stop_churn = threading.Event()
    churn_dir = base / (prefix + '-temporary-entry-churn')
    thread = None
    churn_count = [0]
    if args.churn:
        churn_dir.mkdir()
        def churn():
            while not stop_churn.is_set():
                p = churn_dir / 'temporary.lock'
                p.write_text('x')
                p.unlink()
                churn_count[0] += 1
                time.sleep(0.0005)
        thread = threading.Thread(target=churn, daemon=True)
        thread.start()

    if args.phase == 'boundaries':
        for tool in ['build', 'verify']:
            for case in ['bad-authority-sha', 'bad-manifest-sha', 'existing-run',
                         'protected-run', 'symlink-run', 'alias-input', 'output-escape']:
                cmd, work = command(tool, tool+'-'+case)
                cleanup = None
                if case == 'bad-authority-sha':
                    replace(cmd,'authority-sha256','0'*64)
                elif case == 'bad-manifest-sha':
                    replace(cmd,'input-manifest-sha256','0'*64)
                elif case == 'existing-run':
                    work.mkdir()
                    (work/'sentinel').write_text('must survive')
                elif case == 'protected-run':
                    replace(cmd,'work-root',SOURCE/'forbidden-new-run')
                    replace(cmd,'output-root',SOURCE/'forbidden-new-run/out')
                elif case == 'symlink-run':
                    work.symlink_to(SOURCE, target_is_directory=True)
                    cleanup = work
                elif case == 'alias-input':
                    alias = FIXTURES/(prefix+'-'+tool+'-alias')
                    alias.symlink_to(SOURCE,target_is_directory=True)
                    replace(cmd,'input-root',alias)
                    replace(cmd,'input-manifest',alias/'manifest.json')
                    cleanup = alias
                elif case == 'output-escape':
                    replace(cmd,'output-root',SOURCE/'forbidden-output')
                try:
                    run(tool+'-'+case,cmd,1,timeout=20)
                finally:
                    if cleanup is not None:
                        cleanup.unlink()
                if case == 'existing-run' and (work/'sentinel').read_text()!='must survive':
                    raise RuntimeError('EXISTING_RUN_MUTATED')
    else:
        cmd, build_work = command('build','build-positive')
        if run('build-positive',cmd,0):
            positive = FIXTURES/(prefix+'-positive')
            positive.mkdir()
            # Copy precisely source inputs, without author's output/runtime directory.
            manifest = json.loads((SOURCE/'manifest.json').read_text())
            for rel in ['manifest.json','entry.tsx','shell.css','index.html'] + ['snapshot/'+x['path'] for x in manifest['sources']]:
                dest=positive/rel
                dest.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(SOURCE/rel,dest)
            shutil.copy2(build_work/'out/index.html',positive/'index.html')
            for name, mutate, expected, marker in [
                ('positive',None,0,None),
                ('old-learning-clip','clip',1,'INNER_CONTAINER'),
                ('covered-control','cover',1,'CONTROL_NOT_HITTABLE'),
                ('last-task-unreachable','last',1,'CONTROL_NOT_HITTABLE')]:
                if args.positive_only and mutate:
                    continue
                subject=positive
                if mutate:
                    subject=FIXTURES/(prefix+'-'+name)
                    shutil.copytree(positive,subject)
                    html=(subject/'index.html').read_text()
                    # Replace existing hashed style bytes and CSP hash, not unsafe-inline or network.
                    begin=html.index('<style>')+len('<style>')
                    end=html.index('</style>',begin)
                    css=html[begin:end]
                    if mutate=='clip':
                        changed=css.replace('.stage-surface .learning-grid{grid-template-columns:minmax(0,1fr)}', '.stage-surface .learning-grid{grid-template-columns:1fr}').replace('.stage-surface .learning-grid>*{min-width:0}', '')
                        # Vite may render minmax as minmax(0,1fr); exact old shell rule only.
                        if changed==css:
                            raise RuntimeError('NEGATIVE_CSS_TARGET_NOT_FOUND')
                    elif mutate=='cover':
                        changed=css+'\n.learning-glossary{position:relative}.learning-glossary:after{content:"";position:absolute;inset:0;z-index:99;background:transparent}'
                    else:
                        changed=css+'\n.learning-path li:last-child button{pointer-events:none}'
                    import base64
                    oldhash=base64.b64encode(hashlib.sha256(css.encode()).digest()).decode()
                    newhash=base64.b64encode(hashlib.sha256(changed.encode()).digest()).decode()
                    html=html[:begin]+changed+html[end:]
                    html=html.replace('sha256-'+oldhash,'sha256-'+newhash)
                    (subject/'index.html').write_text(html)
                    m=json.loads((subject/'manifest.json').read_text())
                    m['build']['indexSha256']=sha(subject/'index.html')
                    (subject/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
                cmd,work=command('verify','verify-'+name,subject)
                run('verify-'+name,cmd,expected,marker)
                if usage(base)>64*1024*1024:
                    raise RuntimeError('AUTHOR_BROWSER_STAGE_64MIB_THRESHOLD')
    stop_churn.set()
    if thread:
        thread.join(timeout=2)
    source_after = input_identity()
    report=dict(phase=args.phase, prefix=prefix, results=results,
                passed=all(not x.get('unexpected') for x in results),
                before=start_source,after=source_after,sourceUnchanged=start_source==source_after,
                combinedBytesAfter=usage(base), fixturesBytes=usage(FIXTURES),
                boundedAuthorValidationOnly=True, screenshotsAndFailuresRetained=True, temporaryEntryChurnCount=churn_count[0], positiveOnly=args.positive_only)
    (EVIDENCE/('browser-'+args.phase+('-positive-churn' if args.positive_only else '')+'-summary.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    return 0 if report['passed'] and report['sourceUnchanged'] else 1


if __name__=='__main__':
    sys.exit(main())
