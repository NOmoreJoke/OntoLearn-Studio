"""Worktree-local pytest helpers for Windows cp1252 and env-var limit compatibility."""

import hashlib
from pathlib import Path

import pytest

_MAX_INLINE_PARAM_ID_CHARS = 16384
_IMMUTABLE_BOUNDARIES_DOC = (
    Path(__file__).resolve().parents[3] / "docs/iterations/I03/I05-semantic-boundaries.md"
).resolve()


def pytest_make_parametrize_id(
    config: pytest.Config,
    val: object,
    argname: str,
) -> str | None:
    """Bound huge parametrize string IDs so PYTEST_CURRENT_TEST fits Windows's 32767-char limit."""
    del config
    if isinstance(val, str) and len(val) > _MAX_INLINE_PARAM_ID_CHARS:
        digest = hashlib.sha256(val.encode("utf-8", errors="surrogateescape")).hexdigest()[:12]
        return f"{argname}-len{len(val)}-{digest}"
    return None


@pytest.fixture(autouse=True)
def _utf8_for_pinned_legacy_boundaries_doc(
    request: pytest.FixtureRequest,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Default Path.read_text to UTF-8 for the immutable I05 doc test on Windows cp1252 hosts."""
    node_name = getattr(request.node, "originalname", request.node.name)
    if (
        request.path.name != "test_semantic_error_adapter.py"
        or node_name != "test_golden_rows_cover_exact_approved_25"
    ):
        return

    original_read_text = Path.read_text

    def _read_text_utf8_default(
        self: Path,
        encoding: str | None = None,
        errors: str | None = None,
    ) -> str:
        if encoding is None and self.resolve() == _IMMUTABLE_BOUNDARIES_DOC:
            encoding = "utf-8"
        return original_read_text(self, encoding=encoding, errors=errors)

    monkeypatch.setattr(Path, "read_text", _read_text_utf8_default)
