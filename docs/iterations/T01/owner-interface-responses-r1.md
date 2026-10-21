# T01：跨 owner 接口答复 r1

仅设计答复，不修改当前 CAS 候选、公共协议或文件责任，不消费未批准实现。“接受”只覆盖 T01 的 Store/canonical 责任；其他 owner 的实现、值政策和验收仍须对应决策。实际状态唯一见 [status](../../reviews/T01/status.md)。

## 1. T05 D6/D7/D9、M12–M16 与 P7/P8

已全文读固定 `41210534972d50965a2a4ce259660658e3bbdd81` 的 owner-decisions-after-interface-facts.md，SHA `6650363f0195f1a2cb21e2eee2dfe5a072d698275ca3a2f5ef389615fe92a17f`。只使用自身批准 Store/JobStore 和该事实/设计材料，未读取 C3 未批准实现。

| 编号    | T01 明确答复                                                                                                                                                                                                  | 实施前精确证据或后续                                                                                                                                                                                             |
| ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| D7 / P7 | 接受严格三字段分区：executionSemanticsVersion、engineVersion、dependencyLockHash 全等；current/historical 新消费均不豁免。原身份历史只读另保留，不能重签新 producer                                           | 三字段各单独改变、historical 新消费、原身份历史读回、canonical projection/derived 关联分别验证。C3 finite5 未批准，不删 equality guard                                                                           |
| D6      | 接受完整 firing 认证及全 heads 原位置认证后再投影单 result。原 rule 版本/digest、binding、when 位置、比较政策/值/结果、全部 heads、basis 和 producer 来源均须绑定。阈值不是事实 basis，不调用 reason 重算历史 | I05 给同一真实执行器的版本化 firing 载荷和 source 投影；T05 单组校验不证明全图匹配完备。T01 join 成功 job/result/inputSnapshot、完整 implementation、依赖/定义集合及 payload/rows hash。当前没有已批准多head载荷 |
| M12     | 接受“新 selected 消费的实现不兼容 → UNSUPPORTED_CAPABILITY {}”作为未来适配决策，不借 protocol VERSION_INCOMPATIBLE。现有通用 create_job derived 门实际为 IDENTITY_CONFLICT，本次 CAS 不改码                   | 固定26报告没给 prepare_semantic_request 的真实异常类型/DTO，需 I05 实际路径和 golden；届时在明确边界适配，不误称已接线                                                                                           |
| M13     | 接受授权后确无 result → NOT_FOUND {resource:result}，当前 result_get 已如此处理                                                                                                                               | 授权先于存在性；跨项目或无权限不能据此推断存在。可信 result 行已在但 producer 丢失属于 M16                                                                                                                       |
| M14     | 接受真实 payload 已驱逐 → PAYLOAD_EVICTED {resultId:权威id}。当前 result_get 保留 evicted 元数据，实际取 rows 时才抛码                                                                                        | 分别验原身份读、分页、缺元数据；不改成 NOT_FOUND，不从 caller 合成 resultId                                                                                                                                      |
| M15     | 接受可信主进程/会话授权失败 → PERMISSION_DENIED {}，先授权后查存在                                                                                                                                            | Coordinator.allowed_projects 是实际门；project 映射和 caller 声明不是 actor 授权。新 producer/read 入口须提供可信 scope，不假装 JobStore 已有用户权限系统                                                        |
| M16     | 接受可信已存 producer/hash/firing 一致性损坏 → INTERNAL_ERROR {}。caller 伪造先走真实授权/身份门，不归 verified-user 错误                                                                                     | I05 给真实内部 failure 类型和安全 origin；未知组合不自动映射用户错误，不回传原值或异常                                                                                                                           |
| D9 / P8 | 接受失败定位采用独立受限诊断资源，不把失败藏在成功 rows，不借 OWNERSHIP_CONFLICT.detailRef，不向旧 params 擅加 ruleId/index                                                                                   | 下方公共3提案待 canonical/I05/T05 接受；旧协议2仍缺完整载体                                                                                                                                                      |

诊断提案：在批准的规则输入错误分支增加专用可选 `diagnosticRef`（UUID），新增只读业务方法 `semantic.diagnostic.get(projectId, diagnosticRef)`。资源不是成功 result/current 或 firing 证明。可信 owner 在失败边界持久绑定 actor/scope、project、原 request/operation、可空 job、inputSnapshotId 和规则来源；来源必须是实际 stored revision/digest 或实际 preparedPlanRef/digest，不能认证 caller 自报。返回固定版本、真实规则 id/source 和有限定位 `{section:when|comparison|head,index:非负整数,reason:批准有限枚举}`；无可信位置不伪造 index，无 operand、原值、路径、堆栈。读取重验授权。失败 Job 与提交前失败均可关联，不能为运输定位制造 succeeded Job。资源数量/保留期和分页上限须测量后冻结，不能留无界数组。这是 P8 明确待批准的 schema/registry/errors/fixtures 变化，尚未写公共文件。

D1–D5 的 term/value/精度/日期/Q6 和 D8 的预算值由 I05/T05/有权产品负责人选择；T01不以保存 opaque payload 代替决定。P2–P6/P9/P10不因本答复扩大责任。

## 2. T03 来源字节、确认与生命周期

已全文读 process `b86833dc40ae9f5e3b975e1e23c9af254d6ec431` 的 source-selection/design-and-handoff.md，SHA `5ac818da2cc702e2899fb9f10fcc0f0bcdb8a1420b9bf1d71ccc199e055a66cc`（product `8c904b57b7c5aac7b2b19273e679e7e36304dd1c`）。接受 readForInspection 的 main-only 复验字节、无提交 proof；XLSX 先真实枚举再选 sheet，不能用伪 sheet 调 preview。broker 对象身份/scope、每次 SHA、最多两个实际未终态操作及取消边界保留，不等于已采用实现。

实际本树：main→coordinator 与 coordinator→worker 都是有界 JSONL；Coordinator.execute 写一次 parameters 后关闭 worker stdin，worker._execute 只读第一帧。JobStore.put_blob 单值也限262144字节。8MiB文件不能塞现帧、不能按路径重开，也不能只改main端就称接通。

T01提出同一协议内分块：原始每块64KiB，base64约87.4KiB并保留完整 envelope 预算；main-only上传绑定 project/lifecycle/generation、总长度/SHA和固定序号，每帧仍核完整 maxFrameBytes。seal重算全部字节/长度，拒缺块、乱序和重复冲突，之后才给不可变 sourceRef。可复用同库 job_blobs 存块/manifest（128块覆盖8MiB），但须新增严格版本化 source 类型、归属、在途/总量限制与回收/pin策略；任意 put_blob 不是受信 source。字节不返renderer，错误/日志不含内容或路径。

预览绑定 sealed sourceRef、SHA、encoding/sheet、真实解析表摘要、规范mapping定义digest、project/domain base及真实Store预览/确认。提交前 main 调 readForCommit 复验原实际 proof，必须与已确认 SHA/options 等值；Job只处理该封存快照，不再打开路径。全局 operation 固定实际请求/确认；重选、configure、取消、项目换代使未受理授权失效，迟到消息不恢复旧 proof；已提交后只按 receipt 协调。

worker 也须在现有受控 stdin JSONL 接收绑定分块，seal核验后解析，保留 memory/time/cancel 预算；解析结果/plan超过单帧时仍需受控分页/分块。不扩大 MAX_FRAME、不另开HTTP/任意文件通道，也不在 coordinator 事件循环重解析以跳过隔离。

精确责任缺口：T01已有main/engine.ts、coordinator/JobStore/canonical；I06保留main/index/task-service/preload/env/App/style；T03负责真实parser/构建/broker。**worker.py尚未交接**，第一帧后关闭语义不能由T01越权改写，需总控指定唯一owner或移交后冻结受控消息/取消/结果合同。protocol.py的generic bounded decoder可复用，暂不申请改MAX或无关资源文件。32 FS、旧S1或本CAS都不能代替CSV/XLSX→确认→Job→Store及真实生命周期联验。

## 3. T10 固定业务投影、必要闭包与新项目导入

已全文读固定 `b39c87ed80d28bfd63b21881a5e6673eee212e7c` 的 i06-trusted-transfer-contract-request.md，SHA `6e52cdf4230b61034366963ef39808cbdf8b7e62655a0ec168d77706b311b7bd`，并核对PRD FR-1000/G.6。

1. **接受白名单投影及I06位置lease边界。** 不复制DB/userData、不递归项目树；picker只是候选，guard先于open/read/hash/mkdir，实际身份扩展及跨await/发布前重验。完整private根/密文/别名和动态位置能力由I06实际owner提供，不声称原excludedRoots已动态登记。T10不取得第二writer。
2. **投影来源。** T01在唯一一致读事务固定projectId、domainSnapshotRef/revision、完整checkpointRef/operationSequence、metadata/draft/learning CAS、格式/reader/writer版本和coverage，输出严格业务payload及digest/manifest。checkpointRef绑定源证据，不能把原完整checkpoint/claim/context和全部祖先打包当白名单。现project_checkpoint含assistanceAudit；必须按批准业务schema保留真实辅助来源，不能按audit字段名一律删，也不能带I06私有profile audit。
3. **接受完整包必需集合。** 所有定义、当前事实id/subject/predicate/object/owner/source_row/managed_value、mapping generatedVersion/stale、版本ledger及retirement/tombstone控制共同保真；来源定位用可移植引用。任务/清单、当前恢复配置/版本和应用状态须来自真实owner，不能用空表代替完整语义。四选项独立，未选不夹带；无raw只限制直接重跑，不降完整包。
4. **最小撤销闭包。** 以当前domain/app状态和实际保留的撤销/恢复引用为根，按类型追踪before/after snapshot、控制证据、来源/所有权/retirement及真实版本，固定点后每个引用可解析且hash成立。普通历史运行/会话不默认作为根。若闭包必然含未选history/session或I06私有材料，拒绝本次完整导出并指出范围冲突，不静默删引用、暗带或降模板。现完整库链验证不能直接认证裁剪传输投影；需另实现明确coverage和引用校验的transfer证明，不伪造完整源history或复制旧active claim。
5. **引用映射。** 新projectId由唯一writer产生；源project/operation/job/grant不是目标授权。按实体类型维护旧→新映射，重算含项目身份的snapshot/checkpoint/digest/ref并核全部引用；拒悬空、跨项目、重复冲突和未知类型，不能递归替换任意业务字符串。项目作用域definition/fact/owner/source-row在规则许可时保留，以维持相同映射冲突；全局job/result/attempt/operation按owner规则映射。业务文本只作数据，不恢复活跃授权或请求。
6. **新项目原子发布。** 先核包格式、必需集合和闭包，再由唯一writer在一个外层事务建立新public/internal身份、正式域/应用/映射/控制、genesis/checkpoint和唯一import receipt。现create_project/application CAS不等于完整import；需受限import plan通过Store.commit，T10不能直接多表写。失败不动原项目/选中上下文；丢响应按同operation/request对账，只有核验receipt后才交newProjectId。用户实际打开后tasks.selectProject(newId,[])，不能同ID假清授权或传包内jobIds。
7. **附件能力与缺口。** 绑定真实source对象、project/generation、长度/hash和main-only有界读取能力；读取前I06 guard，包内/renderer路径不授予能力。Store尚无该source注册、完整学习等业务投影和import receipt，须与T03封存合同统一；保持缺口，不用DB备份代替。

X1–X6全部保留：manifest/实际包、私有明文及真实密文排除、位置/别名/在途替换、同/独立profile新项目无旧授权、模型失败/恢复不阻断Store、源码和真实包。设计/CAS不关闭这些门。包格式、业务文本敏感策略、平台位置原语和闭包正式JSON/错误待同版审定，不批准消费T10未合并实现。

## 4. T09 多阶段完成证据

已全文读固定 `e6519932b0b20fd1862dcd6f038a621fce8177f5` stage-evidence-contract.md，SHA `637daea093465952aab800e329317f31514325285077850b81589e5cdd1e4ce7`。接受真实成功当时原子保存current完成证据、今天保留stale、终态今天仍current，不从今天result倒推当时有效。Plan/slot选择与完成账本序号、attempt epoch/root/祖先、真实job/result和完整分页需权威一致读及消费CAS重核。T09 binder不是持久账本。T01下一阶段先统一真实attempt/不可洗白辅助账本和完成边界，不接受renderer的passed或任意StageCompletion；当前动作明确拒learning，尚无完成receipt。
