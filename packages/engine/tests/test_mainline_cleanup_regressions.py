"""Simulated initialization faults test cleanup bookkeeping, not OS qualification."""

import asyncio

import pytest
from ontolearn_engine import coordinator as runtime
from ontolearn_engine.project.mainline import make_example_provider
from ontolearn_engine.storage import UnsupportedProjectFormat
from test_mainline_named_example_dispatch import INDEX_SHA256
from test_mainline_named_example_dispatch import staged_bundle as staged_bundle


@pytest.mark.parametrize("phase", ["signal", "thread"])
@pytest.mark.parametrize(
    "book", ["missing", "oversized", "unresolved", "callback-error", "settled"]
)
def test_query_cleanup_observation_never_masks_initialization_primary(
    tmp_path, monkeypatch, phase, book
):
    calls = []
    primary = UnsupportedProjectFormat("primary initialization fixture")

    class Temporary:
        def __init__(self, **kwargs):
            self.name = str(tmp_path)

        def cleanup(self):
            calls.append("temporary")
            raise RuntimeError("secondary temporary fixture")

    class Store:
        def __init__(self, *args, **kwargs):
            pass

        def reconcile_jobs(self):
            pass

        def close(self):
            calls.append("store")
            raise RuntimeError("secondary store fixture")

    class Coordinator:
        def __init__(self, *args, **kwargs):
            self.closed = False
            if book != "missing":
                size = 17 if book == "oversized" else 1
                self._query_replies = {str(i): None for i in range(size)}

        def finish_query_reply(self, request_id, **kwargs):
            calls.append("query-finish")
            if book == "callback-error":
                raise RuntimeError("secondary query callback fixture")
            if book == "settled":
                self._query_replies.pop(request_id)

        async def stop(self):
            calls.append("coordinator")
            raise RuntimeError("secondary coordinator fixture")

    class Thread:
        ident = None

        def __init__(self, **kwargs):
            pass

        def start(self):
            raise primary

        def is_alive(self):
            return False

    signal_calls = 0
    original_signal = runtime.signal.signal

    def signal(*args):
        nonlocal signal_calls
        if args[0] != runtime.signal.SIGTERM:
            return original_signal(*args)
        signal_calls += 1
        if phase == "signal":
            raise primary
        if signal_calls == 1:
            return object()
        calls.append("signal")
        raise RuntimeError("secondary signal restore fixture")

    monkeypatch.setattr(runtime.tempfile, "TemporaryDirectory", Temporary)
    monkeypatch.setattr("ontolearn_engine.job_store.JobStore", Store)
    monkeypatch.setattr(runtime, "Coordinator", Coordinator)
    monkeypatch.setattr(runtime.signal, "signal", signal)
    monkeypatch.setattr(runtime.threading, "Thread", Thread)
    monkeypatch.setenv("ONTOLEARN_ALLOWED_PROJECTS", "[]")
    with pytest.raises(runtime.StartupInitializationFailure) as caught:
        asyncio.run(runtime.serve(profile="business3"))
    failure = caught.value
    assert failure.cause is primary
    assert {"coordinator", "store", "temporary"} <= set(calls)
    assert ("signal" in calls) == (phase == "thread")
    assert failure.reader_state["queryCleanupAttempted"] is True
    assert failure.reader_state["queryCleanupSettled"] == (book == "settled")
    assert ("queryReadHolding" in failure.cleanup_failures) == (book != "settled")
    if book in {"missing", "oversized"}:
        assert "query-finish" not in calls
    else:
        assert calls.count("query-finish") == 1


@pytest.mark.parametrize("supplied", [False, True])
def test_serve_forwards_only_explicit_bootstrap_provider_before_signal_failure(
    tmp_path, staged_bundle, monkeypatch, supplied
):
    provider = (
        make_example_provider(root=staged_bundle, manifest_sha256=INDEX_SHA256)
        if supplied
        else None
    )
    observed = {}
    primary = RuntimeError("simulated signal initialization failure")

    class Temporary:
        def __init__(self, **kwargs):
            self.name = str(tmp_path)

        def cleanup(self):
            observed["temporaryClosed"] = True

    class Store:
        def __init__(self, *args, **kwargs):
            pass

        def reconcile_jobs(self):
            pass

        def close(self):
            observed["storeClosed"] = True

    class Coordinator:
        def __init__(self, *args, **kwargs):
            observed["provider"] = kwargs["example_provider"]
            observed["profile"] = kwargs["profile"]
            self._query_replies = {}

        async def stop(self):
            observed["coordinatorClosed"] = True

    original_signal = runtime.signal.signal

    def signal(*args):
        if args[0] != runtime.signal.SIGTERM:
            return original_signal(*args)
        raise primary

    monkeypatch.setattr(runtime.tempfile, "TemporaryDirectory", Temporary)
    monkeypatch.setattr("ontolearn_engine.job_store.JobStore", Store)
    monkeypatch.setattr(runtime, "Coordinator", Coordinator)
    monkeypatch.setattr(runtime.signal, "signal", signal)
    monkeypatch.setenv("ONTOLEARN_ALLOWED_PROJECTS", "[]")
    with pytest.raises(runtime.StartupInitializationFailure) as caught:
        asyncio.run(runtime.serve(profile="business3", example_provider=provider))
    assert caught.value.cause is primary
    assert observed["provider"] is provider and observed["profile"] == "business3"
    assert all(observed[key] for key in ("temporaryClosed", "storeClosed", "coordinatorClosed"))
    assert caught.value.reader_state["queryCleanupSettled"] is True


def test_serve_refuses_provider_in_legacy_profile_before_initialization(staged_bundle, monkeypatch):
    provider = make_example_provider(root=staged_bundle, manifest_sha256=INDEX_SHA256)

    def forbidden(**kwargs):
        raise AssertionError("legacy provider must be refused before resource acquisition")

    monkeypatch.setattr(runtime.tempfile, "TemporaryDirectory", forbidden)
    with pytest.raises(ValueError, match="^INVALID_PROFILE$"):
        asyncio.run(runtime.serve(profile="legacy2", example_provider=provider))
