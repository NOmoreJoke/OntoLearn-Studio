# T10 → I06/T01：受信导出白名单与导入生命周期合同 r1

2026-10-21，待总控及对应 owner 批准；没有注册公共方法、批准包格式、修改共享文件或宣称真实导出入口已实现。

已全文读取 I06 流程提交 `235c3ac1b218e0529344587307462d8278e6d87e` 的 `semantic-export-integration-request.md`（SHA256 `f69b5ca9c5f66adf3987c72788f70fc42daf48fb83d9047339f3fae7f17baebc`），并读取固定产品 `e2c269ad78a78e1a042cadc93b1c81a874707153` 的 main/index、task-service、private-directory、model-service。以下回应其§2–3。该版本 `PrivateLocation.excludedRoots` 仅实际DB/wal/shm，open后集合固定；本提案不把动态根算成已经登记。

## 1. 选择等价白名单读取边界

T10 不读取/打包 Store SQLite 文件、userData 或任意项目目录树。完整/模板/HTML均从 owner 的固定业务投影生成；附件仅来自已选择、可证明归属的原始数据对象。I06私有根由其main唯一owner提供受信边界，T10不从renderer、包内字段、模型文本或“排除数组”推断。

本提案请求批准下面的内部职责与输入约束，正式 canonical 方法/参数/schema 仍由 T01 同版批准。表中“对象/lease”是 main 内不可序列化能力，不能成为桥接参数。

| 输入/位置     | 受信来源与精确范围                                                                                                                                         | 允许操作                                                                                       |
| ------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| 源项目/Store  | main选中项目；T01返回projectId、完整checkpoint身份、域/应用版本/CAS与schema/reader/writer版本绑定的不可变投影。T10不接触原始DB字节                         | 校验正式schema后编码；没有泛化SQL、FS读取或二次Store writer                                    |
| 可选原始数据  | T01提供固定对象ID、所属项目/代次、预期长度/hash及未打开的有界读取引用/来源位置证明。选择对象须在同次固定清单中，经相应guard后才取得main/engine只读读取能力 | 仅读取清单内该对象；不follow目录、不按包内路径或renderer路径读磁盘；越界/版本漂移/来源不明拒绝 |
| 导出final     | 实际main native picker选择的单个新文件，规范化父目录+有限basename；绑定父目录身份、最终文件身份及当前项目/请求代次                                         | 原子不覆盖发布；不扫描该父目录树，不把父目录当数据读取根                                       |
| 导出staging   | 先guard批准final同FS父目录内严格随机子目录的prospective范围，再由T10排他创建固定成员、扩展绑定实际目录/文件身份                                            | 仅自身成员的写入/校验/发布/非递归清理。当前HTML服务已有该流程，但尚无I06私有根guard接线        |
| 输入包        | 实际main native picker仅给main-owned候选位置；先guard，才打开只读句柄并取得稳定长度/hash/身份，有限大小                                                    | 先内存结构检查；正式payload校验/支持版本核对后才交唯一writer；不把zip成员当FS路径              |
| import-unpack | 只有经批准的payload确需落盘时，先guard批准prospective位置，再由main/唯一writer创建排他任务子目录并绑定身份；否则为none                                     | 按正式成员白名单建固定新文件，无symlink/硬链接成员/目录遍历；失败不修改已有项目                |
| 新项目staging | T01唯一writer返回的新目标能力，不是renderer或T10任意路径；新projectId及引用映射固定                                                                        | 唯一writer验证后原子发布；T10不自己建第二数据库/事务或覆盖原项目                               |
| backup        | 本合同的新项目导入及不覆盖导出均为none                                                                                                                     | 未来需要backup须单独批准实际业务投影与位置，绝不默认复制数据库/userData/private目录            |

因此source project没有“递归读取根”；实际数据库位置仍由main/T01提供给I06当前DB排除，不因白名单忽略它。final是单个文件，staging/unpack是精确任务子目录；父目录即使是home也不被当成可遍历载荷根。任务实际位置或任何白名单源与私有边界相交则拒绝，不以“不是同一路径字符串”判定安全。

## 2. I06 main-only位置lease（请求）

建议由I06提供内部 `withTransferLocationLease(descriptor, action)`，T10持有不可序列化lease；这是待批准适配器名称，不是现有函数或新公共能力。descriptor只能由main组合：当前profile身份、源项目/版本、上述精确read/write/staging/unpack位置及操作用途；none必须明确记录，不能用空数组假装已检查动态位置。renderer只表达操作与选项，不提供这些位置。

I06 owner从其实际profile路径/持有锚点导出完整私有边界：`model-gateway-private-v1`整体及credentials/configurations/audit与pending/journal等所有后代，含密文文件；不把具体路径/原件/句柄返给renderer或Python。guard独立于模型网络/credential可用性，不要求读取真实密钥。T10只得到是否可继续的lease及固定安全失败。

lease分为bootstrap与实际身份绑定两步，要求：

1. native picker只返回候选位置，不open/read/hash。bootstrap guard可以执行有限的metadata-only realpath/lstat及其owner持有的私有元数据核对；不得先open业务文件、hash内容、mkdir、写出或提取再补检查。对已存在路径用realpath/lstat及持有句柄核对，未存在目标解析最近实际祖先+严格后缀。检查私有边界与每个实际范围的相同/包含/被包含关系；文件只读范围还须排除已登记私有文件的同dev/ino硬链接别名。源附件若owner不能证明来源或排除私有原件，不接受为附件。
2. profile私有锚点、目标父目录、源对象/任务目录身份须稳定。在bootstrap guard批准prospective范围后才打开文件/创建目录，立即扩展绑定实际身份；若扩展失败不得继续读取/写入。每次打开/读取/写入前、跨await恢复和最终发布前重验；项目/代次或profile切换使lease失效。用户可控symlink、替换目录、重新打开别名与祖先重叠拒绝；仅经批准的OS别名按I06现有边界处理。
3. 动态位置通过该等价白名单/lease实际校验，不宣称已经加入原冻结`excludedRoots`。若I06选择可更新registry实现，必须由其owner同步私有I/O重验及在途任务失效规则，不能仅修改初始化数组。
4. 现有HTML服务的fault checkpoint不是权限检查接口；不能把测试hook或仅picker返回前的一次检查当完整lease实现。批准后由T10在本线独占服务增加明确guard调用，保持既有发布/耐久性/清理状态。
5. bootstrap失败在首次open/read/hash/mkdir/写入前拒绝；实际身份绑定或后续检查失败则停止后续IO，不读私有字节、不继续写出导出正文；已发布结果保持published，不因后续失败谎报取消。身份丢失不递归清理；报告cleanup pending并仅允许受控协调。无法确定是否发布时保持publication-unconfirmed，不自动重试新发布。

同UID恶意进程持续控制namespace不在当前I06 POSIX边界保证内；不能把逐次身份校验称为抵抗该类攻击的绝对保证。Windows及平台不支持的安全原语须另经owner批准/实际验收，不能以关沙箱或放宽检查兼容。

## 3. 载荷、完整/模板与私有状态

| 类别                                     | 允许的业务语义                                                                                                                                                                                                                                                                                                  | 必须排除/失败规则                                                                                                                                                                                                                                      |
| ---------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 完整包必需内容                           | FR-1000全部必需集合不可裁剪：本体定义、当前断言事实及映射重跑/来源定位/人工冲突检测所需来源与所有权元数据；映射定义、查询、约束、规则、行为、场景定义、学习任务及清单；恢复当前项目所需配置和版本；另含生成版本/managed值/墓碑、域/应用状态及完整checkpoint中必要撤销引用闭包。T01批准精确payload不得删减该集合 | 缺必需当前事实/来源不能冒称完整；不能用“排除凭据”名义静默删除合法业务checkpoint。合法项目配置及恢复当前状态/必要撤销所需、可证明的最小闭包按T01合同保留；一般运行历史/会话仍服从选项。若必要闭包与未选项冲突，须拒绝或协调合法schema，不能暗带或静默删 |
| 模板                                     | 用户明确选择模板；只含正式允许的定义/映射/结构/说明及其必要版本                                                                                                                                                                                                                                                 | 不含当前事实/私有项目实例、凭据或旧授权；不可把损坏完整包自动降成模板后返回成功                                                                                                                                                                        |
| rawSources/derived/history/agentSessions | 分别明确选择；所有false仍可为完整包。manifest和实际成员/业务投影必须一致；当前state所需的来源/撤销快照不能被误当可选运行历史删除                                                                                                                                                                                | 未选不写入。无原文件仅限制直接重跑，缺相应运行输入仅限制对应重放，不误降模板；版本/依赖/实际语义不足明确未支持                                                                                                                                         |
| 模型业务文本/会话                        | 被明确选择的业务文本可作为普通数据，保留真实辅助/逐attempt来源；业务配置与I06 profile配置分开                                                                                                                                                                                                                   | 不恢复为执行指令、活跃发送任务或独立掌握证据；包内URL不自动加载/调用                                                                                                                                                                                   |
| I06私有profile状态                       | 无允许载荷                                                                                                                                                                                                                                                                                                      | credentials含密文原件、binding/ref/principal/版本、profile配置journal/endpoint配置、audit/发送ledger、context/grant/preview/catalog/selection/invocation等运行授权均不得导出/恢复授权；不能作为附件、日志、失败dump或迁移元数据带出                    |

投影是业务白名单，不以扫描真实密钥作为生产权限判断。任意业务自由文本/原始文件若含用户粘贴敏感内容，不能宣称通用检测已解决；必须沿owner批准的字段/来源限制与脱敏或拒绝策略验收，该策略未批准前不开放真实导出。X2使用隔离合成标记及密文原件比对证明系统私有材料排除，不能因此声称识别了所有用户自带秘密。

## 4. 精确生命周期与失败处理（不改共享文件）

实际固定源码：`TaskService.selectProject`只在projectId改变时调用`onProjectChanged`；main已传`models?.selectProject(projectId)`；`ModelGatewayService.selectProject`对相同ID直接返回，对新ID关闭旧application并生成local新context、空grant/preview等。不能把重复调用同一ID当授权重置。

拟定调用顺序：

1. 主进程验证可信窗口/mainFrame、项目/请求代次，选择选项；真实picker之后先取得bootstrap位置lease，再open/read/hash或mkdir；实际身份扩展绑定成功才继续。取消不创建新项目/授权，未到发布前的失败只结束本次transfer；本地Store和现有合法项目上下文继续工作。
2. T01唯一writer验证完整包、身份映射及全部引用后原子发布**新的projectId**。包内旧项目ID和context/grant都不是授权来源；拒绝覆盖或复用当前projectId。失败/不明回执按T01正式receipt协调，不调用tasks.selectProject，不猜测成功，也不重放领域写/网络请求。
3. 用户实际打开新项目且T01正式receipt可核验后，由main调用`tasks.selectProject(newProjectId, [])`，其中newProjectId来自writer而非包/renderer。现有回调可触发新local context；严禁传入包内jobIds恢复旧运行。独立profile为新main服务，同profile即使已有凭据也必须重新选择/预览/确认，receiver在实际确认前为0。
4. 窗口崩溃/只读恢复保持现有本地receipt/CAS和真实状态，不借恢复回调执行导入、重发或自动授权；同项目正常恢复不得无理由清除合法现有授权，保留I06 A03已有边界。导入数据本身永远不携带可复用grant。
5. 模型初始化/审计/网络失败只使模型/对应transfer受限，不能阻断窗口、Store保存或已提交本地结果；位置guard失败也只拒绝transfer。返回固定安全码与有限状态，不返回路径、原始异常或私有数据。

当前没有正式import receipt或已批准入口，因此不提出可直接套用的main共享diff。正式schema冻结后，T10先给I06精确路由/guard工厂调用diff及失败分支：预计仅main/index的有限可信路由与依赖构造，既有task-service选择回调原则上可复用；若不能证明其满足新receipt/代次约束，再单列task-service diff交原owner。canonical/engine全由T01维护，T10不占写。

## 5. X1–X6 同候选真实验收计划（全未关闭）

| 门  | 实际入口与同版原件要求                                                                                                                                                                                                   | 当前边界                                                            |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------- |
| X1  | 真实完整/模板/HTML入口，四个选项分别开关及全关、manifest与解码成员/当前业务内容逐项对照；失败/取消同样核临时产物                                                                                                         | 私有报告/候选zip单测及native保存不足以关闭真实X1                    |
| X2  | 隔离合成credentials/config/audit/context/grant标记，保存私有明文测试值及**真实生成密文原件**hash/长度/字节；检查实际包每成员、解压/导入库页、manifest/HTML、日志、staging/backup/unpack，失败/取消亦查；不得在生产读密钥 | 没有真实exporter，未验；不能只搜plaintext或把metadata audit当可带出 |
| X3  | DB/项目白名单/final/staging/unpack与私有根同路径、祖先、后代、symlink、硬链接别名、重新打开和操作中替换；证明在读取/写出前拒绝且不破坏原项目                                                                             | private服务现有路径单测不是I06动态根联验                            |
| X4  | 实际导出→独立profile与同profile新项目导入，记录新project/context/local、旧grant拒绝、实际receiver=0；用户实际选择/预览/确认后才允许一次授权范围内发送                                                                    | 没有真实导入入口，未验；不可用合成exporter或包内grant替代           |
| X5  | 同版模型启动/审计/网络故障与取消/窗口恢复期间的Store保存、正式receipt、域/应用CAS对照；读取恢复不能执行网络或领域写重放                                                                                                  | 原I06证据保留原版本；受影响组合另验，不重复无delta专项              |
| X6  | 批准source/canonical/implementation同输入与实际新包实物/hash；源码/包内逐门raw可回读；未知版本/缺依赖安全拒绝                                                                                                            | 当前Docker只运行固定源码私有服务，不是产品包内/双平台证据           |

外审/CI/正常合并/远端核验仍需同候选实际证据。跨模块新增测试先由总控登记owner与精确路径；本提案和隔离native通过均不改变完整T10完成条件。
