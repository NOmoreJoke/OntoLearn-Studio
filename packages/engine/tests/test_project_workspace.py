"""Volatile draft/refresh isolation, not durable draft recovery."""

import pytest
from ontolearn_engine.project import ProjectFault
from ontolearn_engine.project.workspace import DraftWorkspace, ResultView


def test_result_refresh_mode_switch_and_late_result_leave_exact_draft_intact():
    workspace = DraftWorkspace("p")
    workspace.open_editor("query", 7, {"text": "SELECT"})
    edited = workspace.edit("query", 0, {"text": "用户未保存输入"})
    for status in ["current", "stale", "historical", "failed", "cancelled"]:
        assert workspace.refresh_result(
            "query", workspace.begin_refresh("query"), ResultView("r-8", "s-8", 8, status)
        )
        assert workspace.draft("query") == edited
    assert not workspace.refresh_result(
        "query", workspace.begin_refresh("query"), ResultView("old", "s-6", 6, "current")
    )
    assert workspace.result("query") == ResultView("r-8", "s-8", 8, "cancelled")
    workspace.set_mode("assisted")
    assert workspace.draft("query") == edited
    workspace.set_mode("guided")
    assert workspace.draft("query") == edited


def test_stale_save_callback_and_stale_edit_cannot_clear_or_overwrite_new_draft():
    workspace = DraftWorkspace("p")
    workspace.open_editor("ontology", 4, {})
    first = workspace.edit("ontology", 0, {"label": "第一稿"})
    latest = workspace.edit("ontology", first.generation, {"label": "第二稿"})
    with pytest.raises(ProjectFault, match="DRAFT_CONFLICT"):
        workspace.edit("ontology", first.generation, {"label": "迟到输入"})
    with pytest.raises(ProjectFault, match="DRAFT_CONFLICT"):
        workspace.accept_committed("ontology", first.generation, 5)
    assert workspace.draft("ontology") == latest
    accepted = workspace.accept_committed("ontology", latest.generation, 5)
    assert accepted.content_json == latest.content_json
    assert accepted.base_revision == 5
    assert accepted.generation == latest.generation + 1
    assert not accepted.dirty


def test_project_sessions_are_independent_and_reopen_never_discards_dirty_contents():
    first, other = DraftWorkspace("p"), DraftWorkspace("other")
    first.open_editor("query", 1, {"label": "初稿"})
    other.open_editor("query", 1, {"label": "另一个项目"})
    draft = first.edit("query", 0, {"label": "脏稿"})
    with pytest.raises(ProjectFault, match="DRAFT_ALREADY_OPEN"):
        first.open_editor("query", 2, {"label": "刷新结果"})
    assert first.draft("query") == draft
    assert other.draft("query").content_json == '{"label":"另一个项目"}'


@pytest.mark.parametrize("mode", ["professional", "", None])
def test_p0_modes_are_only_guided_and_assisted(mode):
    with pytest.raises(ValueError):
        DraftWorkspace("p").set_mode(mode)


@pytest.mark.parametrize("revision", [True, -1, 0.5, None])
def test_invalid_draft_base_is_rejected(revision):
    with pytest.raises(ValueError):
        DraftWorkspace("p").open_editor("query", revision, {})


def test_same_revision_late_callback_and_old_current_cannot_replace_new_or_stale_result():
    workspace = DraftWorkspace("p")
    old_request = workspace.begin_refresh("query")
    new_request = workspace.begin_refresh("query")
    new = ResultView("new-query", "same-snapshot", 8, "current")
    assert workspace.refresh_result("query", new_request, new)
    assert not workspace.refresh_result(
        "query", old_request, ResultView("old-query", "same-snapshot", 8, "current")
    )
    stale_request = workspace.begin_refresh("query")
    stale = ResultView("new-query", "same-snapshot", 8, "stale")
    assert workspace.refresh_result("query", stale_request, stale)
    assert not workspace.refresh_result("query", new_request, new)
    assert not workspace.refresh_result("query", stale_request, new)
    assert workspace.refresh_result("query", stale_request, stale)
    assert workspace.result("query") == stale
