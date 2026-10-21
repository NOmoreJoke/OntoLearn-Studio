# T05 消费批准 T09 固定输入

总控消息实际授权只读使用 `873c8c051b9870aa12fc7e1dbbd3e0c358e7c380` 的输入，未批准其服务或旧 Store helper。本线从该 Git ref 用 `git show` 读取 manifest 和每项输入；没有读取变化中 HEAD 作为获批实现，没有写 T09 原件。

- version：`prd-v0.6-learning-1`。
- manifest SHA256：`aaaef2c023320038bc155640566bdc69e0bb862a2836d7cc6ef49f4a632ac39e`。
- PRD source SHA256：`7586b2c4784b8c691d510e2be16310ed551e110af6df96b7c6aeb86152f60fbb`，固定ref与本线PRD均一致。
- 本线副本：`tests/fixtures/quality/approved-T09-873c8c0/`，manifest 与17个输入全部保持原字节；逐项 SHA 测试，未重格式化源。
- 总控独立审计路径：`iteration-control/2026-10-21-weekly-release/T09-controller-fixed-baseline-audit.md`，通知哈希 `710f17356bbe5518ce927e567003ae77791507b5e8fa477e09a6fa81af1fdeb2`。

新增测试只将 G-base 的 constraint/rule/ontology 结构显式适配到 T05 私有校验与未执行 plan，保留 `urn:ontolearn:learning:`、同一告警变量 join 和字符串 `001`。R-05/06 从批准步骤读取两个已启用规则与保存顺序，验证计划稳定及规则链提示；不求出 inferred，不生成实际 trace，不向 Store 写预期。

V-01/R-01–06/O-01 原状态全部保留 runtime-pending，50计划/54检查键不计产品完成。完整正式验收必须获取执行器实际各阶段输入/输出/依据并逐项比对。E.5 原输入亦仅作哈希校验，不将轮次指针当真实round输出。

原 `tests/fixtures/quality/g-base.json` 继续作为独立局部反例/比较测试输入，具有私有命名空间和额外显式 Alarm 类型条件，不冒充批准产品基线。正式 G.2 联验以本批准固定bundle为准；不得把两套身份混为同一项目的断言或依据。
