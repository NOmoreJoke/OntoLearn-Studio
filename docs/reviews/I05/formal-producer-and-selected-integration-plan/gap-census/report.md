# I05 / FR / profile 剩余验收事实清单

结论：**已收口的 finite7 私有计算、16c supplied-batch 复核、3ef strict 恢复都是真实有界成果；仍不足以关闭完整 I05/B1 或 FR-500–505。** 余项包含实际资源拒绝、尚未覆盖的数学输入、确实缺少的解释/消费接口、原输入未给出的规则或状态，以及真实生命周期/平台/发布门；不能统一归为“等 T01/native”。本文件只作下一集成方案的静态事实输入，没有授权实现或运行。

本 agent 为 `/root/formal_i05_gap_census`，仅写本目录。实际做文件/Git/stdlib JSON、ZIP、hash 和精确集合关联；未 import 产品、运行引擎/测试/probe/worker/包、调用网络/模型/GUI、切分支/提交或改任何旧产品/测试/资源/锁/指南/160 原件。旧运行结果均注明来源，不冒称本轮重跑。`census-static.py.raw` 可复核本清单，不含 matcher、数值比较器或第二 oracle。首静态帮助脚本误取 `headRefs` 的 KeyError 属归档 schema 使用错误，已读实际 `heads/headIndex` 修正；原产品/oracle 未变，见 `static-first-failure.json`。

## 1. 固定事实来源与范围

精确 bytes/SHA/Git blob 和读取范围见 `readonly-inputs.json`（33 个输入、5 个归档 member）。关键身份：

| 来源                    | 固定身份                                                                                                                         | 本次用途                                                                    |
| ----------------------- | -------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| 原 C4 七源              | `523c478d5f39671c4ac7c1ea6997e51d3047d58e`，七源与 `40c18ea1b9ce4fef9a5235718fd7e622e2d06cc4` 逐 diff 无变化                     | legacy finite6、真实 Session/worker/selected 链的有界已有能力               |
| 私有 finite7 计算/probe | `0475d0ec6c486a63c7e8f62f11f35181da6b2576`                                                                                       | 原83输入、实际30/31输出、现有解释字段                                       |
| 独立 oracle             | `f9af899fad31ea19c7540e9624c437a189b8b5bf`；fixture 767826B / `87220503f9983146c974fe3e35025d520cad70e54fdd994aebfa86fb1ff7259f` | 89图、40match、完整 head/basis 的独立期望；不得作为生产输入回填             |
| 当前 strict 产品/交付   | `3ef2f6952ed1a4f852da31c0bef7e8d8679752a5` / `4be2360aac0e6ea06211731364a14beec683310d`                                          | 有独立前提的 strict 恢复已闭环；无 formal authority/aggregate recomputation |
| T05 批量机制 API        | `16c58c6d0ca56491c7134c4866f9bed5e0f722c5`                                                                                       | 同 child 原 L 的三池 replay/saved encoding/issuance；不认证来源或全图完备   |
| T03 D2                  | 产品 `a4d1457fc6a1f1d1832296a8dcdb2ef42da75b98`，过程 `2a0cfdf87fc9c59bb111cb0add5c9e08d03f8af9`                                 | 旧0475固定计算83源/最终包相等的受限证据；不含新 strict/正式集成             |
| Q6                      | 根 `Q6-rule-comparison-decision.md` 已采用                                                                                       | 九域、六 numeric、语言/日期/失败及固定REC政策是已定要求；不重问Q6           |

原完整 I05 提示要求真实 Turtle、只读查询、RDFS/受控规则、SHACL；真实外联拒绝；源码和包同例；PyInstaller/资源/动态库/许可；S1 同口径至少两档测量；实际 Job/持久化/取消/错误/窗口联验；指定同版双审、CI 与正常 develop 合并。只收规则恢复子域并未覆盖这些全部任务。B1 原文位于主 checkout 的 `docs/architecture/m0-review-and-update-plan-2026-10-19.md:155–161`；本 strict 树该文件不存在，不以缺文件误判原要求消失。

## 2. 83 输入：实际状态与精确缺口

本次直接解码固定 `runtime-evidence.zip` 的 `30-final-probe.json`、`31-final-oracle-comparison.json` 和 `31-final-oracle-coverage.json`，按 caseId 做精确关联。完整83项、每项原 sourceRef/pointer/SHA、投影摘要、实际状态、映射图和 true/false 引用在 `actual-83-census.json`，另保留50 productCases、54 learningChecks 与106原操作引用的“未执行”事实。

- 实际 probe：78 success / 4 resource failure / 1 not-executed；进程 **exit1**，外部120秒监督未超时。
- 实际 checker：78 math-observable-fields-pass / 4 failure / 1 not-executed；**exit1**。未把“预期资源拒绝测试通过”改称该业务计算成功。
- 83条中4个 E.5 fragment 的 `fullOriginalInputContext=false`。repair 条目虽然元数据 `fullOriginalInputContext=true`，仍明示原规则缺失并禁止执行；这个布尔不是可信原上下文证明，也不能推翻其 not-executed。

| 精确 input ID                | 观察                                                                                        | 剩余事实/责任与必须避免的替代                                                                                                                                                                                 |
| ---------------------------- | ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `E.5:event-fragment:round:1` | `RESOURCE_LIMIT {resource:semanticInput}`；私有 `RULE_INPUT_BUDGET/resource`，ruleId=R-risk | 是真实资源/收费边界，非 native/T01 缺失导致。已有输入仅原 initial+event，非完整行为/资源状态；即使数学恰等两图也未成功。后续经批准对实际新候选记录原收费热点，不能加预算、删source或用expected补图取绿。      |
| `E.5:event-fragment:round:2` | 同 round1 的 input 资源拒绝                                                                 | 除实际资源失败，原事件累加片段缺前轮行为/工单/资源 RDF，**无精确完整 oracle 图同值**；须由实际 T06/T07 原轮次 supplier 形成真实状态。                                                                         |
| `E.5:event-fragment:round:3` | `RESOURCE_LIMIT {resource:semanticWork}`；`WORK_LIMIT/resource`，ruleId=None                | 图工作池真实失败，完整原轮次状态同时缺失；不能把它说成已知数值算法错误，也不能把安全拒绝当 E.5 成功。                                                                                                         |
| `E.5:event-fragment:round:4` | 同 round3 的 work 资源拒绝                                                                  | 同上；必须保原拒绝及全轮次原验收。                                                                                                                                                                            |
| `transfer:repair`            | `ORIGINAL_INPUT_CONTEXT_INCOMPLETE`，未执行                                                 | 原 `transfer-inputs.json:/repair` 没有 rule definitions；ruleVersion 不是继承 R-risk 的许可。原任务本质为实际 SHACL repair consumer。由原 T09/T05/T02 owner 明确原输入/修复操作，不造空规则成功或借别的规则。 |

这里尚未由“失败码”精确定位资源耗尽的单条 debit，不臆断某个唯一热点。现有合同已披露 source 重复编码、入口/child input 限额可能早拒；后续优化若改变源编码、预算/API或载体，须列原ref/delta/兼容和原L影响，交真正 owner 批准。保原池是约束，不能因此永久宣告 E.5 业务不必完成。

### 原文五项上下文缺失

| 原 ID / pointer                                      | 已给内容与缺失                              | 下一真实供给/验收                                                               |
| ---------------------------------------------------- | ------------------------------------------- | ------------------------------------------------------------------------------- |
| `ontology-model`，course `/tasks/0`                  | 课程只给四项新增，未给先前完整项目          | T02/原任务 owner 指定实际完整项目快照；四项数学增量可单列，但不称完整项目推理。 |
| `transfer-repair`，transfer `/repair`                | 无规则定义                                  | 原实际 SHACL 数据、shape、修复动作/版本；不得继承 R-risk。                      |
| `learning-report`，checks `/checks/learning-report`  | 未固定 RDF 输入项目                         | T10 实际输出及生命周期输入，报告结论绑定真实版本。                              |
| `G-list-13:edit-and-undo`，cases `/cases/33/steps/3` | 中间编辑 subject 未指定，无法构造完整中间图 | 原 owner 给真实被选对象/ChangeSet；undo 仍仅撤最后确认编辑，不以整库恢复替代。  |
| `G-list-05:late-V1`，cases `/cases/25`               | V1 完成轮次/完整 payload 未给               | 由实际 V1 job/worker产生旧结果；不能用 V2/current/expected反推 V1 历史。        |

这些缺口与授权/物理路径不同；单纯补 native 也不会补出原规则、实际行为状态或缺失的 V1。

## 3. 49/89 图、24/40 match：实际成功不等于计划映射

`31-final-oracle-coverage.json` 自身标 `actualResultsSupplied=false`、`actualMathCompared=false`：它是**精确输入值关联计划**，80 mapped inputs、79 eligible mapped inputs、51 eligible图、38未覆盖图，不能直接当运行覆盖。

将其与实际78成功相交，得到 **49成功图、40未覆盖图、24唯一match（15 accepted/9 false）、16个 `(match,headIndex)` 引用**。未成功覆盖的 match 恰 `e001`–`e016`，全属于 E.5；缺的不是另外16种比较算法。完整成功/未覆盖 ID 与所有关联见 JSON，分类无重叠且40项总和如下。

| 40项分组    | 精确图 ID / 规则                                                                                     | 性质及下一验收                                                                                                                      |
| ----------- | ---------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| 行为/提交 9 | B-01-behavior/commit、B-03-behavior/commit、B-07-behavior/commit、B06-commit、B10-commit、B11-commit | 原83数学生产输入未产生这些真实后状态；需要实际行为/提交结果，不能把同结论或同初态当同阶段。尚未证明引擎对这些给定完整状态算法失败。 |
| E.5 24      | `e5-c{3,4}-r{1,2,3,4}-{event,behavior,commit}`                                                       | 两个 r1-event 恰映 round1 但实际资源失败；其余22没有本次成功同值原输入。T06/T07真实轮次/容量/重放/恢复状态与I05资源问题须分别补齐。 |
| 取消 2      | cancel-committed、cancel-uncommitted                                                                 | 实际当前未提交轮回滚与已提交历史保留；纯图计算无法替代取消原子性。                                                                  |
| 导入 2      | imported、imported-user-edit                                                                         | 实际导入和人工编辑状态未由这83项生产；需要真实 Store/来源/ChangeSet链。                                                             |
| 课程增量 1  | ontology-model-delta-only                                                                            | 原课程四项新增的局部数学期望；不是原完整项目输入或真实执行声明。                                                                    |
| repair 2    | transfer-repair-before、transfer-repair-after                                                        | before有输入但原规则缺失禁止执行；after须真实修复消费者。不得由oracle倒填。                                                         |

所有89图都是“若对该数学图推理”的独立期望，不是89个真实 Job 已运行。概念阶段本身未请求推理时，不能制造额外成功Job来覆盖计数；新增覆盖必须来自原操作明确输入或经授权的独立数学样例，和实际生产生命周期覆盖分别记。

## 4. 旧 C4 与新 finite7：不能抹去旧成果，也不能跨版继承

### 4.1 旧 C4 的实际既有能力

根 `I05-controller-C4-source-string-repair-readback.md` 已完整读回固定原件1254成员、源码输入及多个平台调用。其十九任务 driver 使用 **Session(test_mode=False)、正常 coordinator/isolated worker、实际 semantic.start/job.get/result.get/result.page，并关闭重开 JobStore**，不是 fake finish。十组共190完整结果；新 source/mac包/Linux source/Linux包有完整 payload/rows/上下文/分页，旧finite5包实际完成调用后才产生17处语义不符。finite6 selected query/SHACL、current/historical和旧身份拒绝有真实有界证据。原件未包含可离线重开原DB的全SQL资源表，不能扩大为完整DB归档恢复证明。

C4 七源在40c/523逐 Git diff 无变化；其 `resources.py` 自报有限6/实际lock。指定最终双审和发布门未过，旧C4不得被本轮重新标正式通过；但也不得写成“现有项目从未有过真实 Job/Store/selected”。

### 4.2 实际代码差异与剩余能力

| 面            | C4 / 现legacy路径                                                                                               | 新finite7私有路径 / 仍缺                                                                                                                                |
| ------------- | --------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Rule IR       | 523 `semantic.py:209–213` 为 id/when/单 then；无比较字段、无多head组                                            | 当前 `quality.RuleSpec` 有 comparisons/heads；原T05九域值比较、多head原子，actual originalMatches/PreparedFiringBatch完整保存。                         |
| 闭包/join     | 单阶段有限RDFS+BGP，输出单head，不递归反馈                                                                      | 0475两语言模式复用唯一 `_finite_closure` / `_finite_matches`，没有第二matcher；profile额外计费和T05 compile/evaluate。finite7不是完整RDFS/OWL。         |
| 身份/格式     | C4 finite6，legacy结果严格5键                                                                                   | profile显式 finite7 / `i05-reasoning-result/2`，result含17键及typed native/PV/batch。默认resources当前仍i04基础身份；不能靠字符串换标获得producer权限。 |
| 规则请求/保存 | 当前 `semantic_execution._request:145–154` 仍要求 `{enabled,when,then}`，parameters仅inputSelection             | 缺原真实定义 supplier 对完整RuleSpec/comparisons/heads/policy/revision/digest/disabled的精确版本化映射和不可变快照身份；不能从结果反推IR。              |
| selected      | 当前 `semantic_scopes._selected_output:91–98` 只接受5键；`project_validation_scope`明确仅内部一致性，不认证来源 | strict 3ef只返children与有限fact，不重算聚合；缺正式finite7消费投影、原请求/Job/Store可信来源和全生命周期。不能删新字段塞回legacy五键。                 |
| 旧worker      | C4确有同版真实链证据，但原语义worker已冻结，维护权已交T01                                                       | 新集成只能向T01请求当前批准owner supplier；不能整棵复制C4、回收worker写权或造第二JobStore。                                                             |
| query/SHACL   | C4字符串term身份修复已有源码/包/真实selected证据                                                                | 未因此证明全部Q6消费者C格；各自规范语义仍独立，不能把规则comparator安装成SPARQL/SHACL语义。                                                             |

## 5. 数学与解释字段：四种不同缺口

### A. 已有并已观察的有限数学/载体

0475实际成功核完整 RDFS/custom/derived集合、warning、accepted firing bindings/有序when、comparison operand term/operator/boolean、全部 head index/occurrence/basis、原false/true binding/when/proof、完整定义/Catalog/child limits、来源occurrence、rows/payload和batch bytes hash。根读回证明24match/16head所对应范围。原新规则按稳定ruleId完整divmod分池，含disabled；custom不反馈RDFS/其他规则。3ef后真实跨exec又覆盖9domain/负零/SourceRecord长字段等，属于strict恢复成功，不补齐全部真实图九域与原83完整产品验收。

### B. 未覆盖观察，不能直接宣称算法缺陷

独立oracle `scopeBoundary` 明确 **18个comparison扩展格只有integer**。22扩展其余为 join/多输出/disabled/开放世界负例。原78成功并未完整覆盖：六numeric混型/直接binary32/64舍入与溢出/次正规/负零、字符串码点、语言标签/跨标签、IRI/布尔eq/ne、四date/dateTime域、false后错误及全部图source/预算边界。T05纯机制fixture/测试支持这些政策是另层证据；尚须真实图入口、query、SHACL各消费格与source/package同版数据。

oracle只提供operand词法/真值，不提供每个内部 Number/Calendar 值；原外部checker没有独立解码私有typed bytes语义。保全bytes及hash不是数值独立重算证据。此为观测/独立oracle覆盖缺口，不据此断言Number算错。

### C. 解释载体确实缺的字段，需最小真实供应变化

`_finite_closure:385–448` 每次推导实际知道 direct inputs，但当前仅 `proofs[result]=union(leaf proofs)`。`_profile_reason:1059–1072` 输出 rdfsEvidence 的 result/basis/proofLeaves，没有 direct-step/层次字段。现仅核唯一R04叶witness。FR-502/附录C要求相关公理和**直接输入事实**，不能把叶集合标成直接步骤。若当前叶basis对某样例已足够展示，只能如实展示其边界；对链式推导完整解释仍需在唯一计算时捕获真实直接边，配独立预期和预算，不事后重跑reason补解释。这属于解释载体/供应缺口，未发现或声称闭包数学错误。

`quality/rule_firing.py:426–433` 实际检查全部comparisons，先false不隐藏后错误；全部通过才返回 PreparedFiring。false match没有返回 ComparisonEvidence，originalMatches只保绑定/when/proof。因此原oracle只能核false无accepted firing/head。PRD要求结论完整依据链，并未逐字要求false ComparisonEvidence；缺false trace不能单独定为违反FR的算法漏洞。但若下一界面/验收承诺逐false比较解释，须T05 owner明确新增有限载体、位置、费用和消费者，不能伪造已有字段或从预期反填。

### D. 已有明确支持面缺口，不能只写“未跑”

当前 `semantic.py:1226–1239`：sh:datatype白名单没有rdf:langString；min/maxInclusive shape参数仅integer/int/decimal/float/double且not ill_typed，日期shape边界不支持。这是实际可达入口受限。原 `_terms:84–92` 对宿主ill_typed/未知datatype/非有限值有前门；新规则profile绕过legacy ill_typed路径并不自动令 query/SHACL 同样可达。

必须逐C格规定真实source/入口/consumer合同/错误：SHACL datatype按精确IRI与适用词法、maxCount/in按RDF term、范围按自己的SPARQL关系，正常false/type-error为validation结果；不能一律转规则E3任务失败，也不能让规则D3/D4替代query/SHACL的政策。日期/语言等扩展若属已采用范围，精确列最小源码变化/原hash/消费者/正负golden交owner；当前不因安全拒绝就关闭原FR-504，亦不在本轮擅改能力或代码。

## 6. 完整原I05/FR剩余验收矩阵

| 要求                         | 已有证据层                                                                | 尚缺的真实验收 / 精确方向                                                                                                                                                   | 不能替代它的证据                                               |
| ---------------------------- | ------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| B1真实库/外联/源码包一致     | C4有限6旧真实suite/stdio；T03 D2固定0475源/包211961节点深比且83同为78/4/1 | 新组合含strict/production supplier后，T03 owner重冻精确输入并做源/包同一Job样例/资源/插件/许可/动态链接；实际可达parser/validator/query外联负例继续                         | 旧health、仅probe包、无网络配置声明、旧包过不等新包            |
| FR-203/C Turtle能力/安全保留 | 私有解析器/支持构造和字符串保真有真实旧证据                               | 与实际导入/预览/Store提交/导出同版闭环，unsupported拒绝保持原文件/项目；九域source词法不由宿主改写                                                                          | 仅parse成功，或从N3逆推原文/span                               |
| FR-400–404 查询消费者        | C4有限只读/selected query、T04父接口另行负责                              | 原真实query定义/输入范围/current-vs-history/可见SPARQL/完整结果空集/分页/保存与版本；query自己的日期/数值C格                                                                | 规则比较全绿或Graph数学同值                                    |
| FR-500检查入口与范围         | 旧semantic纯服务/错误边界                                                 | T05实际一键入口聚合语法/SHACL/规则/新知识，明确snapshot/scope/constraint版本、unsupported/未执行，完整报告                                                                  | 2873普通测试或一个RESOURCE_LIMIT断言                           |
| FR-501组合语义/撤回          | 0475有限算法，R01/04/05/06数学值子范围                                    | 真实Job成功计算→保存后当前/过期/撤回；R02删除唯一依据撤回且不删断言，R03另一依据保留，R05规则链提示，R06保存顺序无关，含真实编辑/启停                                       | 原初始图的同值期望或只核结论数                                 |
| FR-502解释                   | accepted多head/完整basis、原source、R04叶witness                          | 真实直接RDFS输入/公理可定位；全真实图九域/完整解释独立oracle；T08只能翻译实际trace                                                                                          | 叶basis当直接层次、hash当数值证明、伪false trace               |
| FR-503分级与定位             | 原finite细码→安全DTO适配                                                  | 真正source/定义/shape/规则位置绑定当前授权与版本，三类问题在真实界面可点定位，不泄原值/路径/stack                                                                           | 受控测试location或任意caller自报source                         |
| FR-504约束编辑/测试          | 旧五模板、有限pySHACL，C4某selected报告真实                               | 真实owner保存版本化shape、双scope、不合格/修复对象及完整报告；明确上述日期/langString/C格补齐                                                                               | 把规则profile比较当SHACL range/datatype                        |
| FR-505规则编辑/测试          | finite7比较/多headmechanism+真实图有限子集                                | 实际版本化规则supplier和UI启停/完整条件heads/独立expected/actual/error，零match常量先验、false后错、头组失败原子、全九域/混型/预算                                          | 18个integer比较格、外部expected直接给matcher                   |
| FR-006/D、10.3恢复           | C4旧finite6真实Job/history；3ef纯函数失败清理/终态                        | 原正式Job/project/snapshot/vector/definitions/parameters/source/implementation/L绑定、唯一Store原子成功、失败/取消/late/重开/retired/GC/window权限，历史不可回收            | 新ledger、测试monkeypatch捕获、caller boolean formal authority |
| 附录E/G行为/沙盘数学         | T05 89图独立期望含E5/40match                                              | T06/T07实际轮次/event/behavior/resource/commit状态作为真实输入，补4资源失败与e001–e016；取消/回放/resume/reset                                                              | 事件累加片段、expected补全状态、自动加budget                   |
| 10.2容量/测量                | B1旧观测、D2当前主机包；120秒一次未超时                                   | 保S1两档真实数量/种子/查询hash/冷暖/设备/峰值和失败；Q5目标按既有决策表，未来组合资源/缓存账本另验                                                                          | 抽象R票据=RSS/CPU、一次5秒=最坏上界                            |
| 10–12/平台/真人/发布         | 部分host CLI/旧隔离Linuxnative、固定macOS27 unsigned arm64 D2             | 目标macOS15/Windows、签名安装/无系统Python/断网干净设备、实际窗口/取消恢复、真实新用户12.1/12.2/可信回答，指定GLM-5.3最高+M3.1-Flash xhigh同版新审、CI/正常develop合并/远端 | macOS27开发包或Linux替代目标双OS、内部两agent替指定模型        |

以上是I05参与的整体要求交叉引用，不擅自拿T05/T04/T06/T01等唯一owner源码写权；具体供应请求由主方案逐路径交根。外部平台/签名/真人与内部真实临时JobStore3/owned worker链分层，前者未到不能永久冻结后者；反之内部链过也不能登记正式生产入口/父功能全完成。
