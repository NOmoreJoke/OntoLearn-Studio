# 启动诊断原字节P2处置

已全文读取总控 `T01-controller-business3-ready-startup-design-review.md` 11404B/SHA `55d18362b395c00036eca633ebe3ff93b38e0923e4e1d03965ea5e0ac5d65680`，接受其唯一新增P2-RAW-1024：decoded值及重序列化不能证明原帧实际字节数，现reader回调缺原长依据。原r2四项P2闭合保留，不重做旧产品测试。

新增 `docs/iterations/T01/business3-ready-startup-contract-r3.md` SHA `e9fcb876e6f4526ebf0b3c72783baddb39d3d3ce723393f1eb569b470707bbad` 采用原reader只读payloadByteLength，口径不含LF、含去CR前payload及空白/转义；1024预算只适用于诊断，不降其他帧/hello限额、不重解析。完整原bytes的1023/1024/1025、2000spaces、同decoded不同转义、CRLF/跨chunk、ready前后/旧generation和最终错误链均列计划，未执行。

文档作者 `/root/recovery_design_review` 另派独立 `startup_r3_design_check`，全文只读r3/根报告/r2及实际规则hash，回执为无设计阻断，可关闭P2-RAW-1024文档问题；没有产品/测试/源码读取或写入。主T01全文读回根报告和r3，hash相同；关闭是否由root登记仍待，不把内审当接口实现或移交生效。

jsonl.ts与task-presentation.ts均仍待I05精确双实体交接/独立/root生效；I06的main/index.ts及task-service.ts仅必要接线意向，其他四文件若共享类型重建即可，不机械改。当前未修改这些文件或启用新码/ready。原默认2行为、实际启动和呈现全链、源码/包/native及指定双审/CI/正常合并门保留。

同批新增 `full-function-acceptance-map.md` 仅将原T01 FR001–006/804和发布门映射成44个不重复ID，固定已有产品证据为b35，明确项目生命周期/完整恢复/学习/真实Agent路径等缺口；不登记完成度或新增P1。它是避免缩范围的验收导航，不是新的运行通过。本批只提交文档，pure table新代码仍为原授权phase下未提交候选、另作实际验证和独立审查。
