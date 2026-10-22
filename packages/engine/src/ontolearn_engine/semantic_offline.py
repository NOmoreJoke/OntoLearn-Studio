"""Scoped fail-closed I/O guard for pure, in-memory semantic operations.

The hook is permanent, but affects only the executing context. It does not
reconfigure RDFLib's global plugin registry or other engine tasks.
"""

import logging
import sys
from contextlib import contextmanager
from contextvars import ContextVar


class SemanticError(ValueError):
    """Internal code only; callers must map it to the shared boundary contract."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


_active = ContextVar("ontolearn_semantic_offline", default=False)


def _audit(event, args):
    if _active.get() and (
        event.startswith("socket.")
        or event in {"urllib.Request", "subprocess.Popen", "os.system", "os.posix_spawn"}
    ):
        raise SemanticError("EXTERNAL_ACCESS_DENIED")


sys.addaudithook(_audit)


class _NoRawLiteralDiagnostics(logging.Filter):
    def filter(self, record):
        # RDFLib logs invalid literal values and tracebacks before raising/returning.
        # Keep other tasks' logger behavior intact; no raw input escapes this scope.
        return not _active.get()


logging.getLogger("rdflib.term").addFilter(_NoRawLiteralDiagnostics())


@contextmanager
def offline():
    token = _active.set(True)
    try:
        yield
    finally:
        _active.reset(token)
