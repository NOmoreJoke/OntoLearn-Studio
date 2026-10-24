"""Explicit OS bootstrap environment; never forward application secrets or authority."""

import os
import sys
from collections.abc import Mapping

_SYSTEM_KEYS = frozenset(
    {
        "HOME",
        "USERPROFILE",
        "APPDATA",
        "LOCALAPPDATA",
        "SYSTEMROOT",
        "WINDIR",
        "COMSPEC",
        "TEMP",
        "TMP",
        "TMPDIR",
        "LANG",
        "LC_ALL",
        "LC_CTYPE",
        "TZ",
    }
)


def worker_environment(source: Mapping[str, str] | None = None) -> dict[str, str]:
    source = os.environ if source is None else source
    return {
        key: value
        for key, value in source.items()
        if (key.upper() if sys.platform == "win32" else key) in _SYSTEM_KEYS
    }
