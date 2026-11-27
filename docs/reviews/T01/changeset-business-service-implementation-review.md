# T01 正式 ChangeSet 服务实施与验证

本阶段按根授权 `421f974c43975886d280386316b34b5f1e284712d68d38f338d8083beb217467` 和固定计划 `39ebbf378386004eb9e8654bf9dbd7465e50d5215a87c55fde01cffc258d71e1` 实施。当前父功能状态统一见 [status](status.md)；完整范围保留 [44 项验收地图](../../iterations/T01/full-function-acceptance-map.md)。本报告记录本阶段实际交付，不改写旧计划的历史待审文字。

## 实际变化

在显式内部 business3 中增加 `changeset.preview`、`changeset.diff.page`、`changeset.confirm`，将既有 `changeset.commit` 接成真实确定性 Job。输入限于 Store 可验证且可逆的人工 asserted RDF 和 ontology triples/singleValuedPredicates/references；拒绝触及旧 opaque 值。预览调用真实 Store 回滚演练，冻结完整 before/after/control，分别核 preview identity、prepared ref、Store marker 与 Job context 四种 hash。

完整 Diff/undo-impact 按 canonical UTF-8 bytes 分段，base64 传输。raw 总限 16MiB、每段 32768B、最多 512 段；blob、manifest、page 和 frame 各按实际编码校验。TS 共享重组器一次有界捕获必要 data-only 字段，逐段及整值核 offset/长度/hash/UTF-8/JSON；真实 Node 监督器测试使用该函数后请求确认。限制是工程保护，不是 Q5、RSS 或性能证明；任意敌对 Proxy 隔离不属于此进程内 data-only 合同。

首次确认核完整、活跃分页链及当前基线/控制/结构/引用/ownership，真实 hello clientId/engineSessionId 绑定至原 prepared。confirmation 与严格版本化原请求回执同事务持久化；同 host/Session 的精确请求先返回原回执，cursor TTL/GC、RPC id 改变或后续版本推进不造成重签。新 Session/新 operation 不得接管旧确认；原已 claim operation 按完整持久 context 对账，跨重开返回原 Job 并保原归因。

受理事务保存 claim+queued；提交事务经唯一 Store writer 原子保存 domain/marker/sequence/checkpoint/receipt/result+succeeded。正式分支不运行 test worker。提交闸前实际让普通 dispatcher 有机会受理取消，只有已持久 cancelling 才胜出；同步 SQLite 事务途中不能承诺接纳新取消。受控 scheduler 测试验证这一机制，明确不是自然 OS 到达时序。提交后异常或迟到取消按持久终态返回，不能覆写已成功事实。

选择撤销生成新 operation/revision，保留不相交后续变更。冲突完整读取真实目标快照、控制历史、后续 B/C 操作、当前引用及 owner/slot/墓碑；ABA 不能凭当前值相同消失。缺历史返回 impactComplete=false 并暂停；conflict 无可提交凭据，不能转 confirm。

## 候选身份与范围

- 实施前过程 HEAD `f51a9e10647d75cd07fe28007ab73c0e65451f63`；批准集成基线 `5f910b52c69d86a1076b2032e5d3c63e715947f3`。最终本地提交另以 Git 回执绑定，不把过程 HEAD 当远端批准。
- [最终源码清单](evidence/changeset-final-source.json)：2573B，SHA256 `21ce587382ed854b29c1b38ad2646a573e01273b3efd4950709e0786e8518b21`；[源码 ZIP](evidence/changeset-final-source.zip)：146725B，SHA256 `64d03db87de4523dd4c2d5e547e3e98ba0431ade82f1ebde760a747916a35d68`。精确10产品+4新测试，验证前后回读相同。
- 不修改原 tests、desktop、storage/transactions/format3/applications/worker/protocol/resources、errors/dependencies、锁、构建配置或 CI。受保护 AGENTS SHA `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759` 保持未暂存；旧 task-runtime 维护窗口已关闭。

## 实际验证及首失败

| 验证                    | 实际结果与原件                                                                                                                                                                                                                                                                                                                                                                                |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 最终完整 npm check      | exit0，1125 TS、2789 Python，44 项原不适用 skip；lint/格式/类型/build/ruff 均通过。`/tmp/t01-changeset-fullcheck-01.log` 8269B，SHA `30fbb987d484118dd70a1cd9975d76862244e5b6e1bede2174323c21a96c8888`。                                                                                                                                                                                      |
| 新服务/故障             | 最终78项；此前75新+165旧JobStore=240通过。27个真实 os._exit 边界、13处 SQLite authorizer 实际拒写、异常/模拟存储失败/取消逐边界回滚、完整持久 dump、真实失效与无关结果保留。                                                                                                                                                                                                                  |
| stdio/Node              | 新stdio5项、新真实监督器2项包含在最终check；完整 Diff、>frame旧值、订阅/receipt page、选择undo/重开、旧确认新operation拒绝、普通dispatcher取消、ABA完整B/C及引用影响逐值核对。                                                                                                                                                                                                                |
| canonical/helper        | 最终93项包含在最终check；精确32768±1、16MiB/512与超限、跨段UTF-8、base64/JSON/乱序漏页/改值及捕获边界。                                                                                                                                                                                                                                                                                       |
| sources                 | verify:sources exit0，12个归档源文件保持。                                                                                                                                                                                                                                                                                                                                                    |
| 串行新 unsigned package | package:dir exit0。`/tmp/t01-changeset-package-02.log` 14323B，SHA `f5ea2a89a04617e3208ea20aba2387c8ea4932c739ed0cad75ba404c86994fb9`。                                                                                                                                                                                                                                                       |
| 冻结包内正式业务        | 实际 frozen engine、testMode=false；3个正式 Job 完成提交、不相交B、undo及新Session原operation重试，真实数据库 revision/sequence/claims/receipts 各3、只保留B。报告10988B/SHA `5565d6f9462a396b8839d5a42d0034e36cce11fe12a896169569f2e4dd7ebce1`。                                                                                                                                             |
| 静态包同源              | 实际 asar/main bytes 相等，main SHA `fcdd498ce6084b10369648512a11fba931306f3164d88448caf7ef841776b850`；8 JSON+Python helper共9资源逐字相同；registry `1f2e298209e238433c02864a05c70b24482e4c1fd00e7309f63eac84a1f3706b`；引擎 SHA `10dea9b2e9f104707935fc4b418131d91b423548b07ed8f0598086f5783c95a4`。绑定报告1951B/SHA `7d9d5de09ac003618e79db3446807b4ee0ba49e1b267c2d542d6377bebf4512b`。 |

真实 hello 首失败暴露 strict3 成功响应仍投影至旧2能力白名单，已在 TS/Python 同步修复，并加入完整17能力实际响应回归。独审另发现 helper getter 预算捕获竞态和同ref损坏 blob 被忽略两项P2：分别一次有界 descriptor 捕获、preview 事务内读回并全值核验已有不可变记录；新增反例先实际失败，修后由独立 agent 原探针关闭。详见 [独立实现审查](changeset-business-service-independent-review.md)。

新 fixture 的 marker 字段、receipt page order、legacy format/profile 误配、TS overload/转义等首失败均保留，不改旧验收迁就新实现。第一次构建与 fullcheck 构建并行，导致校验目录 main 的随机 CSP nonce 不同于首包；两完整 main 和唯一 nonce 差异保留，之后串行重包。第二次绑定的旧探针不认识 Vite 静态 JSON.parse 字串，保留失败后仅扩探针识别精确 JSON.parse(string literal)，不 eval 应用或放宽产品；最终绑定通过。后续只文档/归档不重跑未变产品。

## 后续完整验收与审查输入

仅内部服务阶段完成相应机制验证。专用 stdio host 调用不证明真人已读完整 Diff/点击确认，也不证明 I06 sender/mainFrame/项目选择/命名 preload/App 已接通。真实 Agent producer、附录C完整领域语义、source parser/授权/pin、学习激活及不可洗白辅助账本、metadata/draft/learning 全项目恢复、原44项其余功能与 T08/跨功能、双平台/native/真人验收都保留，逐项关联原地图，不降为本typed子集。

同候选 ZCode GLM-5.3最高与 MiniMax Code M3.1-Flash/xhigh 的新独立完整审查、意见处置、push/PR/CI、正常合并 develop 与远端核验仍为后续门。当前宿主没有启动 Electron、GUI/native/e2e/HMR、凭据后端或审查应用；隔离环境缺口不计通过。两模型使用 [相同只读审查输入](changeset-external-review-input.md)，内部 agent 不能替代。

## 原始证据封存

[完整原始归档](evidence/changeset-raw-evidence.tar.gz) 1189059B，SHA `29a3f65fdff1f7635f1595db8a6d368d26050455c719ac92c53ab733cac85c0a`；[索引](evidence/changeset-raw-evidence.json) 193052B，SHA `40ce9396152a431ad0417105ccbecaa8d7929bf01978e39d3aab6bbe1cdf1673`。163成员包括281对原完整工具call/output（主线105、独审57、Python59、canonical60）、首失败/被替代输入、27真实退出、源码/Node/包内全部原stdin/stdout/stderr三流和验证脚本。每行原source prefix、offset/长度/SHA绑定，未完成capture自身call不伪造output。全部成员hash、每对call/output及wire三流base64/长度/SHA已经回读验证。

报告引用的独审最终30586B/SHA `3acb0305f1ece626c07f192c3ccb07af1c69907ec3a3ec816137475481e31a30` 已全文读回，显式绕过reviews忽略规则的格式检查通过。大原件本阶段入库仅为总控已要求可恢复原始工具及首失败审计；不包含SQLite运行库、凭据或用户业务资料。
