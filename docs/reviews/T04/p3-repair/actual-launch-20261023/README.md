# 固定507新双审收件导航

本目录保存两个真实新审查任务的创建、完整输入、原turn终态、全文模型报告及owner逐意见处置；旧554结论不继承。两报告均对完整同507有界S1给出Pass，最小原turn独审证实MiniMax存在越界请求/收据覆盖，流程不通过，不能接收为完整同版双Pass；后续处置待总控。父功能与发布完成度唯一入口仍为 [T04 status](../../status.md)。

受审产品 `5070004ec8e3219bea33960bd88f57f1976e9cf8`，批准base `5f910b52c69d86a1076b2032e5d3c63e715947f3`；两个review树detached HEAD `f2102f0738706d7ed29907ac84f10ad0a506555a`。本owner随后只追加过程证据，不改变受审产品/验收原文。42项真实产品文件逐字等507；AGENTS保持de15，仅未暂存保护M。

| 入口 | 内容与时间边界 |
| --- | --- |
| [dual-review-receipt.json](dual-review-receipt.json) | 当前收件，严格原SID/原turn终态；模型意见与controller接收分字段 |
| [Z原报告](zcode-reviewer-original.md)、[Z索引](zcode-reviewer-originals-index.json)、[Z处置](zcode-owner-disposition.md) | 全文27064B，17成员无损原件；两处报告事实纠正和观察边界 |
| [M原报告](minimax-reviewer-original.md)、[M索引](minimax-reviewer-originals-index.json)、[M处置](minimax-owner-disposition.md) | 全文38855B，31成员无损原件；N1–N7全部处置、首失败证据等级与过程披露 |
| [创建收据](creation-receipt.json)、[创建原件索引](creation-originals-index.json) | 事前时点，21成员；当时终态未知/M完整输入证明待补，历史不改写 |
| [完整输入原件索引](actual-input-read-originals-index.json) | 7成员delta：Z编号1–137重建26203B、M两Read1–136+实际尾LF重建26243B，与固定输入hash相同 |
| [Z设置](zcode-owner-task-settings.json)、[M设置](minimax-owner-task-settings.json) | 操作者事前权威回执；M文件与创建归档同3349B，覆盖后reviewer文件另在M原件包，不原位恢复 |
| [创建输入独审](creation-process-review.md)、[Z收件独审](zcode-collection-review.md) | 各阶段独立最小只读审计，不替代模型或父验收 |
| [M过程独审](minimax-process-audit.md)、[M请求审计](minimax-native-request-audit.json) | 独立原turn请求审计确认MP-01/MP-02均P2，流程不通过；无config/peer结果正文 |
| [最小取证路由](native-evidence-routes.md) | 已授权原SID/原turn精确来源；不能据此扩大为全局扫描 |

实际命令收据包含argv/cwd/UTC起止/数字exit/raw与hash。两模型独立完整check均最终TS719/Python1167、SSR14、离线真实组件DOM5通过；M缺绑定先exit1、补锁内平台包后exit0，失败原件保留。模型自建探针有缺完整收据部分已在处置中降级，不能声称全部尝试原件完备。

归档入Git的理由：本轮明确要求全文报告、原始失败、创建与原turn真实终态可恢复，避免ignored runtime消失后只剩自述hash。仅纳入本任务必要小原件与无损压缩包；大型DOM trace继续本地ignored，索引明确可恢复范围。原报告、覆盖前后设置及原编号输入不经格式化、不修改时序。新流程文档的格式/链接/hash核验不触发未变产品复测。
