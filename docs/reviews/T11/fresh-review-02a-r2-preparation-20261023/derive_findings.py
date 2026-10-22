"""Static source binding for the original19 opinions; no product execution."""

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
SCOPE = json.loads((HERE / "scope-107-read-plan.json").read_text())
BY_PATH = {r["path"]: r for r in SCOPE["files"]}
V = "scripts/release/verify.mts"
CLI = "scripts/release/verify-release.mjs"
T = "tests/unit/t11-release.test.ts"
IO = "tests/unit/t11-release-io.test.ts"
MAC = "scripts/release/collect-macos.sh"
WIN = "scripts/release/collect-windows.ps1"
PE = "scripts/release/pe-machine.ps1"
R = "docs/release/README.md"
U = "docs/release/user-study.md"
G = "docs/release/migration-recovery.md"
A = "docs/iterations/T11/acceptance.md"
S = "docs/reviews/T11/status.md"

# Exact source coordinates are independently proposed by collector_fix, then
# extracted from the immutable02a page bodies. A terminal display-only empty
# line is not silently counted as a physical source line.
DETAILS = {
    "M-F-A": (
        "v3显式case和独立case pin；通用合法空层与G.6六层非空分开，模板不能restoreCurrent，旧v2拒绝。",
        [(V, 232, 239), (V, 946, 985), (T, 645, 715), (G, 19, 23)],
        "SOURCE_STATIC / OWNER_HISTORICAL_SYNTHETIC_E1_E2",
        "T01/T10正式接口、真实双向G.6迁移与重关联冲突、继续编辑查询撤销；F01不代答。",
    ),
    "M-F-B": (
        "Q9批准来源/日期/hash入树，route/model与独立freeze及APPROVED_MODEL双向pin；任意共同tuple和Base URL误用拒绝。",
        [(V, 13, 18), (V, 843, 857), (T, 717, 736), (R, 27, 31)],
        "SOURCE_STATIC / OWNER_HISTORICAL_SYNTHETIC_E1_E2",
        "合法API凭据、真实返回版本/模式、评估hash和零伪造原件；不授新服务、网关或消费。",
    ),
    "M-F-C": (
        "evidence固定873唯一manifest/PRD SHA、版本及17精确路径；内容hash仍来自唯一manifest，缺/多/版本共同改pin仍拒绝。",
        [(V, 19, 44), (V, 565, 580), (T, 803, 824)],
        "SOURCE_STATIC / OWNER_HISTORICAL_EXPLICIT_FIXED873_E1_E2",
        "真实领域50例输出、57P0产品集成及CI显式探针；oracle构造不作领域执行。",
    ),
    "M-F-D": (
        "保完整八步core&&transferCompleted并拒矛盾；产品提示完成与独立迁移/辅助分记，保4/5和3/5边界。",
        [(V, 888, 902), (T, 785, 801), (U, 25, 29)],
        "SOURCE_STATIC / OWNER_HISTORICAL_SYNTHETIC_E1_E2",
        "至少5真人、逐段/逐次辅助及Agent完整示范反例；F16跨尝试资格待决，不改分母。",
    ),
    "M-F-E": (
        "命令/日期/候选与默认四skip、显式flag分层，旧65/695等仅属原候选。",
        [(A, 18, 32), (S, 3, 23)],
        "DOCUMENT_STATIC / OWNER_HISTORICAL_EXPLICIT_FLAG_E1_E2",
        "新指定审查和CI须实际取到873并显式执行，默认绿/skip不关闭固定输入门。",
    ),
    "M-F-F": (
        "恢复与每个旧资产报告都强制rollback-retain-new-version-copy及rollback-refuse-incompatible-format。",
        [(V, 308, 317), (V, 1041, 1055), (T, 773, 783), (G, 21, 23)],
        "SOURCE_STATIC / OWNER_HISTORICAL_SYNTHETIC_E1_E2",
        "真实上一版双平台签名包、保留新数据副本、旧版拒新格式及备份恢复原件。",
    ),
    "M-F-G": (
        "主持人/独立验收者核同意、资格、逐段尝试与示范计数；工具record只hash，不添布尔认证真人。",
        [(U, 7, 21), (U, 29, 29), (V, 880, 885)],
        "DOCUMENT_AND_SOURCE_STATIC",
        "真实同意/观察原件、人数/八步完成率、辅助来源与尝试关系由主持人及独立验收者核。",
    ),
    "M-F-H": (
        "原①半成品：状态/步骤/首raw保留；原②同包：package/inventory/app/engine/provenance声明字节绑定；原③PE：界限/固定错误/关闭流。",
        [(MAC, 19, 42), (MAC, 69, 71), (WIN, 16, 42), (WIN, 84, 93), (V, 777, 804), (PE, 7, 28), (T, 738, 771)],
        "COLLECTOR_STATIC / OWNER_HISTORICAL_BASH_N_E1 / OWNER_HISTORICAL_SYNTHETIC_E1_E2",
        "①真实两OS首步/中途失败、成功和防覆盖；②T03唯一包内清单及真实安装/解包来源；③Windows PowerShell语法及小PE运行。三子项不互替。",
    ),
    "M-F-I": (
        "同fd有限结构/hash；PE/koly不认证安装器实质、签名链或来源，valid仅绑定报告声明字节。",
        [(V, 417, 451), (R, 35, 47)],
        "SOURCE_STATIC / OWNER_HISTORICAL_CONTROLLED_IO_E1_E2",
        "真实Authenticode/时间戳链、Developer ID/嵌套代码/公证/Gatekeeper、下载安装和来源原件。",
    ),
    "M-F-J": (
        "CLI墙钟覆盖freeze.now并拒伪未来now；同步来源/偏差外部记录，工具不认证时钟正确。",
        [(CLI, 17, 26), (T, 1151, 1171), (R, 45, 47)],
        "SOURCE_STATIC / OWNER_HISTORICAL_CLI_E1_E2",
        "真实取证机日期/时区/同步来源、可知偏差及报告时间链须操作者记录并独审核对。",
    ),
    "M-F-K": (
        "dated当前入口、适用候选/取代关系；旧active/current和不同来源hash不合并，不回写旧原件或Goal。",
        [(S, 3, 23)],
        "DOCUMENT_STATIC",
        "持续收件核原件身份和适用期，原状态/来源矛盾保留。",
    ),
    "M-F-L": (
        "首38仅摘录/transcript、缺独立完整raw；其后48归档另列，不补造或推断永久不可获得。",
        [(S, 17, 23)],
        "DOCUMENT_STATIC / OWNER_HISTORICAL_ARCHIVE_IDENTITY",
        "当前首38独立完整raw缺口UNKNOWN；不重跑冒充首败或以后继回填。",
    ),
    "Z-F1": (
        "Expected只safeParse一次，finite日期检查保留。",
        [(V, 509, 517)],
        "SOURCE_STATIC / OWNER_HISTORICAL_FREEZE_TYPECHECK_E1_E2",
        "新指定审者按真实语义处置，无需调用次数镜像测试；owner不签关闭。",
    ),
    "Z-F2": (
        "受控打开/fstat、限额先于分配parse、同fd读取/hash/格式、尾部漂移检查及finally关闭；可信稳定祖先前提保留。",
        [(V, 345, 407), (V, 434, 451), (IO, 39, 125), (R, 43, 47)],
        "SOURCE_STATIC / OWNER_HISTORICAL_CONTROLLED_IO_E1_E2",
        "确定性小文件模拟不证明所有祖先目录并发替换安全；不做新压力/native/SQLite损坏研究。",
    ),
    "Z-F3": (
        "缺dest显式MIGRATION_DESTINATION并continue，不传undefined跳过绑定；不反称原分支不可达。",
        [(V, 1067, 1074), (T, 1144, 1149)],
        "SOURCE_STATIC / OWNER_HISTORICAL_SYNTHETIC_E1_E2",
        "真实双向资产及迁移报告仍待验。",
    ),
    "Z-F4": (
        "Mac全部已知系统命令含最前OS/arch门及xcrun改绝对路径。",
        [(MAC, 8, 16), (MAC, 20, 71)],
        "SOURCE_STATIC / OWNER_HISTORICAL_BASH_N_E1",
        "真实macOS15 arm64可用性及成功/失败流程；禁止真实collector即使预期早拒绝。",
    ),
    "Z-F5": (
        "DOS长度/e_lfanew范围/PE签名machine/size/finally与固定PE_INVALID；Win组件架构约束。",
        [(PE, 7, 28), (WIN, 63, 68), (IO, 102, 115)],
        "POWERSHELL_SOURCE_STATIC / OWNER_HISTORICAL_TS_SMALL_PE_E1_E2",
        "真实Windows PowerShell语法、有效/截断/越界小PE及签名/架构；TS不代替PS运行。",
    ),
    "Z-F6": (
        "pending/failed/complete及步骤，成功末尾才complete；strict marker/check绑定，missing/pending/failed/malformed负例拒绝。",
        [(V, 46, 53), (V, 777, 781), (MAC, 19, 42), (WIN, 16, 42), (T, 738, 762)],
        "COLLECTOR_STATIC / OWNER_HISTORICAL_BASH_N_E1 / OWNER_HISTORICAL_SYNTHETIC_E1_E2",
        "真实两OS首步/中途失败、成功/新目录防覆盖；marker不证明native、签名或同包。",
    ),
    "M036-F1": (
        "verify.ts原字节rename唯一verify.mts；纯JS参数/Node24.3+24.x门、try内动态import；整段stderr/空stdout/exit2恢复，manifest-schema仍exit1，独立warning保留。",
        [(CLI, 2, 27), (T, 1173, 1338), (A, 3, 7)],
        "SOURCE_STATIC / OWNER_HISTORICAL_NODE24_15_CLI_TYPECHECK_FULLCHECK_E2",
        "旧Node仅guard模拟，非旧Node实机；须完整新同02a指定双审与全文处置，不能替代原18。",
    ),
}


def source(path):
    return b"".join((HERE / p["pageId"]).read_bytes() for p in BY_PATH[path]["pages"])


def main():
    old = json.loads(source("docs/reviews/T11/owned-fixes-20261023/disposition.json"))
    originals = {r["id"]: r for r in old["findings"]}
    rows = []
    for id, (action, refs, levels, pending) in DETAILS.items():
        original = originals.get(id, {"originalSeverity": "中", "ownerAction": "F1 exact ESM/error-surface repair"})
        evidence = []
        for path, start, end in refs:
            raw = source(path)
            lines = raw.splitlines(keepends=True)
            assert 0 < start <= end <= len(lines), (path, start, end, len(lines))
            excerpt = b"".join(lines[start - 1 : end])
            evidence.append({
                "path": path,
                "candidate": SCOPE["candidate"],
                "sourceSha256": hashlib.sha256(raw).hexdigest(),
                "physicalLines": [start, end],
                "excerptSha256": hashlib.sha256(excerpt).hexdigest(),
                "excerpt": excerpt.decode(),
            })
        rows.append({
            "id": id,
            "originalSeverity": original["originalSeverity"],
            "ownerStatus": "OPEN",
            "ownerClosed": False,
            "sourceTreatment": action,
            "originalOwnerActionRecord": original["ownerAction"],
            "sourceEvidence": evidence,
            "existingVerificationLevels": levels.split(" / "),
            "stillDependentOn": pending,
            "nextDisposition": "Independent close/reopen/partial/unverifiable by original severity and actual evidence; no preset Pass",
        })
    assert len(rows) == 19
    obj = {
        "schemaVersion": 1,
        "candidate": SCOPE["candidate"],
        "preparationOnly": True,
        "findingCount": 19,
        "ownerClosedCount": 0,
        "originalSeverityChanged": False,
        "sameTopicZ036O1": "Information observation of M036-F1; not twentieth finding",
        "MNewTurnFailedMeaning": "Review did not complete; product pass/fail not inferred",
        "originalMNotPass": "7d28 and036 preserved unchanged",
        "historicalEvidence": {
            "E1": {
                "record": "docs/reviews/T11/owned-fixes-20261023/verification.json",
                "candidate": "33894063fcf17bc865f4c91556a8ca01845812e7",
                "targeted": 109,
                "fullTS": 739,
                "fullPython": 1052,
                "archiveSha256": "2e714950bfcba075d2d01d464ed8cbef1c4c3c473e8299419cceb2b5bb67dba0",
                "layer": "Historical owner controlled/static/synthetic/build; not product/native/production",
            },
            "E2": {
                "record": "docs/reviews/T11/f1-fix-20261023/verification.json",
                "immutableBinding": {
                    "suppliedHistoricalFile": "supplemental-history/02a-postcommit-binding.json",
                    "originalPath": "docs/reviews/T11/f1-candidate-handoff-20261023/binding.json",
                    "fixed107Changed": False,
                },
                "candidate": SCOPE["candidate"],
                "node": "v24.15.0",
                "firstTargeted": 122,
                "finalTargeted125IncludedInFull": True,
                "final125StandaloneRerun": False,
                "fullTS": 755,
                "fullPython": 1052,
                "archiveSha256": "95067c1679eb1bfe1dab15219f74b41e9993ccfdd1d25b5a3afaa663436d901b",
                "layer": "Historical owner run, early env from wrapper qualification; no inherited designated Pass",
            },
        },
        "currentPreparationProductCommands": [],
        "findings": rows,
        "releaseAuthorized": False,
    }
    (HERE / "source-treatment-19.json").write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")
    md = [
        "# 19项source处理与验证层级绑定", "",
        f'固定候选 `{SCOPE["candidate"]}`。19原级不改，owner全OPEN/关闭0；source已处理与指定审查/真实父门关闭分开。M前任务failed不反推产品不通过，Z036-O1不增第20项。', "",
        "E1：338历史owner专项109、显式739TS/1052Py和14raw。E2：02a绑定的owner首专项122，末版125并入显式755TS/1052Py，125未单独再跑。均非本准备或下一审者亲跑。", "",
        "| ID | 原级别 | source已处理及位置 | 既有验证层级 | 仍依赖的门 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        refs = "；".join(f'{x["path"]}:{x["physicalLines"][0]}–{x["physicalLines"][1]}' for x in row["sourceEvidence"])
        md.append(f'| {row["id"]} | {row["originalSeverity"]} | {row["sourceTreatment"]} 位置：{refs} | {" / ".join(row["existingVerificationLevels"])} | {row["stillDependentOn"]} |')
    md += ["", "原字节摘录、行范围和hash见`source-treatment-19.json`；完整source仍须按107全文plan读，不以本表代读。原高1/中3/低8、Z六P4与M036-F1中保留；各新审自行逐项处置，不预设Pass。", ""]
    (HERE / "source-treatment-19.md").write_text("\n".join(md))
    print(json.dumps({"staticSourceBindings": len(rows), "productRuns": 0}))


if __name__ == "__main__":
    main()
