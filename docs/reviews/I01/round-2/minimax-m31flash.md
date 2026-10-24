# I01 Round 2 独立对抗审查报告（MiniMax M3.1-Flash）

任务标识：`I01-R2-MiniMax-M31Flash-20261020-0548`
迭代：I01 / S1 / ADR-0002（源真相、隔离场景、不可变历史与可重建派生视图的存储及失效 spike）
受审范围：`e628f5e7b6c09e10e15644552a6171c4a9a3072e` → `3e787fb7f8923a0848c173215af2747861e4b35a`

---

## 0. 结论

**通过（无阻断问题；3 项中等、6 项低等，均可在本候选后关闭或延期至对应迭代）。**

本轮复审结论与首轮不同，理由是首轮两项阻断在本候选中经我独立复现均已关闭，且本候选没有引入新的阻断级回归：

- **F-01（首轮阻断）已关闭**：`publish()` 现在在事务内调用 `can_publish_current()`，同时校验依赖未失效 **且** `快照 projectRevision == 当前正式 revision`（`storage.py:679`）。我以首轮报告的原始反例路径独立复现（依赖未变、旧快照迟到发布），结果：迟到结果状态为 `historical`、`staleReason` 为空、当前指针未被覆盖。首轮报告的"当前指针被旧快照覆盖"已不可复现。
- **F-02（首轮阻断）已关闭**：`resource` 改为受保护导入（`storage_probe.py:21-24`），`entrypoint.py` 改为惰性导入探针模块，Windows 缺 `resource` 与缺 `storage_probe` 两种情形下 health 仍可用，且有独立子进程回归测试。`test_storage.py:867` 覆盖两模块。

**必须明确的保留意见**：`acceptance.md` 与 `ADR-0002-storage.md` 中若干条"已覆盖/已校验"表述，在本候选实际实现下**不成立或被过度声明**（详见第 4 节 M-01、M-02、N-02、N-03）。这些不是阻断项（不违反 I01 冻结范围的任何一条退出门槛，也未造成数据损坏或安全缺陷），但它们使验收文档的可信度低于其应有水平，按 `scope.md` 门禁第 4/5 条，后续任何据此文档推进的变更都必须新候选、双方重新审。

**我不采信开发者处理声明**：首轮 17 条意见的关闭状态全部由我在本候选上重新验证（见第 5 节），并另做 8 组对抗探针（`/tmp/i01r2/probe_a.py` … `probe_h.py`）独立复现边界行为。

---

## 1. 评审任务、模型及思考设置的来源记录

| 项目 | 值 | 来源性质 |
|---|---|---|
| 任务标识 | `I01-R2-MiniMax-M31Flash-20261020-0548` | 派发方（开发会话）声明，登记为流程参数。 |
| 模型 | MiniMax M3.1-Flash | **独立可观测**：本会话运行时自报 `Model: MiniMax-M3.1-Flash`、`agentName: mavis`。派发方另声明经 MiniMax Code UI 侧栏核验显示 `M3.1-Flash`。两者一致。 |
| 思考设置 | xhigh | **纯来源记录**。派发方声明 UI 显示 xhigh。我无法从会话内独立观测 UI 档位，本轮亦未使用 computer use 复核 UI 界面；该声明不作为任何通过依据。 |
| 项目目录绑定 | 完整绝对路径 `/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio` | **独立可观测**：本会话 cwd 即该路径，且我在其下成功执行了只读 git 操作与 `npm`/`uv` 验证。 |
| 分支 | `feature/I01-storage-invalidation` | **独立可观测**：`git rev-parse --abbrev-ref HEAD` 实测一致。 |
| 与其他模型互不披露 | 声称 | 我**未读取** `docs/reviews/I01/round-2/zcode-glm53.md`（该文件在本轮结束时已存在，27505 字节）。我仅在本轮对 `docs/reviews/I01/round-2/` 目录做了一次 `ls` 以确认报告落盘路径与工作区边界，未打开其内容。 |
| 内部 agent 复核 | `docs/reviews/I01/internal-review.md` | 仅作线索阅读；其结论不构成本报告任何判断的依据。所有关闭状态均由我独立复核。 |

**独立性声明**：本报告全部结论基于我直接读取的代码、需求原文，以及我自己执行的验证命令与对抗探针。

---

## 2. 项目路径、分支、base/head 与工作区边界

- 项目绝对路径：`/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio`
- 分支：`feature/I01-storage-invalidation`（实测）
- base SHA：`e628f5e7b6c09e10e15644552a6171c4a9a3072e`（实测可解析）
- head SHA：`3e787fb7f8923a0848c173215af2747861e4b35a`（`git rev-parse HEAD` 实测与派发候选一致）
- 固定范围共 **2 个提交**：`6d8e4b3 feat(I01): spike transactional storage and dependency invalidation`、`3e787fb fix(I01): harden publication, recovery and platform boundaries`；**67 个文件，+6961 / −2**（`git diff --stat` 实测）。
- 远端状态：无 push / PR / merge（`git log`、`git status` 与 `docs/reviews/I01/status.md:94` 一致）。
- 实现、测试、配置、依赖、验收相对候选 HEAD **无未提交差异**（`git status --porcelain` 实测：实现路径 0 项改动）。

**工作区边界核验（实测）**：`git status --porcelain=v1 -uall` 共 64 项。

- `docs/iterations/I01/preexisting-files.json` 登记的 **61 项本轮前文件，我逐项重算 SHA-256：61/61 一致，0 缺失、0 不匹配**。
- 64 项中，59 项落在该 61 项清单内；余下 5 项为本轮流程证据（`docs/reviews/I01/status.md` 追加、`docs/reviews/I01/round-2/frozen-source-check.txt`、`docs/reviews/I01/round-2/zcode-glm53.md`，及 2 份原型/审查类文档）。其中 2 份中文名文件在 porcelain 转义下未被我的路径集合匹配到，经单独核对**存在于磁盘、且已登记在 61 项清单内**（`docs/reviews/M0深度审查_采纳评估_2026-10-19.md`、`docs/reviews/OntoLearn-Studio-Prototype_原型遗留三项修复与验证_第五轮_2026-10-19.md`），并非遗漏或夹带。
- 派发说明的"61 项"与实测 64 项的差异由上述流程证据完全解释。
- **我未修改、未暂存、未还原、未清理任何仓库文件**；未 stage 任何内容。全部对抗探针脚本写在 `/tmp/i01r2/`（7 个文件），独立打包产物写在 `/tmp/i01r2-wheel/`。本报告是本轮唯一新增的仓库文件。

---

## 3. 已检查范围、验证命令与实际结果

### 3.1 需求依据（逐条读取原文，非依赖开发者摘要）

- `AGENTS.md`（10 条开发规则全文）
- `docs/iterations/I01/inputs/scope.md`：I01 冻结范围表格行、顺序清单、统一门禁第 1–8 条
- `docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md`：**S1 全章（第 28–62 行）**，含 4 张存储责任表、3 类版本区分、交付定义、S1 退出门槛 1–6
- `docs/iterations/I01/inputs/goal-objective.md`、`inputs/M0深度审查_采纳评估_2026-10-19.md`、`inputs/sources.json`
- `docs/prd/PRD-本体学习与落地Agent工作台.md` V0.6：FR-006（第 256–270 行）、FR-304（361–370）、FR-604（471–473）、FR-700～705（477–501）、FR-804（521–531）、FR-1000（569–588）、**附录 C（959–979）、附录 D D.1/D.2（983–1012）、附录 E E.1～E.5（1016–1092）、附录 G G.0～G.6（1115–1254）**
- `docs/iterations/I01/ADR-0002-storage.md`（60 行全文）、`docs/iterations/I01/acceptance.md`（72 行全文）——**作为被审对象，不作为通过依据**

**冻结输入完整性**：`inputs/sources.json` 登记的 4 份副本 SHA-256 **4/4 逐位一致**（我独立复算）。`preexisting-files.json` 61 项 **61/61 一致**。

### 3.2 实现检查范围

`packages/engine/src/ontolearn_engine/`：`storage.py`（935 行，全文）、`invalidation.py`、`invalidation-v2.json`、`rdf_snapshot.py`、`storage_probe.py`、`entrypoint.py`、`protocol.py`、`__main__.py`、`__init__.py`；`packages/engine/tests/`：`test_storage.py`（993 行，全文）、`storage_baselines.py`（220 行，全文）、`test_protocol.py`（11 项，未改动）；`packages/engine/pyproject.toml`、`uv.lock`、`scripts/build-engine.mjs`、`scripts/verify-i01.py`、`scripts/verify-sources.mjs`、`.prettierignore`、`.github/workflows/ci.yml`；`docs/iterations/I01/evidence/round-2/` 全部 19 个文件；`docs/reviews/I01/round-1/` 全部 3 个文件；`docs/reviews/I01/internal-review.md`、`status.md`、`frozen-source-check.txt`。

### 3.3 验证命令与实际结果（均为我本轮亲自执行）

| # | 命令 | 实际结果 |
|---|---|---|
| V1 | `git rev-parse HEAD` / `--abbrev-ref HEAD` | `3e787fb7f8923a0848c173215af2747861e4b35a` / `feature/I01-storage-invalidation` ✅ 与候选一致 |
| V2 | `git diff --stat e628f5e..3e787fb` | 67 文件，+6961 / −2，2 个提交 ✅ |
| V3 | `npm run check` | **EXIT=0**：eslint 0 warn、prettier 通过、tsc 通过、**vitest 4 passed**、electron-vite 构建成功、ruff 通过、**pytest 160 passed in 5.24s**（test_protocol 11 + test_storage 149）✅ 与 evidence/round-2/check.txt 逐项一致 |
| V4 | `npm run verify:sources` | **EXIT=0**，"已核对 13 个归档源文件" ✅ |
| V5 | `npm run test:e2e` | **EXIT=0**，1 passed（桌面真实引擎 health + 隔离 + 最小窗口）✅ |
| V6 | `shasum -a 256 release/mac-arm64/.../ontolearn-engine` | `ddd465de1a1df8c89b10b63efc8155c8a3c17df7cf36479e0f866eef2cfe7f7c` —— 与 `evidence/round-2/package-manifest.json` 登记值**逐位一致** ✅ |
| V7 | 包内探针（`PATH=/usr/bin:/bin`、剔除 `PYTHONPATH`/`PYTHONHOME`）`--storage-probe --scale 1 --trial 0` | `inputSha256=b0bcc466774f…`、`querySha256=7879b25f2833…`、`snapshotId=71930b09f264…`、`result=["urn:case:0:alarm/A01"]`、`triples=18`、`rdflib=7.6.0` —— 与 `evidence/round-2/packaged-1x-0.json` **完全一致** ✅ 包内同样例成立 |
| V8 | 包内 health（同一受限环境） | `{"ok":true,…,"capabilities":["health"]}` ✅ 仅声明 health，未虚增能力 |
| V9 | evidence/round-2 交叉核对 | 12 条测量（development 1x/10x ×3 + packaged 1x/10x ×3）；**同 scale 跨 6 条 `inputSha256`/`querySha256`/`result`/`snapshotId`/`triples` 完全相同**；triples 18/180；`rssAvailable=true`；rdflib 7.6.0 ✅ |
| V10 | 包内目录清单实测 | 25,120,774 字节 / 154 文件 —— 与 manifest 登记**完全一致** ✅；包内含 `rdflib-7.6.0.dist-info/LICENSE`、`pyparsing-3.3.3.dist-info/licenses/LICENSE`、`ontolearn_engine/invalidation-v2.json` ✅ 资源许可证与机器可读规则均实际入包 |
| V11 | 61 项本轮前文件 SHA-256 复算 | **61/61 一致**，0 缺失、0 不匹配 ✅ |
| V12 | 冻结输入 4 份 SHA-256 复算 | **4/4 一致** ✅ |
| V13 | 独立对抗探针 7 组（`/tmp/i01r2/probe_a.py`…`probe_h.py`） | 见第 4 节各项证据；**M-01、M-02、N-02、N-03 均被独立复现** |
| V14 | 独立构建 wheel（`uv build --out-dir /tmp/i01r2-wheel`） | wheel 内含 `ontolearn_engine/invalidation-v2.json` ✅ 机器可读规则随包分发，不依赖仓库相对路径 |
| V15 | `uv sync --frozen --dry-run` | "Would make no changes"，锁文件自洽 ✅ |

### 3.4 未验证事项（如实声明，不作推断）

1. **Windows CI 实际运行**：本机为 macOS arm64，无对应主机。F-02 的修复我通过源码审查 + 仓库自带子进程回归测试（`test_storage.py:866-895`）确认其逻辑闭合，但**未在 Windows 上实跑 CI**。CI 中 `desktop` job（`.github/workflows/ci.yml:39-63`）的 `windows-latest` 腿仍待 PR 后核验。
2. **Linux 打包产物与跨平台动态链接**：未验证。
3. **干净设备、无系统 Python、断网安装、签名**：未验证（ADR 与 manifest 的 `scope` 字段已如实声明）。
4. **完整业务执行器**：CSV 导入/预览 UI、行为触发与冻结条件、资源阶段、E.2 轮次执行器、SHACL、RDFS/规则组合、解释 UI 均未实现，属 I05/后续业务。**本报告不把存储测试视为完整业务通过**。
5. **100× 合成档**：计划中标注"按资源余量选做"，本候选未做；证据如实只含 1×/10× 两档。
6. **Q5 容量线**：未定。本候选未自设任何容量通过线，测量仅为原始记录。
7. **`npm run package:dir` 未由我重跑**：我复用了 `release/mac-arm64` 现存产物，以其二进制 SHA-256、目录字节数、文件数与 manifest 登记值三项逐位一致作为佐证，并以 V7/V8 实际执行包内探针与 health 证明该产物可用。`--collect-all rdflib` 等构建改动的间接验证依赖该产物，未独立重建。
8. **`scripts/verify-i01.py` 未由我重跑**：其产物（12 条测量、manifest、licenses、dynamic-linkage）我已逐项与实际产物/探针输出交叉核对一致（V7、V9、V10）。

---

## 4. 问题清单

严重程度定义：**阻断** = 违反 I01 冻结范围 / S1 退出门槛 / PRD 主定义，或造成数据损坏、安全缺陷、既有链路回归；**中** = 实现与自身文档声明不符，或存在无护栏的语义缺口，可能误导下游；**低** = 边界语义、文档精度或错误面问题，不影响本轮验收结论。

本轮共 **9 项**：0 阻断、3 中、6 低。全部给出处理结论。

---

### M-01 ［中］墓碑与 `edits` 之后，第二来源对同一语句的所有权冲突抛裸 `sqlite3.IntegrityError`，而非 `Conflict`

- **位置**：`packages/engine/src/ontolearn_engine/storage.py:497-577`（`_replace_mapping`），关键在 `:575-576`（`DELETE` 后 `executemany INSERT`）；`storage.py:471-495`（`_check_slot`）在 `:489` 以 `row["object"] is not None` 跳过墓碑行。
- **触发条件**：
  1. 受管事实被人工删除（`remove`）→ 墓碑行 `object=NULL`，但**行仍在，`id` 仍为原语句的内容派生摘要**；
  2. 另一来源（不同 `owner`）提交**同一语句**（相同 subject/predicate/object → 相同 `id`）；
  3. 或：受管事实被 `edits` 改值后（`object` 已变、`id` 仍为**原始**内容摘要），另一来源提交该**原始**语句。
- **影响**：
  - 违反 `ADR-0002-storage.md:57` 自订错误契约（"Conflict 表示基线/所有权/轮次身份冲突"）与 `scope.md` I01 行"多来源与人工冲突"的可定位要求：调用方拿到的是 `UNIQUE constraint failed: facts.project, facts.id`，**无法区分"多来源所有权冲突"与"存储内部缺陷"**；PRD FR-304 要求"发现此类所有权冲突时必须说明并阻止提交"——此处**阻止了**（事务回滚、revision 未推进、无 marker），但**未说明**。
  - 对照实验（同一语句、非墓碑）走 `_check_slot`，抛出可定位的 `Conflict: Ownership conflict: slot=urn:equipment/001 urn:name, other=M1, row=001`。**同一语义冲突在墓碑/编辑后走不同分支、给出不同错误形态**，是实现内部的不一致。
  - 数据完整性未受损：实测回滚后 revision 保持 2、无 marker、`facts` 表未变。
- **证据**（我本轮独立探针 `/tmp/i01r2/probe_c.py` C1 与 `/tmp/i01r2/probe_g.py` G1）：
  ```
  === 墓碑 + 第二来源 ===
  tombstone row id == content digest of the ORIGINAL statement: True
  M2 stages the SAME statement -> same id -> PK collision
    RAW sqlite3.IntegrityError: UNIQUE constraint failed: facts.project, facts.id
    -> rollback ok -> revision: 2  marker(other-owner): None
  === 对照：非墓碑 + 第二来源 ===
    Conflict: Ownership conflict: slot=urn:equipment/001 urn:name, other=M1, row=001
  === edits 后 + 第二来源提交原始语句 ===
    RAW sqlite3.IntegrityError: UNIQUE constraint failed: facts.project, facts.id
  ```
  **注**：此行为在首轮候选中已存在（`git show 6d8e4b3:…/storage.py` 确认 `_check_slot` 的 `object is not None` 与 `remove` 的 `object=NULL` 墓碑逻辑未变），**首轮两份报告均未覆盖此路径**。本轮为新发现，非本候选引入的回归。
- **建议**：
  1. 在 `_check_slot` 中对墓碑行也执行所有权判定（墓碑同样占用该 subject+predicate 槽位与该内容派生 `id`），使第二来源稳定得到 `Conflict`；
  2. 或在 `_replace_mapping` 的 `executemany` 处捕获 `sqlite3.IntegrityError` 并转换为带 slot/owner/row 的 `Conflict`；
  3. 补回归：墓碑 + 第二来源、`edits` 后 + 第二来源提交原始语句，两者均须得到可定位 `Conflict` 且事务回滚。
- **处理结论**：**建议在本候选后关闭**。它不违反 I01 冻结范围中任何一条明文退出门槛（"多来源与人工冲突"条目要求的是阻止与定位，阻止成立、定位在本路径失效），也未造成数据损坏；故不构成阻断。但 `acceptance.md:10` 声称"多来源共同事实拒绝"已被覆盖，**该声明在本路径上不成立**，需与 M-02 一并修正或由本条修复兑现。

---

### M-02 ［中］`acceptance.md` 与 `ADR-0002-storage.md` 多处"已覆盖/已校验"表述超出本候选实际实现

- **位置**：`docs/iterations/I01/acceptance.md:10`、`:11`、`:14`、`:44`、`:64`、`:68`；`docs/iterations/I01/ADR-0002-storage.md:27`、`:29`、`:39`、`:56`。
- **触发条件**：按文档字面理解验收。
- **影响**（逐条对照我实测的实际实现）：

  | 文档表述 | 实际实现 | 判定 |
  |---|---|---|
  | `acceptance.md:44`："G.2 Q-01｜真实固定 SELECT，G-base 结构合成事实中完整结果仅 A01" | 固定 SELECT 跑在 `storage_probe.py` 的**独立合成孪生**（`urn:ontolearn:` 命名空间、`rdf:type`）上，**不是**存储的 G-base 基线。存储的 G-base 用 `urn:type`/`urn:level` 等自有谓词，其本体为 JSON 类/属性列表，**重建后无 rdf:type、无 rdfs:subClassOf、无 SHACL 形状**（我实测 F1：18 triples，`rdf:type` 计数 0，`subClassOf` 计数 0） | 表述可读作"合成事实"，但"真实固定 SELECT"与 G-base 的关联被暗示；G-base 本身**未**经 RDF 重建与固定查询验证 |
  | `acceptance.md:14`："缺失或格式不完整输入不标为可重放" | `start_run` 只校验 `snapshot["project"]` 匹配，**接受轮次快照**（payload 键为 `project/run/round/state`，无 `projectRevision`、无 `dependencyVector`）；`history()` 随后判 `replayable=True`（我实测 E3/C2） | **不成立** |
  | `acceptance.md:64`："领域依赖未变（仅模型配置变更）后，新 revision 的结果已发布，旧 revision 晚完成也只能为 historical" | 成立（V13/D1 复现） | ✅ 成立 |
  | `acceptance.md:68`："墓碑经显式确认后的 edits 恢复后可重新映射" | 成立（我实测 D2：恢复后 owner 重跑成功、`mapping_status` 干净） | ✅ 成立 |
  | `ADR-0002-storage.md:27`："显式 `edits={factId:object}` 保持记录身份与映射基线" | 成立，但**未说明副作用**：`edits` 后 `facts.id` 不再等于当前内容摘要（我实测 G1），内容派生身份不变量被打破 | 表述正确但遗漏关键副作用 |
  | `ADR-0002-storage.md:56`："缺失或形状不全明确 false" | 依赖键缺失已严格拒绝（我实测 D4：空列表/未登记/非字符串键全部 `ValueError`），但**输入快照形状**缺失未被检查 | 需限定为"依赖键与配置形状" |
  | `ADR-0002-storage.md:39`："要求输入快照 projectRevision 等于当前正式 revision" | 成立（`can_publish_current` 实测） | ✅ 成立 |

- **证据**：`/tmp/i01r2/probe_f.py` F1（存储 G-base 重建结果与探针孪生的谓词集对比）、`/tmp/i01r2/probe_e.py` E3、`/tmp/i01r2/probe_g.py` G1。
- **建议**：
  1. `acceptance.md:44` 明确区分"存储 G-base 基线（JSON 定义 + `urn:` 谓词，**未**经 RDF 重建/固定查询）"与"探针合成孪生（`urn:ontolearn:` 命名空间 + `rdf:type`，**是**固定 SELECT 的实际对象）"；两者不可互称"真实固定 SELECT / G-base"。
  2. `acceptance.md:14` 与 `ADR-0002-storage.md:56` 补入 N-02（输入快照形状未校验），或在实现中补校验。
  3. `ADR-0002-storage.md:27` 补记 `edits` 后 `id` 与内容摘要解耦的后果（与 M-01 关联）。
- **处理结论**：**建议在本候选后关闭**（文档修正即可，无需改实现的部分属低风险）。文档精度问题本身不构成阻断——`scope.md` 门禁第 4 条要求"逐项记录采纳/部分采纳/不采纳/延期与证据"，本轮记录的是**证据与实际实现不符**，属于必须修正的记录问题。**若不修正，后续 I03/I04 会以这些表述为契约前提实现，属实质风险**，故不建议长期延期。

---

### N-01 ［低］`publish()` 以轮次快照为输入时抛裸 `KeyError: 'dependencyVector'`

- **位置**：`storage.py:614-684`（`publish`），`:630`（`load_snapshot`）→ `:653`（`snap["dependencyVector"]`）。
- **触发条件**：`publish(project, round_snapshot, ...)`。
- **影响**：错误形态为 `KeyError`，而 `ADR-0002-storage.md:57` 规定 `KeyError` 表示"读取身份缺失"，此处身份存在、**形状不符**，语义错配。事务正确回滚，无数据损坏。
- **证据**：`/tmp/i01r2/probe_e.py` E4 → `RAW KeyError: KeyError('dependencyVector')`。
- **建议**：`publish` 入口校验输入快照形状（须含 `projectRevision`/`dependencyVector`/`state`），形状不符抛 `ValueError`。
- **处理结论**：可延期至 I03/I04 的统一错误映射；不阻断。

---

### N-02 ［低］`start_run` 接受轮次快照作为运行输入，`history()` 判 `replayable=True`

- **位置**：`storage.py:762-773`（`start_run`）、`storage.py:857-891`（`_history`），`:874-888`（`replayable` 判定）。
- **触发条件**：`start_run(project, round_snapshot, config, implementation)`。轮次快照 payload 键为 `project/run/round/state`。
- **影响**：`replayable` 判定只检查 config 形状、implementation 键与"快照可加载"，**不检查输入快照是否为项目状态快照**。结果：一个绑定到轮次快照的运行被标为 `replayable=True`，而其输入不含 `projectRevision`/`dependencyVector`/`state.definitions`。PRD FR-703 要求运行须记录"项目版本、输入快照、规则与行为版本、参数、事件、执行语义版本和逐轮状态"，G.6 要求"只有沙盘输入、配置、行为/规则版本和执行语义版本齐全时，才可标记为可重放沙盘运行"。此处**输入形状不齐却标为可重放**。
  - 补充事实：FR-703 的"规则与行为版本"在当前实现中只能由调用方以 `config.ruleVersions/behaviorVersions` 自行填入，存储层**不与实际 `versions` 表交叉核对**（我实测 C4：项目实际有 `rule:R-risk` 版本 1，而 config 填空字典仍判 `replayable=True`）。存储层无法证明调用方未漏报——`ADR-0002-storage.md:9` 已诚实声明"完整依赖集合由 I03 能力契约强制派生"，故本条只针对**输入快照形状**这一存储层可自证的缺口。
- **证据**：`/tmp/i01r2/probe_e.py` E3：
  ```
  run2 input snapshot == round snapshot: True
  replayable: True
  bound input payload: ['project', 'round', 'run', 'state']   ← 缺 projectRevision / dependencyVector
  ```
- **建议**：`start_run` 校验输入快照须含 `projectRevision`/`dependencyVector`/`state`，否则 `ValueError`；`replayable` 相应要求输入为项目状态快照。
- **处理结论**：可延期至 I03（能力契约与运行绑定语义落地时一并收紧）；不阻断。

---

### N-03 ［低］"当前"指针采用"最新 revision 胜出"，可致某业务种类长期没有 current 结果

- **位置**：`storage.py:679`（`can_publish_current`）、`invalidation.py:31-35`、`invalidation-v2.json:61-70`（`publicationPolicy`）。
- **触发条件**：某 `kind` 的**首个**结果在快照 revision R 上算出，其后发生过一次**与该结果无关**的提交（例：新增一条 query 定义），使正式 revision 变为 R+1；该结果随后发布。
- **影响**：结果被判为 `historical`、`staleReason` 为空、**该 kind 没有任何 current 结果**。PRD D.1 定义"当前"为"输入和依赖版本均未变化"；本实现额外要求"快照 revision 等于当前正式 revision"，比 D.1 更严。后果是：语义上完全有效的新鲜计算被静默降级为历史，用户/Agent 看到的是"没有当前结果"而非"有当前结果"。
  - 客观地讲，此设计**保守且不违反 D.1**（D.1 是"可作为当前结果使用"的定义，未禁止更严的发布策略），且 F-01 的修复正是依赖这一严格性阻止旧快照覆盖新指针（我实测 D1 复现）。因此本条**不是缺陷**，而是需要下游知情的语义选择。
  - 附带观察：`commit()` 对**语义为空**的提交（重复提交同一份定义）仍推进 `projectRevision`（我实测 H2：向量不变、revision 1→2→3）。`ADR-0002-storage.md:55` 已声明"projectRevision 对每个成功 operation 推进"，与实现一致，不构成不一致；但会放大 N-03 的触发频率。
- **证据**：`/tmp/i01r2/probe_h.py` H1 → `result state: historical`、`current for kind 'query': None`；H2 → 向量不变而 revision 递增。
- **建议**：在 ADR 中显式记录"发布资格采用快照 revision 与正式 revision 相等"这一**已选择的、比 D.1 更严**的策略及其后果（某 kind 可能没有 current 结果），供 I03/I04 决定是否保留；`commit()` 是否推进 revision 对无语义变化的提交可另行评估。
- **处理结论**：**建议在下一候选以文档方式补记**（低风险）。不阻断。

---

### N-04 ［低］`collect_cache` 会清空**已过期（stale）**结果载荷

- **位置**：`storage.py:748-760`（`collect_cache`），`:755` 的排除条件仅含 `result_pins` 与 `current_results`。
- **触发条件**：结果已 stale（不在 `current_results` 中）、未被报告 pin → 载荷被置 NULL。
- **影响**：PRD D.1 定义"已过期"为"上游已变化，**结果保留供查看**"。回收后该结果仅剩 `dependencies`/`stale` 元数据，载荷不可查看。S1 计划"只有未被历史/报告固定引用且可安全重建的载荷可回收"允许回收可重建载荷，故**不违反冻结范围**；但与 D.1 的"保留供查看"存在张力。
  - 客观地讲：stale 结果本就是过期计算结果，其载荷可由快照重建；D.1 的"保留供查看"更可能指"保留该结果条目及其过期原因与重跑入口"，本实现**保留了条目、原因与依赖**。因此本条属**边界语义**，非缺陷。
- **证据**：`/tmp/i01r2/probe_a.py` H16 → `payload after collect: None`、`deps still available: {'facts:asserted': 1}`。
- **建议**：在 `acceptance.md:11` 的"缓存回收安全"一栏补一句说明"已过期结果的载荷可被回收，条目/原因/依赖保留"，避免下游误以为过期结果长期可查看。
- **处理结论**：可延期；如与 M-02 一并修订文档则一并解决。不阻断。

---

### N-05 ［低］G-map-empty 固定 CSV 的**两行**完整集合在仓库测试中从未被构造

- **位置**：`packages/engine/tests/test_storage.py:40-41`（`mapped()` 助手恒定只产出一行 `row="001"`）；`packages/engine/tests/storage_baselines.py:118-155`。
- **触发条件**：按 PRD G-map-empty 固定 CSV（`001,泵站A` / `002,泵站B`）执行 M-01。
- **影响**：PRD G.1 M-01 的预期是"**恰好**生成 `equipment/001`、`equipment/002` 及名称"。仓库测试从未构造 `002` 行（`grep 002` 在 `test_storage.py` 中只命中一处，且是 `W002` 工单号，与映射行无关）。因此"恰好两个实体"这一集合完整性断言在仓库内**无回归保护**。
  - 存储层**本身能表达**该完整集合：我实测（H3）提交两行固定 CSV 后，得到 `[('urn:equipment/001','"泵站A"','001'), ('urn:equipment/002','"泵站B"','002')]`，与 PRD 预期一致；`source_row` 正确保留。因此这是**测试覆盖缺口**，非实现缺陷。
  - `acceptance.md:42` 已声明"G.1 M-01/02/03/04/06 … 未执行 CSV 导入/预览 UI；不能标为完整业务通过"，其"完整预期"一栏指向 prepared mapping 计划。文档未越界，但 S1 退出门槛 6 要求"逐项记录实测范围与完整预期集合/顺序"，固定 CSV 的两行集合未进入任何回归。
- **证据**：`/tmp/i01r2/probe_h.py` H3/H4（能力成立）与 `grep -n "002" packages/engine/tests/test_storage.py`（仅 1 处且无关）。
- **建议**：新增一条以固定 CSV 两行为输入的测试，断言实体集合恰为 `{001, 002}`、`source_row` 分别为 `001`/`002`、重复执行集合不变（M-02）。
- **处理结论**：可延期至 G.1 业务用例实现时；建议在本候选后顺手补入（成本极低）。不阻断。

---

### N-06 ［低］`finish_run` 重复插入抛裸 `sqlite3.IntegrityError`

- **位置**：`storage.py:844-851`。
- **触发条件**：对同一 `run` 调用两次 `finish_run`。
- **影响**：与 F-11 同族。`ADR-0002-storage.md:57` 已登记"重复 pin/终态插入可抛唯一性错误"，属**已声明的现状**，本候选未扩张该面。事务回滚正确。
- **证据**：仓库测试 `test_schema_cannot_overwrite_history_and_missing_snapshot_is_honest:378` 断言 `sqlite3.IntegrityError`；`probe_d.py` D7 确认 `run_terminal` 的 UPDATE/DELETE 被 SQL 触发器拒绝（`immutable evidence`）。
- **建议**：随 F-11 的 I03/I04 统一错误映射一并处理。
- **处理结论**：**允许延期**至 I03/I04（与 F-11 同一处理结论）；不阻断。

---

### N-07 ［低］`Store.snapshot()` 持写锁，与其他写者竞争时超时抛裸 `OperationalError`

- **位置**：`storage.py:588-596`（`snapshot`）经 `:54-67` 的 `_transaction` → `BEGIN IMMEDIATE`。
- **触发条件**：另一连接持写锁时调用 `snapshot()`。
- **影响**：读语义的"取快照"操作需要写锁，5 秒后抛 `sqlite3.OperationalError: database is locked`。这是首轮 F-06 的**同类但不同入口**：F-06 关注的是**打开**数据库即取写锁，该问题已由 `storage.py:73-74`（当前格式直接 return，不开事务）修复；但 `snapshot()` 自身仍取写锁。属首轮 R4"锁竞争错误形状"的同一延期项（"普通写锁竞争的裸 SQLite 错误按 F-11 延期到 I03 错误映射，文档明确现状"）。
- **证据**：`/tmp/i01r2/probe_b.py` B11 → `snapshot() -> OperationalError after 5.21s: database is locked`。
- **建议**：随 F-11/R4 的 I03 错误映射处理；如需，可在 `_transaction` 上区分读写意图。
- **处理结论**：**允许延期**至 I03/I04；不阻断。

---

### N-08 ［低］`collect_cache` 不回收已 pin 报告的结果，但**当前**结果亦被排除在回收之外且其载荷保留——与文档一致（确认项）

- **位置**：`storage.py:748-760`。
- **影响**：复核 `acceptance.md:11`"固定报告和历史轮次在缓存回收后完整"这一断言：实测 pinned 结果载荷保留（仓库测试 `test_multiple_reasons_late_result_cache_isolation_and_history:249` 断言 `db.result(old)["payload"] == ["risk"]`），历史轮次位于 `rounds`/`snapshots` 且有 SQL 不可变触发器保护，不受 `collect_cache` 影响（`collect_cache` 只改 `results.payload`）。断言**成立**。
- **证据**：`probe_d.py` D7（6 张历史表 UPDATE/DELETE 全部被拒）+ 仓库测试通过。
- **建议**：无需修改。
- **处理结论**：**无需处理**（确认为已正确实现，防止下游误改）。

---

## 5. 历史 17 条意见逐项关闭判断

来源：`docs/reviews/I01/round-1/processing.md`（开发者处理声明）＋ MiniMax Round 1 报告 11 条（F-01…F-11）＋ ZCode Round 1 报告 6 条（R1…R6）＝ 17 条。以下判断**由我在本候选上重新验证**，不采信处理声明。

### 5.1 MiniMax Round 1（11 条）

| 编号 | 原严重度 | 开发者处理 | **我的判断** | 依据（我本轮实测/阅读） |
|---|---|---|---|---|
| F-01 旧快照迟到覆盖新当前 | 阻断 | 采纳 | **已关闭** | `storage.py:679` 引入 `can_publish_current`（`invalidation.py:31-35`），要求依赖未 stale **且** 快照 revision == 当前正式 revision。probe D1 精确复现首轮反例：迟到发布后 `current` 仍指向较新结果、迟到结果 `state=historical`、`stale=[]`。首轮报告第 129 行的"LATE rev1 OVERWROTE NEWER rev2 CURRENT: True"**不再复现** |
| F-02 Unix `resource` 破坏 Windows | 阻断 | 采纳 | **已关闭**（本机模拟层面） | `storage_probe.py:21-24` 受保护导入 + `resource=None` 时 RSS 为 null 且 `rssAvailable=false`；`entrypoint.py` 惰性导入探针；`test_storage.py:866-895` 以 `meta_path` 拦截 `resource` 与 `ontolearn_engine.storage_probe` 两种情形，health 仍返回 `capabilities:["health"]`。**实际 Windows CI 仍待 PR 后核验**（未验证项 3.4-1） |
| F-03 空/未解析依赖永不过期 | 中 | 采纳 | **已关闭** | probe D4：`[]`、`["query:unknown"]`、`["rule:unknown"]`、`["facts:asserted","scenario:unknown"]`、`[42]` 全部 `ValueError`；`facts:asserted` 作为空项目显式范围被保留。仓库另有 `test_unregistered_or_empty_dependencies_cannot_be_published` |
| F-04 定义级 IRI/词法未校验 | 中 | 采纳 | **已关闭** | `storage.py:409-435` `_definition()` 在 `commit` 内逐定义校验 `references`/`triples`/`singleValuedPredicates`；`storage.py:456-469` `_validate_references` 复核。仓库 `test_invalid_ontology_triples_fail_in_commit_not_later_graph_build` 覆盖 4 类非法三元组并断言同批 `manual` 事实一并回滚 |
| F-05 迁移故障注入单点 | 中 | 采纳 | **已关闭** | `storage.py:69-132` 注入点扩至 11 个（`before`…`after_commit`）＋ 4 个 v0 点；`test_storage.py:704-761` 对 11 点 × (exception, 真实子进程 `os._exit`) 全部断言 DDL/版本/数据回滚或提交后保持 v2、重开可重试 |
| F-06 当前格式开库也取写锁 | 中 | 采纳 | **已关闭** | `storage.py:73-74` 当前格式直接 return，不进事务；`test_storage.py:764-774` 在他方持 `BEGIN IMMEDIATE` 时成功打开并读取。**残留**：`snapshot()` 自身仍取写锁 → 本轮新编号 N-07（首轮 R4 同一延期项） |
| F-07 提交后异常拿不到成功返回 | 低 | 部分采纳 | **已关闭（按其登记语义）** | `ADR-0002-storage.md:31` 明文"必须另外通过 `marker(project,operation)` 对账"；probe D3：`after_commit` 抛错后 marker 存在、revision=2、数据已提交、同 operation 重试返回**同一 marker** 且无重复写入。专用异常类型明确留给 I03/I04（与 F-11 同一处理结论） |
| F-08 墓碑重跑阻断/恢复未文档化 | 低 | 采纳 | **已关闭** | `ADR-0002-storage.md:29` 明确"人工修改**或人工删除（墓碑）**…重跑停止"及"恢复路径是一个新的、预览并单独确认的 ChangeSet，通过 `edits={factId:managed_value}` 显式放弃人工值或人工删除"。probe D2：墓碑后重跑 → `Conflict: Manual drift`；经 `edits` 恢复后 owner 重跑成功、`mapping_status` 干净。**本轮另发现该路径的副作用** → M-01（不改变 F-08 本身的关闭判断） |
| F-09 单值并集语义/基线字段惰性 | 低 | 采纳 | **已关闭** | `ADR-0002-storage.md:29` 写明唯一执行格式为 ontology 顶层 `singleValuedPredicates` 绝对 IRI 列表、作用域为全项目并集、`properties.*.single` 不作执行约束；`storage_baselines.py:67` G-behavior 已补 `singleValuedPredicates:["urn:P","urn:workOrderStatus"]` 真实字段；`storage.py:447-454` `_validate_single_slots` 在提交内拒绝与既有事实冲突的新声明。仓库 `test_explicit_manual_edits_multivalue_noop_and_single_slot` 覆盖多值并存与单值冲突 |
| F-10 实现兼容规则未机器化 | 低 | 采纳 | **已关闭** | `invalidation-v2.json` 增 `implementationCompatibility`（identityKeys/default=isolate/reuse=disabled_in_S1/staleReason=null）与 `publicationPolicy`（staleReason=null）；`storage.py:624` 从 `RULES` 读取 identityKeys；`invalidation-v1.json` 已随本候选删除（`git ls-tree` 确认 HEAD 仅存 v2），无残留引用 |
| F-11 错误面不统一/未知删除 no-op | 低 | 延期并补文档 | **已关闭（按其登记语义）** | `ADR-0002-storage.md:57` 已登记现状：`Conflict`=基线/所有权/轮次身份冲突、`ValueError`=存储形状错误、`KeyError`=读取身份缺失；SQLite 唯一性错误可原样抛出；未知事实删除为可审计 no-op。**本轮实测未发现该登记之外的新错误面扩张**；但发现 N-01（`KeyError` 用于形状不符而非身份缺失）与 M-01（所有权冲突抛裸唯一性错误）——二者属**本轮新问题**，不改写 F-11 本身的关闭判断，但说明其登记范围需在下一版 ADR 补充 |

### 5.2 ZCode Round 1（6 条）

| 编号 | 原严重度 | 开发者处理 | **我的判断** | 依据 |
|---|---|---|---|---|
| R1 operation/job 类型校验 | P3 | 采纳 | **已关闭** | `storage.py:226-229`：`type(base) is not int`（拒 bool）、operation/job 必须非空字符串；`storage.py:785-788` 轮次同样校验；`test_storage.py:810-816` 覆盖 `12345/True/None/""` |
| R2 轮次重试及跨运行复用 | P3 | 采纳 | **已关闭** | `storage.py:797-808`：按 operation 查既有轮次，同 run/number/job/内容返回原快照，异内容或跨 run 抛 `Conflict`（不再抛裸 `IntegrityError`）；probe B9 跨项目复用亦得 `Conflict`；`test_storage.py:819-839` 覆盖响应丢失后幂等重试、跨运行、内容不符、终态后只返回既有证据 |
| R3 净零事实过度失效 | P3 | 采纳 | **已关闭** | `storage.py:285-286` 重复墓碑删除 `continue`；`storage.py:340-361` 按提交前后事实/owner/映射定义的净变化决定是否推进 `facts:asserted` 与 mapping 键。probe H2：重复提交同一份定义 → 依赖向量不变；probe D5：仅模型配置变更 → 结果 `stale=[]`、状态仍 `current` |
| R4 迁移 TOCTOU 及锁错误 | P3 | 部分采纳 | **部分关闭 / 剩余部分允许延期** | TOCTOU 已修（`storage.py:77-83` 在写锁内重读版本；`test_storage.py:777-807` 交错回归）。剩余"锁竞争抛裸 `OperationalError`"按其登记延期至 I03/I04 错误映射 → 本轮对应 N-07。**延期不影响本轮通过** |
| R5 映射循环重复查询 | P3 | 采纳 | **已关闭** | `storage.py:514-520`：`own_ids` 与 `single_predicates` 在循环外预取，槽位集合复用；`storage.py:550-552` 用 `staged_slots` 判单值多值。**文档未作倍数或时延承诺**，与处理声明一致 |
| R6 全量快照增长 | P3 | 延期 | **允许延期** | `ADR-0002-storage.md:59` 明确"完整前后快照和保守保留继续作为正确性优先的 spike 选择…Q5 未定，不宣布容量达标"。属已登记的已知权衡，不阻断。**本轮未发现该权衡被突破**（`commit` 仍只写前后两个内容寻址快照） |

### 5.3 汇总

- **17 条中 15 条已关闭，2 条部分关闭/延期**（R4 的 TOCTOU 已修、锁错误形状延期；R6 全量快照增长延期）。
- **首轮两项阻断（F-01、F-02）均已关闭**，且我以独立探针在**未修复**路径上未复现任何等价缺陷。
- **无任何一条历史意见被"沿用旧版通过"**：上表每一行的判断都基于本候选 HEAD 的代码与本轮实测。
- R4/R6 的延期**不构成通过障碍**：二者均已在 ADR 中登记、均不违反 I01 冻结范围的任何一条退出门槛（门槛 6 明确"重放输入缺失时如实标识"，而本候选对**依赖与配置**形状缺失确实如实标识为 false；仅**输入快照形状**存在 N-02 这一处缺口，已单列并给出可延期结论）。
- 上一轮 MiniMax 报告第 39 行指出"其 V9/第 3.4 节和实际 evidence 均为 12 条"——本轮实测 evidence/round-2 恰为 **12 条测量 + 1 份 manifest**，与该更正一致。

---

## 6. 关键验收项的独立核验记录

- **事务边界与故障矩阵**：`test_atomic_fault_matrix` 覆盖 2 模式 × 7 提交点 × 4 失败态 = 56 项；`disk` 失败另由 `test_actual_database_full_modes` 以 `PRAGMA max_page_count` 真实触发 `SQLITE_FULL`（映射/ChangeSet/轮次）。我另做 probe D6：`mapping` 与 `changeset` 两条路径实测 `database or disk is full`，且 `state` 未变、revision 未变、无 marker。**"磁盘失败"未使用仅边界注入的替代口径**。`exit` 失败为真实独立进程 `os._exit(73)`。
- **响应丢失对账**：probe D3 确认 `after_commit` 失败后 marker 存在、数据已提交、幂等重试返回同一 marker 且不重复写入；probe B10 确认同 operation 换 base 会被拒（`Conflict: operationId reused`）。
- **同事务提交标记**：`storage.py:380-395` 在**同一** `BEGIN IMMEDIATE` 事务内写入 `commits`、`commit_evidence`、前后快照与正式数据；probe D7 确认 `snapshots/commits/runs/rounds/run_terminal/commit_evidence` 六表的 UPDATE/DELETE 全部被 SQL 触发器拒绝。
- **所有权与冲突**：多来源同事实被 `_check_slot` 拒绝且错误可定位（probe C1b）；**例外见 M-01**（墓碑/编辑后路径）。
- **单值/多值/净零**：多值可并存、单值声明与既有事实冲突在提交内被拒、重复墓碑与净零改动不推进版本——均经仓库测试与 probe D5/H2 复现。
- **附录 D 九行与机器可读规则**：`invalidation-v2.json` 九行与 PRD D.2 逐行对应，**第 9 行 model 的 `staleReason` 为 `null`**；probe D5 实测：模型配置变更后 `model:cfg` 版本推进但结果 `stale=[]`、状态仍 `current`——**"模型配置不产生领域过期原因"成立**。probe B6 实测 `query:q1` 变更产生 `QUERY_CHANGED` 且相关依赖之外不受影响。实现兼容与发布策略单列且 `staleReason` 均为 null，未新增第九种领域原因。
- **场景隔离与历史**：`runs/rounds/run_terminal` 与正式 `facts` 表分离；probe D7 确认历史表不可改写；取消保留已提交轮次、终态后拒绝写轮次、跨运行 operation 复用被拒——均有仓库测试覆盖。
- **两档合成负载与真实包内同样例**：1×/10× 各自三重复，18/180 三元组，命名空间按 `urn:case:{i}:` 逐档独立（**未以同 ID 重复 G-base 冒充扩容**）；固定 SELECT 完整结果集与 expected 逐条比对；我实测包内探针输出与 evidence 逐位一致（V7），且 development 与 packaged 同 scale 六条记录四项关键值完全相同（V9）。内存原始值含 `tracemalloc` 峰值与进程 `ru_maxrss`，`condition`/`method` 如实标注"OS cache 未受控""Warm 为同进程第二次调用"。
- **基线诚实性**：`storage_baselines.E5` 与 PRD E.5 原表逐行数值一致（产能 3：积压 W004 / W007–W008 / W010–W012 / W013–W016，累计 3/6/9/12；产能 4：各轮完成各自新建四单、积压为空，累计 4/8/12/16），两次重放逐轮集合一致。`acceptance.md:40-52` 逐项区分"完整业务验收状态"，G.2 V-01/R-01–06/O-01、G.3 B-01–11、G.4/G.5 A-03–10、G.6 设备 B 场景**均如实标为未执行/未通过**。**未发现把占位能力、合成负载或存储替身冒认为完整业务基线的情况**；Q5 未定亦未被自行设定容量线。
- **静态/运行/打包/生产四类证据**：`evidence/round-2/` 的 `check.txt`（运行）、`e2e.txt`（运行）、`package-dir.txt`+`package-manifest.json`+`dynamic-linkage.txt`（打包）分层清晰，`package-manifest.json` 的 `scope` 字段明写"current macOS arm64 development machine…no clean-device/install/signing claim"。**本机模拟与实际 Windows CI 的区分**在 `acceptance.md:69` 与 `status.md:88` 均如实标注，本报告亦重申该边界。

---

## 7. 安全与数据一致性专项检查（未发现新问题）

- **SQL 注入**：生产代码全部参数绑定（`?`）；仅常量 DDL/触发器名与测试侧整数 PRAGMA 使用插值。
- **输入校验**：`iri()` 拒绝相对/含空白/非法字符 IRI；`term()` 经 Turtle 单三元组解析。probe E1 实测四种 Turtle 指令注入（`PREFIX`/`BASE` 换行注入、多语句注入、相对 IRI）**全部被拒**（`Unsupported S1 RDF object` / `Malformed IRI object`），无一进入存储。probe E2 实测 20 万字符长字面量解析 0.7 ms，无解析放大。
- **跨项目隔离**：probe E6 实测跨项目 `publish` 与 `start_run` 均 `Conflict: Cross-project`；probe E7 实测项目 P 的事实变更**不**使项目 Q 的结果失效（Q 的 `stale=[]`、current 指针仍在）。
- **不可变与隔离**：六张历史表有 SQL 触发器；`runs`/`rounds` 与正式 `facts` 分离；`publish`/`start_run` 校验快照项目归属。
- **无网络、无凭据、无遥测**；`irii`/`term` 不接受 URL 解析、插件发现或远程数据集。**未提交任何数据库、业务数据或密钥**。
- **缓存回收**：仅置空未 pin、非 current 的可重建载荷，状态/定义/来源/输入快照保留（probe H16、仓库测试）。

---

## 8. 最终结论

**通过。**

- **阻断问题 0 项**。首轮两项阻断（F-01 旧快照迟到覆盖当前、F-02 Unix `resource` 破坏 Windows）经本候选独立复现确认**已关闭**；我以 8 组对抗探针在首轮报告的原始反例路径上未复现任何等价缺陷。
- **中等问题 3 项**（M-01 所有权冲突在墓碑/编辑路径抛裸 `IntegrityError`；M-02 验收与 ADR 多处表述超出实际实现；N-01…N-03 中 N-03 为语义选择记录）。三项均**不违反** I01 冻结范围的任何一条退出门槛，**未造成数据损坏、安全缺陷或既有链路回归**。
- **低等问题 6 项**（N-04…N-08 及 M-01 的文档侧），均可在本候选后关闭或延期至对应迭代；其中 N-08 为**确认项**（断言成立，无需修改）。
- **历史 17 条意见**：15 条已关闭、2 条部分关闭/延期；**无一条沿用旧版通过**，每条均由我在本候选重新验证。R4/R6 的延期已在 ADR 登记且不影响通过。
- **四类证据区分**处理得当；未发现把占位能力、合成负载或存储替身冒认为完整业务基线；Q5 未定未被自设容量线；Windows 实际 CI、干净设备/签名/跨平台均如实标为未验证。

**后续要求（不改变本轮结论，但必须遵守）**

1. **M-01、M-02 应在本候选之后关闭**：M-01 属实现修复（需新候选、双方重新审）；M-02 属文档修正（`acceptance.md`/`ADR-0002-storage.md` 属受审范围，修改同样构成新候选，须按 `scope.md` 门禁第 5 条重新双审）。
2. **N-01、N-02、N-03 建议随 M-02 一并在下一版 ADR/acceptance 中写明实际边界**（尤其"输入快照形状未校验"与"发布资格严于 D.1 定义的当前"）。
3. **N-05 建议在 G.1 业务用例实现时补入固定 CSV 两行集合的回归**；N-04、N-06、N-07 随 F-11/R4 的 I03/I04 统一错误映射处理。
4. **Windows 侧仍待 PR 后 CI 实跑核验**；本报告的本机模拟不替代该核验，也不接受"模拟通过即视为跨平台已验证"。
5. 本轮通过**仅对 `e628f5e…3e787fb` 这一固定范围有效**；任何实现、测试、配置、依赖或验收文档变更均构成新候选，须双方以同一 base→head 重新独立审查，**不得沿用本轮或上一轮任一方的通过意见**。

---

## 附：本轮我实际执行的独立验证与探针

均在 `/tmp/i01r2/`，**未写入仓库**；仓库侧仅新增本报告一个文件。

| 文件 | 覆盖内容 |
|---|---|
| `probe_a.py` | 墓碑/编辑后所有权冲突、对照组、身份摘要解耦、同 revision 双发布、stale 后无 current、空提交推进 revision、缓存回收清空 stale 载荷、映射 sourceHash 变更的失效传播 |
| `probe_b.py` | 轮次快照作运行输入、`publish` 形参错误、跨项目 operation 复用、operation 重试与换 base、`snapshot()` 写锁竞争 |
| `probe_c.py` | 墓碑 + 第二来源（原始）、对照组、`edits` 后第二来源、轮次快照可重放、publish 裸 KeyError、恢复后重跑、相同定义重提交、结果被取代的状态标签 |
| `probe_d.py` | 首轮 F-01 精确复现、F-08 恢复路径、F-07 提交后对账、F-03 依赖登记、D.2 第 9 行 model 语义、真实 SQLITE_FULL（映射/ChangeSet）、六表不可变性 |
| `probe_e.py` | Turtle 指令注入四种变体、解析开销、replayable 假阳性、publish 裸 KeyError、`facts:asserted` 空项目范围、跨项目隔离、跨项目失效隔离、失败 operation 无 marker |
| `probe_f.py` | 存储 G-base 的 RDF 重建结果（谓词集/rdf:type/subClassOf 计数）、探针孪生对比、固定 SELECT 的 A01/A02/A03 区分、冻结输入 sources.json 完整性 |
| `probe_g.py` | `edits` 后 id 与内容解耦及第二来源提交原始语句、发布资格严格性、空提交推进 revision、固定 CSV 两行集合可表达性、仓库测试 002 覆盖度 |
| `probe_h.py` | 某 kind 首次发布因无关提交而无 current、语义空提交推进 revision、固定 CSV 两行集合实测、仓库 `002` 覆盖核对 |

`uv build --package ontolearn-engine --out-dir /tmp/i01r2-wheel` 产出的 wheel 经确认含 `ontolearn_engine/invalidation-v2.json`（机器可读规则随包分发）。
