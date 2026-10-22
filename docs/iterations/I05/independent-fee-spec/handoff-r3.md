# R3 固定候选交接

revisionBase=8d703858a9e7777e0086057032aea280316e49c1。candidate/process实际commit在本次提交后单独的r3-author-process-receipt.json给出，不预填未来hash。所有交付仅两个授权fee docs前缀；AGENTS15147B/SHAde15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4保持本地M，不stage。

独立delta建议先核[R2正式Fail](../../../reviews/I05/independent-fee-spec/independent-review-r2.md)与[R3回应](../../../reviews/I05/independent-fee-spec/r3-disposition.md)，再用同一六完整入口验证首错/paidPrefix/receipt/failed清理，随后核114和静态位置/已知许可门。旧R2 reviewer/collector禁止用来覆盖旧件；如复核请新路径保存。

工作目录为本树；Python固定 `/Users/kyle/.local/share/uv/python/cpython-3.12-macos-aarch64-none/bin/python3.12 -B`。以下纯程序命令已实际执行，具体argv/stdout/stderr/exit见review对应r3命名记录；重跑会保护immutable attempt文件，应给全新路径名，不覆盖本候选证据。

| 命令（都在charge-reference-v3）                                           | 实际结果                                                     |
| ------------------------------------------------------------------------- | ------------------------------------------------------------ |
| verify_r3.py final-math-02 test_reference.py test_complete_failures_r3.py | 13原typed +10完整入口方法exit0                               |
| run_reference.py --attempt baseline-final-02 --baseline-only              | 2410分析=执行项，exit0                                       |
| run_reference.py --attempt all114-final-02                                | 114项，231960分析/231899执行，exit0                          |
| produce_failures_r3.py                                                    | 六真实完整失败入口，exit0（final-math-02命令2原记录）        |
| verify_r3.py bind-table-02 bind_per_id.py                                 | bound114/amount-null0，exit0                                 |
| verify_r3.py independent-audit-06 audit_execution_r3.py                   | 七完整tape独立replay+literal、114receipt/17L/字段保全，exit0 |
| check_determinism_r3.py                                                   | 114+6两seed的分析/执行/金额/已付/首错/receipt相等，exit0     |

两个审计器假设错误及event49错误预期曾实际exit1，原raw与日志都保留，不以最终exit0改写历史。一次标题查询缺review/handoff-r2.md exit2保在修订记录。初始R1/R2/输入隔离事故/所有首Fail原件不动。

新manifest包括两授权前缀下全部普通文件的bytes/SHA，旧v1隔离材料只opaque哈希，不读内容；self-exclusion严格只排artifact-manifest-r3.json和随后r3-author-process-receipt.json。最终integrity逐件验证revisionBase已有件=当前bytes，另验证输入raw/SHA、源AST、写面和protectedAGENTS；commit后process再验证manifest成员current=Git=SHA与index空。

仍pending：当前source与wire/codec绑定、同次原始17L capture、产品真实issuer/usage与发点、真实owner H/调用许可。原预测分配、独立数学和提案invoice分别精确，pending不抹除这些值。提案中的1个资源拒绝只由其精确原cap首拒证明，不能将任意业务RESOURCE_LIMIT视为合法。未执行产品/pytest/npm/build/native/DB/GUI/network/安装/版本探针/push/旧小Ledger回归，未修改T05受审候选。
