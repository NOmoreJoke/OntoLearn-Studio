# F1 / P3 精确修复处置

本次只修复新增显式 null 属性没有进入 profile 精确变更索引的问题，申请原 fresh reviewer 对新候选做精确 delta 复核；作者不自签关闭 F1，不将首审 NEEDS_CHANGE 改成 Pass。

修复 base 为已封存首报告的 `289fa9877e864a5ae5aa4f3b0593f6d454dce351`，原完整候选 `d355d384470d6de30c28229945cb77a65cca3dd4`、原 candidate-manifest、首报告、作者全部首失败/日志保留。唯一既有规范索引改动是 `profile-change-index.json` 增加 `#/independentParentProfile` 一行：`old=null`、`new=null`、`newProperty=true`，由 newProperty 区分旧键不存在与新键显式 null。descriptor 本身没有改动。

两项文档工具改动：

- `materialize-documents.py` 的变化条件先比较键是否存在，再比较值；不再把 absent 与 null 仅用 get 的相等结果合并。本轮未运行生成器，没有重新生成或覆盖原候选、规范正文、旧日志或首报告。
- `protocol-selfcheck.py` 新增 presence-aware 顶层全集核验：实际变化键和索引恰一一对应，拒绝缺项、额外项、重复 pointer；逐项核 old/new 值与真实 descriptor、newProperty 必须为实际键存在关系对应的布尔值。原全部 schema、1,241字段、26包/六直接项/来源和45/33/58 guard断言及26个反例保留。

新增 `F1-repair-profile-index-negatives.json` 的三个有限反例分别删除新增 null 行、在新 descriptor 合成一个没有索引的 null 新键、把新增 null 键伪称为旧属性。增强自检首次 exit0，实际核21个顶层变化，三个反例均被 presence-aware 断言拒绝，原26个反例继续被拒绝。完整 stdout/stderr 另存 F1-repair 新日志；没有覆盖原 selfcheck-first exit1 或首审工具失败记录。此为有限 stdlib 文档检查，非完整 JSONSchema 引擎验证，非产品/loader/运行证据。

旧D0/D1、descriptor/四schema/字段表、依赖规范、guard账与合同、protocol/consumer/业务carrier接口、所有新 actual pin 和执行权均保持原字节。没有新增 G02/G03 schema，没有安装、产品 import/compile/build、resolver、probe、archive/native/GUI、fee/caller 工作。作者仅在授权的两个新 prefix 精确修改三件既有文件并添加本修复证据，未stage/commit；原T03固定新候选后请原reviewer复核。
