"""FR-901 credential scan for every outbound free-text projection (W4-A1).

Both the project package's optional business text and every free-text report
field are scanned item-by-item before any bytes are generated. Only two
outcomes are accepted: ``clear`` (no secret pattern matched) or ``redacted``
(the projection already carries complete fixed redaction markers and no live
secret matched). Anything else rejects the whole export with the frozen
``PERMISSION_DENIED`` credentialRejection code - the secret itself is never
echoed, logged or included in the fault.
"""

import re

SECRET_PATTERNS = (
    # AWS access key ids and symmetric secret material shapes.
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"(?i)aws[_.-]?(?:access[_.-]?key|secret[_.-]?key)[_.-]?(?:id)?:\s*\S+"),
    # Generic key/secret/token/password assignments with nonempty material.
    re.compile(
        r"(?i)\b(?:api[_.-]?key|secret|token|password|passwd|credential)s?\b"
        r"\s*[:=]\s*[\"']?[A-Za-z0-9_./+-]{8,}"
    ),
    # Bearer authorization headers and private key blocks.
    re.compile(r"(?i)bearer\s+[A-Za-z0-9_./=+-]{16,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    # Slack-style tokens and Google API keys.
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
    re.compile(r"AIza[0-9A-Za-z_\-]{35}"),
)
REDACTION_MARKERS = ("[REDACTED]", "\u2588\u2588\u2588", "\ufffd\ufffd\ufffd")

# W4-02 / W4R2-01 / W4R2B-01 / W4R2B-02: deterministic host-absolute-path
# hygiene for every outbound surface. Non-file hierarchical IRIs (including
# non-ASCII CJK segments such as ``http://example.org/本体/home/v1``) are masked
# as full tokens so legitimate RDF IRIs stay byte-for-byte intact while host
# paths glued to CJK/punctuation, case variants (e.g. ``/users`` on APFS),
# double-slash POSIX prefixes (``//Users``), Windows drive/root-relative/UNC
# backslash forms, ``file://``, and ``.ontolearn-host-selections`` are always
# caught. Known boundary: whitespace tokenization scrubs the root-carrying
# token; trailing segments separated by spaces are outside token scope.
HOST_PATH_PLACEHOLDER = "<local-path>"
STAGING_DIRECTORY_NAME = ".ontolearn-host-selections"
_NON_FILE_URI_RE = re.compile(
    r"(?i)(?<![A-Za-z0-9+.-])(?!file://)[a-z][a-z0-9+.-]*://[^\s\"'<>\\，；。！？（）【】\[\]{}|]+"
)
_HOST_PATH_MARKERS = (
    re.compile(
        r"(?i)(?<![A-Za-z0-9._/\\-])/+((?:Users|home|private|var|tmp|etc|Volumes|root))"
        r"(?=(?:/(?!>)|\\|\Z|[\s\"'，；。！？（）【】\[\]{}|]))"
    ),
    re.compile(
        r"(?i)(?<![A-Za-z0-9._/\\-])\\+(?:Users|home|private|var|tmp|etc|Volumes|root|Windows|ProgramData)(?=\\)"
    ),
    re.compile(r"(?<![A-Za-z0-9._/-])[A-Za-z]:(?=\\)"),
    re.compile(r"(?i)file://"),
    re.compile(r"(?i)(?<![A-Za-z0-9._-])\.ontolearn-host-selections(?![A-Za-z0-9._-])"),
)


def _strip_non_file_uris(value):
    return _NON_FILE_URI_RE.sub("", value)


def host_path_marker(value):
    """True when free text carries a host absolute path or private directory
    identifier token. Never matches legitimate ``urn:``/``http(s)://`` IRIs or
    ordinary Chinese/ASCII project names."""
    if not isinstance(value, str) or not value:
        return False
    scrubbed = _strip_non_file_uris(value)
    return any(pattern.search(scrubbed) is not None for pattern in _HOST_PATH_MARKERS)


def sanitize_text(value):
    """Replace every whitespace-delimited token carrying a host path marker
    with the fixed ``<local-path>`` placeholder; separators and every other
    byte are untouched."""

    def scrub(token):
        return HOST_PATH_PLACEHOLDER if host_path_marker(token.group()) else token.group()

    if not host_path_marker(value):
        return value
    return re.sub(r"\S+", scrub, value)


class CredentialLeak(Exception):
    """Raised before any output byte exists; never carries the secret."""


def scan_text(value):
    """Scan one free-text string. Returns "clear" or "redacted".

    Raises :class:`CredentialLeak` when a live secret pattern matches, so the
    caller can reject deterministically without touching the material.
    """
    if not isinstance(value, str) or not value:
        return "clear"
    for pattern in SECRET_PATTERNS:
        if pattern.search(value) is not None:
            raise CredentialLeak()
    if any(marker in value for marker in REDACTION_MARKERS):
        return "redacted"
    return "clear"


def scan_texts(values):
    """Scan an iterable of strings; combined two-state outcome."""
    status = "clear"
    for value in values:
        outcome = scan_text(value)
        if outcome == "redacted":
            status = "redacted"
    return status


def _combine(outcomes):
    return "redacted" if any(outcome == "redacted" for outcome in outcomes) else "clear"


def scan_projection(value):
    """Walk an arbitrary JSON projection and scan every free-text leaf.

    Numbers, booleans and structural keys are not business text; strings are.
    Structural identifiers that never carry user prose (hash-like hex strings,
    UUIDs, enum codes, ISO timestamps) are skipped as non-free-text.
    """
    hex_like = re.compile(r"[0-9a-f]{64}\Z")
    uuid_like = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\Z")
    timestamp_like = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z\Z")

    def walk(node):
        if isinstance(node, str):
            if (
                hex_like.fullmatch(node)
                or uuid_like.fullmatch(node)
                or timestamp_like.fullmatch(node)
            ):
                return "clear"
            return scan_text(node)
        if isinstance(node, dict):
            return _combine(walk(item) for item in node.values())
        if isinstance(node, (list, tuple)):
            return _combine(walk(item) for item in node)
        return "clear"

    return walk(value)
