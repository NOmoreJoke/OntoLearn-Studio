# ZCode fresh R04 七项意见独立处置核验

结论：七项意见中，问题2的关键因果链不成立，问题1仍应保留未确认；提交数需要更正。问题3–5的源码边界可采，维持原非阻断／延期归属；问题6只作原政策的语义边界交ROOT审结，不构成新增用户批准；问题7为维护建议。本核验不修改ZCode原稿或其“Pass，附条件”结论，不代替指定双审。

原件：`zcode-report-original-final.md`，438行／54252B，SHA256 `b1dbe8e068fcf5f3aa12a95b0634344c9f1fd4bff7241116b8e9f05dbe6671b7`，本审全文读取并重算一致。源码全部以Git对象 `cb8c9b7a5d780544b2910901ec9141236905d65c` 静态读取；另全文读取原D8决定单、choice-A授权记录及该SHA的ADR-0002。未读取MiniMax R04原稿／当前结论，未向外审传递信息；未运行产品、探针、测试、GUI、安装、PS、SQL或PRAGMA，未修改源码与既有证据。唯一写入为本报告。

## 逐项处理

### 1. witness无ORDER BY：保留未确认，非阻断

`storage.py:1212–1215` 的同槽SELECT确无ORDER BY；`1147–1173`的单值声明group／LIMIT 2亦无明确排序。可采“未规定排序”的源码事实，不能把它直接升级为已发生的跨运行错误、错误witness或违反字典序最小要求。ZCode本轮也未构造同槽双冲突反例；原D8决定单第23行已明确“无ORDER BY不等于已证明用户缺陷”。维持未确认／非阻断，后续若产品要求稳定排序，由负责人补明确契约与构造性验收；本轮不据此改源。

### 2. 43692与50000字符IRI：该反例因果需要纠正，不能作为已证缺陷

关键源码位置：`packages/contracts/src/index.ts:951–989` 的 `capture()` 只调用于 `{expected, pages}`（第989行），它限制的是收到的分页信封／segment `dataBase64` 等字符串。该43692上限与32768原始字节的base64长度相匹配。文档在第1033行才从已重组bytes解码并JSON.parse，第1038行仅调用 `validateBusiness3('ownershipDetailDocument', document)`，**没有 `capture(document)`**。因此解码后slot.subject为50000字符，并不会因capture的43692检查直接失败；原稿第218–221行把分页base64限制当成witness字段限制，证据错位。建议收回这条确定反例与“schema收紧至43690”的直接建议，不能据此缩窄既有合法输入面。

实际schema事实：`changeSetFact`／`changeSetTriple`单字符串上限262144；ownership文档slot等字符串schema上限16777216。真正的后置约束是 `v2.ts:311–315` 对文档整体施加保守编码预算262144，与manifest 16MiB上限存在已披露的跨层行为边界；`index.ts:1020–1021`仍有“original 16MiB document policy”注释。应把这个既有整文档预算／注释问题单独保持OPEN，不与43692混同，不宣称已统一或已关闭。

当前UI可达性也不能以“通常IRI很短”证明不可达：事实输入 `OntologyMainlinePage.tsx:291–307` 未设maxLength；`mainline-facts.ts:53–81`未另设43692长度门槛。但事实还须经过重复／定义三元组支持检查、引擎shape／IRI／frame／存储admission、真实提交及再次冲突路径（`domain_changesets.py:141–166,432–459`、`storage.py`）才能成为展示证人。本审未构造或执行50000字符完整流程，不确认该具体长IRI已在当前UI完成入库／冲突／持久化，也不补造预算通过。即使该流程可达，也不能推出原稿所述capture拒绝；应据真实整文档约束另证。

### 3. definitions.triples坏词法：可采OPEN，非阻断延期

`domain_changesets.py:448–464`只对manual S/P/O及edits值做caller守卫；`storage.py:1125–1129`仍在定义triples层调用iri／term与canonical判定。精确说法是：已类型化TermInputError未进入该caller守卫，或非canonical触发ValueError，均不因manual修复而自动闭合。当前UI生成canonical triples的范围与原D8第24行延期保持；Agent／原始triples接线前由T01处理。此处只作源码核对，未新增wire复现。

### 4. Conflict ownership映射与通用定位：事实可采，建议须保合同边界

`storage.py:57–64`确无ownership键，直接读该Conflict.code会落INTERNAL_ERROR。`job_store.py:607–636`会先捕ownership类别：有真实witness＋proof者持久化新详情；其它路径写旧三字段详情并返回带detailRef的OWNERSHIP_CONFLICT。因此不能说当前所有权冲突一律显示INTERNAL_ERROR；原稿区分 `_application`内外总体成立，通用无可读定位保持原延期归属。

不直接采纳“只补码映射”作为完整修复：契约OWNERSHIP_CONFLICT强制合法detailRef；裸Conflict没有据此自动获得真实可读定位。任何后续调整需保持有效错误信封、真实witness／明确无定位合同，不以伪detailRef或泄露诊断文本补齐。本轮不实施。

### 5. 白名单缺集：重算成立，但17与26不是包含关系

`mainline-session.ts:86–104`共有17个UI允许码；`errors.json.codes`为26个契约码。交集10，UI额外7，所以契约缺集为26−10＝16，并非26−17＝9。ZCode列出的16码与本审重算一致：

`CURSOR_EXPIRED, CURSOR_MISMATCH, ENGINE_EXITED, HANDSHAKE_REQUIRED, MAPPING_VALUE_INVALID, METHOD_NOT_ALLOWED, NETWORK_FORBIDDEN, NOT_FOUND, PAYLOAD_EVICTED, QUEUE_FULL, SEMANTIC_INPUT_INVALID, SESSION_MISMATCH, TIMEOUT, UNSUPPORTED_CAPABILITY, UNSUPPORTED_CONSTRUCT, VERSION_INCOMPATIBLE`。

UI额外7码：`CANCELLED, ENGINE_DISCONNECTED, ENGINE_UNAVAILABLE, INVALID_CHANGESET_DOCUMENT, INVALID_PREVIEW, INVALID_RECEIPT, STALE_CONTEXT`。这解释混集计数，不等于这些UI码违规。可采缺集，维持原D8第27行非阻断延期；本审未逐方法证明这16码在所有当前错误路径均不可达，不能把“当前不可达”扩为全路径穷尽结论。接线方法应与其真实可产生码集逐项对照。

### 6. de-CH-1901语法与canonical：保留语义边界，由ROOT审结

已全文读取原D8第13／40行及ADR-0002原文。第13行讲首子段触发域与合法后续数字子段；第40行要求正反对照且不静默normalize。ADR第27行明确对象必须等于 `term(value).n3()`、非规范别名拒绝提交。choice-A记录requirements第16行亦明确“保持既有canonical输入政策、不静默规范化”，其verbatim决定本身授权的是最小修复与T02复审门禁延续。

在这些材料下，语法合法与可按原字面提交须分开：`de-CH-1901`语法合法；既有消费层把语言tag转小写后的canonical精确形作为可提交对象，所以原大小写别名受控拒绝，`de-ch-1901`／`en-001`正控成功。可采这种一致性说明，不把第13行单个例证自动当作推翻既有canonical政策的新批准。

原稿“唯一自洽／只有两条路”是审查者推论，不能代替用户决定或穷尽所有未来设计；“需用户确认”也不是由本审自动新增的执行授权或门禁豁免。将字面／类别解读与现有授权一并交ROOT判断是否还有真正未解决的用户意图；若要改变存储／输入政策，再取得相应决定。当前不改源、不代用户表态、不把ZCode意见当作新的批准。

### 7. 文件增长：可采信息级维护建议

固定SHA中job_store.py 2993行、storage.py 1887行、E2E spec 1748行，与原稿一致。行数不是当前正确性缺陷证明，维持信息级非阻断；后续按模块职责评估，不扩大本轮修复范围。

## 提交计数与原稿表述纠正

只读Git对象计数：`583c05c7..cb8c9b7a`为27个提交（普通与first-parent口径均27），不是原稿§2的26。`45f64b38..cb8c9b7a`为7个：`4472cd9f, 0e7ba05b, 362394aa, a0b125e1, 41a58557, ef54674f, cb8c9b7a`。原稿同一段写“5个”却列7个，需要更正。若§5.3仅指排除两个test提交后的生产修复，则5可成立，应显式写明该分类，不能混作全部新增提交数。此为元数据计数纠正，不代表head／tree身份不符。

## 交接边界

以上可作为ROOT逐意见处置及向原ZCode请求同轮事实纠正的依据；原最终原件保留，本审不修改其文字／判定，不向另一个外审披露。MiniMax R04仍按自身独立任务处理；本审没有读取其材料。无新产品验证、无源码改动、无新增授权或双审门禁通过声明。
