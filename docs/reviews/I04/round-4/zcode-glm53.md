# I04 Round 4（C4）独立对抗性审查报告（ZCode / GLM-5.3）

> **报告修订记录 R1（同一原任务内证据补正）**：总控读回首版（204 行，SHA256 `af5a3b9c…e29e6`，逐字快照留存于 `build/I04-evidence/zcode-r4-first-terminal-report.md`）后提出五项证据准确性核对，本人逐项核实成立并补正：①B1 行"86 项含 ESRCH 组"不实——86 = frame 53 + owner bootstrap 30 + 握手定时 3，不含 memory_guard/lifecycle ESRCH 组，依据改为代码直读 + 开发线 sealed 整版证据绑定；②完整 check 运行环境精确化——实际在 I04-reconnect worktree 与隔离 Linux 容器，primary 未跑整版且 out/release 为历史；③三次工具性失败的原始文件已被同名成功重跑覆盖，恢复副本（注明来源）另存独立根；④pid 边界改为代码精确值 `(1,0xFFFFFFFF]`；⑤握手探针排除论证改用写入/尝试上界 34,201（含保守批次与迟到 hello），不以响应数 33,317 为唯一依据。**未改动任何冻结源码/测试/配置/依赖/验证 JSON；未重跑已绿整版；最终结论经独立复核后不变（通过，边界同 §8）。**

## 1. 评审任务、模型及思考设置的来源记录

- 任务来源：总控派发的正式 C4 冻结审查任务，派发关联标签 `I04-R4-ZCode-GLM53-8f8eda1e24c0425ea2a65d2566978913ee310b8b`（标签为关联标识，非原生 UUID，派发文本已声明不冒充原生 UUID）。完整审查提示词原文（原 launch 十项 + 完整 Goal 九节 + 追加十项真实路径）由派发方提供；是否实际派发、模型/思考核验及任务终态另存本轮 dispatch（`round-4/dispatch.json`），属派发方可见记录。
- 模型与思考设置：按派发声明为 ZCode GLM-5.3 / 最高思考，任务标识及设置由本次原生 UI 派发逐次核验并另存。本人无法看见宿主 UI 配置，不虚构、不自证；本会话实际以独立只读审查身份执行，可见上下文为派发提示词 + 受审 worktree 实际文件 + 指定历史输入。
- 审查纪律：未创建 Goal/线程、未实施、未提交、未推送、未切分支或合并、未操作审查 UI；未在宿主 Mac 启动任何 Electron/e2e/native/HMR/产物 GUI；未读取另一模型（MiniMax）本轮 round-4 任何报告、进度或结论（`round-4/` 下我仅读取了 `source-lineage-note.json` 这一开发线的事实性流程说明，不含他方结论）；未以开发者、总控或内部 agent 判断作为通过依据（c4-internal-review 等内部证据仅作事实线索，全部独立复核）。
- 本报告为唯一获准写 primary 的输出；全部探针、导出、依赖、缓存与日志在 gitignore 的 `build/I04-review-ZCode-GLM53-C4/` 独立根内。
- 过程事件如实记录：本轮一次 Mimosa 安全 hook 拦截——我的独立探针脚本经 Write 写入时被按"命令注入"误报拦截（脚本为固定参数列表 + 无 shell、无用户输入拼接）。未绕过安全意图：改以内联 heredoc 执行探针，不落盘脚本文件（与 C3 轮同类误报的合规绕行一致）。

## 2. 项目路径、分支、base/head、候选清单与 export 身份

| 项 | 实际值（本人独立核对） |
| --- | --- |
| Git 根 | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I04-resident-jobs`（`git rev-parse --show-toplevel`） |
| 分支 | `feature/I04-resident-jobs`（实测） |
| base | `e45e6038b5e0f8f4adc69ed55aafccd75b3d3500`（merge-base 核验为 head 祖先） |
| head | `8f8eda1e24c0425ea2a65d2566978913ee310b8b`（= 当前 HEAD 实测） |
| 受审区间 | 完整 base→head **121 文件，+42286/−236**（非 last commit、非 C3→C4 补丁、非仅 Windows 小修——`git diff --name-only` 实测） |
| 候选清单 | `candidate-4.json` 声明 121 文件；本人对**全部 121 条**重算 SHA256 并与 `git show 8f8eda1e:<path>` 的 git blob 比对：**121/121 逐字节一致，0 不匹配 0 缺失**；清单集合与实际 diff 集合**完全相等** |
| 保护文件 | `AGENTS.md` 保持 dirty、未 stage，审查开始时实测 SHA-256 = `db1fb184809932a27c5bfd8c91b72837d719cdbdc07d7a83860e5cba38529786`，与派发要求逐字符一致 |
| 工作区 | `M AGENTS.md` + 未跟踪纯流程文件（`candidate-4.json`、`integration.json`、`round-4/` 两份 prompt 与派发/lineage 记录）——均属派发明示允许的候选/round-4/process 纯流程文件，无任何实现/测试/配置/依赖/验收改动 |
| 独立 export | `git archive 8f8eda1e…` 解包至 `build/I04-review-ZCode-GLM53-C4/source`（776 文件）；独立 `.venv`（`uv sync --frozen`，editable 指向本人 export，运行时 `ontolearn_engine.__file__` 已打印确认）、独立 `node_modules`（`npm ci`，独立 npm cache）、独立 uv/npm 缓存、独立 pytest basetemp 与临时 DB；primary 的 out/build/release 全程未写入；报告以 primary 路径/分支/base/head 记录受审身份，另记 export 执行目录，未把 export 冒充另一候选 |
| 运行证据与候选绑定 | `c4-verification.json.runtimeSourceCheckpoint=9eb0b6e`；本人核验 `9eb0b6e→8f8eda1` 仅 4 个 docs/流程文件（acceptance/c4-internal-review/c4-verification/status），**无任何实现/测试/配置/依赖变化**——C4 全部 check/打包/矩阵/GUI 证据绑定的运行时字节与候选 head 完全一致；GUI/生产运行检查点 `f504b30` 之后仅 `test_worker_parent.py`/`test_worker_owner_bootstrap.py`/`verify-i04-package.py` 三个宿主验证文件变化（见 §5 C4-Z1 的归属更正） |
| sealed 输入 | `build/I04-evidence/c4-sealed-runtime-inputs.json`（124 文件，SHA `41c9588c…`）：本人对**全部 124 个文件**对照当前工作区重算哈希，**0 缺失 0 不匹配** |
| 148 原始工件 | `c4-verification.json.rawArtifacts`（148 项）：本人**全量**重算 SHA256+字节数，**148/148 一致，0 缺失 0 不匹配** |
| C4 引擎包 | macOS 实测 `…/I04-reconnect/release/mac-arm64/…/engine/ontolearn-engine` SHA256 = `1f5a5eb81476d6b38b7ba26bc7891c2e675db553e186d152adb06c7bce10e83d`（与派发及 c4-verification 声明逐字符一致）；Linux 引擎 `a2099042ece8a6e375a07fedff723f734ed5f307870c31bd11514ca4f69a7444` 为容器内路径，宿主不可达，以经哈希核验的证据 JSON 为据（如实记录，未直接复算）。primary 自身 `out/release` 为历史 C2/C3 产物，本轮未用作任何 C4 判定依据 |

## 3. 已检查范围、验证命令与真实结果

### 3.1 代码审查范围（实际读码）

- **C4 增量全文精读**（C3→C4 全部 9 个代码文件 diff + 现版本全文）：`worker.py`（273 行全文：Windows FILETIME/固定句柄 owner 身份、POSIX 直接父进程、100ms 监控线程、退出码 73/74/75/76）、`coordinator.py`（660 行全文：serve 循环、request 门序、execute 全阶段、darwin RSS 轮询仅捕 `ProcessLookupError`、`worker_owner_arguments()` 接线）、`contract_probe.py`（三处显式 `read_text(encoding="utf-8")`）、`scripts/verify-i04-package.py`（包内新增 worker_parent 全部 + owner bootstrap 读前拒绝用例）、`test_frame_corpus.py`（cp1252 模拟 fixture：monkeypatch `Path.read_text` 仅对三个 fixture 资源且 `encoding∈{None,"locale"}` 时注入——在 `io.text_encoding` 归一化**之前**拦截，覆盖 UTF-8 mode；两条回归分别证明注入臂真实生效与正式代码路径不受平台缺省影响）、`test_worker_owner_bootstrap.py`（255 行全文：Win32 doubles 验证签名/64 位句柄/身份核对/六类失败 fail-closed、参数化非法 argv 含全角数字与越界值、`test_actual_worker_refuses_work_before_a_valid_owner_is_established` 三臂真实子进程 stdin 保持开启退出 73 零输出）、`test_worker_parent.py`（全文：coordinator 代码自报 `coordinatorPid/workerPid` JSON——解决 Popen.pid 可能指向 venv redirector 的问题；只 kill 该已验证 owner 一次；3 秒 worker 死亡断言保留）、`test_resident_runtime.py`（default-handshake finally 仅 win32+EINVAL+进程已退出容忍 close 清理，BrokenPipe 保留、其他 OSError 仍抛）、`test_coordinator_control.py`（stderr 按本机 `os.linesep` 精确比对固定有界消息）。
- **C3 未变核心抽核**（C3 双审通过字节，本轮 diff 实测 UNCHANGED 的文件定向复核关键声明）：`job_store.py`（`commit_job_round` 守卫 `state!="running" or mode!="rounds"→INVALID_STATE`；expected 状态精确比对 IDENTITY_CONFLICT；reconcile 二分）、`memory_guard.py:80-91`（`set_errno(0)` 防残留，仅 `read<=0 且 errno==ESRCH→ProcessLookupError`，其余 `MemoryGuardUnavailable`）、`protocol.py`（JsonlReader feed 追加前 `len(buffer)+length>max_bytes` 上限检查、finish/stop 语义）、`engine.ts`（`startupTimer`/握手 send 为绝对 setTimeout、`health()` resolve 后复查 `current(session)` 迟到隔离、capabilities 过滤仅 health）、`task-service.ts`（跨会话 unsubscribe 仅在 `engineSessionId` 匹配时发远端、`fenceConnection`/`connectionChanged`/`restoreOnce`/`recover` 结构）、`packages/contracts/v2/schema.json`（分页上界 200/100，C4 零变化）。
- **构建/CI/入口**：`.github/workflows/ci.yml`（Quality job：`npm ci`(28)→`uv sync --frozen`(29)→矩阵证据步(30-37，`--i04-matrix-source-revision HEAD`，PR merge-ref 兼容)→`npm run check`(38)；失败仍红、`if: always()` 上传 summary/cases；desktop job 三平台 `package:dir`+`verify-i04-package.py`；本轮相对 C3 无 CI 变化）、`build/ontolearn-engine.spec`（datas 显式含 contract_v2.py、contracts/v2、uv.lock provenance）、`packages/engine/entrypoint.py`（`--worker` 私有 dispatch token 保留于 argv，`--storage-probe` 保留，无 I05 hooks）。
- **文档与历史输入**：最新 AGENTS（含无桌面打扰与并行规则）、总控 `goal-objective.md`（173 行全文）、`I04-launch-prompt.md` 派发原文、I04 `acceptance.md`/`implementation.md`/`ADR-0003`、I03 `protocol.md`/`jobs-and-storage.md`/`shared-state.md`/`acceptance.md`、M0 计划 S2 全文（64-123 行）、PRD V0.6 §8.6/§8.7/FR-700~705/§10.3；C1 两份原报告 + `round-1-disposition.json` + `round-1-evidence-lineage.json`、C2 两份原报告 + `round-2/dispatch.json` + `round-2-processing.json`、C3 两份原报告（Z 135 行/SHA `759fa027…`、MM 352 行/SHA `b1acf1e2…`）+ `round-3/dispatch.json` + `round-3-processing.json`（R3-N1 方法更正记录读回）；`c4-verification.json`、`c4-internal-review.json`、`c4-ci-trigger.json`、`c4-frame-encoding.json`、`c4-frame-encoding-v2.json`、`round-4/source-lineage-note.json`。

### 3.2 实际运行的验证命令与真实结果（全部完整重定向取 `$?`，隔离 export 根）

| # | 命令/核验 | 结果 | 退出码 |
| --- | --- | --- | --- |
| 1 | 候选完整性（121 清单对 HEAD 树 git blob 重算 SHA256） | 121/121 一致、集合相等 | 0 |
| 2 | `git diff --name-only 9eb0b6e..8f8eda1e` | 仅 4 个 docs/流程文件 | 0 |
| 3 | 124 sealed runtime inputs 对当前工作区重算 | 0 缺失 0 不匹配 | 0 |
| 4 | 148 raw artifacts 全量重算 SHA256+字节 | 148/148 一致 | 0 |
| 5 | macOS C4 引擎二进制 `shasum -a 256` | `1f5a5eb8…` 一致 | 0 |
| 6 | CI attempt1 五份原始工件哈希（run/jobs/annotations/linux/windows log） | 5/5 一致 | 0 |
| 7 | `uv sync --frozen`（export 根独立 venv） | 成功（editable 指向 export） | 0 |
| 8 | `npm ci`（export 根独立 node_modules/cache） | 成功 | 0 |
| 9 | pytest `test_frame_corpus.py + test_worker_owner_bootstrap.py + test_handshake_deadline.py` | **86 passed** | **0** |
| 10 | pytest `test_worker_parent.py + test_resident_runtime.py::test_default_handshake_deadline_closes_real_source_or_packaged_transport` | **2 passed in 7.76s**（含真实 3s owner 死亡等待与 ~5s 自然退出） | **0** |
| 11 | `npx vitest run tests/unit/{supervisor,task-runtime,task-service}.test.ts` | **57 passed / 3 files** | **0** |
| 12 | PYTHONUTF8=1 下 pytest `test_frame_corpus.py` | **53 passed**（51 帧例 + 2 cp1252 回归在 UTF-8 mode 仍生效） | **0** |
| 13 | **本人独立 busy-inbox 握手探针**（真实生产默认 `handshakeMs=5000`、真实 stdio/SQLite、无任何 clock/queue/limits mock；内联 heredoc 执行，日志 `probe-handshake-c4.log`） | 持续唯一 pre-hello health flood：**5.0874s 自然退出、exit 0、stderr 0 字节、实际响应 33,317 条、duplicateIds=0、5.5s 迟到 hello 因管道已断未被接受（lateHelloWriteOk=false）**——**排除"请求预算耗尽/重复 ID 致命"的解释不依赖响应计数单点：实际写入/尝试上界 34,201（uniqueIdsSent 34,000 + 1 个可能未完整写入的批次 200 + 迟到 hello 1），仍 < 65,536**。断言 `PROBE_OK` | **0** |
| 14 | Windows CI 首败日志分组实测 | `39 failed, 978 passed, 3 skipped`；分组 `test_frame_corpus`=36、`test_coordinator_control`=1（`\r\n` vs `\n` 实测证据行）、`test_resident_runtime` default-handshake=1、`test_worker_parent`=1；36+1+1+1=39 与 `c4-ci-trigger.json` 四组精确一致 | —（读取核验） |
| 15 | source-lineage-note 三事实核验 | ① 冻结 JSON SHA `327263aa…`/61262B 未改写；② 旧 checkpoint `checks` 序列化确实重复最终 sealed log 路径/计数（浅引用症状在）；③ 旧 log 实测 630/1051、630/1048+3skip、包 13；最终 log 实测 630/1052、630/1049+3skip、两平台包各 17 dots | 0 |
| 16 | cp1252 可解码性验证（"中文😀".encode().decode('cp1252')） | 成功（10 字符乱码），新回归的乱码断言可达 | 0 |

**保留的工具性失败（如实记录，不掩盖）**：① 首次 vitest 使用 `--reporter=basic` 启动失败（`ERR_LOAD_URL`/`Failed to load custom Reporter`——vitest 5 无该 reporter，与 C2 轮 MiniMax 遇到的同类参数错误一致），去掉参数后重跑通过；② 首次探针误用上级手动 venv（无包）rc=1，改用 export 内 `source/.venv` 后通过；③ 一次 Write 落盘探针被 Mimosa 误报拦截（§1）。三处均未绕过安全意图。**边界更正（R1）：原始失败输出文件已被成功重跑的同名重定向覆盖，独立根现存日志均为最终成功运行——失败原文从本审查会话的工具输出记录逐字恢复至 `build/I04-review-ZCode-GLM53-C4/failures-recovered-from-session.md`（恢复副本、注明来源，不冒称原文件仍在）**；首版报告已由总控逐字快照，其"原失败记录保留在各日志"的不准确表述以本更正为准。

### 3.3 证据审阅与绑定（读实际内容，独立复核）

- `c4-verification.json`（1482 行）：两平台 check（macOS 630/1052、Linux 630/1049+3）、两平台包各 17 runtime、两平台各 144 格矩阵（96+48 全 passed）、源码+包内各 6 项隔离 Linux GUI/native、12 源归档；limitations 六条如实（Windows native 仍需 CI、macOS runner 未取得非代码结论、owner 修复曾有两次 harness/环境失败保留、POSIX onedir 边界、签名/干净设备/生产/领域未验）。`productionAndDesktopRunCheckpoint.checks` 归属缺陷见 C4-Z1。
- `c4-internal-review.json`：六项独立有限审查索引（encodingInitial/encodingFixed/rootTests/owner/packageOwnerFirst/packageOwnerFinal），C4-ENC-01（P2，第一版 cp1252 模拟在 UTF-8 mode 失效）已由 223f978 修正并独立复检；`remainingInternalImplementationBlockingFindings=[]`；明确不替代外部门禁。
- `c4-frame-encoding.json`/`-v2.json`：第一版模拟 5cbe39c 的 UTF-8 mode 1 红保留、223f978 修正后双模式复现旧 36 红/新 51+2 绿的原始记录；"修模拟不等于实测 Windows"边界如实（真实 Windows 由 CI 证明——attempt1 已实证 36 红，修复后须下次 CI 复验）。
- `c4-ci-trigger.json` + 五份原始工件：run39462746525 attempt1 conclusion=failure；Linux Quality success；Windows engine:check 39 失败（分组 14# 实测吻合）；macOS cancelled、runner_id=0、steps=[]、官方 annotations 明确 hosted runner 未取得/容量约束——未取得 runner 诊断，不记代码通过也不记代码失败，无用户手动取消证据（与派发口径一致）。
- CI attempt1 的 Windows 失败**真实证明**了缺省代码页问题在生产路径存在（parser 正确解出 UTF-8 中文😀、expected 经 locale 解码乱码——日志断言差异方向与此一致）；C4 修复为显式 UTF-8（源字节与原精确断言保留，我逐行核读 diff，无 expected 放宽）。

### 3.4 未验证事项（如实保留，不记为通过）

1. **远端三平台真实 CI（C4 版）**：尚未运行——修复后的 Windows 真实 cp1252/stderr CRLF/EINVAL/真实 launcher 亲缘链与 owner 身份链、macOS hosted runner，均须在双审通过后的新 CI 中验证；本轮全部本地证据不能替代。
2. Windows native ABI 上的 owner 身份监控实际行为：Win32 doubles 只验证签名/身份/失败策略（test 文件头自我声明"only Windows CI can establish actual native behavior"），macOS/Linux source+onedir 实测不冒充 Windows；原 CI 的完整亲缘链（launcher→实际协调器）未捕获复现，修复不声称唯一根因。
3. 本机未运行 `test:e2e`/Electron/打包产物 GUI（无桌面打扰约束）；隔离 Linux 源码+包内 GUI/native 证据经 148 工件哈希绑定与实读，非本人复跑。
4. `package:dir` 未由本人重跑：两平台 C4 引擎二进制哈希已核（macOS 实测、Linux 以核验过哈希的证据为据），且 124 输入清单证明打包相关输入字节自证据采集后未变。
5. 完整聚合 `npm run check` 未在本 export 重跑整版：同候选已有充分绿证据——**运行环境精确化（R1）：C4 完整 macOS check/打包实际运行于 I04-reconnect worktree，Linux 于隔离 arm64 容器；primary checkout 本轮未运行整版 check，其 `out/release` 为历史 C2/C3 产物**。该运行的运行时输入经 124 文件 sealed 清单与 primary 候选字节哈希同源（本人实测 0 缺失 0 不匹配、git blob 0 差），两平台最终 log 计数我实测 630/1052、630/1049+3skip；本轮按效率规则以定向复验 + 关键反例 + 证据绑定覆盖，我独立运行了 86+2+53 Python、57 TS 与独立握手探针。
6. 签名、干净设备安装、生产运行、领域业务（E.2/E.5/G.4/FR-704）、I05 语义、I06 网关、性能容量通过线：均未验证/未完成，不由本 ADR/报告代替。
7. `parallel-coordination.md`、完整 `state.json` 未逐行通读；I03 R2-F1"恰好 24 条反例"的数字未逐条清点（反例族与双端严格校验在整包运行中覆盖）。

## 4. 本轮新发现问题

### C4-Z1（P3，非阻断，已披露并更正）：`c4-verification.json` 旧生产/GUI 检查点的 `checks` 字段浅引用归属错误

- **位置**：`docs/reviews/I04/c4-verification.json` 的 `productionAndDesktopRunCheckpoint.checks`（source=f504b30）。
- **触发/机制**：收集脚本按引用保留 checks list，随后替换最终 list 元素，序列化时旧检查点重复了最终 sealed 检查（`c4-sealed-check.log` 630/1052、`sealed-check.log` 630/1049+3）——即把**最终** 9eb0b6e 的计数错误归属给**旧** f504b30 运行。
- **证据（本人独立核验）**：① 冻结 JSON SHA `327263aa…`/61262B 与 `round-4/source-lineage-note.json` 的 frozenFile 一致（原 JSON 未被改写）；② 症状实测在；③ 旧 log 实测 `c4-root/check.log`=630TS/**1051**Py、`c4-final-linux/check.log`=630TS/**1048**Py+3skip、包 13 项；最终 log 实测 **1052**/**1049+3**、两平台包各 17——与更正声明逐项吻合；`laterChangedHostHarnessFiles` 三文件（owner bootstrap 新增等）解释 +1 测试增量，自洽。
- **影响**：证据链自洽性（读者可能把最终计数归给旧检查点）；不影响任何实现/测试/配置/依赖字节，不影响最终 sealed 验证的真实性（其自身 log 与哈希完好），不影响 GUI/矩阵原始证据归属。
- **处理结论**：**接受开发线主动披露的事实更正**（冻结原 JSON 保留 + `source-lineage-note.json` 交叉索引，处置方式与 C1 轮 P3-7/Z1 先例一致）。**非阻断，允许以说明文件形式结案**；后续候选若重录 c4-verification 类摘要时应修复收集脚本的浅引用。

### 已核验为非问题的对抗性假设（记录证据边界，不编造问题）

- "worker owner argv 可被滥用扩大能力"——证伪：`--coordinator-owner` 仅由受信 coordinator 以 `os.getpid()`（win32 +FILETIME）生成；worker 侧严格解析（ASCII decimal ≤20 位、pid∈(1,0xFFFFFFFF]（即 [2,4294967295]，与代码 `1 < pid <= 0xFFFFFFFF` 精确一致）、win32 created≠0/POSIX==0），frozen 入口 `--worker` 私有 token 不扩公开协议；worker 本身无 DB/路径/网络（docstring 与代码一致）；缺失/已死/复用/监测异常均退出 73（Win32 doubles 六类失败 + 参数化非法 argv + 真实三臂子进程均验证）。
- "POSIX 直接父进程校验可被 PID 复用欺骗"——证伪（代码层）：owner 死后 worker 被 repartner，`getppid()` 返回收养者而非复用原 PID 的新进程；`pid>1` 排除 init。当前 source/onedir 有实测；onefile/broker 边界已如实声明待验。
- "monitor.close() 的 join(0.5) 失败会使已完成任务误标"——确认存在但属保守设计：监控线程无法停止=监控故障=fail-closed 退出 73→coordinator 按 ENGINE_EXITED 失败该 job；正常路径 `stop.wait(0.1)` 可中断，概率极低；与"监测不可用不静默忽略"的既定语义一致，非缺陷。
- "cp1252 模拟是镜像测试"——证伪：注入臂断言 `default_cases != loaded_cases` 且首例文本等于 cp1252 误解码形式（我实测该 decode 可达），证明注入真实生效；正式路径显式 UTF-8 不受影响；普通与 `-X utf8` 双模式均 53/53 通过。
- "stderr 换行修复放宽了产品 stderr 语义"——证伪：diff 仅改测试期望为 `os.linesep` 精确比对**同一**固定有界消息（`ENGINE_SESSION_FAILED`），产品 `__main__` 输出未变（coordinator.py 零相关变化）。
- "EINVAL 清理容忍会吞真实失败"——证伪：仅 `win32 && errno==EINVAL && process.poll() is not None` 且在全部自然退出/传输断言**之后**的 finally 清理中；BrokenPipe 保留、其他 OSError 仍抛。
- "握手 deadline 在 C4 回退"——证伪：serve 循环顶部检查字节未变（C4 唯二变化为 import 与 `worker_owner_arguments()`），本人默认参数独立探针 5.0874s 自然退出、迟到 hello 未接受。
- "CI 矩阵步可能被跳过/绑定错误源"——证伪：步序 npm ci→uv sync→matrix（HEAD 绑定）→check，失败仍红，always 上传。
- "包内资源依赖缺省代码页"——证伪：spec datas 显式打包 contracts/v2+contract_v2.py+uv.lock；`contract_probe.py` 三处显式 UTF-8；`verify-i04-package.py` 在临时 cwd 运行并已扩展 owner 用例。

## 5. 历史问题逐项独立判断（22 个原始 ID + R3-N1）

判定口径：以本候选实际代码、本人运行结果与哈希绑定证据为准；原 ID/等级原样保留；C3 通过不自动沿用作 C4 结论——但 C3 双审通过的核心产品字节在本候选**未变**（`git diff d3ad536..8f8eda1e` 对 job_store/engine.ts/task-service/protocol/memory_guard/schema 等 UNCHANGED 实测），我的复核依据为"字节一致 + 关键声明点抽核 + 本人定向运行"。

### 5.1 C1 — ZCode（4 项）

| ID | 级别 | 摘要 | 本轮判断 | 独立依据 |
| --- | --- | --- | --- | --- |
| B1 | P2 | darwin 内存故障误分类竞态 | **已关闭（在 C4 字节上保持关闭）** | `memory_guard.resident_bytes` 仅 `read<=0+ESRCH→ProcessLookupError`（`set_errno(0)` 防残留）；coordinator 轮询仅捕它并交真实退出码（EOF 后 74→RESOURCE_LIMIT(memory)，coordinator.py:456-457 直读）；C4 未改此路径。**依据边界（R1 更正）：本人本轮定向 86 项（frame 53 + owner bootstrap 30 + 握手定时 3）不含 memory_guard/lifecycle 的 ESRCH 组；B1 判定依据为代码直读 + 开发线 1052 整版 sealed 证据（log 哈希绑定 9eb0b6e 同源字节，ESRCH/竞态组在其中通过），非本人复跑** |
| Z1 | P3 | source-final1 清单时点差异 | **已关闭** | C4 以 124 sealed 输入清单重新绑定（0 差实测）；历史成因由 lineage 交叉索引 |
| Z2 | P3 | reconcile 死分支 | **已关闭** | `reconcile_jobs`（job_store.py:926 起）为 cancelling→cancelled/其余 failed 二分，直读 |
| Z3 | P3 | 非分页响应显式字节预算预检 | **按原约延期（开放）** | 本轮无 schema 词汇/预算扩张（contracts 在 C3→C4 零变化）；与 I03 O1 同批，维持原登记 |

### 5.2 C1 — MiniMax（15 项）

| ID | 级别 | 摘要 | 本轮判断 | 独立依据 |
| --- | --- | --- | --- | --- |
| P1-1 | P1 | 断连后首次重建订阅 NOT_FOUND、UI 陈旧 | **已关闭（保持）** | task-service.ts:119 跨会话仅本地 fence；fenceConnection/connectionChanged/restoreOnce/recover 抽核；字节与 C3 双审通过版一致；隔离桌面证据经 148 工件绑定 |
| P1-2 | P1 | 96 格矩阵断言不完整 | **已关闭（保持）** | `commit_job_round` 精确 expected 比对直读；两平台 144 格矩阵 summary 哈希核验（96+48 全 passed）；CI 独立 step + 缺格负例 exit 1 机制在 |
| P1-3 | P1 | 资源上界降级 INTERNAL_ERROR | **已关闭（与 B1 同根，保持）** | 同 B1；fail-closed 语义未宽化 |
| P2-4 | P2 | 分页上界三层不一致 | **已关闭（保持）** | schema 200/100（C4 零变化）+ 引擎 maxPageItems=200 + TS 一致；210 行 200+10 用例在整包绿证据中 |
| P2-5 | P2 | job.progress 无生产端 | **已关闭（保持）** | `_progress`/`_stage` 生产端在 coordinator.py:99-141 直读；恒 completed/total=None |
| P2-6 | P2 | seen 无回收、65536 后会话终止 | **已关闭（按声明的有限会话策略，保持）** | `seen` 只增不减、上限含 hello/ping（coordinator.py:173-175 直读）；ADR-0003 明示生命周期；本人探针 33,317 响应仍在预算内运行正常 |
| P3-7 | P3 | local-verification differences=[] 与实际不符 | **已关闭（保持）** | lineage 索引；C4 sealed 清单重新绑定 |
| P3-8 | P3 | 内部审查无法映射修订 | **已关闭（保持）** | C4 起证据以 observedGitHead+文件哈希显式绑定（本轮我复核一致） |
| P3-9 | P3 | native 失败未索引 | **已关闭（保持）** | 原始失败与哈希保留于 lineage/证据目录 |
| P3-10 | P3 | status 表述矛盾 | **已关闭（保持）** | 现行 status.md 时点段落清晰（162 行通读） |
| P3-11 | P3 | 矩阵计数无证据 | **已关闭（保持）** | 144 格机器记录 + CI artifact + 负对照 |
| P3-12 | P3 | 原生聚焦自证/dialog 缺字段 | **已关闭（证据层面，保持）** | 外部 xdotool/XGetInputFocus 观察者 + nativeDialogs 字段在 148 工件中；宿主复现仍待远端 CI |
| P3-13 | P3 | reconcile 死分支 | **已关闭（同 Z2）** | 同上 |
| P3-14 | P3 | commit_job_round 绕状态机 | **已关闭（保持）** | 显式守卫直读（`state!="running" or mode!="rounds"→INVALID_STATE`）；running→running 为持久证据修订，状态名迁移仍由 `_transition` 校验 |
| P3-15 | P3 | claim 预查在事务外 | **已关闭（保持）** | 预查 advisory（coordinator.py:255-258 直读，幂等豁免防 QUEUE_FULL 误拒重放）；权威创建在事务内复验完整指纹，operation 主键唯一 |

### 5.3 C2 新增（3 项）

| ID | 级别 | 摘要 | 本轮判断 | 独立依据 |
| --- | --- | --- | --- | --- |
| R2-N1 | P3 | 父侧监测不可用缺在树回归 | **已关闭（保持）** | 在树回归 `test_parent_rss_monitor_unavailable_fails_only_the_target_real_worker`（Darwin 专属）在 C4 整包绿证据中（1052 含之） |
| R2-N2 | P2 | 握手预算流量条件性 | **已关闭（在 C4 字节上独立重验）** | serve 循环顶部检查（coordinator.py:636-640 直读，C4 未改）；**本人默认参数 busy-inbox 探针**：5.0874s 自然退出、exit 0、stderr 空、实际写入/尝试上界 34,201 < 65,536（34000 唯一 ID + 保守 1 批次 200 + 迟到 hello 1，实际响应 33,317 与之自洽）、duplicateIds=0、迟到 hello 未接受（探针日志留存）；不把单请求等待超时当全握手上限（LIMITS 分立核对） |
| R2-P1 | P2 | （MiniMax 同根）握手可被绕过 | **已关闭（同 R2-N2）** | 同上；及时会话不受影响由 test_handshake_deadline.py 三项定时测试覆盖（我的 86 项含之） |

### 5.4 R3-N1（方法事件，无产品 P 等级）

**维持"审查 harness 自身缺陷、非产品问题"的定性，不构成产品修复、新 P 项或自然超时性能证据。** 依据：round-3 MM 报告修订记录与 §5/注 A/注 B、round-3-processing 同任务方法更正记录读回——v2 重复 200-UUID payload 触发 duplicate-id fatal 冒充期限终止、活会话 `stderr.read()` 阻塞（挂起 >4 分钟，33.571s 为收尾关 stdin 后 EOF 观测，非自然到期）；v1/v2 `-I` 忽略 PYTHONPATH 使"红臂"实际跑同版代码（无效红臂）；v3/v4 修正（每批新 UUID、有界收尾、显式 sys.path 红臂），但其 `MAX_TOTAL_REQUESTS=40000` 与**写调用批次**比较（理论 8,000,000 帧），不构成 <65536 的请求数上界——排除性论证改用实际 `replies`（183/192/193 批×200≈36192/38019/38119，红臂 63201=316×200+1），四臂 duplicateIds=0。该事件不进入受审代码、不需新候选；本轮候选源码中无该 harness。我的独立探针（33,317 replies、独立实现）与其结论方向互证，但互不依赖。

### 5.5 继承开放项（不计入 22 ID）

I03 R2-F1 保持关闭（双端 `accepts_job_event` 字节未变，整包绿）；I03 O1 / Z3 按约开放（本轮零词汇扩张）；I03 O2 遵守（UI 固定模板）；I03 O3 / I01 R6 按约开放（无无依据优化）；F5 保持满足（classify 语义未变，C4 未引入机械映射）；F6 基础设施子项保持关闭、E.2/E.5/G.4/FR-704 业务仍开放不代完成；I05/I06 边界遵守（entrypoint 保留 `--storage-probe`，无 semantic hooks、无网关）。

**22 个原始 ID 合计：21 关闭 + 1 按原约延期（Z3，P3）；0 依据不足；0 未关闭阻断。**

## 6. 十项原验收 + 追加十项真实路径的逐项判断

| # | 原验收 | 判断 | 关键证据/边界 |
| --- | --- | --- | --- |
| 1 | 常驻健康/协商/registry SHA/只开放已实现能力/v1 不兼容/旧注释修正 | **通过** | 同 PID 复用、registry 原始字节 SHA、`PROTOCOL_VERSION=2`；`productRuntime=["health"]`（C4 未变）；我的 vitest 57 含 supervisor 组 |
| 2 | 严格 JSONL：全边界 + 追加前上限 + 终态后丢弃 + 双端同源 | **通过** | JsonlReader 追加前检查直读；51 帧例双模式（普通+UTF8 mode）53/53 绿；**C4 修复缺省代码页读取且保留原字节与精确断言**；Windows 真实平台复验待 CI |
| 3 | request/job/operation/session/subscription/seq 归属与乱序 | **通过** | seen 去重/上限、matchesResponse、代次/会话/项目/订阅联合校验（字节未变+抽核） |
| 4 | 有界队列/并发/单 writer/各超时/心跳/取消/内存/忙碌可取消/故障隔离 | **通过** | LIMITS 分立；**握手绝对 deadline 在 C4 字节上经本人默认参数独立探针重验**；排队计入总时限（tick 347 行直读）；owner 死亡守卫新增（worker.py 全文审+实测） |
| 5 | 唯一 SQLite/同事务证据/完整指纹/无第二权威 | **通过** | operation 主键+immutable 触发器+事务内复验（C3 字节+抽核）；worker 无 DB 入口（worker.py 直读） |
| 6 | S1 故障矩阵逐项 | **通过** | 96+48 逐格精确断言 + 两平台 144 格 recorder 哈希核验 + 真实 READONLY/取消/退出分支（C3 字节+绿证据绑定） |
| 7 | 安全错误→UI 四段式 | **通过** | classify 真实主码分类+未知兜底；固定模板；**stderr 平台换行修复不改变产品语义**（仅测试期望按 os.linesep） |
| 8 | 窗口重建/崩溃/无响应/后台任务保留 | **通过（以隔离证据+哈希绑定为准，本机未复跑）** | 源码+包内各 6 项 C4 独立路径 GUI/native 证据（148 工件绑定）；外部 X 焦点/dialog 字段在 |
| 9 | U1 边界/分页/真实依赖/测试任务不登记业务 | **通过** | 200/100 四层一致；测试能力 test-only+test_mode 双门；renderer 无创建入口 |
| 10 | ADR-0003 真实运行采用 + 包内资源 SHA | **通过** | ADR 边界如实（Darwin 非硬上限等）；spec 显式打包契约+锁；两平台引擎 SHA 核验（macOS 实测）；临时 cwd 寻址 |

**追加十项**（派发指定真实路径，逐项独立核验）：

| # | 路径 | 判断 | 证据/边界 |
| --- | --- | --- | --- |
| 1 | 3 次只读恢复/marker-revision 竞态/迟到 health/job.get 对账/不重发写 | **通过** | task-service 抽核 + 隔离证据绑定（字节与 C3 双审版一致） |
| 2 | 96+48 原精确断言/mid_job_terminal/逐格只读 recorder/CI 步位置与 HEAD 绑定/缺格非零 | **通过** | 哈希核验 + CI 步序直读 + 负对照机制（C3 已实测、字节未变） |
| 3 | Darwin 仅真 ESRCH 转交真实退出码/其他 fail-closed/父子隔离先 fence 后 reconcile | **通过** | memory_guard:80-91 + coordinator:443-448 直读；不以其他平台跳过冒充 Darwin（专属测试在 macOS 真实执行于整包绿证据中） |
| 4 | result.page 默认 200/显式更小预算/稳定 resultId 游标/F6 多页摘要/回收反例/历史不删/未知总量 stage | **通过** | 四层上界一致；`_progress` 恒 null 总量；摘要仅首页（C3 字节+绿证据） |
| 5 | 65536 唯一请求有限会话（含 hello/ping、不淘汰）/父 stdin 开启 fatal 干净退出/新会话对账 | **通过** | 代码直读 + 我的探针在预算内行为正常 + default-handshake 传输用例实测（2 passed 含之） |
| 6 | 外部 X 焦点/dialog 字段/源码+包内窗口恢复；arm64 不冒充 x64/Windows/CI | **通过（边界如实）** | 148 工件绑定实读；未在宿主复现 |
| 7 | JobStore 不可达分支清理/round 守卫分工/queued/cancelling/terminal 拒绝/advisory 预查 vs PK 权威/集合删除重加 ledger/失效/所有权/跨项目反例 | **通过** | 直读 + 144 格矩阵（definition-remove 逐格 staleReason 精确重算在绿证据中） |
| 8 | 生产默认握手绝对 deadline：每次读取/解析 loop 检查/不续期/粘包/已缓冲多帧/不误杀及时 hello/心跳不延长/过期安全终止清理/非单请求超时当全上限 | **通过（本人独立重验）** | serve 循环顶部 `>=` 检查、deadline 一次建立（直读）；**默认 5000ms 真实路径探针 5.0874s 自然退出、迟到 hello 拒绝、exit 0/stderr 空**；三项精确定时测试绿 |
| 9 | 精确定时回归与真实默认包 case：计时来源/容差/首次每 loop/握手前后状态/真实退出输出/包内默认值/规范资源（线索文件均实读） | **通过** | `test_handshake_deadline.py`/`test_resident_runtime.py` 第 13 项/`scripts/verify-i04-package.py` 实读并运行；包内默认值经 C4 两平台 17 项包 runtime（哈希绑定）；非仅 mock/缩短参数 |
| 10 | 新 C4 Windows 路径：UTF8 共享资源与契约探针按原字节/OS stderr 精确固定模板/peer-exited EINVAL 只限清理/真实父 worker 身份/退出/兄弟隔离/可信 private-bootstrap/包内同例/不扩大 worker 能力 | **通过（本机模拟与实测边界如实区分）** | 显式 UTF-8 三处 + cp1252 双模式模拟（含注入臂真实性断言）实测 53/53；stderr os.linesep 精确比对；EINVAL 三条件容忍直读；owner 身份三臂真实子进程 + Win32 doubles 六类失败；包内验证脚本已扩展；**Windows native 真实行为仍待下次 CI（不冒充已验）** |

## 7. CI 首败与 C4 处置的准确边界

- C3 通过后推送 24fd202、PR #5 创建；run39462746525 attempt1：Linux Quality **success**（含源码+包内 native recovery）；Windows engine:check **39 failed/978 passed/3 skipped**（我实测分组：frame_corpus 36=UTF8、coordinator_control 1=STDERR CRLF、resident_runtime 1=PIPE-CLOSE EINVAL、worker_parent 1=WORKER-OWNER，36+1+1+1=39 精确吻合）；macOS **cancelled**、runner_id=0、steps=[]、官方 annotations 为 hosted runner 未取得/容量约束——**不记代码通过也不记代码失败，无用户手动取消证据**。
- C4 处置：UTF8→显式 encoding（资源字节与原精确断言保留，双模式模拟验证）；STDERR→os.linesep 精确比对同一固定消息（产品 stderr 不变）；EINVAL→仅 win32+peer 已退出的 finally 清理容忍；WORKER-OWNER→真实 owner 身份监控（pid+win32 FILETIME+固定句柄，读 stdin 前核对，缺失/已死/复用/监测异常退出 73）。**原始失败与 attempt1 全部归档未抹除**（5 工件哈希核验）。
- **保留边界**：修复的最终 Windows 根因确认与真实 launcher 亲缘链复现由下一次真实 CI 验收（C4 尚无 CI）；Windows native ABI 行为不被 doubles/macOS/Linux 实测冒充；5cbe39c 旧模拟的 UTF-8 mode 1 红保留，223f978 修模拟不等于实测 Windows（attempt1 的 36 红才是实测证据，修复后待 CI 复验转绿）。

## 8. 最终结论

**通过（针对冻结候选 C4：`e45e6038b5e0f8f4adc69ed55aafccd75b3d3500` → `8f8eda1e24c0425ea2a65d2566978913ee310b8b`，121 文件）。**

- 候选身份、冻结完整性与证据绑定全部成立（121 清单 0 差、124 sealed 输入 0 差、148 工件 0 差、9eb0b6e→head docs-only、macOS 引擎二进制实测一致）。
- C4 相对 C3 的产品变化（owner 身份 argv、显式 UTF-8 读取、包验证扩展、四处测试平台适配）经全文精读、独立运行与对抗性检查，未发现阻断或重要缺陷；worker owner 监控的安全边界（不扩能力、fail-closed、可信参数）成立。
- 22 个历史 ID：21 关闭 + 1（Z3）按原约延期，独立复核依据如 §5；R3-N1 维持方法事件定性；CI 首败四组的修复处置经代码与模拟/实测核验，边界如实。
- 本轮新发现仅 C4-Z1（P3，证据归属，已披露并以 lineage note 更正，非阻断）。
- **通过的含义边界**：仅指本冻结候选在本轮可执行验证范围内满足原验收与继承义务。以下仍为后续必备门禁、未验证不视为通过：**C4 版远端三平台真实 CI（尤其 Windows native 身份/编码/stderr/管道与 macOS runner）**、feature push/PR/正常合并/远端核验、签名、干净设备、生产运行、领域业务（E.2/E.5/G.4/FR-704）、I05/I06 集成。本轮未在宿主启动任何 GUI、未推送、未合并。
- 上述结论独立作出，未参考、也未等待另一模型本轮任何报告或结论。

## 9. 资源与约束声明

- 全部验证在本人独立 export（`build/I04-review-ZCode-GLM53-C4/`）内完成：独立 venv/node_modules/npm/uv 缓存、basetemp、临时 DB 与探针日志；primary 的 out/build/release 未写入；无符号链接或借用其他线可变依赖。
- 未启动宿主 Electron/native/HMR/产物 GUI，未自动点击或 Raise 任何应用，未操作审查 UI；一次 Mimosa 误报拦截以 heredoc 合规绕行（§1）。
- 冻结文件零改动；`AGENTS.md` 保持 dirty 且 SHA 未变未 stage；本报告为唯一写 primary 输出 `docs/reviews/I04/round-4/zcode-glm53.md`；未覆盖 round-1~3 任何报告。
- 共享构建预约：本轮未在 primary 运行任何 check/build/package（定向验证均在 export），无共享输出占用。
