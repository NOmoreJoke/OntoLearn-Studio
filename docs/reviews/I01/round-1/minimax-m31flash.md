# I01 Round 1 独立对抗审查报告（MiniMax M3.1-Flash）

任务标识：`I01-R1-MiniMax-M31Flash-20261020-0015`
迭代：I01 / S1 / ADR-0002（源真相、隔离场景、不可变历史与可重建派生视图的存储及失效 spike）
审查范围：`e628f5e7b6c09e10e15644552a6171c4a9a3072e` → `6d8e4b3021b368661247c03c47f01e4d32ebf6e1`

---

## 0. 结论

**不通过。**

本候选在存储语义、故障矩阵、附录 D 九行映射、迁移/恢复、真实 RDFLib 建图与包内同样例方面做了扎实且诚实的工作：105 项 Python 测试与 4 项 TS 测试全绿，14 条两档测量原始值可复现，包内引擎二进制哈希与探针输出与归档证据逐位一致，冻结输入与 61 项本轮前文件的 SHA-256 全部未变。**但存在 2 项阻断问题，均为本候选新引入或本候选未关闭的既有要求缺口：**

1. **F-01（阻断）**：旧快照的迟到结果可以覆盖更新的"当前"指针——直接违反 `scope.md` I01 行明写的"迟到结果拒绝发布为当前"、S1 计划第 47 行"旧任务迟到不能覆盖新版本"以及 PRD 附录 D.1"绑定不可变快照的结果只能作为历史结果使用"。`acceptance.md` 声称"旧快照及旧实现迟到发布被隔离"，实际只隔离了"旧实现"维度，"旧快照"维度在依赖未变时被证实可覆盖。
2. **F-02（阻断）**：`storage_probe.py` 顶层 `import resource`（Unix 专有模块，Windows 不存在）使既有 Windows CI 矩阵腿（`desktop` job / `windows-latest`）在 `engine:check` 阶段即失败，并使 Windows 上打包引擎在启动时 `ModuleNotFoundError`。开发者已在 `docs/reviews/I01/status.md:50` 自行记录该风险，但未修复。

按 `scope.md` 统一门禁第 4/6 条——"阻断未关闭或关键验收无法验证不得通过"——本轮不得出具通过。F-01、F-02 关闭后需另起候选并重新双审。

中低严重度问题 9 项，其中 F-03、F-04、F-06 建议同批修复，F-05/F-07～F-11 可在后续候选或对应迭代处理（见第 4 节各条"处理结论"）。

---

## 1. 评审任务、模型及思考设置的来源记录

| 项目 | 值 | 来源性质 |
|---|---|---|
| 任务标识 | `I01-R1-MiniMax-M31Flash-20261020-0015` | 开发者会话记录（`docs/reviews/I01/status.md:41`）。我未独立观测到该标识的生成过程，仅按派发信息登记。 |
| 模型 | MiniMax M3.1-Flash | **来源记录**：开发会话声明经 MiniMax Code UI 核验。**我能独立观测**：本会话运行环境自报 `Model: MiniMax-M3.1-Flash`、`agentName: mavis`、工作目录为上述仓库。 |
| 思考设置 | xhigh | **纯来源记录**。我无法独立观测 UI 的思考档位，也未使用 computer use 复核 UI 界面；该声明不作为通过依据。 |
| 项目目录绑定 | 原生 Select Directory 指向本仓库 | **纯来源记录**；我独立观测到 cwd 与仓库路径一致，且可对该路径执行只读 git 操作。 |
| 分支 | `feature/I01-storage-invalidation` | **独立可观测**：`git rev-parse --abbrev-ref HEAD` 实测一致。 |
| 与其他模型互不披露 | 声称 | 采信为流程声明；我未查阅 `docs/reviews/I01/round-1/zcode-glm53.md`（该文件在本轮结束时亦未产出）。 |

**说明**：本报告的全部结论仅基于我直接读到的代码、需求文本与我自己执行的验证命令，不以开发者或其他模型的通过意见为依据。

---

## 2. 项目路径、分支、base/head 与工作区

- 项目绝对路径：`/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio`
- 分支：`feature/I01-storage-invalidation`（实测）
- base SHA：`e628f5e7b6c09e10e15644552a6171c4a9a3072e`
- head SHA：`6d8e4b3021b368661247c03c47f01e4d32ebf6e1`（`git rev-parse HEAD` 实测与派发候选一致）
- 候选规模：1 个提交（`feat(I01): spike transactional storage and dependency invalidation`），43 个文件，+4369 / −2
- 远端状态：无 push / PR / merge（`git log` 与工作区均无相关痕迹）

**工作区（受审实现之外）**：`git status --porcelain -uall` 实测 63 项（7 modified + 56 untracked）。其中 `docs/iterations/I01/preexisting-files.json` 登记的 **61 项**本轮前文件，我逐文件重算 SHA-256，**61/61 全部一致，0 缺失、0 不匹配**；余下 2 项为本轮审查流程证据（`docs/reviews/I01/status.md`、`docs/reviews/I01/frozen-source-check.txt`）。派发说明中"61 项"与实测 63 项的差异由此完全解释，不存在遗漏或夹带。

我未修改、未暂存、未还原、未清理任何仓库文件；除本报告外未写入其他仓库文件。所有对抗探针脚本写在 `/tmp/i01-review/`。

---

## 3. 已检查范围、验证命令与实际结果、未验证事项

### 3.1 需求依据（逐条读取，非依赖开发者摘要）

- `docs/iterations/I01/inputs/scope.md`（I01 冻结范围全文）
- `docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md`（S1 全文 + 退出门槛 1–6）
- `docs/iterations/I01/inputs/goal-objective.md`、`inputs/M0深度审查_采纳评估_2026-10-19.md`
- `docs/prd/PRD-本体学习与落地Agent工作台.md` V0.6：FR-006、FR-304、FR-604、FR-700～705、FR-804、FR-1000、附录 C、附录 D（D.1/D.2）、附录 E（E.1～E.5）、附录 G（G.0 基线）
- `AGENTS.md`
- `docs/iterations/I01/ADR-0002-storage.md`、`docs/iterations/I01/acceptance.md`（**作为被审对象，不作为通过依据**）

**冻结输入可用性核验**：`inputs/sources.json` 登记 4 份副本的 SHA-256 与实际文件逐位一致（4/4 OK），冻结输入可用于恢复需求。

### 3.2 实现检查范围

`packages/engine/src/ontolearn_engine/`：`storage.py`（770 行）、`invalidation.py`、`invalidation-v1.json`、`rdf_snapshot.py`、`storage_probe.py`、`entrypoint.py`；`packages/engine/tests/`：`test_storage.py`（94 项）、`storage_baselines.py`；`scripts/build-engine.mjs`、`scripts/verify-i01.py`；`packages/engine/pyproject.toml`、`uv.lock`、`.prettierignore`；`.github/workflows/ci.yml`；`docs/iterations/I01/evidence/*`。

### 3.3 验证命令与实际结果

| # | 命令 | 实际结果 |
|---|---|---|
| V1 | `git rev-parse HEAD` / `--abbrev-ref HEAD` | `6d8e4b3021b368661247c03c47f01e4d32ebf6e1` / `feature/I01-storage-invalidation` ✅ 与候选一致 |
| V2 | `uv run --frozen pytest packages/engine/tests/test_storage.py -q` | **94 passed in 3.07s** ✅ |
| V3 | `… -k atomic_fault_matrix` | **56 passed**（2 模式 × 7 提交点 × 4 失败态）✅ |
| V4 | `npm run check` | **EXIT=0**；eslint 0 warn、prettier 通过、tsc 通过、vitest 4 passed、electron-vite 构建成功、ruff 通过、**105 passed**（test_protocol 11 + test_storage 94）✅ |
| V5 | `npm run verify:sources` | **EXIT=0**，"已核对 13 个归档源文件" ✅ |
| V6 | `npm run test:e2e` | **EXIT=0**，1 passed（桌面真实引擎 health + 隔离 + 最小窗口）✅ |
| V7 | `shasum -a 256 release/.../ontolearn-engine` | `b8e076d1…edd0146`，与 `package-manifest.json` 登记值**逐位一致** ✅ |
| V8 | 包内探针（`PATH=/usr/bin:/bin`，剔除 `PYTHONPATH`/`PYTHONHOME`）`--storage-probe --scale 1 --trial 0` | `inputSha256=b0bcc466774f…`、`querySha256=7879b25f2833…`、`snapshotId=71930b09f264…`、`result=["urn:case:0:alarm/A01"]`、`triples=18` —— 与 `evidence/packaged-1x-0.json` **完全一致** ✅（包内同样例成立） |
| V9 | 证据交叉核对 | development 1x/10x 与 packaged 1x/10x 的 `inputSha256`/`querySha256`/`result`/`snapshotId` 两两相同；`triples` 18 / 180；`rdflib 7.6.0` ✅ |
| V10 | 61 项本轮前文件 SHA-256 复算 | 61/61 一致，0 缺失、0 不匹配 ✅ |
| V11 | 自建对抗探针 6 个（`/tmp/i01-review/`） | 见第 4 节各项证据；F-01、F-02、F-03、F-04、F-05、F-06、F-08、F-09、F-11 均被**独立复现** ❌ |
| V12 | 乐观并发实测（两连接同基准并发写） | writer A 提交、writer B 得 `Conflict: Old projectRevision; re-preview required`；最终仅 1 条事实、仅 1 个 marker ✅ 并发控制正确 |
| V13 | Windows 导入链模拟（meta_path 拦截 `resource`） | `storage_probe` 与 `entrypoint` 均 `ModuleNotFoundError: No module named 'resource'` ❌ 见 F-02 |

**测量证据边界**（不影响结论，供后续参考）：冷态 `fixedSelect` 中位数约 540 ms，而同进程热重复约 9.5 ms，且 1x→10x 该值基本不变——冷查询由 SPARQL 解析开销主导，**不构成规模信号**。ADR-0002 已声明"两档很小，不外推容量""Q5 未定，不证明业务容量足够"，与实际数据一致，未发现夸大容量结论。100× 档属计划中选做项，未做。

### 3.4 未验证事项（明确边界）

1. **Windows 与 Linux CI 实际运行**：本机为 macOS arm64，无对应主机。F-02 的结论基于导入链静态分析 + `resource` 不可用的模拟复现 + Python 官方文档（`resource` — Availability: Unix, not WASI）三重佐证，**不是**在 Windows 上实跑 CI。
2. **Linux 打包产物**与跨平台动态链接：未验证（ADR 已声明不在本次范围）。
3. **干净设备、无系统 Python、断网安装、签名**：未验证（ADR 已声明）。
4. **完整业务映射 / 行为触发 / 沙盘执行 / pySHACL / RDFS+规则组合 / 解释 UI**：不属 I01 范围（I05）。**本报告不把存储测试视为完整业务通过**；`acceptance.md` 在这点上表述克制，未发现冒认。
5. **未重新执行 `npm run package:dir`**：只复用了已存在的 `release/mac-arm64` 产物，并以其二进制 SHA-256 与 `package-manifest.json` 登记值一致作为佐证；`build-engine.mjs` 的 `--collect-all rdflib` 等改动经该产物间接验证。
6. **未运行 `scripts/verify-i01.py` 重跑**：其产物（12 条测量、manifest、licenses、dynamic-linkage）已逐项与实际产物/探针复现核对一致。
7. **Q5 容量线**：未定，本报告不提出任何容量通过线。

---

## 4. 问题清单

严重程度定义：**阻断** = 违反 I01 冻结范围/S1 退出门槛/PRD 主定义，或使既有 CI/打包链路回归，本候选不得通过；**中** = 实现与自身文档声明不符，或存在无护栏的语义缺口；**低** = 文档、错误面或边界语义问题，不影响本轮验收结论。

---

### F-01 ［阻断］旧快照的迟到结果可覆盖更新的"当前"指针

- **位置**：`packages/engine/src/ontolearn_engine/storage.py:499-551`（`publish`），关键在 `:518-521`（依赖版本比较）与 `:547-550`（`INSERT OR REPLACE INTO current_results`）；另见 `invalidation.py:17-26`（`reasons`）
- **触发条件**：结果的依赖键集合在两个 revision 之间**未发生变化**（例如仅模型配置变更、或只改动与该结果无关的维度），而一个在较旧 revision 启动、较晚完成的任务调用 `publish` 并携带旧快照。`publish` 只比较 `snap["dependencyVector"][key]` 与当前 `versions`，不比较 `snap["projectRevision"]`；比较结果为空 ⇒ `stale` 为空 ⇒ 直接 `INSERT OR REPLACE` 覆盖"当前"指针。
- **影响**：
  1. 直接违反 `docs/iterations/I01/inputs/scope.md` I01 行明写的"**迟到结果拒绝发布为当前**"。
  2. 违反 S1 计划第 47 行"旧任务迟到不能覆盖新版本"。
  3. 违反 PRD 附录 D.1"**历史**：绑定不可变快照，只能作为历史结果使用；用于新报告或下一步操作时必须显式选择"——被提升为 current 的结果实际绑定的是较旧快照，等于让"新报告默认只使用当前已提交状态"（D.2 补充规则 2）失效。
  4. `docs/iterations/I01/acceptance.md` 第 11 行声称"旧快照及旧实现迟到发布被隔离"——**"旧快照"一半经实测不成立**，属于验收结论与实现不符。
- **证据**（`/tmp/i01-review/probe_late.py`，独立复现）：
  ```
  revision after initial: 1
  r1 (rev1 snapshot) -> current = True
  model-only change -> revision 2, facts:asserted version unchanged, r1 stale = []
  r2 (rev2 snapshot) -> current is r2 = True
  --- LATE publish from rev1 snapshot ---
  late result stale : []
  current payload now : ['LATE-from-rev1']
  current snapshot rev : 1
  current is r2 (rev2)? : False
  LATE rev1 OVERWROTE NEWER rev2 CURRENT: True
  ```
  现有测试未覆盖该分支：`test_multiple_reasons_late_result_cache_isolation_and_history:233` 的 late 案例依赖**已变化**（因此自然 stale）；`test_old_implementation_cannot_displace_new_current` 只覆盖**实现来源**维度。
- **修复建议**：
  1. `publish` 中比较 `snap["projectRevision"]` 与 `self.revision(project)`：当快照 revision 低于当前 revision 且其依赖版本集合在两者间未变化时，不得成为 current（应保留为可查看历史记录）。
  2. 更稳妥的做法：`current_results` 增加 `revision` 列，替换指针时要求新结果的快照 revision **不小于**已登记指针的 revision；或改为按 `(project, kind, implementation, revision)` 保留并由读取侧选取最新且依赖已复验者。
  3. 补一条回归：**"依赖未变 + 旧快照迟到发布"** 必须不成为 current（现有两条测试都不覆盖此组合）。
  4. 修正 `acceptance.md` 第 11 行的表述，使"旧快照"与"旧实现"两半的覆盖状态与实际一致。
- **处理结论**：**必须在本候选后续版本关闭**，属 I01 冻结范围的明文要求，未关闭不得通过。

---

### F-02 ［阻断］`import resource` 使既有 Windows CI 矩阵腿与包内引擎崩溃

- **位置**：`packages/engine/src/ontolearn_engine/storage_probe.py:10`（`import resource`，模块级）；`packages/engine/entrypoint.py:6`（`from ontolearn_engine.storage_probe import main as probe_main`，模块级）；`packages/engine/tests/test_storage.py:13`（`from ontolearn_engine.storage_probe import measure`，模块级）
- **触发条件**：在 Windows 上运行 Python。`resource` 是 Unix 专有标准库模块，官方文档明确标注 "Availability: Unix, not WASI"（https://docs.python.org/3/library/resource.html），Windows 从 Python 3.3 起即不存在该模块。
- **影响**：
  1. `.github/workflows/ci.yml:39-63` 的 `desktop` job 在 `windows-latest`（ci.yml:44）上运行 `npm run engine:check`（ci.yml:59）→ pytest 收集阶段即 `ModuleNotFoundError` → **既有 CI 矩阵腿由绿转红**。
  2. `npm run package:dir`（ci.yml:63）在 Windows 上经 `scripts/build-engine.mjs` 构建的引擎，其入口 `entrypoint.py` 模块级导入 `storage_probe` → **打包引擎启动即崩，health 探针不可用**（`apps/desktop/src/main/engine.ts` 的 `getEngineCommand` 在 packaged 分支直接执行该二进制）。
  3. 违反 `scope.md` 统一门禁第 6 条"遵守CI保护不绕过"与第 5 条"CI修代码同样回审"的前提——本候选合并将使 CI 红灯。
- **证据**（`/tmp/i01-review/probe_windows.py`，用 meta_path 拦截器精确模拟 Windows 无 `resource`）：
  ```
  OK, resource unavailable: No module named 'resource'
  1) storage_probe import error -> ModuleNotFoundError No module named 'resource'
  2) entrypoint import error     -> ModuleNotFoundError No module named 'resource'
  3) ontolearn_engine.__main__ mentions storage_probe: False   （health 路径本身不依赖，可修复）
  ```
  佐证：`docs/reviews/I01/status.md:50` 已自行记录"独立后续静态检查还需关注 storage_probe 的 Unix resource 导入与既有Windows CI/包内health兼容"，但该风险**未修复、未登记为已关闭**。
- **修复建议**：
  1. `storage_probe.py` 改为受保护导入：`try: import resource except ImportError: resource = None`，在 `resource` 不可用时把 `processHighWaterRssBytes` 记为 `null` 并在 `condition`/`method` 字段注明"RSS 不可用"，不得让缺失平台能力阻断整条探针。
  2. `entrypoint.py` 把 `storage_probe` 改为**惰性/可选导入**（仅在 `--storage-probe` 分支内导入），使 Windows 上普通 health 路径不依赖探针模块。
  3. `test_storage.py:13` 改为在 `resource` 缺失时跳过仅依赖 RSS 的断言（或以 `pytest.importorskip` 保护），保证 Windows 上 `engine:check` 可收集。
  4. 补一条 Windows 平台检查（或至少在 CI 增加 `import resource` 可用性守卫）避免同类问题复发。
- **处理结论**：**必须关闭**。这是本候选引入的跨平台回归，且已破坏仓库既有 CI 矩阵；`scope.md` 明确要求"桌面或桥接改动运行 `npm run test:e2e`"，Windows 侧 health 不可用等同于桌面能力受损。

---

### F-03 ［中］`publish` 接受空依赖集与未解析的依赖身份，结果将永久不过期

- **位置**：`packages/engine/src/ontolearn_engine/storage.py:499-551`（参数 `dependencies` 在 `:502`；`vector` 构造在 `:518`；`reasons` 在 `:521`）
- **触发条件**：`publish(..., dependencies=[], ...)`，或 `dependencies` 中包含项目中不存在的 identity（如 `"query:does-not-exist"`）。
- **影响**：`reasons()` 用 `now.get(key, 0)` 比较，两侧同为 0 ⇒ 永不产生 stale 原因；该结果将**永久保持 current**，即使事实、映射、规则全部改变。附录 D 要求"结果只订阅实际依赖"并"仅改模型配置不使确定性领域结果失效"，但"漏报依赖"与"确实不依赖"在存储层完全无法区分。`acceptance.md:18` 已声明依赖须由未来能力定义派生，但这只是流程约定，**存储层对漏报零成本、零告警、零护栏**。
- **证据**（`/tmp/i01-review/probe2.py` A/B 段）：空依赖结果与 `"query:does-not-exist"` 依赖结果在事实真正变化后 `stale` 仍为 `[]`，且 `current(...)` 仍返回该结果。
- **修复建议**：
  1. `publish` 拒绝空 `dependencies`（抛出明确错误），强制调用方声明至少一个真实依赖。
  2. 对每个依赖 identity 校验其是否已在项目 `versions` 或 `definitions` 中登记；未登记时拒绝发布，或至少在 `results` 上标记"未解析依赖"并令 `current()` 对其返回 `None`。
  3. 后续在能力注册表中把"能力 → 依赖键"绑定为强制来源，使漏报在协议层即不可表达。
- **处理结论**：建议与 F-01 同批修复（两者叠加会放大错误当前结果的危害）。

---

### F-04 ［中］定义级 IRI/词法未在提交时校验，与 ADR-0002 自身声明不符

- **位置**：`packages/engine/src/ontolearn_engine/storage.py:310`（`_validate_references` 只校验引用形状与可解析性）；`packages/engine/src/ontolearn_engine/rdf_snapshot.py:56-65`（建图时才校验）
- **触发条件**：提交 `layer="ontology"` 且 `value.triples` 中含非绝对 IRI 的 subject/predicate，或缺少 `subject`/`predicate`/`object` 键。
- **影响**：`ADR-0002-storage.md:29` 明写"整个计划的显式 definition `references` 必须可解析，**IRI/词法项**及引用形状失败均回滚"——实际该回滚只对 `facts` 生效（`_fact` 在 `storage.py:177-189`）。定义层的非法 IRI 会被**成功提交并持久化进源真相**，直到读模型重建时才抛错；此时已无法定位到具体提交批次，且源真相已被污染。ADR 的声明与实现不符。
- **证据**（`/tmp/i01-review/probe2.py` C/D 段、`/tmp/i01-review/probe3.py` D 段）：
  ```
  COMMIT ACCEPTED a definition with a non-absolute subject IRI
  definition persisted: True
  graph build FAILED later: ValueError Absolute stable IRI required
  ---
  COMMIT ACCEPTED malformed triple
  graph build FAILED later: KeyError 'subject'
  ```
- **修复建议**：在 `commit` 的定义写入路径上，对 `value` 中出现的 IRI/词法项（至少 `triples` 数组）复用 `rdf_snapshot.iri()` / `term().n3()` 做同 facts 一致的规范化校验，失败即回滚；并在 ADR 中明确"定义级 IRI/词法校验"的覆盖范围。
- **处理结论**：建议与 F-01 同批修复（属实现与自身 ADR 声明不符）。

---

### F-05 ［中］迁移故障注入实际只覆盖一个点

- **位置**：`packages/engine/src/ontolearn_engine/storage.py:69-116`（`_migrate`），关键在 `:74` 的 `with self._transaction():`——**未把 `hook` 传入** `_transaction`。
- **触发条件**：`_migrate` 调用 `_transaction()` 的默认空 hook，因此 `hook("before")` 与 `hook("before_commit")` 在迁移路径上**永不触发**；可用的迁移注入点只有 `"v1_created"`（仅新建库路径）与 `"migration_mid"`（仅 v1→v2 路径）。
- **影响**：S1 退出门槛 6"迁移失败可恢复"与 `acceptance.md:14`"迁移中断回滚"的证据强度低于声明——`test_migration_failure_backup_restore_and_future_format:328-338` 使用"任何阶段都抛"的 hook，在其 v1 备份场景中实际只命中 `"migration_mid"` 一个点。DDL 在 SQLite 中确为事务性，故实质风险不高，但"迁移可恢复"目前是单点证据。
- **证据**：源码 `storage.py:74` 与 `storage.py:55-56`（`_transaction(hook=lambda _: None)` 默认参数）；测试 `test_storage.py:328-338`。
- **修复建议**：将 `migration_hook` 传入 `_transaction`，并在 `v1_created`、`mapping_state` 建表与回填、`commit_evidence` 建表与触发器、`current_results` 重建/改名、`PRAGMA user_version=2` 各点分别注入失败并断言 `user_version` 与表结构回滚、重开可重试。
- **处理结论**：可延期至下一候选，但需在 `acceptance.md` 中如实标注当前迁移故障覆盖的实际注入点，避免以单点证据表述为"迁移可恢复"已充分验证。

---

### F-06 ［中］`Store` 构造无条件取写锁，只读打开也会被其他写者阻塞至超时失败

- **位置**：`packages/engine/src/ontolearn_engine/storage.py:39-52`（`__init__` → `_migrate`）与 `:69-116`（`_migrate` → `with self._transaction():` → `BEGIN IMMEDIATE`）
- **触发条件**：对**已是 v2、无需任何迁移**的数据库调用 `Store(path)`，而同一数据库另有连接持有写事务。
- **影响**：`_migrate` 即使在 `user_version == FORMAT_VERSION`、一条 DDL 都不需要执行的情况下，仍执行 `BEGIN IMMEDIATE`（写锁）。结果是：(a) 打开一个只读用途的 Store 也会与写者互斥；(b) 失败以裸 `sqlite3.OperationalError: database is locked` 从**构造函数**抛出，既不是领域错误也不携带上下文；(c) 忙等待固定 5 秒后失败，恢复路径（如崩溃后对账、备份、只读检查）在此期间完全不可用。S2 将引入常驻协调器与并发 job，该构造副作用会放大。
- **证据**（`/tmp/i01-review/probe6.py`）：
  ```
  user_version after first open: 2
  --- opening a second Store on an ALREADY-MIGRATED (v2) db while a writer holds the lock ---
  FAILED after 5.20s -> OperationalError: database is locked
  --- same, but the second Store only wants to READ ---
  FAILED after 5.20s -> OperationalError: database is locked
  ```
- **修复建议**：
  1. `_migrate` 在 `version == FORMAT_VERSION` 时直接返回，不开启写事务（只读打开应零写副作用）。
  2. 需要迁移时，把"只读检查 user_version"与"取得写锁执行迁移"分两步，且迁移失败的重试语义与普通读路径分离。
  3. 构造函数对 `OperationalError` 做一次受控包装（携带 project/路径/是否迁移中），或至少在 ADR 中写明"打开项目库需要独占写锁"这一运行约束。
- **处理结论**：建议同批修复或至少在 ADR 中显式登记该运行约束（否则 S2 的并发设计会基于错误前提）。

---

### F-07 ［低］提交后取消使 `commit()` 抛出，调用方拿不到已提交的标记

- **位置**：`packages/engine/src/ontolearn_engine/storage.py:66-67`（`hook("after_commit")` 位于 `try/except` 之外，异常直接上抛）与 `:346`（`return self.marker(project, operation)` 因此不可达）
- **触发条件**：提交成功后收到取消/响应投递失败（`after_commit` 钩子抛错）。
- **影响**：语义本身正确（数据已提交且不可撤销，与 ADR "提交成功后才收到取消或响应丢失，不能撤销已提交事实"一致），但调用方只拿到一个异常，**无法从返回值判定"是否已提交"**，必须另外调用 `marker(project, operation)` 才能对账。S2 要求的"提交成功但响应丢失"四类情形区分，在当前接口面上缺少可用的判别信号。
- **证据**（`/tmp/i01-review/probe3.py` E 段）：
  ```
  commit RAISED: KeyboardInterrupt cancelled after commit
  revision (data committed?): 2
  marker present: True
  facts: ['urn:equipment/001', 'urn:after']
  ```
- **修复建议**：引入专用异常类型（如 `CommitAcknowledgementLost`），携带 `marker` 与 `operation`，使调用方可在同一异常路径上完成对账；在 ADR 的接口契约中写明该异常语义。
- **处理结论**：可延期；但建议在 ADR 中先写明"提交后失败必须另调 `marker` 对账"，避免 S2 误用。

---

### F-08 ［低］人工删除（墓碑）后映射重跑被永久阻断，且恢复路径未文档化

- **位置**：`packages/engine/src/ontolearn_engine/storage.py:400-406`（`_replace_mapping` 的漂移判定 `fact["object"] != fact["managed_value"]` 对墓碑同样成立）
- **触发条件**：用 `remove` 人工删除一条受管事实（写入墓碑，`object=NULL`），随后重跑该映射。
- **影响**：墓碑的 `object` 为 `None`、`managed_value` 保留原值 ⇒ 判定为"人工漂移"⇒ 重跑被 `Conflict("Manual drift")` 阻断。ADR-0002:29 只描述了"**人工修改**的受管记录"导致漂移阻断，**未说明人工删除（墓碑）同样阻断**；FR-304 要求"用户如需放弃人工改动并恢复为上次映射受管值，系统必须展示将被覆盖的内容并单独确认"，当前既无展示也无显式恢复接口（仅存在未文档化的 `edits` 隐式技巧）。这使受管范围在一次人工删除后进入无文档恢复路径的状态。
- **证据**（`/tmp/i01-review/probe4.py` 1 段）：
  ```
  after manual delete, fact rows: [... 'object': None, 'owner': 'M1', 'source_row': '001', 'managed_value': '"泵站A"']
  mapping rerun BLOCKED: Manual drift: mapping=M1, row=001, slot=urn:equipment/001 urn:name
  explicit edit back to managed value: OK
  mapping rerun after restore: OK
  ```
- **修复建议**：在 ADR 中区分"修改漂移"与"删除墓碑"两类阻断并写明各自恢复入口（墓碑可用 `edits` 显式恢复为受管值，或提供"确认放弃人工删除并按受管值重建"的显式操作）；`acceptance.md` 相应补充墓碑场景的预期。
- **处理结论**：可延期至对应业务迭代，但需在 ADR 中补记，避免"人工删除 = 受管范围不可再生成"这一事实只存在于代码里。

---

### F-09 ［低］单值谓词声明的作用域是全项目并集，且 G-behavior 基线所用格式完全无效

- **位置**：`packages/engine/src/ontolearn_engine/storage.py:372-380`（`_check_slot`）与 `:428-435`（`_replace_mapping` 中的重复判定）；基线见 `packages/engine/tests/storage_baselines.py:65-73`
- **触发条件**：项目内任一 `layer="ontology"` 定义在**顶层** `singleValuedPredicates` 中列出某谓词。
- **影响**：(a) 作用域是"该谓词在整个项目内单值"，而非"该本体定义内单值"，但 ADR 未写明此语义；(b) `storage_baselines.py` 的 G-behavior 本体用的是 `properties: {P: {type: "boolean", single: true}}` 结构，**存储层完全不读取该格式**，该基线中的单值声明是惰性的（inert），容易让后续读者误以为已被覆盖。
- **证据**（`/tmp/i01-review/probe4.py` 2 段）：仅 ontology 定义 A 声明 `urn:name`，定义 B 无声明，第二个值仍被 `Conflict: Ownership conflict` 拒绝 ⇒ 证实为并集语义。
- **修复建议**：在 ADR 中写清单值声明的唯一格式与作用域；或让存储层同时接受并归一化基线所用的 `properties[].single` 结构，使基线具备实际约束力。
- **处理结论**：可延期，属文档/语义澄清。

---

### F-10 ［低］实现兼容隔离规则未进入机器可读规则文件

- **位置**：`packages/engine/src/ontolearn_engine/invalidation-v1.json`（仅含 9 个 family，`schemaVersion: 1`）
- **触发条件**：S2/U1/Agent 以该 JSON 为"共同契约来源"消费失效规则。
- **影响**：S1 计划要求交付"版本化的机器可读失效规则与 `staleReason` 码表"，并明确"引擎/依赖升级的缓存隔离**单列实现兼容规则**"。当前该隔离规则只存在于 ADR 散文与代码中（`current_results` 主键含 implementation、`current()` 比较 implementation），**JSON 内无任何条目**（实测 grep：JSON/配置中无 `dependencyLockHash` / `executionSemanticsVersion` 规则项）。下游若按"唯一机器规则来源是 invalidation-v1.json"（ADR-0002:37）接入，将无处取得该规则，极可能各端自行发明，正是 S1 交付定义要避免的。
- **证据**：ADR-0002:37 与 `:39`；`invalidation-v1.json` 全文；`grep -rn "dependencyLockHash|executionSemanticsVersion" --include=*.json packages/ scripts/` 无结果。
- **修复建议**：在 `invalidation-v1.json` 增加 `implementationCompatibility` 段（比较键、隔离/复用语义、复用前置的等价性测试与兼容版本字段），并 bump `schemaVersion`。
- **处理结论**：建议与 F-01/F-03 同批修复（属机器可读契约完整性）。

---

### F-11 ［低］错误面不统一，部分非预期输入被静默接受

- **位置**：`packages/engine/src/ontolearn_engine/storage.py:594-599`（`pin_result`）、`:679-686`（`finish_run`）、`:255-269`（`remove` 分支）、`:118-122` 与 `:227`（`create_project` / `revision`）
- **触发条件**：重复 pin 同一 result+report；重复 `finish_run`；`remove` 不存在的 fact id；向不存在的 project 提交。
- **影响**：同一存储层对外抛出 `Conflict`（ValueError 子类）、裸 `sqlite3.IntegrityError`、裸 `KeyError` 三类错误，并存在静默 no-op；ADR-0002:9 声明"后续应用服务负责业务 schema、预览及确认"但未约定存储层错误类型契约，调用方需逐点 try/except。
- **证据**（`/tmp/i01-review/probe3.py` F/G/H 段、`/tmp/i01-review/probe2.py` I 段）：
  ```
  second identical pin raised: IntegrityError UNIQUE constraint failed: result_pins.result, result_pins.report
  second finish_run raised  : IntegrityError UNIQUE constraint failed: run_terminal.run
  remove of unknown id accepted silently
  commit to unknown project raised: KeyError 'nosuch'
  ```
- **修复建议**：统一映射为 `Conflict` 或定义清晰的领域异常族（重复 pin/终态重入/未知 id/未知 project 各有可辨识的 code）；在 ADR 中登记错误类型契约，供 S2 的结构化错误码直接映射。
- **处理结论**：可延期至 S2 错误码落地时统一处理；建议先在 ADR 记录现状。

---

## 5. 历史问题逐项判断

本轮为 Round 1，无本审查的前轮意见。以下对仓库内已登记的**历史问题**（`docs/reviews/I01/internal-review.md` 的独立 agent 复核 7 项 + `docs/reviews/I01/status.md:50` 开发者自记风险 1 项）逐项给出我独立的关闭/未关闭判断。

| # | 历史问题（来源） | 我的判断 | 依据 |
|---|---|---|---|
| H-1 | slot 混淆导致人工新增覆盖映射 / 不同多值误拒绝（internal-review.md:7） | **已关闭** | `manual` 对既有受管事实抛 `Conflict("Explicit fact edit required; cannot take ownership")`（`storage.py:296-299`），只能新增；`edits` 按事实 id 改值（`:272-290`）；不同多值可并存、单值声明冲突被拦（`test_explicit_manual_edits_multivalue_noop_and_single_slot` 通过）。 |
| H-2 | 旧实现迟到覆盖新版当前指针（internal-review.md:8） | **部分关闭** | "旧**实现**"维度已关闭：`current_results` 主键含 implementation，`current()` 比较 implementation（`storage.py:577-592`，`test_old_implementation_cannot_displace_new_current` 通过）。但"旧**快照**"维度**仍未关闭**——见 **F-01**，我已独立复现旧快照迟到发布覆盖新当前指针。该条意见的原始表述只覆盖实现来源，故判"部分关闭"而非"未关闭"。 |
| H-3 | null 重放配置仍标可重放（internal-review.md:9） | **已关闭** | `history()` 的 `replayable` 逐项校验类型、最大轮次范围 1–1000 与三项实现来源（`storage.py:703-725`）；`test_reference_check_and_incomplete_replay_are_explicit` 与 `test_scenario_round_cancel_isolation_replay_and_late_publication` 通过，缺失快照时如实为 `False`。 |
| H-4 | manual no-op 错误推进事实版本（internal-review.md:10） | **已关闭** | 完全相同的人工事实走 `continue` 分支，不写库、不推进 `facts:asserted`（`storage.py:296-299` 与 `:312-318`）；`test_explicit_manual_edits_multivalue_noop_and_single_slot:466-468` 断言向量不变。 |
| H-5 | round 空 operation/job（internal-review.md:11） | **已关闭** | `commit_round` 对空 operation/job 抛 `ValueError("operationId and jobId required")`（`storage.py:638-639`）；`test_reference_check_and_incomplete_replay_are_explicit:511-512` 覆盖。 |
| H-6 | 只有快照 Turtle 建图，缺规范事实 adapter 证据（internal-review.md:12） | **已关闭** | `rdf_snapshot.graph_from_snapshot` 从规范 facts 与 ontology triples 建图并过滤墓碑（`rdf_snapshot.py:51-66`）；`test_normalized_snapshot_rebuild_ignores_tombstones_preserves_old_input` 覆盖人工编辑与旧输入保留；测量探针亦已改用该 adapter（`storage_probe.py:93`），包内探针输出与 evidence 一致（V8/V9）。 |
| H-7 | RDF N3 词法等价绕过共同事实所有权（internal-review.md:13） | **已关闭** | `_fact` 要求对象严格等于 `term(value).n3()`，xsd:string / 语言标签统一后派生身份（`storage.py:185-189`、`rdf_snapshot.py:43-48`）；三引号、转义、显式 xsd:string 的跨映射/manual 反例回归通过（`test_rdf_lexical_alias_cannot_bypass_ownership`）。 |
| H-8 | storage_probe 的 Unix `resource` 导入与既有 Windows CI / 包内 health 兼容（`status.md:50`，开发者自记） | **仍未关闭** | 见 **F-02**：以 meta_path 模拟 Windows，`storage_probe` 与 `entrypoint` 均 `ModuleNotFoundError`；`ci.yml:44` 的 windows-latest 矩阵腿在 `engine:check` 阶段即失败。风险已被记录但未修复，也未登记为已关闭。 |

**结论**：历史问题 7 条中 6 条已关闭、1 条部分关闭（H-2 的快照维度转为本轮 F-01）；开发者自记风险 1 条仍未关闭（F-02）。

---

## 6. 最终结论

**不通过。**

- 阻断问题 **2 项未关闭**：F-01（迟到旧快照结果可覆盖更新的当前指针——违反 I01 冻结范围明文要求、S1 退出门槛与 PRD 附录 D.1，且 `acceptance.md` 对该点的覆盖声明不成立）、F-02（`import resource` 破坏既有 Windows CI 矩阵腿并使 Windows 包内引擎无法启动——本候选引入的跨平台回归）。
- 中等严重度问题 4 项：F-03（空/未解析依赖导致结果永不过期）、F-04（定义级 IRI/词法未在提交时校验，与 ADR-0002:29 声明不符）、F-05（迁移故障注入实际只覆盖一个点）、F-06（`Store` 构造无条件取写锁，只读打开也会被阻塞 5 秒后失败）。建议 F-03/F-04/F-06 与阻断项同批修复，F-05 可在下一候选补强。
- 低严重度问题 5 项：F-07～F-11，均给出明确处理结论，允许延期至对应迭代，但 F-10（实现兼容规则未进机器可读文件）建议随 F-03 一并处理。
- 静态、运行、打包、生产四类证据的区分在本候选中处理得当，未发现把占位能力、合成负载或存储替身冒认为完整业务基线的情况；Q5 未定亦未被自行设定容量线。
- 关键验收**无法在此轮判定为通过**：F-01 所涉"迟到结果拒绝发布为当前"是 I01 冻结范围内的明文验收项，当前实现未覆盖且经实测可复现反例；F-02 所涉 Windows 侧验证在本机不可执行，但失败条件已由导入链静态分析、模拟复现与官方文档三重锁定。

**后续要求**：修复 F-01、F-02（并建议同时修复 F-03、F-04、F-06）后**另起候选**（新 base→head），按 `scope.md` 统一门禁第 3、4 条重新执行双模型独立审查；不得沿用本轮任一方的通过意见，不得在修复未完成时 push 或合并。

---

### 附：本轮我实际执行的独立验证脚本

均位于 `/tmp/i01-review/`，不写入仓库：

- `probe_late.py` — F-01（旧快照迟到发布覆盖当前指针）
- `probe_windows.py` — F-02（Windows 无 `resource` 时的导入链失败模拟）
- `probe2.py` — F-03、F-04、F-07、F-11
- `probe3.py` — F-04（定义级校验隔离复现）、F-07、F-11
- `probe4.py` — F-08、F-09、F-11
- `probe5.py` — 乐观并发（通过）、`Store` 构造锁行为初现
- `probe6.py` — F-06（`Store` 构造无条件取写锁）
