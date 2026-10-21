# I06 对 T01 来源 r2：主进程可冻结输入

2026-10-21。实际全文读取 T01 固定 ff98761ad14bbcea39331f2305e4e7c56bc6ef2e 的 docs/iterations/T01/source-contract-t03-response-r2.md，SHA256 dfd39ff7ddb9fb861b392cf0268bd3b23e09caa0cc42248976ce9b067af8fccf。设计方向接受，与本线68df生命周期补充一致；不批准该提交runtime或source_content实现消费。source_content/manifest仅内容完整性与同库缓存，永不等于活source授权、公共wire、消费者pin、确认或plan认证。

原固定材料保留，以下为I06给T01的具体选择与剩余装配门；数值是待T01接受的设计profile，未测量为产品能力或性能。当前责任/政策按78df AGENTS与ff5f共同指南，不改历史db1/b24原件。guard新路径尚待总控登记，本轮不创建guard、测试或修改旧private-directory/repository/共享代码。

## 主进程选择

| 合同点         | I06明确选择                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 帧profile      | raw65536B/最多128块/总长≤8388608B，0B为0块；两段header、最大合法chunk与seal完整UTF-8 JSON按各自协商帧计数，按r2不含终止LF，begin前不足就拒绝。不另启小块profile，不放宽MAX。实际字段/字符串上限与编码由T01唯一canonical冻结。                                                                                                                                                                                                                                                 |
| 在途准入       | 全main最多1个未终态begin；每upload最多1个未结append；全部窗口/项目合计最多2个未接纳lease，pending/receiving/sealed/受理unknown均占，按声明原长预留合计≤16MiB。broker实际2槽另计，不能重建host、换项目或取消未settled来腾配额。T01须在coordinator同样执行权威总量，不只相信main。                                                                                                                                                                                              |
| TTL候选        | receiving idle30s、从begin受理到seal总计120s、sealed未受理600s；采用单调计时，idle仅由真实成功接收的新块更新，总计120s硬上限不延长；status/重复消息/部分失败不刷新idle或续期。到期先撤销未来受理资格；实际消费、writer或清理未终态仍计相应资源，不把expired当物理结束。具体清理receipt/重启策略仍由T01补齐。                                                                                                                                                                  |
| begin/取消     | main在任何await前预留；begin按原session/project/attempt和完整descriptor幂等，改descriptor拒绝。丢ack不换attempt补发；按原身份status。只有attempt时也可release并建立取消tombstone；not-found不证明无迟到begin。实际writer barrier、清理及无迟到分配终态确认前不提前释放。                                                                                                                                                                                                      |
| append重试选择 | 选择严格序号，所有重复append均拒绝并终止未接纳upload，包括同bytes重复；begin的幂等不推广到append。ack丢失只查询原尝试，不自动重发该块或另开upload。如果权威status在原writer请求实际终态后证明该块已接收，且原upload/descriptor、该块SHA/长度/序号及累计进度精确匹配，可继续下一块；not-found、未终态或进度矛盾均不能据此继续。原块确未接收也不自动补发，本次失败/受控清理后由明确新预览动作重建当前绑定。若T01选择同块幂等，先提出精确比较/状态/不延寿fixture，双方同版修订。 |
| 代次/phase     | inspection与preview新phase绑定必须由真实owner签发；configure即使同值也撤销旧接纳并换selectionId/generation，新ref不改旧immutable seal。真实proof仍留main；复验到最终dispatch前逐await/实际写帧guard；已dispatch由coordinator受理/revoke原子排序和原operation回执对账，不以本地wall-clock断言先后。                                                                                                                                                                            |

以上并发/TTL不构成完整RSS、解压、parser、持久磁盘或结果profile。触发硬界只拒绝对应新消费，不删除既有业务/历史，模型/转移失败不阻断无关本地Store保存。

## T01与T03须补齐的精确装配门

1. **source权威与消费者pin。** 内容manifest/完整成员校验、活SourceAcceptance和consumer pin分别建模。只读inspection/preview先于最终人类写确认，但每个实际消费者都须在同Store事务中校验实际phase/epoch/项目/用途并pin后才读。pin绑定真实consumer/Job/context，不能拿任意字符串冒充；只读pin不获得写授权。受理/撤销/expire/回收需明确原子状态、unknown查询和有限收据，accepted写Job沿原operation/claim/base/确认绑定。内容缓存事务成功不关闭此门。
2. **持久配额的实际owner输入。** 请T01给版本化有限profile：每项目与全profile的source原字节/块/manifest/对象数量、未引用孤儿与已pin集合的计账、额外结果/plan存储界、低空间拒绝、清理预算/时机与历史保留兼容。孤儿和取消未清理者仍计账；已受理引用不因TTL删块。I06不以16MiB临时配额当持久上限，不从blob单值上限推导总库界，不为T01任意选择未经其评估的磁盘值。无获批有限profile时main不开真实上传，不能默认Infinity或由renderer决定。
3. **完整typed结果，不能复用source类型认证。** T01冻结严格结果manifest：实际capability/implementation与有限结果variant、project/consumer/输入ref和摘要/phase、结果schema版本、完整序列的字节长度/页数/完整hash、不可变页身份/序号/每页长度hash及明确终态；对应payload必须有真实类型schema，不以opaque JSON或未知variant放行。每页完整envelope服从两段协商帧；单consumer最多1个未结页读取，原顺序验证并在完整性/终态核完后才把完整plan交确认/提交。正式schema须明确页编码/hash覆盖及拼接规范、最大页/项/总bytes和取消/TTL/持久pin；不足或未知拒绝该能力，不能截断为成功。这里只给main消费合同，不另建公共validator、结果类型或renderer通用读接口。
4. **真实Table投影。** r2所述原Unicode、不trim/NFC、拒孤立surrogate、safe整数及保持顺序方向接受。等待T03给实际fields/cell.kind有限类型、完整投影和缺失语义；T01冻结canonical JSON/TS-Python逐字fixture。全部rows/cells与format/encoding/sheet及source_hash均绑定；parser implementation另入完整计划。样本可明确标受限，旧Preview三个hash不替代tableDigest，未完成或截断结果不能进入正式确认。

公共code/key/retryable/有限params、方法名与错误origin仍由T01唯一catalog定；本线不自造SOURCE错误或把任意IO原因透传。source.*/diagnostic.*仍仅提案，不给renderer/Agent新入口。worker维护已交T01、protocol/resources/语义/旧tests/build/CI未随转；无更强原子confinement/native依赖申请。

本轮只文档对齐与静态检查，不重测产品，不动e2c字节、不启动GUI或容器、不恢复/重建Goal。真实source→parser→完整预览/确认→Job→Store及X1–X6、同候选包/指定双审/CI/远端门保留。未批source_content模块的存在不缩减这些验收。

## 静态复核记录

/root/i06_design_review全文核对固定r2与本线合同输入，确认无新增静态阻断；审查时正文SHA4a5dcdc96d6f1a498ed242f3448c9621592ad8e624d1af84c6c27e51ae38af87。根随后明确丢ack对账须匹配原upload/descriptor及该块SHA/长度/序号/累计进度并格式化，正文SHA7b5166ec69a23a5314bf9f1e8facc255a4ce130654674573c0083ce7a7610c3b；该澄清未新增重试或授权。文档格式及diff检查通过，产品/锁/原测试相对e2c无diff；未进行运行验证，未读取source_content实现。
