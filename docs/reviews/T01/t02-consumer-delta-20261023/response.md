# T01 对 T02 37bd 的增量回单

37bd 的 R1–R8／C1–C8 可作为 f20 供方计划的消费精度补充；无需重写原计划。这里只列新增明确项及实际缺口，不代表已有新 M/S1/S2/CostSession 产品发行。输入固定在 `input-identities.json` 的三个 Git blob，不随工作树 HEAD 前进。

## R1–R8 的真正 delta

| 请求              | 相对 f20 新明确的消费要求及当前缺口                                                                                                                                                                                                                              |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| R1 五字段         | 即使只替换 object，仍需完整保留 identifier/labels/definitions/synonyms/examples；返回真实业务值、显式 home/absence、语言/顺序/缺失语义和实际 profile/policy。当前仅有设计，没有新产品值；L1、精确唯一、不 trim/NFC/casefold 沿用 f20，不重新提问。               |
| R2 首读预算       | 历史重开查询/历史页使用当前受信查询预算；不能免计费复用已终结写会话。新 undo 使用新操作预算。仍缺真实 issuer/bootstrap policy、同会话首读前建立方式、生命周期及所有读/parse/copy/预演/持久增长调用库存。                                                         |
| R3 全源           | **旧 C5 阶段的 source bind** 只认证 Store2 四键 RDF 域，不能认证 M/business3 或新 proof。需兼容的完整 RDF view，加与原源独立绑定的完整 M/proof；不兼容则供方明确消费 delta 和费用，不能删字段凑形状。保全部 supports、definition triples 下标、原 ID/归属/墓碑。 |
| R4 原 plan/S2     | C2–C7 提供更具体的可执行 oracle。Preview 类型/hash 不证明真实生产调用；可信编排须实际调用旧 C5 阶段的 `change_preview`，T01 从完整源独立复算/重演。仍缺同版 model/source/M/proof/plan/参数/cursor/context 的严格绑定与发行闭包。                                 |
| R5 全 Diff        | 区分按原协议受控且逐次收费的同页重试，与不能组成完整文档/确认资格的重复拼段。不新造 cursor 协议；实际页链、全段重组和失败回单仍缺。                                                                                                                              |
| R6 四事务         | 将四个漂移 case、取消/重试落实到完整观察点。拒绝要求失败事务无部分写、本请求无额外错误领域写；不要求抹除前段已合法生成的 plan/page/confirmation/Job 历史。                                                                                                       |
| R7 对账/undo      | 分开历史只读预算、原写会话、新 undo 预算；证明后续非相交变化保留，相交/引用冲突暂停。原 receipt/终态保真、unknown 不换 ID 重放沿用 f20。                                                                                                                         |
| R8 canonical/host | 回同版 schema/registry/TS/Python 和逐路径必要 delta／无需改动依据。机制 issuer/host/project/session 合同需实际提供；K 在 M1/S2 前共同冻结方向不变，正式 engine/main 与 I06 产品启用后置，不要求四基础文件先全改。                                                |

原四切点不变：`preview_changeset` 保存材料前，`confirm_changeset` 签确认前，`create_changeset_job → create_job` 首 claim 前，`commit_job → domain_changesets.commit → ProjectTransactions.commit` 首领域写前。各自在原事务内重取当前源/proof并重演；exact 已受理重试和已提交 receipt 走不可变历史分支，不能用 current 校验误拒旧成功。

## C1–C8 的消费判据补充

- C1/C8：当前全 proof、原四事务和首读前同 issuer/同会话计费方向不变，补实际 source/M/model/profile/policy 绑定及真实调用库存；revision、旧 source_ref、客户端“已计费”均不足。
- C2：恰一 removed/added，同 S/P 且 O 真变；S 为既有 individual、P 为既有 dataProperty。noop 不建空 Job；换 S/P 或更宽合法操作只是不属于此切片。
- C3：除 commands/实体变化字段为空，还比较完整 candidate 实体及外部引用不变；保五字段文本、语言和列表顺序。空 EntityChange 不证明无 metadata 夹带。
- C4：old 全部支持恰一 manual fact，index=None，原记录活动且 S/P/O 对应，owner/source_row/managed_value 全 None；不得从 RDF 去重后挑一支持。
- **判据 C5**：同 (S,P) 活动 fact 恰此一条；new Triple 不存在于原 facts 或 definition payload 的全部支持。此编号区别于上文“旧 C5 阶段”。
- C6：保绑定原 record ID，须满足获准新 typed 形状；不生成新 SPO hash/IRI 派生 ID。合法但不可表示则拒绝此段。
- C7：candidate facts 恰 base 去 old 加 new，RDF 差集一致；完整记录、全部 M/支持/归属/墓碑/control 对应，原回滚 after 全量核同，不能只比 RDF、计数或总 hash。

承接已修语义：domain/range 是 RDFS 推理声明，不是实例必填、类型或值匹配门；不加 `prop.range == literal.datatype`。range=xsd:string 不能单凭声明拒绝 canonical integer literal。原词项/datatype 白名单、ill_typed 和声明结构守卫保留；此反误拒判据不冒充正向 supplier fixture。

## 实际可供与首次小段

当前可供 f20 政策/路径/原切点、此对照和 37bd 消费 oracle；没有新可 import 产品 ref 或运行 Pass。第一次 D 小段是五字段/L1/unknown 失败表、完整比较表、首读前 issuer 与调用库存、四事务 current/history 分派，以及最小 K/host delta。只报真实签名和缺项，不将 draft 分类升级公共错误码。

后续两新路径纯 helper 可独立先行：`entity_metadata.py` 与对应测试只验证给定有限不可变材料的字段/home/集合规则；不证明真实 home、全项目覆盖或 M 写成功。其正式实施依自己的精确窗口，与此文档回单分开。

首个真实单事实机制段仍需 C/S1/K/M1＋S2 同版材料：实际五字段/home、全源 control/retirement/支持/原记录/显式引用、真实 issuer/policy 与实际费用、旧 C5 阶段的 model/service/source_projection pin及真实 Preview、S2 proof/plan/参数/确认/Job 绑定、全 Diff 页和有限失败。保 `edits[原recordId]=new.object` 与原唯一 writer/receipt/新 undo；不造第二账本、不取同名 WIP，不等完整 CRUD/Turtle/T08/T10、整个 M0 或 App 真人人机票。R9/R10 留原 I06 owner，物理 HOLD 不变。
