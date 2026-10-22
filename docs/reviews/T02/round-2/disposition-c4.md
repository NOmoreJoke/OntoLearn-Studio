# T02-S1 C4 全部首轮意见处置

新产品候选 `35aa93fc007e92632d83747f7fe345295db340c8`，批准base仍`5f910b52c69d86a1076b2032e5d3c63e715947f3`。独立集成树`.worktrees/T02-s1-review-fixes`、分支`feature/t02-s1-review-fixes`；UI子树`.worktrees/T02-s1-ui-review-fixes`独占开发，提交3b3f1f8仅以a07c563集成，Python由原T02单独写。原493及两review树原件保持，原首轮Pass不传给C4。

首轮两正式报告原文、终态与原始证据见`../round-1/received-20261022/`。MiniMax摘要与终态自称1P2+4P3，但正文实际P2-1和P3-1..5六项；ZCode五项P3，按**11项**逐项登记，未删改原报告。模型设置/权限实际证明见原launch回执，而不是以模型自述或“未触发逐命令批准”推断。

## 逐项事实、改动与验证

| ID | 处置及依据 | 实际证据 | 当前结论 |
| --- | --- | --- | --- |
| M-P2-1 类型前门 | model.validate先检查Snapshot与三个元组元素类型，再解引用/哈希；change_preview在建set前检查Fact及RDF术语，Put.entity/精确bool/create及Copy/Delete目标类型在查表/哈希前守卫；deletion_impact非法目标固定诊断；bind_rdf_projection先validate editor，removed_sources先检查Preview及removed Triple元组。只用本线内部固定reason/location，无宽泛捕获所有异常、无第二公共错误协议 | 新`test_ontology_input_boundaries.py`实际六报告反例、集合/Put/Copy/Delete坏类型、可变/畸形字段、三入口固定诊断及输入不变；真实Store测试追加foreign editor/invalid Preview/unknown origin零写入。81 ontology专项及全check1133Py通过 | 修复并有运行证据；待独立内审及双方全新完整审 |
| M-P3-1 批量删除影响 | 保留**基准快照**精确引用；页面检查和Diff均明确版本与“包括本次计划将解除的引用”。没有改成最终候选空集合，没有隐藏原引用。原报告“成功提交”实际为成功生成Preview，本服务没有commit | 新类删除+同批解除domain/types测试断言全部三个基准引用、六个实际RDF删除项和完整candidate；headless断言基准版本/引用及请求 | 部分接受：标注已修；“保守过报”为语义限定，交新审判断 |
| M-P3-2 copy死类型 | 删除未发出的copy变体，注释明确复制完整定义进入可编辑新表单后发create。FR200未要求持久复制谱系，服务Copy.source本身亦仅选源、不持久化谱系，故不将“缺少持久溯源”编成已实现能力或修复目标 | headless四种实体复制完整metadata、修改examples后精确完整create意图及基准断言；旧Python Copy不复制实例断言测试保留 | 死变体已修，持久谱系主张不接受；全部事实/原意见交新审 |
| M-P3-3 UI覆盖 | 既有11项均保留；新增25对象前后分页完整顺序/集合、页边界、搜索重置/空表、四类复制后编辑、新建清空、assert/retract完整事实、版本/项目基准、坏值失败固定文案、基准删除影响、局部图截断边集合。未改原acceptance条款 | UI子树21项真实headless交互通过；4 TS单测及harness/unit/desktop类型检查通过；原始流与首失败在封存包 | 补齐明确缺口，仍仅合成callback呈现证据，无IPC/Store/e2e |
| M-P3-4 类树计算 | 页面仅tree tab且objects依赖改变才计算；classTree一次建parent→children索引，保排序/闭环/多父/重复边与缺失父语义；祖先集合/边/排序仍有成本 | 既有循环/多父精确序列测试保留，新增排序根/缺失父/共享后代/自环/重复父完整序列、输入逆序与空集测试通过 | 已最小处理；未测性能变化、不承诺整体O(n)、容量线或提升幅度 |
| M-P3-5 reason断言 | 对原16个未断言reason补真实业务负例：重复/矛盾事实、IRI身份冲突、非法字段/语言/字面量、来源移除集越界等；断言固定reason、必要location、输入不变/Store零写入。不是用AST计数镜像实现 | 39条新增输入边界+3条真实Store追加；本线总81Py通过。旧验收不删改 | 实际边界断言已补，待新审确认覆盖充分 |
| Z-P3-1 小写语言子集 | 当前私有模型、页面与canonical RDF term一致，保原范围与源字节，不私自接入parser或改共享schema；正式I05/T01导入投影需在批准合同下处理语言规范化并完整保留数据 | 新测试明确en-GB拒绝invalid_language且输入不变；旧语言/多行与来源保留测试仍过；父adapter门仍未开始 | 接受观察，正式adapter前延期，**非已实现导入支持** |
| Z-P3-2 默认rdfs类 | 不改既有None→rdfs:Class语义，增加原声明和复制声明完整RDF断言，实例事实不克隆 | 新`test_unspecified_class_declaration_and_copy_remain_rdfs_without_assertion_cloning`通过；原固定OWL声明与编辑测试保留 | 补证据，待新审 |
| Z-P3-3 重加事实幂等 | 保持RDF集合语义，不改成无需求支持的错误；重加已存在事实应精确空Diff，不复制事实或引入metadata变化 | 新`test_readding_an_existing_assertion_is_an_exact_idempotent_empty_diff`完整断言added/removed/changed/entity_changes、候选事实与完整RDF不变 | 接受现有语义并补证据；“已存在/无变化”未来呈现可另处理 |
| Z-P3-4 classType更新类型 | update改为key/value关联泛型，select值只允许rdfs/owl，服务invalid_class_type仍权威兜底 | unit/desktop/harness类型检查、634TS完整check、Pythoninvalid_class_type具体负例通过 | 已修复，待新审 |
| Z-P3-5 object前置格式 | 增规范n3单术语示例及由预览服务检查格式/语义说明；没有在renderer造第二parser。正式公共边界的完整提示仍依批准adapter合同 | 真实headless坏值经合成拒绝呈现固定文案且无成功预览；Python真实invalid_rdf_term/invalid_literal反例通过；两类证据分开 | 部分接受：轻提示/失败覆盖已补；完整前置parser延期，不把合成拒绝当引擎/IPC证明 |

## 实际验证与首失败

- 集成后唯一完整`npm run check` exit0：**634 TS／1133 Python**，含lint/format/typecheck/build/ruff；原始完整流`integration/test-results/t02-s1-r2/streams/check-integrated-first.log`。
- 本体四文件专项81 passed；其中新输入边界39条、真实Store追加3条。最后完整check在追加精确RDF/candidate断言后运行，覆盖最终源码，不以之前81项运行代替最终验证。
- UI独立子任务21项headless通过、25对象、4 TS单测、定向类型/lint/format通过。全参数/退出码/前后hash见UI交接和原始流。
- UI首失败1：新n3提示长URL触发原移动端无横向溢出断言，未删断言，以既有code换行样式修复；首失败2：JSON元组未收窄导致harness tsc exit2，显式收窄后通过。原流/失败JSON/对应构建与截图全部保留。
- Python首次静态check发现新测试unused A import/I001；初次工具输出在聊天，未改相同导入前重录失败为`ruff-first-recorded.log`，后只修导入，后续ruff与全check通过。没有产品测试失败被覆盖。

`c4-evidence-manifest.json`绑定20产品/测试/fixture+5 harness、完整base→35aa的112tracked delta和实际源hash；新84份原始证据（集成+UI）封存`c4-raw-evidence.tar.gz`，3010490B/SHA `b637c73924b856b89852547cf0dc82ce0621ee76d730543bb66c413cfb0faddf`，已独立读回每成员字节/hash。因本轮指定新审需可恢复首失败/截图且尚无CI artifact，此包仅为本地Git受控证据，不宣称远端/异机备份。

## 全部保留边界

acceptance、公共契约、Store/Job/main/preload/App、依赖/锁/CI均未改；无正式IPC/确认/commit/undo、I05导入往返、T08真实草稿、平台/真人/生产/CI/PR/merge/远端通过。旧typed接入方案仍仅上下文、未采用；若将来采用新版本须按真实调用图重新验证成本/来源合同，不沿旧方案假定runtime兼容。所有原父功能缺口和历史失败保持，新候选须双方全新同版完整审，不能继承493结论。

## 独立完整复核：C4未通过

固定35aa独立复核实际**不通过**，新发现未配对surrogate可从project/synonyms/examples逃逸UnicodeEncodeError。M-P2整体仅部分关闭，其余修改无阻断性回归；完整原结论`independent-c4-review.md`。上述“已修复/待审”为该复核前的处置记录，不覆盖本次Fail。后继C5将拒绝不可UTF-8文本并新增基准/Put负例、必要验证与复核；旧35aa源码/原日志/原Fail均保留。
