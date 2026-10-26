"""Read-only native pytest accounting for the two-process CI dispatcher."""

from __future__ import annotations

import json
import locale
import os
import sys
from pathlib import Path

import pytest

_stream = None
_directory = None


def pytest_addoption(parser):
    group = parser.getgroup("engine CI accounting")
    group.addoption("--engine-ci-report", required=True)
    group.addoption("--engine-ci-owner", required=True)
    group.addoption("--engine-ci-files")


def _event(event, **fields):
    _stream.write(json.dumps({"event": event, **fields}, ensure_ascii=False) + "\n")
    _stream.flush()


def pytest_configure(config):
    global _stream, _directory
    _directory = Path(config.getoption("--engine-ci-report"))
    _directory.mkdir(parents=True, exist_ok=True)
    _stream = (_directory / "events.jsonl").open("x", encoding="utf-8")
    _event(
        "session_start",
        pid=os.getpid(),
        parentPid=os.getppid(),
        owner=config.getoption("--engine-ci-owner"),
    )


def _file(item):
    return os.path.normcase(str(item.path.resolve()))


@pytest.hookimpl(trylast=True)
def pytest_collection_modifyitems(config, items):
    assignment = config.getoption("--engine-ci-files")
    if assignment is None:
        return
    files = set(json.loads(Path(assignment).read_text(encoding="utf-8"))["files"])
    selected = [item for item in items if _file(item) in files]
    rejected = [item for item in items if _file(item) not in files]
    items[:] = selected  # Whole files only; native collection order is retained.
    config.hook.pytest_deselected(items=rejected)


@pytest.hookimpl(trylast=True)
def pytest_collection_finish(session):
    with open(os.devnull, "w") as stream:
        default_encoding = stream.encoding
    identity = {
        "rootpath": str(session.config.rootpath),
        "executable": sys.executable,
        "pytestVersion": pytest.__version__,
        "platform": sys.platform,
        "utf8Mode": sys.flags.utf8_mode,
        "preferredEncoding": locale.getpreferredencoding(False),
        "stdoutEncoding": sys.stdout.encoding,
        "defaultFileEncoding": default_encoding,
    }
    manifest = {
        "identity": identity,
        "items": [{"nodeid": item.nodeid, "file": _file(item)} for item in session.items],
    }
    temporary = _directory / "collection.json.tmp"
    temporary.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporary.replace(_directory / "collection.json")
    assignment = session.config.getoption("--engine-ci-files")
    if assignment is not None:
        expected = json.loads(Path(assignment).read_text(encoding="utf-8"))
        if manifest["items"] != expected["items"] or identity != expected["identity"]:
            raise pytest.UsageError("shard collection differs from the full native manifest")


def pytest_runtest_logstart(nodeid, location):
    _event("start", nodeid=nodeid)


def pytest_runtest_logreport(report):
    _event(
        "report",
        nodeid=report.nodeid,
        phase=report.when,
        outcome=report.outcome,
        duration=report.duration,
        wasxfail=getattr(report, "wasxfail", None),
        longrepr=report.longreprtext if report.failed or report.skipped else None,
    )


def pytest_runtest_logfinish(nodeid, location):
    _event("finish", nodeid=nodeid)


def pytest_sessionfinish(session, exitstatus):
    _event("session_finish", exitstatus=int(exitstatus), testsfailed=session.testsfailed)


def pytest_unconfigure(config):
    if _stream is not None:
        _stream.close()
