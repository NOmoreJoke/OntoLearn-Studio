# C／K／I06合同差分与四P3后继准备（draft）

本件仅补已收37bd、836c53c和f20计划的未决差分，不复制36件原材料、不重测C5。根已正式接收/路由37bd，并给唯一T01纯字段helper的独立新树/5f两文件实施票；原836稿“pending”是当时快照，不回改。**该票属于T01，不是T02的adapter或两P3开工票。** helper实际产品回件尚未在本件取得；无新typedPreview/Job/undo运行、供方采用或公共启用。

## 现在只需收口的C／K差分

下面是draft职责和交付判据，非新增公共方法、schema或错误码；唯一T01 owner决定实际签名/载体与固定失败。

| 差分 | 需要固定到什么程度 | 验收边界 |
| --- | --- | --- |
| C bootstrap与覆盖起点 | 明确原可信owner已打开Store的来源/连接绑定、bootstrap policy从哪里可信取得；同一实际CostSession在本次首读/解码/复制/物化前已有，不能用costId/caller布尔或事后追认开库读取 | reader入口拒绝未知issuer/错连接/过期上下文；未知caller active transaction不进入、不回滚caller；只管理自己的事务。此为未来实际供方判据，不解除损坏SQLite/HOLD或证明任意文件物理安全 |
| C深层库存与清理 | 按同版实际调用图列S1、C5 validate/rdf_triples/bind/change_preview/digest副本、原预演/envelope/全部页及历史、confirm/claim/commit/发布的预扣项；首次失败和受控页重试不退款，不换session清零 | 所有实际调用前预扣；spent已花不退，reserved真实释放ACK才返还。嵌套cleanup与Job terminal有独立封存额度；业务额度耗尽不借ownership详情旁路侧写；真实I/O失败保首因/已持久事实，不保证必能close/terminal |
| C写会话与后继操作 | 原写请求跨分页/确认/排队/首次commit同一费用生命周期；重开对账取当前受信查询预算，新undo为新的明确操作/预算，旧历史身份仅供核真 | 精确已受理operation重试走历史核/返回原Job，不重派；新claim/首次commit仍验current。原写会话结束不能无限免费查历史，TTL到期也不重置已花额度；具体状态/释放接口由真实issuer固定 |
| K最小内部承载 | 必须在M1/S2共同冻结前给真实entityMetadata before/after、profile/version和跨原参数/响应的材料；逐项标“仅私有envelope”或“经过strict参数/响应”的proof字段，不能向旧v1塞可选字段冒新版本 | 新旧/profile混用有限拒绝，旧合法值和默认v2保留，两端TS/Python同判；内部K不等公开RPC/产品启用。schema/registry/fixtures/binding/helpers仅申请实际必要path delta，不授整目录 |
| K与C联接 | 指明哪些预算/issuer引用只在可信进程内传递，哪些请求只引用原plan/确认/Job身份；完整页/确认/接纳/commit分别如何复用真实成本上下文与S2 envelope | renderer不能签成本票/proof，也不把费用状态编码进ontology value；原writer/receipt/undo权威不复制。需真实调用图和新同版产品pin，旧423/f20和同形对象都不能代替 |

第一实施helper只校给定有限材料，不认证真实home/全项目/provenance；其回件可成为上述解释规则输入。C→非空S1→C/S1/K/最小M1/S2同版机制的原门序保持；真实业务identifier缺失不派生，domain/range不变成闭世界值校验。完整M CRUD/Turtle/T08/T10不作这些设计或单事实机制的统一前置。

## I06具名合同：只申请六个动作槽

T01负责canonical/命名engine/main与四基础文件，I06仅preload/index.ts及renderer的env.d.ts/App.tsx/style.css和获准专测。以下槽名只便于对齐，**不是T02命名新wire API**。实际最小参数/响应/失败和新供方pin仍待T01/I06回单，不给正向返回fixture。

| draft动作槽 | 应传递的既有权威和关联材料 | 页/动作失效与回单要求 |
| --- | --- | --- |
| 当前源→预览请求 | T01受信scope/project与真实完整投影；UI只提单事实用户意图，T02生产Preview和T01独立复算由批准编排完成；真实准备结果带T01版本化plan/proof身份 | 关联实际项目/session、revision与连接/request generation，不能用payload自报身份代host。完整M/全部支持及候选不变性见37bd C1–C8；旧回复不能覆盖新草稿 |
| 完整Diff页 | T01 manifest/段/offset/rawByteLength/hash/页cursor及原record/control/M/undo-impact；原字节完整重组后解码UTF-8 | 受控同页重试按原合同计费；文档重复拼段/缺段/跨proof页不得确认。不能用表格可见摘要或只读末页当全Diff/真人已读 |
| 显式确认 | 当前真实App展示的精确T01 plan/proof与completion材料，经真实人类动作进入原confirm；原confirmationRef等只由T01返回 | 旧点击、切项目/版本/连接、晚返、断线恢复均失效，不自动重签；renderer confirmed=true/模型grant不当确认。要求实际可见Diff和动作→原回单证据，不新造“真人token” |
| Job受理与取消 | 只用原确认回单创建原Job，稳定operation与真实Job/result关联；取消使用原Job/operation，不以退订充取消 | queued/running/terminal区分；接纳不等提交。晚取消不能改已提交成功，失败/取消收尾由原writer及C预留合同负责；I06不另造提交队列/重试authority |
| 响应丢失对账 | 原operation/Job/result/receipt与历史proof，当前查询预算由原可信owner取得 | unknown保不确定并阻止自动换operation重放；跨session/重开仍能核原历史，当前源变化不否定旧成功；旧对账回复不能恢复当前写资格 |
| undo | 新当前源/proof/预算、原目标operation历史证据、完整undo-impact、新显式确认与原Job | 不相交后续变化保留，相交冲突显示并拒；不伪造逆plan或回退审计revision。机制fixture确认和App真人证据分开 |

I06应回：每槽实际复用/新增的确切具名方法与DTO来源、最小逐路径delta、上述关联/失效/有限失败状态及实际验证计划；未供即标精确缺项，不重写宽App方案。机制阶段需要可信内部owner/context和K，正式生产host/位置/产品scope/App启用仍后置，但不取消任何实际调用授权。

## 四P3：最小下一候选清单（未实施）

当前C5 e5ad精确定位只读核过，路径/bytes/SHA在同目录manifest。下面不是修复Pass，也不把准备当新候选已创建。

| 原意见 | 建议最小delta／责任 | 后继验证与保留事项 |
| --- | --- | --- |
| digest入口边界 | T02新树ontology/service.py:105的snapshot_digest优先改为私有_snapshot_digest；仅更新137/225两内部调用，__init__.__all__原本未导出，保持不增导出。两调用位于validate之后；新adapter只用有校验的公开入口/require_current，不直接调裸digest | 合法输入摘要字节/Unicode保留语义不变，既有公开入口坏Unicode固定诊断继续成立。无需新增“函数名称私有”镜像测试；实际adapter结合真实源验证。若最终选择新增validate或meter，另列路径/成本profile变更，不当本最小重命名已覆盖 |
| localGraph页签/memo | T02新树OntologyPage.tsx:105，hook保持无条件调用，计算callback内按graph页签门控；缓存依赖覆盖tab/selected/完整图输入，图分支做相应非空守卫。若以view引用作依赖，I06必须按不可变当前快照在输入变化时提供新引用，否则先修精确输入合同 | localGraph(view, selected,12)现有节点/边/排序/total/truncated语义保持；切对象/页签/更新图输入结果须当前，旧21项合成呈现行为作新候选回归，不能代App/真人。不新增第二graph算法、不量化性能或声称线性 |
| 深链ancestor Set成本 | 维持已接受非阻断观察；当前不改view-model.ts:27–60的遍历/复制，不造Q5阈值 | 待真实数据规模/设备/批准阈值再评估；索引/tree useMemo事实保留，不把整树说成线性或给未测提升 |
| 历史交付指针 | 旧delivery/stage及既有审查输入不改；下次完整新候选包的当前指针/证据索引另指新product/process | 旧文原误导点仍属历史原件，不声称已修；已正式接收的37bd/836状态在本新记录表达，不回改其当时pending |

真正T02下一候选仍须根精确新树/累计base/C5逐路径采用/两旧路径及必要专测授权，并等新同版供方的非空真实回件后才运行typedPreview/Job/undo联验。四P3中的前两项可先准备如上最小delta，但本件没有写代码、建立候选或运行旧C5。原双指定新审、CI/正常合并/远端发布及父Goal边界不变。
