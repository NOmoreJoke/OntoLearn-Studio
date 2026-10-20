# I05 / B1 独立候选验收与集成接口需求

执行状态、验证版本和剩余门禁统一见 [I05 状态](../../reviews/I05/status.md)。依据为 PRD V0.6 附录 C/D/E/G、原计划 B1 全文及 S1 测量定义；原文保留在 I01/inputs，不改写归档。

当前独立阶段原始证据与源文件哈希见 [independent-v2.json](independent-v2.json)。JSON 原字节以 `.json.raw` 保留，体量不足 1 MiB，用于尚无 CI artifact 时的离线复核；大构建缓存、下载压缩包、二进制和旧版测量只保留在独立 build 目录，不提交。

许可与导入证据包含 uv.lock 全依赖、实际 PyInstaller 归档模块、RDFLib plugin entries、pySHACL assets、wheel 元数据/许可、CPython 及其静态原生依赖。PyInstaller bootloader 的 COPYING/例外和工具的 vendored 许可亦保留；清单角色表示声明依赖或构建工具，不声称工具的间接 vendored 模块一定未进入归档。当前 macOS Python 原生来源以官方 PBS 的 15 个文件段匹配验证，原始 PYTHON 元数据按字节保留；跨平台运行时另行匹配，不能套用本机来源。系统 libz 的上游元数据存在 zlib-ng 许可路径缺失，实际 link=system z 且动态链接可核对；不冒称包含 zlib-ng。

## 候选决定与实际边界

RDFLib 7.6.0、pySHACL 0.30.1 及全部传递依赖固定于 uv.lock；规则使用仓库内有界三元组模式 join，无额外规则库。pySHACL 所需 owlrl 随包存在，但不启用 OWL-RL/RDFS 默认扩张、SHACL-AF、JS、导入或任意约束。只调用锁定 Validator 的内存 Graph API，避免通用入口 URL/path 加载及 RDFLib 全局布尔转换 patch。

| 候选能力  | 验收与有限语义                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Turtle    | 固定 data 文本、Turtle parser、绝对 IRI、稳定事实身份；保留中文、语言、字符串/布尔/有限常见数值与日期类型。非法词法、NaN/Infinity、未知 datatype 明确拒绝。非列表空白节点、其他 RDF 格式及超范围 OWL/RDFS 拒绝，不做自动格式推断或删减。                                                                                                                                                                                                                                 |
| 查询      | SELECT/ASK，Graph 内只读；递归检查已解析代数，SERVICE（含 SILENT/变量/嵌套）、所有 FROM/FROM NAMED（含 file/相对 BASE）在求值前拒绝。扩展函数、随机/时间/UUID/BNODE、除 COUNT 外的聚合（含 SAMPLE/GROUP_CONCAT/SUM/AVG/MIN/MAX）、LIMIT/OFFSET 不支持；不可变结果的服务分页待真实任务接线。ORDER BY 只接直接投影变量，RDF 值相等时用规范词法/类型作稳定次序；无 ORDER BY 的完整结果规范排序。未承诺任意昂贵查询的进程内执行时限，正式执行须由 I04 有界隔离 worker 承担。 |
| RDFS      | 仅子类传递/类型、domain/range 类型推导；label/comment 不参与推理。结果含相关公理与直接输入事实依据。不是必填校验、OWL-RL 或完整标准推理。                                                                                                                                                                                                                                                                                                                                |
| 受控规则  | 全部规则固定读取断言＋RDFS 闭包；收集结果后返回，不触发第二条规则或再次 RDFS。受控输出为领域类成员/属性断言，禁止生成本体公理或任意谓词。全部有效匹配保留完整输入和原始依据；潜在链给 RULE_CHAIN_UNSUPPORTED 提示，允许保存/启用，显式断言事实仍可直接匹配。                                                                                                                                                                                                             |
| SHACL     | 命名 NodeShape/PropertyShape、targetClass、直接 URI path、min/maxCount、datatype、in 列表、min/maxInclusive。空白节点仅用于完整无环允许值列表。白名单覆盖整个形状图；未知约束、复杂路径、SPARQL/JS/target/function/validator/rule 均拒绝，不得静默 conforms。结果来自真实 Validator，含 focus/path/component/sourceShape/value/severity。                                                                                                                                |
| 验证范围  | 只验证调用者明确提供的事实图，不自动注入本体或当前推导；有意使用推导时须由应用层显式选择并记录实际范围。拒绝把 subclass/domain/range 公理混入验证输入，因为 pySHACL 的 targetClass 在 inference=none 时仍会沿子类匹配。                                                                                                                                                                                                                                                  |
| 外联      | 产品入口不接受 URL、path、可选 parser/store/processor 或 pySHACL 通用 kwargs。文本/形状中的 owl:imports 直接拒绝。执行期 context-local audit hook 阻断 socket（含 DNS）/urllib 与子进程；不改变其他任务的网络配置。此 hook 是 Python 库执行防线，不是 OS 沙箱或敌意 Python 代码隔离。                                                                                                                                                                                    |
| 错误/资源 | 内部只返回固定 SemanticError.code；解析器原值诊断在语义上下文抑制。1 MiB 文本、10 万输入/结果三元组、有界规则/匹配与累计工作预算属工程防护，不是业务容量验收线。最终错误信封/分页/持久状态由 I03/I04 接线。                                                                                                                                                                                                                                                              |

## 固定用例与完整预期

同一 semantic_samples.suite 在源码与真实 app resources/engine executable 执行。它使用 S1 固定 18 条 G-base 结构孪生事实和独立 ontology，身份不与 S1 prepared storage fixture 混用。

- Q-01 结果恰好 A01；Q-02 关闭 A01 后完整空集合。ASK 真值和字面量中的 SERVICE/FROM 正例另验。
- V-01 删除 003 名称，只产生其 NameProperty/minCount 违规，补回后消失；真实各有限模板另验证完整对象/路径/组件/来源约束/值/等级。
- R-01 风险仅 001，完整依据含 A01 和 R-risk。R-02 删除 A01 后纯重算空集合；存储的过期/撤回发布另待集成。
- R-03 A04 替代 A01 后风险保留，依据不得再包含 A01。
- R-04 P001/CriticalPump 先产生 Equipment 再被 R-risk 使用，完整风险集合为原 001 和 P001。
- R-05/06 R-next 保存启用但无二阶 NeedsInspection；交换规则顺序得到完全相同结果/依据/提示。
- O-01 删除 003 告警后查询为空，只表达未记录，无闭世界否定推导。
- 额外单元覆盖子类循环、多跳、domain/range、无规则/RDFS反馈、多个依据、重复变量、非法规则与类型、相同路径/组件的不同形状、混合范围拒绝和工作预算。

映射、行为、E.5 沙盘不是该纯语义模块的实现范围。附录 D 的过期、原子提交、历史及取消必须在真实 S1/I04 集成阶段按原验收补齐，不能用预制状态或任务替身抵扣。

## 无窗口验证和测量方法

`npm run check`、`npm run verify:sources`、`npm run package:dir`；只调用包内 Python engine executable，绝不启动 Electron。`uv run --frozen python scripts/verify-i05.py --packaged '<实际包内引擎路径>' --output '<独立证据目录>'` 执行同样例、网络接收端校准/零命中、两档三重复。

测试专用本地接收端仅接合成探针：先正向请求证明可达，再检查产品所有拒绝入口零命中、零 socket/DNS/urllib 尝试。另故意绕过产品格式门，仅在探针中调用真实 JSON-LD 库加载入口，证明同一执行 guard 在 urllib.Request 事件处拒绝。产品不启用 HTTP 服务，不外发业务数据。

S1 原 seed=20261019、独立 urn:case:{i} 命名空间、18/180 事实、输入/查询摘要和完整结果保持一致。另报四条 ontology、公理和重分类后的语义输入摘要；真实 RDFS 结果完整集合为每份 8 条类型推导＋共同 1 条传递公理，规则结果每份一个风险设备。SHACL 范围单独用原断言事实，不能把该 ontology 混入范围。

每档各三次新子进程，源码/包内共十二条原始 JSON。S1 phase 原名原口径保留；候选 FirstAfterS1 明确经过 S1 查询预热，Warm 为同进程重复。独立 startup mode 测量三次“新进程启动、导入候选模块、输出 ready 并退出”的总墙钟，含进程收尾，不称纯 import 时长；真实 OS 冷缓存未控制。perf_counter_ns、tracemalloc 当前/峰值及 lifetime ru_maxrss 分开记录；后者不是阶段 RSS，tracemalloc 不覆盖全部原生内存。失败、stderr、设备/版本、包体/文件哈希与动态链接清单保留。

## 待 I03/I04 冻结后的纯接口需求

以下是提交给唯一维护者的需求，不是已批准共享契约：

- 应用层将已授权、不可变项目输入和明确 scope 交给 worker；分别提供 ontology、断言/选定推导范围、query/SHACL/rules 定义。禁止传 URL、SQL、任意代码或库配置。
- 全部实际依赖包括相关 facts/ontology/规则/约束/查询定义及定义集合成员摘要，新增定义也要改变集合来源；不使用伪 facts 键替代漏报依赖。
- 入参与结果记录 inputSnapshotId、projectId、scope、dependencyVector/集合摘要、executionSemanticsVersion=i05-finite-1、engineVersion、dependencyLockHash；纯函数自身不决定 job/operation/session 身份或持久终态。
- 结果载荷分 asserted/derived、完整来源依据和真实 validation 违规；安全错误 code 最终映射 I03 注册表，不直接跨 bridge 暴露 Python 异常链。
- read-only 不改项目；发布结果经 Store 实际依赖复验，迟到/取消/失败不冒充 current。I04 worker 管总时限、取消和内存/队列，不能只靠文本/工作量上限。
- 实际任务、持久化、取消、错误、包内执行和窗口重建重连联验后，才可评估正式注册该能力；不得在当前 health 声明中提前加入。
