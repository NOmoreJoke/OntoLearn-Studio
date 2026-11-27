"""Volatile editor session. Persistence requires the pending Store metadata API.

Result refresh has no setter for draft contents. Sessions are never authoritative
project data and are not a substitute for durable draft recovery.
"""

from dataclasses import dataclass, replace

from ontolearn_engine.project.transactions import ProjectFault
from ontolearn_engine.storage import canonical


@dataclass(frozen=True)
class Draft:
    editor: str
    base_revision: int
    generation: int
    content_json: str
    dirty: bool


@dataclass(frozen=True)
class ResultView:
    result_ref: str
    snapshot_ref: str
    project_revision: int
    status: str


class DraftWorkspace:
    def __init__(self, project: str):
        if not isinstance(project, str) or not project:
            raise ValueError("Project identity required")
        self.project = project
        self.mode = "guided"
        self._drafts: dict[str, Draft] = {}
        self._results: dict[str, ResultView] = {}
        self._refreshes: dict[str, int] = {}
        self._completed: dict[str, int] = {}

    def set_mode(self, mode: str) -> None:
        if mode not in {"guided", "assisted"}:
            raise ValueError("Unsupported disclosure mode")
        self.mode = mode

    def open_editor(self, editor: str, base_revision: int, content: object) -> Draft:
        if not isinstance(editor, str) or not editor or type(base_revision) is not int:
            raise ValueError("Editor and base revision required")
        if base_revision < 0:
            raise ValueError("Nonnegative base revision required")
        if editor in self._drafts:
            raise ProjectFault("DRAFT_ALREADY_OPEN")
        draft = Draft(editor, base_revision, 0, canonical(content), False)
        self._drafts[editor] = draft
        return draft

    def draft(self, editor: str) -> Draft:
        return self._drafts[editor]

    def edit(self, editor: str, generation: int, content: object) -> Draft:
        current = self.draft(editor)
        if type(generation) is not int or current.generation != generation:
            raise ProjectFault("DRAFT_CONFLICT")
        updated = replace(
            current, generation=generation + 1, content_json=canonical(content), dirty=True
        )
        self._drafts[editor] = updated
        return updated

    def accept_committed(self, editor: str, generation: int, revision: int) -> Draft:
        """Called only with the matching committed marker by the trusted owner."""
        current = self.draft(editor)
        if type(generation) is not int or current.generation != generation:
            raise ProjectFault("DRAFT_CONFLICT")
        if type(revision) is not int or revision <= current.base_revision:
            raise ValueError("A later committed revision required")
        updated = replace(current, base_revision=revision, generation=generation + 1, dirty=False)
        self._drafts[editor] = updated
        return updated

    def begin_refresh(self, slot: str) -> int:
        """Advance for each request or invalidation, even at the same input revision."""
        if not isinstance(slot, str) or not slot:
            raise ValueError("Result slot required")
        generation = self._refreshes.get(slot, 0) + 1
        self._refreshes[slot] = generation
        return generation

    def refresh_result(self, slot: str, generation: int, result: ResultView) -> bool:
        if not isinstance(slot, str) or not slot or not isinstance(result, ResultView):
            raise ValueError("Result slot and view required")
        if (
            result.status not in {"current", "stale", "historical", "failed", "cancelled"}
            or type(result.project_revision) is not int
            or result.project_revision < 0
            or not isinstance(result.result_ref, str)
            or not result.result_ref
            or not isinstance(result.snapshot_ref, str)
            or not result.snapshot_ref
        ):
            raise ValueError("Versioned result view required")
        if type(generation) is not int or generation != self._refreshes.get(slot):
            return False
        current = self._results.get(slot)
        if self._completed.get(slot) == generation:
            return current == result
        if current is not None and result.project_revision < current.project_revision:
            return False
        self._completed[slot] = generation
        self._results[slot] = result
        return True

    def result(self, slot: str) -> ResultView | None:
        return self._results.get(slot)
