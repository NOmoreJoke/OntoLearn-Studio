"""``ontolearn-report-v1`` bounded projection and self-contained offline HTML.

The projection is collected from the real Store: project metadata title, the
learning ledger (with the strict independent-transfer rule), ontology/data
summaries from actual state, and persisted query/validation results with their
true staleness. The HTML renderer escapes every dynamic string as plain text
(zero raw HTML/script injection) and stays offline-readable with the existing
CSP - no external resources, no inline script.
"""

import html
import json
from datetime import UTC, datetime

from ontolearn_engine.storage import canonical, digest

PROJECTION_VERSION = "ontolearn-report-v1"
MAX_LIST = 200
RESULT_SCAN_CAP = 400

HINT_KIND = {1: "concept", 2: "operation", 3: "partial", 4: "full"}
AGENT_ASSISTANCE = {"agent-full-assistance": "full"}
CHECK_STATUS = {
    "passed": "passed",
    "not-checked": "not-run",
    "needs-repair": "failed",
    "failed": "failed",
}


def _now_iso():
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _hint(task, payload):
    """The strongest revealed hint level mapped onto the frozen enum."""
    level = payload.get("maxHintLevel", 0)
    if type(level) is not int or level <= 0:
        return "none"
    hints = task.get("hints") if isinstance(task, dict) else None
    kinds = [hint.get("kind") for hint in hints or []]
    kind = kinds[level - 1] if isinstance(kinds, list) and 0 < level <= len(kinds) else None
    if kind == "concept":
        return "concept"
    if kind == "operation":
        return "operation"
    if kind in ("partial-demonstration", "partial"):
        return "partial"
    return "full"


def _feedback_text(payload):
    feedback = payload.get("lastFeedback")
    if feedback is None:
        return ""
    if isinstance(feedback, str):
        return feedback[:16384]
    try:
        return canonical(feedback)[:16384]
    except (TypeError, ValueError):
        return ""


def learning_attempts(records, tasks):
    """Project the live ledger rows onto ReportLearningAttemptDTO.

    The independent transfer rule is recomputed here and is strictly stronger
    than any stored flag: a transfer task, actually completed, a persisted
    passed check with real evidence, zero hints and zero agent assistance.
    Full demonstrations, partial hints, agent assistance and UI-only
    completions can never count.
    """
    attempts = []
    for record in records:
        if record["withdrawn"]:
            continue
        payload = record["payload"]
        task = tasks.get(payload["taskId"]) or {}
        transfer_task = bool(task.get("transfer"))
        hint = _hint(task, payload)
        agent = AGENT_ASSISTANCE.get(payload.get("assistance"), "none")
        evidence = payload.get("evidenceIds") or []
        status = CHECK_STATUS.get(payload.get("checkStatus"), "error")
        evidence_ref = evidence[0] if isinstance(evidence, list) and evidence else None
        operation_completed = bool(payload.get("operationComplete"))
        independent = bool(
            transfer_task
            and operation_completed
            and status == "passed"
            and evidence_ref is not None
            and hint == "none"
            and agent == "none"
        )
        attempts.append(
            {
                "taskId": payload["taskId"],
                "attemptId": record["attempt"],
                "transferTask": transfer_task,
                "operationCompleted": operation_completed,
                "hint": hint,
                "agentAssistance": agent,
                "check": {
                    "status": status,
                    "evidenceRef": evidence_ref,
                    "summary": _feedback_text(payload),
                },
                "stageOutcomes": list(payload.get("completedGuidedStages") or [])[:MAX_LIST],
                "independentTransferSuccess": independent,
            }
        )
    return attempts[:500]


def collect(store, project, internal, host):
    """Bounded honest projection of real persisted state."""
    from ontolearn_engine.project import format3, learning_ledger

    checkpoint = store.project_checkpoint(internal)
    metadata = checkpoint["application"]["metadata"]
    state = store.state(internal)
    try:
        records = learning_ledger._records(format3.application_state(store, internal))
        tasks = host.learning.bare_service().tasks if host is not None else {}
    except Exception:
        records, tasks = [], {}
    counts = {}
    for definition in state["definitions"]:
        counts[definition["layer"]] = counts.get(definition["layer"], 0) + 1
    facts = state["facts"]
    manual = sum(1 for fact in facts if fact["owner"] is None)
    mapped = len(facts) - manual
    ontology_summary = [f"{layer}: {counts[layer]} 个定义" for layer in sorted(counts)] or [
        "本体定义为空"
    ]
    data_summary = [
        f"事实总数: {len(facts)}（手工 {manual}，映射 {mapped}）",
        f"映射规格: {len(state['mappingState'])} 个",
    ]
    query_results, validation_results = _semantic_results(store, internal)
    behavior_results, scenario_comparisons = _w4_results(store, project, internal)
    return {
        "projectionVersion": PROJECTION_VERSION,
        "projectId": project,
        "title": (metadata.get("name") or "项目报告")[:16384],
        "generatedAt": _now_iso(),
        "projectRevision": store.revision(internal),
        "goals": [],
        "competencyQuestions": _competency_questions(state),
        "learning": learning_attempts(records, tasks),
        "ontologySummary": ontology_summary[:MAX_LIST],
        "dataSummary": data_summary[:MAX_LIST],
        "queryResults": query_results[:MAX_LIST],
        "validationResults": validation_results[:MAX_LIST],
        "behaviorResults": behavior_results[:MAX_LIST],
        "scenarioComparisons": scenario_comparisons[:MAX_LIST],
        "assumptions": [],
        "unresolved": [],
    }


def _w4_results(store, project, internal):
    """Bounded real projection of persisted ``w4:behavior:*`` / ``w4:scenario:*`` runs.

    All reads go through the wire services' own public accessors over their
    append-only evidence rows; no second write path and no ad-hoc SQL here.
    Entries keep their true staleness against the live project revision and
    current input snapshot.
    """
    revision = store.revision(internal)
    snapshot_id = digest(store._snapshot_projection(internal))
    behavior_rows, scenario_rows = [], []
    from ontolearn_engine.behavior import service as behavior_service

    for run_id in behavior_service.indexed_runs(store, project)[:RESULT_SCAN_CAP]:
        record = behavior_service.load_run(store, project, run_id)
        if record is None or "binding" not in record:
            continue
        state = record.get("state")
        if state == "failed":
            status, note = "failed", "行为执行失败"
        elif state == "cancelled":
            status, note = "cancelled", "行为运行已取消"
        elif (
            record["binding"]["baseRevision"] == revision
            and record["binding"]["inputSnapshotId"] == snapshot_id
        ):
            status, note = "current", "当前结果"
        else:
            status, note = "stale", "输入已更新，结果过期"
        behavior_rows.append(
            {
                "resultId": record["runId"],
                "inputRevision": record["binding"]["baseRevision"],
                "semanticsVersion": record.get("versions", {}).get(
                    "semanticsVersion", "E.1-private-v2"
                ),
                "scope": "sample",
                "status": status,
                "statusNote": note,
                "summary": (
                    f"行为样本运行 {state}：{len(record.get('actions', []))} 个动作，"
                    f"{len(record.get('diff', {}).get('added', []))} 条新增差异"
                ),
            }
        )
    from ontolearn_engine.scenario import service as scenario_service

    for run_id in scenario_service.indexed_run_ids(store, project)[:RESULT_SCAN_CAP]:
        record = scenario_service.load_run(store, project, run_id)
        if record is None or record.get("status") != "succeeded":
            continue
        identity = record.get("identity", {})
        current = (
            identity.get("projectVersion") == revision
            and identity.get("inputSnapshotId") == snapshot_id
        )
        metrics = record["rounds"][-1]["round"]["metrics"] if record.get("rounds") else {}
        scenario_rows.append(
            {
                "resultId": record["runId"],
                "inputRevision": identity.get("projectVersion", 0),
                "semanticsVersion": identity.get("semantics", "scenario-e2-v1"),
                "scope": record.get("scenarioId", ""),
                "status": "current" if current else "stale",
                "statusNote": "当前结果" if current else "输入已更新，结果过期",
                "summary": (
                    f"场景运行完成 {record.get('lastCommittedRound', 0)}/"
                    f"{record.get('evidence', {}).get('maxRounds', 0)} 轮："
                    f"积压 {metrics.get('backlog', 0)}，"
                    f"已完成工单 {metrics.get('completed', 0)}，"
                    f"未关闭高危告警 {metrics.get('openHighAlerts', 0)}"
                ),
            }
        )
    return behavior_rows, scenario_rows


def _competency_questions(state):
    questions = []
    for record in state["definitions"]:
        if record["layer"] != "query":
            continue
        try:
            payload = json.loads(record["payload"])
        except ValueError:
            continue
        if isinstance(payload, dict) and isinstance(payload.get("descriptor"), dict):
            question = payload["descriptor"].get("capabilityQuestion")
            if isinstance(question, str) and question:
                questions.append(question)
    return questions


def _result_status(store, result_id, job_state):
    """Fixed literal lookups; every variable binds through a parameter."""
    is_current = (
        store._db.execute("SELECT 1 FROM job_current WHERE result=?", (result_id,)).fetchone()
        is not None
    )
    stale_row = store._db.execute(
        "SELECT stale FROM result_state WHERE result=?", (result_id,)
    ).fetchone()
    stale = bool(stale_row and stale_row[0])
    if job_state == "failed":
        return "failed", "执行失败"
    if job_state == "cancelled":
        return "cancelled", "已取消"
    if stale:
        return "stale", "输入已更新，结果过期"
    if is_current:
        return "current", "当前结果"
    return "historical", "历史结果"


def _semantic_results(store, internal):
    """Project real persisted query/validation job results with staleness.

    Bounded plain lookups only: the project's result ids, then their job
    projection rows, then their owning job DTOs. Nothing is interpolated into
    a statement; identifiers always bind through parameters.
    """
    query_rows, validation_rows = [], []
    ids = [
        row[0]
        for row in store._db.execute(
            "SELECT id FROM results WHERE project=?", (internal,)
        ).fetchall()
    ][:RESULT_SCAN_CAP]
    for result_id in ids:
        meta = store._db.execute(
            "SELECT job, projection FROM job_results WHERE id=?", (result_id,)
        ).fetchone()
        if meta is None:
            continue
        job_row = store._db.execute("SELECT dto FROM jobs WHERE id=?", (meta["job"],)).fetchone()
        if job_row is None:
            continue
        try:
            dto = json.loads(job_row["dto"])
            projection = json.loads(meta["projection"])
        except (ValueError, TypeError):
            continue
        capability = dto.get("capability")
        if capability not in ("query.execute", "validation.execute"):
            continue
        status, note = _result_status(store, result_id, dto.get("state"))
        entry = {
            "resultId": result_id,
            "inputRevision": projection.get("inputProjectRevision", 0),
            "semanticsVersion": str(
                (dto.get("implementation") or {}).get("executionSemanticsVersion", "changeset-v1")
            ),
            "scope": str(dto.get("input", {}).get("scope", "asserted")),
            "status": status,
            "statusNote": note,
            "summary": str(projection.get("summary", ""))[:16384],
        }
        if capability == "query.execute":
            query_rows.append(entry)
        else:
            validation_rows.append(entry)
    return query_rows, validation_rows


def render_html(report):
    """Strict plain-text HTML escaping for every dynamic string; offline CSP."""
    esc = html.escape

    def lines(values):
        return "".join(f"<li>{esc(str(value))}</li>" for value in (values or []))

    def attempt_rows(attempts):
        rows = []
        for attempt in attempts:
            check = attempt["check"]
            rows.append(
                "<tr>"
                f"<td>{esc(attempt['taskId'])}</td>"
                f"<td>{esc(attempt['attemptId'])}</td>"
                f"<td>{'是' if attempt['transferTask'] else '否'}</td>"
                f"<td>{'是' if attempt['operationCompleted'] else '否'}</td>"
                f"<td>{esc(attempt['hint'])}</td>"
                f"<td>{esc(attempt['agentAssistance'])}</td>"
                f"<td>{esc(check['status'])}</td>"
                f"<td>{esc(check['evidenceRef'] or '')}</td>"
                f"<td>{'是' if attempt['independentTransferSuccess'] else '否'}</td>"
                "</tr>"
            )
        return "".join(rows)

    def attempts_table(attempts):
        if not attempts:
            return "<p>暂无学习尝试记录。</p>"
        return (
            "<table><thead><tr><th>任务</th><th>尝试</th><th>迁移任务</th><th>已完成操作</th>"
            "<th>提示</th><th>Agent 协助</th><th>检查</th><th>证据</th><th>独立迁移成功</th>"
            f"</tr></thead><tbody>{attempt_rows(attempts)}</tbody></table>"
        )

    def result_rows(results):
        return "".join(
            "<tr>"
            f"<td>{esc(item['resultId'])}</td>"
            f"<td>{item['inputRevision']}</td>"
            f"<td>{esc(item['semanticsVersion'])}</td>"
            f"<td>{esc(item['scope'])}</td>"
            f"<td>{esc(item['status'])}</td>"
            f"<td>{esc(item['statusNote'])}</td>"
            f"<td>{esc(item['summary'])}</td>"
            "</tr>"
            for item in results
        )

    def results_table(caption, results):
        if not results:
            return f"<p>{esc(caption)}：暂无。</p>"
        return (
            f"<h3>{esc(caption)}</h3>"
            "<table><thead><tr><th>结果</th><th>输入版本</th><th>语义版本</th><th>范围</th>"
            f"<th>状态</th><th>说明</th><th>摘要</th></tr></thead>"
            f"<tbody>{result_rows(results)}</tbody></table>"
        )

    learning = report["learning"]
    independent = sum(1 for attempt in learning if attempt["independentTransferSuccess"])
    goals = f"<ul>{lines(report['goals'])}</ul>" if report["goals"] else "<p>暂无。</p>"
    questions = (
        f"<ul>{lines(report['competencyQuestions'])}</ul>"
        if report["competencyQuestions"]
        else "<p>暂无。</p>"
    )
    assumptions = (
        f"<ul>{lines(report['assumptions'])}</ul>" if report["assumptions"] else "<p>暂无。</p>"
    )
    unresolved = (
        f"<ul>{lines(report['unresolved'])}</ul>" if report["unresolved"] else "<p>暂无。</p>"
    )
    return (
        '<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{esc(report['title'])}</title>"
        "<style>body{font-family:system-ui,sans-serif;max-width:60em;margin:2em auto;"
        "padding:0 1em;color:#1a1a1a}h1{font-size:1.5em}h2{border-bottom:1px solid #ddd;"
        "padding-bottom:.2em;margin-top:1.6em}table{border-collapse:collapse;width:100%;"
        "margin:.6em 0;font-size:.9em}th,td{border:1px solid #ddd;padding:.35em .5em;"
        "text-align:left;word-break:break-all}th{background:#f6f6f6}code{font-size:.9em}"
        ".meta{color:#666;font-size:.9em}</style></head><body>"
        f"<h1>{esc(report['title'])}</h1>"
        f'<p class="meta">项目 {esc(report["projectId"])} · 版本 {report["projectRevision"]} · '
        f"生成于 {esc(report['generatedAt'])} · 独立迁移成功 {independent} 项</p>"
        f"<h2>目标</h2>{goals}"
        f"<h2>能力问题</h2>{questions}"
        "<h2>学习</h2>"
        + attempts_table(learning)
        + "<h2>本体</h2><ul>"
        + lines(report["ontologySummary"])
        + "</ul><h2>数据</h2><ul>"
        + lines(report["dataSummary"])
        + "</ul>"
        + results_table("查询结果", report["queryResults"])
        + results_table("验证结果", report["validationResults"])
        + results_table("行为结果", report["behaviorResults"])
        + results_table("场景对比", report["scenarioComparisons"])
        + f"<h2>假设</h2>{assumptions}"
        + f"<h2>待解决</h2>{unresolved}"
        + "</body></html>"
    )
