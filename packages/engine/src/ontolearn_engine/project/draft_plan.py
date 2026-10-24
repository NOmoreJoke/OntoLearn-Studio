"""Pure durable-draft CAS plans for the pending format3 Store integration.

No I/O, mutable repository, schema, writer, public DTO or authorization grant.
Heads must come from the trusted Store transaction, never renderer assertions.
The eventual Store adapter must reload/CAS and allocate the operation receipt in
that transaction. Durable generation is distinct from local unsaved-edit tokens.
"""

import json
from dataclasses import dataclass

from ontolearn_engine.storage import Conflict, canonical, digest


def _identity(value: str) -> None:
    if not isinstance(value, str) or not value:
        raise ValueError("Draft identity required")
    _utf8(value)


def _utf8(value: str) -> None:
    try:
        value.encode("utf-8", errors="strict")
    except UnicodeEncodeError:
        raise ValueError("Draft requires valid UTF-8 text") from None


def _revision(value: int) -> None:
    if type(value) is not int or value < 0:
        raise ValueError("Nonnegative integer draft version required")


@dataclass(frozen=True)
class DraftHead:
    project: str
    editor: str
    generation: int
    exists: bool
    bound_domain_revision: int
    content_json: str | None

    def __post_init__(self):
        _identity(self.project)
        _identity(self.editor)
        _revision(self.generation)
        _revision(self.bound_domain_revision)
        if type(self.exists) is not bool:
            raise ValueError("Draft presence must be explicit")
        if self.exists:
            if not isinstance(self.content_json, str):
                raise ValueError("Existing draft payload required")
            _utf8(self.content_json)
            # Strict JSON text, with no nonfinite constants or equivalent spellings.
            if canonical(json.loads(self.content_json)) != self.content_json:
                raise ValueError("Canonical draft payload required")
        elif self.content_json is not None:
            raise ValueError("Deleted draft must retain only its header")

    @property
    def content_hash(self) -> str | None:
        return digest(json.loads(self.content_json)) if self.exists else None

    def value(self) -> dict:
        return {
            "project": self.project,
            "editor": self.editor,
            "generation": self.generation,
            "exists": self.exists,
            "boundDomainRevision": self.bound_domain_revision,
            "content": json.loads(self.content_json) if self.exists else None,
        }


@dataclass(frozen=True)
class DraftPlan:
    before: DraftHead
    after: DraftHead
    intent: str

    @property
    def fingerprint(self) -> str:
        return digest(
            {"intent": self.intent, "before": self.before.value(), "after": self.after.value()}
        )

    @property
    def diff(self) -> dict:
        return {
            "resource": ["draft", self.after.editor],
            "before": self.before.value(),
            "after": self.after.value(),
        }


def _baseline(
    project: str,
    editor: str,
    head: DraftHead | None,
    expected_generation: int,
    domain_revision: int,
) -> DraftHead:
    _identity(project)
    _identity(editor)
    _revision(expected_generation)
    _revision(domain_revision)
    if head is None:
        head = DraftHead(project, editor, 0, False, domain_revision, None)
    if not isinstance(head, DraftHead) or (head.project, head.editor) != (project, editor):
        raise Conflict("Cross-project/editor draft", category="identity")
    if head.generation != expected_generation:
        raise Conflict("Draft generation changed", category="state")
    if head.bound_domain_revision > domain_revision:
        raise Conflict("Draft refers to future domain revision", category="state")
    return head


def save_draft(
    project: str,
    editor: str,
    head: DraftHead | None,
    *,
    expected_generation: int,
    domain_revision: int,
    bound_domain_revision: int,
    content: object,
) -> DraftPlan:
    before = _baseline(project, editor, head, expected_generation, domain_revision)
    _revision(bound_domain_revision)
    if bound_domain_revision > domain_revision:
        raise Conflict("Draft input is in the future", category="state")
    after = DraftHead(
        project, editor, before.generation + 1, True, bound_domain_revision, canonical(content)
    )
    return DraftPlan(before, after, "save")


def delete_draft(
    project: str,
    editor: str,
    head: DraftHead | None,
    *,
    expected_generation: int,
    domain_revision: int,
) -> DraftPlan:
    before = _baseline(project, editor, head, expected_generation, domain_revision)
    # A tombstone header survives even an audited deletion of an absent draft.
    after = DraftHead(
        project, editor, before.generation + 1, False, before.bound_domain_revision, None
    )
    return DraftPlan(before, after, "delete")


def restore_draft(
    project: str,
    editor: str,
    head: DraftHead | None,
    target: DraftHead,
    *,
    expected_generation: int,
    domain_revision: int,
) -> DraftPlan:
    """Target provenance/coverage/confirmation are validated by the future Store adapter."""
    before = _baseline(project, editor, head, expected_generation, domain_revision)
    if not isinstance(target, DraftHead) or (target.project, target.editor) != (project, editor):
        raise Conflict("Cross-project/editor restore draft", category="identity")
    if target.bound_domain_revision > domain_revision:
        raise Conflict("Restore draft input is in the future", category="state")
    # Historical target generation is never reinstated; the live header moves forward.
    after = DraftHead(
        project,
        editor,
        before.generation + 1,
        target.exists,
        target.bound_domain_revision,
        target.content_json,
    )
    return DraftPlan(before, after, "restore")
