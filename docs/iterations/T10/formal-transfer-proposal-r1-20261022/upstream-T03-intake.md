# T03 固定纯设计输入接收

根提供`T10-upstream-T03-fixed-design-inputs-20261022.json`，sourceRepo为T03-mapping。12个`T10DesignReadPermission=true`文档按各自固定ref:path核原始Git长度/SHA全部匹配；另3源码仅身份支撑，没有取字节/直接读取或采用实现。精确清单见source-provenance.json。这里是已有设计/历史证据的读取，不批准新schema/runtime或重关联API。

只读agent`/root/t10_formal_prd_audit`实际全文读11份许可文档：6份source-selection核心设计/完整值/validation，以及integration-request、acceptance、project-candidate-validation、product-package-verification、product-package-identity；第12份table-interface-r2-manifest只做固定字节hash，没有展开。owner仅以获准事实和以下边界完善提案，没有读取3源码或供方HEAD。

## 1. 可依据的具体事实层级

- 私有进程内`SourceSelectionBroker`由可信main持有，注入`TrustedPicker(signal)`；选择摘要包含selectionId、project/lifecycle/generation、format/encoding/sheet、长度/fullraw SHA，无路径/文件名/单元格。openProject的scope、configure以及ReadFor各phase按对象身份管理。XLSX初选sheet=null，只inspection枚举后显式配置。
- SourceProof以同一个对象`===`和WeakMap登记检查，跨broker/旧代次/伪造同值对象拒绝。配置、预览、提交读重算原始hash；返回的确切字节不能再按路径重开。configure即使字节/选项相同也换身份/代次，旧proof不能复活。它不是持久source身份、上传授权或跨设备proof。
- 固定私有broker8MiB与两个未终态host/FS操作限制是该组件边界，不是项目包容量、全局上传/pin/GC配额，也不是全别名/同UID攻击安全证明。
- 原始Table是完整有序值：`source_hash`（原完整输入bytes SHA）、`sheet`（CSV为CSV，XLSX为所选表）、ordered fields、ordered rows；Row.number为物理行/工作表行，Cell.text均为string，kind观察值string/empty/boolean/datetime/date/number。CSV的001保string，XLSX数字不按显示样式补零；empty/空串与公式显式缓存空串不同，Table没有presence，不能倒推缺cell与保存None之差。
- Table不包含encoding/format/sourceRef/phase/selectionId/generation/长度/project-domain基线/确认/operation/producer/tableDigest。不能把source_hash当Table/options摘要，也不能从describe样本或生成事实集合恢复完整Table。
- CSV私有caller编码枚举为utf-8-sig/utf-8/gb18030/big5/utf-16，默认utf-8-sig；caller sheet=null但Table.sheet=CSV。XLSX encoding=null、sheet需实际选定，sheet=null只inspection。迁移不能静默转码或只保存hash忽略encoding/options。有限新profile不能称全部CSV能力。
- 真实parser producer三字段身份和executionSemanticsVersion尚未独立声明接入；`t03-source-parser-v1`仅建议。不能从package版本、源码SHA、库版本、I04基础设施标签/锁、hello或Job元数据拼producer认证。完整Table/golden必须由真实调用链认证；合成例子继续synthetic。

这些事实来自获准文档/旧验证，本次没有源码复测。旧macOS27 arm64 unsigned CLI包探针覆盖旧0ad，不覆盖303新边界/a4d/v3，更不证明目标macOS/Windows picker、真实worker、Store或迁移通过。

## 2. 仍需正式供给的六组合同

| 合同                       | 本提案具体要求                                                                                                                                                                                      |
| -------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 持久封存/sourceRef         | begin/chunk/seal、严格version/归属、不可变sealed身份、length/fullraw hash；内容身份与短命live lease/写授权分开；sealed后append拒绝                                                                  |
| 两段JSONL预算              | main→coordinator、coordinator→worker完整UTF-8 envelope及base64预算、协商上限/较小profile；65536原字节base64=87384 ASCII，再加封装。128块只对应8MiB/64KiB profile，不是普遍限额，不改MAX_FRAME求通过 |
| phase/代次/失效            | inspection/configure/preview/commit真实phase；configure换代次不自动把旧ref升格；新source/context/proof绑定和取消/迟到结果拒绝                                                                       |
| lease/admission/pin/GC     | 受理与revoke权威顺序、pin原子取得/释放、总量/并发/TTL、重启/unknown/fence/barrier；两个FS槽或WeakMap不能替代                                                                                        |
| 完整解析/计划与producer    | 完整ordered Table/options digest、真实parser producer、完整RDF/plan/conflicts、有界分页；提交不得消费describe或截断样本；只读inspection/preview先于最终写确认                                       |
| 正式重关联/旧operation对账 | 新选择/options/context/proof、完整预演和人确认；保owner/source-row/managed、映射版本/sourceHash/sheet/encoding；旧operation按原身份与当前读权限对账，不要求旧lease/proof/旧CAS仍有效                |

其中source对象持久化、I/O能力、canonical字段和worker装配的唯一实现owner按根责任表共同冻结；本提案不从T03领域模块越权实施共享writer/bridge/协议/锁。

## 3. 必要input/output绑定

导出迁移投影须给：固定checkpoint对应的source元数据、mapping定义/version/identity规则、owner/source-row/managed/tombstone、完整raw SHA及实际sheet/encoding/options；用户选择raw才提供受信有界字节能力。raw缺失只恢复当前，source描述不授读取权。

重关联/预览须绑定：新project/lifecycle/generation/phase、实际bytes/seal、完整options、Table/options digest、mapping definition/version、project/domain base、真实producer和完整plan/conflicts。用户写确认与admission再绑定当次确切快照、operation/request和确认范围，不把ReadForCommit当用户确认/Job受理/Store提交。

旧operation lookup先分流，使用当前合法读权限和原完整request/context/operation。已受理/已提交返回原receipt；unknown按原operation等barrier/fence查清，不能因源lease过期或新base不同丢失已提交事实，也不能先要新人确认。只有权威证明旧请求未受理且不可能迟到受理，才允许新确认产生新operation。

具体反例已进入acceptance-plan的Source段及A07：缺/乱块、同长内容变与恢复字节、同hash不同options、configure phase换代、完整Table顺序/行2与4/CSV001/公式空缓存、伪造producer、两段帧不足、pin/GC/撤销竞态、旧operation对账不依赖旧liveproof。全部为未来设计验收，不是本轮执行通过。
