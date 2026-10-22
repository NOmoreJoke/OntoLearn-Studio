# 外部 oracle 的业务模型与字段政策

本模块生成独立 expected，不读取 source/package 观察、不执行产品，也不冻结未来 JSONL 适配。输入只使用固定 0e42 的两纯 JSON，业务依据分别列入每项 `expectedSourceRefs`；原观察的 `sourceRefs` 仍仅表示输入来源。

## 完整比较域

| 域 | 固定内容／有限关系 | 不可放宽的边界 |
| --- | --- | --- |
| RDF | 完整三元组集合；IRI、lexical、datatype、language 每字段 | simple/string 仅按 RDF1.1 身份对应，language 仅身份比较 casefold；原 raw occurrences/文本摘要仍保留。integer01/1、date/offset 原词法不合并。合法 shape-list blank node 必须全图双射，不能删除节点或尾项 |
| query | ASK bool；SELECT variables 顺序、全部二维 typed cells/None、全 rows/tie order | 不只比数量；原 Q01 只返回 alarm 一列；FILTER type error 是空结果，不是错误任务 |
| SHACL | conforms exact bool；所有 violations 的 focus/path/value/sourceShape/constraint/severity 六字段多重集 | value=None 必须保留，MaxCount/MinCount 不能补造单 value；空报告仍有完整 true/空列表模型；拒绝没有部分报告 |
| 原83 | 原独立手选图、全部 matches/bindings/typed when/comparison/head index/accepted、leaf basis、definitions/sources | 80整图匹配加3个后续E5片段的显式当前 facts 映射。片段按独立已手选 matches，不继承完整轮次图。repair profile 不执行，前后 SHACL 另列 |
| 有限 RDFS／legacy | 仅四条批准关系；完整新图、所有规则匹配/heads、每个 when 的 leaf basis；不反馈 custom | stable-first candidate key 为批准 directsteps 合同§2的 result+ordered-premises key，不新增 shortest-depth 语义。cycle 的自反结果来自实际环的传递推导，不是 seed 通用自反公理 |
| scope | 原6／derived9 facts分立；ontology含派生axiom；完整两视图/query/SHACL、selectedRuleIds/warnings/来源basis | fresh prepare reason1，project复用同次结果并reason0；源身份与精确provenance编码缺件仍pending。事实不能混入公理，也不成为正式selected权限 |
| fullview/DAG | 完整业务图/全部head occurrence/aliases/raw source；payload7/native15/child11由获准literal声明固定；/3显式加directSteps | native exact int非bool，wire整数hex；每个step两有序premises、depth=1+max、完整叶union；所有所请求roots都保每个occurrence。未知完整typed usage/嵌套投影不猜值，逐项pending |
| wire/restore | 全payload/rows/sidecar原bytes的SHA、长度、rows拼接；同次expectation/allocation；完整native及每child全尾项对应 | `finiteRelations`提供可自测的有限关系；实际capture来源另需真实凭据，JSON自述或值相等不能证明同次发行。源/包各自发行，不比较地址，不用source SHA预填bundle code |
| restore负例 | 14 observations／9 enum；在实际接收bytes上扰动且原expectation不变，应A1拒绝 | 不重绑期望，不重reason；没有部分view且原成功物料不变。不能升级为深层DAG/末child原子性全部覆盖；精确错误投影仍pending |
| date budget | 公共43460为23m+420=1M；43461需1M+23；D1早错366042／晚超1M，三序同一完整政策 | 费用来自65e设计§5.1的独立代数，不是库CPU或whole-H。真实观测完整账本尚须未来获准采集/适配 |
| B1 | 独立1×/10×四ontology，原18k facts→改型仍18k→merge18k+4；RDFS 8k+1、k规则matches、完整query及原facts SHACL | First/Warm业务全同；不冒充十ontology suite或S1 snapshot；snapshot未执行不写0，计时/包指纹不能预填 |

所有固定 expected 用完整 typed 业务对象表达；同一个数据集的不同 policy/operation/selector 保持独立 ID、参数及摘要。输入/字段/ID任何delta使构建或check失败，不能静默混版本。

## 独立性与预先登记回归断言

83 的 triples/graphs/rdfsWitnesses/matches 来自 T05 已收件独立手选 expected，不因旧文件叫 inputs 而传入引擎；构建只解析这些有限集合及其来源。其他 finite fixtures 根据固定文本和已采用规范独立解释，没有调用 matcher/validator 产品或从输出生成 golden。

12个非标准date首错在root明确允许后，使用旧6891测试L275–313的预先登记literal断言：7/8/9/10在parser门，15/16在有限域门。`declaredRegressionAuthority`明确是 **pre-registered legacy regression assertion**，不是独立标准或固定库解析实现已证。未使用新probe或其运行输出；旧独审只说明原断言预先存在且未改，不作为预算/业务expected来源。

接口引用仅接收root AST literal-only提取的_PAYLOAD/_REASONING/_CHILD：旧7/15/11齐全，native缺名graphBudget、child缺名planDigest/budgetUsage已补。没有读取这些模块的解码/计算算法，也不由key存在猜/3格式。

## 尚不能计完整通过的字段

当前覆盖全部417：280项字段规格已定、137项含必要pending。该数字是规格状态，不是产品通过数；`wholeOracleComplete=false`。

- 82个可数学profile调用：完整数学expected已给，实际累计producer/copy/projection收费及真实child准入缺独立完整规范。单项尺寸低于cap不证明总收费通过；不得将历史78/4/1写成expected。
- 32个fullview/DAG/restore对象：顶层字段名齐全，但graphBudget/budgetUsage完整值/嵌套typed投影、真实同次发行与预算准入仍缺证。14负例另缺A1精确安全错误投影。
- 11个legacy正常观察的五字段DTO及全部evidence编码/警告字符串排序；3个正常scope的精确provenance编码；DAG text拒绝的精确错误投影。
- 7项精确前门码/阶段：坏空格IRI、两个nni负值、scope missing-source/wrong-source/missing-result/unselected-result。另implicit-jsonld守卫的实际异常投影。拒绝/零Validator/无部分业务结果仍有明确约束。

每个缺口都有逐ID、逐字段的gap/required说明，见coverage.json。unknown/incomplete/unexpected-failure不被oracle匹配，collection exit0也不是originalOperationPassed。JSONL适配、完整预算/来源门及source/package真实验收另窗；本阶段不写最终比较器。
