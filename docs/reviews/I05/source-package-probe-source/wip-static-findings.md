# 冻结前静态发现与修正记录

本件记录源码编写期间真实发现，不是运行日志或固定候选独审结论。原工具调用和 agent 原消息保留在当前会话；下文是摘要，不把重新撰写文本冒称原始 stdout。

1. root 初写 _catalog 错用了不存在的 CONTRACT.SCHEMA。只读 canonical fixture 后改为已核固定 schema.json 的完整文档，并沿用 resources.CONTRACT.ERROR_CATALOG，不另 exec checker。
2. 准备 ledger 成功会 transferred；复用于 production 必触发 reused。独立测试作者静态核 actual6891 的 begin/state 与原 fixture，root 改为生产阶段另建 CaptureLedger。
3. root 曾按旧深层测试方法写 replace(expected, payload_digest, rows_digest)。测试作者指出新实施窗 L36 明确禁止按扰动结果另发 expectation；root 重新读精确窗口并删除重绑。本候选用同一原 expected/allocation，对 A1 拒绝与旧深层测试另域明确区分。初始错误未作为已通过证据。
4. root 初写的 eligible=false 跳过条件覆盖了同 sourceCaseId 的 repair before/after shape。独立作者按固定资产指出应只跳第77个 profile，root 已限定 operation，保独立 SHACL 真调用。
5. header 初写多余 parity 格式字样，按固定合同 §4.2 改为 i05-source-package-observations/1。默认 stdout 无 binary buffer 时改为安全 harness 失败，不让 AttributeError 在 collector 外穿透。

输入生成器初次 query 路径错误原工具 output 已保存在 inputs/generator-first-failure.raw，1496 B／af6240ae1690378f46675e01ba2cf4c1382746d1b6d9683664f42eb155f1bf63。后续字节复现成功，不覆盖首错。

root 写本说明时首次 apply_patch 外层 JavaScript 因 Markdown backtick 与 template literal 冲突，工具返回 SyntaxError: missing ) after argument list；当次未调用文件补丁工具。改用无该冲突的正文后写入。本错误不是产品或生成器运行失败。
