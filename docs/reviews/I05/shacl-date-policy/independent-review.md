# SHACL date policy 独立静态审查

结论：最终设计静态有限通过。首轮发现的预算与首错误次序阻塞项已在最终稿 §5.1 关闭；本次未发现其他未闭合的设计阻塞项。此结论不表示日期能力已经实现、真实 Validator 已验证通过，也不授权产品施工或正式 execution 接线。

## 范围与输入身份

审查树为 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-shacl-integer-entry`，源码基线为 `7f99e9c62bed85b6fa38a8efb6be44ce3f1fba81`。设计和用户决定全文阅读；相关产品源码从该固定 Git ref 静态读取。固定环境库源码只作为文本阅读，未导入。最终设计已按以下字节与 SHA-256 核对。

| 输入                                                                                                       |  字节 | SHA-256                                                            |
| ---------------------------------------------------------------------------------------------------------- | ----: | ------------------------------------------------------------------ |
| `docs/iterations/I05/shacl-date-policy-design.md`                                                          | 22938 | `1457aea0ba8b15ed0d137492dd648bc846e9757e067cf2cf506b70949aa996cc` |
| 主 checkout `iteration-control/2026-10-21-weekly-release/SHACL-date-and-SQLite-user-decisions-20261022.md` |  2651 | `6fd2c6162bef2da5b2d9f6a218a0482fb12ab5a6e2811efcfcf4d477a80e9c8f` |
| 基线 `packages/engine/src/ontolearn_engine/semantic.py`                                                    | 58495 | `1a2bfd40bc30a7a4ba5f90ab79cba5d9e0a4311b028681d8ceced528e1982075` |
| 基线 `packages/engine/src/ontolearn_engine/semantic_turtle.py`                                             | 33916 | `4180feb9d0c775669b65338e1cfb37a8d5bb7f3ce155b4804dd53a43efad5214` |
| 基线 `packages/engine/src/ontolearn_engine/semantic_error_adapter.py`                                      | 15426 | `0572b4730ba1ac28192e84633633d7da222e6603ff7da811c84e1f368eb55014` |
| 基线 `uv.lock`                                                                                             | 28440 | `86dfe82d952e2c88edcfc5658f488f6e1f0d04b4ec3b1e6f5c5d3bc4f57e8b73` |
| `.venv/lib/python3.12/site-packages/pyshacl/constraints/core/value_range_constraints.py`                   | 15659 | `f4a18946cd0a328fff0be4d35412572321b19b5cd4b1252c8ef520231cf82299` |
| `.venv/lib/python3.12/site-packages/pyshacl/rdfutil/compare.py`                                            |  9761 | `546ad62a98f62b99c33e90b334588d7710a0c09e05c04639eed461f31760a7df` |
| `.venv/lib/python3.12/site-packages/pyshacl/shape.py`                                                      | 33733 | `b5dd7f31207c0f7894211188b2213e1e1fefb26a376c7a26baa70194bda3064e` |
| `.venv/lib/python3.12/site-packages/rdflib/xsd_datetime.py`                                                | 23387 | `88f5fe16466721f72618e981001a33d3108e574ac3301606da33bcaf8fa80555` |

## 原阻塞发现与关闭依据

**D1，P2，设计阻塞，已在最终稿关闭：新增 preflight 的预算及首错误不能由 Graph/set 枚举顺序决定。**

首轮 §5 只有总额度与若干收费意图，尚未固定收集、排序、缓存、重复引用及错误检查顺序。可复现的设计反例是：100 个共享 targetClass、不同 path 的 NodeShape，约 20000 个 focus，仅一个 path 含库可接受但不满足本政策的非 Z date。两图均可落在原文本和 triples 上限内。若先检查该 path，可先得到 `RDF_TERM_INVALID`；若先扫描足够多空 path，可先耗尽额度而得到 `GRAPH_INPUT_LIMIT`。这是静态反例，未运行构图或测试。

最终稿第 83–104 行补齐了该缺口：固定关联、bound、focus 和 value 的稳定顺序；先完整收费收集及排序再核该集合的日期域；每次迭代器建立、包含 StopIteration 的拉取、成员保留、键、排序预约、缓存命中及重复读取均先付；缓存限定本调用按 class 首次使用建立；日期字段与库兼容检查的先后及错误优先也被明确。收集期间不足额度直接资源拒绝，不再寻找更具体错误；底层枚举顺序不再决定同一集合中先核哪个坏值。第 104 行保留了上述反例以及域错误先到、预算先到两类独立验收，未把资源拒绝改写为词法错误。因此此项在设计层关闭，实际收费与次序仍须由未来实现及运行证据验收。

同时复核第 49–54、102 行：每个 bound/value 先核有限域，随后立即核固定库值兼容；全部 bound 兼容通过后才进入事实 scope。最终稿消除了先前可能被读成统一后置兼容检查的歧义。

## 其他实质审查结论

- **版本与旧行为隔离自洽。** 新 `utc-date-range-v1` 显式选择独立入口版本；两个策略继续必填。基线 `semantic.py:1365` 当前只接受 range `legacy`，设计未把新增政策当成既有实现。旧 strict、整数 illtyped 宽点和 legacy 的受理域、错误次序保持；不改全局语义版本、转换表、规则 comparator 或正式 execution/scopes。
- **有限域与用户决定一致。** 双侧须为精确 `xsd:date`、11 个 ASCII 字符 `YYYY-MM-DDZ`、0001–9999 公历有效日期；不进行 offset 转换、词法修复或 dateTime 替代。第 37、51、85 行明确覆盖非 date bound 遇 date value 的反向混合，避免只按 date bound 分支检查。无关属性的合法 date 不被新增全图 Z 门误拒。
- **约束与 target 边界明确。** 本轮仅开放 minInclusive/maxInclusive 的 date 参数，相等通过。基线 `semantic.py:1243–1253` 的允许谓词不含 exclusive，设计没有宣称开放它；用户对 exclusive 的严格边界未被改成 inclusive 行为。bound 始终检查，包含无 target 的情况；数据域只检查真实 target/path/value 对，无 target 或无值不补造 violation，minCount 仍交真实 Validator。
- **target 等价论证有当前域前提。** 基线 `_shapes` 仅允许命名 NodeShape、PropertyShape、targetClass 与直接 IRI path；形状类型门排除了隐式 RDFS Class target，事实 scope 又排除 subclass/domain/range 公理。在这些限制下，设计第 58 行以实际 rdf:type 选 focus 与当前 Validator 目标选择相容。未来扩大继承、target 或 path 后不能直接沿用这一前提。
- **库复用与真实报告边界正确。** 固定 pySHACL range 组件经 `compare_literal` 比较，RDFLib date parser 会剥时区，因此单纯扩大白名单不足。第 54、64–68 行要求先核原词法和双侧有限域，再核精确 date 库值及年月日，之后一次真实 Validator；不一致固定 `VALIDATION_FAILED`、Validator0，不缩域或拼接普通违规。完整六字段、原 value lexical/datatype 和真实 conforms 均保留。
- **错误阶段未混淆。** 第 47–56 行保留严格解析阶段已有 `INVALID_LITERAL_LEXICAL` 优先级；形状参数出域是 `INVALID_SHAPE`，实际比较对不兼容是 `RDF_TERM_INVALID`，事实 scope 和资源门各自保留。非法词法前门拒绝不被计为 Validator 的范围违规。
- **writer 与资源声明有限。** 第 106 行起仅申请 semantic.py 私有分支与新增独立测试，不接 Store/Job、execution、错误公表或 native。第 72–104 行只给新增显式 preflight 的固定工作单位，不声称覆盖库内部 CPU、运行时分配、物理内存或 H。SQLite 决策及 HOLD 未被本方案改变。

## 非阻塞实施验收门与限制

当前无未闭合设计阻塞。以下仍是未来实施验收，不能凭本报告视为已通过：0001/9999、闰年/月日、混合类型和原词法的真实库正反结果；无 target/无值及多 NodeShape 复用的真实 focus；一次真实 Validator 与完整报告；D1 的顺序、逐操作先付、收费和失败阶段；旧 legacy/整数宽点及旧 golden 的完整兼容。固定库不能满足已采有限域时应保留反例并窄修，不能改变用户域或预期求绿。

本轮仅做文件、Git 固定源码和依赖源码文本的静态阅读及字节哈希核对；未导入产品或库，未运行产品、测试、探针、worker、数据库、formatter 或性能验证。仅新增本报告，产品、旧证据及其他文档未修改。本结论只针对上表最终设计字节，不是产品能力、运行通过或生产安全证明。
