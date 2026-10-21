# I06 → T01/T03：来源快照传输选择与准入边界

2026-10-21。**I06 接受可信 main 选择、真实字节复验和对象身份 proof 的设计边界；选择在唯一 canonical JSONL 内有界分块传递不可变快照，不传源路径，不扩大原帧上限。** 以下为本线明确提出的冻结输入，不是已获 T01 接受的公共 schema、文件交接或已实现能力。主分支/依赖仍只消费批准5f；没有复制T03实现、改共享代码、运行测试或GUI。

已读T03当前固定流程 `b86833dc40ae9f5e3b975e1e23c9af254d6ec431`，产品 `8c904b57b7c5aac7b2b19273e679e7e36304dd1c`；design SHA `5ac818da2cc702e2899fb9f10fcc0f0bcdb8a1420b9bf1d71ccc199e055a66cc`、validation SHA `8619d28e8ba9a9cacfbc9ffddae4c92821f6ecfc2b5f23986c3e694e1c12e30f`。其32FS/662TS/1052Python为原线验证记录，本线未重跑；真实parser/枚举、transport、IPC、Job/Store/native仍未接线。旧f2c/2f7仅历史。

## 1. 唯一传输与主进程对象

1. main持有唯一broker及当前scope/proof实际对象、预览和接纳账本。renderer只可经冻结后的具名接口请求选择/配置/预览/确认/取消，不传路径、原始bytes、proof、任意RPC或picker回调。相同字符串或同形对象不构成权限。
2. main对 `readForInspection/readForPreview/readForCommit` 得到的独有字节副本固定所有权，按实际SHA/长度核对，再以同一engine会话的canonical消息分块送到coordinator。副本不能作为可变共享缓冲交给别的消费者；engine在seal时独立核完整字节SHA。SHA只覆盖原bytes，不把encoding/sheet混算成“文件SHA”；解释选项另作精确绑定。
3. 不新增HTTP/TCP端口、通用路径读取、任意文件IPC、第二协议目录/validator或第二项目可变权威。不把8MiB/base64塞单帧，也不借测试fixture/环境变量启用正式能力。
4. 正式parser及Job只读取已seal、匹配实际SHA的快照。`readForCommit`成功后磁盘可能再变，承诺处理明确确认的那个快照，而非执行时磁盘仍最新。任何阶段均不让worker按原source path重新打开。

## 2. 分块profile及严格字段

本线选择固定块方案；数值及具体方法名须T01在同一canonical一次接受/冻结，不在本线私造运行schema：

| 项          | 冻结提案                                                                                                                                                                                                                            |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 原bytes上限 | 8,388,608；允许host更低上限，不能更高。0bytes可传输，空CSV/XLSX是否合法由真实parser决定                                                                                                                                             |
| 块          | raw 65,536B；非末块必须满块，末块1–65,536B；0bytes为0块。最多128块                                                                                                                                                                  |
| 编码        | 严格canonical base64；满块87,384 ASCII字符。先限编码长度，再严格decode、核decodedLength与chunkSHA，重新编码须逐字相同；拒绝空白、非canonical padding、错长/错块                                                                     |
| 帧          | 完整UTF-8 JSON envelope/参数/响应必须满足实际协商maxFrameBytes，且不超过原262144上限（LF按原reader规则）。不能只核raw或base64。若实际预算容不下本profile所需帧，安全拒绝此source传输，普通本地能力保持；不自动放宽limit或悄改块规则 |
| 顺序        | uploadId精确绑定当前session/project；index从0、offset=index×65536，expectedLength=min(65536,total-offset)。错序/重复/越界/额外键拒绝并使该未接纳upload终止，不以覆盖写修复                                                          |
| 背压        | 全main最多1个未终态begin；每upload最多1个未结chunk请求，等严格匹配ack再发下一块。writer队列/实际写完回调纳入预算，不能一次排128帧或连续begin绕过pending上限                                                                         |
| 总临时预算  | 每个受控main/engine所有窗口/项目合计最多2个未接纳lease，pending-begin/receiving/sealed/admission未定均占；按begin声明长度预留、合计≤16MiB raw。取消未真实settled/关闭/清理者不提前释放                                              |
| 寿命提案    | receiving idle≤30s、总传输≤120s；sealed未接纳预览lease≤10min。到期失效并使对应预览不可提交，不自动延长/自动确认。T01须给单调时钟/取消/清理实件与精确状态                                                                            |

16MiB只指未接纳快照raw配额，不是整体RSS或XLSX解压预算。T03真实parser的压缩包展开、行列、字符串、表/预览字节、时间/内存界独立保留；仍由唯一受控worker资源边界执行。持久输入的总磁盘配额/保留政策由T01冻结，不能将记录移出临时预算就获得无限存储。

建议同canonical的内部方法与形状（名称为冻结候选，当前均未注册runtime/Agent能力）：

| 方法                     | params / result的必需含义                                                                                                                                                                                                                             |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `mapping.source.begin`   | main生成的transferAttemptId及解析的projectId、sourceLifecycleId、selectionId、generation、purpose=inspection或preview、format、encoding、sheet、byteLength、sha256 → 新uploadId/receivedBytes=0/nextIndex=0；严格项目权限、实际会话和全局配额后才预留 |
| `mapping.source.append`  | projectId/uploadId/index/offset/decodedLength/chunkSha256/base64 → 同uploadId/receivedBytes/nextIndex精确ack；无path/proof/renderer回调                                                                                                               |
| `mapping.source.status`  | projectId/transferAttemptId → 该同session尝试的pending/receiving/sealed/released/expired及有限进度/引用；只查询、不新分配/不延长寿命，跨项目/旧session不提供记录                                                                                      |
| `mapping.source.seal`    | projectId/uploadId → main-only snapshot lease引用及实际长度/SHA/完整解释选项；总长度/块数/完整SHA核对全部成功，才可交parser，不创建Job/claim/确认                                                                                                     |
| `mapping.source.release` | projectId及精确attempt/upload/snapshot lease引用，严格互斥三选一 → 取消处理中/已释放/已失效或已pin状态；不得影响已正式接纳的持久输入。未知/跨项目/旧session引用不成为可读凭证                                                                         |

所有id/数值/字符串/编码/sheet/错误均由T01共同受限词汇严格冻结；表中概念不允许宽松object或任意extra params。sourceLifecycle/selection/generation只是main产生的绑定标量，**不是SourceScope/SourceProof对象的序列化证明**。原内部SourceFailure.kind须由唯一catalog映射固定code/key/retryable/有限params，不能原样透传cause/path。传输方法不Agent eligible，也不直接暴露renderer桥。

begin前main先同步预留两lease/16MiB中的名额，再进入任何await；pending-begin及ack丢失unknown都持续占用。transferAttemptId是独立传输尝试身份，不是正式operation。server按当前session/project/attempt及完整descriptor精确去重：相同begin只返回原尝试，不另分配；改变descriptor或跨项目拒绝。server在异步暂存前原子登记pending及配额。begin超时/cancel不得换新attempt补发；当前scope仍有效时仅按原身份status对账，失效则受控release/清理，不安装迟到成功。未确认结果不能提前释放本地预留，旧controller/broker也不能被重建绕过。

begin尚未返回uploadId时，以原transferAttemptId执行release；server须按同writer顺序建立取消tombstone，使迟到begin不能再分配或复活。收到取消意图不等于完成释放：pending begin、writer及临时文件实际终态确认前继续计配额；release结果须明确取消处理中与已清理。

status的not-found本身不能证明旧begin不会迟到：T01须给同writer的dispatch/barrier或原写入已实际终态及server清理证明。只有明确未发出、server已确定释放/过期且无迟到写入，或原session/进程已终态并按受控清理处理时，才能按各实际资源终态释放。磁盘未清理的孤立暂存仍受T01存储quota计账；不因逻辑abort把它算消失。具体幂等/tombstone保留及未知状态界限在唯一合同冻结，不在main另造durable claim。

seal前临时片段可使用T01受控暂存；不会产生正式domain revision/Job/operation claim。seal后的同SHA去重只可共享精确bytes，不共享项目/会话/选择/选项/parser/预览/人工确认权限。主机当前8MiB声明、单个快照hash或一个opaque ref均不是项目读取授权。

## 3. inspection不能变成preview或Job

XLSX初选sheet=null是合法未选表状态。新私有 `readForInspection` 只给main bytes/summary，**不签proof**；旧readForPreview的sheet前置继续保持。流程为实际inspection快照→真实 `xlsx_sheets` 有界枚举→用户选真实sheet→configure新代次/失效旧记录→readForPreview签main对象proof。不能填虚构sheet/空字符串绕关，也不把私有32FS测试说成实际枚举已通。

inspection用途lease仅用于冻结的只读枚举/检查，不可直接用于mapping admission、人工确认或模型外发。preview用途必须有实际选项及broker proof，仍只证明来源；后续表/映射/版本/人类确认另行绑定。模型隐私始终独立，文件选择/本地上传不会授予gateway grant。

## 4. 确认、发送切点及持久pin

正式计划须由真实parser结果建立，绑定项目/domain base/实际依赖、来源SHA/长度/选项、表摘要、规范mapping/变更计划与parser implementation、preview身份、用户实际确认、operation。hash编码/确认指纹使用T01/T03共同冻结规范，不复制私有materialCanonical充当新wire真相。

提交前调用 `readForCommit(scope,同一proof对象)`，其结果B须与预览快照A的实际SHA/长度/选项一致。可让Job消费已seal的同源A；若lease到期或engine会话变更，不能凭hash捞旧handle自动提交。重新上传后的完整预览/确认绑定如何更新必须依冻结合同，不能把旧确认偷换到新输入。原完整operation的重试身份不可因临时transferId变化而静默改写；T01需明确稳定内容计划与临时交付lease的指纹边界，未知接纳先对账。

| 时点                     | 明确语义                                                                                                                                                                                                                                                         |
| ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 未dispatch               | main串行检查当前scope/selection-generation/完整预览/确认/源proof及复验结果；任一await后失效则停止。最终实际写帧前必须有同步可信guard或等价可证明fence；现有EngineSupervisor.request没有调用方guard接口，需T01与I06冻结最小接线，不能仅靠调用前一次检查冒称已保证 |
| admit已dispatch、ack未到 | 进入提交未定，保留原operation/计划；重选/关闭/取消只撤销未来旧预览资格，不能保证跨进程零Job。按原operation查询accepted/committed；不新operation重放，不伪称取消成功                                                                                              |
| 正式admission            | T01先使精确不可变bytes可耐久读取，再在原Job/Store/claim同一准入事务原子绑定/pin输入、完整plan/CAS/确认/operation。DB失败留可回收未引用blob，不留下假Job成功；DB成功后release/TTL不得删输入                                                                       |
| accepted以后             | 按真实Job cancel/提交/恢复边界；旧源文件随后改变、UI重选或新engine session不改变已接纳Job输入。已提交事实与历史保留，不能用broker.cancel抹掉                                                                                                                     |

new session/TTL只失效未接纳的transfer lease。持久source artifact与未接纳lease分别建模：accepted Job恢复从原不可变持久引用读取，绝不重开原路径。release/expire与admission竞争须由同一T01 owner给原子状态迁移，pin赢则保留；release赢则拒绝admit；不确定时先对账，不先unlink。

## 5. 实际最小缺口及责任

| owner                               | 当前需要接受/交付的精确项                                                                                                                             |
| ----------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| T03                                 | 新固定broker/inspection边界、实际parser/`xlsx_sheets`及表/映射摘要/implementation、真实8MiB与解压等独立限制；不把旧f2c候选作为最终接线依赖            |
| T01 canonical7/main-engine          | 单canonical五方法或等价同协议方案、实际协商profile/安全错误、session/project权限、pending/背压/最终写帧guard；只有同源实现验证后注册runtime           |
| T01 storage/project/Job/coordinator | temp与持久artifact引用/预算、durable pin与原全局claim/CAS/确认、release race/丢ack/重启对账、只读inspection与正式Job边界；不建第二项目DB/Store writer |
| I06余六及待登记私有adapter          | 实际TrustedPicker、唯一broker/账本、具名桥、主进程最终guard/撤销与只读恢复；具体新增main/mapping私有路径先由root确认与T03目录owner，无自动路径交接    |

需T01给出：稳定内容计划/临时lease的精确指纹、持久quota/原子发布与清理、最低帧profile、有限错误、final-write guard及接纳状态/重试fixture。缺这些实件时source方法保持不可用，不用mock seal/假Job关闭门。worker.py、protocol reader、resources、原测试、CI或构建锁的新增需求逐路径交接，不从T01十二共享或T03构建四推导授权。

必要验收包括：0/1/65536/65537/8MiB及超界、错base64/块序/长度/hash/extra字段/小协商帧、pending-begin/丢ack/迟到成功及全局2lease/16MiB与abort未settled、inspection无proof/真实sheet枚举、源变/选项变/同UUID重开/旧回调、真实parser→预览确认→复验→Job→Store、dispatch前取消与dispatch后丢ack对账、pin/release/TTL崩溃竞态、源码/新实际包同输入及真实native picker取消。路径、schema和owner先冻结；本提案没有运行这些用例，不以旧e2c/9fc结果代替。
