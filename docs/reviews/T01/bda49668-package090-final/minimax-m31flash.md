# T01 candidate bda49668 / package090 —— 指定双审报告（MiniMax M3.1-Flash / xhigh / 始终授权）

- 报告路径（本方唯一写入）：`/Users/kyle/Documents/工作/知爻/本体/outputs/20261024_t01_candidatebda49668_designated_dual_review_001/minimax/report.md`
- 本轮任务 ID：`mvs_3b7c6df7a4e14425be92353b0173ca43`（与 `minimax/actual-task-receipt.json:5` 一致）
- 候选 HEAD：`bda4966818f8af55b7726045aa65e52863317604`　parent：`212625b2440c66c9d4034cd384013d6bf6034116`　base：`5f910b52c69d86a1076b2032e5d3c63e715947f3`（实测亦为 merge-base）
- 累计：**44 commits / 573 changed paths / 1314 tracked**
- 源码 S：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-project-transactions`；Git authority：`/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio/.git/worktrees/T01-project-transactions`
- 分支：`feature/weekly-t01-project-transactions`
- 本轮为**全新、独立、完整累计**只读复审。未读取对方本轮任务/报告/目录（`.../zcode/**` 全程未打开、连列目录也未做）。未运行 build/安装/测试/GUI/APP/engine/打包/网络，未修改任何产品源码、测试、配置、依赖、索引或证据原件，未 stage/提交/推送/合并，未读写任何工具/项目/用户 memory。**本轮唯一写入物为本报告。**

**过程披露（本方自述，不隐藏）**：本任务在 09:36:14Z 出现一次 provider 中断，provider 返回了"可能涉及版权或我不便回答"的提示（见 `minimax/PROVIDER-INTERRUPTION.json`）。ROOT 在**同一原任务**内发出了一次澄清（09:37:02Z，`CLARIFICATION.json`），本方在同一任务、同一模型/同一权限下继续，未换会话、未换模型、未 fallback、未付费、未重置。原始 prompt 未被修改（48059 B / `229ece84a…5a607` 不变）。

---

## 0. 结论（先给）

### 0.1 两个互不抵销的判定

| 范围 | 判定 | 依据 |
|---|---|---|
| **当前宿主内部演示**：macOS 27.0.1 / Darwin 27.0.0 arm64，候选 `bda49668`（代码身份），同一物理 `package090`（`OntoLearn Studio.app`） | **PASS**（限定范围） | 见 §2、§3、§4：bda 相对 212 仅 1 行测试注册变更，我逐字节独立复核；本机完整 check 自然 0（139.34 s / 35 TS 文件 1694 PASS / Ruff 352 / Python 3545 收集 = 3495 PASS + 50 skip + 1 故意 duplicate-ZIP warning）；package090 的 full18（16 PASS + 2 Linux 条件 skip）、三 fault 首轮 PASS、native 0/0/1 + 真实 Cmd-Q 的既有实物证据经 ROOT 受理；我独立重算了源码连续性、66 项构建输入、1314 源叶与 APP 910 成员 |
| **正式分发 / 跨平台 / 目标平台 / 完整 MVP** | **HOLD（逐项保留，无一关闭）** | 见 §0.3 |
| **FR 结算** | **0/17 不变；FR003 仍 partial；不预结 FR401/402** | `release-scope-2026-10-25.csv` 实读：59 行中 17 行发布目标为 2026-10-25，其「状态」全部为"未取得完整产品正式完成证据"；「正式证据/PR/merge」列 59 行全空 |

> 口径纪律：本报告的"绿/0/PASS"全部是对**既有冻结证据**（先核 bytes/SHA 后读）与**本轮现码静态直核**的结论，**不构成新的运行证据**。本地绿 ≠ 远端绿；Windows native 未验 ≠ Windows 通过；内部演示 PASS ≠ 正式分发通过。

### 0.2 本轮我自己的新发现（此前各轮均未登记）

1. **【证据更正｜Low】red 的 exit 1 是探针自设的退出码，不是 pytest 的原生错误退出。** `fixture-red.stdout.log` 只有 `6/32 tests collected (26 deselected) in 0.06s`，**没有 pytest 的 ERROR 段**；非零退出来自探针自身的 `pytest_sessionfinish` → `session.exitstatus = 1`（`fixture-collection-probe.py:33-35`，当 `self.passed` 为假）。因此"预期 red 自然 1"的措辞应更正为"**探针判定失败导致的非零退出**"。**实质缺陷与修复仍然成立**——缺失事实由 `fixture-red.json` 中六个节点的 `name2fixturedefs.bundle == []`（且 `tmp_path` 亦为空）独立证明，与退出码来源无关；且 `--collect-only` 不执行 setup，故该探针**本身并不复现** Windows 上"6 ERROR"的运行后果，那仍是基于 pytest 公开语义的推断。ROOT 受理票与统一处置 §10 中"red 自然 exit 1"的记录按此更正，不改原文件。
2. **【平台｜High·新增】bda 使 6 个 Windows native 用例在 Windows CI 上"首次真正执行"，其自身结局目前未知。** 修前：Windows 上 `skipif(os.name != "nt")` 为假 → fixture 解析失败 → setup ERROR（快速、响亮、fail-closed）。修后：`.github/workflows/ci.yml:112-129` 的 `windows-latest` 矩阵先跑 `npm run engine:check`（内含 pytest），这 6 例将**第一次**在真实 NTFS 上走完 `WindowsResourceRoot` / `NtCreateFile` / junction / 句柄关闭路径。这批代码路径**从未在任何机器上执行过**（不是"未在 Windows 上验证"，而是"从未运行"），可能因环境（runner 临时盘文件系统、`cmd mklink /J` 可用性、持句柄下的 rename/share 语义）而失败。**故 fixture 修复是"必要但远不充分"**：它关闭的是接线缺陷，不是平台验证门；首个真实 Windows 运行应按"首次执行、结局未知"预期，而不是走过场。
3. **【证据｜Medium】"承接 090 产品运行证据"这一桥接在本候选上是充分的，且我独立复核了它的边界，而非沿用其结论。** 承接成立的具体依据是：bda 相对 212 的**全部**差异只有 1 个测试文件 1 行；生产/构建输入 66 叶在 S 与 C 双根均逐字节未变；APP090 910 成员与根 mode 与原物逐项相同；ASAR/engine 载荷哈希与原物相同。**不充分的部分只有一处且已被诚实披露**：新 check 产出的 `out/main/index.js` 与已封装 090 的同名文件**字节不同**（见 §2.5），因此不能称"新五件全部同旧 hash"；该差异我实测为**仅一处 24 字符 dev CSP nonce literal（23 个字节位不同），其余 594318 字节逐字节相同**，且该 nonce 只在 `devURL` 分支生效，生产 CSP 变体不受影响。
4. **【现状｜确认】"缺 fixture"这一旧发现已在 bda 被真实修复，且未新增任何耦合。** 现码 `packages/engine/tests/test_windows_example_resource.py:10` 为 `from test_mainline_example_provider import bundle as bundle`；该模块在 212 就已有 `from test_mainline_example_provider import load`，故**导入期依赖未增加**，只是把 fixture 对象带入本模块命名空间。全仓无 `conftest.py`（`git ls-files | grep conftest` 为空），`pyproject.toml` 仅设 `testpaths`，即默认 prepend 导入模式，`packages/engine/tests` 被放入 `sys.path` —— 这条链路 212 已依赖且 212 全量绿，本轮不引入新前提。写法与仓内既有惯例完全一致（`test_mainline_cleanup_regressions.py:10` 的 `staged_bundle as staged_bundle`、`test_mainline_draft_dispatch.py:17` 与 `test_mainline_query_changeset.py:21` 的 `owned as owned`）。
5. **【机制｜确认】`uncertain` 闩锁在当前 bda 仍为单向。** 我在现码上重新穷举 `apps/desktop/src/main/engine.ts` 全部 `uncertain` 赋值：`:822`（delivery.records 置位）、`:2098`、`:2501`、`:2566` 三处写入点，全部是 `= true`，**全文件无任何复位为 false 的路径**；读点 `:714`、`:957` 一致。此项不因 bda 变化，也不因本机 check 全绿而改变。
6. **【机制｜确认】四个 16 槽责任账本在 bda 仍是四个，未合并。** `engine.ts:771`（`#mainlineDeliveries`）、`engine.ts:1167`（`#mainlineRecords`）、`desktop-ipc.ts:164`（`deliveries`）、`project-mainline-service.ts:735`（`#fullIntents`）各自独立；**不得相加为 8**。

### 0.3 正式/平台 HOLD（逐项保留，本轮无一关闭）

签名与公证；安装器与升级路径；wholeAPP legal 与 `_distutils` 来源闭包；Windows 真机打包与运行（含本轮修好的 6 个 native 用例的真实执行）；目标 macOS 15 arm64；参考/五龄设备；损坏 SQLite 物理保护（B/C 未授权）；D2 性能/规模/索引口径；D8 双审熔断与 C4–C6 积压；用户备份与恢复演练；FR-002 / FR-203 / FR-300 P0 缺口；真实 LLM 与 I06 网关及 S3 前置（密钥、prompt injection、spend cap、evals、供应商降级/弃用）；静态加密与设备被盗预案；渗透测试与安全问卷证据包；"谁查看过"审计；a11y/键盘/读屏、RTL/i18n、全屏空/加载/错误态与表单保留/返回语义；依赖 advisory 与 Python 自动扫描；远端分支保护；组织归属与 bus factor；CI29（run40071234771 / head `8be6f08a`）Quality FAILED / macOS FAILED / Windows CANCELLED（20 m 门）根因未闭；**0/17 发布流程**（push → PR → 真实新 CI 全绿 → squash develop → 远端复核，均未执行）。

---

## 1. 受理与边界回读（本方实测）

### 1.1 附件与原用户清单

| 对象 | 期望 | 本轮实测 | 判定 |
|---|---|---|---|
| 附件（=本 lane `prompt.txt`） | 48059 B / `229ece84a…5a607` | `stat` 48059；`shasum` 逐字相符；与 `actual-task-receipt.json` / `launch.txt` 登记一致 | ✅ |
| 原 11255 B 清单 | 逐字保留、恰一次、在 EOF | 文件末 11255 B 的 SHA256 = `1ca23def39d88ceaace9ad1b8aa14ee8714229871e9d6b1d1edd0f9e847f709c`；首行"你现在是我的软件工程审查员。"；特征串"你现在是我的软件工程审查员。"/"a schema someone designed"/"1,382.59"/"remembering why it's built this way"在全文各**恰 1 次** | ✅ |
| 清单结尾 | 无尾随字节 | 末字节为 `)`（`…(someone who was there)`），无换行追加 | ✅ |
| 阅读完整性 | 读至 EOF 恰一次 | 用官方文件读取工具分 3 段连续读至第 313 行 = EOF，**未重复读、未抽样** | ✅ |

### 1.2 实际设置与路径

| 项 | 本方实测 | 判定 |
|---|---|---|
| provider / model / 思考 / 权限 | `minimax` / **MiniMax-M3.1-Flash** / **xhigh** / **始终授权（bypassPermissions）** | 运行时环境 + `actual-task-receipt.json:11` 双向一致；本轮未因权限受阻缩减任何动作 |
| 任务 ID | `mvs_3b7c6df7a4e14425be92353b0173ca43` | 会话 ID 与派发回执一致 |
| cwd | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-project-transactions` | `pwd` 实测逐字相同（含中文 Unicode 路径） |
| 规范源码目录 | 同上 | 派发回执记录主线已用 MM 原生选择框逐字回读重选；**本方在只读边界内以 `pwd` + Git worktree 注册 + 全部原件路径解析三处字节级一致独立复核**，未操作 GUI（越过本轮只读边界） |
| 报告路径 | `.../minimax/report.md` | 与派发回执 `reportPath` 一致；写入前该文件**不存在**（目录存在 ≠ 报告已生成） |
| 宿主 | macOS 27.0.1 / Darwin 27.0.0 arm64 | 与 ROOT 受理的当前主机范围一致；目标 macOS 15 仍 UNVERIFIED |

### 1.3 Git / 工作区身份（全部 `git --no-optional-locks`）

| 对象 | 期望 | 本轮实测 | 判定 |
|---|---|---|---|
| git-dir | `…/OntoLearn-Studio/.git/worktrees/T01-project-transactions` | 同 | ✅ |
| HEAD | `bda49668…17604` | 同 | ✅ |
| HEAD^ / parent | `212625b2…4116` | 同 | ✅ |
| base / merge-base | `5f910b5…947f3` | 两者均为该值 | ✅ |
| branch | `feature/weekly-t01-project-transactions` | 同 | ✅ |
| commits base..HEAD | 44 | 44 | ✅ |
| changed paths base..HEAD | 573 | 573 | ✅ |
| tracked files | 1314 | 1314 | ✅ |
| 工作区状态 | 仅 ` M AGENTS.md` | 同 | ✅ |
| cached / untracked | 空 / 空 | 空 / 空 | ✅ |
| AGENTS.md overlay（S 工作区） | 15147 B / `de15f6ce…5c8c4` | 同（**受保护、非产品变更、未编辑/未重置/未 stage**） | ✅ |
| AGENTS.md committed（C checkout 内） | 1056 B / `1b3c0291…43a6fb` | 同；**S 与 C 的这唯一 AGENTS 差异不得混同** | ✅ |
| index 文件 | 179247 B / `3e9e222d…2ba42d` | 同（`OntoLearn-Studio/.git/worktrees/T01-project-transactions/index`） | ✅ |
| 索引树 vs HEAD 树 | 一致 | 均为 `ef1704c2fe29aeede2e979b29500256582a39e7c`（工作区无内容性改动） | ✅ |

> `S` 与 `C`（`outputs/20261024_t01_windows_pytest_nodeid_fix_001/clean-checkout`）是**两个不同根**：S 只有受保护 AGENTS overlay，C 的 AGENTS 是 committed 1056 B 版。bda 在两处 HEAD 一致。

### 1.4 本轮只读边界（严格遵守并自证）

只使用：文件读取、标准库文本/JSON/哈希/字节比较、`git --no-optional-locks` 只读查询、既有 JSON/日志/证据原件的逐针核对。
**未**运行：build / 安装 / 测试 / GUI / APP / engine / 打包 / 网络；**未**打开任何活跃可变 DB；**未**执行对方或任何待审脚本；**未**写入本报告之外的任何文件；**未**读取对方本轮 `zcode/` 目录。
本轮所有"我实测"的判定均标注了证据类型：**静态观察** / **静态推断** / **既有运行证据复核** / **打包实物复核** / **生产事实**。

---

## 2. 本轮直接变化与新证据（A 段）逐件独立复核

### 2.1 唯一改动：一个 fixture 显式注册

`git diff 212625b2..bda49668` 全量输出**只有 1 个文件、+1 行**：

```diff
--- a/packages/engine/tests/test_windows_example_resource.py
+++ b/packages/engine/tests/test_windows_example_resource.py
@@ -7,6 +7,7 @@ import subprocess
 import pytest
 from ontolearn_engine.project import _windows_resource as resource
 from ontolearn_engine.project.mainline import ExampleResourceFault, make_example_provider
+from test_mainline_example_provider import bundle as bundle
 from test_mainline_example_provider import load
```

| 项 | 212 | bda | 判定 |
|---|---|---|---|
| 文件字节 / SHA256 | 10529 / `5273b28b…67588` | 10589 / `a11455af…be27f` | 与任务书一致 |
| blob | `cbae1f82…` | `b11b071e…` | — |
| AST 差异 | — | 仅 1 条 `ImportFrom`；其余 AST 全等 | 与 `AST-DELTA.json` 一致；**我另以现码全文实读核对**：6 个 `@native` 用例的参数化展开（1+2+3）、`skipif` 条件与 reason、`assert` 文本、真实 API 调用（`WindowsResourceRoot`/`make_example_provider`/`load`/`ctypes.WinDLL`）**逐字未动** |
| 提供者模块 | `test_mainline_example_provider.py` 4960 B / `ecdac934…fe875` | 同（**未改**） | fixture 真定义在 `:15-33`（`@pytest.fixture def bundle(tmp_path)`），**不是复制品** |
| 是否有 conftest / fixture 复制 / mock / skip 扩张 | 无 | **仍无**：全仓 `git ls-files` 无 `conftest.py`；`pyproject.toml` 无 `pytest_plugins`；skip 条件与数量未变 | 无扩张 |

### 2.2 red → green collection probe（我逐字段实读，非采信结论）

探针本体（`fixture-collection-probe.py`）以 `pytest.main(["--collect-only","-q","-p","no:cacheprovider","-k","test_native_", …])` 运行，并在 `pytest_collection_finish` 读取 `item._fixtureinfo.name2fixturedefs`。

| 项 | red（212 状态） | green（bda 状态） |
|---|---|---|
| cwd | `…/20261024_t01_windows_pytest_nodeid_fix_001/clean-checkout` | 同 |
| 起止 / 耗时 | 09:12:24.642359Z → 09:12:24.908795Z / 0.2664617089321837 s | 09:13:01.807923Z → 09:13:02.065793Z / 0.25790195795707405 s |
| exit / 期望 | 1 / 1（expectedRed） | 0 / 0 |
| 收集节点 | 恰 6 个，原 nodeid 逐字（1 个 held-bundle + 2 个 junction[intermediate/root] + 3 个 api-failure[info/read/open]） | 同 6 个，**逐字相同** |
| `bundle` fixture 定义 | **空数组** | 1 条：`module=test_mainline_example_provider`, `function=bundle`, `file=…/clean-checkout/packages/engine/tests/test_mainline_example_provider.py` |
| `tmp_path` 定义 | 空数组 | 1 条：`module=_pytest.tmpdir`, `function=tmp_path`（真实 pytest 内置） |
| `skipif` marker | 6 个，reason 全为 `real Windows HANDLE / NTFS contract` | **完全相同**（未改平台条件、未放宽） |
| `nativeBodiesExecuted` | false | false |
| 平台/跳过是否被改 | false | false |

**我自己的判断**：
- 修复**真实成立**：缺的是"本模块命名空间里没有该 fixture 定义"，修后解析到的是**原提供者的真实 `bundle`**，不是复制、不是替身、不是 mock；`tmp_path` 解析到真实 pytest 内置。六例的 nodeid、参数、skip 条件一字未动。
- **red 的非零退出是探针自设**（见 §0.2-1）：pytest 自身在 `--collect-only` 下没有产生任何 ERROR 输出。事实层面，缺失由 `name2fixturedefs.bundle == []` 独立证明，退出码来源不影响结论；但"自然 1"的措辞需要更正，且**不能据此宣称"Windows 上 6 ERROR"已被复现**。
- **Windows 侧结论不变**：这 6 个测试体在本机从未执行（`skipif` 为真），Windows 上零运行证据。

### 2.3 完整 check（既有运行证据，我读原始日志并独立重算分解）

| 项 | 值 | 核验 |
|---|---|---|
| 命令 / cwd | `uv run --frozen npm run check`；`…/20261024_t01_windows_pytest_nodeid_fix_001/clean-checkout` | 与 `FULL-CHECK.json` / `FULL-CHECK-START.json` 一致 |
| HEAD | `bda49668…17604` | 与当前 S/C 一致 |
| attempt | 1（单次） | `attempt: 1` |
| 起止 | 09:13:17.542954Z → 09:15:36.879428Z | — |
| 耗时 / 退出 | 139.33603262493853 s / **exit 0，自然退出** | — |
| 源前后字节 | source / clean 均逐字节不变 | `source-check-before.json` 与 `source-check-after.json` **同 SHA `186f030a…`**；`clean-check-before/after` 同 SHA `6bb38dbe…` |
| eslint / prettier | `--max-warnings 0` 通过；`All matched files use Prettier code style!` | 原始日志实读 |
| typecheck | contracts / unit / desktop 三路全过 | 原始日志实读 |
| vitest | **35 文件 / 1694 PASS** | 原始日志实读 |
| build | main 594.34 kB、preload 391.73 kB、renderer html 0.70 kB / css 11.04 kB / js 1,201.46 kB | 与 `check-actual-five-JS.json` 字节数一致 |
| ruff | `All checks passed!` + `352 files already formatted` | 原始日志实读 |
| pytest | **collected 3545 = 3495 passed + 50 skipped + 1 warning**，119.77 s | 终端总结行原文：`3495 passed, 50 skipped, 1 warning in 119.77s`；唯一 warning 是 `test_prepare_fr003_bundle.py` 里**故意**的 duplicate ZIP |
| **skip 分解（我独立重算）** | **44（`test_project_format3.py`）+ 6（`test_windows_example_resource.py`）= 50** | 我按日志进度字符逐文件重算：仅这两个文件出现 `s`；Windows 文件为 26 通过 + 6 skip = 32 项，与探针"6/32 collected (26 deselected)"互相印证 |
| 预算 / 断言 | 未改 | `alteredTestBudgets: false`；我实读现码，6 例断言与参数未动 |

> **重要口径**：`ssssss` 是 macOS 上的**平台条件 skip**，不是"Windows 已通过"，也不是"产品已拒绝"。50 skip 中仍有 6 项是本候选最关心的 Windows 生产分支，**零运行证据**。

### 2.4 产品连续性（bda → 同一物理 090）：我独立重算，不采信其结论

| 承接项 | 任务书声明 | 我的独立实测 | 判定 |
|---|---|---|---|
| S 其余 1313 叶 | 与 212 逐字节相同 | 以 `source-before.json`（212 快照，1314 条）为基准，对 S 逐叶重算 bytes+SHA：**差异恰 1 条** = 允许的那一个测试文件 | ✅ |
| C 其余 1313 叶 | 同上 | 以 `clean-before.json` 为基准对 C 重算：**差异恰 1 条**，同一文件 | ✅ |
| 生产/构建输入 66 叶 | 未改 | `BUILD-INPUTS-212625b2.json` 的 66 项在 **S 与 C 双根**逐项重算：**0 不符** | ✅ |
| N（node-checkout）旧 1314 | 仍为 212 原样 | 逐叶重算：**0 不符**；其 5 件 JS 亦 0 不符 | ✅（N Git UNBORN，非源码 authority） |
| APP090 910 成员 | 与原物同 path/kind/mode/hash/linktarget | 我以 `package-readback.json` 重建期望集合（910 条），再对冻结 APP 实物逐路径重算（symlink 读 target、目录读 mode、文件读 bytes+SHA）：**observed == expected == True**；根 mode 期望 493 / 实测 493 | ✅ |
| ASAR / engine 载荷 | 19014603 / `fbf5741e…`；6232272 / `c6d12ac5…` | 我直接对冻结 APP 实物重算：**19014603 / `fbf5741e…76`**、**6232272 / `c6d12ac5…13`**，逐字相符 | ✅ |
| 新 engine/包/运行时 | 未重跑 | 证据与实物均无新 runtime 记录；旧 raw 的 HEAD 仍为 212 | ✅ |

**承接充分性判定（本轮核心）**：
- **充分的部分**：bda 相对 212 的**全部**差异是一个测试文件的 1 行；该行不进入任何生产路径、不进入任何构建输入、不进入 66 项生产依赖、不改变 APP 实体、不改变引擎二进制。因此 package090 的**同一物理实物**在 bda 下依然成立，其 full18 / 三 fault / native 的成功谓词未被本次改动触及。**这不是"任何一行变更都要重跑历史"的 blanket 要求**，而是逐针证明了"影响输入集合为空"。
- **不充分的部分（只有一处，且已被诚实披露）**：新 check 产出的 `out/main/index.js` 与已封装 090 的同名文件**字节不同**。因此**不能**称"新五件全部同旧 hash"，也**不能**把新 build 反向采入旧 090。详见 §2.5。
- **仍需后继**：真实 Windows CI 必须跑通（§0.2-2）；PR6 push → 真实新 CI 全绿 → squash develop → 远端复核 → ROOT 结算，一步未做。

### 2.5 五件构建产物与 nonce 差异（我做了字节级独立核验）

| 产物 | 旧（212 / 已封装 090） | 新（bda 本次 check） | 判定 |
|---|---|---|---|
| `out/preload/index.js` | 391731 / `e50e629b…8bc3` | 391731 / `e50e629b…8bc3` | **完全相同** |
| `out/renderer/assets/index-CFiAwwRM.css` | 11040 / `59ac41c5…22a5` | 11040 / `59ac41c5…22a5` | **完全相同** |
| `out/renderer/assets/index-CHAACd0i.js` | 1201461 / `f1c984a6…a1c` | 1201461 / `f1c984a6…a1c` | **完全相同** |
| `out/renderer/index.html` | 709 / `80672ec7…f93d1` | 709 / `80672ec7…f93d1` | **完全相同** |
| `out/main/index.js` | 594342 / `2fa0f2a3…39a1` | 594342 / `6f408120…d595` | **字节数相同、内容不同** |

**我的独立字节核**：以冻结 090 的 ASAR 回读件 `out/main/index.js`（其 SHA `2fa0f2a3…39a1` 与旧五件登记**完全一致**，说明我对的是同一实物）与新 build 逐字节比较：**长度同为 594342，差异恰 23 个字节位，全部落在 offset 590253–590276 这一处 24 字符字面量内**（旧 `"2hH2ltkJ1J9WLiBV5V5ztP3k"` → 新 `"mSj5sG2OhI9XdyzpHOKsddAK"`；23 是因为其中 1 个字符恰好相同），该区间**之外 594318 字节逐字节相同**。

**该差异的产品含义（我核了源头）**：`apps/desktop/src/csp.ts` 的 `contentSecurityPolicy(development?)` 只在传入 `development` 时才写入 `nonce` 与 `connect-src` 放宽；生产变体不含 nonce，且 `script-src` 无 `unsafe-inline`/`unsafe-eval`。`electron.vite.config.ts:7` 在**模块顶层**生成 `randomBytes(18)` 并对**所有**构建生效 —— 这就是"每次构建 main 字节不同"的根因（与上一轮 MM-O36 一致，本轮在字节层确认）。因此：
- 该 nonce **只在 devURL 分支生效**，不改变已封装 090 的生产 CSP 行为；
- 但它使 **main bundle 不可按字节复现**，任何"新 build 与旧包逐字节相同"的断言都不成立 —— 任务书与 `PRODUCT-CONTINUITY.json` 在这一点上表述准确（`notRestoredOrAdoptedIntoOldRuntime: true`）。

### 2.6 reader 纠正与 ROOT 受理票

- `BEFORE-READER-CORRECTION.json`：首个 preflight 元数据读取器把 `git ls-files -z` 的**末尾 NUL**当作一个空项，导致 `len(paths)==1314` 断言失败。纠正 = 过滤末尾空分量。`sourceOrIndexWritten: false`、`testsOrAppExecuted: false`、`priorEvidenceOverwritten: false`。
  **我的判断**：这发生在**任何源码/测试/索引操作之前**、且是**证据读取工具自身**的缺陷，不是 pytest 首败、不是产品失败、不是重跑。纠正被如实保留（未抹除），符合"不把从无失败当从未发生"的要求。**该事件不构成任何产品结论的推翻，也不构成重试证据。**
- ROOT 受理票 `controller-t01-bda49668-fixture-and-product-continuity-root-acceptance-20261024.json`（我实测 **7268 B / `02a87482ce57fb5b44714e20014ab877f89cb1ac8ad6ab91f041ff9467d3bca1`**，与任务书一致）实读要点：`acceptedFixtureOnlyChange: true`、`acceptedFullCheck: true`、`acceptedSamePhysicalPackage090ProductContinuity: true`、`newRuntimeRunClaimed: false`、`parentRuntimeRawHEADUnchanged: "212625b2…"`、`Windows6NativeVerified: false`、`targetMacOS15Verified: false`、`pushAllowed: false`、`mergedUsableFRs: "0/17"`、`ROOTProductOrTestExecution: false`、`freshDesignatedPairAdmitted: true`。
  **我的判断**：受理票与我独立重算的连续性结论**逐条一致**，未发现受理票与实物之间的矛盾；但它受理的是"精准桥接"，**不等于** bda 已取得任何新的运行证据或平台资格。
- `DELIVERY-bda49668.json`（12849 B / `49b8652c…7dc`）列出 38 件证据引用，其 `ROOTAcceptance`/`freshDesignatedPair` 字段在**形成时刻**为 `PENDING`/`NOT_YET_ADMITTED_OR_DISPATCHED` —— 按形成时刻保留、由后继 ROOT 受理票取代，**不改写原件**。

---

## 3. 产品运行证据（B 段）与它对 bda 的承接力

### 3.1 证据身份（我逐针核过引用哈希）

- `ENTRY.json`（8592 B / `95eeb5f4…12e0`）：`HEAD: "212625b2…"`，`scope: "macOS27.0.1/Darwin27 arm64; mac15 target and Windows6 UNVERIFIED. All formal release/legal/SQLite/D2/D8/LLM/referencehardware HOLD remain. No push/merge or FR closure."`，`attemptsPerMode: 1`。
- `full18Stats`：`collected 18 / passed 16 / skipped 2 / unexpected 0 / flaky 0 / durationMs 85908.478`。
- 三 fault：`reload`（main 90722）、`renderer-recovery`（main 90921）、`coordinator-exit`（main 91067），均 `result: PASS`、`driverNaturalExit: 0`、`guards.pre/post: 0`。
- `native-lifecycle`：`result: "NATIVE_RESTORE_DECLINE_NORMAL_QUIT_OBSERVED"`、main 91191、engine 91199。

### 3.2 关键数字（我从 ROOT 故障/native 复核件独立抽取核对）

| 断言 | 我的实测 | 判定 |
|---|---|---|
| coordinator 的被故障引擎是**真实 SIGKILL**，非自然 0 | `engineChildEvents[0] pid 91072 exit/close signal = SIGKILL`；替换引擎 `pid 91074 exit/close signal = null`（自然 0） | ✅ 属实，且**不得**写成"所有进程 exit 0" |
| 三 fault 的目标 Job 终态**不一致** | reload / renderer → `succeeded`；coordinator → `failed` / `ENGINE_EXITED`（已授权故障，非重提成功） | ✅ 属实 |
| native 三次真实 prompt 响应 0/0/1 | `CUA.nativeActions[].response = 0, 0, 1` | ✅ 属实 |
| CUA 链是 **11 对 call/output，不是 11 次点击** | `CUA.pairedCalls = 11`，`allCallIDsHaveOneMatchingOutput = true` | ✅ 属实 |
| native 窗口数 3、拒绝后无第 4 窗 | `native-lifecycle.windows = 3` | ✅ 属实 |
| 有限 PID 采样，不推全局 drain | 独立复核件仅对**已知** PID 记 absence | ✅ 属实 |
| `resourcesPath`/`execPath` 按路径分列 | 三 fault 的 `actualApp` **有** appPath/resourcesPath；native 记录**无**该字段；full18 helper 未直接提供 getter | ✅ 属实；**不得**笼统降为 UNKNOWN，也**不得**回填未提供字段 |

### 3.3 承接是否充分（我自己的判断）

**充分**，理由已由 §2.4 逐针给出：bda 的影响输入集合为空（1 个测试文件 1 行，不进生产、不进构建输入、不进 APP 实体、不进引擎二进制）。090 的机械包身份、full18 / 三 fault / native 的成功谓词**未被本次改动触及**，因此以"同一物理实物"承接是成立的。

**但不充分的部分只有一处，且必须保留**：
1. 新 build 的 main bundle 与旧包字节不同（§2.5）——真实存在，不得说"五件全同"。
2. **bda 没有、也不可能有任何新的 Windows native 运行**；且如 §0.2-2，bda 使这 6 例**首次真正执行**，其自身结局未知。
3. 旧 090 runtime raw 的 HEAD 仍是 212 —— 引用时必须标 212，不得涂改。

**据此给出的具体"影响输入 / 成功谓词"**（供 ROOT 判定桥接充分性时使用）：
- 受影响输入集合 = ∅（生产源码、契约、依赖/锁文件、`scripts/`、构建配置、引擎源、打包配置**逐字节未动**，66 项构建输入双根复核 0 不符）。
- 受影响谓词集合 = ∅（full18 的 18 条定义、三 fault 的四个谓词、native 的 0/0/1 与 Cmd-Q 全部只依赖未变的生产二进制与 APP 实体）。
- **唯一新增未覆盖谓词** = "6 个 Windows native 用例在真实 NTFS 上的执行结果"（bda 前不可达、bda 后可达且未知）。
- **未受影响但仍未闭的谓词** = Windows 全平台、macOS 15、签名/公证、legal 闭集、D2/D8、真实模型、恢复演练、远端 CI 绿。

---

## 4. 现码第一手直核（E 段主线）

> 以下位置均指当前 bda 工作树（与 212 相同，因 bda 只改了一个测试文件）。判定后标注证据类型。

### 4.1 preload（唯一桥接）

`apps/desktop/src/preload/index.ts`（86 行，全文实读）：
- 暴露面是**按业务命名的方法**（`:49-85`），**没有** `invoke(method, params)` 式通用通道；无 Node/fs/shell 能力进入 renderer。
- `receiveMainline`（`:14-47`）：先取业务结果 → 解析 delivery envelope → **恰好一次** `project:reply-received` ACK 与 5 s 超时竞速 → ACK 失败走 `catch {}`（`:40-42`）**静默吞掉** → 但 `:46` **仍返回业务 payload**。注释自述"Main keeps the original unacknowledged lease; no retry/clear is fabricated"。
  **判定（静态观察）**：单次 ACK、无产品自动私有重试，**成立**。原处置 MM-O17 的纠偏（ACK 失败仍返 payload、成功 accept 时清 pending、不得说"16 次恢复点击必成功"）在现码仍**成立**。这是**保责任、无恢复通道**的潜伏脆弱性，自然触发未被证明。

### 4.2 desktop-ipc（IPC 闸门）

- `trusted(event)`：`apps/desktop/src/main/index.ts:317-323` —— `event.sender === window.webContents` **且** `event.senderFrame === window.webContents.mainFrame` **且** `isTrustedDocument(event.senderFrame.url, trustedURL)`。**三重校验成立**。
- `deliveries`（`desktop-ipc.ts:105`）上限 16（`:164`）；**唯一 `deliveries.delete(id)` 在 `:142`（consume 成功之后）**；consume 抛错路径先 `return permission()`（`:136-140`），**跳过删除**；`accepted` 的 FIFO 驱逐（`:144`）**只作用于已消费身份**。
  **判定（静态观察）**：未 ACK 的 delivery 永不释放、且**不参与** FIFO 驱逐；"非每 UNKNOWN 都建 IPC delivery"在 `receive` 先于 deliveryId 生成处成立（`:172-174`）。四个 16 槽账本独立，见 §0.2-6。

### 4.3 project-mainline-service（幂等与恢复）

- `#keepIntent`（`:621-636`）：紧凑身份 `{operationId, request, engineSessionId, jobId}` 单独 `retainHolding`（`:625`），注释明写 **never FIFO-forgotten**；有 accepted 时另 `retainHolding(intent.payloadEntry, accepted)`（`:632`）。
- `#offerIntent`（`:637-660`）：退役回调**只**释放 `payloadEntry`（`:650`）；释放失败**恢复 `intent.accepted` 并原样上抛**（`:651-654`）；`pendingReplies.size > 1` 时**只删自己**的令牌（`:642-644`）；`#fullIntents.delete(intent)`（`:656`）是**全文件唯一**删除点。
- `#readAcceptedIntent`（`:661-699`）：**只发 `job.get`**（`:676`，无 `job.create` 重放），并对返回 job 做**六项全等校验**：`jobId` / `projectId` / `operationId` / `capability` / `confirmationRef` / `stable(job.input) === stable(request.input)`（`:683-692`），任一不符即 `invalid()`；随后 `this.source.current() !== current → denied()`（`:693`）。
- `#fullIntents` 上限 16（`:735`）；`intent.unknown → denied()`（`:751`，注释 "No automatic replay of an entered write."）。
  **判定（静态观察）**：M3 的完整义务语义（不 FIFO、不代 ACK、无偿退款、不删除 origin、不建持久意图账本）在现码**逐条成立**；`queryWriteEntered(pin)`（`:775`）区分"已入线未知"与"未入线已知失败"，后者可按原参数重试完成 —— **不得**写成"每次重试都新铸 operationId 失败占位"。

### 4.4 engine.ts（会话、账本、容量）

- `uncertain`：**只置位不复位**（`:822/:2098/:2501/:2566` 全部 `= true`；读点 `:714/:957`）→ **M1 单向闩锁成立**（§0.2-5）。`health`/独立 TaskService 走各自 session/generation，不等于整个应用停止。
- `#mainlineDeliveries` 上限 16（`:771`）；`#mainlineRecords` 上限 16（`:1167`，**只 set 不 delete**，`:1310`）→ 准确口径是初始 1 + 15 次继任 = 16，第 17 个新 record 被拒，且**有效 client 优先复用**；`#fullIntents` 16（service `:735`）；IPC `deliveries` 16（`:164`）——**四个独立账本，不相加**。
- `#retainHolding`（`:835-871`）的预算公式：`maximum = min(floor((134217728 − bytes − 4096)/32), 1048576 − objects − 128, delivery ? 134217728 : 263168)`，`maximum < 1 → invalidStateOrdinary()`（`:858`）。
  **我的独立结论（更正上一轮 MM Top-2 的数字与后果）**：该式**成立**，但
  (a) `b` 是 `mainlineHoldingMeasure` 的保守 JSON 量（含 key/引号/指纹内再转义），**不是简单字符数**；
  (b) **第三根轴 263168 是常驻 scratch**，只看 objects 轴会高估容量；
  (c) `maximum < 1` **不是唯一拒绝出口** —— `measure` 超限、`#mainlineReserve`、先付新重叠都可能更早拒；
  (d) 因此**不能**把"1183 次""1.1k–1.5k"当固定阈值，也不能推"全 App 永久冻结"。真实边界是"**同一 EngineSupervisor 实例**内该类身份无释放路径，累积到预算耗尽时安全拒绝"；换 session 不退旧账，但**重建 supervisor/重启应用会建新账本**（进程内账本重置 ≠ 原未知副作用已对账）。
- `#releaseHolding`（`:872-883`）：拒绝条件是 `holding.record !== record`（**不检查 currentSession**），`bytes === 0` 幂等返回，释放时 `holding.value = undefined`；`#mainlineHoldingEntries` 为 WeakMap，**只有 set 无 delete**。

### 4.5 Windows 资源读取器与 format3（平台分支）

`_windows_resource.py`（当前 11396 B / `0a7cac52…9843`）：
- `access = 0x100000(SYNCHRONIZE) | 0x80(FILE_READ_ATTRIBUTES) | (0x20 FILE_EXECUTE 目录 / 0x1 FILE_READ_DATA 成员)`（`:167`）；
- **ShareAccess 仅 `0x1`（FILE_SHARE_READ），目录与成员都拒绝 WRITE/DELETE**（`:175-176`）；
- CreateOptions `0x200000(FILE_OPEN_REPARSE_POINT) | 0x20(FILE_SYNCHRONOUS_IO_NONALERT) | (目录不加 FILE_DIRECTORY_FILE，成员加 0x40 FILE_NON_DIRECTORY_FILE)`（`:177`）—— **目录 type-neutral 是字节层面真实成立的**；
- 设备名必须匹配 `\Device\HarddiskVolume[0-9]+`（`:227`，排除 SUBST/映射盘），文件系统必须 `NTFS`（`:242`）；
- 读取上限 `maximum + 1`（`:247`），失败一律收口为 `EXAMPLE_RESOURCE_UNAVAILABLE`。
**判定（静态观察）**：结构与上一轮独立核一致，未发现 ABI 缺陷。**残余结构性限制（此前已披露，本轮复核仍成立）**：两次身份采样之间的窗口**不能证明**"期间始终无 reparse"；共享规则**不自动阻断**所有 FSCTL 元数据操作；`maximum+1` 是**字节上限而非墙钟上限**。**真实 Windows 执行 = 零**。

`format3.py:171-187`：`backup.close()` → `target.open("r+b" if os.name=="nt" else "rb")` + `os.fsync` →（仅 POSIX）父目录 fsync → `proof = sha256(target.read_bytes())` → `hook("after_backup")`。**次序完整保留；无写截断、无吞错误。**
**归因更正（沿用并确认上一轮 ROOT 事实核 F2）**：Windows 上**没有**这里的显式父目录 fsync，是**既有平台差异**（501 已有 `if os.name != "nt"` 条件），**不是** 212 引入的新回归。缺口本身仍存在：**"备份内容已持久"在 Windows 上成立，"备份目录项已持久"未被证明**。建议不采信未经证明的 `FlushFileBuffers` 实现，也不据此降级既有不变量。

### 4.6 CSP 与渲染隔离

`apps/desktop/src/csp.ts` 是**唯一** CSP 配置源：生产变体 `connect-src/object-src/base-uri/frame-src/form-action` 均 `'none'`，`script-src 'self'` **无 `unsafe-inline`/`unsafe-eval`**；仓库内 `unsafe-inline` 仅出现在**开发分支**的 `style-src`（Vite CSS HMR 用途，`:20`，附注释说明生产用本地 CSS），不影响生产变体。
**判定（静态观察）**：CSP 唯一源、生产无 unsafe、渲染端隔离三条不变量在现码**成立**；渲染端无 `dangerouslySetInnerHTML`/`innerHTML`/`document.write` 的既往结论在 bda 未受影响（本轮未重扫全量，按未改动的同一字节来源承接）。

---

## 5. 上一轮全部意见的独立处置

> 口径：confirmed=事实成立；qualified=机制成立但时序/范围/后果须限定；refuted=具体断言与固定事实冲突；HOLD=门未闭。**我改的是判定，不改原模型的严重度与原文。** 上一轮两份报告与统一处置均已全文实读（775 行 / 193 行 / 485 行），两份独审与 ROOT 事实核亦已全文实读。

### 5.1 MM Top10 逐条

| ID | 原标题（等级） | 我的独立判定 | 依据 / 边界 |
|---|---|---|---|
| MM-T1 | `uncertain` 单向闩锁（High） | **confirmed + qualified** | 现码穷举见 §4.4；只限主链 owner 的授权，不等于整个 App 停止；换 session 不退旧 UNKNOWN |
| MM-T2 | 约 1183 次操作后全局永久冻结（High） | **有限容量 confirmed；1183/永久/全局 refuted** | 预算式见 §4.4(b)(c)(d)；上一轮 ROOT 事实核 F3 亦持同一口径；"b=758"是假设，无完整 request 见证，未实测 |
| MM-T3 | 未 ACK 双 16 槽 + `fullIntents` 失败占位（High） | **confirmed + qualified** | 四个独立 16 见 §4.2/§4.3/§4.4；已入线未知与未入线已知失败须分，后者可按原参数重试 |
| MM-T4 | 跨引擎会话创建回执不可对账（High） | **confirmed + qualified** | `project_lifecycle.py:82-102` 的 `origin_value` 强制恰 3 字段 `{hostClientId, engineSessionId, permission}`（各 36 字符 UUID 形），我现码复核一致；不得删 origin、不得以 UUID+body 充当物理证明 |
| MM-T5 | Windows 6 例 + macOS 15 零运行证据（Medium） | **confirmed，平台 HOLD** | bda 修了接线，**未产生任何平台证据**；见 §0.2-2 |
| MM-T6 | Windows 迁移备份目录项未持久化（Medium） | **"本次引入" refuted；缺口 qualified 成立** | §4.5：501 已有 nt 跳目录 fsync；不得写成已证掉电回归，也不得据此降级不变量 |
| MM-T7 | 无用户级备份/恢复；损坏库拒启（Medium） | **confirmed / FR 与恢复 HOLD** | 迁移备份 ≠ 用户备份；FR-002/203/300 各自未完 |
| MM-T8 | `prepare-fr003-bundle.py` 残留锁（Medium） | **confirmed 工程可用性风险** | `O_CREAT|O_EXCL` 锁 + `finally` 中 `lstat`/dev-ino 比对后 unlink；不得按年龄自动删锁 |
| MM-T9 | 38 处 import 指向不存在的模块（Medium） | **缺失成立；38 与"全部被吞"refuted** | 上一轮独审实测为 **36 条 import 语句 / 8 个不同缺失目标**（semantic 20 + semantic_execution 11 + semantic_turtle 5），且部分在 `try` 外；当前 design-only 不假启 |
| MM-T10 | 每翻一页全量物化（Medium） | **confirmed + qualified / D2 HOLD** | 通用 `result.page` 与 typed rows 完整物化是**两条不同路径**，均非 SQL 侧游标；当前 10000 行 / 8 MiB 上限使"500 万行"不是已证反例；未测不量化耗时 |

### 5.2 MM 其余 52 项（O01–O52）

我不逐条复述原文，只记我的判定与边界（严重度沿用原文，未擅自新增）：
- **O01–O05（发布/法务/跨平台/损坏库/LLM）**：全部 confirmed/HOLD。其中 O01 的数字需更正：090 的 `nonEngineStandaloneSignatureFailures` 是 **9**，不是 17；17 是 native 成员数。二者不可混。O02 机械 32 件闭包 ≠ wholeAPP legal/_distutils。
- **O06–O11（FR 缺口/redo/影响面板/ABA/墓碑/本体整表）**：confirmed 或 qualified；重复撤销报 `INVALID_STATE` 是**保护行为，不得改无条件 no-op**；客户端 `entityDeletionImpact` 非权威 `undo-impact`，显示混淆风险登记，未证其替代完整 Diff 确认。
- **O12–O17（records/intents/seen/并发/退役/ACK）**：confirmed 或 qualified，口径与 §4.2–4.4 一致（records 初始 1+15 继任；`#intents` 只增不删；`Coordinator.seen` 65536 为 session 内防重放硬界；主链并发直接拒绝是设计事实；退役抛错保原责任；ACK 失败仍返 payload）。
- **O18–O25（悬挂 import/Turtle/内存护栏/DDL/workspace/create_project/原值/墓碑）**：悬挂 import 数量按 36/8 更正；`semantic_scopes.py` 的 text **自行构造**，旧"两路 Turtle 无界绕过"是误判，`semantic_execution._term` 先过 1 MiB `_text` 门；Darwin 内存护栏为咨询式采样（`native_hard_limit=false`），退出码 75 与真实 `ENGINE_EXITED` 区分度不足（未证本轮 fault 由该 guard 导致）；内部异常消息含原值是**潜在**面，`SafeError` 跨边界只投影 code/受限 params。
- **O26–O34（UX/a11y/i18n/文档/e2e 覆盖腿）**：`finally` 无条件清 busy 是维护风险（未证可达重叠写）；`queryControllers` Map 不清理是保留风险（持 pending/Job，不可 LRU）；查询历史只有"下一页"；渲染端无 `AbortController`（围栏≠物理取消）；i18n 全缺，`messageKey` 确由固定中文模板渲染（旧"NaN 毫秒/不渲染"未被证据支持）；无 CHANGELOG/Terms/Privacy，`appId` 仍个人命名空间；首次丢回复 e2e 只覆盖 IPC 业务回复层。
- **O35–O46（版本字面/构建 nonce/契约体积/长文件/死代码/Dependabot/临时目录/Git 历史/平台/锁/回滚/分支保护）**：`"@ontolearn/contracts": "*"` 违反仓内精确版本字面偏好（但 npm workspace + lock 锁的是仓内包，非已证外部漂移）；构建 nonce 不可复现已在 §2.5 字节级确认；`packages/contracts/v2` 约 2.3 MB 随包分发，**其是否含业务数据本轮仍未逐字审 → 记为无法确认**；`engine.ts` 2623 行 / `job_store.py` 2589 行超 2000 维护阈值（`semantic.py` 1627、`workspace-controller.ts` 1531 **未超**，历史误报已更正）；Dependabot **不覆盖 Python**、本轮无网络 ⇒ advisory 状态**无法确认**；e2e 的 `mkdtemp` profile 从不删除；`test_approved_old_reader_rejects_actual3` 依赖 Git 历史可达性（CI 已用 `fetch-depth: 0`）；远端分支保护**未核（UNKNOWN）**。
- **O47（0/17 与"全盘不可承接"）**：**0/17 confirmed；"任何一行变更全部旧包/runtime 不可承接" refuted**。按影响输入逐项桥接——这正是本轮 bda 的实际处理方式（§2.4），既有"一律重跑"与"一律沿用"两个极端都不成立。
- **O48–O52（远端未推/CI29 根因/19 MB 日志/文档纪律/license 闭集）**：远端状态是**固定接收记录时事实**，本轮未联网刷新，不冒最新远端实时查询；CI29 其余 F 与 20 分钟总因**不得**一概归因 nodeid；**8 短 ID / 9 超限 nodeid** 的口径保留；O52（仓内打包链在强制 license 闭集不满足时仍 exit 0、`electron-builder.yml:15-18` 把强制输入绑死在 builder 自己的 `node_modules`）**成立且值得作为未来工程改进采纳**，但会改构建/验收输入，须另立候选，机械 32 件闭集 ≠ wholeAPP legal。

### 5.3 Z Top10 逐条（我的判定）

| ID | 原标题（等级） | 我的独立判定 |
|---|---|---|
| Z-T1 | 远端链完全未走（High） | **confirmed 流程门**：bda 未 push、PR6 仍 `@8be6f08a`、CI29 三终态未闭；本地全 check 与 090 有限实测不能抵销 |
| Z-T2 | 6 个 native 用例 `bundle` fixture 不可见（High，§5 标 P2） | **confirmed 结构成立；运行后果为推断**（Z 自述已披露）。**本轮 bda 已按最小边界修复并被我独立复核**（§2.1–2.2）：真实注册原 fixture、保留六例/参数/skip/断言、无 conftest/mock/skip 扩张。**该测试基建缺陷在 bda 上关闭**；但它**不产生任何 Windows 平台资格**，且使 6 例首次真正执行（§0.2-2） |
| Z-T3 | Windows 真实平台完全 UNVERIFIED（High） | **confirmed，平台 HOLD 保留** |
| Z-T4 | M1 + records16（Medium-High） | **confirmed + qualified**（§4.4） |
| Z-T5 | M3 十六义务容量（Medium-High） | **confirmed 保责任；"永久/必然"须限定**（§4.2–4.4） |
| Z-T6 | 故障注入下 retire/consume 失败无产品恢复入口（Medium） | **confirmed 潜伏限制**；自然触发在现不变量下未证成，不得写成当前 E2E 失败原因 |
| Z-T7 | M2 跨会话回执不可对账（Medium） | **confirmed**，并**直接反证**"重启恢复所有限制"的说法 |
| Z-T8 | 无备份恢复 + FR 缺口（Medium） | **confirmed + qualified，已有 HOLD** |
| Z-T9 | 签名/legal（Medium） | **confirmed**；9 与 17 的口径已更正（§5.2 O01） |
| Z-T10 | 平台/规模/卫生（Medium） | **confirmed + qualified**：mac15 未验；通用 page 与 typed rows 两条路径不同；10000 行/8 MiB 仍界；`invalidation.py` 的 `read_text()` 无显式 encoding，但原 1745 B JSON 为纯 ASCII，**不是活跃缺陷** |

### 5.4 Z §10 的 H1–H15 与清单分类（我的处置要点）

H1 历史/过程、H2 隐私/安全制度、H3 UX/a11y/i18n、H4 依赖/发布/支持、H5 模型前置、H6 分页/undo 规模、H7 Turtle 局部门、H8 内存护栏/首帧、H9 exit75 分类、H10 悬挂 profile 模块、H11 活体 hang/leaseBusy、H12 busy-finally、H13 Abort/导航、H14 历史/controllers、H15 原值异常面 —— **全部承接未闭**，我的修正与上一轮独审一致：H7 的"两路无界绕过"是误判；H10 是 8 个缺失目标而非 8 条语句；H12 未证可达竞态；H11 未演练，不新造本轮必须更多故障运行门。
Z §11 的**分类**式承接我逐簇核对，其中两处必须分清：
- Z §11.1 把"改号越权"列入"整类不适用"，而 §11.2 又称已核 —— **以 §11.2 为准**：本地 `projectId`/owner/session/frame/issuer 防线真实存在且有负例，不能因无 SaaS 用户 URL 而豁免。
- Z §11.1 把"CSV 2009 导入"整体不适用 —— **不成立**：**FR-300 CSV/XLSX 明确未实现**，属欠项而非不适用。
- 其余簇：云/无网络**不豁免**本地数据恢复、隐私、规模与正式分发义务；零日志是取舍，不等于这些义务已满足。

### 5.5 统一处置 §9 的十项更正，逐条我的判定

1. **Z"累计产品仅 W 三 Python + 两测试"** → **refuted**：base→212 还改了 desktop engine/task/IPC/query、Coordinator/JobStore/storage/事务/metadata/worker 等主链。正确口径：**501→212 的 W 增量** = 3 生产叶 + 13 测试叶；fde→212 另有 24 文档 + W16 + 501 两测试。**bda 相对 212 的增量 = 1 测试叶 1 行**（本轮实测）。
2. **"所有限制仅容量且重启可恢复"** → **不成立**：M2 跨 session 原回执仍冲突、UNKNOWN/未 ACK 责任不因 session 重置退账、用户数据恢复/平台/签名/legal/FR 缺口均非容量。
3. **Windows/hash/close** → hash **只约束内容**，不替代物理路径/句柄资格；成员 close 失败拒，**根链 close 失败在已有 primary 异常时保首因**，不得说"所有 secondary 均独立上报"；采样不证期间一直无 reparse。
4. **计数** → import 为 **36 语句 / 8 目标**；签名 9 / 17 / 3 / 1 分层，不混。
5. **getter 按模式** → 三 fault 有 appPath/resourcesPath，native 无该字段，full18 helper 未直供，execPath 未供仍 UNKNOWN；物理 expected **不回填**观测。
6. **机制/清单** → 243 有序行 ≠ page 400 实测；计费 ≠ RSS；无网络 ≠ 传输加密已实现；产品零日志 ≠ 事实值从未持久化。
7. **输入与安全文档归属** → **W16 没有新增 ZIP**（T09 ZIP 在更早 fde 增量）；`SECURITY.md` 已有私有披露渠道，旧"从无"纠正；个人 `appId` 不从代码证明产权或 bus factor。
8. **制造（089→090）** → 089 是**真实制造输入遗漏**（wrapper 0 / postflight 1，缺两件 Electron license），**永久保留为 FAIL**；090 补供同版本本地 dist/path 只纠正冻结 090，**不回写 089**；机械 32 闭集 ≠ wholeAPP legal。
9. **桥接** → MM"任何修复全部包/runtime 不可承接"过强；按影响输入 + ROOT 票逐项桥接，旧 PASS 仍标旧身份；**不因文档/测试改动重跑全部，也不让旧 PASS 冒新源码**。本轮 bda 正是这条口径的实例（§2.4）。
10. **不采纳的扩面** → 不删 origin、不把 UUID/body 当物理 proof、不建持久意图账本、不 FIFO/按年龄遗忘、不代 ACK/无偿退款、不扩预算或改错误目录求绿；不新增 operationId 回执接口、ACK 重试协议、目录 FlushFileBuffers、SQL keyset、guard 或模型网关来迎合本报告。

### 5.6 本轮唯一发生变化的旧意见

| 旧意见 | 212 时状态 | bda 时状态（我的判定） |
|---|---|---|
| Z-T2 / Z §5：6 个 native 用例缺 `bundle` fixture（P2 / Top2 High） | 结构缺陷成立，Windows 后果为推断 | **结构缺陷已修复并被我独立复核**（§2.1–2.2）；**平台后果仍未验**；**新增**：修后这 6 例将在 Windows CI 上首次真正执行，结局未知（§0.2-2） |
| MM-O47（0/17 与承接口径） | 0/17 confirmed；"全盘禁止承接"refuted | 不变；本轮以"影响输入为空 + ROOT 票"实际执行了该口径 |
| 其余全部 MM-T1..T10 / O01..O52 / Z-T1..T10 / H1..H15 / 160 项 | 见 §5.1–5.5 | **状态未变**；bda 只改了一个测试文件，未触及任何生产路径或机制 |

### 5.7 更早历史（085/087/088/fde/089 等八份原件）

ROOT 已明确本轮不重复"每候选全读八件"门；**本方本轮未全文实读这八份旧报告**，按争议回溯原件，不宣称读过。已核到的历史事实与原件（089 三件、090 实际链、CI29 原件、APP 实物）均与上一轮一致：
- 085 MM BLOCK / Z 内部 PASS；087 pair001 MM BLOCK / Z 内部 PASS；087 pair002 双方内部 PASS / formal HOLD；088 双方内部演示 PASS / formal HOLD —— 原样保留。
- 086 首入口 9 PASS / 1 T02 FAIL / 2 SKIP / 6 未跑；087 guard 首败 0 产品用例；088 renderer FAIL/FAIL/PASS（第二次人工输入可信确认但具体键/因果未知）；旧 native 第一个 0 来源 UNKNOWN —— 原样保留。
- 089 首次制造失败（缺 2 件 Electron license、postflight exit 1，engine/package 命令自然 0）**永久 FAIL**；090 的成功不回写。
- CI29（run40071234771 / head `8be6f08a`）：Quality FAILED / macOS FAILED / Windows CANCELLED（20 m 门）；Windows 官方 348 DOM 行进度 100%@06:56:47；最早 draft 四组超长 `PYTEST_CURRENT_TEST` 原栈在案；**其余 F 与 20 分钟总因不全知**，不得泛归 nodeid/locale/fsync/resource。
- 1790 是**字节数（B）**，不是秒/预算；300 s 原预算与 JSON 直接 `timeout:false` 与 helper 由自然 0 推断的 timeout:false 分开。

---

## 6. 最值得修复的 Top 10（按严重度；本产品形态：本地优先、单用户、本地数据、无资金流、无服务端）

> 每项给出位置 / 触发时序 / 影响 / 严重度 / 证据类型 / 最小建议。**不为凑数虚列**：与上一轮重复但仍然成立的项保留原严重度，不因"已在本轮复核过"而降级；本轮新增项按其实际影响排序。

**1.【High｜平台｜bda 新增后果】6 个 Windows native 用例将在 Windows CI 上首次真正执行，结局未知**
- 位置：`packages/engine/tests/test_windows_example_resource.py:156-262`；`.github/workflows/ci.yml:112-129`（`windows-latest`，`timeout-minutes: 20`，先跑 `npm run engine:check`）。
- 触发：修前 Windows 上 setup ERROR（快速响亮）；修后这 6 例**第一次**进入 `WindowsResourceRoot` / `NtCreateFile` / junction / 句柄关闭路径，而这条路径**从未在任何机器上运行过**。
- 影响：runner 临时盘文件系统、`cmd mklink /J` 可用性、持句柄下 rename/share 语义任一不符即失败；若出现挂起，job 会在 **20 分钟**上限被取消（与 CI29 的 Windows 取消同形），且不会留下可定位的首败栈。
- 严重度：**High**（发布门，且是本候选唯一新增的未验证执行面）。
- 证据：**静态观察**（现码 + CI 配置）；**零运行**。
- 最小建议：把下一次真实 Windows 运行当作**首次执行**对待 —— 单独一次、保留首败完整栈、不改预算不放宽断言、不用新增 skip 换绿。

**2.【High｜可用性｜会话级】M1 `uncertain` 单向闩锁，无复位路径**
- 位置：`engine.ts:822 / 2098 / 2501 / 2566`（全部 `= true`），读点 `:714 / :957`。
- 触发：任一主链请求超时（默认 5000 ms）或写失败 → 该 owner record 被永久污染 → 该会话内此后全部 `project:*` / `query:*` 恒为 `PERMISSION_DENIED`。
- 影响：一次慢请求即让整条主链在该会话内不可用，进程内无自愈；**无数据损坏**（`operation_claims` 兜底），但用户侧无指引。
- 严重度：High（会话级中断）。
- 证据：静态（现码赋值穷举）。运行后果为推断，未注入复现。
- 最小建议：**不得**清 `uncertain`、**不得**自动重放未确认写入；应给该拒绝**专属、可行动**的错误码与文案（"本会话状态不确定，请重启引擎会话"）。

**3.【High｜容量】四个独立 16 槽责任账本不回收，且拒绝与"参数非法"不可区分**
- 位置：`engine.ts:771` / `engine.ts:1167` / `desktop-ipc.ts:164` / `project-mainline-service.ts:735`。
- 触发：(a) 渲染端崩溃/reload 发生在主进程回复与 preload ACK 之间 → IPC 与 engine 各占 1 槽且永不释放（`desktop-ipc.ts:142` 是唯一 delete 点，且在 consume 成功之后）；(b) 已入线写失败 → `intent.unknown` 占 `#fullIntents`，而唯一 delete（`service:656`）在退役回调内，不执行。
- 影响：耗尽后新提交被永久拒；**四账本独立，不得相加为 8**；渲染端 ACK 失败后仍收到业务 payload（`preload:40-46`）。
- 严重度：High。
- 证据：静态（现码四个上限点与唯一删除点）。
- 最小建议：**保留义务语义**（不 FIFO、不代 ACK、不无偿退款）；仅做两件小事 —— 容量拒绝用**专属错误码**与"重启应用"的可行动文案；设计一条"同一 deliveryId 有界私有 ACK 重试"用例（先设计、另立候选）。

**4.【High｜数据对账】跨引擎会话后创建/内置示例的原回执永久不可对账**
- 位置：`project_lifecycle.py:82-102`（`origin_value` 强制恰 3 字段且各为 36 字符 UUID 形）、`mainline.py` 的 `operation_claims` 命中分支（`IDENTITY_CONFLICT`）、`engine.ts` 每次握手新发 `clientId: randomUUID()`。
- 触发：引擎在"已持久化提交之后、回执抵达渲染端之前"死亡 → 用户以同一 `operationId` 重试 → 新会话 origin 与原记录不成立 → 冲突。
- 影响：**不会**产生重复项目/草稿（守卫有效），但原回执永久不可取回，UI 永久停留"创建结果尚未确认"。
- 严重度：High（对账不可达 + 用户可见悬空）。
- 证据：静态。
- 最小建议：保留 origin 与全部拒绝语义；至多补一条**只读**的"按 operationId 查询原回执"内部路径（不新增写路径、不改 origin 绑定、不建持久意图账本）。

**5.【High｜发布流程】远端链一步未走，0/17 不能预结**
- 位置：`release-scope-2026-10-25.csv`（59 行；17 行发布目标 2026-10-25，状态列全为"未取得完整产品正式完成证据"，正式证据列全空）；PR6 仍 open / head `8be6f08a` / merged=false；CI29 三终态未闭。
- 影响：本地 check 全绿与 090 有限实测**不抵销**远端；bda 尚未 push。
- 严重度：High（流程阻断）。
- 证据：既有接收记录 + 我对 scope CSV 的直接实读；本轮未联网刷新远端，不冒最新实时状态。
- 最小建议：顺序固定 —— fresh 双审 → ROOT 全文接收 → 正常 push PR6 → 真实新 CI 全绿 → squash develop → 远端复核 → ROOT 结算。

**6.【Medium-High｜容量｜无专属错误码】主链紧凑身份无释放路径，容量耗尽时报不可区分的 `INVALID_STATE`**
- 位置：`service.ts:621-636`（`retainHolding`，注释"never FIFO-forgotten"）、`engine.ts:853-862`（`maximum` 与 `maximum < 1`）。
- 触发：每个**不同** operationId 的主链提交都在 intent 自身 holding 上计一笔紧凑身份费用，该笔**永不释放**（退役回调只释放 `payloadEntry`）。
- 影响：该实例内预算耗尽 → 安全拒绝，但错误码与"请求非法"不可区分，用户与支持无法判断原因。
- 严重度：Medium-High。
- 证据：静态。**任何具体次数都未经实测**：按 `mainlineHoldingMeasure` 的 `bytes=32b+4096` / `objects=b+128` 与 `maximum` 式（bytes 轴、objects 轴、263168 常驻 scratch 三轴取 min），上一轮的"1183 次"是**未含 scratch 的假设商**，不是阈值，也不是实测；本轮**不接受**该数字为事实。
- 最小建议：① 容量类拒绝给**专属错误码**与可行动文案；② 把"紧凑身份永不释放、由全局预算兜底"写进 ADR，明确寿命上限与恢复路径；③ **先测量再谈提高上限**。

**7.【Medium｜数据韧性】Windows 迁移备份的目录项未持久化（既有平台差异，非本次引入）**
- 位置：`format3.py:176-186`。
- 触发：Windows 上 `target.open("r+b") + os.fsync` 只 flush **文件内容**；无 POSIX 等价的父目录 fsync（该条件 501 已有）。
- 影响："备份先持久、再发布迁移事务"这一意图在 Windows 上**只对文件内容成立**；迁移与掉电的窄时序下，备份目录项是否落盘未被证明。
- 严重度：Medium。
- 证据：静态；**未在 Windows 复现，也不声称已复现**；Windows 侧 durability 仍 UNVERIFIED。
- 最小建议：要么取得实际 NTFS 持久化契约与实测再实现目录 flush；要么在 Windows 上把不变量显式改写为"文件内容已持久、目录项未持久"并写入 ADR —— **不要让注释继续声称一个 Windows 上不成立的强度**。

**8.【Medium｜功能完整性】无用户级备份/恢复入口；FR-002 / FR-203 / FR-300 三条 P0 未实现**
- 位置：`storage.py` 的损坏库明确拒启（"explicit repair required"）、仅 v2→3 迁移备份（保留作证据）；`format3.py:158-187` 的迁移备份强制可验。
- 影响：磁盘故障/误删 → 应用拒启，用户数据无法自救；当前页 CSV、内置示例与 T09 ZIP **都不替代**上述三条 FR。
- 严重度：Medium（数据韧性；正式范围 HOLD）。
- 证据：静态 + 历史三轮一致。
- 最小建议：补项目级导出/导入入口，并**实际做一次恢复演练**（没恢复过的备份只是希望）。

**9.【Medium｜工程韧性｜建议采纳】仓内打包链在强制 license 闭集不满足时仍 exit 0，且强制输入绑死在 builder 自己的 `node_modules`**
- 位置：`apps/desktop/electron-builder.yml:15-18`（两条 `from: ../../node_modules/electron/dist/…`）；根 `package:dir` 链无该 32 件闭集断言。
- 触发：CLI `--config.electronDist` 可从别处提供 Electron 基础应用，而 builder 的 license 输入仍解析自自身 `node_modules` → **两者不同源时 builder 静默少拷两个强制文件而不报错**。
- 影响：同一命令在别的机器/别的 Electron 来源下可能静默产出不合规包，只有仓外 postflight 才能发现（089 即如此）。
- 严重度：Medium（工程韧性，不影响当前产品行为）。
- 证据：静态（配置）+ 既有运行证据（089 wrapper 0 / postflight 1、缺 2 件）。**本轮未实施**。
- 最小建议：把"实际 electronDist 与 license 输入同源 + 产物闭集逐叶针校验"纳回仓内 `package:dir`；注意这会改构建/验收输入，**须另立候选**，且机械 32 件断言**不替代** wholeAPP legal/_distutils。

**10.【Medium｜规模/性能｜D2】每翻一页都在 Python 内存中重新物化整个结果载荷**
- 位置：`job_store.py` 通用 `result.page`（全量 payload + available 扫描）；typed rows 走 `semantic_result` 的 rows page（完整 load + 摘要校验，**不同路径**）；`compensation.py` 的撤销对账对每个后续 commit 重建历史。
- 影响：结果集越大每页成本越高；当前游标**语义**正确（keyset + 快照绑定 + 页字节/页项上限 + 60 s TTL），生产另有 10000 行 / 8 MiB 上限 —— 故"500 万行超时"**不是已证反例**，也不证明 page 400。
- 严重度：Medium（D2 未量化）。
- 证据：静态；未做负载测量。
- 最小建议：在 D2 内先量化（阶梯数据量下的翻页耗时 + 执行计划），再决定是否改 SQL 侧游标；**不得**以性能名义删安全校验或改页序语义。

### 6.1 本轮新增但不入 Top 10 的发现

- **【证据更正｜Low】** red 的 exit 1 来自探针自设的 `session.exitstatus = 1`，pytest 自身在 `--collect-only` 下无 ERROR 输出（§0.2-1）。事实不受影响，但 ROOT 受理票与统一处置 §10 的"red 自然 exit 1"应按此更正，且**不得据此宣称已复现 Windows 的 6 ERROR**。
- **【构建｜Low】** main bundle 每次构建字节不同，根因是 `electron.vite.config.ts:7` 顶层 `randomBytes(18)` 对所有构建生效（§2.5 已字节级确认）。影响：产物不可按字节复现，任何"新 build 与旧包完全相同"的断言都不成立。

---

## 7. 其余阻断与缺口（保留在案，不因 Top 10 而丢弃）

1. **正式发布义务**：未签名、未公证、无安装器与升级路径（`electron-builder.yml` `mac.identity: null`、三平台 `target: dir`）；wholeAPP legal 与 `_distutils` 来源闭包未接受；机械 32 件 license 闭集不等于法务闭包。
2. **跨平台与设备**：Windows 真机打包与运行、目标 macOS 15 arm64、参考/五龄设备、无开发环境离线启动 —— 全部**未发生**。
3. **数据韧性**：损坏 SQLite 物理保护未授权/未闭；无用户备份/恢复演练；FR-002 / FR-203 / FR-300 未实现；Windows 备份目录项 durability 未验。
4. **容量与可用性（同族）**：`#mainlineRecords` 只增不删（初始 1 + 15 继任 = 16，第 17 拒）；`#intents` 只增不删；`Coordinator.seen` session 内 65536 硬界；主链并发直接拒绝（设计事实）；退役回调抛错时引擎与 IPC 各泄漏 1 槽且 preload 单次 ACK 失败被 `catch {}` 吞（**保责任、无恢复通道**，自然触发未证）。
5. **引擎内部质量**：8 个缺失 profile 目标（36 条 import、部分在 `try` 外）—— 当前 design-only 不假启，但接线前必须修闭包；Darwin 内存护栏仅咨询式、退出码 75 与真实 `ENGINE_EXITED` 区分度不足；`CREATE TABLE IF NOT EXISTS definition_retirements` 在写事务内取 schema 锁；`project/workspace.py` 仅被测试引用；内部 `create_project` 绕过版本化但**当前协议不可达**；内部异常消息内嵌原值属**潜在**面（跨边界只投影 code/受限 params）。
6. **渲染层 UX / a11y / i18n**：无焦点管理与区域播报；`<a href aria-disabled>` 仍可聚焦且仍带 `onClick`；查询历史只有"下一页"；`queryControllers` Map 不清理；渲染端无 `AbortController`；i18n 完全缺失（`index.html lang="zh-CN"`，`toLocale/Intl.` 0 处）；全屏空/加载/错误态、表单保留与返回语义**未逐页核验**。
7. **工程卫生**：`apps/desktop/package.json` 的 `"@ontolearn/contracts": "*"` 违反仓内精确版本字面偏好；`packages/contracts/v2` 约 2.3 MB 随包分发（**其内容是否含业务数据本轮仍未逐字审 → 无法确认**）；`engine.ts` 2623 行 / `job_store.py` 2589 行超 2000 维护阈值；3 个零消费者导出与未接线的 legacy 分支；Dependabot 不覆盖 Python；e2e 的 `mkdtemp` profile 从不删除；`prepare-fr003-bundle.py` 崩溃残留锁与第三方删锁导致 cleanup 失败；`npm test`/`npm run build` 新增 `uv` 依赖钩子。
8. **文档与组织**：无 CHANGELOG / Terms / Privacy；`appId: io.github.nomorejoke.ontolearnstudio` 仍为个人命名空间；远端分支保护规则**未核（UNKNOWN）**；第三方 advisory 状态**未核（本轮无网络）**。
9. **流程与积压**：C4–C6 配对失败与 D8 人工裁决、47 阶段指定双审积压、086/087 guard 首败、CI29 三终态、089 首败、旧 088 renderer FAIL/FAIL/PASS 与 native 首 0 UNKNOWN —— 全部**原样保留，不回写**。
10. **模型前置**：真实 LLM 与 I06 网关未接入；S3 前置（密钥只在主进程、prompt injection 防护、per-customer spend cap、evals、供应商降级与弃用迁移）整套仍缺；**本地优先与引擎不持密钥的架构边界不变**。

---

## 8. 原用户 160 项清单的适用性与逐项判定

> 记号：✅ 满足 ｜ ⚠️ 部分满足 ｜ ❌ 未满足 ｜ ➖ 当前形态不适用（附类别理由）｜ ❓ 无法确认（未实际核到）
> 产品形态（本轮现码直核）：本地优先、单用户、离线、无服务端、无 HTTP 端口（CSP `connect-src 'none'`）、无账号/登录、无计费、S3 前无模型接入。**SaaS/多租户/支付/云运维类不适用，且不为满足清单扩建功能**；**但不适用 ≠ 本地等价义务已免**。

### 8.1 整类不适用（按类别说明依据）

| 类别 | 覆盖条目 | 依据 |
|---|---|---|
| 账号/身份 | 2、3、4、6、7、8、11、12、13、14（部分） | 无服务器/无登录/无多用户多租户；IPC 以 sender/mainFrame/可信文档三重校验替代（`index.ts:317-323`）。**但"改号越权"（10）在本地形态下适用且已核** |
| 支付/计费 | 27、28、98–105 | 无任何货币、订阅、发票、退款、计量 |
| 邮件 | 74、75、126 | 不发邮件 |
| 对外 API / 集成 | 106、107、109、112、113 | 无对外 API/webhook/OAuth；内部 stdio 协议是设计契约（schema + registry 双端执行），**不因"非公开"而豁免** |
| 云基础设施 | 18、64、66、67、68、72、79、82、83、89 | 无云、无端口、无自有名域证书、无状态页。**本地等价物仍需**：Git 回退 ≠ 用户一键回滚、配置可重复性、正式分发 |
| 观测/值班 | 80、81、84、85、86、87、88 | 无在线服务；零日志是隐私取舍，**不等于**错误聚类、性能观测、runbook、支持能力已满足 |
| 合规套件 | 52、53、54、56 | 无 PHI/卡号/第三方 PII 供应商接入。**但 48、49、50、51、55、57、58、59 仍适用/待办**，不能一律免到"首个企业客户"之后 |
| 流量/规模（云侧） | 72、76（部分）、93 | 无连接池/无 cron/无多服务；**本地负载、磁盘占用、D2 规模口径仍适用或未核** |

### 8.2 适用且本轮已核（有实现与证据）

10（改号越权：`projectId`/owner/session/frame/issuer 防线）、22（软删除/retirement 与不可变历史）、23（双端校验）、24（epoch 毫秒 + 单调钟）、25（标识符白名单 + 参数化 SQL）、26 部分（emoji/重音/代理对全链正确；**RTL 排版无法确认**）、30/31（`operation_claims` + `commits(project,operation)` + `rounds.operation` 三层幂等）、32 机制（keyset 游标 + `CURSOR_MISMATCH`/`CURSOR_EXPIRED` + 页字节/页项上限）、38（精确 pin + 双锁文件 + `verify:sources`）、40（严格 schema + `.strict()` + 规范化 JSON）、41 部分（SQLi ✅ / XSS ✅ / CSRF·CORS 不适用）、43（无 HTTP 面；等价物是 CSP `connect-src 'none'`）、44（CSP 唯一源即安全头等价物）、46（引擎无凭据、Agent 不得自确认）、62（CI 跑完整 check + `verify-i04-package.py`；**但本候选未推送、未在远端跑过**）、69（常驻 coordinator + 有界 Job 队列）、70（三次尝试 + 指数退避 + `attemptToken`）、73（`invalidation-v2.json` 唯一 `staleReason`；仅改模型配置不使领域结果过期；历史/失败/取消不计过期）、90/91/94/95（1694 TS + 3495 Py 断言具体预期集合；真实 SQLite/RDFLib/CLI/Electron 路径）、108（协议版本协商 + `VERSION_INCOMPATIBLE` + 契约双端执行）、121（完整 Diff → 人工确认；`agentEligible=false`）、128（引擎侧 undo-of-undo 可达 + 影响文档；**UI 只暴露"撤销当前"**）、134（worktree + feature 分支 + 单写入者 + base SHA + PR 合回）、139（ADR 1–2 屏含理由与未决项）、150/155/156（逐轮处置与证据链在档；迁移有独占租约 + `integrity_check` + 源哈希复查 + 相位原子性）、157（registry 的 capability/exposure/`requiresConfirmation` 门）、160（ADR + `docs/reviews/**` 记录"为什么"）。

### 8.3 适用但未满足或无法确认（如实登记）

20（恢复从未演练 ❌）、34（FR-300 CSV/XLSX 未实现 ❌）、48/49/50/51（渗透/问卷/披露/失窃预案 ❌）、55（"谁查看过" ❌）、58（数据驻留声明 ❌）、63（无产品级一键回滚 ❌）、77（无用量计量与成本告警 ❌）、78（无 DR 计划 ❌）、81（无错误聚合 ❌）、84（无运营看板 ❌）、86（无 on-call ❌）、93（未做负载测试 ❌）、96（未在参考/五龄设备测 ❌）、114（prompt injection 防护未实现 ❌）、116（无 per-customer spend cap ❌）、118（无模型供应商降级 ❌）、119（无模型弃用迁移 ❌）、130（i18n 全缺 ❌）、138（两个文件未拆 ❌）、144（无 CHANGELOG ❌）、145（无 Terms/Privacy ❌）、152（无 on-call ❌）、154（无审计材料 ❌）、158（未完成跨平台正式交付 ❌）；
以及 ❓：17（索引与执行计划未测，D2）、19（无夜间备份）、21（无 PITR）、37（无密钥轮换体系）、59（无季度访问复核签核）、87（runbook 覆盖度未核）、125（表单保留未逐页核）、131（返回按钮语义未逐页核）、136/153（框架补丁与依赖安全状态未核，无网络）、140（README 一小时上手未实测）、147（bus factor 属组织事实，源码无法认证）。

### 8.4 逐项计数（我按本轮口径重数，合计 160）

| 判定 | 条目数 |
|---|---|
| ✅ 满足 | 29 |
| ⚠️ 部分满足 | 49 |
| ❌ 未满足 | 28 |
| ➖ 当前形态不适用 | 42 |
| ❓ 无法确认 | 12 |
| **合计** | **160** |

> 与上一轮 MM 的计数一致（29/49/28/42/12）。**该一致来自同一事实基础，不是对上一轮结论的背书**；本轮对每条的限制条件见 §8.2–8.3。其中 **#32（page 400）仍只能标"机制已核、page 400 未验"**，**#90（单测作者知情）本轮实为 profile 保留项的引用错误，原引用应纠正**。

### 8.5 13 条人员/组织条目

无法从仓库证据确认人员配置与轮值 —— 这 13 条**是组织事实，不由源码认证**。可核对标：指定双审 + 独立复核 + CI 门禁 + 总控记录**本轮实际运作**（本报告即其中一环）；单一创始人 + 个人名下仓库构成真实的 bus factor 风险，但**不从代码推断具体人数或产权归属**，也不把 `appId` 个人命名空间写成"公司产权不存在"。

---

## 9. 证据边界与仍未知项（不得洗绿）

1. **本轮未产生任何新的运行证据**：未跑 build/测试/GUI/APP/engine/打包/网络。所有"绿"都是对既有冻结证据的复核或现码静态结论。
2. **Windows 6 个 native 用例：UNVERIFIED**；且 bda 后它们**将首次真正执行**，结局未知（§0.2-2）。修的是接线，不是平台资格。
3. **目标 macOS 15 arm64：UNVERIFIED**；全部运行证据均在 macOS 27.0.1 / Darwin 27.0.0 arm64。
4. **CI29 三终态未闭**：Quality FAILED / macOS FAILED / Windows CANCELLED（20 m 门）；其余 F 与总耗时根因**未取得**；**不得**一概归因 nodeid，也**不得**据此要求重跑全部历史。
5. **远端未绿**：PR6 仍 open / head `8be6f08a` / merged=false；**bda 未 push**；本轮未联网刷新远端，不冒最新实时状态。
6. **有限 PID 采样**不等 all-APP exit 0 或全局 drain；**不由 PID absence 反推 engine 已 reap**。
7. **coordinator 的被故障引擎是真实 SIGKILL**，不是自然 0；**不能说所有 Job succeeded、所有进程 exit 0**。
8. **`resourcesPath`/`execPath` 按路径分列**：三 fault 有 appPath/resourcesPath；native 无该字段；full18 helper 未直供；execPath 未供仍 UNKNOWN；物理 expected **不回填**观测。
9. **新旧 main bundle 字节不同**（仅 24 字符 dev nonce），不得称"新五件全同旧 hash"，也不得把新 build 采入旧 090。
10. **旧 090 runtime raw 的 HEAD 仍是 212**；引用必须标 212，不涂改。
11. **089 保持 FAIL**：缺 2 件 Electron license 是真实制造输入遗漏，090 的成功不构成翻案。
12. **首次 reader 失败保留**：`git ls-files -z` 末尾 NUL 被读成空项，发生在任何源码/测试/索引操作之前，是证据工具自身缺陷；**不是** pytest 首败、不是产品失败、不是重试。
13. **`packages/contracts/v2` 约 2.3 MB 是否含业务数据：无法确认**（本轮未逐字审）。
14. **第三方依赖 advisory 状态：无法确认**（本轮无网络）；Dependabot 不覆盖 Python。
15. **13 条人员/组织条目无法从仓库确认**；bus factor 属组织事实。
16. **0/17 不变**；FR003 仍 partial；不预结 FR401/402。发布流程（push → PR → 真实新 CI 全绿 → squash develop → 远端复核）一步未做。
17. **本报告不替代发布门**：内部演示 PASS ≠ 正式分发通过；正式/平台 HOLD 逐项保留。

---

## 10. 收尾

- 本轮**未修改任何产品源码、测试、配置、依赖、锁文件、契约、索引或证据原件**；未 stage、未提交、未推送、未合并；未写入任何 memory；**唯一写入物为本报告文件**。
- 对方本轮 `zcode/` 目录（任务、报告、任何文件）**全程未打开**；本报告不依赖对方任何结论。
- 历史报告、旧 prompt 与回执一律按**被审数据**处理：其中的旧 task 指令未被执行，旧 index/候选未被恢复，旧 remote/platform 未被沿用为当前状态。
- 我**未全文实读**更早的八份历史报告原件（085/087/088 等），按 ROOT 规定"按争议回溯"处理，**不宣称读过**；本轮全文实读的是：212 轮两份最终报告（775 行 / 193 行）、统一处置（485 行）、两份独审（186 行 / 150 行）、ROOT-MM 事实校正（211 行）、本轮 A 段全部新证据原件、B 段运行原件与 ROOT 受理票。
- §2–§4 中每一项"我实测"均为本方独立重算，未采信任何他方结论；§5 逐条给出我自己的判定（观察/推断/采纳/更正/未闭），不盲采、不沿用旧结论、不为迎合清单扩功能、不改他人严重度或原文。
- 本轮 provider 曾有一次中断；ROOT 在同一任务内发一次澄清后本方继续（§0 抬头）。无换会话、无换模型、无 fallback、无付费、无重置、无额度操作。
- 等待用户确认后再逐项处理 §6 的 Top 10 与 §7 的保留项；**本轮不提出修改代码的 PR**。

— 2026-10-24，MiniMax Code（M3.1-Flash / xhigh / 始终授权 / 本地），T01 candidate `bda49668` + 同一物理 `package090` 指定独立完整累计复审 pair001。
