# C1 driver 有界进程核算修复：设计与实际验证

本候选只改 `tests/e2e/c1-native-macos-driver.mjs`；observer 原字节不变。新树 `T01-c1-native-runtime-20261023`、分支 `fix/T01-c1-native-runtime-20261023` 从 `acbe2dc6388c855f7fbabbb6da08cdf6c14bcbab` 创建，approved merge-base 为 `5f910b52c69d86a1076b2032e5d3c63e715947f3`。AGENTS 按要求携带最新原字节，不属于本次源码提交面；没有提交、stage 或操作旧树。

## 固定输入与可证边界

完整读取 `/tmp/t01-c1-remediation-20261022/independent-native-01-termination-attribution.md.raw`：13433B，SHA-256 `a641190ef2098c25cbc66a4b0873a5728baca3ffd8b51bf8c5828c9e2341ca4e`，以及其列出的 run01 driver、observer、事件、CUA 动作、stdout/stderr 和外层命令 receipt 原件。

run01 的真实 driver exit1 保留。原件证实 observer succeeded、三次 health、两次真实 dialog CUA 动作及原 Python/main 对象 exit0/close0；缺少变化后的原始 ps 行和采样区间，不能确证 zombie、PID reuse 或真实最终 absence。本候选不补造旧采样，不重签旧 receipt，也不把这批旧恢复证据当新 driver 的 native 验收。

## 最小机制

- 不变所有权记录保留原 pid、birth/lstart、comm、原始行、亲缘 birth 和来源；另列 `rowPresent`、`birthMismatch`、`displayMismatch`、原对象 exit/close、`terminalPending`、`resolvedTerminal`、`signalEligible`。直接 main 与原 ChildProcess 需要真实 exit0 和 close0；helper 仅沿已建立原亲缘/birth 加 fresh absence，不能伪造 close。
- 明确 birth 不同永久失败，后续 close0/absence 不抹除。单独 argv 采样发现不同 birth 同样永久拒绝。`lstart` 只有秒精度，本方案不宣称完全消除了同秒复用。
- 仅 display 变化进入 2000ms 有界 quarantine，不 signal；只有采得明确 Z 终止态、同原对象 exit0/close0、无 birth 冲突且后来新 ps 调用确认实际无行，才能终结。活动/未知 display 变化不可用后来的 close 或 absence 洗白。采样启动早于 close、回调晚于 close不算 fresh absence。
- 已 exit/close、quarantine、birth 冲突或已终结的生命周期不再充当祖先根；其后代不借该 PID 被重新收养。仅 metrics 报告但未建立原亲缘/birth 的 PID 不算已核算排空。
- 每次 signal 前重新采该单 PID、按原 birth/comm/状态及 lifecycle 核对；未知、关闭、quarantine 或解析失败者不 signal。任何 signal 尝试（含异常）都保 overall failure，无组杀、盲杀；自然终结与测试清理分开记录。
- ps 保 stat、命令参数、调用开始/结束、退出与 timeout；只归档自有 PID/runner 的原行和新行。尾部 ring32、转变512、诊断4MiB；稳定行仅采样时刻变化不反复充当转变。溢出或解析不全显式 diagnosticIncomplete、禁 signal 和成功。全局 discovery 不采无关用户 argv。
- finally 独立读取同 runId 的原子 observer 文件，分别记录 recovery、child lifecycle、main lifecycle、process accounting、overall 与 firstFailure；文件不可用时保留已验 runId 的 stream lifecycle，不伪造文件。socket/monitor 收尾错误不跳过后续收证，任何早期失败不清除。

原四 CLI 参数、120000ms runtime/300000ms cleanup 上限、main-only inspector bootstrap、真实 dialog/health 逻辑、禁 renderer CDP 和禁关闭 hang monitor 的边界保持。

## 本次实际检查

证据目录为本树 `outputs/c1-native-runtime-20261023/out/`（ignored 输出，不属于产品或旧测试改动）。纯检查脚本从候选源提取实际函数，既不 import CLI，也不调用真实 ps、kill、Electron 或产品。`classifier-04.stdout` 记录 16 组通过与对应源码 SHA：

1. 同 birth 稳定活动行及 signal 资格。
2. 不同 birth 永久失败，close0/absence 不消除。
3. display+Z 须等原 close0 和后续 fresh absence。
4. 活动 display 变化不可洗白。
5. 未知 display 状态不可洗白。
6. ps 早快照、晚回调不误认 close 后采样。
7. 缺失/非零/被信号 close 不成功。
8. 缺 exit、事件顺序错误、child error 不算可信 close。
9. helper 原亲缘加 fresh absence，不伪造 close。
10. 终结 PID 重现不能重新 signal。
11. 解析失败/既有诊断缺失不能证明 absence。
12. 实际严格 ps parser 保 stat/原行，拒坏行和重复 PID。
13. 使用 run01 原件验证早期 driver fail 仍保独立 recovery，不改变原 fail。
14. 实际 processTable 控制回调：timeout（含 code1+signal）、坏解析拒绝；仅受限正常 code1 空目标行表示 absence。
15. 实际 cleanup 控制输入：signal 后失败，临 signal 新 birth 冲突不 signal。
16. 实际 sample/allProcessesAbsent/updateEntry 控制输入：关闭 PID 及其后代不重收养、未知 metrics PID 阻止排空、1500 次稳定采样不耗尽转变历史。

首次扩展检查 `classifier-02.*` exit1 是 fixture 未提供 `rawLine`，原双流及脚本保留；修 fixture 后 `classifier-03.*` 和最终 `classifier-04.*` exit0。最初13组 `classifier-01.*` 亦保留，不能当最终源码身份的检查。最终 `syntax-01.*`、单 driver `lint-01.*`、`git diff --check` 实际 exit0。

本树独立 `npm ci --ignore-scripts` 和 `uv sync --frozen` 实际 exit0，未借其他树的 node_modules/.venv。npm 安装跳过 scripts，不声称 Electron dist 已到位。本次不启动 native，不运行 GUI/产品/OS 实验。

## 源码身份及完整检查

首次 fixed driver：41587B，SHA-256 `3ebd981b9824d578f22e89c3a44e653dbef0af97cee474495e4244a4dc13b469`。

observer：13673B，SHA-256 `33678a1742bcfb2ed9710ed65a7894ee33f9fb047c4fd2d1743207eabcddf22c`（与 acbe 相同）。

携带 AGENTS：SHA-256 `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`，保持 unstaged。

完整 `npm run check` 于 2026-10-22T16:57:28.886794+00:00 启动，exec session48029。实际命令、cwd、七个输入前后哈希、stdout/stderr 路径/字节/哈希和终态写入 `fullcheck-01.receipt.json`；下节只在实际结束后补结果。

候选需由主线安排独立 patch 审查，再由根绑定新身份和独占新 run 目录协调真正 native 复验。本报告不授权/不声称后续 native 已通过。

## 完整检查实际终态

`npm run check` 实际 exit0，2026-10-22T16:57:28.886794+00:00 至 2026-10-22T16:59:49.126384+00:00；22 个 TS 文件、1125 项测试通过；2969 项 Python 通过、44 项跳过（119.19s）。lint、format、typecheck、build、ruff 均通过。七个输入前后字节/hash一致（`sourceBytesUnchanged=true`）。

完整 stdout 8681B / SHA-256 `7d5974830eff1d6b6355b723012b76a893731033caa9141c15d5b5dcd62b6c9e`；stderr 0B / SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`。原始 receipt SHA-256 `e28a0c14a54978c181281bd512e5b8055a0cf366086d80337b46fb85bf659d84`。

检查期间未修改源码；未启动 native/GUI。独立实现审查与后续 native 验收仍由主线/根分别安排，不以本 check 替代。

## 首次独审发现及最小修正（check-02 候选）

主线转来 create_core_review 的精确独审反例：`source='ancestry'` helper 无原 ChildProcess 句柄，comm 变为不同显示且 stat=Z，后来 fresh absence 在首版会被 `requiresClose=false` 放行。首版的“helper 原亲缘+absence”规则遗漏了 display 变化必须取得原对象 exit0/close0 的附加条件。这是候选实现缺口，不是原 native run01 的根因证明。

在修改前以独占 `xb` 保存首版 driver 41587B / `3ebd981b9824d578f22e89c3a44e653dbef0af97cee474495e4244a4dc13b469` 与报告7140B / `4f9877d16d320e826f717cacc47f62cf8e63faccedebb9f59edba1138ed7b479` 原字节：`first-fixed-driver-3ebd981b.mjs.raw`、`first-fixed-report-4f9877d1.md.raw`，并生成 `first-fixed-preservation-01.json`。check-01 的 exit0 和原16组输出保留，只适用于其绑定的首版源码。

唯一源码变化为 `resolvedTerminal` 增加 `(!displayMismatch || trustedOriginalClose)` 条件。无原对象 close 的 helper 一旦 display 改变，即使 Z 后 absence 仍保持未结，quarantine 超时失败，始终不可 signal；稳定 comm 的 helper 仍可凭原亲缘/birth+fresh absence 终结。engine/main 的原 exit0/close0+Z+fresh absence 路径保持。observer、spec、产品、timeout 和 rounds 均未修改。

新候选 driver：41637B，SHA-256 `8c69a55ce6fdfa7b444f1b91211d42cc562753b1596fddc554406c3277624cdc`。新增源提取检查在保存首版上实际失败（`classifier-05-before.*` exit1，`true !== false`），修后原16组和新增组合共17组通过（`classifier-06-after.*` exit0）：helper display→Z 无 close 后立即 absence 不通过、超过 quarantine 后仍失败且无 signal；稳定 helper absence 与 engine close0+Z 后 absence 两正例通过。逐项与源码身份在 `classifier-results-05-before.json` / `classifier-results-06-after.json`，新脚本为 `classifier-check-05.mjs`。syntax-02、lint-02 实际 exit0；没有真实 ps/kill/native 调用。

fresh `npm run check` 的 check-02 于2026-10-22T17:02:18.523193+00:00启动，exec session75371；新双流、前后输入身份与终态只写 `fullcheck-02.*`，不覆盖 check-01。源码已停止修改，待独立审者对新 hash 复核；本段不替独审者关闭意见。

### check-02 实际终态

新候选 fresh 完整检查实际 exit0，2026-10-22T17:02:18.523193+00:00 至 2026-10-22T17:04:26.212478+00:00（session75371）：22个TS文件/1125测试通过；2969项Python通过、44项跳过（109.96s），全部前序lint/format/typecheck/build/ruff通过。七输入前后字节/hash一致，`sourceBytesUnchanged=true`。

新 stdout 8680B / SHA-256 `745a2b4ebe8ed4b9edb3dfc8949a6177e53981a708a0680e6bc594acc5fa6795`；stderr 0B / SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`；`fullcheck-02.receipt.json` SHA-256 `b83551ad49b65df546bf7a31b9f593a4100338868d56ba5dbe2570cfc28567ab`。本次结果只绑定41637B / `8c69a55ce6fdfa7b444f1b91211d42cc562753b1596fddc554406c3277624cdc` 新driver，未覆盖首版证据。

源码继续停写，observer仍原字节，等待原独审者delta复核。未执行native/GUI，不以此结论代根的原生验收或审查关闭。
