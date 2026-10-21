# 当前责任更新读回

## 最新单文件补充：worker.py

2026-10-21 10:21+08 生效通知已在安全边界实际全文读取 I05-T01-worker-ownership-handoff.md，并读回共同指南追加段。当前共同指南 SHA 为 ff5f9fd0a4913cc6c2fa612ec565bdf40d67db4a6640e5293d4ca1e7d02cfaff；已核验原 b24 全部字节仍为其精确前缀，AGENTS仍78df2825…a759。旧指南/冻结输入不改写。

worker.py 未来唯一维护者为 T01，只从批准5f的9314字节/2fa848aa3a2148e59a24f01c9333701f0f03eed95cffe55a0a78b74f1d06f2f0施工；不得消费未批准C3的13638字节/3d934e79aff65288e1f249e2763f46b4eb86f50bd05ccc7628643951f4d4f99d语义worker。C3原字节继续冻结；需修先由总控精确返还，T01停写并保存身份/差异。protocol/resources/语义/旧tests/build/CI不随转，semantic4 futureoffer未生效，wire/限额/公共3/ready或运行能力均未因此获批。T06不改共享路径；所有本线agent已终态，后续实际任务再传最新政策，不为本通知重启agent、复测或恢复blocked Goal。

## 前次 b24 责任快照

2026-10-21，实际全文读取共同指令及三份生效 handoff，SHA-256：

- developer-common-instructions.md：b24c4c88404f422c5fae4bf6c01e231b678e46741250801e8100cc62a31fec39。
- I05-T01-format3-ownership-handoff.md：18485767098d448a4fcce2fc7e59b5a325433826894b98111cab96926fdc2097。
- I06-T01-format3-ownership-handoff.md：add9884ab9a0cda3a8a562f26a3b7c515255919d65eb0487d6c254681ed4991d。
- I05-T03-build-ownership-handoff.md：88057b59e173453d197bfeae183dc99b8c09c71e30d518781bf774ebc037e95b。

当前 T01 唯一维护 storage.py、格式基础 Python 四文件、canonical/main engine 八文件；T03 唯一维护 pyproject、uv.lock、build-engine、entrypoint 四文件。I06 仍维护 main/index、task-service、preload/index、renderer/env、App、style 六文件。既有测试、CI、resources 和其他未交文件不自动授权；返还须精确交接。T06 仅自身原私有路径及独立 UI 授权路径，不改上述共享文件，不复制未批准实现。

对 ui-integration-handoff.md 和旧 interface/readiness 的责任说明：T00 仍作正式业务接口协调，实际 canonical/engine 维护归 T01；App/renderer 公共装配仍归 I06。接线依具体 owner 与总控批准推进，不能把接口协调人当所有共享文件维护者。

AGENTS 仍为 78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759；原第九节、无桌面、指定双审与逐任务模式读回不变。df090 及更早 SHA 保留为历史快照；两份已提交冻结外审输入不改写，实际操作遵守本次更新。这是责任政策变化，不是受审实现/测试/依赖/验收变化，不据此无变化重测、重开 Goal 或外审。

已透传 UI 与独立复核 agent。UI agent 实际回执全文读取共同指令和三 handoff、hash 匹配并接受排除；独立复核 agent 的原报告已终态，其原 df090 输入保留，下次任务再核最新政策。

UI 原 571b4d6 三项 P2 的完整独立报告原文归档 ui-local-review-1.md；负例工具归档 evidence/ui-571b4d6-negative-probes.mjs。该工具读取其写明工作树当时源码，当前树修复后不再当作旧候选重现命令，旧源码以固定 Git 571b4d6 为准；未改旧不通过结论。开发 agent 已实际接受三项并在自身树修复，新的必要验证来自实现变更。
