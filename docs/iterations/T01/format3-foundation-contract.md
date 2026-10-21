# 格式3基础：T01 最小内部合同与验收设计

状态：待 T00 合同统一和独立挑战的具体设计；未启用 metadata、未迁移数据库、未注册协议3。T01 为单一基础候选集成人，现有写权仍只有 storage.py、project 私有包及专用测试/文档。依据总控 T00-project-format-version-proposal.md、T00-project-format-version-review.md（含第8节依赖澄清）。当前域服务实际状态见 [status](../../reviews/T01/status.md)。

## 1. 最小基础候选与文件请求

基础是一个不可拆开的最终候选：Store3 迁移/应用CAS/操作证据/checkpoint，JobStore ready/claim 适配，canonical业务3及两端绑定，coordinator/main真实握手。可以先做私有探针，但不能把会使旧 Project 结果非法的中间态当可用产品。采用批准5f接口，不消费未批准语义或网关；不以 I05/I06 整项完成为固有前置。实际 develop 变更仍刷新基线、完整联验和双方新审。

现阶段最小确需协作路径：

1. `storage.py`、`project/`、`test_project_*`：T01 已获写权。
2. `job_store.py`：请求其唯一 owner 明确 ready 层级、非 worker 应用CAS入口、全局 operation claim 和 receipt/confirmation。代实施或有界移交均可，不复制 JOB_SCHEMA。
3. canonical `{schema,registry,errors,fixtures,binding-regressions}.json` 和 TS `{index,v2}.ts`：同一份资源演进，明确 bootstrap/业务版本和如实格式，不复制第二协议目录。
4. `coordinator.py`、`main/engine.ts`：实际协商、通知版本、session/registry绑定及 ready；Python validator/resources 先验证同源能力，确需源码改动再逐文件交接。
5. 新命名应用入口若实际需经过 task-service/main/preload，逐路径给准确 diff 再交接；本设计不自授其余 UI、worker、protocol、build/锁/CI 或既有测试。

## 2. Store3 层和 Job ready 层

选择两阶段安全边界，避免 storage 反向导入或复制 JobStore：

- Store3 取得受控迁移入口后原子验证/建立本层所有必需结构，最后写 user_version=3。当前格式3打开只读验证结构和子版本，不用 IF NOT EXISTS 修补损坏。
- JobStore 在同 writer lease 下初始化/验证自己的结构并对账原任务；两层成功后才授予新 engine session/ready。Job 层失败即关闭实例和租约，保留有效但未 ready 的 Store3，重开显式幂等恢复，不降版本、不伪称应用可用。
- 迁移入口先停止接纳、收尾/对账旧任务、fence worker、关闭自有旧连接，再交同 lease。PRAGMA 升3不能让已打开的任意外部连接自动失效。旧 raw SQLite 并行访问不受支持，也不拿这个边界掩盖自有连接漏关。
- 新建/迁移格式3不伪造旧 metadata/学习历史。缺旧证据记 not-recorded，仅拒绝相应恢复，不一概拒绝合法旧库。旧快照/marker/运行输入原字节保留。

## 3. 版本、CAS 与唯一事务

| 状态                      | 并发身份                                                   | 持久化/失效规则                                                                |
| ------------------------- | ---------------------------------------------------------- | ------------------------------------------------------------------------------ |
| 正式域定义/事实           | 既有 projectRevision、dependencyVector、domainSnapshotRef  | 域变化仍原子推进并按既有规则失效；原hash域不加项目名/草稿                      |
| 项目名/模板/归档/显示模式 | metadataVersion CAS                                        | 应用-only 保存不推进域 revision/vector/hash，不使领域结果无意义过期            |
| 编辑草稿                  | 每 editor 的 generation CAS、boundDomainRevision、内容摘要 | 自动保存是受信本地应用操作；旧generation拒绝，不额外弹每次人类Diff或启动worker |
| 学习尝试当前视图          | 每 attempt 的 recordVersion CAS                            | 绑定任务/课程/输入/真实工具证据，不能靠客户端自报独立完成                      |
| attempt 辅助事件          | 同项目不可变事件身份/顺序                                  | 追加保存，不被checkpoint恢复抹除；每次尝试独立评价                             |
| 全项目操作                | 同项目 operationSequence，既有全局 operation claim         | 域-only、应用-only、组合提交都占一序号；domainRevision相同也不能漏历史         |

所有更改仍由 Store.commit 同一 SQLite 事务执行。受信应用服务在同外层事务取得/核验 operation claim，校验项目/来源/actor/必要确认，把完整 plan/CAS/输入/确认身份绑定指纹；Store 负责状态、序号、checkpoint和receipt原子落盘。普通自动草稿不生成Agent强确认，Agent正式写入和整个checkpoint恢复保留明确人类确认。没有worker的应用保存仍有claim/receipt，不假造Job终态。

旧 commits/commit_evidence 保持不可变历史证据；新操作索引按 operation 引用旧 marker 和新增 receipt，不再建第二份可变幂等权威。全局claim由原受信入口协调，内部Store裸探针不冒充生产授权。组合域+应用成功/失败同一事务；同operation换草稿/目标/CAS/确认要拒绝，响应丢失只按同claim/receipt对账。

新全项目 operation.list 固定 throughSequence，包含真实域与应用操作；当前 stage2 的 throughRevision 仅域历史，继续保留准确命名和范围。合法旧库缺历史时索引只登记实际已知操作并标 legacy-partial，不编造不存在的提交；迁移 genesis checkpoint 只证明迁移时已知现态。

## 4. checkpoint1 与恢复

独立不可变 checkpoint envelope：类型/版本1、databaseFormat3、项目身份、domainSnapshotRef/domainRevision、operationSequence、metadata/draft/学习当前视图及其CAS、完整coverage和内容摘要。它不是旧domain snapshot或round evidence；加载先校验类型/精确形状/coverage/同项目/真实操作来源，再验hash。checkpoint载荷仍在同SQLite，不是第二权威。

完整恢复预览同时绑定域base、应用CAS、throughSequence、详细Diff及覆盖操作清单。确认后任何一侧变化均重新预览；当前脏稿generation也复验，不能让旧restore回调隐式覆盖用户新输入。恢复是新operationSequence，所有CAS向前，不把历史CAS回拨成可重用的旧代次；domain只有实际内容变化才推进。旧域快照缺应用coverage不能称完整恢复，可保留另一明确有限域恢复入口和单独范围确认。

学习当前视图可以恢复，但不可删除/修改真实attempt及辅助事件；重新评估原attempt必须读取其全部辅助记录，不能恢复前进度洗掉完整代做。真正新attempt使用新身份和自己的输入/辅助证据，不能因过去另一次看过示范永久判失败。模型密钥、私有vault/网关审计、端点凭据及发送授权不进入项目checkpoint/包。

## 5. 业务3握手的建议精确帧

这是一份给 canonical owner 的单一草案，未创建另一个协议实现。

- request：既有严格 bootstrap 外层 `protocolVersion=2, method=hello, engineSessionId=null`，params 为 `supportedVersions=[3], clientId=有效UUID`。
- hello 成功：bootstrap响应外层仍2，原请求 id/method，外层 engineSessionId 与 result.engineSessionId 同为新UUID；result.selectedVersion=3、registryHash=本构建真实同源hash，其余 engineVersion/capabilities/limits 沿现有严格形状。ready前不得成功。
- 后续 request/response/notification 一律 protocolVersion=3，session必须精确匹配该hello。Project.formatVersion如实为3，域字段含义保持，不把metadata明细偷偷加进旧strict对象。
- 无交集：bootstrap响应2、method=hello、同pending id、engineSessionId=null、固定 VERSION_INCOMPATIBLE/supportedVersions=[3]；不授予session、不开放业务。新端可识别旧端返回支持[2]仅用于安全终止，不降级。
- null-session错误只匹配未完成的bootstrap hello及其明确错误分支；后续业务、通知或不存在pending的响应绝不能用null通配。重复hello、旧session、错误外层版本、假registryHash按同源规则拒绝并清理pending。

需要实际改变 TS matchesResponse 的 hello版本绑定、coordinator 和 main/engine 的协商/发送/通知版本；不能只改schema常量。旧端与新端四种App/engine组合逐一给成功或安全拒绝，不吞字段、不在不兼容时降级写库。

## 6. 基础验收 fixture 设计

每项需固定 source/canonical/输入/预期hash，比较完整结构/数据/版本/控制/操作证据，保存首跑失败。不以此表存在计通过。

| ID    | 固定输入与完整预期                                                                                                                                             |
| ----- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| F3-01 | 空白3和合法0/1/2迁移；Store必需表/约束/版本/来源标记全齐；旧事实ID/owner/人工漂移/墓碑、mapping语义和所有旧payload/hash不变                                    |
| F3-02 | 每DDL/回填/格式门的异常和真进程退出；Store commit前完整旧库，commit后完整Store3；Job第二阶段失败不得ready，重开幂等，不降版本                                  |
| F3-03 | 旧JobStore持lease时升级不得开始；收尾fence/连接排空后新实例取得相同lease；固定5f旧Store重新开3安全拒绝，未知4/缺结构3拒绝不修补                                |
| F3-04 | 同domain revision下先改名、后自动草稿、再组合域修改；CAS/sequence连续、每操作可对账；前两次domainSnapshotRef/vector/current原样，组合域失效准确                |
| F3-05 | 两连接以相同metadata/draft CAS保存，只有一个成功；旧保存响应/旧结果回调/旧restore回调不得覆盖新草稿；重复operation同计划返回原receipt、异计划拒绝              |
| F3-06 | 只有应用操作也进入throughSequence列表，翻页中追加不污染固定上界；旧已知历史和legacy-partial不伪造缺项                                                          |
| F3-07 | checkpoint完整metadata/draft/学习当前视图+域；坏hash/伪造来源/错项目/round冒充/缺coverage拒绝；restore确认列表及任一CAS变化拒绝且无部分提交                    |
| F3-08 | attempt-A完整示范后恢复旧当前视图，A仍不得计独立成功；新attempt-B新输入无代做可以独立评价；旧辅助事件/工具依据原字节保留                                       |
| F3-09 | 精确hello成功/无交集帧、ready前失败、同chunk假hash、错误selectedVersion/session/null-session/旧会话/重复hello；TS/Python同判，原sender/frame/project绑定不弱化 |
| F3-10 | 同一真实打包引擎运行迁移/CAS/checkpoint/握手样例与源码一致；不自动启动本机Electron。Windows/macOS和最终项目包/真人验收仍各有发布门                             |

本地仅无窗口单测/静态/构建；真实桌面/凭据和指定审查应用由总控预约。基础候选全体最终同版双新审、CI、正常PR/合并和远端核验不减少。
