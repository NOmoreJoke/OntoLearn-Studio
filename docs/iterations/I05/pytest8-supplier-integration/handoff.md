# I05 首次真实失败修复与供方整合

新树从卫生过程提交 d1fb6d1 建立，采用 T03 固定 4e752177 的三条产品路径。旧 2cf、401a、e56、T03 原失败日志及新诊断原件保留。

一次新增诊断的定向 pytest 实际失败，两份完整 JSONL 首败均为 `turtle/front-5 → semantic.parse_turtle → parse/turtle`。各有154条已完成、263条未开始；它们是新增复现实证，不能恢复 T03 首次未落盘的 BytesIO。

新增三个回归的真实 red 栈确认：非法 IRI 在 `_terms` 的 `n3()` 排序键中先抛普通 Exception，未到达既有 `ABSOLUTE_IRI_REQUIRED` 检查。实际采用独立前审的 v2：仅既有文本解析路径启用 URIRef 预检查；已有 OWL.imports 拒绝仍在前，排序和其他直接 Graph 路径保留。普通文本中同时存在多种违规时，拒绝优先级可能改变；不声称关闭全部 n3 异常或测得性能改善。

另据固定公开返回布局，把 roots 的对象属性断言修为精确 dict tuple 断言；原 step0、leaf 引用及顺序保留。新增三回归和原解释恢复参数用例实际4项 green；三源 lint 通过，格式初检仅私有签名排版失败，修正后格式通过，格式化前后 AST 相同。完整417清单及 fullcheck 待 source pin 刷新后验证。

新 semantic 源需先冻结为真实供方版本，再由唯一 probe writer 更新相应一项字节 pin 与 SOURCE/PROCESS lineage；其他21源和两份输入保持原字节。不能忽略 pin、将普通 Exception 泛化为业务拒绝，或用旧6891身份冒充新源码。

私有 frozen provenance/reader 由 T03 另行交付。当前 frozen guard 保留，源码/包 CLI 对照仍需完整候选及运行前外部 binding。S1 物理证据、wholeH、17L 和正式集成验收继续按原责任与门禁处理。
