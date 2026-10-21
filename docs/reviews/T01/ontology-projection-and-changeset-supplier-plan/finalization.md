# Ontology供方方案原件归档收口

本次仅冻结并提交已获独立r3方案阶段通过的文档，不修改主稿、独审结论、任何产品/测试/环境或既有C1/C2/dispatch原件。产品实现、真实JobStore/T02全链、DB/性能/升级/临时峰值及全部实施门尚未运行通过。后续root逐阶段授权仍为必需。

## 固定原件与静态核验

主稿81538B / SHA256 `c752d7bdebe1b60ab5ecaae3dcf87a6a5829d21d45313c2f3d2c04b034205db5`；独审23030B / `d1b73c28f9487ec4173b76f9a86271dfb20ab65e6ab472af407517c6fa239d5b`。独审实际最终工具 `36e387` exit0，§9仅对该身份作方案阶段结论，首审三P2与r2两补充保留在原文。r1与r2快照按各自snapshot-manifest原字节保存，未倒改历史意见。

收口工具 `7c572d` 实际exit0，逐69清单核current/Git/source bytes/SHA；全部5f→原HEAD的86文件逐current==Git，其中C1原59、C2原9和dispatch原17各按其固定ref核同。r1/r2九份原件、AGENTS/common受保护字节、主稿及独审固定身份全部一致，初始index为空。逐件结果见final-static-checks.json；这是文件/Git静态核验，不是产品运行证据。

预期唯一提交parent为 `506e15744e47fd36f43bdbd645f6e65526cf0bf4`。只允许暂存新ontology主稿及本审查目录，其他index/AGENTS/产品不改；commit以 `core.hooksPath=/dev/null` 禁hook，避免文档期触发产品。实际stage/commit的命令终态及提交后每一Git blob/current receipt应在收口工具结果和正式交接提供，不在提交前伪填commit身份，也不制造包含自身hash的递归清单。

## 原始工具记录的真实边界

original-evidence.zip保存作者/独审两条源rollout中的全部ontology阶段response_item工具call/result，另保存root指定六对primary原始工具call/result，逐条原JSONL字节完整保留，包含真实错误、截断输出、修订及后续纠正。author与independent分别独立成member，original-evidence-index.json列一基sourceLine（真实文件行，不把筛选后序号当原ordinal）、原sourceOffset、timestamp、bytes、SHA256、callId与配对。原始源prefix hash仅到该阶段边界，源rollout后续仍会增长；不能把该prefix当整个最终源文件。

作者时间界为2026-10-21T13:08:14.337Z至15:33:23.154Z，源行1089–1595，共106条/53对。独审时间界为2026-10-21T13:43:09.779Z至15:38:31.043Z，源行1121–1460，共84条/42对。前序C1/C2记录、用户/系统/推理消息和session个人元数据未收录；工具参数中的原密文不解密、不改写。两条选区均无缺配对call/result。本包不宣称归档root完整会话。primary仅精确收录六对：`9ddaaa`为首次授权全文读；`253d2a`/`6cabf8`/`e9866f`/`66e88d`/`bbf54d`为最终主274行及独审全文读。它们为非连续精确选择，逐sourceLine/offset/hash可追。`9ddaaa`所在同一完整调用先做C2文档归档核验/stage/commit、再读本授权，原样保留伴随内容，不将其当ontology产品运行证据；其余并行C2/dispatch工具不收。primary末次结果时间2026-10-21T15:42:20.959Z，晚于作者/独审边界，单独标明，不回填成其阶段原件。

归档保留此前工具真实失败/纠正，包括错误路径/静态解析、格式检查不通过及修正；作者 `a1a779` 的格式exit1、`1a4f71`修正后exit0、独审实际KeyError及修正，以及作者followup独审调度thread limit失败均在原始记录。调度失败不是独审通过；实际通过来自其后独审 `36e387`。输出包装截断仍以原工具记录保留，已有补读事实见调查和独审原文，不用本收口去补造原输出。

本次作者收口的后续核验、生成ZIP/index/manifest、格式检查、stage和commit均在作者/独审边界之外，未伪称已包含在原始工具包；它们由当前收口命令实际返回的终态证明。所有时间为原始UTC；本地时区Asia/Shanghai。

## 文档ZIP、逐件清单与安全边界

source-documents.zip保存本任务主稿、调查/审查/处置、r1/r2原快照和本收口说明/静态核验，并保存只读授权、根T02审查、T02固定主稿和AGENTS/common原件。来源映射与逐member bytes/SHA在original-evidence-index.json；仅复制文档，不复制69项产品源码、环境或用户数据库，不导入或运行T02。

original-evidence.zip仅含上述三角色工具JSONL及其原样输出。外部index绑定两个ZIP及每个解压member，delivery-manifest.json绑定本任务其余全部待提交文件（明确排除自身，避免自引用），原件/归档/索引均可分别核对。ZIP成员使用相对安全路径、无符号链接，读回验证CRC、member集合和每件bytes/SHA。

文档格式工具仅针对新收口文件，禁止重写已通过主稿、独审或历史快照。最终交接应附真实docs-only commit及parent、完整逐Git/current结果与残留受保护AGENTS状态；未运行产品DB、测试、构建、网络、模型、GUI/native或新代码树。
