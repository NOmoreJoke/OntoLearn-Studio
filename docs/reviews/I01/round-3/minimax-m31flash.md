# I01 Round 3 独立对抗审查报告（MiniMax M3.1-Flash）

任务标识：`I01-R3-MiniMax-M31Flash-20261020-0643`
迭代：I01 / S1 / ADR-0002 —— 源真相、隔离场景、不可变历史与可重建派生视图的存储及失效 spike
受审范围：`e628f5e7b6c09e10e15644552a6171c4a9a3072e` → `1e3b179de1e1f9f7ad4b6556f292ef769c113d18`

---

## 0. 结论

**通过。**

- **阻断问题 0 项**。S1 退出门槛 1–6 全部在本候选上被独立验证成立；D.2 九行正反例、G-base/G-map-empty/G-behavior/E.5 的实测范围与未执行项区分、SQLite 单事务提交边界与故障矩阵、隔离场景轮次、不可变历史与缓存回收、两档独立命名空间合成负载、真实 RDFLib 基础打包与包内同样例回归，均达到本轮冻结范围要求的证据强度。
- **本轮新发现问题 6 项，全部为「低」**：F3-01～F3-05 为本轮首次提出的实现/文档精度问题；F3-06 为已登记延期到 I03 的粒度约束复述。**无一项违反 I01 冻结范围的任何一条退出门槛，无数据损坏、无安全缺陷、无既有链路回归**，故均不构成阻断。
- **历史 29 条编号意见（F-01…F-11、R1…R6、N1…N2、M-01/M-02、N-01…N-08）逐项重新判断**：**22 条已关闭**，**6 条为已明确登记、允许延期的项**（R4 剩余锁错误、R6、N-03、N-04、N-06、N-07），**1 条为确认项**（N-08，断言仍成立，无需处理）。**没有任何一条历史意见被"沿用旧版通过"，也没有把任一未关闭项当作已关闭。** 所有延期项均已写入 ADR-0002 或 `acceptance.md`，不违反任何退出门槛，且都被明确指向 I03/I04 或 Q5/真实负载。
- **本轮不采信任何开发者声明或内部 agent 结论**。第 4 节的每一条、第五节每一条关闭判断，均由我在本候选 HEAD 上重新读取代码并执行自己的探针/命令得到；`docs/reviews/I01/internal-review.md` 仅作线索阅读，不构成本报告任何判断依据。
- 按 `scope.md` 统一门禁第 4/5 条：本报告为独立一轮双审中的一方；本轮新发现的 6 项低等问题**建议在下一候选中修复**（涉及实现/测试/文档变更即须新候选、双方重新审），**不影响本轮通过结论**。

---

## 1. 评审任务、模型与思考设置的来源记录

| 项目 | 值 | 来源性质（严格区分） |
|---|---|---|
| 任务标识 | `I01-R3-MiniMax-M31Flash-20261020-0643` | **派发方（开发会话）声明**，登记为流程参数。 |
| 模型 | MiniMax M3.1-Flash | **独立可观测**：本会话运行时自报 `Model: MiniMax-M3.1-Flash`、`agentName: mavis`。派发方另声明经 MiniMax Code 侧栏核验显示 `M3.1-Flash`、分支 `feature/I01-storage-invalidation`。两者一致。 |
| 思考设置 | xhigh | **纯来源记录**。派发方声明 UI 显示 xhigh。我无法从会话内独立观测 UI 档位，本轮**未使用 computer use** 复核 UI 界面。该声明**不作为任何通过依据**。 |
| 项目目录绑定 | `/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio` | **独立可观测**：本会话 cwd 即该路径，且我在其下成功执行 git / npm / uv / PyInstaller 全部验证。 |
| 分支 | `feature/I01-storage-invalidation` | **独立可观测**：`git branch --show-current` 实测一致。 |
| 与另一模型互不披露 | 声称 | 本轮撰写报告时 `docs/reviews/I01/round-3/` 仅含 `frozen-source-check.txt`；我**只列出目录名**，未打开任何其他模型的 round-3 报告或结论。历史轮（round-1、round-2）原始报告与 `processing.md` 按任务要求读取。 |
| 内部 agent 复核 | `docs/reviews/I01/internal-review.md` | 仅作线索；**其结论不构成本报告任何判断的依据**。 |
| 独立 agent 复核 | — | **本轮未委托任何内部子 agent 复核**，第 4/5/6 节全部由我本人执行。 |

**独立性声明**：本报告全部结论基于我直接读取的代码与需求原文，以及我本轮亲自执行的验证命令与对抗探针（脚本全部在 `/tmp/i01-r3-probe/`，产物全部在 `/tmp/i01-r3-verify/`）。

---

## 2. 项目路径、分支、base/head 与工作区边界

- 项目绝对路径：`/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio`（实测 cwd 一致）
- 分支：`feature/I01-storage-invalidation`（实测）
- base：`e628f5e7b6c09e10e15644552a6171c4a9a3072e`（实测可解析）
- head：`1e3b179de1e1f9f7ad4b6556f292ef769c113d18`（`git rev-parse HEAD` 实测，与派发候选一致）
- 固定范围 **3 个提交**：`6d8e4b3 feat(I01): spike transactional storage and dependency invalidation`、`3e787fb fix(I01): harden publication, recovery and platform boundaries`、`1e3b179 fix(I01): validate replay inputs and locate reserved ownership conflicts`；**91 个文件，+9369 / −2**（`git diff --stat base..head` 实测）。
- 远端状态：`origin/develop` 仍停在 base `e628f5e`；`feature/I01-storage-invalidation` **无上游、无 push、无 PR、无 merge**（`git branch -vv`、`git log origin/develop` 实测；`docs/reviews/I01/status.md` 同载）。符合"双审前不 push"。
- **工作区边界（实测）**：`git status --porcelain` 共 11 项，与我开工时**完全一致**——7 项已修改的既有文件（`design/prototypes/…pen`、`docs/README.md`、`docs/architecture/0001-desktop-framework.md`、`docs/development.md`、`docs/m0-checklist.md`、`docs/reviews/I01/status.md`、`docs/source-manifest.json`）+ 4 项未跟踪流程文档目录/文件。
- `docs/iterations/I01/preexisting-files.json` 登记的 **61 项既有文件，我逐项重算 SHA-256：61/61 一致，0 缺失、0 不匹配**。
- **我未修改、未暂存、未还原、未清理任何仓库文件**；未 stage 任何内容；未新增/覆盖任何实现、测试、配置、依赖或验收文档。独立打包产物写入 `build/`（`.gitignore:12` 已忽略）与 `/tmp/i01-r3-verify/`；**未触碰 `release/`，未覆盖 `docs/iterations/I01/evidence/` 下任何归档证据**。本报告是本轮唯一新增的仓库文件。

---

## 3. 检查范围、命令与实际结果、未验证事项

### 3.1 需求依据（逐条读取原文，未依赖开发者摘要）

- `AGENTS.md`（10 条开发规则全文）
- `docs/iterations/I01/inputs/scope.md`：I01 冻结范围表格行、顺序清单、统一门禁第 1–8 条、非目标与未决边界
- `docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md`：**S1 全章**（存储责任表、三类版本区分、交付定义、**S1 退出门槛 1–6 全文**）
- `docs/iterations/I01/inputs/goal-objective.md`、`inputs/M0深度审查_采纳评估_2026-10-19.md`、`inputs/sources.json`
- `docs/prd/PRD-本体学习与落地Agent工作台.md` V0.6：**FR-006 / FR-304 / FR-604 / FR-700～705 / FR-804 / FR-1000**；**附录 C（能力矩阵）、附录 D D.1/D.2、附录 E E.1～E.5、附录 G G.0～G.6**（含 G-base / G-map-empty / G-behavior 固定基线与 G.1～G.6 用例表）
- `docs/iterations/I01/ADR-0002-storage.md`、`docs/iterations/I01/acceptance.md` —— **作为被审对象，不作为通过依据**
- `docs/reviews/I01/round-1/`、`round-2/` 两模型原始报告及各 `processing.md`（历史意见来源）
- `docs/reviews/I01/status.md`、`internal-review.md`、`frozen-source-check.txt`、round-3 `frozen-source-check.txt`

### 3.2 实现检查范围

`packages/engine/src/ontolearn_engine/`：`storage.py`（1068 行，全文逐行）、`invalidation.py`、`invalidation-v2.json`、`rdf_snapshot.py`、`storage_probe.py`；`packages/engine/tests/`：`test_storage.py`（1294 行，全文）、`storage_baselines.py`（220 行，全文）、`test_protocol.py`（未改动）；`packages/engine/entrypoint.py`、`pyproject.toml`、`uv.lock`；`scripts/build-engine.mjs`、`scripts/verify-i01.py`、`.prettierignore`、`.gitignore`；根 `package.json`；`docs/iterations/I01/evidence/round-3/` 全部 22 个文件。

### 3.3 验证命令与实际结果（均为我本轮亲自执行）

| # | 命令 | 实际结果 |
|---|---|---|
| V1 | `git rev-parse HEAD` / `--abbrev-ref HEAD` / `rev-parse --show-toplevel` | `1e3b179de1e1f9f7ad4b6556f292ef769c113d18` / `feature/I01-storage-invalidation` / 目标绝对路径 ✅ 与派发候选一致 |
| V2 | `git diff --stat e628f5e..1e3b179` | 91 文件，+9369 / −2，3 提交 ✅ |
| V3 | `npm run check` | **EXIT=0**：eslint 0 warn、prettier 通过、tsc 通过、vitest 通过、electron-vite 构建成功、ruff check 通过、ruff format 53 文件已格式化、**pytest 198 passed in 5.73s**（test_protocol 11 + test_storage 187）✅ 与 `evidence/round-3/check.txt` 记载的 198 项一致 |
| V4 | `npm run verify:sources` | **EXIT=0**，"已核对 13 个归档源文件" ✅ 与 `evidence/round-3/verify-sources.txt` 一致 |
| V5 | `npm run test:e2e` | **EXIT=0**，1 passed（桌面真实引擎 health + 隔离 + 最小窗口）✅ 与 `evidence/round-3/e2e.txt` 一致 |
| V6 | `uv run --frozen python scripts/verify-i01.py --packaged "release/mac-arm64/…/engine/ontolearn-engine" --output /tmp/i01-r3-verify` | **EXIT=0**：`{"measurements": 12, "health": "ok", licenses: rdflib 7.6.0 BSD-3-Clause / pyparsing 3.3.3 MIT, "bytes": 25123766}` ✅ **独立复现 12 条开发/包内测量** |
| V7 | 归档 `evidence/round-3/` 13 个 JSON + manifest ↔ 我独立运行 `/tmp/i01-r3-verify/` 逐字段比对 | `inputSha256`/`querySha256`/`result`/`expected`/`snapshotId`/`triples`/`scale`/`trial`/`seed`/`device`/`rdflib`/`sqlite`/`python` **全部一致**；manifest 的 `executableSha256`/`engineDirectoryBytes`/`fileCount`/`uvLockSha256`/`health`/`licenses`/`host`/`machine` **全部 MATCH** ✅ 归档证据真实可复现 |
| V8 | `npm run engine:build`（独立重建 PyInstaller，输出至已忽略的 `build/`） | **EXIT=0**，"Build complete!"；重建产物 **154 文件 / 25,123,766 字节**，与归档 manifest 的 `fileCount`/`engineDirectoryBytes` **完全一致** ✅ |
| V9 | 重建产物可执行文件 SHA-256 | `bbcfdc3c7a0b98bcd7e5c8013d51f90a99a2510180bddd316a7b711b7736ac86` —— 与归档 `package-manifest.json` 登记值**逐位一致** ✅ |
| V10 | 重建包内探针（`PATH=/usr/bin:/bin`，剔除 `PYTHONPATH`/`PYTHONHOME`）`--storage-probe --scale 10 --trial 9` | `triples=180`、`inputSha256=25393c99db27…`、`querySha256=7879b25f2833…`、完整结果与 expected 10 项逐条相等、`rdflib=7.6.0`、`rssAvailable=true`；与归档 `packaged-10x-0.json` 关键字段**完全一致** ✅ **包内同样例回归成立** |
| V11 | 重建包内 health（同一受限环境） | `{"ok":true,"capabilities":["health"]}` ✅ 仅声明 health，未虚增能力 |
| V12 | 重建包内资源 | `ontolearn_engine/invalidation-v2.json`、`rdflib-7.6.0.dist-info/LICENSE`、`pyparsing-3.3.3.dist-info/licenses/LICENSE` 均实际入包 ✅ 机器可读规则随包分发，不依赖仓库相对路径 |
| V13 | `uv.lock` 核对 | `rdflib==7.6.0`（`requires-dist` 精确钉住）、`pyparsing==3.3.3` 带 sdist/wheel 哈希 ✅ 真实 RDFLib 依赖已锁 |
| V14 | 61 项既有文件 SHA-256 复算 | **61/61 一致**，0 缺失、0 不匹配 ✅ |
| V15 | 独立对抗探针 **5 组 26 例**（`/tmp/i01-r3-probe/p1.py`…`p5.py`） | 见第 4/5/6 节各项证据；**F3-01、F3-02、F3-03、F3-04、F3-05、F3-06 均被独立复现**；历史 F-01/F-08/F-09/R3/M-01/N-01/N-02/N-08/ZCode N1 逐条复现 |
| V16 | RDF/Turtle 注入与 IRI 合法性探针（`p4.py`，10 个对象词法 + 7 个 IRI） | `@prefix evil: <http://x/> .`、多语句注入 `"x" . <urn:s> <urn:p> "y"`、`_:blank`、嵌套三元组 **全部被拒**；相对 IRI、含空白/`|`/`"`/`<>`/`>` 的 IRI **全部被拒**；`"x"^^<xsd:string>`、`"""alias"""` 可解析但 `n3() != 原值` → 存储层以 "Canonical RDF object required" 拒绝 ✅ 无解析放大、无远程引用、无插件发现 |

### 3.4 未验证事项（如实声明，不作推断）

1. **Windows CI 实际运行**：本机为 macOS arm64，无 Windows 主机。F-02 的修复我以源码审查 + 仓库自带子进程回归（`test_missing_unix_probe_module_cannot_break_health_or_measurement`，拦截 `resource` 与 `ontolearn_engine.storage_probe` 两种情形并执行 health）确认逻辑闭合，**但未在 Windows 上实跑 CI**。`windows-latest` 腿仍待 PR 后核验——**本报告不冒称已实跑**。
2. **Linux 打包产物与跨平台动态链接**：未验证（仅有 macOS arm64 的 `otool -L` 清单）。
3. **干净设备、无系统 Python、断网安装、签名与安装**：未验证。归档 `package-manifest.json` 的 `scope` 字段与 `acceptance.md:58` 均如实写明"no clean-device/install/signing claim"，本报告重申该边界。
4. **完整业务执行器**：CSV 导入/预览 UI、行为触发与条件冻结、资源阶段、E.2 轮次执行器、SHACL、RDFS/规则组合、解释 UI **均未实现**。本报告不把存储替身视为完整业务基线，`acceptance.md:40-52` 的"完整业务验收状态"列已逐项标为未执行/未通过。
5. **100× 合成档**：计划标注"按资源余量选做"，本候选只做 1×/10× 两档，证据如实只含 12 条。
6. **Q5 容量线**：未定。本候选未自设任何容量通过线，测量仅为原始记录；两档样本极小，**不可外推容量**。
7. **I05 语义**：SHACL、RDFS/规则组合、远程 `SERVICE`/`FROM` 拒绝矩阵、解释边界均未执行。
8. **正式业务签名/干净设备/首发平台**：不在本迭代范围，不得视为通过。
9. **`npm run package:dir`（含 electron-builder 的 `release/` 产出）未由我完整重跑**：为避免覆盖归档证据所指向的 `release/` 产物，我改为独立执行 `npm run engine:build`（PyInstaller 阶段，输出至已忽略的 `build/`）并对**重建产物**做包内探针/health/许可证/资源核验；重建产物与归档 `release/` 产物的可执行文件 SHA-256、文件数、字节数三项逐位一致，间接证明 `release/` 产物确由同一 HEAD 的同一构建产生。electron-builder 的 `package:dir` 阶段本身未由我重跑。

---

## 4. 本轮问题清单

严重程度定义：**阻断** = 违反 I01 冻结范围 / S1 退出门槛 / PRD 主定义，或造成数据损坏、安全缺陷、既有链路回归；**中** = 实现与自身文档声明不符，或存在无护栏的语义缺口，可能误导下游；**低** = 边界语义、文档精度或错误面问题，不影响本轮验收结论。

本轮共 **6 项：0 阻断、0 中、6 低**。全部给出处理结论。

---

### F3-01 ［低］`publish` 不校验 `kind`，`NULL` 进入 `current_results` 主键可产生重复当前指针且结果不可寻址

- **位置**：`packages/engine/src/ontolearn_engine/storage.py:735-805`（`publish`）——`implementation` 在 `:745-751` 有严格形状守卫，`dependencies` 在 `:754-773` 有解析守卫，而 **`kind` 全程无任何校验**；`current_results` 主键定义见 `:1052-1053`（v1 表）与 `:116-120`（v2 迁移表）。
- **触发条件**：`publish(project, snapshot, deps, None, payload, IMPL)`（`kind=None`）；`kind` 为业务结果定义身份（`ADR-0002-storage.md:9` 原文："`kind` 是业务结果定义身份（例如 `query:Q1:asserted`）"）。
- **影响**：
  - SQLite 的 UNIQUE 索引把 `NULL` 视为互不相等，因此 `(project, kind=NULL, implementation)` 主键**不阻止重复行**：实测可写入 **2 条** `kind IS NULL` 的 `current_results` 行。
  - 指针随之不可寻址：`current(project, kind, implementation)` 以 `WHERE kind=?` 传 `None` 恒不匹配 → 实测返回 `None`。已发布结果静默地既不能被"当前"读取，也不能被后续同 `kind` 发布覆盖。
  - 事务仍正确提交，故不产生正式数据损坏；影响限于派生视图指针的可寻址性与唯一性。
  - 与同函数内 `implementation` 的严格校验形成不对称：同一入口对"来源身份"要求完整非空字符串，对"结果身份"完全不要求。
- **证据**（我本轮独立探针 `/tmp/i01-r3-probe/p1.py` P3、`p2.py` NEW-A）：
  ```
  ### P3 publish with kind=None
    -> {'result_id': 'ea8ff64b-…', 'rows': [(None, '{"dependencyLockHash":"c",…}')],
         'current_lookup': None}
  ### NEW-A publish with kind=None allows multiple NULL-key rows
    -> {'results_with_null_kind': 2, 'current_rows_null_kind': 2, 'current_lookup_returns': None}
  ```
- **修复建议**：在 `publish` 入口按 `implementation` 同等强度校验 `kind` 为非空字符串（建议同时拒绝 `""`），失败抛 `ValueError` 并保持零写入；补一条回归（`kind=None` / `""` → `ValueError`，`results` 与 `current_results` 计数不变）。
- **处理结论**：**不阻断，建议在下一候选修复**。触发路径需要调用方传入非法 `kind`，当前无任何业务能力调用 `publish`（正式能力仍仅 health），不构成产品可达缺陷，也不违反 S1 退出门槛；但它是"存储层形状守卫不对称"的实际缺口，与本轮 ZCode N1 / MiniMax N-01 同族（同一入口的输入守卫），建议与 F3-02 一并收口。

---

### F3-02 ［低］`commit_round` 对非对象的历史 `config` 抛裸 `AttributeError`，越出 ADR-0002 已登记的错误面

- **位置**：`storage.py:936`：`maximum = json.loads(record["config"]).get("maxRounds")`；对照 `storage.py:1003-1006`（`_history` 显式 `isinstance(config, dict)` 检查并置 `replayable=False`）与 `storage.py:884`（`start_run` 的 `isinstance(config, dict)` 守卫）。
- **触发条件**：`runs` 表中 `config` 列不是 JSON 对象的行（实测以 `json.dumps(None)` 写入即触发）。这类行是**本仓库自身测试用于模拟历史遗留状态的既有做法**（`test_legacy_nonobject_run_configuration_is_not_claimed_replayability` 直接 `INSERT INTO runs … json.dumps(None)`），故不是纯理论状态。
- **影响**：
  - `AttributeError` 不在 `ADR-0002-storage.md:57` 登记的错误面内（该处登记："`Conflict` 表示基线/所有权/轮次身份冲突，`ValueError` 表示存储形状错误，`KeyError` 表示读取身份缺失"）。
  - 同一"非对象 config"在 `history()` 路径被识别为形状缺失并如实标 `replayable=False`，在 `commit_round` 路径却以未归一异常崩溃——**同一输入属性在两条路径上行为不一致**。
  - 异常发生在 `_transaction` 内 → 事务正确回滚，**无数据损坏**；但 I03/I04 若按 ADR 登记的错误面做映射，`AttributeError` 会作为未归一的内部错误逃逸。
- **证据**（我本轮独立探针 `/tmp/i01-r3-probe/p1.py` P2）：
  ```
  ### P2 commit_round with non-object legacy config
    -> RAISED builtins.AttributeError: 'NoneType' object has no attribute 'get'
         maximum = json.loads(record["config"]).get("maxRounds")
  ```
- **修复建议**：在 `commit_round` 读取 `maxRounds` 前加 `config = json.loads(record["config"])`，非 dict 则抛 `ValueError`（与 `start_run` 守卫对称）；补一条回归。
- **处理结论**：**不阻断，建议在下一候选修复**。不违反任何退出门槛、不造成数据损坏。但它使 `ADR-0002-storage.md:57` 的错误面登记**不再完整**，应在下一版 ADR 补记或直接以本修复收口。

---

### F3-03 ［低］`collect_cache()` 无项目作用域，会跨项目清空其他项目的派生载荷

- **位置**：`storage.py:869-881`（`collect_cache`）——`SELECT id FROM results WHERE id NOT IN (…) AND id NOT IN (…) AND payload IS NOT NULL` **没有任何 `project` 过滤**；对比 `publish`/`current`/`start_run` 等均以 `project` 为第一作用域。
- **触发条件**：任意一次 `collect_cache()` 调用。
- **影响**：
  - 实测：项目 `q` 的一条已发布结果载荷，在对另一项目调用 `collect_cache()` 后被置为 `None`。
  - 影响边界是**可重建派生载荷**：条目、`stale` 原因、`dependencies` 与输入快照均保留（`ADR-0002-storage.md:41` 与 N-04 的既有结论），正式数据/历史/定义不受损。
  - 真实风险有两点：① API 无法表达"只清理本项目的缓存"，在多项目桌面应用中清理半径大于调用方意图；② 顺序敏感——`pin_result` 在载荷被清空后会抛 `ValueError("Cannot save report with evicted payload")`，即"先清理、后保存报告"会失败（先保存则正常）。
- **证据**（我本轮独立探针 `/tmp/i01-r3-probe/p1.py` P9）：
  ```
  ### P9 collect_cache() crosses project boundaries
    -> {'collected': ['8843c36e-…'], 'q_result_payload': None}
  ```
- **修复建议**：为 `collect_cache` 增加可选 `project` 参数并在无参时保留全局语义（或显式改名为 `collect_cache_all`）；同时在 `acceptance.md` 的"缓存回收安全"一栏补一句"清理为全库作用域，且须先固定报告再清理"。
- **处理结论**：**不阻断**。既有 N-04 已被允许延期且 ADR:41 已声明"过期而未固定的派生载荷也可被回收"；本条是其**作用域维度**的补充观察，属文档/接口精度问题，不违反 S1 退出门槛 3（"缓存清理不损坏历史、保存的定义和正式数据"成立）。

---

### F3-04 ［低］`remove()` 使受管事实的人工改值在活动状态中消失，仅存于 `commit_evidence` 前置快照，ADR 未记载

- **位置**：`storage.py:280-298`（`remove` 循环：对受管事实执行 `UPDATE facts SET object=NULL` 形成墓碑，不校验 `object != managed_value`）；对照 `storage.py:512-518`（`_replace_mapping` 的 "Manual drift" 检查会拒绝带漂移的重跑）。
- **触发条件**：先 `edits` 把受管事实改成人工值，再 `remove` 该事实。
- **影响**：
  - 实测：墓碑化后活动状态中 `object=None`，人工值 `'"人工值"'` **从活动事实集中消失**。ADR 记载的恢复路径是 `edits={factId:managed_value}`——恢复的是**受管值**，人工值不在恢复路径上。
  - **不是数据丢失**：人工值仍完整保存在该次提交的 `commit_evidence.before_snapshot` 中（实测 `human_value_in_before_snapshot: '"人工值"'`，`recoverable_from_evidence: True`），符合 `ADR-0002-storage.md:21` "commits / commit_evidence … 同事务前后快照作为 Diff/撤销依据"。
  - 真实缺口在**文档精度**：`ADR-0002-storage.md:27` 说明了 `edits` 后 ID 与当前值摘要解耦，但**未说明**"`remove` 对带漂移的受管事实会丢弃人工值，人工值只能从提交前置快照追溯"。下游若据此实现撤销 UI，可能误认为人工值可直接恢复。
- **证据**（我本轮独立探针 `/tmp/i01-r3-probe/p1.py` P1 与 `p3.py` NEW-H）：
  ```
  ### P1 remove() after manual edit of a MANAGED fact
    -> {'facts': [{… 'object': None, 'owner': 'M1', 'source_row': '001', 'managed_value': '"泵站A"'}],
         'human_value_survives': False}
  ### NEW-H human value recoverable via commit_evidence before_snapshot
    -> {'live_object': None, 'human_value_in_before_snapshot': '"人工值"',
         'recoverable_from_evidence': True}
  ```
- **修复建议**：在 `ADR-0002-storage.md:27` 补一句："对带人工漂移的受管事实执行 `remove` 会将其墓碑化并丢弃当前人工值；该人工值保留在同事务提交的 `commit_evidence.before_snapshot` 中，可追溯但非一等恢复入口。"；若产品需要一等恢复，应在 I01 后续或 FR-804 撤销契约中明确以 `edits` 显式恢复。
- **处理结论**：**不阻断，建议以文档方式在下一候选补记**。无数据损坏，人工值可追溯；属 M-02 同族的"文档表述未覆盖真实语义"问题，但影响面小、无误导下游的实现后果。

---

### F3-05 ［低］ChangeSet 计划内部无序语义未定义：`remove` 与 `edits` 同批作用于同一 id 时恒为"恢复"

- **位置**：`storage.py:280-298`（`remove`）**无条件先于** `storage.py:299-317`（`edits`）执行，与调用方在计划字典中书写的先后无关。
- **触发条件**：`commit(..., remove=[X], edits={X: v})`。
- **影响**：
  - 实测与仓库测试 `test_managed_delete_restore_in_same_plan_preserves_mapping_dependency_version` 一致锁定为"**先删后改 = 恢复为 v**"。
  - 调用方**无法表达**"先改值再删除该事实"（自然的净效果应为删除）。当前唯一使用场景恰好是 ADR 记载的恢复路径（`edits={factId:managed_value}` 显式放弃人工值或人工删除），故现状安全。
  - 真实缺口是**契约空白**：计划是 `{definitions, manual, edits, remove, mapping}` 五个并列集合，实现内部有固定顺序而文档未声明，I03/I04 若基于该 API 构造更复杂的 ChangeSet，容易按"字典书写顺序即执行顺序"理解而得到相反结果。
- **证据**：`storage.py:280-317`（代码顺序即证据）；`packages/engine/tests/test_storage.py:957-977` 锁定当前语义为"恢复"。
- **修复建议**：在 `ADR-0002-storage.md` 的"最小格式 v2 与接口"或"决定及边界"段显式写明计划内部执行序（`definitions → remove → edits → manual → mapping`），并声明 `remove`+`edits` 同批同 id 的净效果为"恢复"；或在 I03 契约中禁止同批出现同 id。
- **处理结论**：**不阻断**。现状行为与既有 ADR 恢复路径一致，无数据损坏；属接口契约空白，建议在下一候选以文档方式补记（与 F3-04 同批处理成本极低）。

---

### F3-06 ［低·已登记延期复述］`facts` 依赖只有项目级粒度，存储层无法表达更细的断言事实范围

- **位置**：`storage.py:756-773`（`publish` 的依赖解析）、`invalidation.py:19-28`（`reasons`）、`invalidation-v2.json`（`facts` 族仅 `staleReason` 一项，无粒度定义）。
- **触发条件**：调用方需要把结果范围绑定到具体主语/子集（例如只依赖 `urn:equipment/001` 的断言）。
- **影响**：实测 `publish(..., ["facts:urn:equipment/001"], ...)` 被拒为 `ValueError: Unresolved snapshot dependency: facts:urn:equipment/001`；`facts` 族也不在 `LAYERS` 内，故无法用定义登记伪造更细的 facts 键（实测 `ValueError: Invalid definition layer/identity`）。结果是**任何订阅 `facts:asserted` 的结果都会被项目内任何无关主语的事实变更置为过期**（实测：新增 `urn:equipment/999` 的无关事实 → 订阅结果 `FACTS_CHANGED`）。PRD D.2 第 2 行的"**相关**当前推导/查询结果"在当前粒度下是项目级粗粒度。
- **既有登记**：`ADR-0002-storage.md:9` 已明文声明"调用服务必须同时记录真实数据范围和全部实际依赖。存储层不猜测遗漏的业务依赖，完整依赖集合由 **I03 能力契约**强制派生"；`acceptance.md:18` 亦载"手工事实使用 `facts:asserted`"。**这正是 Round 2 已接受的边界，不是本候选引入的缺陷**，本轮仅作独立复核并复述其影响面。
- **证据**（我本轮独立探针 `/tmp/i01-r3-probe/p5.py`）：
  ```
  dependencyVector keys: ['facts:asserted']
    ACCEPTED dep 'facts:asserted'
    REJECTED dep 'facts:urn:equipment/001' -> ValueError: Unresolved snapshot dependency
    REJECTED dep 'facts:other'              -> ValueError: Unresolved snapshot dependency
    REJECTED facts-layer definition -> ValueError: Invalid definition layer/identity
    unrelated-subject fact change -> result stale: [{'code': 'FACTS_CHANGED', 'dependency': 'facts:asserted', 'before': 1, 'after': 2}]
  ```
- **修复建议**：无需在 I01 改实现。I03 能力契约落地时，明确"结果的数据范围"与"依赖键"的映射规则，并决定是否引入更细的 facts 作用域键或改为按范围登记的定义级依赖；在 `invalidation-v2.json` 的 `schemaVersion` 升级中同步。
- **处理结论**：**已登记延期至 I03，允许延期，不影响本轮通过**。该边界已由 ADR:9 / acceptance.md:18 明文声明，属 S1 计划所允许的"完整依赖集合由 I03 能力契约强制派生"；本条不构成新缺陷，仅提示 I03 不可沿用"存储层已能表达真实数据范围"的假设。

---

## 5. 历史 29 条编号意见逐项关闭判断

来源：Round 1 MiniMax 报告 11 条（F-01…F-11，2 阻断/4 中/5 低）＋ Round 1 ZCode 报告 6 条（R1…R6，全部 P3）＋ Round 2 ZCode 报告 2 条（N1、N2，P3）＋ Round 2 MiniMax 报告正文 10 条（M-01、M-02 为中；N-01…N-08 为低，其中 N-08 为**确认项**）＝ **29 条**。

**编号口径说明**：Round 2 MiniMax 报告摘要写"共 9 项：0 阻断、3 中、6 低"，与其正文实际编号（M-01、M-02、N-01…N-08 共 **10** 条）不一致；按任务要求，**以正文全部编号处理**，含确认项 N-08，**不杜撰 M-03**。下表逐条列出全部 29 条。

### 5.1 Round 1 MiniMax（F-01…F-11）

| 编号 | 原严重度 | 开发者处理 | **本轮独立判断** | 我本轮的依据 |
|---|---|---|---|---|
| F-01 旧快照迟到覆盖新当前 | 阻断 | 采纳 | **已关闭** | 探针 F-01 复现：`current_is_new=True`、`late_state='historical'`、`late_stale=[]`、`first_stale=[]`；`storage.py:800` 的 `can_publish_current` 仍要求快照 revision == 当前正式 revision。首轮反例不可复现 |
| F-02 Unix `resource` 破坏 Windows | 阻断 | 采纳 | **已关闭（本机模拟层面）** | `storage_probe.py:21-24` 受保护导入，`entrypoint.py:8-12` 惰性导入探针；仓库子进程回归覆盖 `resource` 与 `storage_probe` 两模块且 health 仍返回 `capabilities:["health"]`。**实际 Windows CI 仍未实跑（3.4-1）** |
| F-03 空/未解析依赖永不过期 | 中 | 采纳 | **已关闭** | `publish` 拒绝空依赖集/未登记依赖/非字符串键；`facts:asserted` 作为空项目显式范围保留（`storage.py:758-759`）。仓库 `test_unregistered_or_empty_dependencies_cannot_be_published` 覆盖 5 类 |
| F-04 定义级 IRI/词法未校验 | 中 | 采纳 | **已关闭** | `storage.py:414-440`（`_definition`）+ `:461-474`（`_validate_references`）+ `:452-459`（单值声明冲突）；仓库 `test_invalid_ontology_triples_fail_in_commit_not_later_graph_build` 覆盖 4 类非法三元组并断言同批回滚 |
| F-05 迁移故障注入单点 | 中 | 采纳 | **已关闭** | `storage.py:76-132` 覆盖 11 个 v1→v2 注入点 + 4 个 v0 点；仓库 `test_migration_each_ddl_commit_and_process_exit_is_recoverable` 对 11 点 × (异常, 真实子进程 `os._exit`) 全部断言 DDL/版本/数据回滚或提交后保持 v2、重开可重试；`test_initial_schema_creation_failure_is_atomic_and_retryable` 覆盖 v0 四点 |
| F-06 当前格式开库也取写锁 | 中 | 采纳 | **已关闭** | `storage.py:73-74` 当前格式直接 return 不进事务；`test_current_format_open_does_not_take_writer_lock` 在他方持 `BEGIN IMMEDIATE` 时成功打开读取。**残留**：`snapshot()` 自身仍取写锁 → 即 N-07（已登记延期） |
| F-07 提交后取消拿不到已提交标记 | 低 | 部分采纳 | **已关闭（按其登记语义）** | `ADR-0002-storage.md:31` 明文要求"必须另外通过 `marker(project,operation)` 对账；异常本身不能证明事务未提交"。探针 NEW-B 复现：`after_commit` 抛 `OSError` 后 marker 存在、revision=2、**同 operation/plan/job 重试返回同一 marker 且不重复写入**、前后快照齐备 |
| F-08 墓碑重跑阻断/恢复未文档化 | 低 | 采纳 | **已关闭** | 探针 NEW-F 复现：墓碑后重跑 → `Conflict: Manual drift: mapping=M1, row=001, slot=urn:equipment/001 urn:name`（可定位）；经 `edits={id:managed_value}` 显式恢复后重跑成功、`mapping_status.stale=[]` |
| F-09 单值并集语义/基线字段惰性 | 低 | 采纳 | **已关闭** | `storage.py:442-450`（`_single_predicates` 跨项目 ontology 定义求并集）+ `:452-459`（提交内拒绝与既有事实冲突的新声明）。探针 NEW-G（修正版）复现：两个 ontology 定义各自声明不同谓词时，**同主语同谓词的第二值仍被拒**且 Conflict 可定位；`storage_baselines.py:67` G-behavior 已含真实 `singleValuedPredicates` |
| F-10 实现兼容规则未机器化 | 低 | 采纳 | **已关闭** | `invalidation-v2.json` 含 `implementationCompatibility`（identityKeys/default=isolate/reuse=disabled_in_S1/staleReason=null）与 `publicationPolicy`（staleReason=null）；`storage.py:745` 从该契约读取 identityKeys；仓库仅存 v2，无 v1 残留 |
| F-11 错误面不统一/未知删除 no-op | 低 | 延期并补文档 | **已关闭（按其登记语义）**，但**登记面本轮被打破** | `ADR-0002-storage.md:57` 登记的现状仍成立（未知事实删除为可审计 no-op，可由 `commits.plan` 追溯）。**但本轮新发现两条越出该登记面的错误形态**：F3-02（`AttributeError`）与 F3-01（`kind` 未校验导致静默不可寻址）。二者不改变 F-11 自身的关闭判断，但**下一版 ADR 必须补充登记**，否则 F-11 的"已关闭"是脆弱的 |

### 5.2 Round 1 ZCode（R1…R6）

| 编号 | 原严重度 | 开发者处理 | **本轮独立判断** | 我本轮的依据 |
|---|---|---|---|---|
| R1 operation/job 类型校验 | P3 | 采纳 | **已关闭** | `storage.py:226-229`（`type(base) is not int` 拒 bool、operation/job 非空字符串）；`test_operation_and_job_identity_types_are_checked_before_write` 覆盖 `12345/True/None/""` |
| R2 轮次重试及跨运行复用 | P3 | 采纳 | **已关闭** | `storage.py:919-930` 按 operation 查既有轮次，同 run/number/job/内容返回原快照，异内容或跨 run 抛 `Conflict`；`test_round_retry_after_ack_loss_is_idempotent_and_cross_run_reuse_is_conflict` 覆盖响应丢失后幂等重试、跨运行、内容不符、终态后只返回既有证据 |
| R3 净零事实过度失效 | P3 | 采纳 | **已关闭** | 探针 NEW-L 复现：完全相同映射重跑后向量 `{facts:asserted:1, mapping:M1:1, rule:risk:1}` **完全不变**；真实源变更后 `mapping:M1` 推进到 2 且 `mapping_status.stale=[MAPPING_INPUT_CHANGED]`。仓库另有重复墓碑与同批净零回归 |
| R4 迁移 TOCTOU 及锁错误 | P3 | 部分采纳 | **TOCTOU 已关闭 / 锁错误部分允许延期** | TOCTOU：`storage.py:77-83` 在写锁内重读版本，`test_concurrent_migration_rereads_version_after_lock` 交错回归。剩余"写锁竞争抛裸 `OperationalError`"按其登记延期至 I03/I04 错误映射，与 N-07 同一延期项。**延期不构成通过障碍** |
| R5 映射循环重复查询/JSON 解析 | P3 | 采纳 | **已关闭** | `storage.py:519-528` 循环外预取 `own_ids` 与 `single_predicates`，槽位集合复用 `staged_slots`；文档未作倍数或时延承诺，与处理声明一致 |
| R6 全量快照增长 | P3 | 延期 | **允许延期** | `ADR-0002-storage.md:59` 明文登记为"正确性优先的 spike 选择…Q5 未定，不宣布容量达标"。本轮复核确认 `commit` 仍只写前后两个内容寻址快照，**该权衡未被突破**；不违反任何退出门槛（门槛 6 允许"如实记录"，并要求"不以存储模拟替代完整 M0 基线"——本候选已如实区分） |

### 5.3 Round 2 ZCode（N1、N2）

| 编号 | 原严重度 | 开发者处理 | **本轮独立判断** | 我本轮的依据 |
|---|---|---|---|---|
| N1 `publish` 非 dict `implementation` 抛裸 TypeError | P3 | 采纳 | **已关闭** | 探针 NEW-E 复现：`None`/`[]`/`42`/`"engine"` 四类输入**全部 `ValueError`**，且 `results_written=0`（零写入）。`storage.py:745-751` 前置守卫 |
| N2 轮次快照误用于 `publish` 抛裸 KeyError | P3 | 采纳 | **已关闭** | 探针 NEW-D 复现：`start_run` 与 `publish` 均抛 `ValueError: Project state snapshot required`；`storage.py:619-644`（`_project_snapshot`）为共用校验入口 |

### 5.4 Round 2 MiniMax（M-01、M-02、N-01…N-08）

| 编号 | 原严重度 | 开发者处理 | **本轮独立判断** | 我本轮的依据 |
|---|---|---|---|---|
| M-01 墓碑/`edits` 后第二来源撞保留事实 ID | 中 | 采纳 | **已关闭** | `storage.py:488`（`reserved_id = digest([subject,predicate,value])`）与 `:493-496` 的 `row["id"] == reserved_id` 判定不再被 `object IS NULL` 跳过。探针 P5/P6 复现两条路径均得**可定位 Conflict**：`slot=urn:equipment/001 urn:name, other=M1, row=001, id=b9fe8e1b…`；探针 P7 复现**不同多值仍可共存**（`M2 '"另一值"'` 与 `M1` 墓碑并存），未把墓碑当成整槽排他锁；探针 NEW-G 复现单值谓词下仍可定位 |
| M-02 验收/ADR 表述超出实际实现 | 中 | 采纳 | **已关闭** | 逐条核对：① `acceptance.md:44` 已改为"真实固定 SELECT **仅作用于独立 G-base 结构合成孪生**…存储 G-base fixture 的 JSON/urn:type 描述**未经该查询或 RDF 语义验证**"，`ADR-0002-storage.md:66` 补充"两者身份不混用"；② "缺失或格式不完整输入不标为可重放" 已由 `_project_snapshot` 实际实现，探针 NEW-D 复现遗留不合格运行 `replayable=False`；③ `ADR-0002-storage.md:27` 已补"编辑后 ID 仍是初始内容摘要，不再等于当前值摘要；墓碑同样保留初始 ID"；④ `ADR-0002-storage.md:56` 已覆盖输入快照形状；⑤ `:39`/`:64`/`:68` 三条我独立复现均成立。**本轮仍另发现 F3-01…F3-05 五处新的表述/实现精度缺口**，与 M-02 原列条目不重叠 |
| N-01 `publish` 以轮次快照为输入抛裸 KeyError | 低 | 采纳 | **已关闭** | 同 N2，探针 NEW-D 复现 `ValueError` |
| N-02 `start_run` 接受轮次快照且 `replayable=True` | 低 | 采纳 | **已关闭** | `storage.py:619-644` + `:646-733`（`_snapshot_state` 逐记录校验定义/JSON/引用/事实与 owner-源行-基线/mappingState 及版本原因）；探针 NEW-D 复现遗留 run `replayable=False`；仓库另有 9 组输入形状 + 13 组不完整记录 + 6 组 mappingState 形状回归 |
| N-03 严格 revision 资格可能没有 current | 低 | 部分采纳 | **允许延期（已文档化）** | `ADR-0002-storage.md:39` 明文"该保守发布策略比仅复验领域依赖更严…该 kind 可能暂时没有 current；必须基于新正式快照再发布"；`acceptance.md:64`/`:80` 同载。**该策略不违反 PRD D.1**（D.1 是"可作为当前结果使用"的定义，未禁止更严），且 F-01 的修复正依赖这一严格性。属**语义选择**而非缺陷；I03 能力契约须知晓。**允许延期至 I03，不影响通过** |
| N-04 未固定 stale 派生载荷可被回收 | 低 | 部分采纳 | **允许延期（已文档化）** | `ADR-0002-storage.md:41` 明文"过期而未固定的派生载荷也可被回收，条目、原因、依赖与输入保留，不能承诺过期载荷无限期直接查看"；`acceptance.md:11` 同步。探针 N-08 复现：pinned 载荷保留、历史轮次与 `committedProgress` 不受影响。**本轮补充 F3-03（作用域维度）**。**允许延期，不影响通过** |
| N-05 固定 CSV 两行集合未入测试 | 低 | 采纳 | **已关闭** | `test_g_map_empty_fixed_two_row_prepared_collection_is_exact_and_repeatable` 以固定两行（`001/泵站A`、`002/泵站B`）构造 prepared mapping，断言**恰好 4 条类型/名称事实**、owner=`fixed-csv`、source_row 分别为 `001`/`002`、**重复提交集合与依赖向量均不变**。CSV 解析/预览业务仍未实现，`acceptance.md:79` 如实标注 |
| N-06 重复 `finish_run` 抛裸 IntegrityError | 低 | 延期 | **允许延期** | 行为未变（`run_terminal` 主键 + 不可变触发器）；`ADR-0002-storage.md:57` 已登记"重复 pin/终态插入可抛唯一性错误"。属 F-11 同族，**明确指向 I03/I04 受限错误映射**；事务回滚正确，不阻断 |
| N-07 `snapshot()` 持写锁、竞争抛裸 OperationalError | 低 | 延期 | **允许延期** | 行为未变（探针 NEW-C 复现：另一连接持写锁时第二写者 5 秒后 `OperationalError: database is locked`）。`snapshot` 需写事务以持久化内容寻址证据，改读事务会掩盖写入；按 R4/F-11 留 I03/I04 统一映射与协调器排队/超时。**允许延期，不影响通过** |
| N-08 pin/current/历史缓存安全（**确认项**） | 低 | 无需改动 | **仍然成立，无需处理** | 探针 N-08 复现：pinned 载荷 `['pinned']` 保留；`history()` 轮次数与 `committedProgress` 在 `collect_cache()` 后不变；`acceptance.md:11`"固定报告和历史轮次在缓存回收后完整"**断言成立**。建议下游勿"修复" |

### 5.5 汇总

- **29 条中 22 条已关闭，6 条属已登记且允许延期的项**（R4 剩余锁错误部分、R6、N-03、N-04、N-06、N-07），**1 条为确认项**（N-08，断言仍成立、无需处理）。其中 F-07 与 F-11 属"按其自身登记语义关闭"——F-11 的登记面本轮被 F3-01/F3-02 打破，下一版 ADR 必须补充登记，否则其关闭是脆弱的。
- **首轮两项阻断（F-01、F-02）均已关闭**，我以独立探针在首轮原始反例路径上未复现任何等价缺陷。
- **没有任何一条历史意见被"沿用旧版通过"**：上表 29 行的判断全部基于本候选 HEAD（`1e3b179`）的代码与本轮实测。
- **所有延期项均已写入 `ADR-0002-storage.md` 或 `acceptance.md`，均不违反 I01 冻结范围的任何一条退出门槛**（门槛 6 明确"重放输入缺失时如实标识"——本候选对依赖、配置、**输入快照形状**三类缺失均如实标识为 false/拒绝）。
- 延期项指向明确：F-07/F-11/R4/N-06/N-07 → **I03/I04 统一受限错误映射**；R6/N-03/N-04 → **Q5 容量线与真实负载 / I03 能力契约**；F3-06 → **I03 能力契约**。

---

## 6. 关键验收项的独立核验记录（S1 退出门槛 1–6）

| 门槛 | 要求（原文摘要） | 我的独立核验 | 判定 |
|---|---|---|---|
| **1** | 映射替换与 ChangeSet 在提交**前/中/后**模拟取消、异常、磁盘写失败及进程退出；恢复只见最后已提交状态；旧 ChangeSet 拒绝提交；来源与所有权同步恢复 | 仓库 `test_atomic_fault_matrix` = **2 模式 × 7 提交点 × 4 失败态 = 56 例**（`exit` 为真实独立进程 `os._exit(73)`）；`test_actual_database_full_modes` 以 `PRAGMA max_page_count` **真实触发 SQLITE_FULL**（映射/ChangeSet/轮次三模式），断言事实/revision/progress 不变；探针 NEW-B 复现响应丢失后 marker 为权威且重试幂等。**磁盘失败未使用边界注入的替代口径** | ✅ 成立 |
| **2** | 删除源行不删除手工事实；人工修改、受管范围和多来源所有权冲突**均可定位并阻止**不合法提交 | 源行删除：映射空计划仅撤回其受管数据，手工事实保留（仓库 `:152-153`）；探针 P5/P6 复现墓碑/编辑后第二来源得可定位 `Conflict`（含 slot/owner/row/id）；探针 P7 复现不同多值不被整槽拒绝；探针 NEW-G 复现单值 slot 冲突可定位；旧基线/第二连接基线拒绝与 operation 重试对账有回归 | ✅ 成立 |
| **3** | 规则撤回只替换当前推导；附录 D 每类变化得到准确过期原因；缓存清理不损坏历史/定义/正式数据；仅改模型配置不错误失效领域结果 | `test_nine_appendix_d_rows_positive_and_negative` **9 组参数化正反例**全绿；`invalidation-v2.json` 九行与 PRD D.2 逐行对应、**第 9 行 model 的 `staleReason` 为 `null`**；探针 F-01 复现模型配置变更后既有结果 `stale=[]` 且仍为 current；探针 N-08 复现缓存回收后 pinned 载荷与历史轮次完整 | ✅ 成立 |
| **4** | 场景副本隔离；固定轮次提交/取消边界符合 E.2；历史输入、结果和已提交轮次不被新运行改写 | `runs`/`rounds`/`run_terminal` 与正式 `facts` 表分离，轮次不写正式数据；取消保留已提交点（`committedProgress` 完整）；终态后拒绝写轮次；新运行不改动旧运行（`db.history(run) == history`）；六张历史表有 SQL 不可变触发器；探针 NEW-J 复现轮次序号 1..1000 与 `maxRounds` 越界分别 `ValueError`/`Conflict` | ✅ 成立 |
| **5** | 两档规模测量和附录 D 正/反例映射均有原始记录；机器可读规则与文档对照无遗漏；不把合成负载当作完整业务基线 | 1×/10× 各 3 次 ×（development+packaged）＝ **12 条原始测量**（归档 13 个 JSON 与我独立运行的 13 个 JSON 逐字段一致）；命名空间按 `urn:case:{i}:` 逐档独立，**未以同 ID 重复 G-base 冒充扩容**（`inputSha256` 1× 与 10× 不同）；固定 SELECT 完整结果集与 expected 逐条相等；`invalidation-v2.json` ↔ PRD D.2 ↔ `acceptance.md` D.2 表三方逐行无遗漏；`acceptance.md:40-52` 明确把存储 fixture 与 RDF 合成孪生分列 | ✅ 成立 |
| **6** | 对 G-base/G-map-empty/G-behavior/E.5 逐项记录实测范围与完整预期集合/顺序；未执行业务用例保留未通过；迁移失败可恢复；重放输入缺失时如实标识 | `storage_baselines.py` 的 E.5 **8 行逐轮集合与 PRD E.5 原表逐值一致**（产能 3 积压 W004 / W007–W008 / W010–W012 / W013–W016，累计 3/6/9/12；产能 4 各轮完成各自新建四单、积压为空、累计 4/8/12/16），两次重放逐轮集合一致；`acceptance.md:40-52` 逐项标注"完整业务验收状态"，**G.2 V-01/R-01–06/O-01、G.3 B-01–11、G.4/G.5 A-03–10、G.6 设备 B 场景均如实标为未执行/未通过**；迁移 11+4 注入点 × 异常/真实进程退出全部可恢复；重放输入缺失（含输入快照形状、依赖、配置、来源）如实标识为 `replayable=false` 或拒绝 | ✅ 成立 |

**附录 D 九行正/反例与唯一机器码表**：九行与 PRD D.2 逐行对应，**D.2 第 9 行（仅模型服务或 Agent 提示配置变化）`staleReason=null`**，经探针 F-01 独立复现"模型配置变更不产生领域过期原因"；`invalidation-v2.json` 中 `implementationCompatibility` 与 `publicationPolicy` **单列且 `staleReason` 均为 null**，未新增第九种领域原因；展示文案不进入机器码表。

**附录 C / E / G 的诚实性**：`acceptance.md` 的"完整业务验收状态"列把**存储回归**与**完整业务通过**明确分开，未把占位能力、合成负载或存储替身登记为已通过的业务基线；G-map-empty 的两行完整集合已进入回归（`acceptance.md:79`），CSV 解析/预览业务仍标未执行；E.5 的 8 行是**预置期望状态的存储回归**，`acceptance.md:38` 明写"这些是预先准备的期望状态存储回归，不是执行 E.2 得出的业务结果"——**表述准确，未越界**。

**真实 RDFLib 依赖与基础打包（I01 冻结范围的显式条款）**：`pyproject.toml` 精确钉住 `rdflib==7.6.0`，`uv.lock` 含 `rdflib 7.6.0` 与 `pyparsing 3.3.3`（带 sdist/wheel 哈希）；**V8–V12 独立重建 PyInstaller 产物并复跑包内同样例**（10× 探针完整结果集 + 包内 health 仅声明 `health` + 许可证与 `invalidation-v2.json` 实际入包 + 可执行文件 SHA-256 与归档**逐位一致**）——**"新增真实 RDFLib 依赖即执行对应基础打包和包内样例回归，不等 I05"这一条已实际兑现，不是声明**。

---

## 7. 安全与数据一致性专项检查

- **SQL 注入**：生产代码全部参数绑定（`?`）；仅常量 DDL/触发器名与测试侧整数 PRAGMA 使用插值。
- **RDF/Turtle 注入**（探针 V15/p4.py）：`@prefix evil: <http://x/> .`、多语句注入、`_:blank` 空白节点、嵌套三元组 **全部被拒**；`term()` 以单三元组 Turtle 解析并要求 `len(parsed)==1`，无插件发现、无远程数据集、无 URL 解析取数；`iri()` 拒绝相对 IRI 与含空白/`<>"{}|^`\`\\` 的 IRI。
- **词法与身份绕过**：`"x"^^<xsd:string>`、`"""alias"""`、带语言标签的别名均因 `term(value).n3() != value` 被拒（"Canonical RDF object required"），`test_rdf_lexical_alias_cannot_bypass_ownership` 覆盖三条路径（映射/手工）。
- **跨项目隔离**（探针 NEW-K）：跨项目 `publish` 与 `start_run` 均 `Conflict: Cross-project snapshot`；`collect_cache` 的跨项目作用域见 F3-03（仅派生载荷，不涉正式数据）。
- **不可变与证据**：`snapshots`/`commits`/`runs`/`rounds`/`run_terminal`/`commit_evidence` 六表对 UPDATE/DELETE 全部由 SQL 触发器拒绝（`immutable evidence`）；`commit_evidence` 与正式数据、前后快照同事务。
- **无凭据、无遥测、无云调用**：`storage.py`/`rdf_snapshot.py`/`storage_probe.py` 不含任何网络、凭据或遥测路径；`verify-i01.py` 以 `PATH=/usr/bin:/bin` 且剔除 `PYTHONPATH`/`PYTHONHOME` 运行包内产物。
- **未提交凭据、业务数据或运行数据库**：本轮 diff 不含任何 `.db`、密钥或业务数据文件；`evidence/` 下只有测量 JSON 与命令输出。

---

## 8. 最终结论

**通过。**

1. **阻断问题 0 项**；S1 退出门槛 1–6 全部独立验证成立（见第 6 节逐项表）。
2. **本轮新发现 6 项，全部为低**（F3-01…F3-06），**无一项违反 I01 冻结范围、无数据损坏、无安全缺陷、无既有链路回归**，故不构成阻断。F3-01/F3-02 建议在下一候选修复；F3-04/F3-05 建议同批以文档方式补记；F3-06 为已登记延期至 I03 的边界复述。
3. **历史 29 条编号意见逐项处理完毕**：22 条已关闭，6 条属**已明确登记、允许延期**且不违反任何退出门槛的项，1 条为确认项（N-08）；**无未关闭的阻断项，无以"旧版通过"沿用者，无杜撰编号**。所有延期项均已写明指向 I03/I04 或 Q5/真实负载。
4. **关键验收均可验证**：静态（lint/格式/类型/ruff）、运行（198 项 Python + vitest + e2e）、打包（独立重建的 PyInstaller 产物 + 12 条包内/开发测量 + 许可证/资源核验 + 可执行文件 SHA-256 逐位一致）四类证据分层清晰且可复现；**生产证据（干净设备、无系统 Python、断网安装、签名、首发平台、实际 Windows CI、完整业务执行器、I05 语义、Q5 容量）未验证且不在本迭代范围，本报告不冒称通过**——归档 `package-manifest.json` 的 `scope` 字段与 `acceptance.md:58` 已如实声明该边界。
5. **按 `scope.md` 统一门禁第 4/5/6 条**：本轮通过结论仅对 `e628f5e…1e3b179` 这一固定范围成立；下一候选若含实现/测试/配置/依赖/验收变更，须重新双审。**双审前不 push**（当前 `origin/develop` 仍为 base，无 PR/merge，符合门禁）。

---

*报告人：MiniMax Code / mavis（模型 MiniMax-M3.1-Flash）。本轮未委托内部子 agent 复核；全部判断基于本人直接读取的代码与需求原文，以及本人执行的命令与探针。探针脚本：`/tmp/i01-r3-probe/p1.py`…`p5.py`；独立打包测量产物：`/tmp/i01-r3-verify/`、`build/engine/`（均为已忽略或临时路径，未覆盖任何归档证据）。*
