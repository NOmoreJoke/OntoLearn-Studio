# QueryPage 固定 507 消费小包独立静态核验

2026-10-23；结论：**通过。无阻断或剩余准备文档问题。** 两项非阻断 P3 文档问题已反馈 owner、更正并实际读回关闭。原产品 F-R3-01 没有因此修复或关闭。

## 本次核验对象

仅核 `docs/iterations/T04/querypage-consumer-507/` 的 README、manifest、五份 `.txt` 阅读副本，以及 status 本次新增的消费包 bullet。复用此前固定 507 入口证据，只读必要固定 Git 源，不以 live 11371B 需求稿作产品或契约依据。未重审 S1/42 项、未读取 T01/T08 新实现或其他树。

产品 ref `5070004ec8e3219bea33960bd88f57f1976e9cf8`、批准 base `5f910b52c69d86a1076b2032e5d3c63e715947f3` 与有界有限接收范围表述一致。

## 身份、依赖和消费说明

- 五份副本 QueryPage/draft/results/reader/query.css 的 bytes、行数、SHA-256、Git blob OID、fixedReadableRef 均逐项与固定 507 相符，副本实际字节逐字相等；sources 文件集合正好等于 manifest 五项，无额外共享源副本。`.txt` 只供阅读，未被描述为 docs 可执行模块。
- 16 项 dependencyRefs 的 bytes/行数/SHA/blob OID/ref 全部匹配固定 507。直接 task-presentation、contracts 根与内部 v2 validator、其 states/schema/registry/errors 数据，以及 package/lock/tsconfig 和宿主样式定位均存在。
- 必要 import 关系准确：QueryPage 直接导入 draft/results、task-presentation、JobView、React 和 query.css，不直接导入 reader；task-presentation 使用 package 根。内部 `src/v2` 与 package `./v2` 的 design-v2 export 不可互换。React/react-dom 19.3.1、zod 4.6.7 与固定声明一致；JSX/DOM/Bundler/JSON 编译上下文描述准确。未以这些身份核对声称重新安装、构建或独立可平铺编译。
- 样式说明准确：main.tsx 导入 style.css，后者导入 tokens.css；query.css 有颜色 fallback、两列和 max-width 760px 的一列规则。它不是 Shadow DOM，若干 selector 无 workspace 后代限定，宿主全局样式会参与。原 OBS-3 留给实际 App 接线，没有在包内冒称已隔离或已做布局验证。
- props/callback 描述对应固定 QueryPageProps。必需 projectId/catalog、可选真实历史/词汇/model/saved 输入、同项目 query job、绑定的取消标记、私有 result 与安全校验均准确。execute 返回 Promise<void>，不返回 jobId；save 返回真实 persisted ID 且更新不可换 ID；同 request/documentGeneration 回填与编辑变化提示不能代替 CAS。新建/saved 推进 generation、model 清 visual 但保留保存身份/generation 的区别保留。
- reader 仅消费四个命名 bridge，是可选读取适配器，不是 executor、writer、订阅 owner 或 QueryPage 内置依赖。bind/update 使用真实 authority；页大小 1–200、metadata 身份检查、当前发行 cursor、排序锚、可丢弃 snapshot、安全错误映射准确。Promise<boolean> 不直接当 Promise<void> 页面回调；父适配仍须处理成功/失败及生命周期。
- cancel 的 ACK/最低版本与真实状态分离，dispose 不自动取消 worker。typed RDF term、ASK 专用形状、零列及 F-R3-01 度量政策未被包内自定，I05 payload/N3/AgentSidebar 不能直接充作权威 presentation。
- status 新 bullet 准确将该包限定为获接收 507 的源码消费资料，不是 live 需求稿或新 presentation 政策。固定树当时 test-only 不推定历史无真实 executor；T01 新 asserted 后端票/旧 C4 复用核验不在本包验收，也未扩大为 public presentation/App/draft save 授权。T08 e3 AgentSidebar DOM 不计 QueryPage/I04 真实取消。完整 FR、selected/profile、ASK、网络拒绝、历史及保存边界保持。

## 发现及关闭

1. 非阻断 P3：README 两个 callback 表格行曾含未转义 union `|`，GFM 会拆坏列，导致签名/说明不可正确阅读。首次修补声明后独审读回仍为裸 pipe（execute 行 5 个、save 行 4 个），未提前计关闭。owner 后来直接重写两行只留行为，并把完整签名移至 `:38–44` 的 fenced ts 块；本次实际读回完整 union 签名和两列表格，关闭。该过程只改 README，未改源码副本。
2. 非阻断 P3：reader 说明曾写 ACK 后“重读真实终态”，可能误解该次 getJob 保证终态。owner 已在 README `:54` 更正为“随后重读真实状态；终态由后续真实观测确认”，与固定 reader 行为一致，关闭。

## 文档身份与限制

| 文件                                     | 字节数 | SHA-256                                                            |
| ---------------------------------------- | -----: | ------------------------------------------------------------------ |
| querypage-consumer-507/README.md         |   9344 | `3674fc8b4ea86ec615b9d402860a50cde3a451771094bad41f06824282ecf45a` |
| querypage-consumer-507/manifest.json     |  10259 | `2ffd48fd30a6e9e733f29416021d8993d1304663aad1afce880db25a0605cdad` |
| status.md（全文件身份；只审新增 bullet） |  13828 | `c934b91721413a9527fccdd5f72398fb00d392ec8d9a5f259261a967fee34ffb` |

本次只新增本审计，不改源码、副本、manifest、README、共享依赖或状态文件。未运行产品检查、GUI、后台、外部模型或指定双审；没有将静态消费包核验升级为真实 App/IPC/worker/Store 联验、父验收或发布授权。
