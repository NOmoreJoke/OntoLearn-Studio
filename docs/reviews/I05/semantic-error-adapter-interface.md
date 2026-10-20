# I05 纯语义错误适配接口

本轮唯一新增实现为 `semantic_error_adapter.py` 及专用测试。本地 feature 以 merge 提交 `bda48d78579622bb83cd7e326368c613033c4c2d` 纳入已批准 I03/develop `e45e6038b5e0f8f4adc69ed55aafccd75b3d3500`；保留此前 v4 实施 `2a8dcad9f9036ae49b96282d8bf64f279846b14e` 与责任交接 `06f0814a373cf7487ac0725bdb17155c66f13c7d`，未 rebase。共享 entrypoint / build-engine 与受保护 AGENTS 字节未变。

## I04 可消费的形状

```python
from ontolearn_engine.semantic_error_adapter import (
    ErrorContext,
    Origin,
    Producer,
    SemanticErrorAdapter,
    Stage,
)

adapter = SemanticErrorAdapter(
    error_catalog=canonical_errors_document,
    error_schema=canonical_schema_document,
)
error_dto = adapter.adapt(
    producer=Producer.TURTLE,
    reason=internal_reason_code,
    context=ErrorContext(stage=Stage.SYNTAX, origin=Origin.VERIFIED_USER_INPUT),
)
```

构造参数是由 I04 从可信只读 canonical 资源载入的完整 `packages/contracts/v2/errors.json` 和 `schema.json` 文档。适配器自身不读取路径或 I04 模块、不决定资源位置，不依赖尚未冻结的运行时包布局。messageKey、retryable、参数白名单和错误字节预算直接由唯一规范目录派生并核对 schema 的对应分支，不硬编码第二套真相。所需目录或 error 节点损坏 / 不一致时构造以固定本地配置错误停止；不能在没有有效目录时编造公共错误 DTO。

配置核对覆盖所消费六类的参数规范及整个 error 节点的唯一 const-code 分派，不替代整份协议 schema 的批准 / 来源完整性校验。

输入仅允许精确枚举 / context 类型：

| 类型 | 有限成员 | 含义 |
| --- | --- | --- |
| Producer | TURTLE、QUERY、REASON、SHACL、PROJECTION、PUBLIC_PARAMS | 已由可信调用边界确认的实际产生分支；不是 renderer 自报的函数名。 |
| Stage | SYNTAX、QUERY、RULE、CONSTRAINT、PROJECTION、PARAMS | 已确认的输入 / 执行阶段。Turtle 可为 syntax 或 constraint，query 可为 query 或 syntax 数据项，reason 可为 rule 或 syntax，SHACL 可为 constraint 或 syntax 数据项，投影仅 projection，公共参数仅 params。 |
| Origin | VERIFIED_USER_INPUT、TRUSTED_INTERNAL、UNKNOWN | 已确认用户提交内容、可信服务生成 / 适配器输入、或无法归类。它不表示适配器验证过身份或权限。 |
| ErrorContext | stage、origin | frozen 数据对象，嵌套枚举也逐项验证；未知类型 / 值或不匹配组合安全兜底。 |
| reason | 精确 str 的内部固定细码 | 不接收异常正文、任意详情或安全参数字典；不调用异常对象的 str/repr。 |

内部 reason 仅接受1至64字符的精确固定码；空串、超长、带前后缀的变体不 trim、不解析，直接兜底。已知细码也必须与真实 producer×stage 白名单一致。Stage.RULE 在有限推理执行分支中包含 RDFS / 受控规则工作；图输入验证为 SYNTAX，不能以此阶段声明最终推理结果量。

输出仅四字段：`code / messageKey / params / retryable`，均满足 canonical `error` schema 和预算。返回新对象，无输入原值 / URI / 路径 / 堆栈 / 凭据 / 任意参数。retryable 只是规范元数据，函数没有任务重放、网络或状态副作用。

## 归责边界

已批准的25项 v3 映射以 `docs/iterations/I03/I05-semantic-boundaries.md` 第一张表为准，并优先于历史合码。用户内容的词法 / 已知非法项按实际 syntax / rule / constraint 等阶段归类；可信生成项违约和不能区分者返回 INTERNAL_ERROR。类型 / 选择组合错误只有在 PUBLIC_PARAMS＋PARAMS 且来源已确认为用户参数时映射 INVALID_REQUEST/params；不能把传入解析器的非字符串机械归容量或归责用户。

真实资源 / 工作预算和外联阻断由对应已确认引擎分支映射已有有限类别；合法但范围外构造只有已确认用户语义来源时才可给出该构造分类。未确认来源、未知 producer / reason / phase、旧歧义合码及未分类路径均走 INTERNAL_ERROR。v4 的可信所选载荷 / 来源不一致复用 INTERNAL_ERROR；实际最终投影视图量超限复用 semanticResult，累计投影工作量复用 semanticWork。没有新公共码、参数枚举、方法或运行能力。

`INVALID_TURTLE` 的真实文档解析失败按已批准历史条目固定为 field=syntax（即使所解析文档是约束）；`INVALID_UNICODE` 则按实际 syntax/query/rule/constraint 入口分流。最终查询量只接受 QUERY×QUERY，RDFS / 匹配 / 依据量只接受 REASON×RULE，最终投影量只接受 PROJECTION×PROJECTION。

阶段必须来自可信实际分支，不得仅按操作名或异常文本猜测。例如 `check_shapes` 对数据图与模板图均可遇到非法字面量；未确定是哪一层时使用 UNKNOWN 来源并兜底，不能一律标为 constraint 用户错误。

## 验证与剩余接线

用独立写明的规范 golden DTO 覆盖25项映射及用户 / 可信生成 / 无法分类来源、未知输入、阶段错配、canary 不外泄和完整 schema / 受限字段边界。独立审查的3项真实发现及两项开发自查阶段分类修正在证据中保留失败和复核。最终命令与来源哈希统一见 error-adapter-e45.json；纯适配验证不扩大为正式完整链路通过。

I04 仍需实际构造可信上下文，完成资源 / immutable producer / 内容摘要 / 权限验证、Job持久状态与 bridge / UI 的安全错误传播。纯适配器既不读 Store/Job，也不证明上述上下文为真。真实 I04 合并后仍需刷新基线、全链联验与双方新全范围审查。原 v4 测量 / 包内证据只属于其原来源，不据此声明新基线打包或完整 I05 通过；本轮不重跑不变测量和包、不启动窗口、不 push。
