# T02 FR-200/FR-201 全新 R06 整候选独立工程审查（zcode-glm53）

## 0. 结论（结论先行）

**最终结论：整个 FR-200/FR-201 候选（base 583c05c → head 831813c6，31 累计提交 / 79 差异叶 / 1363 tracked 物理源 / 5 构建，tree 944724a8）为「附条件通过（ConditionalPass）」，其中包含对合并的阻断性条件；不是无条件 Pass，也不是 Fail。R05（审 aff386f6）的 ConditionalPass 不被继承，本结论为本轮对 831813c6 的独立重核结果。**

分两层（任务明确要求不得偷换）：

1. **本地实现与同版证据层：通过。** 本人独立复核：831813c6 相对 934bd14f 恰改两份引擎测试文件、六处 `write_text` 增加 `encoding="utf-8"`（+10/-6 行），移除六个新增 keyword 后 AST 与原版完全相等（本人隔离纯计算，见 §2.2）；产品实现、其余测试、依赖、锁文件自 cb8c9b7a 起逐提交分类核实为零变化；CI 仅在 cb8→aff 有一次诊断变化（cb8→aff = 1 CI + 12 证据文档；aff→934 = 10 证据文档；934→8318 = 两测试文件，均无 CI 变化）。本轮新增的关键独立判定（定点复核后收窄为可证口径）：**934 树中 `ensure_ascii=False` 且未显式 encoding 的 `write_text` 恰为 6 处，即 8318 所修复位（manual 370/402/415/486/520 + budget 275）；8318 树全引擎测试目录 39 处 `write_text` 中，12 处 `ensure_ascii=False` 全部显式 `encoding="utf-8"`，该残留为 0；其余 20 处未指定 encoding 者均为默认 `ensure_ascii=True`（输出纯 ASCII）**（本人 AST 逐调用清点，934/8318 双树对照；原稿「22 处／6 处恰为全部 False 位点」计数错误，见 §11-1）。该扫描限 Python 测试树，不覆盖 TS/SQLite/C 扩展路径，也不证明旧 79F 全因归属。Python 引擎源码（src）零 `write_text`、文件写入均为二进制模式（`sys.stdout.buffer`、`"a+b"`/`"xb"`/`os.write`），Python 产品面无同类写点；TS/SQLite/C 扩展产品路径不在本扫描内、无法确认。本地同版证据（读回，非本人执行）：O041 三模块聚焦 151 PASS/22.58s + 一次 `uv run --offline --frozen npm run check` 自然 exit 0（TS 39 文件 1892 PASS；Python 3769 收集/3719 PASS/50 skip/1 原 warning/160.24s；Ruff 386 文件）；O042 真实 GUI 六例一次 6 PASS/0 skip/0 retry/0 flaky/108413.912ms（57 真实事务 7/7/7/7/22/7、57 唯一 Job/operation、43 拒绝=42 INVALID_REQUEST+1 OWNERSHIP_CONFLICT、58 附件解码哈希全对、8 拒绝向量含 4301 位整数与真实原 ID edit、拒后合法 add rev13/原 ID edit rev20、fresh en-001/de-ch-1901 四链 rev4–7、六独立 profile/App-引擎 PID 实绑、main64708991… 前后针绑定）。FR-200/FR-201 本迭代范围的条款映射（round-05 条款证据映射 + 本人对引擎/渲染/契约关键点独立抽核）成立（§3）。
2. **整候选现有门禁层：不可通过（阻断未关闭）。** 本人核实的远端与 CI 事实：934bd14f 已于 2026-10-25T07:06Z 普通推送一次（exit 0），PR16 open、head 已为 934；唯一自动运行 run 40171564866 attempt1：Mac 593s 成功、**Quality 718s 真实成功（含 packaged recovery 真实执行——相对 R05 时点这是真实变化，R05-02 的 Quality 取消缺口已被该运行关闭）**、Windows 328s 失败：诊断步（`-vv --maxfail=1 --tb=short`）真实首败为 `test_mainline_language_input_rejection.py::test_r03_same_owned_host_rejects_then_commits[language-first-digit-manual]`，栈为 language:47 `owned_rejection(...)` → manual:486 `path.write_text(json.dumps(trace, ensure_ascii=False))` → cp1252 charmap encode，**UnicodeEncodeError，实际 1 FAIL/980 PASS/3 SKIP/258.55s/exit 1**，后继 typecheck/build/e2e/package/verify 全部 skipped（从未运行）。831813c6 **未 push、无任何新 CI 运行**。CI36（run 40164456782，58c9）旧 79F 的全因归属仍未证明（本次首败只证明其中经共享 helper 写追踪的一族；O040 `allOld79FCausesProved:false`）。在 push 8318 → 新 CI 三 job 全绿（Windows 含 engine:check 后继步骤）之前，整候选不满足既有合并门禁。此为门禁级阻断条件，非新发现产品缺陷。

阻断项与条件清单见 §7；本轮问题清单 §5（最高为中危门禁级，无新的高危产品缺陷）；全部既有 OPEN/HOLD 按 §5/§6 保留。

---

## 1. 实际身份、独立性与输入完整性

| 项 | 实际值 | 说明 |
| --- | --- | --- |
| 运行 App | ZCode | 本会话运行时 |
| 模型 | `account:bigmodel-start-plan/GLM-5.3` | 会话环境声明（本人会话内实际可知者） |
| 思考等级/权限 | ROOT 第 2 行声明「Start Plan优先／GLM-5.3／最高／完全访问」 | 本人无法在会话内 UI 回读思考等级与权限模式，如实标注为任务下达值 + 会话环境部分印证；实际 taskID 由操作者正式 UI 读回，本人不自造 |
| 会话 SID | `session_3656bb05dd7ed7d1ccfe89755a461ace` | 操作者 O043 官方 AX 读回，本人不自造 |
| cwd | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T02-s1-review-fixes` | 本人 `pwd` 实测 |
| 唯一仓库写入 | 本文件（`docs/reviews/T02/fr200-fr201-20261024/round-06/zcode-glm53.md`）及其目录创建 | 任务下达第 3 行 |

**输入完整性（本人实际执行，恰一次）**：ROOT 封存附件 `/Users/kyle/.zcode/tmp/paste-attachments/2026-10-25/pasted-text-20261025-154240-4599149b.txt` 全文读至 EOF；`wc -c` = **22583**、SHA256 = **153e1cffd53b31d83ccc9be412bf0736a4c37fd10a77311426e8b0cd866ba406**，与下达一致。用户原始 11255 字节审查清单自 marker「你现在是我的软件工程审查员。」起恰一次出现于 EOF（160 个 `>` 引用行，连续无重复），未改写、未摘引替代。

**独立性**：本轮未读取、未列目录、未打开任何另一方 round-06 内容；R01–R05 为共同历史输入，本方读取了 R05 双方终稿（zcode 全文、minimax 关键意见表 grep 提取）、round-04/05 disposition 与独立审计的存在性与关键结论、round-05 条款证据映射全文，未沿用其结论作本人判定依据（凡引用处标注"读回"；本人判定均另附本人实测）。工作树 `AGENTS.md`（M）为受保护现行政策 overlay、round-01/02/03（??）为受保护历史报告，均未触碰。

**本轮未做**：未运行 npm/check/vitest/pytest/ruff/build/package/install/sync/HMR/GUI 或任何产品/SQL/probe；未动索引/commit/push/分支/远端；未读密钥、无关 profile、mimosa 状态或另一方本轮报告；未重试被拒 probe、未开旧失败 DB/profile、未重打旧包或重跑原 18。一次 Bash 直写 /tmp 源码副本被本仓 Mimosa 安全钩子拒绝（合理拦截），改用 Write 工具提交纯计算脚本、由脚本以只读 `git show` 在内存取版本——方法变更已在 §2.2 披露，无产品导入。

## 2. 冻结候选身份与差异核实（本人独立复核）

### 2.1 身份

| 项 | 下达值 | 实测 | 结论 |
| --- | --- | --- | --- |
| cwd/branch | worktree / `feature/weekly-t02-fr200-fr201` | `pwd`/`git branch --show-current` 同 | 一致 |
| HEAD/tree | 831813c6… / 944724a8… | `git rev-parse HEAD 'HEAD^{tree}'` 同 | 一致 |
| base | 583c05c7… | 存在；`git log --oneline base..head` = 31 | 一致 |
| 差异叶/tracked | 79 / 1363 | `git diff --name-status` 79；`git ls-files` 1363 | 一致 |
| dirty | AGENTS.md M + round-01/02/03 ?? | `git status --porcelain` 一致（政策 overlay 与历史保护件，非候选内容） | 一致 |
| PRD | 93584B / 7586b2c4… | 本人 `wc -c`/`shasum -a 256` 同 | 一致 |

### 2.2 934→8318 精确差异与 AST 等价（本人隔离纯计算）

- `git diff --stat 934bd14f 831813c6`：恰两文件 `test_mainline_manual_input_rejection.py`（+9/-5）与 `test_mainline_read_work_budget.py`（+1/-1）；diff 全文逐行读：六处 `write_text(json.dumps(..., ensure_ascii=False))` 追加 `encoding="utf-8"`，换行仅因参数折行，无其他字符变化。原行位点 manual 370/402/415/486/520 + budget 275，与 ROOT 第 27 行声明一致。
- 隔离纯计算（`/tmp/r06-ast-check/check.py`，stdlib `ast` + 只读 `git show`，无产品导入，不落源码副本）：旧版 `write_text(encoding="utf-8")` keyword 计数 0，新版恰 6（5+1）；对新版移除全部该类 keyword 后 `ast.dump` 与旧版**完全相等**。方法缺陷如实披露：脚本中「raw AST equal」一行因原地 strip 先于比较而恒真、无意义，结论以上述计数与 strip 后相等为准。该结论与 O041 `ASTAfterRemovingSixKeywordsEqualsOriginal:true` 独立咬合。
- 提交分类链：cb8→aff = `.github/workflows/ci.yml`（+10 行 Windows 首败诊断配置）+ 12 证据文档；aff→934 = 10 证据文档；934→8318 = 两测试文件。**分段事实：产品实现、其余测试、依赖、锁自 cb8（R04 双审实现）起零变化；CI 在 cb8→aff 有一次诊断变化，此后 aff→934 与 934→8318 均无 CI 变化；934→8318 仅两测试文件六 keyword。原稿「CI 配置自 cb8 起零变化」表述与自身 cb8→aff 分类矛盾，已更正（§11-2）。**

### 2.3 供应链哈希三角（本人实算）

fr201.3 wheel `99fab7bd…`/2379774B = uv.lock:258 pin = PROVENANCE 记录；upstream wheel `30c0a3eb…`、patch `de5755d6…`（5012B）、repack `166b0919…` 均 = PROVENANCE；`registry.json` SHA256 `5e097b7e…` 在 binding-regressions.json 出现 17 次（pin 同步）。与 R05 读回记录一致，本轮独立重算成立。

## 3. 需求—实现—证据核查（FR-200/FR-201 及闭包）

依据实读：PRD 307–318（FR-200/201）、244–246（FR-003）、256–270（FR-006）、330–333（FR-204）、521–531（FR-804）、附录 C 959–981、D 983–1013、E 1016–1048；D8 choice-A 原件全文（decision A、oldCandidateMayMerge:false、仅解除 T02 本功能 R4+ 限制、四禁止、十项要求）；ADR-0002 及 M0 计划（经 R05 §3 读回记录 + 本轮 PRD/附录直读复核关键条款）。附录 G（1115+）无 FR-200/201 专行，其与 T02 的关系由 round-05 条款证据映射的 GUI 证据目录承担（本人读该映射全文并抽核其引用的关键源码位）。

- **FR-200（业务概念管理）**：四类（class/objectProperty/dataProperty/individual）真实表单 CRUD、类层级/parents→subClassOf、domain/range、个体 types、五组元数据（中文名/英文标识/定义/同义词/示例）与删除影响展示——round-05 映射（28 笔原附件逐笔 + 源码行号）+ O042 本 head 六例 GUI 重跑通过；本人独立抽核渲染 `mainline-ontology`/`mainline-facts` 计划构造与引擎侧 `storage.py` 权威校验链。范围边界维持：不把 CRUD 通过外推为 FR-200 全条/附录 C 全能力（SHACL/规则/查询/导入导出等仍属各 owner 后续）。
- **FR-201（结构关系 vs 实例事实）**：两语义分层（definitions 层 vs facts 层，附录 C:971）；事实原 ID 编辑（`edits={factId:object}`，`storage.py:798–833` 读回 + `_check_slot(manual_incoming=dict(old))` 抽核）；新事实 ID = SHA-256(S,P,O) 双端一致（引擎 `storage.py:30` `digest` + `:494` 无条件重派生拒绝；渲染 `mainline-facts.ts:56–80` TextEncoder+lone surrogate 前置拒绝，本人实读两处）；canonical 政策 = 既有 ADR-0002:27（`term(value).n3()` 相等，非规范别名拒绝），`de-CH-1901` 语法合法但按 canonical 政策受控拒绝由 `test_mainline_language_input_rejection.py:325` 钉住（本人 grep 核实），en-001/de-ch-1901 正控四链 GUI 实跑成立——**Z-06 张力维持语义边界观察，不设新门禁**。
- **D8 四禁止合规**：8318 六处修改均为测试侧显式 encoding，无泛捕 ValueError、无异常文案分类、无静默规范化、无容量上限提高（本人 diff 全读）；`domain_changesets.py:447–465` 预检仅捕 `TermInputError`→`INVALID_REQUEST(field=params)`，未知 parser/N3/Store/preview 失败保留 UNKNOWN/HOLD（注释明示，本人实读）——维持 D8 边界。
- **read 工作预算/写许可**（FR-201 闭包、D8 要求 5/6）：测试文件 `test_mainline_read_work_budget.py`/`postwrite_*` 存在于候选（79 叶内 A 状态）；GUI/引擎证据按 O041/O042 读回；本人未重跑。
- **GUI 六例与 O042 边界**：`reservedIdentity` family 专用、FullRead 相等≠物理 DB 零写、无 Undo GUI/旧超限库恢复声明、serve/HMR/CSP 分支未实跑（`developmentServeHMRCSPBranchActuallyExecuted:false`）、package094 本轮未执行——均按证据边界如实保留。

## 4. 历史意见逐项追踪（R04→R05→本 R06 本人现状核）

| 旧意见 | 本候选（8318）现状（本人依据） | 判定 |
| --- | --- | --- |
| R05 P-1 / R05-01（Windows 79F 根因） | 首败已由 934 诊断实跑取证（cp1252×ensure_ascii=False 追踪写）；8318 关闭该类（本人 AST 扫描残留 0）；但 8318 无 Windows 实跑、79F 全因未证（§5 P-1） | 部分关闭，合并阻断维持 |
| R05 P-2 / R05-02（Quality 取消） | run 40171564866 Quality 718s 真实成功含 packaged recovery（O040 读回） | **已关闭**（934 运行） |
| R05 P-3/R05-06、Z-03、MM R03-04/05（definitions.triples wire） | `domain_changesets.py:451–465` 守卫仍仅 manual/edits；早期 `_definition` 抛点未受控（本人实读） | OPEN 非阻断延期（T01） |
| R05 P-4/R05-07、Z-04、MM R03-02（ownership 通用定位） | 定点复核后精确化（§11-5）：类层 `Conflict.code` 码表（storage.py:57–64）确无 "ownership" 键，但 `JobStore._application`（job_store.py:606–636 本人实读）对 ownership 类冲突实际两分支均 `fault("OWNERSHIP_CONFLICT", detailRef=…)`——(a) `ManualOwnershipConflict`/`SingleDeclarationConflict`（均 category="ownership"，均带真实 witness：storage.py:67–105 首阻断行/首两条记录）且 proof 在场时持久化 typed witness 详情；(b) 其余 ownership 冲突持久化固定三字段 opaque identity。**类层缺键不构成该路径最终 INTERNAL_ERROR**。仍 OPEN 者：通用（非 witness）ownership 冲突无可读定位（仅 opaque identity）；旧 detail 读取 INVALID_STATE→UI「详情暂不可用」降级维持 | OPEN 非阻断延期（限定为通用定位缺口，非码缺失缺陷） |
| R05 P-5/R05-05、Z-05（白名单缺码） | 契约 error oneOf 26 码 vs UI 白名单 17，缺 16（CURSOR_EXPIRED…VERSION_INCOMPATIBLE，本人 Python 全枚举重算，列表与 R04/R05 一致） | OPEN 非阻断延期 |
| R05 P-6、Z-06（de-CH-1901 语义） | 政策为既有且 choice-A 明确保留；测试 :325 在；不设新门禁（本人核实） | 语义边界观察维持 |
| R05 P-7、Z-07、R05-13（文件规模） | `wc -l` 本人实测 job_store.py 2993、storage.py 1887、e2e spec 1748（与 cb8 相同，8318 未改产品） | 信息级维持 |
| R05 P-8、M-01/R05-04（status.md 时点） | status.md 停在 aff 时点（"aff 尚未 push"），现已落后两步（934 已 push、CI 已跑 Windows 失败、8318 为 head）——非造假，时点差扩大 | OPEN（ROOT 收口时更新） |
| Z-01 / MM R03-03（同槽 SELECT 无 ORDER BY） | `storage.py:1212–1215` 仍无 ORDER BY（本人实读）；仍未构造反例 | 未确认观察维持 |
| Z-02（43692 上限） | R04 已撤回 | 不恢复 |
| M-02/R05-09（wheel/锁/可复现） | 本人哈希三角重算全对（§2.3）；不删 .1/.2/upstream 审计件维持 | 维持处置 |
| M-03（4299/4300 边界） | `grep -rn "4299\|4300" packages/engine/tests/` = 0（本人实测）；4301 有 GUI 证据（O042 inputUTF8Bytes:4301） | 未来最小补充建议维持 |
| M-04（standalone EOF 残余） | `rdf_snapshot.py` 仅捕 ValueError/(BadSyntax, Notation3InputError)/Exception（:22/:42/:44 本人实读），EOF IndexError 路径维持 UNKNOWN/HOLD | OPEN 维持（不泛捕） |
| M-06（schema 只约束 id 形状） | `storage.py:484–495` 引擎权威校验 + `_fact` 双防在（本人实读） | 维持非缺陷 |
| M-07（桶导出） | 导出面未改 | 低优先维持 |
| R05-03（无自产新包） | O042 `noNewPackageOrOld18Rerun:true`；旧 094 有界保留 | 维持 |
| R05-10（未提交 AGENTS 链接） | 属政策 overlay 非候选内容；现行 overlay 的归档路径（`docs/iterations/I01/inputs/…`）真实存在（本轮 ls 核实于 PRD 读取路径同源） | 归指南维护，不计数 |
| R05-11（冲突定位不含对象值） | 设计内（locator 不携原值）；维持 | 观察维持 |
| R05-12（两 TS 测试依赖 PATH python） | 产品/测试未变（cb8 起零变化）；本轮未单独重验执行点，按 R05 复核记录读回 | 维持低危 |
| R03 其余（容量/Q5/D2、Undo、native/named exit、text001 等） | 全部按原 HOLD/保留 | 不变 |

## 5. 本轮问题清单（编号/等级/位置/触发/影响/证据/建议/阻断性）

### P-1【中·阻断合并（门禁级，非已证产品缺陷）】8318 无任何 Windows 实跑证据；79F 全因未证
- 位置/触发：`.github/workflows/ci.yml:132–139`（Windows 诊断步）；934 run 40171564866 Windows exit 1（首败栈见 §0）。
- 影响：Windows typecheck/build/e2e/package/verify 在本分支从未运行；PR16 无法合并；若 79F 中存在非追踪写类的独立缺陷，需新候选处理。
- 证据：FIRST-WINDOWS-FACTS（1 FAIL/980 PASS/3 SKIP、后继步骤全 skipped、`notProved` 三项）、FINAL-CI-FACTS（`allOld79FCausesProved:false`）、本人 AST 双树清点（934 树 False×无 encoding 恰 6=修复位；8318 树 12 处 False 全显式 utf-8、该残留 0；限 Python 测试树，不外推 79F 全因）。
- 建议：push 8318 → 新 CI；若 Windows 仍有失败按新事实定根因；任何代码/测试/配置改动即新候选重走门禁。
- 阻断：**是（对整候选合并）**；对本地 mac 同版证据不构成反驳。

### P-2【低·已由 ROOT 显式口径解决定义问题，并入 P-1】Windows 诊断步语义与验收口径
- 位置：`ci.yml:131`「Diagnostic only … not acceptance」注释 + `PYTEST_ADDOPTS='-vv --maxfail=1 --tb=short'`。
- 技术前提（本人独立核验）：`package.json` 的 `engine:check` = `uv run --frozen ruff check . && uv run --frozen ruff format --check . && uv run --frozen pytest`；根 `pyproject.toml [tool.pytest.ini_options] testpaths=["packages/engine/tests"]` 且无 addopts；`PYTEST_ADDOPTS` 仅三个输出/早停 flag、无任何用例筛选。故**零失败时该配置下自然 exit 0 即为全量收集/全量执行**（3769 收集逐项通过或原有有据条件 skip），与无该 env 的绿语义等价；失败时才早停，而早停本身即失败证据。
- 口径判定：ROOT 总控已在本会话明确未来 CI 验收口径（既有全量标准的可核对条件，非同行意见、不降低门禁）：Windows 须实际完整运行上述命令链，同候选真实终态自然 0、全量收集逐项由最终通过或原有有据 skip 覆盖、零失败/早停/取消/timeout/NOTRUN，且 typecheck/build/E2E/package/verify 后继全部真实 success、三 job 实际 success 才接收；不得仅凭 diagnostic 绿/步名推通过。本人据上述技术前提独立判断：**原稿所提"恢复全量语义或操作者显式定口径"前置已由该显式口径满足**，本项不再是独立阻断条件，实际合并阻断由 P-1 的"新 CI 三 job 真实 success"承载。
- 残留（如实）：workflow 步名/注释仍写 "not acceptance"，属文档性滞后——接受未来绿结果的依据是 ROOT 显式口径而非步名；未来若改注释/flags 即新候选重审，本轮不因之要求改动。失败时 `--maxfail=1` 截断其余失败清单是其诊断目的，任何失败本就阻断合并。
- 分类：**非 push 前技术阻断；作为独立项阻断性：否**（并入 P-1 合并条件）。本轮未因此新改代码/CI 或重跑本地。

### P-3【低·延续 OPEN】definitions.triples wire 面（Z-03/R05-06）：见 §4。阻断：否（接线前处理）。
### P-4【低·延续 OPEN（限定为通用定位缺口）】ownership 通用冲突无可读定位（Z-04/R05-07）：类层缺键不构成该路径最终 INTERNAL_ERROR，`_application` 两分支均 `fault(OWNERSHIP_CONFLICT)`，详见 §4 行与 §11-5。阻断：否。
### P-5【低·延续 OPEN】渲染错误码白名单缺 16 码（Z-05/R05-05）：见 §4。阻断：否。
### P-6【低·未确认观察】同槽冲突 SELECT 无 ORDER BY（Z-01）：`storage.py:1212–1215`；加固建议（ORDER BY id+确定性回归）维持。阻断：否。
### P-7【语义边界观察·非缺陷·不设新门禁】de-CH-1901 字面拼写与 canonical 政策张力（Z-06）：政策既有且 choice-A 保留；仅未来改政策才需用户显式决定。阻断：否。
### P-8【信息】技术债集合：核心文件行数（2993/1887/1748）；standalone EOF 8 例 OPEN（M-04）；4299/4300 边界无覆盖（M-03）；status.md 时点落后两步（ROOT 收口时更新）；R05-12 PATH python 依赖。阻断：均否。

本轮**未发现新的阻断级/高危产品代码缺陷**；无凑数项。产品实现自 cb8 未变，R04 双审对该实现的判定面在本候选继续有效但不被继承为通过。

## 6. 无法确认项与独立 HOLD（不因附条件通过解除）

无法确认：8318 Windows 全套行为（P-1）；TS/SQLite/C 扩展产品路径的编码行为（本扫描限 Python 树）；本 head 全树依赖漏洞自动扫描（无 OSV/mimosa 新记录；rdflib 供应链人工核到哈希级）；5×10⁶ 行级索引/分页与性能容量（Q5/D2 无通过线）；迁移回滚演练（format2→3 前向+lease 在）；全流程键盘+读屏与 RTL；生产 CSP serve/HMR 分支实跑（O042 明示 false）；README 新人 1 小时上手；8318 打包制品与包内运行（无新包）。
HOLD（延续，独立保留）：签名、公证、wholeApp 法律/_distutils、全平台/参考设备/macOS15/Win11、性能容量 Q5/D2 及旧超限库恢复、损坏 SQLite 物理资源保护（用户明确保留）、unknown parser/N3/Store/坏快照、Undo GUI 及未实测 ownership 家族、native engine 及 named App exit UNKNOWN。不得用内部演示/本机绿冲抵。当前合并可用仍 2/17（FR401/402）；不因本报告增加 FR 或宣称 Goal/发布完成。934 Windows 失败与 CI36 原始失败/取消不消失；O022 整体不 sealed；O027/093/text001/R03ZPass 等原失败链保留。

## 7. 最终结论、条件与下一最小动作

**结论：ConditionalPass（附条件通过）。** 831813c6 是对 934 已实证 Windows 首败类的最小、测试侧、四禁止合规修复（本人 diff+AST 独立复核），本地实现与 mac 同版运行/GUI 证据达标（O041/O042 读回 + 本人静态独立核验）；但整候选在现有远端门禁下不可判通过——Windows 实跑缺口与诊断步验收口径是合并阻断（P-1/P-2），既有 OPEN/HOLD 全部保留。不预设 ROOT 会接收任何条件；不把 R05 的 ConditionalPass 继承为本轮通过；也不把"缺少尚未 push 产生的新 CI"虚构为源码缺陷。

**本人对"8318 Windows 完整验收仍缺"的独立判断**：这是当前结论维持附条件的唯一实质技术缺口。已证首败类在 Python 测试树内无残留（False×默认编码 write_text = 0，本人双树清点；不外推全部编码风险或 79F 全因），Mac/Quality 两 job 在 934 树（=本候选产品面）已真实绿，因此 8318 push 后 Windows 全绿的概率显著提高；但 CI36 的 language 6F 中仅一族被诊断运行复现归因，manual 72F 中的其余失败无栈无总表，且 Windows 后继步骤（typecheck/build/e2e/package）在本分支从未执行——任何其一再失败均需按新候选处理。故"缺新 CI"不降低本地通过判定，也不构成源码缺陷，但完整保持合并阻断属性。不能根据另一方预设 Pass（本报告成稿时未读、不知其结论）。

**条件（合并前，依既有原标准与 ROOT 已显式定义的可核对口径，非本报告新设）**：
1. push 8318 → 新 CI 实跑，接收条件为：Windows 实际完整运行 engine:check 真实命令链（`ruff check .`→`ruff format --check .`→`uv pytest`；本人核 package.json 与根 pyproject `testpaths=["packages/engine/tests"]`、`PYTEST_ADDOPTS` 仅 -vv/--maxfail=1/--tb=short 无筛选），同候选真实终态自然 exit 0、3769 全量收集每项由最终通过或原有有据条件 skip 覆盖、零失败/早停/取消/timeout/NOTRUN，且 typecheck/build/E2E/package/verify 后继全部真实 success；三 job 实际 success。不得仅凭 diagnostic 绿/步名推通过；任何失败/缺结果不验收、不合并；旧 79F 不追认全同因，缺栈残留清单保留。【阻断（merge 条件；本候选无 push 前技术阻断，当前仍无 push/新 CI/merge 授权）】
2. 双指定模型 fresh 双审（本报告为其中之一）与全部意见处置完成；任何新的 code/test/config/依赖改动即新候选重新验证与双审。【阻断（流程）】
3. 既有 OPEN 按 D8/R04/R05 分工处理（definitions.triples wire、ownership 通用定位、白名单 16 码、4299/4300、EOF 类型化）；canonical 政策维持不变，不为其设新用户表态前置。【非阻断，接线/收口前】
4. §6 全部 HOLD 按原归属保留，不得以本附条件通过冲抵；status.md/m0-checklist 由 ROOT 收口时按实际终态更新。【非阻断，发布前】

**下一最小动作**：由 ROOT 按 D8/正常次序授权 push 831813c6 触发 PR16 新 CI；期间不动冻结候选、不预写结论。

## 8. 用户 11255 字节原始清单逐项判定（1–160 每项独立一行；产品形态：本地优先单用户 Electron+Python 桌面，无账户/云/支付/网络服务；判定=适用（达标/未达标）·部分适用·不适用·无法确认；依据限本人本轮实际核验面，读回处标注）

| # | 项（缩写） | 判定 | 依据/缺口 |
| --- | --- | --- | --- |
| 1 | 有人设计的 schema | 适用·达标 | contracts/v2/schema.json $defs（error oneOf 26 分支本人枚举）+zod 双端+registry pin（§2.3）；SQLite 版本化 |
| 2 | 邮箱带+号登录 | 不适用 | 本地单用户无账户/登录 |
| 3 | 密码重置链接 | 不适用 | 无登录/邮件 |
| 4 | MFA+丢失手机 | 不适用 | — |
| 5 | 会话超时/一键终止 | 不适用（账户语义） | 无账户会话；引擎/窗口生命周期属 I02 已验面（读回） |
| 6 | SSO | 不适用 | 无企业客户面 |
| 7 | SAML | 不适用 | — |
| 8 | SCIM | 不适用 | — |
| 9 | 深于 admin 的角色 | 适用·达标（本范围） | permission 细分+ownership proof+IPC 白名单（preload 单命名空间桥 13 固定 invoke 本人抽核；读回合同） |
| 10 | 改一个数字读他人数据 | 适用·达标（已核路径） | 主进程强制 projectId/无通用 invoke（本人抽核 preload；读回 detailRef origin+fingerprint） |
| 11 | 租户隔离 | 不适用（无多租户）；项目级隔离达标 | 同 #10 |
| 12 | 管理员代登录 | 不适用 | 无支持面 |
| 13 | 登录限速 | 不适用 | 无登录 |
| 14 | 锁定不误伤 | 不适用 | — |
| 15 | 迁移前进/回滚 | 部分适用 | format2→3 前向+迁移写锁在（读回 ADR-0002）；回滚演练未见→无法确认 |
| 16 | 迁移不锁主表 | 部分适用·无法确认 | 本地单用户无高峰并发面；迁移期间表锁/长事务行为未测——单写者/启动期迁移本身不证明无锁（原稿达标判定已收窄，§11-4） |
| 17 | 索引撑 500 万行 | 部分适用·无法确认（大规模） | 实测上限 243 行/80545B/56KB 文本 5 页（读回）；Q5/D2 HOLD |
| 18 | 连接池 | 不适用 | 嵌入式单连接 |
| 19 | 每夜备份 | 不适用（本地数据主权） | backup(newPath) API 在（读回）；无自动任务需求（M0 边界） |
| 20 | 恢复演练 | 无法确认 | 旧 DB 禁打开，无 restore 演练证据 |
| 21 | PITR | 不适用 | 无运维删库场景 |
| 22 | 软删除 | 适用·达标 | 受管事实墓碑、原 ID 保留、历史不可改写（映射+读回） |
| 23 | 服务端（引擎）校验 | 适用·达标（含披露缺口） | `_fact`/`_check_slot`/预检链本人实读；definitions.triples 面 OPEN（P-3） |
| 24 | 时区存储 | 部分适用·达标（存储口径） | 安全整数/UTC（读回）；无提醒调度面 |
| 25 | 撇号姓氏 | 适用·达标（词法面） | UTF-8 全链；8318 正是 Windows Unicode 追踪写修复；Turtle 词法受控 |
| 26 | emoji/重音/RTL | 部分达标 | 56309 Unicode scalars/56314 UTF-8B（读回）；RTL 专项未测→无法确认 |
| 27 | 金额存整数 | 不适用 | 无金额 |
| 28 | 币种/舍入/税 | 不适用 | — |
| 29 | 抗第二客户变更 | 部分适用·达标（P0 边界内） | 版本化契约+不可变快照+canonical 身份；附录 C 前言要求扩展重评 |
| 30 | 幂等键 | 适用·达标 | operationId/claims 同操作同内容返回原结果（读回）；GUI rev13/rev20 唯一 Job（O042） |
| 31 | 四次点击去重 | 部分适用·无法确认 | 服务端幂等（operationId 原结果，#30）与拒绝后状态不变已证（O042）；客户端连点/并发重复提交的去重行为未测——拒绝 Read 不变与 preview 围栏不证明该项（原稿达标判定已收窄，§11-4） |
| 32 | 第 400 页分页 | 适用·达标（已测范围） | 游标校验+页/帧预算；更大受控拒绝（同 #17） |
| 33 | 导出表格 | 不适用（现阶段） | FR-203 Turtle 导出属后续，不虚称 |
| 34 | 2009 年 CSV 导入 | 不适用 | FR-300 映射后续 |
| 35 | 留存规则删除 | 不适用 | 本地用户数据，无合同删除义务 |
| 36 | 密钥不入代码/仓库/chat | 适用·达标 | 79 叶 diff 本人分类全读无凭据；引擎无密钥；S3 未接线 |
| 37 | 轮换 AI 粘贴的密钥 | 不适用 | 未发现任何已入库密钥 |
| 38 | 确认安装包是所要的 | 适用·达标 | 本人哈希三角：wheel/patch/repack/PROVENANCE/uv.lock/registry pin 全对（§2.3） |
| 39 | 依赖扫描 | 部分适用·无法确认（全树） | 无新自动扫描记录；rdflib 补丁人工核达哈希级 |
| 40 | 输入消毒 | 适用·达标（含披露缺口） | 受控拒绝族（词法/语言标签/整数/IRI，本人实读测试与预检）；P-3 面如实登记 |
| 41 | SQLi/XSS/CSRF/OWASP | 适用·达标（已读面） | SQL 全参数化（storage.py 多处本人实读）；createElement 文本渲染（读回）；CSP 本人实读（#44）；无 HTTP→CSRF 不适用 |
| 42 | 上传扫描/限大小/不可执行 | 适用（等价面）·达标 | 示例资源 O_NOFOLLOW/O_NONBLOCK/常规文件/大小限（读回 mainline.py:316–326 本人实读 os.open 标志） |
| 43 | CORS | 不适用 | 无 HTTP 服务 |
| 44 | 每响应安全头 | 部分适用·达标 | csp.ts 26 行本人实读：生产 script-src 'self'；dev 变体 nonce+仅 style-src HMR inline |
| 45 | 静态/传输加密 | 不适用（本地单机 M0） | 边界披露；未来模型网关 TLS 属 S3 |
| 46 | 最小权限（含 AI agent） | 适用·达标 | preload 业务命名桥（本人抽核）；Agent 只草稿+人工确认（不变量） |
| 47 | 日志谁做了什么无敏感 | 适用·达标 | origin(hostClientId/engineSessionId)、固定错误码、无堆栈/路径/原值跨边界（实读 message() 白名单） |
| 48 | 渗透测试 | 不适用（现阶段） | 未执行、未虚称；公开发布前安全审查义务保留 |
| 49 | 安全问卷 | 不适用 | 无企业买家 |
| 50 | 漏洞披露流程 | 不适用 | — |
| 51 | 盗笔预案 | 不适用 | 本地无凭据/生产访问；磁盘加密属用户系统策略 |
| 52 | SOC 2 | 不适用 | — |
| 53 | HIPAA | 不适用 | 无患者数据 |
| 54 | BAA | 不适用 | — |
| 55 | 查看审计 | 部分适用 | 变更审计完整（不可变操作/快照）；本地单用户无"查看"审计需求 |
| 56 | PCI | 不适用 | 无支付 |
| 57 | GDPR 删除触达每表 | 不适用 | 无云个人数据 |
| 58 | 数据驻留 | 不适用 | 本地优先 |
| 59 | 季度访问审查 | 不适用 | 单用户 |
| 60 | dev/staging/prod 一致 | 不适用（部署语义）；源-包一致性已验 | cb8→…→8318 物理源逐级核实（本人 git diff）；旧 094 有界桥接（读回） |
| 61 | IaC | 不适用 | 无基础设施 |
| 62 | 部署管线先跑测试 | 部分适用·当前未达标 | CI 三 job 在册；934 运行 Mac/Quality 绿、Windows fail；8318 未跑（P-1） |
| 63 | 一键回滚 | 不适用 | 无部署 |
| 64 | 零停机部署 | 不适用 | — |
| 65 | 特性开关 | 不适用 | registry 能力注册即面；无运行时 flag 需求 |
| 66 | 自动扩缩 | 不适用 | — |
| 67 | CDN | 不适用 | — |
| 68 | DNS/SSL 续期 | 不适用 | — |
| 69 | 后台任务不冻结页面 | 适用·达标（已测面） | Job 队列/57 事务/恢复（O042+读回）；旧三故障注入（cb8 包读回） |
| 70 | 带退避重试 | 部分适用 | retryable 语义在（合同枚举）；退避策略未断言 |
| 71 | 死信队列 | 适用（等价物）·达标 | 失败 Job 终态保留可查、不与成功混排（读回） |
| 72 | cron 不双跑 | 不适用 | 无多服务器 |
| 73 | 缓存与失效 | 适用·达标（架构面） | invalidation-v2.json 唯一源（AGENTS 不变量）；本轮未重跑失效用例 |
| 74 | SPF/DKIM/DMARC | 不适用 | 无邮件发送 |
| 75 | 退信/投诉处理 | 不适用 | — |
| 76 | 存储清理规则 | 不适用 | 本地文件用户主权；缓存回收语义在（读回） |
| 77 | 成本告警 | 不适用 | 无云成本；模型网关未接线 |
| 78 | DR 计划 | 不适用 | 本地单机无多区域运维面 |
| 79 | 第二区域 | 不适用 | — |
| 80 | 3am 可搜结构化日志 | 部分适用·达标（存在面）；检索工具无法确认 | 逐例结构化 trace/report+哈希（本人实读多个 trace 位点）；集中检索未建设 |
| 81 | 错误聚合 | 不适用（运营上报系统） | 本地逐例 trace 在 |
| 82 | 外部 uptime 检查 | 不适用 | — |
| 83 | 告警呼叫人类 | 不适用 | — |
| 84 | 仪表盘 | 不适用 | — |
| 85 | 跨服务追踪 | 不适用（多服务）；request/Job/origin 绑定为单服务等价物 | — |
| 86 | on-call 轮值 | 不适用 | — |
| 87 | runbook | 不适用（值班语义）；AGENTS/docs 流程文档在 | — |
| 88 | postmortem 改变什么 | 适用·达标 | 失败链留痕→D8 熔断→choice-A→8318 最小修复即实际改变；勘误/处置机制运转中（R05 §12 先例） |
| 89 | 状态页 | 不适用 | — |
| 90 | 懂逻辑者写的单测 | 适用·达标（mac 侧）；Windows 侧未闭 | O041 1892 TS+3719 Py 自然 0（读回）；新引擎测试断言语义/哈希/wire（本人抽读）；CI Windows（P-1） |
| 91 | 三方 API 集成测试 | 不适用 | 无第三方 API；唯一依赖 vendored+回归（§2.3） |
| 92 | 赚钱流 e2e | 不适用（无金钱流）；CRUD/冲突 e2e 等价达标 | O042 六例 6 PASS（读回） |
| 93 | 上线前负载测试 | 部分适用·无法确认 | 预算/容量受控测试在；性能负载未测（Q5/D2 无通过线） |
| 94 | 类生产非生产测试数据 | 适用·达标 | 固定 fixture/合成孪生独立命名空间，无生产数据入库 |
| 95 | 修 bug 不复活旧 bug | 适用·达标 | binding-regressions 17 pin（本人复核 registry 哈希）；R03 拒绝向量回归；8318 AST 等价保全部原断言（本人） |
| 96 | 五年前笔记本 | 无法确认 | 参考设备/低端硬件 HOLD |
| 97 | 可访问性合规 | 部分达标·无法确认（全面性） | 新视图 aria/role 在（读回）；全流程键盘+读屏未验 |
| 98 | 订阅/升降级/按比例 | 不适用 | 无计费 |
| 99 | 催付重试/催缴邮件 | 不适用 | — |
| 100 | 发票带 PO | 不适用 | — |
| 101 | 销售税/VAT | 不适用 | — |
| 102 | 退款/部分退款 | 不适用 | — |
| 103 | 计量与账单一致 | 不适用 | — |
| 104 | 年度定制合同 | 不适用 | — |
| 105 | 财务对账报表 | 不适用 | — |
| 106 | webhook 验签 | 不适用 | 无 webhook |
| 107 | webhook 重试/日志 | 不适用 | — |
| 108 | 版本化 API | 适用·达标 | protocolVersion、schema $id/registry 版本化、旧版本并行校验（读回+error oneOf 枚举） |
| 109 | 用户建撤 API key | 不适用 | 无公开 API |
| 110 | API 限速 | 不适用；等价物帧/页/预算/队列限制在场 | — |
| 111 | 三方 API 变格式预案 | 不适用 | 唯一依赖 vendored 固定（优于预案） |
| 112 | OAuth 刷新 | 不适用 | — |
| 113 | 客户集成沙箱 | 不适用 | — |
| 114 | 提示注入防护 | 不适用（现阶段；S3 未接线） | 架构已定 Agent 白名单+人工确认+网关唯一主进程 |
| 115 | 客户/患者数据不出网 | 不适用（现阶段） | 同上 |
| 116 | 模型花费上限 | 不适用（未接线） | — |
| 117 | evals | 不适用（现阶段） | — |
| 118 | 模型降级 fallback | 不适用（未接线） | — |
| 119 | 模型弃用迁移预案 | 不适用（现阶段） | — |
| 120 | 提示/输出日志 | 不适用（现阶段） | 附录 F 最小调用记录设计已定（读回） |
| 121 | AI 不可撤销动作人工批准 | 适用·达标（架构） | Agent 只草稿、不得自动确认；preview/确认流（本人实读 domain_changesets 预检+映射） |
| 122 | 酒店 wifi 加载 | 不适用 | 本地应用 |
| 123 | 空/加载/错误态 | 适用·达标 | reading/unavailable/ready 三态+role=status/alert（读回） |
| 124 | 可行动错误信息 | 适用·达标 | OWNERSHIP_CONFLICT 中文行动提示+定位视图；固定码白名单（本人实读） |
| 125 | 表单失败保留输入 | 适用·达标 | 冻结 toHaveValue 断言+原输入 JSON（O042 inputRetentionEvidence） |
| 126 | 邮件客户端渲染 | 不适用 | 无邮件 |
| 127 | 可关通知 | 不适用 | 无通知系统 |
| 128 | undo | 适用·达标（引擎面）；GUI Undo 面 HOLD | undo-impact 预览/暂停语义+测试（读回） |
| 129 | 键盘导航+读屏 | 部分达标·无法确认 | 同 #97 |
| 130 | 翻译/本地化格式 | 不适用 | 中文单语；无日期数字本地化面 |
| 131 | 后退按钮符合预期 | 不适用 | 桌面工作台；窗口恢复属 I02 |
| 132 | 人能读的代码 | 适用·达标 | 本人实读 storage/domain_changesets/mainline-session/csp 等；意图注释密度高 |
| 133 | 每次变更 code review | 适用·达标 | 同版双指定模型审查在执行（本轮 R06 即一环） |
| 134 | 分支策略 | 适用·达标 | worktree+feature+base SHA+PR 回并（本 worktree 与 O040 push 记录实证） |
| 135 | 月度依赖升级 | 无法确认 | 未建立月度节奏文档 |
| 136 | 框架 EOL 前升级 | 无法确认 | Electron/React 升级策略未文档化 |
| 137 | 删除 AI 死代码 | 适用·达标 | 79 叶 diff 本人全读无死代码/调试残留；.1/.2/upstream 为审计证据保留（维持处置） |
| 138 | 拆 2000 行文件 | 适用·未达标（信息级） | 2993/1887/1748（本人 wc 实测；P-8） |
| 139 | 架构决定写理由 | 适用·达标 | ADR-0001/0002/0003、M0 计划、迭代/评审体系（目录实证） |
| 140 | README 1 小时上手 | 无法确认 | 未做新人实验 |
| 141 | 交接文档 | 适用·达标 | docs 树+每轮留痕+唯一状态源 m0-checklist/status.md（时点差见 P-8） |
| 142 | 运维 admin 面板 | 不适用 | — |
| 143 | 客服支持工具 | 不适用 | — |
| 144 | 客户可读 changelog | 不适用 | 无外部客户 |
| 145 | 条款/隐私与代码一致 | 不适用（未发布）；本地优先行为与 PRD 一致 | 法律发布 HOLD 保留 |
| 146 | 资产归公司名下 | 不适用 | 个人项目现阶段 |
| 147 | bus factor>1 | 部分适用 | 双模型评审+总控留痕降低单点；创始人单人边界如实 |
| 148 | senior 读每行 AI 代码（人） | 不适用（现阶段组织角色）；双模型逐文件审查+操作者重哈希部分替代 | 不虚称已满足；组织角色不适用不消解本审实际核验责任 |
| 149 | 后端工程师先建模（人） | 部分适用·达标 | 附录 C 主定义+ADR-0002 数据层次先于实现；Q6 能力冻结按用户采用决定单推荐口径（不以旧报告称开放） |
| 150 | 解释 AI 修复副作用（人） | 部分适用·达标（本轮实际承担） | 本轮修复链（934 首败→8318 六处）副作用核查实际执行：AST 等价保全部原断言+双树 write_text 清点+聚焦 151/全检自然 0/GUI 6 PASS（读回）；组织角色缺席不消解此责任，已验面内履行、未验面如实保留 |
| 151 | DevOps 管部署/云账单（人） | 不适用 | 无服务器/云账单；CI/打包由总控承担 |
| 152 | 3am 值班（人） | 不适用 | — |
| 153 | 漏洞公开周补框架（人） | 部分适用·无法确认 | 依赖维护仅个案（rdflib repack 流程在）；升级节奏未文档化（同 #136） |
| 154 | 陪审计走患者数据（人） | 不适用 | 无 HIPAA/审计场景；合规不适用不取消法律发布 HOLD |
| 155 | QA 验 AI 所称测试（人） | 适用·达标 | 同版双指定模型独立审查+操作者重哈希/逐笔核验即此机制（本轮亦执行：本人 AST/哈希/枚举独立复算） |
| 156 | 在线库迁移不掉行（人） | 部分适用·无法确认 | 迁移 lease/回滚语义+测试在；无真实用户库在线迁移演练 |
| 157 | tech lead 拒绝破坏性功能（人） | 适用·达标 | 能力矩阵"扩展须重评"、AGENTS 不代答 Q2/Q3/Q5-9、D8 熔断实践 |
| 158 | architect 规模化（人） | 不适用（现阶段单机）；Q5 容量 HOLD 为对应风险登记 | — |
| 159 | AI 调不动时人来 debug（人） | 部分适用·达标（本轮实际承担） | 934 首败真实栈取证→cp1252×ensure_ascii=False 根因→8318 最小修复由流程实际完成并经本轮双证核验；边界如实：Windows 其余 79F 归因仍缺（P-1）；组织角色缺席不消解此责任 |
| 160 | 一年后记得为什么（人） | 适用·达标 | ADR/评审留痕/m0-checklist/状态文件体系即为此设计 |

不凑 160 个问题：上表为适用性判定，非缺陷清单；新增功能为零。

## 9. Top 10（按严重度；本轮实际发现，不凑数，Top10 之外无其他阻断）

1. **P-1 Windows 门禁未闭**（8318 无实跑；79F 全因未证；Windows 后继步骤从未运行）——阻断合并。
2. **CI 验收口径已由 ROOT 显式定义（可核对条件）**：零失败时 `--maxfail=1` 不削弱全量语义（本人核命令链/testpaths/无筛选）；P-2 原独立阻断性已降级并入 P-1，无 push 前技术阻断。
3. **P-5 白名单缺 16 契约码**（接线时用户可见 INTERNAL_ERROR 降级面）。
4. **P-3 definitions.triples 早期坏词法 UNKNOWN/HOLD**（Agent/原始 triples 接线前的受控面缺口）。
5. **P-4 ownership 通用冲突无错误码映射/可读定位**（非 witness 家族 UI 降级）。
6. **P-6 同槽冲突 SELECT 无 ORDER BY**（首个阻断行不确定；未确认观察）。
7. **P-7 Z-06 canonical 大小写语义边界**（不设门禁，防未来误当缺陷或误改政策）。
8. **P-8 status.md 时点落后两步**（入口文档与实际远端/CI 状态脱节，ROOT 收口更新）。
9. **P-8 核心文件规模 + standalone EOF 残余 + 4299/4300 边界无覆盖**（技术债集合，均有既定归属）。
10. **§6 容量/参考设备/法律签名等独立 HOLD**（无法确认类，发布前必须逐项关闭，不以本附条件通过冲抵）。

## 10. 自然终态声明

本报告为唯一仓库写入（目录创建 + 本文件）。本人本轮实际执行并已披露的命令类型：文件哈希/字节核验、git 只读身份/diff/log/ls-files/show、源码与测试的 grep/定点读取、三个证据目录摘要 JSON 的读取与解析、隔离 /tmp 纯计算（AST 等价、错误码枚举、encoding 风险面扫描、供应链哈希）。未运行任何产品/测试/构建/GUI；未读取本轮另一方报告（round-06 对方文件未列目录、未打开）；事实修订规则知悉：后续修订仅在原代码未变时另封新版本，不改本原件。报告写后将实测本文件 bytes/行数/SHA256 回显于会话终态。

## 11. 定点事实核对与修订记录（修订版新增；原稿 40045B/315 行/SHA256 `652f19e90d0efdf61e564a8c06425e3fd9273bff3cee2510e10e4a916f8e2127` 已由操作者仓外逐字节另封；本次修订仅落本文件，代码/候选未变，不请求改判、不撤任何意见，总判定与全部新旧意见保留）

1. **write_text 计数更正（修订 §0/§5-P-1）**：原稿「AST 扫描全部 22 处」「6 处已带 encoding 且恰为全部 ensure_ascii=False 位点」两处错误。本人复测（`/tmp/r06-ast-check/rescan.py`，stdlib ast + 只读 `git show`，934/8318 双树对照）：两树 `write_text` 总数均 **39**；8318 树 **19 处显式 utf-8、20 处未指定 encoding**；**12 处 `ensure_ascii=False` 全部显式 utf-8**（其中 6 处为 8318 新增，另 6 处在 934 树已带 encoding）；934 树 False×无 encoding 恰 **6** 处 = 8318 修复位（manual 370/402/415/486/520 + budget 275，与 diff 一致）；`packages/engine/src` 零 `write_text`。可证窄结论仅为：**所见 `ensure_ascii=False` × 默认编码 `write_text` 残留 0**；不得据此证明全部编码风险关闭或旧 79F 整类全因，扫描限 Python 测试树、不覆盖 TS/SQLite/C 扩展路径。**采纳**。
2. **CI 分段事实更正（修订 §2.2）**：原稿「CI 配置自 cb8 起零变化」与自身 cb8→aff 含 ci.yml 分类矛盾。正确分段：产品实现/其余测试/依赖/锁自 cb8 零变化；CI 在 cb8→aff 有一次诊断变化（+10 行），aff→934 与 934→8318 无 CI 变化；934→8318 仅两测试文件六 keyword。**采纳**。
3. **P-2 重判（修订 §5/§7/§9）**：本人独立核验 ROOT 口径的技术前提成立（package.json `engine:check` = ruff check→ruff format --check→uv pytest；根 pyproject `testpaths=["packages/engine/tests"]` 无 addopts；ci.yml `PYTEST_ADDOPTS` 仅 -vv/--maxfail=1/--tb=short 无筛选——零失败时自然 0 即全量收集/全量执行，失败才早停且早停即失败证据）。ROOT 总控已在会话内显式定义未来 CI 验收口径（既有全量标准的可核对条件；非同行意见；不改候选/CI；不预称通过；任何失败/缺结果不验收不合并；旧 79F 不追认全因）。独立判断：**"操作者显式定口径"前置已满足**，P-2 不再是独立阻断，并入 P-1；本候选**无 push 前技术阻断**，剩余为 merge 条件（新 CI 按 ROOT 口径三 job 真实 success）与流程条件（双审意见处置）；当前仍无 push/新 CI/merge 授权。本轮未因此新改代码/CI 或重跑本地。**采纳（分类更正，非改判）**。
4. **清单判定收窄（修订 §8 #16/#31）与责任承担改写（#150/#159）**：#16 单写者/启动迁移不证明迁移期间无表锁→部分适用·无法确认；#31 服务端幂等已证但客户端连点/并发去重未测→部分适用·无法确认（原稿两项"达标"过度，采纳收窄）。#150/#159 由"不适用（组织角色）"改为"部分适用·达标（本轮实际承担）"：本轮因果调试与副作用核查实际执行且边界如实（Windows 其余 79F 归因仍缺）；组织角色不适用不消解核验/调试责任的原则按此落实。**采纳**。
5. **Z-04 精确化（修订 §4/§5-P-4）**：类层 `Conflict.code` 码表缺 "ownership" 键（storage.py:57–64）与 `JobStore._application`（job_store.py:606–636 本人实读）两个实际出口分开——后者对 ownership 类冲突两分支均 `fault("OWNERSHIP_CONFLICT", detailRef=…)`：typed witness 分支（`ManualOwnershipConflict`/`SingleDeclarationConflict`，均 category="ownership"、均带真实 witness，storage.py:67–105 本人实读）与 opaque identity 分支；**不据类层缺键推该路径最终 INTERNAL_ERROR**。仍 OPEN 收窄为：通用（非 witness）ownership 冲突无可读定位 + 旧 detail 读取 INVALID_STATE→UI「详情暂不可用」降级。**采纳**。
6. **身份补记（修订 §1）**：会话 SID `session_3656bb05dd7ed7d1ccfe89755a461ace`（操作者 O043 官方 AX 读回，本人不自造）。**采纳**。

以上六项均为事实精确性修订与分类更正：**不改变 §0 两层结论、P-1 合并阻断属性、全部 OPEN/观察/HOLD 清单及 ConditionalPass 总判定**；未新增/撤销任何意见编号，1–160 逐项表完整保留。
