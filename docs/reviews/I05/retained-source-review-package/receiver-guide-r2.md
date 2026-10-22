# R2 活跃审查入口

本 workspace 只保留一个本人 prompt，位于 instructions/；本人 contract 和 own-input-manifest 同目录。以本人 prompt 为完整任务入口。immutable/ 是共同冻结原件，data/snapshots/ 是经 manifest 安全展开且不可执行的分版本只读源码。禁止执行任何源码或测试。

必读 immutable/original-material-map-r2.md/json 的19项固定原件；活跃 M0 为 main-source-only/docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md，I03 同名 inputs 副本字节相同。历史 I05 全输入只有实际 round1/2/3 与 inputs-c1 七件。immutable/shape-process-map-r2.json 提供 a15 过程143件在四现存 namespace 的显式同 blob 映射。不存在的旧 M0/round4 指路已撤为历史，不延用。

immutable/independent-review-r1.md 是备包 R1 的独立 Fail 原件，属于共同固定备包历史；不是本轮另一指定模型的意见。历史 C1 两报告与终态在 data/snapshots/reference-C4/docs/reviews/I05/round-1/，必须阅读。本轮其他任务的 prompt、意见、过程和自动状态禁止发现或读取。

copy-ready 仅代表本地输入复制与结构预检，不代表任务创建、应用 metadata growth、设置读回、产品运行或指定 Pass。仅 reports/、scratch/、review-status/ 可写。实际设置或输入异常立即停，报告 root。
