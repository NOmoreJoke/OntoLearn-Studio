# T02 FR-200/FR-201 全新 R08 整候选独立工程审查（ZCode / GLM-5.3）

## 0. 配置与来源声明

- 本方配置由**操作者经官方 UI 核验后转述**：BigModel 个人订阅 / GLM-5.3 / 思考等级最高 / 完全访问；Start Plan 官方页面显示暂无可用体验套餐，故使用现有个人订阅，无新增付费。**模型本人未直接查看任何 UI**，以上为操作者陈述，如实区分，不虚构本人看见的证据。新任务 ID 由操作者另行核验，本报告未获得任务 ID。
- cwd `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T02-s1-review-fixes`，分支 `feature/weekly-t02-fr200-fr201`。
- 本轮为全新 R08，不继承 R01–R07 任一候选的通过/ConditionalPass 结论；**未读取、未索取另一方当前 R08 正文**（其文件名元信息亦未主动查看）；历史 R01–R07 材料、O 系列输出与仓内归档作为历史输入同等读取。
- 唯一仓内写入为本文件。未运行产品、npm/check/vitest/pytest/ruff/构建/打包/GUI/SQL/probe；未改 index/commit/push/branch；未读密钥、无关 profile 或用户 `.mimosa` 数据；未重试旧拒绝 probe。

## 1. 附件与身份核验（本人实做）

用官方 Read 工具分段完整读取唯一粘贴附件至 EOF，并用 shell 只读计算复核：

| 项 | 结果 |
|---|---|
| 附件字节 / SHA256 | 26708 B / `0f6b92e2968e67edb7b29c697a6cd0baf69e04b92016fac8290651c4c91711c9`，与附件声明一致 |
| 用户原清单 | 尾段恰 11255 B，起于"你现在是我的软件工程审查员。"，该标志全文恰出现 1 次，至 EOF 终止（末行"remembering why it's built this way…"），无重复粘贴 |
| HEAD / tree / 分支 | `62d4b0a2c3ad49ae37775b875a3e7e31db5fadac` / `7ad1d13d6a064aaa07bd046e78427e881e1732b4` / `feature/weekly-t02-fr200-fr201` |
| base→head | `583c05c7…` 为 head 祖先（merge-base 校验通过）；`rev-list --count` = 36 提交；差异叶 98 |
| 9cb→62d4 | 恰 4 叶：`.github/workflows/ci.yml`、`package.json`、`scripts/engine-test-reporting.py`、`scripts/run-engine-tests.py` |
| tracked 物理源 | `git ls-files` = 1380 |
| 工作区状态 | 仅 `M AGENTS.md`（保护 overlay）＋ 未跟踪 round-01/02/03 WIP，与附件声明一致，未被改动或混入 |
| PRD | 93584 B / SHA256 `7586b2c4…f60fbb` 一致；实读 FR-200/201 第 307–318 行 |
| AGENTS.md overlay | 15147 B / `de15f6ce…5a8c8c4` 一致，确认为政策 overlay 非本候选新增 |

## 2. 已读范围与本人验证 vs 他人运行证据的区分

**本人实做（纯计算/只读）**：附件与全部哈希核验（上表）；`git rev-parse/diff/ls-files/status`；PRD 条款与 D8 授权 JSON 实读；round-05 条款映射（28 笔）实读；R07 DISPOSITION（23 本轮＋55 历史位置）实读；O056 COMPLETION.json/FINAL-MANIFEST.json/三份独审/撤销记录/资格文件实读，并**本人独立重算**：1692 针 manifest 全部存在且哈希匹配（0 bad）；mode2 运行 `run-30cfd524` 从 summary/collection/events 原件重计（计数、coverage、双 worker identity 全等、start/finish、每 (node,phase) 报告恰一次、6 setup-skip/0 teardown-skip）；native24 report.json 独立展开（24 specs 全 ok、21 expected＋3 skipped、retry 全 0、附件 101=100 body＋1 引用、21 个 launch body base64 解码后 expectedUserData==userData、21 唯一 userData、21 唯一 sessionData、appPath 均为本 S2 apps/desktop、packaged 全 false）；资格文件 identity 七字段与 native-uv 基线 effective.json 逐项相等；root `pyproject.toml` SHA `ed02773b…` 与资格 configSHA256 相等；两个 CI 脚本 controlHashes 与当前 HEAD 脚本哈希相等；引擎与渲染端代码实读＋定向检索（§4）；CSP `csp.ts` 全文实读；两 TS 测试裸 `python` 复核。

**读取他人真实运行证据（本人未重跑）**：O056 的 `npm run check`（205.846s 自然 0）、`verify:sources`、mode2 114.075s、native24（184.5s/清理 190.3s）、guard 反证回单、ls-remote 远端回单。这些是 ROOT/开发线产生的原始运行记录，本人只做读回与复算，不冒充本人重跑。

**未验**：任何 Windows 真实运行；远端 CI（62d4 未 push，无本 head CI）；打包/签名/公证；GUI 现场（本轮无 GUI 运行）；未逐行读完 storage.py 1887 行/job_store.py 2993 行/t02 e2e 1748 行全文（抽样＋定向检索＋测试面覆盖）；未读另一方 R08 正文；未读 csp 之外全部主进程文件（desktop-ipc/engine.ts/project-mainline-service 仅经差异统计与既往轮次覆盖）。

## 3. 候选构成（base583→62d4 整体）

36 提交、98 差异叶、1380 tracked、5 构建。构成：FR-200/201 引擎实现（mainline.py +417、job_store.py +406、storage.py +114、project_host/query_presentation/coordinator/domain_changesets/rdf_snapshot 修改）；契约双端（TS v2 +131/schema.json +525、python contract_v2 +49、注册表/fixture/binding-regressions）；渲染端 7 文件（OwnershipConflictDetailView、mainline-ownership、mainline-facts 等）；vendored rdflib fr201.1/.2/.3 三轮＋upstream 7.6.0 轮＋补丁＋PROVENANCE；新增 12 个 T02 测试文件＋6 个既有测试扩展；评审归档 round-04..07；最后 9cb→62d4 仅 4 个 CI 叶（产品源码、原 engine/E2E 测试、pyproject、依赖锁、cap、标准、fixture 与断言自 9cb 起零改动——由 4 叶差异直接证明）。

## 4. 代码审查发现（本人实读）

### 4.1 新 CI 控制层（9cb→62d4）

**scripts/run-engine-tests.py（471 行，全文实读）**
- mode 未设或 `1`：`os.execv(sys.executable, [sys.executable, "-m", "pytest", *sys.argv[1:]])` —— 原生 venv pytest、原 args/env/退出码，无任何报告目录/信号控制先建立。符合"默认保持原生"。
- mode `2`：原生完整 `--collect-only` collection → `partition()` 按 CI40 Windows 历史跨度（注释明确"非单例时长/不承诺提速"，未测文件用用例数）做两桶整文件 LPT，确定性排序 → 两 child 各自独立 os-temp/basetemp/cache/report/PID 目录，`--key=value` 单 token 私有参数（即 62d4 修复点，见 §7 问题 6 的历史成因）。
- 计账 fail-closed：每预期 node 恰一 start/finish、setup→call→teardown 顺序与互斥（setup 非passed则不得有 call；teardown 需 setup 存在且一致）；未知事件/重复 phase/缺 phase/集合差异/跨 shard 重复/coverage 差额/child 非 0/输出流未关闭/双 session 边界/exitstatus≠0 全部判非绿；`unsettled/failed/error/teardown-skipped` 均为失败类（teardown-skip 边界为 422b 前初审 P2 的修复，guard 反证 3P+1teardown-skipped→parent 1 已核）；父进程信号→`128+signal` 非零退出。
- 进程治理：POSIX `start_new_session` + 组级 SIGINT→SIGTERM→SIGKILL，`group_alive` 检查与 `cleanup.jsonl` 落证，leader 死后组残留判错误；Windows `CREATE_NEW_PROCESS_GROUP` + CTRL_BREAK + `taskkill /T /F`，**launcher 退出后 descendants 明确记 "UNKNOWN after launcher exit; no job handle"**，不把 POSIX orphan guard 外推 Windows。
- child 身份：随机 owner + 真实 native pid/ppid 双通道记录（直接子进程或 native parent==launcher 的间接关系均可），修复了初审 P2"PID 硬等同"；`guard-native-redirector` 真实回单（launcher37290/native37291/parent37290）已入 O056。

**scripts/engine-test-reporting.py（125 行，全文实读）**：只读计账插件。collection manifest 含 13 字段 identity（rootpath/inipath/configSHA256/testpaths/pythonpath/addopts/executable/pytestVersion/platform/utf8Mode/三种编码）；shard 过滤在 `collection_modifyitems`（整文件集合、保序、deselected 走 hook）；`collection_finish` 时 shard 与全量 manifest 逐项＋identity 强相等，不等即 `UsageError` 非零退出——这是 422b"分离参数污染 pytest root/config 推断"资格失败（原件与撤销记录均保留）在 62d4 的最小修复面：仅改 `--key=value` 并显式记录实际配置 identity，不强塞 `-c/rootdir`、不改调用者原配置。

**ci.yml（164 行，全文实读）**：2 个 job 定义/3 个 runner 实例；Quality（ubuntu，15min）`npm run check` 挂 `CI_ENGINE_TEST_SHARDS='2'`；Desktop 矩阵 macos+windows（20min，`fail-fast:false`）；actions 全 SHA pinned；`npm ci`＋`uv sync --frozen`。Mac `engine:check` 无 SHARDS（默认 mode 1 原生）。Windows 诊断步保留原 `PYTEST_ADDOPTS='-vv --maxfail=1 --tb=short'` 仅追加 `--durations=20 --full-trace`（仅日志）；主 E2E 与全部 6 个 I04/packaged E2E 步骤补 `--reporter=list,github,json`＋`PLAYWRIGHT_JSON_OUTPUT_FILE` 唯一输出位（关闭初审 P2"末条 packaged native 漏 reporter"）；制品 `if: always()` 收 `build/engine-tests/`＋`test-results/`，`failure-traces-linux` 由 `failure()` 改 `always()`。未把本地 Linux global 540 注入 CI；worker/retry/超时/fixture/flags 未改（playwright.config 不在 98 叶差异内）。

**package.json**：仅 `engine:check` 末段 `uv run --frozen pytest` → `uv run --frozen python scripts/run-engine-tests.py`；其余字段/依赖/pre-hook 未变（O056 final-guards 已核，本人复核差异仅此一处）。

### 4.2 引擎核心（抽样深读＋定向检索）

- **rdf_snapshot.py（76 行全文）**：`term()` 只把 `BadSyntax/Notation3InputError` 转 `TermInputError`（确定拒绝），其余异常转**普通 ValueError** 不转 INVALID_REQUEST——未知 parser 失败保留 UNKNOWN/HOLD，与 D8 禁止"泛捕 ValueError 作业务分类"一致。`Literal(..., lang=...lower())` 只用于生成 canonical 比对值；配合 `domain_changesets.preview_changeset` 的 `parsed.n3() != value → INVALID_REQUEST`，实现"语法合法但非 canonical（如 de-CH-1901）受控拒绝、小写 canonical 可提交"的既采政策，**无静默规范化**（存储值即调用方精确字符串）。
- **domain_changesets.py（965 行全文）**：变更链 caller 项先 `iri()`/`term()` 定向 TermInputError 拒绝；`merge_plan/MetadataError/supported` 的窄类型捕获均来自自家校验器；undo 走 `impact()` 从实际历史投影（"never infer from error text"），conflict 产出 undo-impact 文档；`confirm()` 重放 cursor 链核验全文档遍历、重放 fresh preview 强等（确定性）、幂等重签走原 receipt 逐字段比对；孤儿 receipt 视为损坏拒绝重签。
- **mainline.py（1206 行全文）**：会话/授权/预算层。`READ_LIMITS.validation_bytes=1.5MiB` 有完整不变量注释（三份 420002B 历史字面量副本可入、仍在未变的 128MiB retained book 内、2MiB 会超、非 Q5 容量、无其他 cap 抬升）——与 D8"不扩容"一致，HELD_BYTES/HELD_OBJECTS/READ_WORK/MAX_REPLIES 未变。`project.ownership.detail`/ownership proof/写域 scope/失败后 unknown 保留等均闭环。
- **vendored rdflib fr201.3（补丁 136 行＋PROVENANCE 全读）**：六类已知输入失败类型化（相对基址、码点越界、未终结串×2、`^^` 缺 datatype URI、非法语言标签、裸整数超运行时限额——`sys.get_int_max_str_digits()` 原值 4300 保留，不写设置不抬限）；"no catch added; no message/cause/traceback classifier; no integer settings/cap/policy writes"; en-001/de-CH-1901 保留语法、由消费端 canonical 政策决定。upstream 7.6.0 轮＋LICENSE＋repack 回执＋172 新增/158 继承回归证据齐备，limitations 诚实（不含产品级验证、不关闭旧 45f64 Fail）。
- **D8 禁止项定向检索（本人 grep）**：产品路径无 `except Exception`→业务分类（`rdf_snapshot.term` 的 broad catch 显式重抛普通 ValueError 保留未知，例外即设计）；无按 `str(error)`/args 分支控制流（仅诊断/probe 记录）；`.lower()/.strip()` 仅出现于 canonical 派生与元数据非空校验，不作用于存储规范化。
- **渲染端**：`mainline-facts.ts`（编辑/删除保原 fact ID、新建用与 `Store.digest([S,P,O])` 一致的 SHA-256 canonical JSON 内容 ID、lone surrogate 拒绝、managed/重叠支持拒绝）、`mainline-ownership.ts`（只读分页消费者，契约级 `matchesOwnershipDetail` 校验、512 页上界、documentHash 绑定、fail-closed）。结构属性 copy 不冒未明确要求的独立实例事实 copy（无该动作，与 round-05 §2 结论一致）。
- **D8 定向测试（函数名级核对）**：`test_digit_subtags_are_grammatical_separate_from_canonical_case_policy`、`test_grammatical_uppercase_subtag_keeps_existing_canonical_rejection`、`test_non_input_failures_keep_original_unknown_and_hold`、`test_urlsplit_noncontract_failures_keep_unknown_and_hold`、`test_new_input_boundary_keeps_unclassified_parser_and_n3_unknown`、`test_reserved_original_identity_is_controlled_ownership_conflict`、`test_vendor_source_errors_have_dedicated_input_type`、`test_real_stdio_rejection_readback_and_canonical_confirm_job_marker`、`test_original_fact_id_survives_edit_and_undo`、`test_manual_ownership_detail_full_pages_then_original_id_job` 等，覆盖 D8 六项要求（拒前后 Read 不变、同 host 后继合法链、超长整数分类、非法语言标签、正控对照、HOLD 反例不回归）。
- **CSP（csp.ts 26 行全文）**：单一配置源；生产无 `unsafe-inline/unsafe-eval`（script-src 'self'、connect-src 'none'）；仅开发变体加 nonce script＋style unsafe-inline＋localhost connect，且 origin/nonce 有硬校验。

### 4.3 O056 证据本人复算结论

| 声明 | 本人复算结果 |
|---|---|
| COMPLETION 20220B/`bb8be59b…`、FINAL-MANIFEST 417088B/`914ce3f4…` | 一致；1692 针全部存在且哈希匹配，0 bad |
| check 自然 0/205.846s：Vitest 39 文件 1892P；engine 3769=3719P+50S+1 dup-ZIP warning；verify:sources 自然 0；PYTEST_ADDOPTS/PYTHONUTF8 null | 读回原件一致（stdout 末行 `3719 passed, 50 skipped, 1 warning in 183.53s`）；此为他人运行，本人未重跑 |
| mode2 原生 0/114.075s，配置 identity 全等 | 本人重算：full 3769 唯一；worker-1 1638 项/28 文件、worker-2 2131 项/29 文件、57 整文件；两 worker identity==full identity；exit 均 0、owned 均 true；starts==finishes；每 (node,phase) 恰一报；6 setup-skip（均无 call）、0 teardown-skip；计数 3719P+50S；coverage expected=reported=3769、missing/unexpected 空；summary errors=[]、passed=true；controlHashes==当前 HEAD 两脚本哈希；资格 identity 七字段==native-uv 基线 effective.json；root pyproject SHA `ed02773b…` 相等；`WindowsRemoteCIProven=false` 诚实保留 |
| native24：24 唯一=21P+3 原 I04 条件 skip；retry/flaky/unexpected 0；101 附件=100 body+1 引用；21 launch 全等且唯一新 profile | 本人独立展开 report.json：24 specs 全 ok、21 expected+3 skipped（I04 reload/coordinator-exit/native-renderer 三专项，需专用真实 fixture，主 E2E 内条件 skip 属实）、retry 全 0、附件 100 body+1 引用；21 个 launch body 解码后 expectedUserData==userData 全真、userData/sessionData 各 21 唯一、appPath 均本 S2、packaged 全 false |
| 24 条 Electron 退出=23×exit0/null＋PID50411 null/SIGKILL（csp-lifecycle finally 清理）；engine 自然码 UNKNOWN；controller cleanupActions=[] | 读回 COMPLETION 原件一致；本人不将其改写为"全 App 自然 0" |
| 三份独审、422b 资格撤销、guard 回单、nonce 三 build 仅 23 字节差异 | 均实读；初审两 P2 与 teardown-skip/POSIX 残留处置回单在案；422b"3769 自洽但配置不合格"原判保留未倒填 |
| 远端 develop=583、feature=9cb、PR16 open、62d4 未 push | 读回 O056 ls-remote 回单（2026-10-26T03:55Z）；本人未访问远端 |

## 5. 问题清单（本轮本人发现/核实）

| # | 严重级 | 位置 | 触发 | 影响 | 证据 | 建议 | 阻断性 |
|---|---|---|---|---|---|---|---|
| 1 | P1（合并门禁） | 本候选整体 | push→PR→CI 未发生 | 62d4 无任何真实远端 CI 证据；9cb CI40 的 Quality case7 ACK-loss 实际 FAIL（缺断言栈）与 Windows 3477/3769 结算后 292 未结算取消均未关闭 | ci.yml；O050/COMPLETION 远端记录；§4.3 | push 后以真实三 job 回单验收（见 §8 条件） | 阻断 merge，非源码缺陷 |
| 2 | P2 | run-engine-tests.py stop()/Windows | Windows launcher 退出后无法枚举后代（无 job handle） | Windows 残留清理不可证；两进程模式在真实 Windows 从未运行 | 代码注释"UNKNOWN after launcher exit"；guard 仅 POSIX orphan 实证 | Windows CI 首跑时核 build/engine-tests 内 cleanup.jsonl 与任务管理器证据；可评估 Job Object（另行开发，非本票） | 不阻断 push；Windows CI 验收项 |
| 3 | P2 | ci.yml concurrency（cancel-in-progress:true）＋Quality 15min | 强制取消或超时时上传步可能不执行 | `if: always()` 是语法不是保证，证据可能丢失 | ci.yml:10-12；历史 Quality 15m cancelled | 取消后以实际回单判断证据完整性；必要时票内延长 timeout（需授权） | 验收注意项 |
| 4 | P2 | Quality E2E ACK-loss case7（9cb run40252093380） | 原因未定（本地 O054/O055 未复现，缺栈） | CI 复发风险；复发时旧证据不足以定位 | 附件§五；O050 | 本次已补 github/json 结构化报告，复发时以结构化栈定因；不预判未来绿 | CI 验收项 |
| 5 | P2 | tests/unit/t01-mainline-contract.test.ts:656、t01-ontology-metadata-contract.test.ts:168 | Windows PATH 无 `python` 时 ENOENT 误失败 | 诊断噪音/误报；已知与 79F 归因无关 | 本人 grep 复核仍在 | 原测试 owner 下次授权改 `uv run`（历史处分保留） | 非阻断维护 |
| 6 | P2（已修复，保留成因记录） | run-engine-tests.py launch() 私有参数 | 422b 曾用分离 token，pytest 在 `-p` 插件加载前把现存路径参数当 test path，污染 root/config 推断（漏 S2 pyproject、nodeid 前缀漂移） | 曾致 mode2 资格失败（0/3769 自洽但不合格，撤销记录在案） | 422b-mode2-qualification-revocation.json；independent-final-validation-review.md | 62d4 已改 `--key=value`＋identity 记录，本版复算通过；未来新增私有参数沿用此形 | 已关闭 |
| 7 | P2 | 跨边界错误文案 | `INVALID_REQUEST{field:"params"}` 等 42 INVALID 内部分类无逐原因 UI 文案 | 用户可行动性有限（历史 Z F6 家族） | 领域代码固定码；R07 处分 | 对应方法接线前补针对性文案（归口不变） | 非阻断延期 |
| 8 | P2 | ci.yml | 无依赖漏洞扫描步骤（npm/uv audit 类） | 供应链风险仅靠 frozen 锁＋SHA pin 缓解 | ci.yml 全文 | 增设审计步或外部扫描票（新授权） | 非阻断；发布前建议 |
| 9 | P3 | ci.yml 制品 | `i04-package-linux` 与 `failure-traces-linux` 均 always 上传 `test-results/` | 重复上传，存储/时长小幅浪费 | ci.yml:97-113 | 合并或去重（纯 CI 卫生） | 非阻断 |
| 10 | P3 | 依赖治理 | vendored rdflib 偏离 upstream，无自动跟进上游安全修复机制；无月度升级节奏 | 供应链维护债（R07-12/MM09 处分保留） | PROVENANCE；R07 表 | 发布 owner 另票（HOLD 保留） | 非阻断；发布前 |
| 11 | P3 | 全局 | a11y/键盘导航/i18n UI 层、Undo GUI、四具名下游未验 | 发布级范围缺口（非本候选新增） | R07 处分；附件§六 | 各归口原窗口处理 | 范围外 HOLD |

未发现新的源码级 P1 缺陷；不为凑数发明问题。初审两 P2 已在 62d4 关闭并经本人在 §4.1/§4.3 复核（含 guard 真实回单读回）。

## 6. Top 10（按风险排序，含数据完整性/中断维度）

1. #1 远端 CI 未发生——唯一合并级阻断（数据完整性由 CI 全集逐项守门）。
2. #4 Quality case7 ACK-loss 原因未定——服务（CI）中断史中最可能复发且旧证据缺栈。
3. #2 Windows 后代清理 UNKNOWN＋两进程模式 Windows 零实测——平台验收最大未知。
4. #3 强制取消后 `always()` 上传不保证——证据链中断风险。
5. 旧 CI36 Windows 79F 逐例原因未知——新绿不得倒填；复发时无对照基线。
6. #5 两 TS 测试裸 PATH python——Windows 诊断噪音源。
7. #8 无依赖漏洞扫描——供应链暴露面盲区。
8. #7 42 INVALID 无逐原因 UI 文案——用户排障受阻（可行动性）。
9. #10 vendored rdflib 无上游安全跟进机制——长期供应链债。
10. #11 a11y/Undo GUI/四下游未验——发布级功能缺口（HOLD 范围）。

## 7. 历史意见逐项本版现状（R07 23 本轮位置＋55 历史位置，逐 ID 独立一行）

> 同轮补齐说明：本节由首自然稿的集合段扩展为 23＋55 逐行表；操作者已原样封存首自然稿（41108B / SHA256 `647c7e2819bdde53edadf71dd2f6ff0c5ed8d18689e241c86dd0bab41bb4d271`，与补齐前文件实测一致），本补齐不改变原结论、严重级与判定。逐行依据为本轮实读的 R07 DISPOSITION 原表（outputs/20261025_t02_b215f543_fresh_r07_048/resume-20261026-03/DISPOSITION.md）＋本版（62d4）本人实做核验；原文以 R07 处置表为准，此处为定位引用而非复制。62d4 相对 b215/9cb 零产品源码/测试/依赖改动，是多数"仍开/允许延期"的直接事实。

**23＋55 位置状态汇总（本人逐行统计）：关闭 20（本轮 6＋历史 14）／仍开 31（本轮 6＋历史 25）／未验 4（全为历史未确认观察）／允许延期 23（本轮 11＋历史 12）＝ 78。**

### 7.1 R07 本轮 22＋1 位置

| ID | 本版状态 | 直接事实 / R07 原处分定位 | 原归口/事件窗口 |
|---|---|---|---|
| Z F1 | 仍开 | 合并门禁维持：本地同版证据（O056 check/mode2/native24＋本人复算）与 fail-closed 控制层就绪，但 62d4 真实远端 CI 0 次；9cb CI 的 case7 FAIL 与 Windows 未结算按原件保留（本人读回 ls-remote：develop 583/feature 9cb） | ROOT 正常精确 CI 票；新 CI 后、merge 前接收 |
| Z F2 | 允许延期 | 62d4 新增两 .py 均受 Ruff 管辖、无新 raw 命名；"未发生的文件不是当前失败"维持 | T02/ROOT 将来新增 raw 命名或改规则时维护 |
| Z F3 | 允许延期 | 本版正面事实：两 CI 脚本全部 JSON 写入显式 `encoding="utf-8"`（write/cleanup.jsonl/events/collection.json.tmp 逐处本人核对），新代码侧合规；历史 20 默认 encoding 首参 ASCII JSON 窄结论维持不变 | 原测试 owner 下次授权触及该调用或环境适配时 |
| Z F4 | 关闭 | 事实修订已落（双分母 10/10＋12/12、额外 2 为 JSON+换行、全树 23 另计）；62d4 无 dumps 调用面变化（两脚本 json.dumps 写 UTF-8 文件不涉该分母），无待办 | 本次事实修订，无产品改动 |
| Z F5 | 仍开 | 两 TS 裸 PATH `python` 在位（本人 grep：t01-mainline-contract.test.ts:656、t01-ontology-metadata-contract.test.ts:168），与 79F 归因无关的定性维持 | T01 原测试维护者下次授权触及两测试或环境适配前 |
| Z F6 | 仍开 | 集合 OPEN 逐子项维持（definitions 早期 wire、裸 ownership、standalone EOF、缺码集合、无序未确认、应用 4299/4300 分别见 7.2–7.6 对应行）；62d4 零产品改动 | 原 owner／各接线或维护事件，非当前源码前置 |
| Z F7 | 仍开 | 发布 HOLD 群全部保留（本报告 §9 逐类具名） | 各原 owner 对应父 FR/发布/平台/容量验收前 |
| Z F8 | 仍开 | 受控 parser 分类仍限 BadSyntax/Notation3InputError＋vendor 六类型；rdf_snapshot 其余异常→普通 ValueError 未知分支在树（本人实读 44–45 行）；typed witness 与裸 detail 最终码均 OWNERSHIP_CONFLICT、裸族定位未全闭，定性维持 | 未知与新家族在相应接线前按原 HOLD 处理 |
| Z F9 | 允许延期 | 静态证据（参数化/标识符转义/隔离桥；固定 envelope 与有界 typed detail 分开）维持接收；本版未触及合同出口 | T01/T02 后续触及合同出口时核 |
| Z F10 | 关闭 | 既有 O047 证据接收维持（57 事务/43 拒绝/28 FR200 限原 GUI 路径），本版无重跑、无外推，无待办 | 本次既有证据接收 |
| MM R07-01 | 关闭 | 正面窄 literal 格式事实（7 tracked、lint/测试选择未变）；9cb→62d4 恰 4 叶差异直接印证测试选择未变，无待办 | 本次静态接收 |
| MM R07-02 | 允许延期 | 未发生的新 raw 文件仍不是当前失败，不预扩规则维持 | ROOT/T02 未来确增 raw 名字时 |
| MM R07-03 | 允许延期 | 不采当前统一整 reviews 排除维持；本版 round-08 目录仅新增本方报告，未改格式检查范围（不批量格式化归档） | 将来独立配置票才讨论，无当前动作 |
| MM R07-04 | 允许延期 | 状态源追加条件维持；本版唯一仓内写入为本方报告，未动中央状态文档（status.md/m0-checklist.md 不在 9cb→62d4 差异内且本审未改） | ROOT 指定文档 owner，未来证据归档票后、merge 前 |
| MM R07-05 | 允许延期 | AGENTS 为受保护未提交 overlay（本人复核 15147B/`de15f6ce…` 一致）；旧 M0 链接维护非候选新产品缺陷 | ROOT/指南 owner 未来授权维护时 |
| MM R07-06 | 关闭 | 双分母与 39/19/20 事实修订维持；本版无新运行，无待办 | 本次事实修订 |
| MM R07-07 | 允许延期 | 20 当前 ASCII JSON 窄结论（分布 13+5+1+1）维持；未来载荷变化时才需复核 | 原测试 owner，载荷变化时 |
| MM R07-08 | 允许延期 | 旧 map 条款＋笔段≠28 行 ledger 的粒度限定维持；28 笔 FR200 语义通过仍有效（层级/domain/range/type/五组 metadata 不后移）、附录 C 不扩（与 round-05 映射一致） | 整父 FR/具名下游由原 owner 另验 |
| MM R07-09 | 关闭 | 5build 中 4 exact、main 24 字符字段 23 实际异字节限定维持；本版沿用 O056 三 build 副本 nonce 证据（本人读回，未新构建），无待办 | 本次既有证据限定 |
| MM R07-10 | 关闭 | 计数事实＋差因未证维持（386−379=7 仅算术对账）；62d4 新增两 .py 使 py 基线自然 +2，未来计数以实际回单为准，本人不作新计数断言 | 本次事实修订，无新复跑票 |
| MM R07-11 | 允许延期 | 多值 manual edit 观察与原 ID 政策维持（mainline-facts.ts 本人实读：edits 保原 ID、managed/owner/sourceRow/重叠拒绝仍在） | T02/ROOT 未来 PR 说明可解释既有规则，不新改合同 |
| MM R07-12 | 仍开 | vendored parser 补丁/wheel 压缩差异事实维持（615416B DEFLATED upstream vs 2379774B STORED vendored 均在树，PROVENANCE 本人实读）；来源/法律/供应链 HOLD 保留；无新包制造 | 原 vendor/发布 owner，升级/发布前另票 |
| MM R07-13 | 允许延期 | TS 数字类型宽于 zod 的维护一致性维持；9cb→62d4 未触及 contracts（v2.ts 变化在更早提交，R07 时点观察仍适用），未证实际绕过不本票改源 | 契约 owner 下次授权整理类型时 |

### 7.2 R06 Zcode P1–P8

| ID | 本版状态 | 直接事实 / R07 原处分定位 | 原归口/事件窗口 |
|---|---|---|---|
| R06 Z P1 | 仍开 | 新 head Windows 完整缺证维持（62d4 未 push）；旧 CI36 79F 全因未证保留，不追认、不补造 | 合并前真实 CI 门禁；ROOT 正常精确票 |
| R06 Z P2 | 允许延期 | 诊断参数不能凭标签判绿/否认的口径维持；ROOT 显式全集口径已由 62d4 控制层在本地机制化（fail-closed 计账），Windows 实际回单未验 | 未来 CI 证据接收标准（已并入 §8 条件） |
| R06 Z P3 | 仍开 | definitions 早期坏 wire（preview 内 Store 校验未分类异常→UNKNOWN/HOLD）维持；62d4 未触及 | T01 核心维护；原始 triples/Agent 接线前 |
| R06 Z P4 | 仍开 | ownership 通用定位（typed 有 witness、裸旧 detail INVALID_STATE→unavailable；两分支最终均 OWNERSHIP_CONFLICT）维持 | T01 详情合同＋T02 消费；新增相应家族接线前 |
| R06 Z P5 | 仍开 | 错误码集合差（UI17/契约26/交集10/额外7/缺16）事实维持；16 条当前可达性未证、不泛加白名单 | T01 契约＋T02 方法出口；对应方法接线前核对 |
| R06 Z P6 | 未验 | SQL 无 ORDER BY 事实保留；无稳定排序合同或构造性反例，维持"未确认观察"不升级 | T01 Store 维护；下次触及 witness 选取时 |
| R06 Z P7 | 关闭 | canonical 既有精确 term(value).n3() 政策延续并本人实读在位（en-001/de-ch 正控与混合大小写受控拒绝分开）；Q6 已决不重问 | 无待办；未来改政策才新人类决定 |
| R06 Z P8 | 允许延期 | 集合标题已拆解至各单行，由 7.2–7.6 逐行承接；行数不推正确性维持 | 各原归口 |

### 7.3 R06 MiniMax D1–D12

| ID | 本版状态 | 直接事实 / R07 原处分定位 | 原归口/事件窗口 |
|---|---|---|---|
| R06 D1 | 仍开 | 62d4 无新 CI 维持；"整个 base→head 无 push 前技术阻断"判断本版延续（本人未发现新源码缺陷） | ROOT 正常票；新 CI 后合并前核 |
| R06 D2 | 允许延期 | 状态/历史 manifest 追加走归档票；历史 aff/8318 manifest 永久绑定原候选不改写 | ROOT 指定唯一文档维护者，归档票后追加 |
| R06 D3 | 仍开 | definitions 时序定性维持（preview 内先抛，非 confirm 后）；早期坏 wire→UNKNOWN/HOLD 继续 OPEN | T01 原归口；原始 wire/Agent 接线前 |
| R06 D4 | 仍开 | ownership 最终码两分支均 OWNERSHIP_CONFLICT 维持；缺键只在逃出包装条件下相关、不外推 | T01＋T02；随对应家族接线处理 |
| R06 D5 | 未验 | 无序查询不因标题宣称已实测；SQL 事实＋未确认观察维持 | 同 Z P6；T01 下次触及选取时维护 |
| R06 D6 | 仍开 | standalone EOF 两处裸索引的类型化守卫在树（本人实读补丁 `j == len_argstr` 与 `j < 0` 分支）；`. `封装与无构造反例维持"未证形式不可达"，不能写已修或无风险 | T02 vendor 补丁/T01 入口；新增不经现封装解析入口前复核 |
| R06 D7 | 仍开 | 缺 16 码集合事实成立、不等于当前可达缺陷，维持 | 同 Z P5；T01/T02 对应方法接线前 |
| R06 D8 | 仍开 | 两 TS PATH python 代码仍在（本人 grep 复核两处在位）；报告更正≠源码修复维持；O035 ENOENT 与正确 UV 调用并存 | T01 原测试维护者；下次授权触及或环境适配前 |
| R06 D9 | 允许延期 | Ruff 369/379/380/386 各时点计数原件保留、差因不结论；本版不新增计数断言 | 文档唯一维护者，归档票后追加 |
| R06 D10 | 允许延期 | D/E/G 映射与四具名下游（GUI 编辑→推导/保存查询/SHACL/报告）未逐类实测维持；公共失效规则、同事务版本/stale/current 与九行正负例证据维持，两分不抹 | T01 公共失效＋T02 编辑与各下游 owner；父 FR/消费链验收前 |
| R06 D11 | 允许延期 | 应用层 4299/4300 边界断言未加（未来最小维护）；4301 拒绝与合法后继实证维持；本版未触及整数守卫（vendor 4300 限额原样保留，本人实读补丁） | T02 输入边界；下次授权触及整数守卫时 |
| R06 D12 | 关闭 | 正面结论（六 keyword AST、既有本地运行、旧包身份）按原资格保留、不外推全平台/法律；供应链哈希与体积计量分层维持 | 已完成证据与独立 HOLD 分别保留，无待办 |

### 7.4 R04 Z01–Z07 / M01–M07

| ID | 本版状态 | 直接事实 / R07 原处分定位 | 原归口/事件窗口 |
|---|---|---|---|
| R04 Z01 | 未验 | 无序查询观察未确认；同 D5/Z P6 维持 | T01 下次触及 witness 选取 |
| R04 Z02 | 关闭 | 43692 分页信封误因果已撤回；262144 整文档/16MiB 预算边界另保原行，不复活已撤回缺陷 | T01 详情预算下次授权维护 |
| R04 Z03 | 仍开 | definitions 早期 wire OPEN；同 D3 维持 | T01；原始 triples/Agent 接线前 |
| R04 Z04 | 仍开 | typed witness/裸旧 detail 分开；同 D4 维持 | T01/T02；对应家族接线前 |
| R04 Z05 | 仍开 | 集合差与可达性分开；同 D7/Z P5 维持 | T01/T02；对应方法接线前 |
| R04 Z06 | 关闭 | 既有 canonical 政策继续；同 Z P7（本版实读政策在位） | 无待办；改政策才新决定 |
| R04 Z07 | 关闭 | 2993/1887/1748 规模信息接收，不新增重构、不据 LOC 推正确性 | 无待办 |
| R04 M01 | 关闭 | "原归档待 ROOT→最终状态追加"为历史演进非矛盾；62d4 当前节由本 R08 与后续归档票处理 | ROOT 归档票 |
| R04 M02 | 关闭 | 不采无 hash 前提；uv/PROVENANCE 哈希与 .1/.2/upstream 审计件在树（98 叶差异含四轮 wheel，本人未删改） | 无待办 |
| R04 M03 | 允许延期 | 4299/4300 未来维护；同 D11 维持 | T02；下次授权触及整数守卫时 |
| R04 M04 | 仍开 | standalone 残余 OPEN、未证当前 UI 可达；同 D6 维持（类型化守卫在树、不可达性未证） | T02 vendor/T01 入口；新增入口前复核 |
| R04 M05 | 仍开 | 早期 definitions 不受后置 catch 覆盖；同 D3 维持 | T01；原始 wire 接线前 |
| R04 M06 | 关闭 | schema 形状与 Store 内容身份分层维持；真实双端 ID 校验/原 ID edit 证据在位（mainline-facts.ts 本人实读），非当前绕过漏洞 | 无待办 |
| R04 M07 | 允许延期 | 桶导出兼容信息、未证冲突、不直接缩导出面维持 | 契约 owner 下次 API 整理时评估 |

### 7.5 R05 Zcode P1–P8

| ID | 本版状态 | 直接事实 / R07 原处分定位 | 原归口/事件窗口 |
|---|---|---|---|
| R05 Z P1 | 仍开 | O040 首败定因不追认旧 79 全因维持；62d4 完整 Windows 仍缺（本版新增：控制层就绪但未实测，不冒充已验） | ROOT 合并门禁 |
| R05 Z P2 | 关闭 | 934 Quality 718s（含 packaged recovery 成功）为新阶段历史证据保留、旧 CI36 取消留历史、不迁移成任何新 head CI 绿——定性维持，无待办 | 无待办（历史证据归档） |
| R05 Z P3 | 仍开 | 早期 definitions OPEN；同 D3 维持 | T01；接线前 |
| R05 Z P4 | 仍开 | 通用定位合同 OPEN；同 D4 维持 | T01/T02；家族接线前 |
| R05 Z P5 | 仍开 | 缺 16 按出口延期；同 D7 维持 | T01/T02；方法接线前 |
| R05 Z P6 | 关闭 | canonical 语义观察接收、不新增当前批准；政策不变（本版实读在位） | 无待办 |
| R05 Z P7 | 关闭 | 诊断选项演变事实接收；全集口径已由 ROOT 显式并入门禁（§8），不为标签自动验收或强制改配置 | 无待办 |
| R05 Z P8 | 允许延期 | 历史 aff 状态永久保留；当前时点追加走归档票（同 D2） | ROOT 文档 owner，归档票后 |

### 7.6 R05 MiniMax MM01–MM13

| ID | 本版状态 | 直接事实 / R07 原处分定位 | 原归口/事件窗口 |
|---|---|---|---|
| R05 MM01 | 仍开 | 首败假设被 O040 一个真实栈部分超越、旧 79 全部原因仍未知；新 CI 门禁保留 | ROOT；新 CI 后合并前核 |
| R05 MM02 | 仍开 | 934 两 success/Windows failure 为新阶段事实、旧两 cancelled 不抹除；62d4 待新 CI | ROOT/新 CI 后 |
| R05 MM03 | 允许延期 | 无新包维持；旧 094 仅原有界桥接（本版仅读回 root 0755 守卫记录，未重扫 912 成员） | 无新包制造票 |
| R05 MM04 | 允许延期 | 当前入口追加与原 Ruff 差因未知分别承接；同 D2/D9 | ROOT 文档 owner，归档票后 |
| R05 MM05 | 仍开 | 缺码非阻断延期；同 D7/Z P5 | T01/T02；方法接线前 |
| R05 MM06 | 仍开 | definitions 早期 OPEN、不采晚确认分歧；同 D3 | T01；接线前 |
| R05 MM07 | 仍开 | Manual/SingleDeclaration 真 witness 与裸族分开；同 D4 | T01/T02；家族接线前 |
| R05 MM08 | 未验 | SQL 事实维持未确认观察；同 D5/Z P6 | T01 下次触及选取时 |
| R05 MM09 | 允许延期 | 整 wheel/payload/解压量及压缩方式分层维持；历史 vendor 原件保留（PROVENANCE 本人实读未变） | vendor/发布 owner |
| R05 MM10 | 关闭 | AGENTS 为受保护未提交 overlay、链接维护非候选缺陷维持（本人复核哈希一致） | 无待办 |
| R05 MM11 | 关闭 | locator 无 object 是最小定位信息边界、不新增显示需求维持 | 无待办 |
| R05 MM12 | 仍开 | 两 TS 仍 PATH python；同 D8（本人 grep 复核在位） | T01 原测试维护者 |
| R05 MM13 | 关闭 | 核心规模信息接收、不据 LOC 推正确性维持 | 无待办 |

### 7.7 逐行核对方式与边界

以上 78 行逐 ID 独立成行，均对照 R07 DISPOSITION 原表逐行作出（非集合替代）；"直接事实"列中标注本人实做（grep/实读/复算）处为 62d4 新核验，其余为 R07 原处分定位引用。本版未发现任何一项被 62d4 关闭（除 Z F3 新脚本侧合规、Z F4/MM06/MM09/MM10 类事实修订本就无待办、R06 Z P7/R04 Z06/R05 Z P6 政策类原已闭合）或加重；CI 类位置（F1/P1/P2/D1/R05P1/MM01/MM02）统一为"本地证据推进、远端 0 次、门禁不变"。

## 8. 整候选最终判断

- **本地实现：通过**（在本人实读＋O056 同版证据范围内）。FR-200/201 引擎/契约/渲染实现自 R07 以来零变化；9cb→62d4 仅 CI 控制层，其设计（原生保持、fail-closed 计账、配置 identity 强一致、诚实 UNKNOWN）经代码实读、guard 反证回单与本人独立复算核实。
- **本地验收：通过**（同版 62d4：完整 check 1892+3769（3719P/50 有据 skip/1 原 warning）、mode2 配置一致全集合、native24 21P+3 有据 I04 条件 skip、verify:sources；均为他人真实运行＋本人读回复算，非本人重跑）。
- **有无 push 前源码技术阻断：无**（本人未发现新的源码缺陷；初审两 P2 已关闭；#5 等为非阻断维护）。
- **整候选结论：附条件通过（Conditional Pass）**。merge 必须等待 push 后真实 CI 同时满足：① Windows 完整 3769 每项最终 PASS 或原有有据 skip、自然 0、无失败/早停/取消/timeout/NOTRUN（mode2 每 child maxfail1 早停时缺失/失败必须 parent 非 0——控制层已保证，验收仍看实际回单）；② 其后 typecheck/build/E2E/package/verify 及原 3 job 实际 success；③ Quality 专用（I04 三专项用真实 fixture 步骤自身 success）与 packaged recovery 步骤自身 success；④ case7 不复发，或复发时以新增结构化报告定因并处置；⑤ ROOT 接收双 R08 与全部意见处分。未来 CI 未知不预判为绿，也不定性为源码缺陷；旧 79F 不倒填。
- 正常顺序不变：本地验证→同版 fresh 双审/全部意见处分→ROOT 接收→push→PR/CI→merge/remote。本审无远端权限、无新增人类诊断例外前置。

## 9. 独立 HOLD（全部保留，不因本审消解）

签名/公证/wholeApp 法律与 `_distutils`；全平台/目标 macOS15 与 Windows11/参考设备/旧设备；Q5/D2 容量及旧超限库恢复；损坏 SQLite 物理资源保护（用户明确保留）；unknown parser/N3/Store/坏快照家族；Undo GUI 未验/未验 ownership 家族/附录 D.2 四具名下游（GUI 编辑后推导/保存查询/SHACL/报告）；native engine 及 named App 未知退出码；Windows 后代回收 UNKNOWN；模型网关（S3 前不接入）及相关凭据/花费 cap；组织/产权/隐私/法律事项（代码不能证明免责，标注无法确认而非不适用取消义务）。仍 2/17（FR401/402），非整个 Goal/M0/发布完成。旧 094 包 912 基线仅原有界桥接；FullRead 相等不证物理 DB 零写；已知 PID 缺席不证全部自然 0。

## 10. 用户原清单 1–160 逐项判定

图例：判定=适用已满足/适用部分/本轮范围外/不适用/无法确认。依据均为本轮实读/复算或其引用的已核证据；"本地优先桌面应用（Electron+Python stdio、无 HTTP 端口、无多租户、无支付、无云）"是多数不适用项的共同前提（PRD/AGENTS 不变量＋代码结构）。

| # | 条目（缩写） | 判定 | 依据/缺口 |
|---|---|---|---|
| 1 | 先设计 schema 非逐表即兴 | 适用已满足 | contracts v2 schema/zod `.strict()`＋python contract_v2 双端；PRD 附录 C 枚举；ADR-0002 |
| 2 | 邮箱带+登录 | 不适用 | 无登录/邮箱（本地优先单用户） |
| 3 | 重置链接过期一次性 | 不适用 | 同上 |
| 4 | MFA＋找回 | 不适用 | 同上 |
| 5 | 会话超时/杀会话 | 不适用（内部已 fencing） | 引擎 session/generation/replies 生命周期＋中断 fail-closed；无远程用户会话 |
| 6 | SSO | 不适用 | 无企业客户面 |
| 7 | SAML | 不适用 | 同上 |
| 8 | SCIM | 不适用 | 同上 |
| 9 | 深于 admin 的角色 | 不适用（内部权限已实现） | 引擎 permission/ownership proof/PERMISSION_DENIED 体系；无用户角色 UI 需求 |
| 10 | 改数字读他人数据 | 不适用 | 无跨用户；projectId 授权＋ownership proof 校验在位 |
| 11 | 租户隔离 | 不适用 | 单用户本地 |
| 12 | admin 代登 | 不适用 | — |
| 13 | 登录限速 | 不适用 | — |
| 14 | 锁定不误伤 | 不适用 | — |
| 15 | 迁移可前进可回滚 | 适用已满足 | storage format0→v3 迁移逻辑（44 条件 skip 即真实迁移分支）；版本化 Store.commit＋undo/compensation |
| 16 | 迁移不锁主表 | 无法确认（设计上无此争用） | 单连接本地 SQLite；未测量锁行为 |
| 17 | 索引扛 5M 行 | 无法确认（HOLD） | 预算/工作上限保护；Q5 容量未验 |
| 18 | 连接池 | 不适用 | ADR-0002 单连接设计 |
| 19 | 每夜备份 | 适用部分 | 不可变快照/版本历史≠异地备份；无备份调度功能 |
| 20 | 恢复演练 | 适用部分 | undo/补偿已测；整库恢复未测（损坏 SQLite HOLD） |
| 21 | PITR | 本轮范围外 | 版本化修订提供时点状态；无外部 PITR 需求 |
| 22 | 软删除 | 适用已满足 | 墓碑/retirements 保留 provenance；undo impact 逐资源 |
| 23 | 服务端校验 | 适用已满足 | 引擎端 contract_v2/Store 校验；renderer 不被信任 |
| 24 | 时区存储 | 适用部分 | 日期为 canonical RDF 字面量；无本地时区换算/提醒调度 |
| 25 | 姓氏撇号 | 适用已满足 | zh/en 标签/空格保留实证（round-05）；SQL 标识符转义 |
| 26 | emoji/重音/RTL | 适用部分 | Unicode 字面量族已测、lone surrogate 拒绝、UTF-8 显式；RTL 未专项测 |
| 27 | 金额存整数 | 不适用 | 本产品无金额（计算器为另一项目） |
| 28 | 币种/舍入/税 | 不适用 | 同上 |
| 29 | 数据模型抗二客户变更 | 适用部分 | 分层 schema＋版本化契约；未来适配无法预证 |
| 30 | 幂等键 | 适用已满足 | operationId/operation_claims、INSERT OR IGNORE＋accepted 重放逐字段核验、confirm 幂等 receipt |
| 31 | 四连击去重 | 适用已满足 | 内容派生 ID＋FACT_ALREADY_EXISTS＋Store 冲突；操作声明去重 |
| 32 | 第 400 页分页 | 适用部分 | cursor 链完整性校验（confirm 全遍历重放）；400 页未专项测 |
| 33 | 导出表格 | 本轮范围外 | FR-203 Turtle 导出另列（拒绝超范围构造） |
| 34 | 2009 CSV 导入 | 不适用 | 导入为 Turtle 受控拒绝策略 |
| 35 | 保留期规则 | 本轮范围外 | 历史不可改写设计；无保留合同义务面 |
| 36 | 密钥不入代码 | 适用已满足 | 本人 grep 源码无凭据模式；S3 前无网关无密钥；AGENTS 禁提交 |
| 37 | 轮换 AI 粘贴的密钥 | 不适用（前置） | 尚无密钥；未来 S3 凭据模块 HOLD |
| 38 | 依赖确系所愿 | 适用已满足 | vendored rdflib 双轮＋SHA pin＋PROVENANCE；frozen 锁；CI npm ci/uv sync --frozen |
| 39 | 依赖扫描 | 适用部分（缺口） | 无自动扫描步（问题 #8）；靠 pin/frozen 缓解 |
| 40 | 输入净化 | 适用已满足 | 契约 strict 校验＋类型化拒绝；无原始 HTML 注入面 |
| 41 | SQLi/XSS/CSRF/OWASP | 适用已满足 | 参数化 SQL（标识符来自 sqlite_master 并转义）；CSP 生产无 unsafe-*（本人实读 csp.ts）；无 HTTP 面故无 CSRF/CORS 面 |
| 42 | 上传扫描 | 不适用 | 本域无上传 |
| 43 | CORS | 不适用 | 无 HTTP 服务（connect-src 'none'） |
| 44 | 每响应安全头 | 适用部分 | CSP 即桌面等价物且单源；无 HTTP 响应 |
| 45 | 静态/传输加密 | 本轮范围外（HOLD） | 本地 SQLite 明文为既定本地优先设计；stdio 本机；未来云接入另议 |
| 46 | 最小权限（含 AI） | 适用已满足 | Agent 只草稿＋白名单工具、不得自确认（confirm 需人工 cursor 链）；引擎级 PERMISSION_DENIED 密集校验 |
| 47 | 日志不记密钥 | 适用已满足 | 跨边界固定错误码＋受限参数；无凭据可泄 |
| 48 | 渗透测试 | 无法确认（未做） | 发布前 HOLD |
| 49 | 安全问卷 | 本轮范围外 | 无企业买家面 |
| 50 | 漏洞披露流程 | 本轮范围外 | 未建立 |
| 51 | 电脑被盗预案 | 本轮范围外 | 未建立 |
| 52 | SOC 2 | 本轮范围外 | — |
| 53 | HIPAA | 不适用 | 无患者数据 |
| 54 | BAA | 不适用 | — |
| 55 | 审计"谁看过" | 适用部分 | 写操作不可改账本（jobs/commits/receipts/actor）；读操作未全量审计 |
| 56 | PCI | 不适用 | 无卡数据 |
| 57 | GDPR 删除 | 本轮范围外 | 本地数据自持；无控制者处理面 |
| 58 | 数据驻留 | 不适用 | 纯本地 |
| 59 | 季度访问评审 | 不适用 | 单用户 |
| 60 | 三环境一致 | 适用部分 | CI 三 OS 同套检查＋frozen 锁；无 staging/prod 环境 |
| 61 | IaC | 本轮范围外 | 无基础设施；CI yml 入库 |
| 62 | 部署先跑测试 | 适用已满足（门禁设计） | check 为构建/打包前置；merge 另需真实 CI（问题 #1） |
| 63 | 一键回滚 | 适用部分 | 数据层 undo/补偿已测；应用发布回滚无部署系统 |
| 64 | 零停机 | 不适用 | 本地桌面 |
| 65 | 功能开关 | 本轮范围外 | 以迭代/能力域控制范围 |
| 66 | 自动扩缩 | 不适用 | — |
| 67 | CDN | 不适用 | — |
| 68 | DNS/SSL | 不适用 | — |
| 69 | 后台任务队列 | 适用已满足 | JobStore 持久任务＋重启恢复（I04 全链路验收在树） |
| 70 | 重试退避 | 适用部分 | 重启 reconcile 幂等；无网络调用故无网络退避面 |
| 71 | 死信队列 | 适用部分 | failed/cancelled 终态持久保留可查 |
| 72 | cron 双跑 | 不适用 | 单实例 |
| 73 | 缓存失效 | 适用已满足 | invalidation-v2 唯一源 staleReason；图只从不可变快照重建；附录 D.2 公共机制＋正负例（具名下游 GUI 未逐类验） |
| 74 | SPF/DKIM/DMARC | 不适用 | 无邮件 |
| 75 | 退信处理 | 不适用 | — |
| 76 | 临时文件存储规则 | 适用部分 | 每 run 独立 os-temp/basetemp/cache＋清理 guard；应用级存储策略未定 |
| 77 | 成本告警 | 本轮范围外 | 本地无按量成本；未来模型网关 cap HOLD |
| 78 | DR 演练 | 本轮范围外 | — |
| 79 | 第二区域 | 不适用 | — |
| 80 | 3am 可查结构化日志 | 适用部分 | events.jsonl/manifests 结构化；无集中检索（本地） |
| 81 | 错误聚合 | 本轮范围外 | — |
| 82 | 外部拨测 | 不适用 | 无服务 |
| 83 | 告警调优 | 不适用 | — |
| 84 | 仪表盘 | 不适用 | — |
| 85 | 跨服务追踪 | 适用部分 | 操作 marker/receipt 因果链完整；无分布式服务 |
| 86 | on-call | 不适用 | — |
| 87 | runbook | 本轮范围外 | ADR/状态文档在；无运维 runbook 需求 |
| 88 | 复盘改变事物 | 适用已满足 | R01–R08 评审轮＋逐意见处置即制度化复盘（如本票 CI 资格失败→修复→复验） |
| 89 | 状态页 | 不适用 | — |
| 90 | 懂逻辑者写单测 | 适用已满足 | 3719+1892 语义断言（完整预期集合/顺序）；本轮本人对证据的独立复算再校验 |
| 91 | 三方 API 集成测试 | 不适用（有等价物） | 唯一三方库 vendored 且带 172+158 回归带外证据 |
| 92 | 关键流程 E2E | 适用已满足 | native24（21P/3 有据 skip）；CSP/恢复/ACK-loss/T02 六例在册 |
| 93 | 上线前压测 | 本轮范围外（HOLD） | 容量 Q5/D2 未验 |
| 94 | 仿真测试数据 | 适用部分 | 真实样例工程（t01-provider hash 钉定）＋I04 fixture 生成器；无生产数据 |
| 95 | 回归测试防复活 | 适用已满足 | binding-regressions.json＋每轮定向拒绝测试；本轮 grep 复核 D8 禁止项未回归 |
| 96 | 旧设备测试 | 无法确认（HOLD） | 仅 macOS arm64 实测；目标平台/参考设备未验 |
| 97 | 无障碍合规 | 本轮范围外 | 未验（发布前需处置） |
| 98 | 订阅/升降级/按比例 | 不适用 | — |
| 99 | 催扣重试 | 不适用 | — |
| 100 | 带 PO 发票 | 不适用 | — |
| 101 | 销售税 VAT | 不适用 | — |
| 102 | 退款/部分退款 | 不适用 | — |
| 103 | 计量对账 | 不适用 | — |
| 104 | 年度定制合同 | 不适用 | — |
| 105 | 财务对账报表 | 不适用 | — |
| 106 | webhook 验签 | 不适用 | — |
| 107 | webhook 重试留痕 | 不适用 | — |
| 108 | 版本化 API | 适用已满足 | contracts v2 版本化＋业务命名 IPC；schema/fixture/registry 同步演进 |
| 109 | API key 创建/吊销 | 不适用 | 无外部 API |
| 110 | API 限速 | 适用部分（内部等价） | frame/page/work/内存预算保护引擎；无外部 API 面 |
| 111 | 三方 API 变格式预案 | 不适用（结构性缓解） | rdflib vendored＋hash 钉定，升级自主可控 |
| 112 | OAuth 刷新 | 不适用 | — |
| 113 | 集成沙箱 | 不适用 | — |
| 114 | 提示注入防护 | 本轮范围外（设计已隔离） | S3 前无模型 I/O；Agent 白名单/不自确认不变量在位 |
| 115 | 敏感数据不进提示 | 本轮范围外 | 同上；本地优先无外发 |
| 116 | 按客户模型花费上限 | 本轮范围外（HOLD） | S3 网关未建 |
| 117 | 模型评测 | 本轮范围外 | — |
| 118 | 模型降级兜底 | 本轮范围外 | — |
| 119 | 模型弃用迁移 | 本轮范围外 | vendored rdflib 缓解库侧；模型侧 N/A |
| 120 | 提示/输出日志 | 本轮范围外 | — |
| 121 | AI 不可逆操作人工批准 | 适用已满足 | Agent 不得自动确认；changeset confirm 需人工完成全文档 cursor 链＋真人确认；权限 actor/permission 落账 |
| 122 | 酒店WiFi能开 | 不适用 | 纯本地 |
| 123 | 空/载/错状态 | 适用部分 | 固定错误码→explainError；逐屏穷尽未验 |
| 124 | 可行动错误信息 | 适用部分 | 见问题 #7；42 INVALID 无逐原因文案 |
| 125 | 校验失败保留输入 | 无法确认 | preview/confirm 流有完整 before/after；表单字段级保留未专项验 |
| 126 | 邮件客户端渲染 | 不适用 | — |
| 127 | 通知可关 | 不适用 | 无通知系统 |
| 128 | undo | 适用部分 | 引擎 undo/impact 已测＋UI 入口在；Undo GUI 未 E2E 验（HOLD） |
| 129 | 键盘导航/读屏 | 本轮范围外 | 未验 |
| 130 | 翻译/本地化格式 | 适用部分 | 本体元数据 zh/en 已验；应用 UI i18n 不在本域 |
| 131 | 返回键符合预期 | 无法确认 | 桌面导航未验 |
| 132 | 人能读的代码 | 适用已满足 | 抽样模块文档密度高、职责注释清晰（mainline/domain_changesets/rdf_snapshot/两 CI 脚本） |
| 133 | 每变更代码审查 | 适用已满足 | R01–R08 指定双模型独立审查＋独立处置审计（本报告即一环） |
| 134 | 分支策略 | 适用已满足 | 独立 worktree＋feature 分支＋PR 门禁（AGENTS §5；本 worktree 实践一致） |
| 135 | 月度依赖升级 | 无法确认（未建立） | frozen 为刻意稳定策略；无升级节奏 |
| 136 | 框架 EOL 前升级 | 无法确认 | Electron 版本策略本轮未核 |
| 137 | 删 AI 死代码 | 适用部分 | 评审归档完整；fr201.1/.2 旧轮保留为审计链（刻意，非死码遗留） |
| 138 | 拆 2000 行文件 | 适用部分 | job_store 2993/storage 1887/e2e 1748 行大但模块化；信息项不强制重构 |
| 139 | 架构决策留痕 | 适用已满足 | ADR-0001/0002/0003＋迭代目录＋PROVENANCE＋处置表 |
| 140 | README 1 小时上手 | 无法确认 | 有 AGENTS 地图/文档；无人上手时长实测 |
| 141 | 交接文档 | 适用部分 | docs/reviews 全链可追溯；无专门交接手册 |
| 142 | 运维后台 | 不适用 | — |
| 143 | 客服工具 | 不适用 | — |
| 144 | 客户可读 changelog | 本轮范围外 | status/rounds 为内部变更记录；尚无客户面 |
| 145 | 条款/隐私与代码一致 | 无法确认 | 法律文本不在本域；本地优先数据行为已在 PRD 声明；组织义务不因此取消 |
| 146 | 资产在公司名下 | 无法确认 | 组织/产权事项，代码不可证 |
| 147 | bus factor>1 | 无法确认（实际=1 风险） | 流程有多 AI 审查者，人类负责人单一（创始人）——明示风险 |
| 148 | 高级工程师逐行读 | 适用部分 | 双独立 AI 审查＋本人逐行抽样；不冒充人类 senior 逐行签字（历史边界维持） |
| 149 | 后端工程师设计数据模型 | 适用部分 | ADR-0002＋分层契约先于实现 |
| 150 | 解释 AI 修一坏二 | 适用部分 | 对抗性双审＋每轮回归测试即此职能的制度化 |
| 151 | DevOps | 适用部分 | CI 三平台管道在维护；无生产运维面 |
| 152 | 3am 值班 | 不适用 | — |
| 153 | 漏洞周内补框架 | 适用部分 | pin/frozen 缩小暴露；无漏洞监测节奏（问题 #10） |
| 154 | 审计员导览 | 不适用 | 无合规审计面 |
| 155 | QA 验 AI 所测 | 适用已满足 | 本轮即为独立复算（1692 针/mode2/native24/identity 全部本人重算非转述）；ROOT 另有独核 |
| 156 | 活库迁移不丢行 | 适用部分 | 真实 DB 迁移分支在套件（44 条件 skip 即其证据面）；大规模活库未验 |
| 157 | 技术负责人说不 | 适用已满足 | 范围纪律可证（FR 边界、D8 最小修复、拒绝范围后移/扩容） |
| 158 | 架构师扛全体客户 | 本轮范围外 | 单用户本地；规模化 HOLD |
| 159 | AI 修不了时人调试 | 适用部分 | 原始流保全＋资格失败撤销等诚实记录支撑人类介入；无长期实证 |
| 160 | 一年后记得为何如此 | 适用已满足 | ADR/处置表/不可变评审档案＋本报告链 |

统计（2026-10-26 对上表判定列的一次纯计算复核：160 行无缺号无重复、全部可归类）：**适用已满足 29、适用部分 32、本轮范围外 27（多为 S3/发布/运维前置项）、不适用 60（本地优先单用户桌面前提）、无法确认 12（均给出缺口而非假装检查），合计 160**；与操作者复核计数一致，首稿"≈30/26/33/60/11"为估计值、就此作废，各行判定本身未改动。未为凑数增加无用功能；适用整个产品但非本 T02 覆盖的项按"本轮范围外/HOLD"标注而非改判不适用。

## 11. 范围边界收尾

本报告只读审查整个 base583→62d4（不只 CI 两脚本），未预设通过；所有"通过"均限定在 §2 声明的本人实读＋他人同版真实证据＋本人复算范围内。历史失败（9cb CI case7 FAIL/Windows 292 未结算、CI36 79F、330 FORMAT 首败、934 cp1252、422b ENOENT 与资格失败）按原版本保留，未被新证据覆盖或倒填。Top10 未省略任何阻断（#1 即门禁本身）。真阻断（#1）未被降级；非阻断建议均给依据与归口，不为修辞无限往返。

---

## 12. 同轮事实补充 v1.1（2026-10-26；输入＝controller 共享事实与证据边界文件）

### 12.0 输入核验与写作边界

- 输入文件 `iteration-control/2026-10-21-weekly-release/six-patches-20261023/controller-t02-62d4b0a2-r08-shared-evidence-boundaries-20261026.md` 本人核验 7917B / SHA256 `e549fa97ca1f5a2af0c30bee8f7cd14ff3e143d65ccc594dcc7f79c3cea23cb9` 一致并完整读取。"两位作者收到完全相同的此文件及此消息"为操作者陈述，模型本人无法核验对方收件。
- 本节只**追加**：§1–11 原文、160 行表、78 位置表、统计行、Top10 与结论均不覆盖不改写；本节给出受影响条目的 v1.1 更新评估。首自然稿（41108B/`647c7e28…`）与 §7 逐行补齐版（55592B/`5526a3c2…`）按操作者外部封存（操作者陈述）。本轮未新增产品运行，仅静态读取与纯计算；未读另一方 R08 正文。base/head/tree 身份不变。

### 12.1 共享§1：特定定义 Undo 链——本人独立核验成立

- 源码 `tests/e2e/t02-ontology-mainline.spec.ts`（base 即存在、base→head 零改动，本人 `git diff` 核验）325–429 行实测读：349–361 行两次真实点击"预览撤销本次修改"，分别 `inspectDiff` 独立 reverse/forward 完整 Diff 后 `confirmAndRead`；384–425 行仅重开本 owned profile（`--user-data-dir` 复用，断言 userData==sessionData）、显式点击打开同项目、断言"版本 3"、`readCurrent` 与三个原 Job/operation（`getJob`/`getOperation`）逐字读回。
- 原 body `native24-config-fixed/attachments/078-t02-real-m-undo-restart.bin` 本人核验 25671B / `448a3494…f60b`，解析：`stage=completed`；committed/undone/redone 的 `after.domain.projectRevision`＝1/2/3；三 Job 均 `succeeded` 且 jobId/operationId 各自唯一（本人集合去重验证）；`undone.after.domain.state == initial.domain.state`、`redone.after.domain.state == committed.after.domain.state`、`reopened.domain == redone.after.domain` 且 `inputSnapshotId` 相等——逐项独立复算为真。
- native24 report 中该 spec（"five fields, complete Diff, original receipt, Undo/Redo and owned restart"）`status=expected`、duration 4920ms、retry 0（本人展开）。
- **范围限定**：只证明这一个定义、已执行输入/影响范围的 GUI Undo/Undo-of-Undo/owned-restart 链；不能全称"全部 Undo GUI 已验"，也不解除其它 Undo 变体、ownership 冲突族、故障注入族及父 FR/发布 HOLD。

### 12.2 共享§2：负例族 S/P/O 字段保留——本人独立核验成立

- `tests/e2e/t02-fr200-fr201.spec.ts:731` `rejectCallerObject`（本人实读 731–787 行）：受控拒绝（INVALID_REQUEST/OWNERSHIP_CONFLICT 双码、alert 文案含"已输入内容保留"）后 773–775 行对 subject/predicate/object 三个输入框 `toHaveValue` 断言保留输入值；762–763 行为填写前保留基线；784–787 行断言无完整 Diff/确认按钮且完整 Read 前后相等。
- 952–983 行 xsd:string 别名负例：填入 `"typed string"^^<…string>` → 受控 INVALID_REQUEST，971 行 `toHaveValue(alias)` 断言无静默规范化（源码注释明示），无 Diff/确认、Read 相等，附件 `fr201-rejected-explicit-string-alias` 落盘。
- native24：FR201 spec（48 附件）`status=expected`、76897ms、retry 0（本人展开）；attachments 目录 100 文件中拒绝/冲突类恰 43＝42 `fr201-rejected-*`（new/edit×parser/语言/超长整数/IPv6/全角斜杠/非规范各族）＋1 `fr201-rejected-reserved-original-id`（OWNERSHIP_CONFLICT），与历史 42 INVALID＋1 OWNERSHIP 一致。
- **范围限定**：字段保留只证已执行本屏/这些输入；不推出所有表单、所有错误族或其它页面均保留。

### 12.3 共享§3：迁移证据边界——成立，并纠正本报告两处依据错误

- `packages/engine/tests/test_project_format3.py` 文件头明示"Private Store-ready acceptance on synthetic databases only; no business3/Job-ready"（本人实读）。
- 本人从 mode2 原 summary 重算：`test_migration_atomic_faults[` 前缀恰 468 项＝424 passed＋44 skipped；44 为源格式缺对应阶段的条件 skip（源码 167–175 行 skip 分支＋注释"Skip stages absent from the actual original format; do not invent passed hooks"），**不是执行通过**。执行证据是 424 项真实 PASS：合成临时 SQLite、source version 0/1/2、显式 `Store(target_format=3, backup_path=…)`、按 phase 注入 RuntimeError/KeyboardInterrupt/OSError 或子进程 `os._exit(79)`；after_commit → format==3 可重开，其余 phase → `frozen(path)==before`、备份存在则 `frozen(backup)==before`、lifetime lease 可重新获取（本人实读 163–212 行）。
- `test_explicit_gate_backup_and_full_domain_history` 同记录 passed（本人重算）：backupRequired 门禁、迁移前 frozen 不变、备份 frozen==before、`backup_hash==SHA256(backup)`、future-format 拒绝、重开保留 commits（98–128 行本人实读）。
- `frozen()`（86–96 行）＝logical_hash/user_version/snapshot rows 的**逻辑观察，不是物理字节比对**（共享文件边界正确）。
- **对本报告的纠正**：v1.0 清单 #15 将"44 条件 skip"写作"真实迁移分支"、#156 写作"其证据面"是依据错误，按上述真实证据改正（见 12.6）；结论方向不变但收窄为"合成库 Store 层前向迁移＋注入失败原子性＋显式备份门禁已验"；不证明业务 Job-ready、人工 schema 降级、大规模活库、锁行为、损坏 SQLite 物理保护（后两者维持 HOLD）。

### 12.4 共享§4：dependabot 在仓与组织类边界

- 本人实读 `.github/dependabot.yml`：npm（directory /，target develop，weekly，open-pull-requests-limit 5）＋ github-actions（/，develop，weekly）。**不应再说"没有任何更新安排"**；但该配置不证明实际运行/合并处理记录、安全更新开启、uv/vendor 覆盖或人类修复 SLA；ci.yml 无 audit 类步骤维持原事实；pin/frozen≠漏洞扫描。
- 组织类：v1.0 #147 写"实际=1 风险"超出证据——单 writer/多 AI 均不能证明 bus factor 实际值，改为"无法确认（有单负责人迹象，实际人数/身份无证据）"（见 12.6）。
- 密钥：v1.0 #36 的源码 grep 范围本来就限源码；补充边界：不证明全部 Git 历史/AI 聊天无密钥，不要求读取密钥或无关聊天填缺口。四连击（#31）：内容 ID/操作声明/冲突围栏为机制层证据，本轮无实际四连击 GUI 运行（43 附件族中亦无 rapid-click 项），维持原判定并加此边界。

### 12.5 共享§5：主进程三处 delta 语义审读——通过，未发现缺陷；关闭 v1.0 §2 的主进程未读项

本人实读 base→head 三处 delta 及必要上下文（非差异统计代语义检查）：

- `desktop-ipc.ts`（+3）：新增 `'project:ownership-detail'` handler 项（桥接缺失时 PERMISSION_DENIED 兜底，同其它通道）＋一行 `register(...)`。register()（155–186 行本人实读）对所有通道先 `if (!trusted(event)) return permission()`；`project:*`（除 active）走 mainline delivery：`replies.receive()` 全局 16 槽上限（含并发与 UNKNOWN）、原始异常不跨界（catch→permission()）、sender/frame/session 记录供有界重复 ACK。新通道与其他 project 通道同规。
- `engine.ts`（+5/−1）：`MainlineMethod` 联合与 supervisor #request 白名单各加 `'project.ownership.detail'`；selected-equality 分支扩展为 read/draft.save/ownership.detail 三方法——`params.projectId !== record.selected?.projectId` 即 `deniedOrdinary()`；并随通用路径获得 `validateBusiness3('params_/result_'+method)` zod 校验、帧预算与请求超时（1224–1265 行本人实读）。
- `project-mainline-service.ts`（+24）：`getOwnershipConflictDetailPage`（558–577 行本人实读）——调用前捕获 current/client/selectionEpoch，要求 `client.owner === current.owner`；参数以 `{...args, projectId: current.project.projectId}` 覆盖，渲染端 projectId 无法引导至他项目；await 后复核 selectionEpoch 未变、source.current() 的 owner 与 projectId 未变、`client.engineSessionId === current.engineSessionId`，任一不符即 denied；注释"Never publish a workspace, selection or snapshot projection"；异常经 `#run`→safeError 不泄原始异常。`#selectionEpoch` 于 recovery 失效时递增（314–321 行），跨选择敏感操作一致使用（本人实读 280–444 行生命周期）。
- 链路整体（本人既有＋本轮实读拼合）：preload 业务命名方法（+1）→ ipc trusted+delivery → service owner/epoch/session/projectId 围栏 → supervisor 白名单+zod+selected 相等+预算 → 引擎 `mainline.dispatch` 的 `authorize`＋`ownership_proof`（request_hash==digest(request)、base 绑定、current.method 匹配）→ `store.ownership_detail_page`；渲染端 `mainline-ownership.ts` 每页 `matchesOwnershipDetail` 契约校验、512 页上界、fail-closed。**只读通道，逐层 fail-closed，未发现新问题**。v1.0 §2"未读 csp 之外全部主进程文件"一项就此收窄为已读这三处 delta＋必要上下文（其余主进程文件仍非本轮逐行范围）。

### 12.6 受影响条目（v1.1 更新评估；v1.0 原表/原判一字不改）

| 条目 | v1.0 | v1.1 更新 | 依据 |
|---|---|---|---|
| 清单 #128 undo | 适用部分（"Undo GUI 未 E2E 验"） | 适用部分，依据更新：一条真实定义级 Undo/Undo-of-Undo/owned-restart GUI 链已同版验证（12.1）；其余 Undo/ownership/故障族仍未验 | 12.1 |
| 清单 #125 表单保留输入 | 无法确认 | **适用部分**（限已执行本屏/这些输入：受控拒绝后 S/P/O `toHaveValue`＋xsd:string 别名无静默规范化；非全表单穷尽） | 12.2 |
| 清单 #135 依赖升级 | 无法确认（未建立） | **适用部分**（dependabot npm+actions weekly→develop 在仓；实际运行/合并记录、uv/vendor 覆盖、漏洞扫描开关未核） | 12.4 |
| 清单 #31 四连击去重 | 适用已满足（机制层） | 判定不变；加边界：无实际四连击 GUI 运行记录，机制层证据不变 | 12.4 |
| 清单 #15 迁移 | 适用已满足（依据误写 44 skip） | 判定不变、依据改正：424P 原子故障＋显式备份门禁 P（合成库 Store 层）；44 skip 为条件 skip 非执行证据 | 12.3 |
| 清单 #156 活库迁移 | 适用部分（依据误写 44 skip） | 判定不变、依据改正：同 12.3；业务 Job-ready/大规模活库/锁行为/损坏 SQLite 未验维持 | 12.3 |
| 清单 #19/#20 备份/恢复 | 适用部分 | 判定不变；补充：explicit-gate 已证备份创建＋逻辑 frozen 相等＋backup_hash 钉定；从备份执行恢复仍未验 | 12.3 |
| 清单 #36 密钥 | 适用已满足（源码 grep） | 判定不变；加边界：不证明 Git 历史/AI 聊天无密钥 | 12.4 |
| 清单 #147 bus factor | 无法确认（"实际=1 风险"） | 无法确认；删"实际=1"断言：实际人数/身份无证据，仅单负责人迹象 | 12.4 |
| Top10 #8 | "无依赖漏洞扫描——盲区" | 表述更正：**依赖漏洞防护未核验**——ci.yml 无 audit 步＋dependabot 版本更新配置在仓但运行/安全更新记录未核、uv/vendor 不在其覆盖；严重级维持 P2（供应链核验缺口仍真实） | 12.4 |
| Top10 #11 / 问题 #11 | "…Undo GUI…未验" | 收窄：Undo GUI 一条链已验（12.1），其余 a11y/键盘导航/i18n/四具名下游/其它 Undo 家族未验不变 | 12.1 |
| §9 HOLD "Undo GUI 未验" | 全称未验 | 收窄为："Undo GUI 仅一条定义级链已验（12.1），其余 Undo/ownership/故障家族未验"；其余 HOLD 逐项不动 | 12.1 |
| §7 78 位置 | — | **无任何一行因本补充关闭或新开**：Z F6 各子族（definitions/裸 ownership/EOF/缺码/无序/4299-4300）与已验 Undo 链为不同对象；R06 D10 四具名下游（推导/保存查询/SHACL/报告）亦非本链；状态表 20/31/4/23 不变 | 12.1–12.3 |
| §10 统计 | 29/32/27/60/12 | v1.0 表与统计保持原样（已封存）；若按 v1.1 评估重算仅 #125、#135 两行由无法确认→适用部分，则为 29/34/27/60/10＝160——仅说明，不回写 | 12.6 |

### 12.7 结论与条件不变性

- **整候选结论不变：附条件通过（Conditional Pass）**。本轮新事实均为正面收窄或依据纠正：新读通道（ownership-detail）语义审读通过、无新缺陷；Undo/字段保留/迁移/dependabot 为证据边界精确化。
- **push 前源码技术门禁：仍无**（未发现新源码阻断；12.5 反而关闭了 v1.0 的主进程未读项）。
- **需新 CI 后核的合并条件：不变**（§8 五条：Windows 完整 3769 逐项、3 job success、Quality 专项与 packaged recovery 步骤自身 success、case7 不复发或结构化定因、ROOT 接收双 R08 与全部意见处分）。
- **全部原 HOLD 保留**，仅 §9 中 Undo GUI 措辞按 12.6 收窄；签名/公证/wholeApp 法律/_distutils、目标平台/参考设备、容量 Q5/D2、损坏 SQLite、unknown parser/N3/Store/坏快照、其余 Undo/ownership 家族、四具名下游、未知退出码、组织/产权/隐私/法律等继续独立 HOLD。仍 2/17，未合并，无新增 push/CI/merge 授权。

---

## 13. 本人意见处置确认 v1.2（2026-10-26；输入＝操作者处置提案，本人逐项独立表态）

### 13.0 输入核验与边界

- 提案 `outputs/20261026_t02_62d4_fresh_r08_057/zcode-opinion-disposition-proposal-01.md` 本人核验 6929B / SHA256 `2cf9598527affe1c8ecdc6b65d72ab12b89c6ccd9dedbd947e5197587ef3db99` 一致并全文读取。它只覆盖本报告 §5 全部 11 条与 Top10 第 5（旧 79F）共 12 个位置。
- 本节为**本人处置**：逐项同意/限定均基于本人已有实读/复算（§2、§4、§12）＋本轮新增三处直接证据（13.3）；不为迎合提案改判，不预设 Pass。此前各版字节（含 69019B/`51bc5bb6…` 共同事实补充版）全部保留；160 行表、78 位置表、各版统计均不改写；无旧 OPEN 被静默关闭（Z08-06 在 v1.0 本就是"已关闭（本地限定）"，此处维持）。
- 本轮仅静态读取＋纯计算；未跑产品/测试/构建、未动 index/commit/branch/remote、未新增 push/CI/merge 授权、未读对方任何当前材料。

### 13.1 逐项处置

| ID | 本人处置 | 直接依据（本人核验） | 当前阻断性 | owner/事件窗口 |
|---|---|---|---|---|
| Z08-01（=§5#1） | **同意**：merge 门禁仍开 | 本人读回 O056 ls-remote（develop 583/feature 9cb、62d4 未 push）＋ O050 CI-FACTS 原件（13.3：Windows 3429P/3477 结算/292 未结算/15m 与 20m 双取消）；本地 O056 不替代完整回单 | **阻断 merge**（非源码缺陷）；不阻断 push 前流程 | ROOT 未来精确 push/CI 票；merge 前按 §8 五条逐项核 |
| Z08-02（=§5#2） | **同意（限定）**：未验边界，不升级为已证残留，也不写成已证清理 | 本人实读 run-engine-tests.py stop() "UNKNOWN after launcher exit; no job handle"；guard-native-redirector 真实回单（launcher37290/native37291/parent37290）为 Mac 间接 PID 实证；Windows 真实运行 0 次 | 不阻断 push；Windows CI 验收项 | Windows 完整 CI 证据接收；Job Object/新工具须 ROOT 另票，当前无开发 |
| Z08-03（=§5#3） | **同意**：取消/制品限制采纳；不采当前扩大超时 | 本人实读 ci.yml concurrency `cancel-in-progress:true`、15/20min 原值、双 always 制品步 | 非阻断；验收注意项 | 未来实际制品回单判断；任何预算变化须新明确授权 |
| Z08-04（=§5#4） | **同意**：历史 FAIL/缺栈仍开 | 本轮新增直接证据（13.3）：O050 attempt-1 原日志行 1164 `✘ 7 …mainline-consumer-first-ack-loss.spec.ts:256:5 …(7.9s)` 真实 FAIL、行 1192 case 8 ✓；断言栈缺失属实；O054/O055/native24 未复现 | 非当前 push 阻断；CI 验收项 | 下一真实 CI 若复发按新增结构化栈定因；新绿不倒填 |
| Z08-05（=§5#5） | **同意（限定）**：非阻断维护＋**双向因果限定** | 本人 grep 两处在位（:656/:168）；O056 保留首次 ENOENT 失败与正确 uv 通过双原件。采纳提案限定，并据此把本人 v1.0 §5#5 "已知与 79F 归因无关"的单向表述更正为"不作为 79F 根因认定，亦不能排除其为部分环境因素"——表述精确化，非判定翻转 | 非阻断维护 | T01 原测试维护者下次授权触及环境/测试时；无需重跑旧失败填因果 |
| Z08-06（=§5#6） | **同意**：62d4 配置绑定修复**本地闭合** | 本人复算：controlHashes==HEAD 两脚本、identity 七字段与 native-uv 基线全等、ordered3769、run-30cfd524 计账全覆盖；422b 撤销记录原样保留 | 已关闭（限本地控制层资格）；远端归 Z08-01 | Windows/Quality 实际 CI 仍待验 |
| Z08-07（=§5#7） | **同意（部分采纳）**：未验/文案维护，家族 HOLD 不动 | 42 内部分类≠逐原因可行动文案（R07/R08 一贯事实）；已测子集（v1.1 §12.2 的字段保留与固定文案）不外推所有错误出口 | 非阻断延期 | 原 T01/T02 方法接线窗口；不扩新功能、不泛加码 |
| Z08-08（=§5#8/Top10#8） | **同意（限定采纳）** | 本人实读 ci.yml 全文无 npm/uv audit 步；外部扫描存在性未知、不双向断言——与本人 v1.1 §12.4 更正一致；P2 维持（"防护未核验"而非"无任何安排"） | 非阻断；发布/供应链缺口 | 发布/供应链 owner 另票；本票不新增扫描配置或外部调用 |
| Z08-09（=§5#9） | **同意**：非阻断卫生观察 | 本人实读两 always 制品步均含 test-results/；成本未量化不虚构；不删原始失败制品 | 非阻断 | 未来 CI 维护票评估去重；本票无改动 |
| Z08-10（=§5#10/Top10#10） | **同意（部分采纳）** | 本人实读 dependabot.yml（npm+github-actions，均 directory /，weekly，target develop；npm open-pull-requests-limit 5）；实际运行/合并记录、uv/vendor 跟进、SLA/EOL 未证——纠正 v1.0 "全无节奏"暗示（与 v1.1 §12.4 一致） | 非阻断；长期维护未知 | 发布/vendor 原 owner 未来窗口；配置存在不称执行完成 |
| Z08-11（=§5#11/Top10#11） | **同意**：原独立 HOLD 保留＋Undo 子集收窄 | undo 例为 native24 运行序 18（提案"case18"编号**属实**，本人本轮按报告序核验）、4920ms/retry0、body 全断言本人复算为真（§12.1）；清单 15/156/125 限定与本人 §12.6 一致；组织/人数/bus factor/法律角色不可由代码认证 | 非阻断；各独立 HOLD | 原各 owner/父 FR 与发布验收时；不新建功能或产品验证 |
| Z08-TOP10-OLD79F（=Top10#5） | **同意**：未知原因保原 | 旧 CI36 79F 无逐例栈（历史事实）；O050 只含 9cb 时点事实，不含 CI36 原件；不以新绿倒填、不为消因果重跑旧 DB/probe | 非当前阻断（历史残留） | ROOT 历史残留登记及未来真实复发证据 |

### 13.2 提案"精确限定"各段的本人确认

- 段 1（Z08-01/04/OLD79F 验收口径）：与本人 §8 五条及 v1.0 §6 口径一致——逐 node/有据 skip/阶段/session/退出/coverage/全部后继与三 job 实际 success、15/20min 保留、不以 step 绿或总数代证、新绿不倒填。**确认**。
- 段 2（Z08-02）：descendants UNKNOWN 不可写成无残留；未来回单只证可证范围；不自动增设 Windows GUI/任务管理器操作或 Job Object 前置；Windows11 目标设备 HOLD 与 CI 门禁分开。**确认**。
- 段 3（Z08-03）：不延长 timeout/不重试/不降检查；always 仅配置，完整性看本次原运行。**确认**。
- 段 4（Z08-05）：无旧逐例栈，只能限现有证据；无需重跑旧失败。**确认**（并已按此更正本人 v1.0 单向表述，见 13.1）。
- 段 5（Z08-08/10）：仓内无显式 audit 不等平台/组织无扫描；dependabot 覆盖范围与未证清单如 13.1；未来扫描/外部调用另票。**确认**。
- 段 6（Z08-11/清单）：Undo 仅收窄该子集；迁移区分 424 实际 PASS 与 44 条件 skip、合成夹具逻辑观察与损坏活库物理保护；#125 仅已测本屏；组织/法律边界与"不新增人类签字或产品裁决审批"。**确认**（全部与 §12.6 同向）。
- 段 7（Z08-09）：不量化未实测成本、不删原始失败制品。**确认**。

### 13.3 本轮新增直接证据（静态读取，均原件）

- O050＝`outputs/20261026_t02_9cbddf34_remote_ci_050`：attempt-1 Quality 原日志行 1164 `✘ 7 tests/e2e/mainline-consumer-first-ack-loss.spec.ts:256:5 › actual ontology consumer reconciles first lost commit ACK without another submit (7.9s)`（真实 FAIL、无断言栈）；行 1192 case 8 ✓。CI-FACTS.json：Windows `passed 3429 / uniqueSettled 3477 / unsettled 292`、`terminal: KeyboardInterrupt/subprocess.py1590 and official20m cap cancelled`、`jobFinal: cancelled after original15m limit`。该原件同时是 Z08-01/Z08-04 与 Top10 历史语境的直接依据。
- native24 报告 spec 序（本人按 suites 顺序展开）：序 7＝ack-loss ontology 例（与 O050 CI case 7 同名同序）、序 16＝FR201 主链、序 17＝canonical cohort、序 18＝Undo/Redo/owned restart——提案"case18"编号属实。
- 上述读取不产生新产品运行，不改变任何受冻对象。

### 13.4 处置对既有内容的影响

- 无任何旧 OPEN 被关闭或降级：Z08-01/02/03/04/05/07/08/09/10/11 与 OLD79F 全部维持原开/延期/登记状态及原 owner 窗口；唯一"闭合"项 Z08-06 是 v1.0 已定的本地限定闭合，维持不变。
- 表述更正两处（非判定翻转）：v1.0 §5#5 的"与 79F 归因无关"按 Z08-05 双向限定更正（13.1）；v1.0 #10"全无节奏"已在 v1.1 更正，此处维持。
- v1.0/v1.1 全部字节、160 行表（29/32/27/60/12 统计行）、78 位置表（20/31/4/23）原样保留；本节不回写任何前文。

### 13.5 最终结论与条件（不变）

- 整候选仍为**附条件通过（Conditional Pass）**；push 前源码技术阻断仍无；merge 条件仍为 §8 五条（Windows 完整 3769 逐项＋三 job 实际 success＋Quality 专项/packaged recovery 步骤自身 success＋case7 不复发或结构化定因＋ROOT 接收双 R08 与全部意见处分）。
- 本轮**无新增须交 ROOT 的验证/改源缺口**：所有 OPEN 项均已有具名 owner 与事件窗口；如未来需要 Job Object、扫描配置、timeout 调整或外部调用，均按 13.1 所列另票，本人不自行实施。
- 作者完成本处置≠ROOT 已接收≠merge 票；仍 2/17，未合并；签名/公证/wholeApp 法律/_distutils、目标平台/参考设备、容量 Q5/D2、损坏 SQLite、unknown parser/N3/Store/坏快照、其余 Undo/ownership 家族、四具名下游、未知退出码、组织/产权/隐私/法律等全部原 HOLD 保留；无新增 push/CI/merge 授权。
