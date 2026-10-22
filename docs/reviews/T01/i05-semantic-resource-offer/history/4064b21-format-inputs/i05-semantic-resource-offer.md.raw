# I05 私有语义 artifact：四资源只读采用接收

2026-10-22。T01 对下列四件固定资源逐路径明确接收，**用途仅为 I05 新独立 source/package semantic artifact 的私有、不可变、只读供应副本**。不转移公共维护权，不替换批准 develop 或任何当前 T01 WIP，不启用公共契约、Store、Job 或能力。接收是本窗口的 owner 决定，不是已经完成构建或运行。

## 1. 固定范围与来源

- 工作树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-i05-semantic-resource-offer`。
- 分支：`docs/T01-i05-semantic-resource-offer`；base 为 `5f910b52c69d86a1076b2032e5d3c63e715947f3`。候选／过程提交由交付清单从实际 Git 记录，不在本文自引用 HEAD。
- 供应产品仅取 `6891a5842302859a531cf82767c5a482417bc274` 的 Git 原字节；合同仅取 docs head `ee2b30a2dad35b2d395f9c735aff80371ab41110` 的 §5.1–5.4、静态 import 闭包和资源调查。总控限定收件与本窗口全文已读，原件见本次 `inputs/manifest.json`。
- 新树开始仅受保护 `AGENTS.md` 为 M，15852 B／SHA256 `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`；不得暂存。共同规则17891 B／`e437121a08053544c2a09151ac5183baf15b5fa67a3a604891aaa9e77ba971b0` 与前次全文读取的原字节一致。

## 2. 逐路径决定

| 固定供应路径 | bytes | SHA256 | 明确决定与用途 |
| --- | ---: | --- | --- |
| `packages/contracts/python/contract_v2.py` | 34608 | `17aa68bc2271b45ffb70a023b9db9e441bb1b4e79fc9a42bb6932f60631be7b7` | 接收：原样 canonical `resources.CONTRACT` 的启动，及普通固定错误目录／`validate("error", value)` 所需闭包；不授权其它公共服务入口 |
| `packages/contracts/v2/schema.json` | 207256 | `e913138e6f3ac632268ae7f8c2461577022e8298d1c03e0668416a0d654eaabf` | 接收：checker 启动所读原三 JSON 之一及普通 error 结构；不开放新增 v3 schema 的业务执行 |
| `packages/contracts/v2/registry.json` | 15962 | `1f2e298209e238433c02864a05c70b24482e4c1fd00e7309f63eac84a1f3706b` | 接收：checker 原启动读取与 resources 原 registry bytes/hash；不把已包含的 capability/profile 数据当运行授权 |
| `packages/contracts/v2/errors.json` | 16299 | `ad242d93ced7a0c8a463b708b7a1f3105e65f03c3980e0a0c6c4309f8c26544c` | 接收：固定普通错误码、messageKey、retryable、params schema 和原2048编码限制；startup/business3 分支不因此得到执行许可 |

四件均已实际核 Git blob、bytes/SHA，并与批准5f逐件生成差异。没有拒绝项，也没有选择替代 ref；上表不允许混合5f、当前 HEAD 或未来修改版本。原始副本只存本次 review 的 `.raw` 输入，不写入产品路径。

## 3. 顶层副作用与真实静态读取面

固定 `resources.py`（3065 B／`177f57db2c3e768b9fc17d0c9e0665677e6aab55c16003ac7f304254c10d2238`）第9–32行：计算 source/frozen 路径，以 `spec_from_file_location`、`module_from_spec`、`exec_module` 执行原 checker；随后再次读取 registry 原 bytes 并哈希，再读取／哈希实际 lock。checker 第6–16行只 import stdlib，在顶层读取三 JSON 并保存 DOCUMENT／DEFINITIONS／REGISTRY／ERROR_CATALOG；其余函数定义不等于已调用。没有将“只读”误写成“没有顶层执行或副作用”。

`semantic_identity(profile=True, explanation=...)` 只返回 IMPLEMENTATION 的新 dict，并选择 finite-7 或 finite-8；IMPLEMENTATION 的 lock hash已在 resources 顶层计算，原全局 executionSemanticsVersion 仍为 i04。identity 不认证 Job、snapshot、origin、ready 或代码闭包，也不授予执行权限。`resources.safe_error` 的允许闭包是普通目录查询、`CONTRACT.validate("error", value)`、固定 INTERNAL_ERROR fallback；不将任意 validate 名称作为本 offer 的入口。

动态 checker 模块名是 `ontolearn_contract_v2`。原 loader 没有把它缓存到 `sys.modules`；本 offer 不虚称已证运行时单实例。未来须仅由 canonical `ontolearn_engine.resources.CONTRACT` 持有／消费，禁止 alias import、重新 exec 或复制 checker。真实 source/frozen 单实例与资源身份仍须后续同版执行验证。

已按原闭包逐项核22模块 bytes/SHA，并从 AST 重建128条 literal import 边，与固定闭包一致；607个 schema `$ref` 均有本地目标，schema定义所用关键词均在原 checker KEYWORDS 内。这些是静态资料核验，不是产品导入或 validator 运行。两个 quality 懒导出 definitions/planning 在固定供应 map 缺失，仍明确禁止调用／收集；不能由22的数量推断无动态导入或第三方资源需求。

固定22模块中实际资源调用点为 `semantic_execution.py:731` 的 `semantic_identity(profile=True, explanation=explanation)`，resources 内为 ERROR_CATALOG 查询和 `validate("error", value)`。lexical 全函数扫描还真实发现 `resources.py:97` 的 `main()` 内调用 `resource_manifest()`；该 main 不在获准入口，故不能把扫描结果写成“源中没有禁用函数调用”。新 probe 尚未实施，必须在其冻结后再核完整调用面。

语义闭包另有真实顶层副作用：`semantic_offline.py:32/42` 注册 audit hook 与 RDFLib logger filter；dataclass／正则／有限常量也会初始化。本次只读识别它们，未安装 hook、未执行第三方 imports，也不由T01四资源接收代签其物理／whole-H或完整I05行为。

## 4. schema／registry／错误兼容结论

相对5f，schema原66项 `$defs` 全部逐值相同，新增28项为显式 changeset/business3/startup定义，无删除；普通 error 及 implementation 等旧定义不变。checker旧函数中只有 `validate` 改变：成功形状校验后增加 `_changeset_semantics`；对本用途的固定名称 `error`，该函数落到末尾 True。其 `check/equal/semantic/encoded_size` 原函数 AST 均未变。新增11个函数没有顶层自动执行；本接收不授权调用它们或扩大到任意schema。

registry原24个 capabilities 均逐值不变，新增 `changeset.preview`、`changeset.diff.page`、`changeset.confirm` 三项，v2Runtime不变；foundationProfiles/startupDiagnostic新增。资源加载不会自动 dispatch，故保留其原字节可供私有 startup/hash，不等于采用公共 runtime3／ready 语义。

errors原所有顶层字段逐值不变，新增 foundationProfiles/startup；普通26码无新增、删除或变更。逐码比较其 messageKey、retryable、paramsSchema 与 schema普通error的26个 exact oneOf 分支，均一致；每分支保留四个required字段和 additionalProperties=false，INTERNAL_ERROR仍为空params安全fallback。此处只比较 JSON 与 AST，没有构造并执行错误或调用 checker，不能写“错误运行用例通过”。

## 5. 路径与不可变组合条件

| 域 | checker | 三件 JSON | 额外 lock（不是本四资源采用授权） |
| --- | --- | --- | --- |
| source checkout | `packages/contracts/python/contract_v2.py` | `packages/contracts/v2/{schema,registry,errors}.json` | 仓库根 `uv.lock` |
| frozen | `_MEIPASS/contracts/python/contract_v2.py` | `_MEIPASS/contracts/v2/{schema,registry,errors}.json` | `_MEIPASS/provenance/uv.lock` |

checker 从其实际 `__file__` 向上定位 v2，resources 按自身 source/frozen 根定位 contracts；因此保留上述相对布局，不扁平化或移动 checker。resources 对 registry 的两次读取必须对应同一精确字节。source原 resolver使用resolve；本次没有执行路径／符号链接／包内读取验证，不据此保证任何实际文件系统布局。

6891 lock为28440 B／`86dfe82d952e2c88edcfc5658f488f6e1f0d04b4ec3b1e6f5c5d3bc4f57e8b73`，已只读核身份；它由T03/root另外锁定。resources本身、22模块、T03四writer、lock、第三方资源／metadata／许可、新probe／sealed assets及构建provenance不因本四件owner接收取得维护权或默认运行采用。T03最终组合须逐项列真实ref/bytes/SHA；替换任何一件都需具体组合delta和相应同版复审。

## 6. 明确拒绝的用途与后继门

本offer拒绝调用 `resource_manifest/build_request/execute_request/derive_dependencies/permits_transition`，也拒绝通过其它公共 helper 间接抵达它们；dependencies/states 的延迟读取不在三JSON闭包内。原 `resource_manifest` 会glob八JSON，不能在未来调用时仍沿用“三件足够”的结论。fixtures/binding-regressions/frame-fixtures不作为本独立artifact运行资源；历史guard不删。需要任何新增调用或资源时，先另交owner delta，不复制契约、不伪造registry、不静默fallback或拼接替代ref。

该接收不授权修改公共文件或重新授予其未来维护，不运行产品/DB/native/GUI/业务child，不安装依赖、测试或构建；T03专用计量预算未使用。整个worker对象界、真实owner/Store/Job/selected、SQLite损坏输入保护与物理HOLD、原T01 blocked Goal、S1/B1、指定双模型、CI/目标OS/真人及推送合并门全部保留。独立审查仅证明此静态owner offer范围，不代替指定外审。

## 7. 验证与独立审查交付

可恢复原件、机器比较、顶层静态清单及脚本均在本次review目录；验证记录见 `verification.md`，候选清单见 `candidate-manifest.json`，新独立审查与逐项处理在同目录单独保存。冻结候选后审查，不与审查者并发修改候选；所有首轮结论和增量均保留。最终报告的实际结论、过程head和Git状态在交付记录中据实记录，不预填通过。
