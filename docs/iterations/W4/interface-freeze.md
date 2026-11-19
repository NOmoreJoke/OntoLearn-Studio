# Wave 4 Stage 0 接口冻结

本次交付 T03 映射、T06 行为、T07 沙盘与 T10 项目包和 HTML 报告的 DTO、双端校验和命名桥接。参数和结果受 business3 的 256 KiB 帧限制及协商限制约束。项目标识由主进程从当前打开的项目注入。所有选取、预览、准备、运行和操作标识均绑定来源项目，宿主负责在使用时检查选区、会话、版本和持久化状态。

## 通道与权限

| Desktop IPC 通道                        | DesktopBridge 方法          | business3 方法                                                                      |
| --------------------------------------- | --------------------------- | ----------------------------------------------------------------------------------- |
| `project:mapping-source-select`         | `selectMappingSource`       | `project.mapping.source.select`                                                     |
| `project:mapping-preview`               | `previewMapping`            | `project.mapping.preview`                                                           |
| `project:mapping-prepare-commit`        | `prepareMappingCommit`      | `project.mapping.prepare`                                                           |
| `project:mapping-draft-read`            | `readMappingDraft`          | `project.mapping.draft.read`                                                        |
| `project:mapping-draft-save`            | `saveMappingDraft`          | `project.mapping.draft.save`                                                        |
| `project:behavior-run`                  | `runBehaviorSample`         | `project.behavior.run`                                                              |
| `project:behavior-read`                 | `readBehaviorRun`           | `project.behavior.read`                                                             |
| `project:behavior-cancel`               | `cancelBehaviorRun`         | `project.behavior.cancel`                                                           |
| `project:scenario-create`               | `createScenario`            | `project.scenario.create`                                                           |
| `project:scenario-copy`                 | `copyScenario`              | `project.scenario.copy`                                                             |
| `project:scenario-list`                 | `listScenarios`             | `project.scenario.list`                                                             |
| `project:scenario-read`                 | `readScenario`              | `project.scenario.read`                                                             |
| `project:scenario-run-read`             | `readScenarioRun`           | `project.scenario.run.read`                                                         |
| `project:scenario-run`                  | `startScenarioRun`          | `project.scenario.run`                                                              |
| `project:scenario-cancel`               | `cancelScenarioRun`         | `project.scenario.cancel`                                                           |
| `project:scenario-resume`               | `resumeScenarioRun`         | `project.scenario.resume`                                                           |
| `project:scenario-compare`              | `compareScenarioRuns`       | `project.scenario.compare`                                                          |
| `project:scenario-run-delete`           | `deleteScenarioRun`         | `project.scenario.run.delete`                                                       |
| `project:scenario-restore`              | `restoreScenarioBaseline`   | `project.scenario.restore`                                                          |
| `project:transfer-package-export-check` | `checkProjectPackageExport` | `project.transfer.package.export.check`                                             |
| `project:transfer-package-export`       | `exportProjectPackage`      | `project.transfer.package.export`                                                   |
| `project:transfer-package-import-check` | `checkProjectPackageImport` | `project.transfer.package.import.check`                                             |
| `project:transfer-package-import`       | `importProjectPackage`      | `project.transfer.package.import`                                                   |
| `project:transfer-report-prepare`       | `prepareProjectHtmlReport`  | `project.transfer.report.prepare`                                                   |
| `project:transfer-report-export`        | `exportProjectHtmlReport`   | `project.transfer.report.export`                                                    |
| `project:transfer-select`               | `selectTransferFile`        | 主进程文件选取，无 Python 通道                                                      |
| —                                       | —                           | `project.run.before_commit`（`main-process-only`，由 `recordRunBeforeCommit` 调用） |
| —                                       | —                           | `project.agent.before_commit`（既有 `main-process-only`）                           |

新命名入口沿用可信文档检查、库切换拒绝、主进程信封和收件确认。项目管理或恢复挂起时，映射和行为读回、场景列表、详情及运行比较可读。文件选择、准备操作、请求写入、运行、取消、续跑、导入、导出和删除继续按阻断状态返回 `PERMISSION_DENIED`。所有 IPC 接收一个严格对象，主进程在引擎调用前校验请求，并在返回后复核所选项目和会话。现有 12 个 `model:*` 通道继续由原有注册表管理。

`project.run.before_commit` 入参为 `projectId`、`operationId`、`domain`（`behavior | scenario`）、`baseRevision` 和可空 `label`。仅授予主进程登记快照的权限。收据含 `runBeforeCommitVersion: 1`、原项目与操作标识、`checkpointRef`、`reason: 'before-run'` 及等于基准版本的 `domainRevision`。Stage 1 在实际隔离运行进入执行前持久化，重复操作以相同绑定对账。公开 `project.checkpoint.create` 仍仅请求手动快照，原因由引擎铸造为 `manual`。

Stage 0 文件选取存根验证参数及当前项目后返回 `UNSUPPORTED_CAPABILITY`。其它新通道将同一固定契约交给选中项目的 business3 传输层。

## T03 映射

- 初次选取由主进程原生对话框发起。回执给出不透明 `selectionId`、SHA-256 指纹、`csv | xlsx`、工作表列表、当前工作表、字段名、类型和样本。离线映射建议可给出精确字段名匹配依据、候选谓词和少量实际样本。已有选取可通过同一桥指定工作表和编码重新解析。CSV 工作表标识为 `CSV`，编码为 `utf-8 | gb18030 | big5 | utf-16`，其中 UTF-8 BOM 由解析层识别。XLSX 编码为 `null`。Stage 1 由可信宿主向引擎提供选取对应的输入，renderer 只持有令牌。
- `MappingDraft` 使用版本化身份、命名空间、类 IRI、字符串业务键和字段转换，保留空值策略、前导零和关联目标。草稿保存以 `expectedGeneration` 对账，读回返回版本和草稿。业务映射规格随确认的 ChangeSet 提交。
- 预览输入为 `selectionId`、`sheet`、`encoding`、`draft` 和可选 `page`。返回基准版本、指纹、`resultId`、样本偏移、行总数、身份增删及 RDF 变化。问题定位含 `sheet/row/column/field`，代码经固定 `messageKey` 投影。冲突保留 `code/current/source/managed/owner/sourceRow/subject/predicate`，足以携带 FR-304 来源追踪与冲突证据。冲突解决交互归后续批次。
- 提交准备以预览、选取、指纹、基准版本和操作 ID 复验。返回 `MainlineChangePlanDTO` 的 `mappingPreparation` 分支，含 `resultId` 和 `preparationRef`。引擎在既有 `project:changeset-preview → project:changeset-diff-page → project:changeset-confirm → project:changeset-commit` 中解析受信计划并原子写入映射、事实和来源关系。准备引用与手工事实计划互斥。Stage 0 主进程在解析器接通前显式拒绝该分支。Stage 1 对照输入、草稿、源行、所有权和项目版本校验幂等重跑，发现冲突或旧预览即拒绝。

## T06 行为与 R7 适配

| 项               | 冻结转换与拒绝规则                                                                                                                                                                                                                                                                                                                                  |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 触发器         | UI `trigger` 是完整事件类型，映射为 `{eventType, eventId?}`，再转为 planner 的 `event_type/event_id`。空值、未知类型或未经绑定的事件 ID 拒绝。                                                                                                                                                                                                      |
| 2 条件           | 一组 AND 且至少一项。`always` 显式保留。精确 `equals` 与 `has` 在保留字面量类型后映射为 `has`。B-01/B-02 的类型判断映射为冻结推理快照中的 `rdf:type` 类断言，属性条件匹配同一快照中的确切值。不可证明是相同断言语义时拒绝。`exists` 需要无值通配，当前 planner 返回 `unavailable`。                                                                 |
| 3 动作名称和基数 | UI 的 `update` 映射为 `set`，仅单值覆盖。`relate` 映射为 `add`，仅声明为多值的关系。基数以实际快照 schema 为准。`notify` 只产生隔离通知记录。                                                                                                                                                                                                       |
| 4 动作字段       | `object` 在 set/add 中转为 `subject`，`target` 转为 IRI 值。`create.classId` 降为有目录支持的 `initial` 类型断言，planner 仅接收 `object`、可选 `initial`。已有类型初始化与 classId 冲突时拒绝。通知保留受限 `message` 和可选 ID。                                                                                                                  |
| 5 事件与编辑     | `id/type/sequence/version/payload/edits` 全显式。UI input 顺序与宿主事件版本绑定，版本降为 planner 文本。把 UI changes 的 object 转为 subject，按 add/remove/set 降低。create、declare、delete_object 使用 object。原始 payload 自有键 `__proto__`、`constructor`、`prototype` 使整条事件被拒绝。相同事件 ID 的重送按同一语义指纹幂等，异内容冲突。 |
| 6 请求外壳       | `sample`、原 `runId/operationId`、`binding`（项目、项目版本、快照、行为版本、隔离副本和请求 ID）、draft、events。宿主补入真实的单轮标识、类和属性目录、状态、断言/本体/规则版本、推理与消费账本。禁止虚构输入版本或推导。数字版本仅作无损十进制文本转换。                                                                                           |
| 7 Diff           | 私有 `[object,id]`、`[fact,{subject,property,value}]`、`[notification,record]` 拆为 `kind` 标记对象。保留对象和通知差异，UI 可单独呈现；事实的 subject 映射为 UI object。值类型依实际属性目录恢复。                                                                                                                                                 |
| 8 生命周期       | `candidate/false` 为尚待提交的候选。`completed/true` 只来自已确认的隔离副本提交。`failed/false` 与 `cancelled/false` 仅允许未提交轨迹和空提交 Diff；四种状态约束动作与通知状态。                                                                                                                                                                    |
| 9 新鲜度         | `current                                                                                                                                                                                                                                                                                                                                            | stale | historical` 源自真实快照/版本/副本校验。`stale`强制返回固定`staleReason`；历史记录只读。公开条件和动作轨迹按白名单枚举投影。 |
| 10 取消与刷新    | `read` 以原始 binding 和 runId 对账，避免重复投递事件。`cancel` 仅在持久化终态确认后返回 `cancelled`，仍绑定原操作、运行和请求；未确认使用固定安全错误。                                                                                                                                                                                            |
| 11 错误          | `conflict → behavior.conflict`、`invalid_input → behavior.invalidInput`、`unavailable → behavior.unavailable`、`execution_failed → behavior.executionFailed`、`cancel_failed → behavior.cancelFailed`。禁止跨界传送 `BehaviorError.evidence`、原始异常、路径、堆栈和私有诊断。通知内容属于受限业务投影，作为纯文本呈现。                            |

`BehaviorAdapterContract.lowerCondition` 仅冻结语言转换。调用方须以真实冻结快照的类型目录判断 `rdf:type` 可用性，并将表达式转换为私有 planner 的标量或单键表达式。类型、数值、关系、模板、命令字段或基数不可无损表达时失败。重复事件消费、私有 planner 运行、commit 和结果呈现由 Stage 1 接入。

## T07 沙盘

- 创建绑定 `projectVersion` 和 `inputSnapshotId`。配置包含固定轮数、直接/人数乘人均产能、隔离初始编辑、有序事件、规则与行为版本、参数、数据来源和假设。复制绑定原场景和基准，由宿主发行新场景 ID。列表以游标分页，运行详情以已提交轮次分页。
- 运行以操作 ID、运行 ID、场景 ID、版本和快照对账，Host 先登记真实 `before-run` 收据。行为样本和沙盘共用 `IsolatedRunScope` 的判别域。场景运行仅可写隔离副本，按附录 E 固定顺序与原子轮次边界执行。回执保留引擎版本、依赖锁摘要、配置摘要、输入版本、规则和行为版本及重放标记。
- 取消保留已提交轮次。显式续跑通过原运行和检查点引用复核配置、输入和事件消费，创建新的运行身份并记录来源，禁止隐式续跑或盲重放。恢复仅将隔离场景回到选定基准，运行删除使用受限生命周期入口。
- 比较选取 2–10 个同项目的成功运行，可跨场景，结果保留各自版本与每轮指标。固定指标为积压、已完成工单和未关闭高危告警；保留未处理事件。随机实验、历史预测、复杂离散事件模型及平均等待时间属于后续范围。

## T10 项目包与 HTML 报告

- 正式清单 `ontolearn-project-package-v1` 版本栏为 `dbFormatVersion`、`checkpointSchemaVersion`、`applicationStateVersion`、`minReaderVersion`、`minWriterVersion`。`full` 必须有 `definitions/assertions/ownership/checkpoint`；`template` 至少有 definitions，且不宣称恢复当前项目。发出检查回执前以实际归档和版本检查证明恢复、映射重跑、场景重放各自的前提。
- 可选项 `agentSessions/rawSources/derived/history` 默认全关，对应唯一角色 `agent-session/raw-source/derived/history`。选项关时角色必须缺席。每角色与路径唯一，清单仅可移植相对路径、安全成员和 SHA-256，禁止 `vault/credentials/audit/authorization`。Stage 1 在实际归档层校验成员与清单吻合。
- 导出检查与执行绑定所选目标、检查引用和操作；导入检查返回明确版本或包类型拒绝，兼容时返回原包指纹和检查引用。导入执行重新校验其指纹，分配新的项目 ID。冻结冲突策略版本、拒绝所有权冲突和策略指纹，保证同格式、同输入和同版本在设备间行为一致。
- 文件选取仅交给主进程真实对话框，按用途发行 `.html` 或 `.ontolearn.zip` 的 `selectionId`，与项目、会话和读写方向绑定。报告采用 `ontolearn-report-v1` 的受限投影，含目标、问题、学习、本体、数据、查询、验证、行为、场景对比、假设与待解决事项。结果保留实际版本和过期信息。Markdown 属后续范围。
- 报告独立迁移成功需要迁移任务实际完成、持久化通过证据以及零提示和零 Agent 协助。完整示范、部分提示、Agent 代做或仅界面执行完成均不能计入。报告准备后返回 `prepared` 和 `reportRef`。写入确认后返回 `published` 和耐久性状态。文件可能已落盘但无法核实身份时返回 `publication-unconfirmed`，保留指纹与清理状态，先对账再决定是否重试。取消和失败单独投影。
- FR-901 的自由文本规则同时覆盖报告和项目包可选业务数据。Stage 1 在生成字节前逐项扫描输出投影，尤其是标题、说明、目标、结果摘要、导入值和 Agent 文本。只允许凭据扫描为 `clear` 或完成遮蔽且复检通过的 `redacted`。其余使用固定 `PERMISSION_DENIED`，不得生成或交付包/报告，不在错误或日志复述凭据。写文件前重新验证实际投影。HTML 使用现有 CSP，动态值只作为安全编码的纯文本，保持离线可读。

## 双端一致性与 Stage 2

TS 与 Python 共读 18 关键字子集的 schema，校验会话、项目、操作、快照和域引用。协商允许至多 96 个 business3 方法标识，v2 与 mainRuntime 表维持原口径。对最终格式化的 `registry.json` 原始字节计算 SHA-256，同步业务握手、启动诊断、绑定夹具的正向/预期摘要。原始字节夹具重算 UTF-8、Base64 与原分块，保留长度、转义数、CRLF 以及故意使用的错误哈希。

`mapping.commit`、`behavior.test`、`scenario.run` 在 Stage 0 仍为 `design-only`。Stage 2 在真实引擎持久化、主进程真实选取和 Agent 端口、renderer 以及相应真实联验全部闭环后，才可由集成负责人激活并重新同步注册表摘要。

## Stage 1 独占写面

| 切片                               | 独占路径                                                                                                                                                                                                                                            |
| ---------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| W4-A · ZCode Engine                | `packages/engine/src/ontolearn_engine/project/**`、`mapping/**`、`behavior/**`、`scenario/**`、`transfer/**` 及引擎协调器、worker、job store；`packages/engine/tests/test_w4_*.py`；需更新预期时由总控协调的 `content/learning/checks.json`。       |
| W4-B · Codex Main / Agent / Picker | `apps/desktop/src/main/{index.ts,desktop-ipc.ts,project-mainline-service.ts}`、`apps/desktop/src/main/{agent,project-transfer}/**`、排除根目录核对所需的 `apps/desktop/src/main/model-gateway/**`、`tests/unit/w4-main-*.test.ts`。                 |
| W4-C · Renderer 四工作台           | `apps/desktop/src/renderer/src/{mapping,behavior,scenario,transfer,learning}/**`、`apps/desktop/src/renderer/src/App.tsx`、`apps/desktop/src/renderer/src/agent/context-actions.ts`、`tests/unit/w4-renderer-*.test.ts`、`tests/e2e/w4-*.spec.ts`。 |

共享 contracts、preload、Stage 0 回归单测与注册表由冻结 owner 保管。Stage 1 遇到契约缺口先交总控裁决。各切片用自己的测试命名空间，集成由 Stage 2 串行处理。
