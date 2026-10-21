# T01 固定源码：生产位置/native 消费切点静态调查

2026-10-21。结论：固定 T01 源码具备同连接 Store/Job 事务与路径型 writer lock，但没有在首次 IO 前接收、消费或撤销真实位置能力的入口。新增 main 检查后继续原路径 open，不能满足物理绑定。备份的多次 reopen、SQLite 内部 sidecar、连接与锁的失败关闭，以及原 dispatch 与当前许可的分离，都必须由 T01 消费实际供方合同。以下仅是接口请求，不实施或批准这些改动。

## 1. 固定来源与调查边界

- 本轮授权已全文读回：仓库外 `I06-native-location-supplier-plan-preparation.md`，5447B，SHA256 `15d40bf0046f68f6a1d757bc0e05ea6f38c16be16dc0e20739827c2e7a19a18f`。
- 创建/resolution 合同全文静态读取自 `379916267e5c36eebedb44d35a6636b9915ccd70:docs/iterations/T01/project-create-and-resolution-contract.md`，39602B，SHA256 `ff725f2c0ee40cbdf61c9c4d27dfea1be3ccd2068df4399878b037976de4a5f3`，下称 C。
- 实现只读取固定 `423b7e4c799f188cf2ce6e8e7121893ce85624cd` 的 Git blobs，下称 S；没有把 T01 当前可变 worktree、未来 C2/dispatch 方案或后续代码当已批准实现。
- 本报告为 B-M 树中新 docs；不修改 B-M 冻结原件、A、e2c/961、T01/T03 产品、测试、配置或依赖。未 import/执行产品、测试、构建、native 编译或实验，没有网络、GUI、凭据、子进程产品启动或 Goal 操作。静态读取使用 Git；bytes/SHA256 由固定 blob 计算。
- 引用 `S:路径:行` 均对应上述完整 S ref，`C:行` 均对应上述完整 C ref。行范围只帮助定位，不声称运行验证。

| S 中固定路径                                                        | bytes | SHA256                                                             |
| ------------------------------------------------------------------- | ----: | ------------------------------------------------------------------ |
| `apps/desktop/src/main/index.ts`                                    |  6928 | `8578e7461d82bcde08bdaf115990630f3fae12ec1fd1bb8154c84132441e3bf1` |
| `apps/desktop/src/main/engine.ts`                                   | 26260 | `6d55774068ca27a49958daeea9f4b1fa15614c95563ca28b8a768265ecd4365e` |
| `apps/desktop/src/main/task-service.ts`                             | 35857 | `4a14a1171e2562c4b61f3ad48484d2e1ffec22ce41865023b876440efb829b70` |
| `packages/engine/src/ontolearn_engine/__main__.py`                  |  3469 | `dae8f978a8cadc22dcc9f57b1e8a5e46cc760636192e45a2822aa47ab13b4684` |
| `packages/engine/src/ontolearn_engine/coordinator.py`               | 41168 | `6e057cbdd76c674813d9f90e231306cb9cf5611ef7fcbeb234de13d698afa18c` |
| `packages/engine/src/ontolearn_engine/storage.py`                   | 76042 | `fbef0d0ace0a01b9ced5eaecaf83aeb9306258c0cbfa5fd98a6d79e46bc5a39a` |
| `packages/engine/src/ontolearn_engine/job_store.py`                 | 87227 | `8896c3e30007e1dec04eaf47ae5bb5c33a1e9b3a1d016cb9165f99d8b4deeacc` |
| `packages/engine/src/ontolearn_engine/project/format3.py`           | 32169 | `505d0beb124534b2ab2e6c1716df53ef7b8108bedb57f5300fcb79a68e955782` |
| `packages/engine/src/ontolearn_engine/project/project_lifecycle.py` | 20932 | `a43365c1615082a0229de0d8e48569227fa930a7c3a7f869360975d72f30d104` |
| `packages/engine/src/ontolearn_engine/project/project_host.py`      | 15777 | `a142d9dc9e3c56c51110fd21125c65cc72a19631743be92ccf2e8be98da4edeb` |
| `packages/engine/src/ontolearn_engine/process_environment.py`       |   741 | `9a1d305201576cc6cdefa06e89f24b308049d597fd5cb04be950a28eae2f5ef5` |
| `packages/engine/src/ontolearn_engine/worker.py`                    |  9314 | `2fa848aa3a2148e59a24f01c9333701f0f03eed95cffe55a0a78b74f1d06f2f0` |

## 2. root → main → child 的实际来源

这里的 root 是可信应用位置/父目录来源，不是用户自报的路径或逻辑项目 UUID。

| 固定调用点                                                      | 已有真实事实                                                                                                                                                                                   | native 合同消费缺口                                                                                                                                                                   |
| --------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `S:apps/desktop/src/main/index.ts:91–130`                       | 受 launch argument + 同值环境变量限制的 fixture 可供 databasePath；正常路径为 `join(app.getPath('userData'), 'engine.sqlite')`。business3 仅 unpackaged 且显式内部开关选择，正常默认 legacy2。 | userData 字符串不是稳定 appData 控制根身份、安装 instance 或 fresh 证明。没有真实 root/parent/member 能力参数。不能由 ENOENT、当前可写或 fixture 推导首次安装。                       |
| `S:apps/desktop/src/main/engine.ts:121–165`                     | `SupervisorOptions` 接受 `dataPath` 字符串；过滤环境后显式设置 `ONTOLEARN_DB_PATH`、allowedProjects、testMode。                                                                                | 环境路径和项目 UUID 列表不能承载不可伪造位置权。须由可信 main 持有用途能力，并由受限跨进程传递机制交实际 child 校验；具体句柄/通道仍待 native 主方案冻结。                            |
| `S:apps/desktop/src/main/engine.ts:382–429`                     | main 读取同源 registry 原始 bytes，校验 parsed registry 并 SHA256；business3 为 DB 同父目录生成随机 `.t01-backup-UUID.sqlite` 路径；`spawn` 仅三个 pipe。                                      | registryHash 只证明协议资源，不证明库物理对象或 SQLite ABI/VFS。当前 stdio/env 没有 DB/backup/parent 能力传递或验收回执；随机名不是受保护候选对象。                                   |
| `S:packages/engine/src/ontolearn_engine/__main__.py:9–26,55–68` | profile/backup argument 做有限解析后进入 `serve(profile, backup_path)`。                                                                                                                       | 只检查绝对路径，没有实际用途能力、对应 child/Store 实例或撤销代次校验。应在任何位置 IO 前消费真实传递物，而非 connect 后补验。                                                        |
| `S:packages/engine/src/ontolearn_engine/coordinator.py:835–845` | 建 session 临时目录，取 env DB 或临时 fallback；先 `parent.mkdir`，再 `JobStore(database, target_format, backup_path)`，返回后执行 `reconcile_jobs()`。                                        | parent 创建已是实际位置操作；缺失能力不能回退到任意 env/default path 继续生产 IO。DB/锁/备份及初始化写用途须在这些动作之前接纳。fallback 临时库仅是源码既有行为，不是生产新位置授权。 |

在 S 的 main 与引擎源码中静态搜索未发现 `getPath('appData')` 控制根装配、安装 fresh 来源或 `requestSingleInstanceLock`。此结论只覆盖本次固定源码范围；不据此断言所有安装器都不存在。生产控制根/历史来源与唯一安装级 writer 的可靠供方仍须 T01/安装 owner 明确交付，不能由 I06 在本报告建立第二意图账本补足。

## 3. Store/SQLite/备份的真实 IO 顺序

| 实际切点                                                            | 顺序与物理消费                                                                                                                                                                                                                                   | T01 必须消费的精确用途                                                                                                                                                                                                                      |
| ------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `S:packages/engine/src/ontolearn_engine/job_store.py:67–80,99–115`  | legacy2 先按 `str(path)+'.writer-lock'` 以 `a+b` 打开；Windows 读首字节，必要时写入并 flush 后 `msvcrt.locking`，POSIX 用 `flock`。business3 不重复取得此锁，委托 Store。                                                                        | writer-lock 本身的 open/create/read/write/lock 都须绑定核准 parent/member 和进程 owner；同名旁文件、路径可写或锁成功不证明 DB 与锁是核准对象。不能为另一 DB 别名生成第二把独立锁。                                                          |
| `S:packages/engine/src/ontolearn_engine/storage.py:80–94`           | `Path.exists/stat` 检查旧库；explicit3 再调用 `acquire_lease` 并重新 stat；随后 `sqlite3.connect(self.path, isolation_level=None, timeout=5)`，设置 foreign_keys、synchronous=FULL 并迁移。                                                      | 从 metadata 到首次 header/catalog/schema IO 必须保持同一物理对象绑定；存在性/size 不证明 fresh。当前 connect 是路径 open，没有 fd/capability/VFS 消费参数；native 能力必须进入真实 SQLite 打开路径。                                        |
| `S:packages/engine/src/ontolearn_engine/project/format3.py:128–151` | explicit3 按相同 writer-lock 路径 open 并持有 OS 锁，声明从不 unlink；Windows 同样读/写/flush 首字节。                                                                                                                                           | 保留原锁协议的兼容需求，但需要 native 对实际锁对象/别名/撤销与连接持有关系的认证。不能仅改 lock 文件名或看到旧 PID 不在就释放。                                                                                                             |
| `S:packages/engine/src/ontolearn_engine/storage.py:148–184`         | 读真实 user_version；format3 既有库必要时备份，再进同连接事务，重新读版本并核源 logical_hash。                                                                                                                                                   | migrate/read-only reopen/create 是不同用途；已有 schema/逻辑源 hash 验证继续复用，不充物理身份。首次读取发生在迁移决策之前，不能等发现需迁移才请求首 IO 权。                                                                                |
| `S:packages/engine/src/ontolearn_engine/project/format3.py:158–187` | `target.open('xb')` 创建后关闭；第二次按路径 `sqlite3.connect(target)`；源连接 backup 到目标，integrity_check/logical_hash；关闭目标连接；再 `open('rb')` fsync；POSIX 再打开父目录 fsync；最后 `target.read_bytes()` 再读出 bytes 计算 SHA256。 | 需要目标候选独占创建、目标连接/SQLite sidecar、同目标 sync/hash-read、父目录 sync 的精确用途与同对象绑定。初次 xb 成功不能授权后续路径 reopen；后续同路径替换必须拒绝。源 DB 与目标 backup 能力分离，不能把 backup 当 source write 通行证。 |
| `S:packages/engine/src/ontolearn_engine/storage.py:1654–1661`       | 普通 `backup(destination)` 先 exists 检查，再另开 SQLite 目标连接并 backup，finally close。                                                                                                                                                      | 这是另一条实际内容 IO 入口，也须受目标用途能力约束；只拦 migration_backup 会漏掉它。当前 exists→connect 不是原子独占创建证明。                                                                                                              |
| `S:packages/engine/src/ontolearn_engine/storage.py:119–146`         | 唯一 `_transaction` 在同连接上嵌套 SAVEPOINT 或外层 BEGIN IMMEDIATE/COMMIT/ROLLBACK；after_commit hook 可在已持久化后失败。                                                                                                                      | 保留唯一 Store 事务权。能力/撤销需定义何时停止新接纳、已接纳事务如何真实收口，不能把响应丢失或等待取消当 rollback。                                                                                                                         |

S 未显式设置 `journal_mode=WAL`、调用 WAL checkpoint，或注册自定义 SQLite VFS；也未找到 DB/backup 的物理 `rename`/`os.replace` 发布调用。SQL 字符串 `replace` 及 workspace 的 dataclass `replace` 不是文件更名。因此不能报告“当前 WAL/SHM 或原子更名发布已实际通过”。

SQLite 连接内部仍可能请求 journal/WAL/SHM、锁与临时文件；具体实际请求取决于库与运行模式，本次没有执行确认。native 合同必须覆盖其同 build SQLite 的真实 open/access/delete/lock/SHM/sync/close 消费面，按实际用途拒绝越界，不能只拦 Python 可见的 `open()`。若未来方案引入 candidate→发布更名，须另冻结真正执行者、源/目的 parent 能力、排他与同步顺序、失败后 retained 对象；不得把本次未有的调用写成现成接线。

`sqlite3` 是 S 的 Python 导入，连接调用没有显式 VFS 注册/选择。独立 Node native 库即使也链接 SQLite，也不能据此推定注册到了 Python 使用的同一 SQLite 实例；同 build ABI、库实例及真实 xOpen 拦截证明需 T01 消费层与 T03 构建层联合交付，本次没有 import `sqlite3` 或读取运行版本冒充该证明。

## 4. 实际持有者、关闭与 ready 边界

- **main Supervisor 是 child/stdio 持有者。** `S:apps/desktop/src/main/engine.ts:93–109,439–487` 的 Session 持 child、reader、pending、timer；`328–353` 的 finish 先标 terminal、拒绝并清 pending，再 kill，并在 1 秒后可能 SIGKILL；`366–371` 的 stop 同步返回。`637–691` 的 timeout 只删 pending/reject，真正发送在 stdin.write。现无 `stopAndDrain`、永久关闭聚合 receipt 或原 dispatch 物理 binding。request/startup Promise settled 不证明 child/stdio/锁已结束。
- **main 退出没有等待真实收口。** `S:apps/desktop/src/main/index.ts:20–25` 调 tasks.dispose 和 supervisor.stop，没有等待资源终态。未来 T01 需按正式生命周期合同封新接纳并等真实 child/Store/VFS/锁终态；不能靠隐藏窗口或扩大本报告范围实现。
- **Python Coordinator 持 JobStore，worker 不持库。** `S:packages/engine/src/ontolearn_engine/coordinator.py:129–145` 持 store/active/tasks；`592–618` 启动 worker，仅发 capability/parameters/memoryBytes。`process_environment.py:7–33` 的 allowlist 不转发 DB_PATH/项目权；`worker.py:1` 明确 isolated test workload、无数据库/项目路径。不要把当前 worker 当第二 Store 或把位置能力自动下发 worker。未来新增有库 IO 的 worker 是新合同。
- **Coordinator 的内部真实排空可复用，但不是 main 的关闭证明。** `S:packages/engine/src/ontolearn_engine/coordinator.py:733–760` 取消/失败分支 terminate/kill 并 await worker.wait，stop cancel/gather tasks；`906–925` 再尝试 Store close、signal restore 和临时目录 cleanup。`900–905,934` 还明确 reader 可能未 settled，返回仅内部观察，不是 wire ready/cleanup receipt。SIGKILL 也可能截断该清理。
- **Store/JobStore 拥有连接与 writer lease。** `S:packages/engine/src/ontolearn_engine/storage.py:38–47,102–117` 和 `job_store.py:85–126` 按已转移所有权尝试各 close，并保留 cleanup failures；这是实际错误来源，不能抹成成功。现 helper 即使 database.close 失败，仍继续尝试关闭 writer lease。native 消费层须防止“连接/SHM 尚未知而 writer 仲裁已当可重用”，聚合所有真实资源终态并保留 unknown/retained，不凭异常已返回清空名额。
- **协议/Store/Job ready 不等于位置许可。** `S:packages/engine/src/ontolearn_engine/coordinator.py:114–120,839–854` 在 Store+Job 初始化/对账后用内部 `_JOB_READY` 接入 business3；`engine.ts:493–509` 的 hello 与 registryHash 认证完成传输启动。它们不证明 fresh、库 physical binding、当前 library/project scope 或 native 句柄。TaskService 的 `S:apps/desktop/src/main/task-service.ts:75–120` 是视图/项目 generation 与可信选择缓存，不是物理库权威。

普通同 Supervisor 的短 session 断开/重连，不自行等同新项目或清 model grant。native 旧传输能力不能凭同 UUID/同 SHA 复活；新会话的合法接纳、原已持久受理操作的只读对账与永久 owner 关闭须分别定义，不能把 session-ready 当永久资源收口。

## 5. 与固定创建/resolution 合同的准确差异

C:18–29 明确一库多项目、逻辑 libraryEvidenceRef 不认证物理文件、当前许可/原来源/原 dispatch 是三个独立条件。C:35–45 的未来 `create_project_request` / `resolve_operation` 接口需已校验且同 lifetime lease 的真实 Store+Job 连接，scope 与原 binding 不由 renderer JSON 重建。C:150–184 要求 resolution 只读、当前许可重新核验、原 dispatch 能重新对应当前实际库；丢失或复制库不能返回 resolved。

S 的 C1 仅是内部事务机制：`S:packages/engine/src/ontolearn_engine/storage.py:456–500` 委托 creation 到 `project_lifecycle.commit`；后者 `1–5` 明示无 scope/physical dispatch/host resolution，`409–453` 接受 request/origin/readerLimits 并在同事务核原 claim，`471–533` 创建并读回真实 genesis/claim/receipt。`103–106` 的 library_evidence 只 hash SQL migration_id。即使这些内部验证完整，也不能补造 C 所要求的外部位置授权。

现有 `ProjectHostReader` 可继续作为已许可连接上的只读投影：`S:packages/engine/src/ontolearn_engine/project/project_host.py:73–97` 不另开库，其 close 只清自身内存；`141–152` 拒绝加入未知活动 writer 事务。未来应由 T01 host 入口在它读取前核真实 current scope，不把 reader `_ready()` 的“未 close”判断误认成生产许可。无需因 native 方案复制第二 reader、第二 Store、第二 canonical 或重写 immutable receipt。

## 6. 交 T01 冻结的最小接口需求

以下为必要语义与准确消费位置，不是已实现 API 名，也不在本轮授写权。T01 仍唯一维护 shared main/engine/Store/worker/canonical；I06 提供私有位置/native 用途合同，T03 维护其构建闭包。

| 待冻结的私有接口语义              | T01 最小消费位置                                                                                                        | 必须交付的事实/拒绝分支                                                                                                                                                                                                                       |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 可信 bootstrap/location handoff   | `main/index.ts:120–130`、`engine.ts:121–165,409–429`、`__main__.py:9–26`、`coordinator.py:835–844`                      | main 预接纳先于 spawn/位置 IO；用途、root/parent/member 实际身份、profile/process/cohort generation、接收 child/Store owner、撤销与预算真实绑定。跨进程句柄资源须实证接收，不用环境字符串 bearer 或通用 callback。无 binding 不进入生产路径。 |
| 同 build SQLite open/sidecar 消费 | `storage.py:80–94`、`job_store.py:67–80`、`format3.py:128–151`                                                          | 唯一 writer/连接与真实 DB 物理对象绑定；原生 VFS 在首次 header/catalog 前接收用途。精确 sidecar/lock 由核准 DB 派生且受同 gate；错误 identity/别名/替换/reparse/ACL/撤销拒绝，不能路径重开失证。                                              |
| backup 目标生命周期               | `format3.py:158–187`、`storage.py:1654–1661`、`engine.ts:416–418`                                                       | 每次 create/connect/read/sync/close 对应同一已核目标，绑定 source 与 backup purpose，目标对象独占且保留未知。父目录 sync 与未来物理 publish 如需实现须有真实执行原语。                                                                        |
| 原 dispatch 的不可伪造关联        | `engine.ts:637–691` 的真实 stdin.write 边界、coordinator 的服务接纳、Store 事务入口；将来 host create/resolution 薄适配 | 将原 operation/requestHash、原 host/session/generation、已许可 Store 实例、实际库 identity 与真实发送/接纳关联。发送前 gate 不被 await 窗口绕过；当前许可与原归因分离。未捕获不能事后从当前 Store/SQL 行合成，不自动重放。                    |
| 撤销/永久排空及 retained receipt  | `engine.ts:328–380,424–487`、`coordinator.py:733–760,888–934`、`storage.py:38–47,112–117`、`job_store.py:117–126`       | 新接纳先停止；所有实际 child/stdio/SQLite/VFS/SHM/锁/候选资源逐项终态，含待 spawn、失败 init 和 close 失败。逻辑 timeout/cancel 不释放实际名额。ordinary session recovery 与永久 stop 的 owner 寿命分开。                                     |
| 当前库/项目 scope 与只读 recovery | 未来 T01 host wrapper，复用 C:35–45,150–184 以及现 `project_host.py` / C1 creation core                                 | 库 catalog/create/receipt-read 和单项目 read/write 分开。resolution 当前 scope 与原 dispatch 对应都充分才 resolved；复制 A→B、错代次、旧能力、来源/物理绑定缺失保持 unknown 或权限失败。                                                      |
| appData 控制根/fresh/历史来源     | T01 bootstrap 与安装供方；当前 `main/index.ts:127` 只能提供 userData 字符串                                             | 提供稳定安装 instance/根对象与历史迁移来源、安装级唯一 writer、可信 fresh 与缺失来源策略。没有真实来源继续 unknown；不新增 main 项目/Job 持久意图账本，不扫描全盘、不要求删除历史来“恢复 fresh”。                                             |

精确类型、能力发行/传递/撤销原语、SQLite 同 build 接法及新私有 adapter/test 路径，需要根与 T01/T03 在正式实施前共同冻结；本报告不凭当前接口缺口擅设 SQL API、通用 IO callback、连接工厂或新协议。若需改 canonical/旧 tests/build/锁，必须各 owner 列实际路径与必要 delta 单独获批。

本次仅交静态来源与缺接口。没有运行证明连接关闭、锁释放、WAL/SHM、macOS15/Win11x64、native fence、生产 ready 或父功能通过；B-M 临时目录 metadata 的阶段结果不能替代这些证据。
