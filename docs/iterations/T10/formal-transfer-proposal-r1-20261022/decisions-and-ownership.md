# 待决项、任务责任和上游请求

## 1. 待决项必须逐项批准

下表的“推荐”是可审方案，不是已决定政策；未决项不能被某个示例JSON、测试expected或S1行为默认裁定。涉及PRD Q2/Q3/Q5/Q6/Q7/Q8/Q9/Q10的内容由其实际负责人及根确认，不编期限/预算/人天。

| ID / 关联Q                 | 具体选择                                                                                                                          | 推荐与理由                                                                                                                                          | 决定责任 / 未决影响                                                    |
| -------------------------- | --------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| F01 / Q10 模板最低集合     | A定义模板：非实例metadata+所选定义/引用/版本；B允许受限实例但明确无当前恢复；另需确定是否必须全模块定义                           | 推荐A为清楚产品范围，拒损坏full自动降模板；PRD未穷尽该规则，不以S1 template可带核心角色反向定案                                                     | 产品/课程+T00/T01；未批不能发布模板schema或宣称最低验收完成            |
| F02 正式版本/兼容          | A仅登记的精确版本组合；B允许有证明的minor扩展；不兼容必须拒绝或显式迁移链                                                         | 推荐先A，明确format/payload/canonical/checkpoint/application/reader/writer与semantics分层，避免静默丢字段                                           | T01 canonical/格式owner、T00协调；未批不产生真实formatVersion          |
| F03 分片与编码             | A manifestJSON+有序受限JSONL角色；B strict JSON数组分段；raw一对象一成员或显式chunk对象                                           | 推荐A便于有界逐记录处理，但hash规范、记录类型/排序/跨片引用须owner定义；raw超限不得截断                                                             | T01格式+T03来源+T10封装；多成员改变现私有格式，须新实现/新候选审查     |
| F04 ZIP元数据兼容          | A只支持本应用规范producer、拒extra/目录等；B有限登记extra/元数据并给安全规则                                                      | 推荐先A作为明确格式边界，若有外部生产器要求再选B并列具体兼容fixture；不能宣称全部标准zip必失败或已兼容                                              | 格式/安全owner+产品Q10；无获批producer列表不承诺互操作                 |
| F05 / Q5 预算              | 按角色/对象/包/CPU/帧/并发的精确resourcePolicy；候选平台/规模与拒绝边界                                                           | 不从S1数字或T03 broker8MiB抄产品容量。先给精确字段、边界测量矩阵，实际值由Q5/平台证据决定                                                           | 产品/技术+T03/I06/T01；未定不能声明正式容量或无界分片                  |
| F06 / Q10 四选项子范围     | raw按文件/对象，history按run，sessions按业务会话；derived按结果；XLSX whole-file与sheet范围                                       | 推荐显式对象清单和范围digest。原XLSX字节含整本内容，选择一个sheet不等于允许复制全workbook；若只准表格投影须另称派生材料，不能冒充原文件及同hash重跑 | 产品+T03/I06/T09/T07；默认勾选和历史选择粒度不得自行确定               |
| F07 撤销/恢复保留          | 当前对用户承诺可用的typed undo/restore闭包；若要改变窗口/保存期限须产品决定                                                       | 推荐完整保留现有可见合法控制集合，按最小typed引用裁剪；不是复制全部祖先。冲突未选项时阻断并协调                                                     | T01+产品；不能静默只留genesis或缩短已承诺撤销                          |
| F08 凭据/自由文本          | 字段/来源白名单、介质边界、固定敏感形状/拒绝/受控审阅、保真冲突处理                                                               | 推荐以固定私有边界排除为基础，有限检测仅加阻断；不读vault、无通用DLP宣称。任何“仍导出”不得覆盖凭据禁令，脱敏不能保留等价恢复承诺                    | I06安全+产品+各payload owner；未批不开放真实导出                       |
| F09 进口学习来源/actor信任 | 保留foreign历史主张为unverified，或引入明确来源认证机制；不能默认用户等同                                                         | 推荐先原样保业务记录/来源状态并本机新检查，避免虚构PKI或身份平台；不能洗白或丢弃合法历史                                                            | T09/T08/T01+产品；独立掌握资格规则须同版                               |
| F10 导出时源版本变化       | A默认重新预演最新；B用户显式选择已固定的历史snapshot导出                                                                          | 推荐默认A；B须有明确历史选择/范围和当前权限，不能把旧快照叫最新状态                                                                                 | T01/I06+产品；旧确认不能覆盖变化范围                                   |
| F11 / Q2 安全平台原语      | 每目标OS的目录相对受控IO/别名/失效保证；不支持则拒相关transfer                                                                    | 不以Node复验或旧单平台probe宣称全平台。Q2清单/最低OS/架构待根确认，既有样例OS不是默认产品承诺                                                       | I06/T03平台owner；需要实际native/包内验收                              |
| F12 来源重关联             | 原字节/格式/sheet/encoding/身份规则一致，或用户明确选新源后重做完整预览                                                           | 推荐前者才称同源；后者新context/proof/确认，保留人工冲突。旧operation对账不依赖旧live proof/lease                                                   | T03/T01；同名/仅sourceHash不够                                         |
| F13 身份作用域与目标分配   | 项目scope身份保留或逐类型新ID；预演reservation或事务内符号映射                                                                    | 推荐由T01固定typed映射及确认digest绑定，不递归替换文字，不迁移active job/grant；保证确认与执行同计划                                                | T01 canonical+I06 lifecycle；未批不能写重映射器                        |
| F14 FS附件+DB可见性        | 不可变封存+持久prepare/pin；pin转已提交引用与receipt同一权威可见性；GC claim和commit使用同一排序/代次，或证明等价协议             | 推荐同T01事务registry；pin先于对象可被GC看见，跨崩溃保留，unknown无TTL清理，负终态fence后才可释放。不是跨FS/SQLite物理单事务承诺                    | T01/T03/I06；未批不能实现附件导入                                      |
| F15 / Q10 提示归类         | FR101四级如何汇总FR104至少三类，Agent partial/complete与提示并列                                                                  | 推荐保每事件与四级明细、显示Agent完整辅助，不把概念提示算无提示；具体合并算法由课程/学习owner定                                                     | T09/T08+课程；未知证据不能判独立                                       |
| F16 跨attempt重试/暴露     | A当前attempt判定但保留既往暴露；B任务级辅助上限；新数据迁移另有条件                                                               | 不先选A/B；无论哪种都不因清UI/重置/迁移新ID删除旧辅助，不能自动独立，也不擅称永不能重新独立                                                         | T09/T08+产品；冻结前资格结果保持未验证                                 |
| F17 derived未携带的恢复    | 结果metadata/输入依赖保真、载荷缺席，真实重算后核相同查询；或明确支持的不同策略                                                   | 推荐availability与stale/历史分离，不静默改查询scope、不虚构新staleReason；是否允许/何时重算由真实能力支持                                           | T01/查询推理owner+T10；G.6完整集合须实际验证                           |
| F18 能力措辞               | 材料齐全、版本支持、实际验证三轴，按mapping/run列结果                                                                             | 推荐三轴而非单包true；本机接口缺失/未知不可从包声明推支持                                                                                           | T01/T03/T07+产品；无验证不承诺相应重放                                 |
| F19 恢复身份与全局claim    | 首次dispatch前持久恢复记录；稳定业务request/operation与RPC id分离；writer持久admitted/committed/负终态fence；未知目标的lookup归属 | 推荐T01 writer全局claim权威与受保护本地恢复记录协作，当前main ticket不充当耐久恢复身份；无receipt不等于未提交，包hash不充当operation ID             | T01主责，I06/main与T03协同；schema/授权/恢复入口冻结前不能发送真实导入 |

PRD Q3主成功标准、Q6有限本体能力、Q7固定轮次、Q8资源/排期、Q9受测协议也保持待决；本提案不默认选学习优先/首发平台/引擎能力/模型服务或上线日期。Q5与Q10的具体影响已列上表。

## 2. 本轮与后续任务责任

| 工作包                   | 当前可做的具体产物                                                              | 唯一责任与写面                                                              | 进入实现前条件                                                      |
| ------------------------ | ------------------------------------------------------------------------------- | --------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| D0 本提案                | 全套设计、来源/16组合/例子、独审与处置                                          | T10仅本新docs prefix；PRD/供方审计agent只读，不共同改文件                   | 根完整接收设计仍不等运行票                                          |
| D1 格式/类型             | manifest、角色payload、canonical/ID/版本兼容/closure schema和公共正反例         | T01 canonical/格式唯一owner；T00协调                                        | F01–F07/F13/F17及对应Q明确，同版schema获批                          |
| D2 投影与导入            | 一致读/coverage、typed重映射、原子新项目/receipt/lookup、业务冲突               | T01唯一Store/writer；T10只提消费需求                                        | 精确输入/输出/错误/CAS与故障证据，不能借旧Store.state实施           |
| D3 私有IO/lifecycle/桥接 | inventory/epoch、受控IO capability、代次/确认、新项目打开和授权归零             | I06及当前main/bridge唯一owner按根责任表实施；T10不抢main/index/task-service | F08/F11/F14，实际平台能力；批准精确调用diff/路径                    |
| D4 Source                | 有界封存、完整Table/options/producer、持久身份与lease/GC、重关联与admission对账 | T03领域来源与相应装配owner；T01保持canonical写；T03 build/依赖仍唯一维护    | 根固定T03仅设计来源已供，6装配缺口及其验收仍待                      |
| D5 学习                  | task/attempt/check/hint/assistance真实投影和分类政策                            | T09/T08产生业务证据，T01一致保存；T10报告只消费                             | F09/F15/F16及正式schema/来源证明                                    |
| D6 执行/重放             | 对应run真实输入、cfg/语义/engine/lock支持和逐轮验证                             | T07及实际语义owner                                                          | 真实支持/验证合同，不以metadata齐全充完成                           |
| D7 T10包与报告           | 在本线获批独占路径实现编码/有界校验/plan适配/真实报告，保留S1安全性质           | T10；新runtime路径须根先精确登记，Python/canonical边界由T01责任表决定       | D1–D6消费合同与精确阶段运行票；修改即新候选/必要验证/双方新完整审查 |
| D8 跨模块联验            | X1–X6、G.6、学习、真实native/窗口/包内/双平台/真人与完整57P0                    | 根指定单个测试/集成owner与精确paths，平台/CI按既有owner                     | 批准同版真实业务链；不以synthetic替身替代                           |

以上工作包不是新建Codex chat，也不是已启动/完成人员承诺。当前没有共享runtime路径写授权。依赖可独立设计/审查并行推进，实施按真实合同串行集成，按规定从获批base创建新候选，不擅自切当前冻结树。

## 3. 已向根精确请求的固定上游材料

每个答复都须`repo + commit + path + byteLength + SHA256 + 允许层级`，层级区分仅设计、已批schema、可调用实现。没有的逐项标缺口，不读取供方移动HEAD、不因方向接受复制实现。字段名称以下是类别需求，正式命名沿owner批准合同。

| 供应方  | 精确需要的合同                                                                                                                                                                                                                                                                            |
| ------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| T01/T00 | 完整project/checkpoint/application/draft/learning schema、root/typed边/undo与restore闭包、coverage proof、source/owner/managed/tombstone/版本ledger、canonical/reader/writer、schema registry/兼容迁移；一致读投影API；ImportPlan/CAS/identity scope/Store单事务/幂等receipt/lookup及错误 |
| I06     | 完整私有inventory epoch/revision/completeness、动态发布/失效/退役、metadata bootstrap与实际handle capability、平台原语/失败、窗口/项目/profile代次、用户确认/新项目打开/无网络恢复                                                                                                        |
| T03     | 来源对象与封存/有界读取、完整Table/options digest与producer、sourceRef传输两段预算、lease/pin/GC/admission排序/旧operation对账、正式重关联及目标OS边界                                                                                                                                    |
| T09/T08 | 真实task/attempt/check/hint/assistance/操作与独立迁移指标、版本/来源/完整性、所选会话与必要业务证据的拆分、跨attempt/跨设备政策                                                                                                                                                           |
| T07     | 逐run固定input/config/events/behavior/rule/scene/semantics/engine/lock、实际支持矩阵、完整逐轮验证与缺依赖理由、只读历史/重放入口边界                                                                                                                                                     |

首批T03供应以根固定JSON为准：12个docs允许本次设计读取，3源码仅身份支撑不读字节、不采用实现。具体接收层级与缺口见upstream-T03-intake.md及source-provenance.json。其他owner新材料若稍后到达，在本提案新接收记录中单独登记；不得通过改旧225来“更新受审输入”。
