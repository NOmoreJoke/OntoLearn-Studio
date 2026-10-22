# I05 查询供方事实定点收件独立核验

2026-10-23；结论：**通过。未发现阻断、事实扩大或需修改的非阻断问题。** 本次只确认供方事实在 T04 文档中的准确收件；不确认正式 query.execute/Store 联验通过。

## 范围与直接证据

全文读取总控指定 `outputs/20261023_i05_query_execute_supplier_facts/` 的 supplier-table.md、receipt.json、manifest.json；核对当前 Git diff 中 requirements/status 的本次增量及新增 `i05-supplier-facts-intake-20261023.json`。未读取 I05 源码或其他工作树，未重新核验 12/42 项源码或 S1。

三份供方文件的实际字节/hash 均与授权消息和 intake 逐项一致；manifest 的两个成员与 intake 前两项一致，manifest 明确 selfExcluded：

| 文件              | 字节数 | SHA-256                                                            |
| ----------------- | -----: | ------------------------------------------------------------------ |
| supplier-table.md |   5299 | `142e04041783ced4661469d858bc1a5ecead13189904aed863e00c391a194117` |
| receipt.json      |   5429 | `c9b30ce323b01ee7313f264ca956ac15c17dde3b45f8ce25db367d1bf6661572` |
| manifest.json     |    404 | `50c6a406a2713b591ba2c7477187c2873b6e5780f8a474f4aa4b90af71eaa6da` |

receipt 的 sourceRef 为 `9d86ef183b2bfc4d2ac6f1583ceb9a5b29cdf876`，库存产品来源为 `2cf0c3328de464e15a3fa9cdbfdf6aa88d0b4a64`；共列 12 个函数 AST 相同的声明。intake 对应准确，但这仍是供方静态核对结果，不是本次独审重新计算 AST 或运行算法。receipt 的 `overall=NotPass; facts only, not formal query integration acceptance` 保持其含义，未被收件改判。

## 增量事实与边界

1. requirements 新增段和 status 下一步准确表达 algorithm exists / formal wiring pending：真实 RDFLib SELECT/ASK、本地词法/代数检查、context 外联拒绝、build_request/execute_request 及 payload+rows 的存在来自供方表，不被升级为 T04 新运行证据。表中的 build_request 结构/摘要核对与 execute_request 实际解码/投影/查询仍有区别。
2. 所列函数名/行号与 receipt、供方表对应；payload 内容不被视为可信 producer、正式 result/job ID、成功终态、Store 认证或权威 presentation。项目授权、可信输入、owned worker、硬超时/取消、实际 capability implementation、完整 payload+rows 原子发布与迟到围栏均仍待真实接线与接收。
3. context 外联拒绝没有升格为 OS sandbox、其他线程/作用域全局隔离或正式链真实网络拒绝验收。ASK、真实网络拒绝及范围/推导的完整验收要求仍保留。
4. “纯 asserted 无需先完成整个 profile producer”只区分实际依赖，不把 asserted 当 selected/profile 替身，也不降低 FR-400–404。新 finite7/8 typed profile 的真实受理、来源、reader/pin/累计算额和新只读 scope 仍未闭；旧 selected 格式和 finite6 通过不能替代这些接口。
5. 当前隔离树 test-only coordinator/worker 不抹去旧 C4 真 worker 的历史证据；T01 正核复用及 8.3 先冻结、不混新功能按总控本次授权记录。本次没有自行核旧 C4 树或推定可复用结论，也没有 whole-ref 采用供方树。
6. T01 未来结果 metadata 唯一 owner、T04/I05 消费、F-R3-01 原 P3/非阻断/未修未关及契约冻结后处理保持；历史选择、正式保存/CAS/对账、真实 ASK、实际网络拒绝和完整 FR 验收没有删减。没有新增公共 schema、私有替代 producer 或默认结果。
7. intake 如实保留初次 metadata hash 采集缺 cwd、找不到 `.venv/bin/python` 的记录，限定为 metadata-only 失败与修正，没有把它计成产品运行或审批拒绝。本次独审只是确认该声明未扩大，未重演该历史命令。

## 本次 T04 文档身份

| 文件                                               | 字节数 | SHA-256                                                            |
| -------------------------------------------------- | -----: | ------------------------------------------------------------------ |
| query-execute-integration-requirements-20261023.md |  11371 | `6c700decd749d6009a8be2473c8abc58be249e1e2c2ff7f07c8cb7dbb76ff823` |
| status.md                                          |  13415 | `180b952d24ac0eb95919b71b9e81c1104fb2d3838fba862de232d281f3f2c929` |
| i05-supplier-facts-intake-20261023.json            |   2550 | `025cf3e0618989a102f8745a826803810655332090838243b1c5999660d9d611` |

全文件 hash 仅固定本次文档身份；审查对象是本次 delta，不表示重审此前历史。此前 query-execute-preparation-audit 作为前时点记录保持原件。

未运行产品测试、CUA/GUI、后台、外审或模型请求，未改产品/源文件/共享文档，只新增本审计。供方静态事实收件不是正式 supplier 接线或父验收、发布、Goal 完成授权。
