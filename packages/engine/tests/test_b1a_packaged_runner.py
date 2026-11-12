"""Actual process faults for B1a package runner; platform premises stay explicit."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location(
    "b1a_runner_test", ROOT / "scripts/run-b1a-packaged-lifecycle.py"
)
runner = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = runner
assert SPEC.loader
SPEC.loader.exec_module(runner)


def run(source: str, output: Path, timeout: float = 2):
    return runner.run_owned(
        [sys.executable, "-I", "-c", source],
        dict(os.environ),
        output,
        Path(sys.executable).resolve(),
        timeout,
    )


def gone(pid: int) -> bool:
    info = runner.process_info(pid)
    return info is None or info.zombie


def test_real_success_leaves_no_owned_process(tmp_path):
    result = run("pass", tmp_path / "success")
    assert result["primary"] == {"kind": "exit", "exitCode": 0}
    assert result["cleanup"]["complete"]
    assert not result["cleanup"]["hadResidual"]
    assert json.loads((tmp_path / "success/exit.json").read_text()) == result["primary"]


@pytest.mark.skipif(
    os.name == "nt", reason="POSIX setsid and signal fault; Windows Job has a separate real test"
)
def test_timeout_closes_real_setsid_child_but_preserves_foreign_sibling(tmp_path):
    marker = tmp_path / "child.pid"
    foreign = subprocess.Popen([sys.executable, "-I", "-c", "import time;time.sleep(30)"])
    try:
        source = f"""import os,signal,subprocess,sys,time
signal.signal(signal.SIGTERM,signal.SIG_IGN)
code="import signal,time;signal.signal(signal.SIGTERM,signal.SIG_IGN);time.sleep(30)"
p=subprocess.Popen([sys.executable,'-I','-c',code],start_new_session=True)
open({str(marker)!r},'w').write(str(p.pid))
time.sleep(30)
"""
        result = run(source, tmp_path / "timeout", timeout=0.5)
        pid = int(marker.read_text())
        assert result["primary"]["kind"] == "timeout"
        assert result["cleanup"]["complete"], result
        assert result["cleanup"]["hadResidual"]
        assert gone(pid)
        assert foreign.poll() is None  # Existing sibling is outside this launch's ownership.
        assert all(row["pid"] != foreign.pid for row in result["cleanup"]["observed"])
    finally:
        foreign.terminate()
        foreign.wait(timeout=5)


def orphan_source(marker: Path, *, manifest: bool, exit_code: int) -> str:
    return f"""import importlib.util,json,os,signal,sys,time
from dataclasses import asdict
from pathlib import Path
r,w=os.pipe()
p=os.fork()
if p:
 os.close(w);os.read(r,1);sys.exit({exit_code})
os.close(r);os.setsid()
if os.fork(): os._exit(0)
signal.signal(signal.SIGTERM,signal.SIG_IGN)
Path({str(marker)!r}).write_text(str(os.getpid()))
if {manifest!r}:
 spec=importlib.util.spec_from_file_location('evidence',os.environ['B1A_OWNER_SCRIPT']);m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
 record={{'runId':os.environ['B1A_OWNER_RUN_ID'],'profile':{str(marker.parent)!r},'phase':'fixture-orphan','identities':[asdict(m.process_info(os.getpid()))]}}
 with open(os.environ['B1A_OWNERSHIP_MANIFEST'],'a') as f:
  f.write(json.dumps(record)+'\\n');f.flush();os.fsync(f.fileno())
os.write(w,b'1');os.close(w)
time.sleep(30)
"""


@pytest.mark.skipif(sys.platform != "linux", reason="Kernel subreaper+pidfd proof is Linux-only")
def test_linux_double_fork_after_leader_exit_is_owned_without_manifest(tmp_path):
    marker = tmp_path / "orphan.pid"
    result = run(orphan_source(marker, manifest=False, exit_code=7), tmp_path / "double-fork")
    assert result["primary"] == {"kind": "exit", "exitCode": 7}
    assert result["cleanup"]["complete"], result
    assert result["cleanup"]["mode"] == "linux-subreaper-pidfd"
    assert gone(int(marker.read_text()))
    assert result["cleanup"]["manifestRecords"] == 0


@pytest.mark.skipif(os.name == "nt", reason="fork fixture; Windows Job tested separately")
def test_manifest_observes_double_fork_and_prevents_green_with_residual(tmp_path):
    marker = tmp_path / "manifest-orphan.pid"
    result = run(orphan_source(marker, manifest=True, exit_code=0), tmp_path / "manifest")
    assert result["primary"] == {"kind": "exit", "exitCode": 0}
    assert result["cleanup"]["complete"], result
    assert result["cleanup"]["hadResidual"]  # CLI refuses acceptance despite clean termination.
    assert result["cleanup"]["manifestRecords"] == 1
    assert gone(int(marker.read_text()))


@pytest.mark.skipif(sys.platform != "win32", reason="Actual Windows Job Object requires Windows")
def test_windows_job_contains_detached_child_on_timeout(tmp_path):
    marker = tmp_path / "windows-child.pid"
    source = f"""import subprocess,sys,time
flags=subprocess.DETACHED_PROCESS|subprocess.CREATE_NEW_PROCESS_GROUP
p=subprocess.Popen([sys.executable,'-I','-c','import time;time.sleep(30)'],creationflags=flags)
open({str(marker)!r},'w').write(str(p.pid))
time.sleep(30)
"""
    result = run(source, tmp_path / "windows-job", timeout=0.5)
    assert marker.exists()
    assert result["primary"]["kind"] == "timeout"
    assert result["cleanup"]["mode"] == "windows-job"
    assert result["cleanup"]["complete"] and result["cleanup"]["remaining"] == 0


@pytest.mark.skipif(os.name == "nt", reason="POSIX cancellation signal fixture")
def test_runner_cancellation_keeps_primary_and_cleanup_separate(tmp_path):
    # Send TERM to run_owned's own process only after its launcher has started.
    source = "import os,signal,time;os.kill(os.getppid(),signal.SIGTERM);time.sleep(30)"
    # The fixture parent is gated launcher, not runner; it verifies a leader signal
    # exit still triggers descendant cleanup without converting primary to success.
    result = run(source, tmp_path / "leader-term")
    assert result["primary"]["kind"] == "exit" and result["primary"]["exitCode"] < 0
    assert result["cleanup"]["complete"], result


@pytest.mark.skipif(os.name == "nt", reason="POSIX runner signal handling")
def test_actual_runner_term_preserves_cancellation_and_closes_children(tmp_path):
    source = (
        "import os,signal,time;"
        "os.kill(int(os.environ['B1A_OWNER_PID']),signal.SIGTERM);time.sleep(30)"
    )
    result = run(source, tmp_path / "runner-term")
    assert result["primary"]["kind"] == "exception"
    assert "cancelled by signal" in result["primary"]["message"]
    assert result["cleanup"]["complete"], result


@pytest.mark.skipif(os.name == "nt", reason="POSIX observed identity assertion")
def test_broken_manifest_does_not_skip_owned_cleanup(tmp_path):
    marker = tmp_path / "broken-child.pid"
    source = f"""import os,time
open({str(marker)!r},'w').write(str(os.getpid()))
open(os.environ['B1A_OWNERSHIP_MANIFEST'],'w').write('{{broken\\n')
time.sleep(30)
"""
    result = run(source, tmp_path / "broken-manifest")
    assert result["primary"]["kind"] == "exception"
    assert not result["cleanup"]["complete"]  # Evidence corruption is never green.
    assert result["cleanup"]["remaining"] == []
    assert gone(int(marker.read_text()))


@pytest.mark.skipif(sys.platform != "linux", reason="Actual Linux subreaper mid-run adoption")
def test_adopted_relaunch_child_is_reaped_before_still_live_leader_exits(tmp_path):
    marker = tmp_path / "relaunch.pid"
    acknowledged = tmp_path / "relaunch-gone"
    source = f"""import os,sys,time
from pathlib import Path
r,w=os.pipe()
p=os.fork()
if p:
 os.close(w);os.read(r,1)
 pid=int(Path({str(marker)!r}).read_text())
 end=time.monotonic()+3
 while Path('/proc/'+str(pid)).exists() and time.monotonic()<end: time.sleep(.02)
 if Path('/proc/'+str(pid)).exists(): sys.exit(42)
 Path({str(acknowledged)!r}).write_text('child reaped while leader alive')
 sys.exit(0)
os.close(r);os.setsid()
if os.fork(): os._exit(0)
Path({str(marker)!r}).write_text(str(os.getpid()));os.write(w,b'1');os.close(w)
time.sleep(.15);os._exit(0)
"""
    result = run(source, tmp_path / "mid-run-reap", timeout=5)
    assert result["primary"] == {"kind": "exit", "exitCode": 0}, result
    assert result["cleanup"]["complete"], result
    assert acknowledged.read_text() == "child reaped while leader alive"
    assert not Path(f"/proc/{marker.read_text()}").exists()
