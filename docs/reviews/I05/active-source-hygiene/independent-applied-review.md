# I05 两源 hygiene 实际应用窄独审

**结论：允许范围内未发现 P1/P2。** 实际修改落实了 `timed`、`build` 和四个 lambda 的六处、九个可选 keyword-only 默认绑定。独立 checker 严格只撤去这些新增参数并恢复一处本地 import alias 排列后，整个 probe AST 与固定 401a 完全相同；整个 test AST 无需处理即相同。这支持修改范围与当前同步调用形式保持的结论，不构成完整语义运行验证、fullcheck 或发布批准。

## 固定身份与审查边界

| 项目            | 当前观测                                                                                                      |
| --------------- | ------------------------------------------------------------------------------------------------------------- |
| tree / branch   | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-active-source-hygiene` / `fix/I05-active-source-hygiene` |
| HEAD / 比较基线 | `401a6844d25b8990606ae82fc85f932cac352d40`                                                                    |
| probe           | 102669 B；SHA-256 `05f4ac85f883f40142782e9ee3943b8df9593ddf5a35e318ca35bbd6781a6dd4`                          |
| test            | 75277 B；SHA-256 `920883c27b6390a2f38aa71bbb399d3b588fe819b1298282da60e6217f11694b`                           |
| 现行根 AGENTS   | SHA-256 `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`；指定源/证据路径未发现附加 AGENTS  |

读取两源全文 bytes/AST 仅用于身份、完整结构及 COMMENT 序列比较；人工 body 审查限于 `_b1_observation`、其直接调用表达式、`CollectionBoundary` / `_checked_call`、`ProbeFault`、scope 的首部 guard 和精确新增测试。没有展开其他算法或 canonical 模块，没有读取 T03 WIP。只创建 `independent-applied-*` 新文件，不改 owner/source/AGENTS/index/HEAD、原 lifecycle 复制文件或原输出报告；未 stage/commit。

## 独立比较结果

独立 checker 读取 401a 的两个 Git blob，与固定 current bytes 校验；随后在内存副本中执行白名单规范化：

1. 严格识别 `_b1_observation` 内 `timed`、`build`、`semantic.query` lambda、`semantic.reason` lambda、`semantic.check_shapes` lambda、`canonical_bytes` lambda，要求六处唯一，原版均无 keyword-only 参数。
2. 要求新增参数名逐项精确匹配，默认值只能为同名 `Name(..., Load())`，无 annotation/type-comment，且九个参数全部有默认值；仅移除这些 `kwonlyargs` / `kw_defaults`。
3. 要求唯一局部 `from rdflib import ...` 的 module/level 不变，三个 alias 均无 asname；只将 current `RDF, Graph, URIRef` 排列恢复为 base `Graph, RDF, URIRef`。
4. 比较忽略位置属性的**整个** probe AST，结果相同；比较整个 test AST，结果相同；两源 COMMENT token 文本序列也各自相同，没有新增 noqa/ignore 注释。

因此除此白名单外，selector、assets、pins、public codes、底层调用表达式与参数、guard/test 及其他既有 AST 均保持；这是完整结构相等推出的保持结论，没有另行展开这些模块，也没有声称它们全部通过运行验收。格式化导致的行号、位置和源码展示变化仍然存在，AST 比较不会检验 traceback 行号、反射源码文本等行为。

## 六处绑定与当前生命周期

| current 行 | callable                   | 新增可选 keyword-only 默认值           |
| ---------- | -------------------------- | -------------------------------------- |
| 2111       | timed                      | `name=name, phases=phases`             |
| 2132       | build                      | `asserted=asserted, ontology=ontology` |
| 2152       | fixedSelect lambda         | `combined=combined`                    |
| 2157       | rdfsRules lambda           | `combined=combined`                    |
| 2167       | SHACL lambda               | `asserted=asserted, shapes=shapes`     |
| 2182       | resultSerialization lambda | `outputs=outputs`                      |

默认值在当前 def/lambda 创建时求值并保存同一对象的强引用。timed 创建于每轮 name 已确定、phases 新建之后；build 创建于本轮 asserted/ontology 同步返回之后；两个 combined lambda 创建于 graphBuild 返回之后；SHACL lambda 创建于本轮 shapes 返回之后；outputs lambda 创建于本轮 outputs 字典构建之后。未复制或冻结对象，同一 graph/dict 的原地修改仍可见。将来若 callable 被保留，这些默认值可延长对应本轮对象被强引用的时间；未测量回收时刻、引用计数、物理内存或性能，不作增减承诺。

签名确实变化：timed 从三个必需位置参数增加两个可选 keyword-only 参数；其余五个 callable 从零参数变为有可选 keyword-only 参数，仍允许原零参数调用，仍不接受位置参数。当前内部 timed 的三位置参数调用、build/lambda 的零参数消费形式不变；未承诺外部反射、动态替换或未来 keyword 调用完全不受影响。

`timed` L2112 才记录 start，L2113 立即调用 `_checked_call`，L2114–2119 在返回后写本轮 phases 并返回 value。默认值求值仍位于原 callable 创建处、该 timed start 之前，没有将 canonical 工作移出计时区间。调用顺序仍是 asserted parse → ontology parse → build → query → reason → shapes parse → SHACL → outputs → serialization → passes append；调用表达式与 args 保持原 AST。对象绑定求值本身可能带来计时外开销，不保证耗时数值相等。

`_checked_call` L317 在无 context 时直接同步 `function(*args, **kwargs)`；有 context 时 L318 调用 boundary.call。`CollectionBoundary.call` L296 前置 check、L301 同栈调用、L303–304 finally 计时、L309 保存返回 value、L310 后置 check 位置及 args/kwargs 转发均未改。该实现不保存 callable，也没有新增队列/await。当前路径中每次闭包消费结束后才进入下一阶段/下一轮，原审查未见实际跨轮错误这一结论仍成立；此次改动是显式绑定当前轮对象，并非证明旧实现已发生错绑。

默认绑定不能自动使未来异步/延迟执行安全：phases 写入次序、共享对象原地变化、超时/取消、异步返回值以及运行时 boundary/_checked_call 替换仍需单独审查。没有把静态同步实现当作实际 runtime context 的证明。

## M06 及既有静态流

`ProbeFault` current L261–266 的整个 AST 保持。`_scope_observation` 的整个 AST 保持，首个 guard current L1550–1551 仍为 `if counter is None: raise ProbeFault("INTERNAL_ERROR")`；精确测试 `test_scope_without_counter_fails_before_loading_canonical_inputs` current L845–850 的 AST 保持，仍用空 mappings 验证缺失 counter 在输入 lookup/调用前失败并断言固定 code。这里仅审查代码与结构，没有执行测试，也没有把空 mappings 当业务结果。

owner 的六份已授权 command receipt 及其每条 raw stream 均按 bytes/SHA 独立核对相符：environment/import fix/两次 format write/lint/format check receipt 均记 exit 0。lint raw stdout 精确为 `[]`、stderr 为空；format check raw stdout 为 `2 files already formatted` 加换行、stderr 为空。以上是既有真实静态流的读取核验，本 reviewer 未重跑 source lint 或 formatter，也未重建环境。

## P1/P2 与限制

- P1：无；P2：无（只针对本次固定两源窄差异）。未发现需要立即回报的实义风险。
- 本次独立执行仅 pinned Python 3.12 的 stdlib AST/bytes/token/hash 与只读 Git，以及新审查文档的指定 Prettier；没有 import/compile/runpy 产品，没有 pytest/B1/canonical/fullcheck、安装/uv、构建/打包、环境/DB/native/GUI/Goal/push。
- 不把当前 lint0/format0 清掉父候选的其他旧失败或视为产品已通过。原必要 fullcheck、新供应/集成后的验证及冻结候选独立门禁仍由 owner 完成。本任务未检查三共享配置或 T03 后继。
- `independent-applied-proof.stdout.raw` 是可复核 checker 的真实 stdout，含逐项 AST 检查、精确必要 snippet 和 owner raw stream 核验；stderr/exit 与命令 receipt 独立保存。checker 自身亦留存以支持复现，未执行原产品。未覆盖任意将来动态行为与运行时证据。
