# I03 验收与 I04 接入清单

依据为 PRD V0.6 FR-006/303–304/401–404/500–505/600–705/803–805、8.6/8.7、10.2–10.5、附录 C/D/E/G；S1/S2/U1 原计划逐字输入与当前总控范围见 [sources](../../reviews/I03/inputs/sources.json)。以下冻结设计与异常语义，不将未执行运行项减为可选。真实执行结果集中见 [status](../../reviews/I03/status.md)。

## I03 必须通过

| 验收                              | 可评审证据与测试                                                                                                                                        |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 信封与每方法 params/result 都严格 | schema.request/response/notification、registry 的可解析 schema 引用；TS/Python 同一 fixtures：每方法成功、未知额外参数、版本/kind/结果错误互斥反例      |
| hello、身份与响应绑定             | 协议文档的 bootstrap/无交集/重复 hello/预握手拒绝，matchesResponse 的 request/session/method/project/job/nonce 绑定；实际常驻握手由 I04 测              |
| 安全错误                          | 全码成功/非法 params/messageKey/retryable 的跨端语料；固定五参数以内、2048字节上界、受限引用；不携带原值/路径/堆栈                                      |
| 取消与状态                        | states.json 全状态笛卡尔积正反例、cancelling→succeeded 的最终提交证明门、零轮 null/两轮保留/非轮次拒绝；不设成功当前推断                                |
| 真实依赖                          | dependencies.json 选择、闭包与缺失引用拒绝、asserted/derived 的完整依赖集合比较、新规则集合增加；S1 八码+model=null 一致性                              |
| U1                                | 项目/任务/不可变结果/实现/范围/参数身份与 client 草稿边界完整；current/stale/historical/evicted 区分；跨项目/输入/范围/参数/页大小/游标未知与到期拒绝   |
| S1 实际边界                       | kind 非空字符串与来源守卫、NULL 指针反例承接、legacy config ValueError；数据库完整 dump 零副作用、合法 kind 只保留唯一 current                          |
| S1 交接无遗漏                     | jobs-and-storage 全部历史编号、缓存全库与 pin 顺序、人工值恢复、固定 ChangeSet 顺序、项目级 facts、严格 revision、锁/I/O/终态幂等均明确                 |
| 独立审查与源输入                  | 内部独立只读审查及逐项处置；指定 GLM-5.3/最高和 M3.1-Flash/xhigh 同版完整外审。原输入逐字 SHA 一致；不混入他方 AGENTS/计划/原型                         |
| 仓库静态与引擎回归                | npm run check、contracts 独立 `npm run typecheck --workspace @ontolearn/contracts`、verify:sources、diff --check；本机不得启动 Electron/原生/HMR 或产物 |

纯校验器不解析原始 JSONL，也不实现 worker/队列/运行状态存储。原始字节及重复键由 I04 reader 验证，公开 DTO 的 schema 通过不能证明调用者有权限、marker 真存在、hash 对应真实数据或引擎计算正确。

## I04 必须实际完成的原验收

| 原 S2 退出项                    | 本版确定的合同与 I04 实际测试要求                                                                                                                                                                                                       |
| ------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. 常驻 health / 多请求 / JSONL | 一个 session 多次 health 复用真实进程；并发乱序关联；拆包/粘包/跨 UTF-8/CRLF；坏 JSON/重复键/BOM/深度/超长未终止帧，追加前限额；连续超限与终态后 chunk 清 pending。重复请求 ID、未知方法、v1/v2 不兼容、握手前/二次 hello；修原 M1 注释 |
| 2. 忙碌取消/心跳/有界资源       | 真实隔离计算仍响应控制；队列满结构化拒绝；无总量只阶段；独立启动/握手/请求/总量/心跳/取消期限及内存上限。测试能力不得进正式声明                                                                                                         |
| 3. 竞态/worker/恢复             | 映射/ChangeSet 提交前中后取消、异常、磁盘/退出；零轮/部分轮/响应丢失/最终提交后取消；原子 marker/job 状态恢复；隔离 worker 不伤他任务；有限退避与 pending 清理；完整最终证据缺失不得成功                                                |
| 4. 路由/窗口                    | 跨项目、跨 job/session/subscription/seq；旧响应/取消/重复 ID；权限撤销及切项目 generation；新 revision 丢旧订阅；I02 真集成后 renderer 崩溃/无响应/重建查询任务不重发写入、不取消后台                                                   |
| 5. 双端样例/错误全链路          | 同公共语料接受/拒绝完全一致；Python→主进程→窄 bridge→UI 保留 code/messageKey/params/retryable；UI 四段式、定位详情受限；不支持/失败/取消/过期区分                                                                                       |
| S1 承接                         | global operation_claims；严格已批准计划/confirmation 绑定；全部 job/marker/round 同库事务；实际依赖/定义集合变化与失效同事务；终态及 pin 幂等；先 pin 后报告/清理并发；跨项目边界与无外发权限提升                                       |
| U1 稳定分页                     | 真实不可变结果持久化、固定行键/范围/实现；游标服务端存储/权限/到期/篡改/载荷回收；列表固定快照；新增/终态变化不乱页；多字节大小与单行过大拒绝                                                                                           |

上述需 GUI 的验证仅在经核验隔离环境或用户明确可用时段执行；当前本机没有这样的授权。不能隐藏窗口或 stub 原生提示冒充完成。I03 外审仍须由本开发会话分别新建真实任务并记录来源/模型/思考/结束状态，不能用内审或文件存在替代。

## I05 内部语义适配器接口

总控于 2026-10-20 转交的接口需求仅作为内部设计输入：`parse_turtle(text, format=Turtle)`、`query(immutableGraph, SELECT|ASK)`、`reason(asserted+ontology, boundedRules)`、`check_shapes(assertedScope, namedTemplates)`。I05 固定真实库/外联拒绝/打包与许可证；I03 统一公开输入身份与结果/错误；I04 做 ExecutionJob、持久发布和取消接线。

适配器不得自行打开网络或发模型请求，不能把 graph 可变对象放到 DTO 或直接写 Store。解析/查询结果是独立载荷引用；解析成功不等于语义支持。reason 只做 RDFS 后一阶段受控规则，规则输出不再次触发规则或 RDFS；check_shapes 默认明确 asserted，若包含推导必须记录对应范围/实际依赖，不能默认扩展完整 SHACL。保留真实输入、engine/semantics/lock 三键版本与完整依据范围。内部固定错误须在服务边界映射到本版白名单，原异常和输入文本不越界；尚未登记的错误使用 INTERNAL_ERROR 并记录安全诊断码，不能直接开放任意 code。

## I05兼容核对后的补充验收

- errors目录新增有限semanticInput/semanticResult/semanticWork与十类unsupported分类，每类完整成功/非法参数/错误messageKey公共TS/Python反例；parameterMeanings与枚举精确对应，不借frame/page/actions归类语义预算。
- [语义边界](I05-semantic-boundaries.md)逐项保留历史30码并优先覆盖v3的25项细码/来源分支；被替换的INPUT_LIMIT/RESULT_LIMIT/LITERAL/RDF/scope合码不用于新分支；SHAPE_PATH_UNCLASSIFIED及来源未知只INTERNAL_ERROR安全兜底，不解析异常正文；不把私有码直接穿透。
- validationProjection严格分scope、实现与项目快照，validationResources关联角色/hash/真实reasoning结果/载荷/历史选择；TS/Python共同拒绝缺层、错项目/快照/实现/引用/结果种类、回收载荷和未选择历史。
- 真正的分层图读取/摘要/权限/历史选择和SHACL投影仍需I04/I05：独立固定C→Mid→Equipment与x类型用例，asserted不暗增目标，combined保留x派生类型及独立派生公理，核对完整目标/违规/依据和原断言不变。描述符或纯元数据测试不替代这项真实语义联验，不采用Q6最终路线。

## 候选5的审查修订验收

- 根 `npm run typecheck` 必须同时严格检查 contracts 源码、全部 `tests/unit/**/*.ts` 和 desktop；`npm run check` 及现有 CI 直接调用该入口。源码与单测分别临时注入实际类型错误时标准入口必须失败，恢复原字节后完整检查成功；不使用 any、忽略注释、弱化 strict 或排除新测试。
- TS/Python 动态穷举全部含枚举参数错误码的固定含义；错误预算直接来自 errors.json，临时缩小预算验证实际拒绝并恢复；版本与 registry/schema id 一致。通用模板键须与 schema/夹具配对，旧键有拒绝反例。
- canonical schema 限共同词汇，所有数组显式有限上界；未来演进先统一适配器的 fallback 再复审。
- E.2 的未处理事件摘要布局及 I04 必须实际验证的持久/分页/UI 条件以 jobs-and-storage.md 为准；成功至少一轮提交，零提交失败/取消仅显示状态。I03 只冻结设计，不把通用 row 可表达当成场景摘要已生成或可信绑定已验证。
