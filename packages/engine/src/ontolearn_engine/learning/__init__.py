"""Offline learning content and pure checks; no IPC, Store writer or domain executor."""

import sys
from pathlib import Path


def default_learning_root() -> Path:
    """Repository-shaped root holding content/learning and product baselines.

    A PyInstaller build receives the verified learning trees through --add-data
    under sys._MEIPASS; a checkout run uses the source repository itself. Both
    must satisfy baselines.verify() unchanged, which is what anchors the T01
    ledger's content identity (manifestSha256 and friends).
    """
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parents[5]
