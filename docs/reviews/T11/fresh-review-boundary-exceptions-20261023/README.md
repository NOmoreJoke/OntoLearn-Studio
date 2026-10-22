# T11 036 本轮审查输入越界登记（2026-10-23）

两条提交命令触及明确禁令，当前均为 **OPEN，待总控处置**。这里只登记输入，不据输入推断执行、成功或副作用。原始输入完整保留在 `input-only-incidents.json`；对应越界工具返回未读、未转存、命令未重跑。

- ZCode 原 SID `session_8b120f9cd410a68dbf141a7216ac0308`，原 turn `turn_9ee07ab5-c812-41ca-b03e-f83fac40acdb`：调用 `call_e7fd593e12134be4a76a07df` 提交命令请求临时空仓 `git commit`，本轮明确禁止 commit。
- MiniMax 原 SID `mvs_c2a07cc404db489b9e1e5b32c4686c0a`，原 turn `1fff4822-1702-4b24-996b-4c6820b71c44`：调用 `call_01a165325b487476865bedbe` 提交命令请求运行两次 Mac collector 及读取平台版本；本轮明确禁止运行真实 collector／平台 native。预期早拒绝不能豁免调用边界。

独立 agent 仅核对输入收据与本方提示规则，确认临时空仓和预期早拒绝不构成例外；未读取原生日志、工具返回或报告。详见 `independent-review.md`。

ZCode 已有正式 `turn.completed` 和完整原报告，另存于相邻 `fresh-review-zcode-completed-20261023/`。33,375 字节报告与本方精确原 turn 的 Write 内容逐字节一致。原文工程范围结论是“通过”，但过程接受仍待总控裁定；18项只保存一方处置意见，owner关闭数为0。报告计数、M-F-D单元格严重度、manifest哈希抄写差错已分别标注，未改原文。原报告含审查者关于 hook 的断言，因此不主张零暴露；其对应工具返回未读、未转存。

MiniMax 最新正式快照见 `minimax-formal-status.json`，现已 completed；完整报告固定于相邻 `fresh-review-minimax-completed-20261023/`，原文工程范围结论为不通过，新增中级 F-1。历史 NULL 快照仍为当时 UNKNOWN，不回填。GUI保持RELEASED，无新提示、无新任务、无候选变更、无重测、无push／PR／发布授权。此前 owner 误打印注入上下文前缀的异常继续OPEN，未被本收据取代。

本包需要总控先裁定越界影响与原 turn 后续动作。可以继续经批准的精确终态／报告接收；不能自行调用GUI停止、重发提示或以新一轮审查替代原 turn。

完整审查原报告作为指定双审追溯原件入库，保留各自字节和hash；不对原报告运行格式化。大量运行日志仍保留在各自原runtime，不将其全文或原生消息／header入库。
