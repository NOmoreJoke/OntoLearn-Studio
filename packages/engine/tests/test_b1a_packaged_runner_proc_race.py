"""Regression tests for Linux /proc ESRCH (ProcessLookupError) race in B1a packaged runner."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

RUNNER_PATH = Path(__file__).resolve().parents[3] / "scripts" / "run-b1a-packaged-lifecycle.py"


def _load_runner():
    spec = importlib.util.spec_from_file_location("b1a_packaged_runner_under_test", RUNNER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_linux_process_info_returns_none_on_esrch_and_enoent(monkeypatch):
    mod = _load_runner()
    monkeypatch.setattr(mod.sys, "platform", "linux")

    def raise_esrch(self, *args, **kwargs):
        raise ProcessLookupError(3, "No such process")

    monkeypatch.setattr(mod.Path, "read_text", raise_esrch)
    assert mod.process_info(12345) is None

    def raise_enoent(self, *args, **kwargs):
        raise FileNotFoundError(2, "No such file or directory")

    monkeypatch.setattr(mod.Path, "read_text", raise_enoent)
    assert mod.process_info(12345) is None


def test_linux_process_command_returns_none_on_esrch_and_enoent(monkeypatch):
    mod = _load_runner()
    monkeypatch.setattr(mod.sys, "platform", "linux")

    def raise_esrch(self, *args, **kwargs):
        raise ProcessLookupError(3, "No such process")

    monkeypatch.setattr(mod.Path, "read_bytes", raise_esrch)
    assert mod.process_command(12345) is None

    def raise_enoent(self, *args, **kwargs):
        raise FileNotFoundError(2, "No such file or directory")

    monkeypatch.setattr(mod.Path, "read_bytes", raise_enoent)
    assert mod.process_command(12345) is None


def test_linux_malformed_proc_stat_still_raises(monkeypatch):
    import pytest

    mod = _load_runner()
    monkeypatch.setattr(mod.sys, "platform", "linux")
    monkeypatch.setattr(mod.Path, "read_text", lambda self, *args, **kwargs: "123 (app) Z")
    with pytest.raises(RuntimeError, match="Incomplete /proc identity"):
        mod.process_info(123)
