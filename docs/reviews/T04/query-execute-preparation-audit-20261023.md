# 正式 query.execute 集成准备独立静态核验

2026-10-23；结论：**通过。无阻断或待改的准备文档问题。** 初读发现的两处非阻断 P3 文档歧义已由 owner 更正并经本次逐处复核关闭；这不关闭原产品 F-R3-01。

## 范围和依据

全文核验 `docs/iterations/T04/query-execute-integration-requirements-20261023.md`、`query-execute-source-evidence-20261023.json`、`docs/reviews/T04/controller-r3-limited-acceptance-20261023.json`，并核验 `status.md` 本次顶部增量及其直接相邻的最新摘要。status 全文件 hash 仅固定文档身份，不表示重新审核全部历史。

复用此前固定产品 `5070004ec8e3219bea33960bd88f57f1976e9cf8` 的 renderer、reader、results、preload、contracts、TaskService、App 静态入口证据；另只读核对 coordinator job.create 分派和 save_intent 的必要片段。源码身份文件所列 12 项 bytes/SHA-256 均与该固定 Git blob 相等，行号锚可定位。本次只是入口及身份核验，未重复 42 项产品审查或 S1 运行验证。共享基线保持 `5f910b52c69d86a1076b2032e5d3c63e715947f3`。

本次总控直接回执由 owner 任务透传作为接收事实依据；未读取其私人审计、其他树实现或后台。

## 核验结论

- 入口描述准确：query.execute 仍 design-only；coordinator job.create 限 test mode 的三种 test 能力。既有 DesktopBridge/preload/main 命名读取、订阅、取消入口不能冒充正式 execute 或保存方法。QueryPage 回调仍是私有 UI 适配意图，不能直接获得正式 jobId、事务提交点或执行授权。
- presentation 缺口与职责明确：固定公共 result 的封闭形状没有查询列、实际 SPARQL 等展示字段；私有 presentation 必须来自批准的权威同结果来源，不能由当前编辑器、模型草稿或 fixture 补造。未来结果 metadata 唯一 owner 是 T01，T04/I05 按批准契约消费；本文件未新建公共 schema 或 runtime 入口。
- 保存边界完整：load-base/CAS、preview/确认/commit、真实 persisted ID、响应丢失按原 operation 对账、恢复/撤销及失效均交 T01。组件保存身份与 generation 防护没有被描述为 Store 或正式事务；点击保存不能拿最新 revision 掩盖旧载入依据。
- 绑定、分页和取消要求与固定入口一致：真实 project/result/snapshot/scope/parameters 身份、main authority、引擎发行 cursor、单页/页项上限及跨页排序；取消 ACK 与真实终态分离，已有任务订阅/恢复链须接上。
- 计量、RDF term/ASK 与错误分类列为未来唯一契约需明确的供给，不冒充固定 507 已具备的字段或语义。ASK=false、空 SELECT 与零列边界没有新增默认答案。
- supplier 状态准确限定：没有已接收可声明正式 query.execute/Store 结果 metadata 联验通过的 supplier。T01 固定 stageParent 只是定位，未冻结 typed-bridge proposal 的首 lint 状态限定为总控本次回执时；两者都不得作为可消费实现。本次没有读取这些路径。
- F-R3-01 保持 P3/非阻断/未修未关，延期至正式结果 metadata 度量及错误分类契约冻结后处理。draft D1 不扩大为结果计量政策。既有 OBS1–6、零列/ASK 及 16 个 owner 合成讨论样例边界保留；没有把讨论输入当实际业务接口执行。
- 下一步围绕真实项目输入、显式执行、本人 query job、权威 metadata 与真实分页推进，再接保存/恢复和失败边界。未要求等待无关全 M0，也没有重复 S1、无变化新审或当前产品修改授权。
- 有限接收回执准确记录第 5 组同 base→507 完整有界 S1 双方 Pass、新增创建 0、接收 pair +1；不升级为全 native 合规、零曝光、父验收或 push/PR/merge 授权。旧 R2 过程 Fail 与冻结原件保留，原父 Goal 的 blocked 记录未被改为完成或恢复。

## 本轮发现及关闭

1. 非阻断 P3：`status.md:7` 的最新摘要原仍写“待 T00/I05 及相关唯一 owner 判断”，与最新 T01 future sole owner 归属不一致。owner 已同步为 T01 未来唯一责任、契约冻结后 T04/I05 消费；实际读回一致，关闭。
2. 非阻断 P3：requirements 的两个 `.worktrees/...` 定位原未指明相对根，可能从 owner 树错误解析。owner 已在 `:33` 改为完整绝对路径，并给未冻结/首 lint 状态加“总控本次回执时”；实际读回一致，关闭。未为验证定位而读取未批准实现。

## 本次已核文档身份

| 文档                                      | 字节数 | SHA-256                                                            |
| ----------------------------------------- | -----: | ------------------------------------------------------------------ |
| requirements                              |   8195 | `4983de7b152b274aa8299b20edc359b60123e9617243c6c6895bc554e3bf303b` |
| source-evidence.json                      |   2904 | `c352823f6f5620eece4216c9945f1c7591b584eb36a52fdda3135614373822c2` |
| controller limited acceptance             |   1464 | `0477e12278f1344627cb8f478deb4a9881bb60d05061106cbc58af1f5335a1a8` |
| status.md（全文件身份；只审本次顶部增量） |  13187 | `29f3a77886c449c2c11ac9009caa319339a7ed8e0ba4ddc4f4d1417ac10dc320` |

未运行产品测试、GUI、后台、外审或模型请求；未修改产品、原件、上述四文档或共享文件，只新增本审计。本结论为集成需求准备文档核验，不是正式执行/Store 联验、指定双审替代或父功能完成证明。
