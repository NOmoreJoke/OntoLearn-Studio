"""Kill the actual coordinator owner; its exact worker PID must stop independently."""

import ctypes
import json
import os
import subprocess
import sys
import time


def alive(pid):
    if sys.platform == "win32":
        from ctypes import wintypes

        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel.OpenProcess.restype = wintypes.HANDLE
        kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        kernel.WaitForSingleObject.restype = wintypes.DWORD
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel.CloseHandle.restype = wintypes.BOOL
        handle = kernel.OpenProcess(0x100000, False, pid)
        if not handle:
            assert ctypes.get_last_error() in {87, 1168}, "owned child could not be observed"
            return False
        try:
            status = kernel.WaitForSingleObject(handle, 0)
            assert status in {0, 0x102}, "owned child wait failed"
            return status == 0x102
        finally:
            assert kernel.CloseHandle(handle), "owned child handle close failed"
    result = subprocess.run(
        ["ps", "-p", str(pid), "-o", "stat="], capture_output=True, text=True, timeout=3
    )
    return (
        result.returncode == 0
        and bool(result.stdout.strip())
        and not result.stdout.strip().startswith("Z")
    )


def test_worker_exits_after_its_actual_coordinator_is_killed(tmp_path):
    source = """
import asyncio,json,os,sys
from uuid import uuid4
from ontolearn_engine.job_store import JobStore
from ontolearn_engine.resources import CONTRACT,IMPLEMENTATION,LIMITS
from ontolearn_engine.coordinator import Coordinator
from ontolearn_engine import coordinator as coordinator_module
if executable:=os.environ.get('ONTOLEARN_TEST_ENGINE'):
 coordinator_module.worker_command=lambda:[executable,'--worker']
async def run():
 s=JobStore(sys.argv[1],contract=CONTRACT);s.create_project('parent-probe')
 p=s.public_project('parent-probe')
 job=s.create_job(p,str(uuid4()),'test.read',{'inputSnapshotId':s.project_get(p)['inputSnapshotId'],'scope':'asserted','definitionId':'probe','parametersHash':s.put_blob(p,{'workMs':10000}),'derivedResultIds':[],'preparedPlanRef':None},None,IMPLEMENTATION,LIMITS)
 c=Coordinator(s,test_mode=True,allowed_projects={p},emit=lambda _:None)
 c.queued.append(job['jobId']);await c.tick()
 for _ in range(200):
  process=c.active[job['jobId']]['process']
  if process:
   print(json.dumps({'coordinatorPid':os.getpid(),'workerPid':process.pid}),flush=True);break
  await asyncio.sleep(.01)
 else:raise RuntimeError('no real worker')
 await asyncio.sleep(30)
asyncio.run(run())
"""
    owner = subprocess.Popen(
        [sys.executable, "-I", "-c", source, str(tmp_path / "owner.sqlite")],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    worker = None
    try:
        # Both identities are emitted by the actual coordinator, not discovered
        # by matching names. Only this verified owner is killed once.
        import queue
        import threading

        messages = queue.Queue()
        threading.Thread(target=lambda: messages.put(owner.stdout.readline()), daemon=True).start()
        identities = json.loads(messages.get(timeout=8))
        actual_owner = identities["coordinatorPid"]
        worker = identities["workerPid"]
        assert actual_owner > 1 and actual_owner != worker
        assert alive(worker)
        # Popen.pid may identify a venv redirector. Kill the Python process that
        # actually owns SQLite/Coordinator, whose identity came from its code.
        os.kill(actual_owner, 9)
        owner.wait(timeout=5)
        end = time.monotonic() + 3
        while alive(worker) and time.monotonic() < end:
            time.sleep(0.05)
        assert not alive(worker)
    finally:
        if owner.poll() is None:
            owner.kill()
            owner.wait(timeout=5)
        owner.stdout.close()
        owner.stderr.close()
        if worker is not None and alive(worker):
            os.kill(worker, 9)  # Exact child of this probe only; failure remains a failure.
