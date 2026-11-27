# T01 来源封存与有界分块设计

状态：r1待各owner同版接受，仅设计；固定CAS实现为f51dd38，不修改其受审源码/测试。依据owner-interface-responses-r1§2与T03固定product8c904b5/processb86833d；worker.py移交尚未生效，默认2及公共3未ready的入口不开放。

## 1. 不可变内容与活授权分开

main持有broker实际scope/proof对象，不序列化该对象，也不从renderer接收路径/字节/proof。renderer仅表达已批准业务选择。main在sender/mainFrame校验后使用自己的project/lifecycle/generation及随机sourceSessionId构造受控传输；这些序列化身份不能反向替代broker对象身份。

`SourceContentManifest`是同库不可变内容：固定kind/version、totalBytes、wholeSha256、按ordinal排序的chunkRef/byteLength/chunkSha256。它不含路径、文件名、I06授权、model profile或native句柄，可以在T10明确rawSources选项下作为业务对象来源。`sourceRef=digest(manifest)`只代表内容，不是读取/提交授权。

活的`SourceAcceptance`另绑定engineSessionId、sourceSessionId、projectId、main生命周期/代次、selectionId、encoding/sheet及sourceRef；只由可信main/coordinator持有，失效不能靠旧内容hash复活。上传/接纳token不返renderer，不进入项目包。Job成功受理后，将真实已确认内容引用/选项/计划身份冻结在原Job context；不要把可复用grant写入导入载荷。

## 2. 同一协议的候选消息与预算

以下是待canonical冻结的typed消息职责，不是已注册方法。仍使用现有受控JSONL和严格request/response/session绑定，不另建HTTP、二进制旁路或任意FS读取通道。

| 消息职责        | 精确绑定与效果                                                                                                                  |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| begin           | project、engine/source session、lifecycle/generation、声明总长度/SHA、chunkCount及实际选项；分配owner上传身份，尚无可消费source |
| chunk           | 上传身份、ordinal、byteLength、chunkSha256、canonical base64；完整帧先校验再解码，逐块核长度/hash                               |
| seal            | 相同上传身份和声明；按顺序重算总长度/wholeSha256与manifest，全部成立后发布sourceRef；未seal不可解析/消费                        |
| revoke          | 指定上传/接纳身份，先使逻辑授权失效，再发abort；无新内容或领域写。不得用全局无范围删除                                          |
| inspect/preview | 只消费实际活接纳对应的sealed source；worker真实解析，不接受caller自报表/worksheet或Diff                                         |

原始chunk上限65536字节，canonical base64最大87384 ASCII字节。8MiB最多128块；总帧仍对**完整编码后JSON**执行现262144字节限额，不能仅因块小跳过frame检查。允许零字节内容在传输层形成0块manifest，是否是合法CSV/XLSX由真实parser拒绝或接受，不在传输层猜测。超8MiB、非法base64、非整数/越界ordinal、长度/hash不符、未声明块或seal缺块均拒绝；同块精确重试可回原ack，异内容同ordinal冲突，不能偷偷重排覆盖。

可复用同库不可变job_blobs存储有类型块/manifest，单值仍限原预算；必须证明类型/归属、所有成员可解析且匹配digest。临时上传进度可以是coordinator易失状态；崩溃不续接旧活授权，未完成blob不构成source受理。内容GC/pin只由唯一owner做，不得删除仍被Job/来源/导出引用的块。未批准在途数量/总存储预算、超限错误与回收策略前，不开放真实上传；T03的“两项实际host操作”不自动等于全引擎配额。

## 3. 精确预览、提交与撤销线性化

1. XLSX先readForInspection的复验副本→真实xlsx_sheets→显式configure选表；检查副本没有提交proof。CSV保留显式编码，不猜测。
2. readForPreview得到真正proof和确切字节，封存后由真实parser产生表摘要、来源行身份与规范mapping定义。预览绑定sourceRef/SHA/options、实际mapping版本/摘要、project/domain base、真实Store Diff和确认身份。
3. 正式受理前main调用readForCommit，重读所得SHA/options必须与确认逐项一致；仅传输/使用本次复验的相同封存内容。不能按路径让worker二次打开，也不能在确认后换manifest或重算成另一个计划。
4. 操作受理以前的重选、configure、源变、取消、project/lifecycle切换先使main本地授权失效再发abort/revoke。main本地失效不等于coordinator已收到撤销；受理和撤销按coordinator实际权威scope版本/确认序号排序并回执。main发出受理后立即切项目、但撤销在受理后到达时，必须按已受理进入取消/对账，不能声称“受理前已撤销”。每次await返回和Job受理事务前重核coordinator实际scope/token/代次，不让迟到成功复活旧预览。
5. 受理后撤销由main传递到既有Job取消/owner fence，commit前coordinator重核实际未撤销的执行身份；事务提交与撤销按同一受控循环线性化。若commit先完成，保留committed及原receipt，不能称回滚；若撤销先取得权威状态，后续worker输出不得写Store。项目关闭不将物理未终态worker假报已结束。
6. 丢响应只查询原operation/Job/receipt；不重发新operation、重新选择文件或自动执行新的域写。

## 4. worker侧和真实责任

当前Coordinator写一个parameters帧后关闭stdin；worker只读第一帧。因此需要一个明确的、仍采用现有JSONL decoder的worker输入状态机：header→严格顺序chunk→seal→compute。header绑定原Job/operation、capability、sourceRef/manifest和资源预算；每块重核源digest/长度，seal通过才交parser。无Store/FS路径、无数据库连接。取消/总时限/内存门在接收、seal、解析和输出阶段均有效；EOF/缺seal/错Job中止，不能处理半份输入。

真实解析表/提交计划和结果超过一帧时也须明确有界分页或分块，固定总量/顺序/hash及完整终态；不要只解决8MiB输入后用一个超限输出帧失败。T03给parser/plan的实际最大结构和错误，T01统一协议/worker传输；未批准前不声称这些输出已可串流。

T01维护main/engine.ts、coordinator、JobStore及canonical；I06维护业务路由/bridge和broker生命周期；T03维护parser/broker/构建。worker.py须总控独立登记唯一owner及原hash双方接受后才能改；不申请扩大protocol.py/MAX、旧tests或其他资源文件。真实native生命周期放隔离预约，当前无GUI接线。

## 5. 同候选验收

完整字节0/1/65536/65537/8MiB及越界；编码后帧边界；错误base64/整数/块序/缺seal/错hash/重试冲突；跨project/session/代次复用；begin/chunk/seal及worker接收的取消、EOF、超时、真退出；逻辑失效而物理未结束槽位仍占用；main发出受理后切项目时coordinator分别先受理/先撤销，完整确认序号与回执对照；真实CSV/XLSX→检查/选表→预览/确认→Job→Store；提交前源变/选项变/项目域base变；commit与取消两种先后；应用旧CAS/完整DB/历史/receipt不变或真实完整提交；同输入源码与包内实际产物。任何测试替身只记对应机制，不关闭真实parser/native/包内门。
