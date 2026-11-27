# I06 对 T10 受信转移合同 r1 的回应

2026-10-21。结论：接受业务投影白名单、完整私有根排除和新项目导入后的授权隔离方向；**尚不能给出现有 guard 已可用或真实转移已安全接线的回执**。建议先登记独立 main 私有 guard 模块及其元数据供应契约，再由 T10/T01/I06 各自接线。本文只做设计回应，没有新增公共方法、包格式、实现、平台验收或共享写权。

## 1. 固定输入与实际差距

全文读取 T10 固定提交 `b39c87ed80d28bfd63b21881a5e6673eee212e7c` 的 `docs/iterations/T10/i06-trusted-transfer-contract-request.md`，19000 bytes，SHA256 `6e52cdf4230b61034366963ef39808cbdf8b7e62655a0ec168d77706b311b7bd`。同时全文读取其引用的 I06 `235c3ac1b218e0529344587307462d8278e6d87e` 文档，SHA256 `f69b5ca9c5f66adf3987c72788f70fc42daf48fb83d9047339f3fae7f17baebc`，并核对 PRD FR-901/902/904/1000/1001。

本次读取的四个 I06 文件与固定产品 `e2c269ad78a78e1a042cadc93b1c81a874707153` 逐字节相等：

| 文件（相对仓库根）                                         | SHA256                                                             | 直接事实                                                                                                         |
| ---------------------------------------------------------- | ------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------- |
| `apps/desktop/src/main/model-gateway/private-directory.ts` | `40a9a5d52488a25d3958c171ac3e5df4272eed5d42a97f51a76ee5baeb015a88` | POSIX 持有目录锚点，私有 I/O 前后复验固定 excludedRoots；不提供动态 transfer lease 或整个私有根的权威 inode 清单 |
| `apps/desktop/src/main/task-service.ts`                    | `7ed65bd689a8cfa445b4d349a1a996750f67c190600d0f46b2dceb324ebd0a68` | `selectProject` 校验 UUID，清理视图，并仅在项目 ID 变化时触发回调；不校验导入 receipt                            |
| `apps/desktop/src/main/index.ts`                           | `d88c1df806dc913b85a719026640ee6502762153c82c148e57aa32d5dbd9c60b` | main 取得实际 userData/DB；excludedRoots 仅 DB、WAL、SHM；窗口先可用，模型异步初始化；尚无正式 transfer 路由     |
| `apps/desktop/src/main/model-gateway/model-service.ts`     | `0bfd4360cbaf086b143fbc209e68994cc65496f3f9bce7d3a0bc4609c5a28395` | 不同项目关闭旧 application，创建 local、新 context 和空选择/授权集合；同项目直接返回；没有导入载荷恢复授权入口   |

当前 `PrivateOperations` 的最多 32 个在途操作是准入/关闭管理，**不是跨 bucket 的互斥锁、inode registry 或转移隔离机制**。单 bucket 的 `opendir` 有界枚举及内部临时文件检查也不能自动变成整个 profile 的可信清单。现有 `PrivateWriteObserver` 是故障观察 seam，不能承担生产权限判断。

操作遵守最新共同指南 SHA256 `b24c4c88404f422c5fae4bf6c01e231b678e46741250801e8100cc62a31fec39` 与实际最新 AGENTS `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`。本树保留受保护旧 AGENTS `db1fb184809932a27c5bfd8c91b72837d719cdbdc07d7a83860e5cba38529786`，不修改或暂存。已交 T01 canonical 七文件及 main/engine、Python 四文件，以及 T03 构建四文件，不在本设计的未来编辑申请内。

## 2. 逐项回应与需要补齐的合同

| T10 请求                                    | I06 回应                                                                                                                                        | 正式启用前的具体缺口                                                                                                                                                         |
| ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 固定业务投影，不拷 DB/userData/任意目录     | 接受。完整包保留 FR-1000 必需业务集合，模板与四个可选项按真实清单区分；不能借私有排除静默裁掉合法业务配置/来源/撤销闭包                         | T01 批准同版投影、checkpoint/CAS、引用闭包及 reader/writer/version；T10 给逐成员编码与选项映射。文档描述不等于 payload 已批准                                                |
| 原始对象与输入包先 guard 后读               | 接受有界、未打开的来源证明。对象 ID、项目代次、长度/hash 必须来自实际 owner；hash 只验证字节，不授予读取权限                                    | 提供对象归属和实际物理读取范围；若 engine 读取附件，必须在其首次读前消费等价受信能力，不能 main 已检查但 Python 另按字符串 reopen。无需、也不得将私有根清单或凭据交给 Python |
| final/staging/unpack/new-project 位置 lease | 接受 main-only、用途限定、不可序列化能力。backup/unpack 不使用时显式 none；final 父目录仅作发布锚点，不成为 payload 遍历根                      | 需冻结实际位置/成员集合、字节/数量/期限上限、独占创建和发布原语，以及本节后的 bootstrap/绑定顺序。现有 HTML fault checkpoint 不能替代 guard                                  |
| 动态位置与私有根相交检查                    | 选择独立 guard/受信白名单适配器方案，不把新路径虚称已进入旧 excludedRoots，也不先改其初始化数组                                                 | 整个私有根的稳定锚点、完整 inode 元数据来源、在途失效规则尚缺。若改用动态 registry，必须同时覆盖私有 I/O 与转移，不只给 transfer 加一次 path 检查                            |
| 私有材料及密文全部排除                      | 接受整个 `model-gateway-private-v1`，不只三个已知 bucket。其 pending/journal、未来后代、密文和内存授权状态均无允许载荷；metadata audit 亦不导出 | 同 inode 硬链接别名须查可信 inventory；仅 path、扩展名、nlink 或 plaintext 搜索都不足。业务自由文本/附件的额外敏感内容策略仍由 owner 明确，不宣称通用秘密识别                |
| 导入后新项目/new context/local              | 接受正式唯一 writer 的新 ID 与成功 receipt 后再选项目；不消费包内 grant/job/context，失败或发布不明不切项目                                     | 当前 TaskService 不含 receipt 验证，main 必须有受信协调层。T01 receipt 与项目代次、重试/恢复查询语义尚待冻结                                                                 |
| 失败隔离与固定错误                          | 接受 guard 仅拒绝该次 transfer，不把它依赖于模型网络、safeStorage 可用或模型初始化成功；本地 Store/窗口继续工作                                 | 路由按批准错误目录返回有限结果，不回传路径/原异常。不能自行把 transfer 错误伪装成已有 GATEWAY 错误；公共目录扩展归 T01                                                       |
| 全平台及真实入口通过                        | 保留 X1–X6 原门，不以旧 I06 平台或 T10 私有服务原件替代                                                                                         | 本轮没有运行。Windows 当前私有目录本就拒绝；未验证的文件身份/发布原语一律 fail closed，Linux 设计不外推 Windows/macOS                                                        |

## 3. main-only bootstrap 与实际身份绑定顺序

建议构造位置在 `app.whenReady()` 后、profile 单实例归属及实际 userData/DB 确定之后，**独立于 `initializeModels()` 的成功路径**。main 拥有 guard 工厂、profile epoch 和 transfer 请求代次；T10 只能得到当前请求的有限能力。初始化不能为构造 guard 先解密凭据、打开业务源、读取包内容或创建 staging。

私有根尚未建立、仓库恢复失败或 inventory 未齐时，guard 仍须知道其受保护 prospective 范围；没有根目录不等于无需排除。无法完成必要身份/别名证明时，相关转移拒绝，不降级为忽略私有根；不阻塞本地模型之外的正常 Store 保存。若要在私有服务故障时继续安全转移，需由独立的私有存储元数据 owner 提供充分证明，不能以 `models === undefined` 当作私有内容为空。

每个转移按以下顺序执行；名称均为待批准内部设计：

1. main 验证当前窗口、mainFrame、可信文档和用户动作，捕获实际 profile/项目/checkpoint/request generation。native picker 只给候选，不给读取授权；经过 picker 的 await 后再次验证请求归属。渲染端不提供路径、排除根、身份或 writer receipt。
2. bootstrap 仅做有界 metadata 检查：真实祖先、严格 basename/后缀、私有根及实际 DB/任务范围、可信 owner/mode、已知 inode 别名。未存在路径解析最近存在祖先；不存在或错误必须分类，不能把任意访问错误当 ENOENT 放行。拒绝用户可控 symlink；OS-owned alias 也只按已批准规则处理，不泛化为 root 所有的任意链接都可接受。
3. **bootstrap 通过后**才允许打开指定读句柄或排他创建指定任务目录/成员。立即 fstat、核对之前的身份与用途、扩展绑定实际 handle/parent/member；绑定失败不读取、hash 或写正文。创建产生的受控空成员只能在身份仍可证时有界清理。
4. 后续只使用所绑定句柄和固定成员能力，不将 lease 降为字符串后另行 reopen。每次内容 I/O 前与跨 await 恢复后验证 profile/项目/请求代次、inventory revision、源对象/父目录/任务成员身份；流式读取/写出遵守批准的块/总量上限。新位置或 reopen 必须重新 bootstrap/绑定。发现变化停止后续 I/O，不把末次检查后的旧结果继续发布。
5. 发布前重新验证所有身份、同 FS、无覆盖目标和业务 checkpoint/receipt 前置；发布成功后的真实提交事实不能被观察回调异常改写。结果未知时进入有限协调/只读查询，不自动再 publish、再 import 或再请求模型。
6. 释放句柄与 lease；仅清理已绑定、仍归本任务的固定成员，不递归遍历用户目录或在身份丢失后按旧 path 删除。已发布保持 published；不明发布与 cleanup-pending 分开记录。公开结果不包含物理私有路径、inode 清单或内容。

**保证边界：**现有 Node 路径式 `lstat/realpath → open/mkdir/link` 不构成目录相对原子权限边界；`O_NOFOLLOW` 也不能独自约束所有祖先。持有 handle 与事后比对能检测特定替换并在内容读取前拒绝，但不能抹去已发生的 open/mkdir 副作用，也不能保证检测每个瞬时替换。不能把“每个 await 都复验”写成抵抗同 UID 持续 namespace 攻击的证明。当前合作 owner、受信祖先与权限约束内可设计有限 guard；若要求更强原子 confinement，需另交 owner 批准相应 dirfd/平台原语与实际证据，不能在本线私加 native 依赖、放宽 sandbox 或声称已经满足。

## 4. 全私有根与硬链接：metadata owner 不能省略

路径包含关系必须围绕私有**整根**双向检查：相等、祖先、后代及解析后别名；不能仅比 `credentials` bucket，也不能漏掉不存在但已被 main 保护的后续目录。 比较对象是实际准许读取/写入/创建的文件或任务范围；仅为解析或发布而持有的 home 等祖先不成为递归权限范围，也不因它包含私有根就拒绝其下其他不相交的新文件。若能力实际允许遍历该祖先，则必须按该更大范围拒绝，不能借“只是锚点”隐瞒越界权限。文件别名采用同平台可靠文件身份；POSIX 至少比较实际打开对象的 dev/ino 与 owner 清单，不能用 hash 来识别应禁读的文件，因为计算 hash 已经读了私有字节。

建议清单由 I06 私有存储 owner 维护，只在 main 内向 guard 提供不可伪造的、带 profile epoch/revision/完整性状态的元数据视图。来源是 owner 已持有的目录/文件句柄身份、正常私有文件创建/发布/删除事件，以及有界、metadata-only 的启动恢复。不得接受 T10/renderer 注册“这不是私有文件”，不得通过读取 key、解密密文或扫描用户目录寻找别名。

需要先冻结四个条件：

- **完整性与预算：**包含全部 bucket、pending、journal 和其他已存在后代；未知成员、未支持子树、目录替换、枚举预算/期限超限均使相关 transfer fail closed。不得无限递归遍历私有根。现有单 bucket 的 11024 名称限制不是新 inventory 已完成的证明，也不能拿凭据/审计写入准入阈值判合法旧库损坏；inventory 不足只拒绝转移，不删除或重写旧库。
- **一致性与锁：**所有可信私有 namespace 变动须通过同一 owner 的元数据发布协议；snapshot、候选 open/fstat/别名判断与 revision 核对要有短临界区/明确失效屏障。新文件在可被转移观察前登记，临时/正式两名字的同 inode 一并登记。不能把现有每 repository 的 Promise 队列或进程单实例锁当成跨根锁。不能把私有全局锁一直持有到 picker、网络等待或整个大文件编码结束；锁顺序、取消和预算应独立验收。
- **删除/退役身份：**不能在删掉私有名字时无条件遗忘 inode。仍持有或可证残留的别名须保持保护；内部 publish 的临时/正式硬链接对是合法内部恢复状态，不代表可以外发该 inode。如何安全退役、处理异常 nlink/不明别名、重启恢复及预算耗尽，需 owner 给出可证明规则。只枚举当前名字不能证明历史移出/复制内容的所有来源；本方案不声称通用 DLP 或抵抗恶意同 UID 搬移/再链接，来源不明的附件仍拒绝。
- **跨 owner/跨进程：**任何正常私有写者绕开该协议，或 engine 重新打开未绑定来源，都会使 lease 证明失效；不能靠 transfer 轮询补齐。当前单 main profile owner 有帮助，但不证明跨进程 writer/inventory 协议已存在。无支持的身份原语、inventory 未就绪或无法确认闭合性时拒绝相应操作。

因此可接受“静态私有原件在根外的硬链接别名也拒绝”这一验收要求，但不能在没有可信 inventory/变动协议的现状下承诺实现已满足。X2 的合成密文字节比较应由隔离夹具在其自身证据中完成；生产 guard 不返回、读取或 hash 私有内容。

## 5. 唯一 writer receipt 后的项目切换

正式导入协调层需持有 main 请求能力，消费 T01 唯一 writer 的可核验结果：至少绑定本次 request、原目标/项目代次、实际新 projectId、支持的 schema/implementation、提交身份与明确提交状态。这里只列语义条件，**不另造 receipt schema、公共方法或第二 Store writer**。

成功且用户要求打开时，main 在最后一个 await 后重验当前请求/项目/profile 与 receipt，确认新 ID 非当前/包内旧 ID，才调用 `tasks.selectProject(newProjectId, [])`。不能在等待期间用户已切到其他项目后，用迟到 receipt 抢切回来；可保留已提交新项目供用户随后明确打开。若验证与调用之间没有 await，也仍不等于已经取得 T01 事务/CAS 证明。

现有回调可复用：新项目 ID 触发 `models?.selectProject(newProjectId)`，关闭旧 application 并产生 local 新 context；选择、catalog、preview、grant、invocation 均不从包恢复。模型当时不可用不妨碍本地项目成功打开；若随后初始化成功，现有 `tasks.projectContext()` 会用于该时实际项目。相同 ID 的重复 `selectProject` 不会清除旧授权，所以不得复用原 ID 来冒充重新导入隔离。

失败、取消、receipt 不可信或提交状态不明时不切项目、不猜成功、不重放写入或网络。若实际提交成功但回执/后续选择失败，保留其真实提交状态并按同 request 只读协调，不伪称“没有创建项目”，也不再提交一次。窗口恢复只读回当前 main/Store 状态；不自动导入、选新项目、confirm 或 start。原项目正常恢复不无故清空已有合法授权；新导入项目则必须重新选择、预览与用户确认，实际确认前 receiver=0。

## 6. 原 X1–X6 的最小接线与证据 hook

固定请求没有定义六个可调用的生产函数名；下列按原 X1–X6 六门列最小 hook 条件，不把 fault observer、新测试 API 或本表编号冒充已存在接口。具体 main/T10/T01 diff 仍由其 owner 冻结。

| 原门        | 最小可信接线条件                                                                               | 必需反例/直接证据                                                                                                                                            |
| ----------- | ---------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| X1 范围     | T01 固定投影 → T10 实际选项/清单/编码；包含本节前的 bootstrap、实际绑定与有限成员能力          | 完整/模板/HTML、四选项分别及全关；实际成员与业务集合一致；取消/失败临时产物。尚无正式入口不能用假 exporter 关闭                                              |
| X2 私有排除 | 全私有根 metadata owner + inode 别名拒绝 + 白名单载荷；公开结果/日志不携带私有标识或原件       | 隔离合成 key/config/audit/context/grant 与真实生成密文，检查实际包/HTML/manifest/导入库页及 staging/unpack/失败日志；保存字节/hash 比对，不只 plaintext 搜索 |
| X3 位置     | main 工厂、每次 read/create/reopen 的 bootstrap/绑定、await 后及发布前复验、失败停止与有界清理 | 同路径/双向包含、symlink、静态硬链接、祖先替换、跨 await 变动、未知 inventory、预算超限；记录首次内容 I/O 前拒绝。受控替换反例不扩大为持续同 UID 攻击保证    |
| X4 导入授权 | 正式唯一 writer 成功 receipt + 新 ID + main 最后代次核验 → `tasks.selectProject(newId, [])`    | 独立 profile 与同 profile 新项目；旧授权/迟到 receipt/同 ID 导入拒绝；确认前零请求，实际选择/预览/确认后仅范围内一次发送                                     |
| X5 本地保存 | guard/模型失败局部隔离；保留真实提交状态；恢复路径仅查询，不重新执行导入/发送                  | 同候选启动/审计/网络故障、取消/窗口恢复与实际 Store receipt/CAS；原项目不损坏、无领域写/模型重放；不重跑无 delta 旧专项                                      |
| X6 包内     | 注册后的批准 source/canonical/implementation 同候选，真实产品入口与实际新包分别绑定            | 原命令/退出/首失败、实际 executable/resources/hash、未知版本/依赖拒绝；旧 source/包、私有 Docker 服务或纯设计不得顶替；Windows 未实测保持拒绝                |

## 7. 可独立准备的 guard 范围与精确路径申请

建议向总控申请唯一新实现路径 **`apps/desktop/src/main/security/private-root-transfer-guard.ts`**。放在 main/security，强调它是 profile 文件边界，不是模型调用前置；不依赖 `ModelGatewayService` 实例、safeStorage、任何真实 key、T10 包解析器或未批准 T01 canonical。所需内部类型可同文件定义，不复制公共 contracts。

拟定内部职责为 `withTransferLocationLease(descriptor, action)`：main 受信 descriptor、注入的 metadata/epoch/inventory owner、用途限定的实际对象绑定、固定失败、失效/释放及发布前检查。action 只能取得有限受控 I/O 能力；**只把 `{path, assertSafe}` 传给任意 FS action 不足以落实此合同**。若当前平台无法提供所需能力，则只实现和验收 metadata 决策/失效核心，相关真实 I/O 操作保持拒绝，不包装成完整 lease 已交付。

可独立开发的验收是：严格 descriptor/none、双向范围、prospective 后缀、私有 inode/预算/不完整状态拒绝、profile/request/revision 变化、绑定前零内容 I/O、复验失败停止后续调用，以及受控能力不泄漏/不可复用。这些可以用注入 owner/FS port 检查，但只能算模块证据；真实 owner 元数据与 actual FS/入口、源/包联验另按 X1–X6。

若获准实施，另建议登记专属新测试 `tests/unit/i06-transfer-location-guard.test.ts`；真实隔离组合证据可另申请 `tests/i06-transfer-platform/`。**本轮均未创建，注册前不写 guard 或测试。**

独立核心不能自行解决以下现有文件/外部依赖；也不能先写旁路绕过它们：

| 后续变更位置/owner                                                                   | 必须先冻结的接口或责任                                                                                                                                   |
| ------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| I06 `model-gateway/private-directory.ts` 及三个 repository 的协调 owner              | 全根 metadata inventory、启动闭合性、文件生命周期/锁/退役协议；现文件未经本次授权不改。若采用新 inventory 子模块，须另登记精确路径，不暗加第二份可变权威 |
| I06 `apps/desktop/src/main/index.ts`                                                 | 可信 guard 构造、有限 transfer 路由、请求/profile/项目代次及 receipt 消费；由原 owner 代改或精确交接，不由本子任务改                                     |
| I06 `apps/desktop/src/main/task-service.ts`                                          | 目前只拟复用已有回调；仅在 receipt/代次不能由 main 协调层证明时提出精确必要 diff，不把其现有函数当验证器                                                 |
| T10 `apps/desktop/src/main/project-transfer/`、engine `transfer/` 与其 renderer 服务 | guard-before-IO、能力消费与 reopen 禁止、清理/发布/失败状态、真实入口/载荷与范围 UI；T10 给具体 diff，本线不抢写                                         |
| T01 canonical/main-engine/Python Store                                               | 唯一投影/读取能力、writer receipt/CAS/版本与有限错误；本线不写或采用未批准候选，不再造协议/DB/导入 writer                                                |
| T03 构建四文件、平台安全原语                                                         | 只有确需新增平台依赖/打包支持时另行精确申请；本设计不引入 native addon、不改构建/锁/CI/安全恢复                                                          |

请先登记 guard 新路径及完整 metadata owner/锁/失败契约，再冻结 T10 调用点和 T01 receipt。单独实现 metadata guard 可推进独立准备，但在这些缺口未闭合前不得启用真实转移或宣布 X1–X6 通过。既有状态以 [I06 status](../../reviews/I06/status.md) 为准；本轮只验证本文格式与 diff，不启动产品、容器、GUI、平台探针或原矩阵。
