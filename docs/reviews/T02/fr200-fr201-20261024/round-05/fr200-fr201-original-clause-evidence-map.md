# FR-200 / FR-201 原条款—实现—实际证据映射

结论：当前证据已经验证类层级、属性 domain/range、个体类型及五组元数据随真实表单 CRUD 保留；不能把“类层级等其余构造”笼统移到后续。四类 CRUD 通过也不自动等于 FR-200 全条、FR-201 全条及附录 C 所有能力完成。以下逐项说明实际证据覆盖，未验不直接等于实现缺失。

## 1. 身份与读回范围

- 只读候选 `aff386f6b43cf60a847c9c9597265b0b1b477095`，tree `2d9b113b4b6ca25049c157c2b94fc79db42ef38d`，base `583c05c7870ba0f8f642e3eeea1d0590e5859ca2`。本次没有运行产品、测试、GUI、DB、构建或外部模型，没有读取本轮 MiniMax 报告。
- PRD：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T02-s1-review-fixes/docs/prd/PRD-本体学习与落地Agent工作台.md`，93584B，SHA256 `7586b2c4784b8c691d510e2be16310ed551e110af6df96b7c6aeb86152f60fbb`；本次读 FR-200/201 第307–318行、附录 C 第959–979行，物理字节等于 HEAD Git 对象。不是本次重读整份 PRD。
- 源码行号以下均相对此工作树的 `apps/desktop/src/renderer/src/ontology/`，测试为 `tests/e2e/t02-fr200-fr201.spec.ts`（1748行）。不是用外审报告自述替代源码。
- GUI 原始目录 G：`/Users/kyle/Documents/工作/知爻/本体/outputs/20261025_t02_aff386f6_original6_gui_037/runtime-full6-001`。本次直接解析 G/report.json 内嵌 base64 body，读取四份 fr200-form-matrix 全28笔 after.domain.state.definitions，读取 FR201 原22笔 records 的 before/after/Diff 与动作。解码仅在内存，没有重跑 GUI。原 report：3996488B，SHA256 `3b78d51eeb9cff35a0a18929442267abe109e711ae69ba7c51b83c3e36b3d3f6`；原 stats expected6/unexpected0/flaky0/skipped0，102625.483ms；G/gui-exit.json 记录实际子进程 naturalProcessExit=true、exitCode=0。每例 retry0；不是独立观察 GUI 现场。
- check 原始目录 C：`/Users/kyle/Documents/工作/知爻/本体/outputs/20261025_t02_ci_diagnostic_env_corrected_036`。读回 check-attempt-02-result.json、CANDIDATE-QUALIFICATION.json 及 check-attempt-02.stdout.log：39 TS 文件/1892通过，Python3769收集/3719通过/50skip/1warning，自然0。执行时 HEAD 是58c9、CI目标补丁为工作区字节；C 的提交后物理源桥接记录绑定 aff。不是本次独立执行全检；不因此推断 Windows CI 已通过。Ruff369/379口径差异原因本次不认定。

G 内原附件定位/哈希（可与 report 嵌入 body 逐字核对）：

| 原附件 | bytes | SHA256 |
|---|---:|---|
| attachments/01/fr200-form-matrix.json（class） | 95663 | 1791c03ba37489d85023e241660684e451aa58ab78d62c8e3d53670e833b75db |
| attachments/02/fr200-form-matrix.json（objectProperty） | 99063 | 30c6418cfd64ce1657c0d511bae2c63cd7861bbd3c41fa7ae86f2057c8310c5d |
| attachments/03/fr200-form-matrix.json（dataProperty） | 99006 | 4f42d5e7a17ec899cc6e58fb1e422dea315d7df40e93fd307c4f100b8c4e6d52 |
| attachments/04/fr200-form-matrix.json（individual） | 93526 | 63a0c2fea76eea8d4f2765694c573ffc8ff7f0cf04a2a31d63ced56207a0b8fc |
| attachments/05/fr201-original-records-and-literals.json | 425233 | b56359e5837f17881c5327d9eb691b20a727100f764daf6afde5591c0334ceae |

## 2. FR-200 第309行拆分映射

原句要求表格/表单管理所列对象及字段，并在删除已引用内容前展示影响。下表“已验”均限 G 的同版 dev GUI 路径；不是任意图形、容量、所有 OS 或任意历史项目的穷尽证明。

| 原条款要素 | 当前实现（可核对行） | 实际已验证 | 未验/不能推出 |
|---|---|---|---|
| 表格和表单 | OntologyPage.tsx:217–263 表格选择；316–368 详情/载入/复制/删除影响；385–481 类型和字段表单；OntologyMainlinePage.tsx:170–194 接真实 session | 四类用例564–681行经可见 UI 创建、载入编辑、复制新 IRI、删除；G的四份原附件各7笔完整提交 | 不要求原文未写的“每格内联编辑”；未证明任意分页/超大表操作性能 |
| 类；create/edit/copy/delete | mainline-ontology.ts:105–118 区分 rdfs:Class/owl:Class；298–373 生成实际定义计划；OntologyPage.tsx:410–423 类声明选择 | 各例种子A为rdfs:Class、B为owl:Class；class主对象C为owl:Class，create/edit/copy/delete完整链；真实原RDF保声明 | GUI不是两种类声明各自所有CRUD组合的穷尽矩阵；rdfs/OWL变体额外unit不能当额外GUI |
| 类层级 | mainline-ontology.ts:124–130 parents→rdfs:subClassOf；OntologyPage.tsx:461–481 parents编辑；274–287类树显示 | class原附件第3笔 C subClassOf A；第4笔改B；第5笔copy保B；第6/7笔分别删除C及copy。测试429–439、564–681行 | 类层级已真实测，不能归“后续”。类树多父/循环展示、推理闭包/解释不是这次GUI所证 |
| 对象属性、基本结构关系 | mainline-ontology.ts:116、124–130 ObjectProperty/domain/range；表单461–481 | relation的domainA/rangeB→B/A→复制保B/A→两删除；原附件02的第3–7笔；测试442–477行独立RDF期望 | 不外推属性链等附录C明确排除构造；不能把domain/range当必填或闭世界值校验 |
| 数据属性 | 同上DatatypeProperty；实体修改保原定义home与非目标内容，338–373行 | value domainA/range xsd:integer→domainB/range xsd:string→复制→两删除；原附件03，测试481–500行 | 证明的是属性声明编辑；不意味着任意datatype/任意非canonical字面形式可提交 |
| 个体 | mainline-ontology.ts:128–130 types→rdf:type；表单463–481 | one typeA→typeB→复制保B→两删除；原附件04，测试504–512行 | 不据此证明查询/规则/行为实际执行 |
| 中文名称 | OntologyPage.tsx:443–447；mainline-ontology.ts:119–123 label及133–140完整metadata | 四类create labels含“业务名称”@zh，edit“业务名称修改”@zh；copy完整保留；删除只移目标，原附件逐笔可见 | 未穷尽所有语言/文字输入边界；不将单测范围冒GUI |
| 英文标识 | OntologyPage.tsx:434–441 独立identifier，425–433稳定IRI；mainline-ontology.ts:133–140保存真实值 | 各kind CRUD_kind→Edited_kind→Copy_kind；不靠IRI尾段猜值。英文label Business label@en亦始终保留 | 英文标识与英文名称是两个字段；未要求/未证明允许任意IRI重命名，编辑时IRI锁定 |
| 定义 | OntologyPage.tsx:448–452；mainline-ontology.ts:119–123 comment及133–140 metadata | 四类zh/en definitions成对create/edit/copy保留；zh定义修改，en Business definition原文不丢 | 不等于全部历史不透明定义都可编辑；Page明确只读无法无损投影内容（MainlinePage:165–196） |
| 同义词 | OntologyPage.tsx:453–459；metadata:138 | 四类原“ 原始别称 ”/别称二，edit“ 前后空格保留 ”，copy逐项保留 | 非NFC/语义归并、任意最大长度不由这组样本推断 |
| 示例 | 同上，metadata:139 | 四类原带空格示例；edit第一项“第一行\n第二行”真实换行；copy原数组保留 | 不以UI显示摘要代替原存储；本次已读原after payload，未扩推无限长度 |
| 删除前影响范围 | mainline-ontology.ts:262–296 收集S/P/IRI对象命中支持及显式definition references；345–346有引用则拒绝计划。Page:346–366先读并列出影响 | FR201测试1075–1090明确两条关系事实的原id+完整SPO精确toHaveText、阻止删除、无Diff且完整Read不变；原通过spec+原事实records绑定该图。无引用四类真实删除亦通过 | 原body保存真实事实/状态，不单独等于DOM截图证明；精确可见列表依冻结passed UI断言。其它层显式references、非空mapped/墓碑、任意隐含外部引用未由本轮GUI穷尽，不冒称全IRI反向闭包 |

原28笔还共同证明每次非目标兄弟定义保留、facts=[]、元数据与原RDF一起存在。7笔中前两笔为A/B种子，第3–7笔才是主对象create/edit/copy/delete/delete，不把28笔说成28个不同功能或完整父验收。

“基本关系”需按FR-201分别陈述：对象属性结构定义的复制已实际验证；实例断言链本轮验证的是新增、按原ID编辑及删除，没有独立“复制实例事实”UI动作证据。若整条验收将FR-200的复制同时解释为独立实例断言复制，现有材料不能拿结构定义copy替它证明；本审不擅自把此解释设为新增需求或直接判实现缺失。

## 3. FR-201 第313–318行映射

| 原条款 | 当前实现 | 实际证据 | 边界 |
|---|---|---|---|
| 明确区分两种操作 | OntologyMainlinePage.tsx:155–156明示说明；163结构定义与208实例事实为两个区；结构走entityEditPlan，事实走mainline-facts.ts:10/53的原ID计划/内容ID新增 | 事实原附件前7笔只增7定义，facts数量逐笔均0；随后明确assert11个SPO；不是同一自然句自动混译 | 已证这条真实路径语义分离；不声称全部引导文案/所有入口可用性验证 |
| 结构关系生成属性及domain/range，不意味着必然事实 | mainline-ontology.ts:116、124–130生成ObjectProperty/DatatypeProperty及domain/range；MainlinePage:156明确非必填 | 原02/03附件实际声明，以及FR201第6/7定义提交后facts仍0；测试912行断言No inferred relation or required-value fact | 空facts只证没有自动制造实例关系/必填事实，不代表未运行或已验证RDFS推理全部语义 |
| 具体个体实例断言 | mainline-facts.ts:53内容派生ID，10原IDedit/remove；MainlinePage实例区S/P/O | 原05第8–18笔依次两IRI关系、plain、zh、integer、canonical string、boolean、decimal、double、date、dateTime；随后两原ID编辑/两删除，最终rev22/facts9，定义集合保留 | 本manual数据族；非空mapped/tombstone、全部支持来源不由本轮空库GUI推出 |
| 不用同句模糊两语义，用户可用实际RDF核对 | MainlinePage:198–204真实definition payload含triples；353完整rows JSON Diff、360真人确认；事实表S/P/O；测试commit:129–139确认前精确Diff及未提交Read，208–234原Job/marker及后读 | 原附件每笔保存完整before/after、resource级Diff、真实job/marker；可核结构公理及实例SPO，而非仅自然语句摘要 | 本次有源码和passed完整Diff/UI断言，不是重新看现场DOM；不声称Turtle导出、完整解释器、Undo或全部父功能完成 |

新增canonical语言fresh cohort是第6例，不把它算原四CRUD或原FR201动作；G六例共57真实事务（7/7/7/7/22/7），原五例共50。43拒绝（42 INVALID_REQUEST+1 OWNERSHIP_CONFLICT）保受控输入边界，不是57成功交易的替身。

## 4. 附录 C 的范围语义与未证部分

| PRD行 | 本次对应 | 未证/排除边界 |
|---|---|---|
| 961 主定义、M0可代表样例澄清 | 用枚举构造限定FR-200/201，不把“支持”泛化为整标准 | 在本次查阅的PRD、D8原决定与choice-A原授权中，**未找到批准将FR-200类层级/domain/range等移出当前验收的冻结范围原件**。94e局部独审不是需求变更权限；本句不声称搜索过所有ROOT材料或批准必然不存在 |
| 965 IRI/字符串/语言/常见类型/基本三元组 | 原05 eleven facts及原06 canonical语言链；稳定IRI/原ID保存 | 不证明所有datatype、导入、Turtle导出或任意来源显示；这些是原能力矩阵仍需各owner实际证据的义务 |
| 966 bnode/list | 当前这组实体/事实GUI无此输入 | 原文只给SHACL模板受限列表，不提供通用编辑；不能把未实现通用bnode编辑判FR-200缺陷，也不能声称FR203拒绝链已由此验证 |
| 967/968 Class/subClassOf | 当前声明/层级编辑及真实CRUD如上，Page有类树 | RDFS类型判断/闭包、相关公理+直接事实解释未由这次CRUD GUI证明；复杂类表达式本就不在P0 |
| 969/970 属性/domain/range | 真实公理create/edit/copy/delete，结构不制造实例facts | RDFS类型推理执行/解释未由这组GUI证明；明确不是值校验/必填，不能用SHACL规则替代此语义 |
| 971 个体/rdf:type/属性断言 | 分开编辑与原05事实链已验证 | 后续查询/规则/行为消费及derived来源未在这组GUI执行；不把asserted-only原库说成全部来源覆盖 |
| 972 label/comment | 同版四类zh/en原文随CRUD保存并映射RDF | 不能由此代证导入/导出无损往返；不要求label/comment参与P0推理 |
| 973 SHACL模板 | 本次未执行其模板编辑/验证/报告/导出 | 是附录C另列的受限能力，不因“FR200 CRUD”就自动完成；也不能擅自向本域追加任意SHACL |
| 974 受控规则 | 本次未执行规则表单/一阶段规则/完整依据链/包往返 | 仍按原规则owner/父验收处理，不能由本域结构编辑推断存在或不存在完整实现 |
| 975 只读SELECT/ASK | 本次未执行 | 不能由本域CRUD推断查询功能已完成；原文不含CONSTRUCT/DESCRIBE/更新/联邦查询 |
| 976/977 不支持高级构造 | 本域不承诺编辑这些高级表达式 | 非静默保留/拒导入仍需FR203相应证据；不能把解析成功冒可编辑或往返 |
| 979 解释最低要求 | 当前只证真实RDF/原Diff可核对 | 不替代RDFS解释、自定义规则依据链或SHACL真实报告；解析/CRUD/推理/解释/往返必须分开判定 |

以上“未证”不是本次新缺陷清单、不是授予新增开发，也不是批准后移原条款。父FR整体完成必须逐条用对应实现和证据作结；本报告只给现有证据分布，不解除CI、2/17或既有HOLD。

## 5. ZCode最终事实修订短补充

首稿独核 independent-zcode-disposition-audit.md 保持原件。固定修订稿 `zcode/report-factual-revision-01.md`：51052B/344行，SHA256 `8b2ed0b905e92c7f95f50024330455e4dc51ae4d9560ecd8a95c838cc7c6b778`。本次定点读回确认：第32–35/337行改两次generic busy及原SID两续接；338行改实际2993/1887/1748行并区分新增行统计；339行不再由mkdir或未读peer推出目录刚建且空；82/326/340行取消当前候选新增用户canonical表态门；§9实核恰1–160独立行无遗漏重复；12/94/324–326/342行区分既有PR16旧58c9与aff未push/无新CI，原Windows79F/Quality取消门禁及作者ConditionalPass不变。本审不认证GUI现场、不替作者改判。

残句按处置限定，不再让外审往返：

- **第73行**仍称类层级等按94e局部独审属后续，不能作范围批准；本报告原28笔附件已证层级/domain/range/type真实路径，应以第2–4节逐条映射为准，不据此推父FR全条完成。
- **#16（173行）**单写者/启动迁移不等于迁移无锁；**#31（188行）**拒绝Read不变/生命周期围栏不等于四次快速点击去重。逐项展开不自动补足这些证明；不新加验收门或运行。
- **#149（306行）“Q6能力冻结仍开放”**不采为当前状态：ROOT当前决策已确认用户采用Q6单推荐规则/规范版本。此项为ROOT本次直接提供的决策事实，本审未另探索；不是新增用户决定前置，不解除其它HOLD。

最终：原件支持本表列明的真实编辑/提交路径；未找到可用94e局部独审改变FR原范围的批准依据。CI/合并、发布及父能力门禁保持。本次只读映射不替代新的验收运行或指定双审。
