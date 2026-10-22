# 下一集成段固定初版独立审查

结论：**固定 adabdd379feda9a9e31c29f2c0fdc33f74139820 初审不通过，需关闭一项P2调用顺序歧义。** 这是纯规划审查，不是C5产品失败；旧S1有界双Pass及其固定输入不变。

## P2：CostSession发行晚于首个全量源读取的表序

位置均绑定本固定初版 `docs/iterations/T02/next-integration-segment-20261022.md`：第39行标题明确为“调用先后”；第45行第1槽先执行可信当前全量投影；第46行第2槽才写“新supplier创建整次同对象CostSession且先预扣”；第52行又要求第1至6槽的每次读取等操作均执行前计费。

精确触发：后继实施者依表序先在第1槽读取并物化全量domain、metadata、payload、全部支持与引用，随后在第2槽创建session并对bind/change_preview预扣。此时首次读取、解析、复制与驻留已发生在session发行之前，不能满足第52行的全链前置计费要求。整体要求虽有覆盖第1槽的文字，但不能消除这个具体调用次序矛盾；旧方案的计费P2不能仅在adapter计算处关闭。

最小修正：明确由原可信资源owner在**第1槽任何源读取、解析或物化之前**创建或取得整次唯一CostSession；第1槽reader必须接收该同一对象、执行前预扣，失败不重置；第2槽只能复用，不能重建或替换。将同一规则同步到开工与机制验收顺序，验证首读失败也计入累计预算。这里只需澄清原owner合同的顺序，不设计新的公共schema或T02账本。

本问题已先行回报owner并获接受；原初版结论保留。修订需固定新ref后复核，不能回写本报告为初版Pass。

## 其余完整范围核对

- 十件旧材料逐项从所列固定Git读取，大小/SHA及owner原件均匹配。旧处置及初Fail、修订Pass保持原范围；delivery-manifest索引九payload并排除自身，作为第十件另固定。34源／5控制输入是旧目录身份，本次未重建旧闭包。
- C5四模块重定pin逐项匹配：model/service/source_projection已变，__init__相同。旧493指针、旧指南、旧GUI限制和旧运行数字未被当当前许可。新文明确停止旧派生identifier，改为已选M真实业务identifier及缺失拒绝，不造RDF词汇或默填值。
- 八项当前规划依据的固定Git大小/SHA及当前原件一致。总控接收proof快照的1750B／SHA与其声明及根原件匹配；仅为有界S1接收，不是父功能、采用或发布许可。
- T01 423b/a1a的内部business3预演、完整Diff（含definition-status）、确认、durable Job、同writer commit和receipt/undo得到准确承认；M/S1/S2、独立proof及统一CostSession新pin仍缺，未把旧previewHash或逻辑cap改称新能力。
- I05 6891/f79各组件域、已有N3 decoder、selected字节codec与完整Turtle交换有区分；I06 e2/1f3的模型grant／旧读取恢复未充本体确认。新供方闭包、能力／模板／serializer组合、canonical／命名engine／当前host scope均保留待交付。
- 首段严格限定单个人工支持事实object修改，使用实际生产Preview和原fact ID进行纯edits翻译；mapped、墓碑、多支持、目标已有、不可表示及metadata／entity变化不被偷偷降格。完整候选与原Store真实预演after核同，确认、Job接纳、最终commit各原事务复验，receipt历史与新undo proof分开。
- 原事务写权、T01 canonical/main、I06四壳桥、T02适配及两P3路径、I05/T05/T01/T10交换职责列得具体；均是待总控授权的请求。深链观察不量化、不无依据优化，旧交付指针保历史，未宣称已修。
- I05交换合同可并行准备，整批导入必须等待无损表示与同一正式写链；单事实机制、真实页面／真人及完整父验收分开。FR-200–204、metadata CRUD／多支持／跨层引用、导入往返、T08、项目包、目标平台／真人／CI／正常合并／远端和发布门未缩减。
- status/backlog仅追加接收与规划事实，父Goal保持blocked；未把规划或既有S1双Pass转授下一产品候选。系统Python静态写入首失败被记为本方取件／写入问题，未混成产品失败。

## 验证与边界

本次只做固定Git、标准库文本／JSON／hash及已有三接口矩阵来源的静态核对；未重复825／130全量检查、产品测试或探针，未运行SQL/DB/native/GUI/模型，未访问live会话。固定提交git diff --check exit0。除本初审报告外未写文件、未提交，未改主文、旧方案、代码、受审树或控制状态。

其余范围未发现新的实质问题。待上述顺序修订后，可仅对实际差异复核，并沿用本次其余审读结果；不能据此自动批准实施或采用。
