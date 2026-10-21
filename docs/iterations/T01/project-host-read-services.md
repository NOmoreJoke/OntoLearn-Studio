# 可信项目宿主：私有一致读取服务

本阶段消费可信宿主持有的真实 `JobStore(target_format=3)` 连接，提供完整目录冻结分页和指定编辑器的工作区读取。唯一新增实现为 `project/project_host.py`，真实 SQLite 验证为 `test_project_host_read_services.py`。不接收文件路径，不创建连接、库、迁移、公开身份、快照、checkpoint、权限或 RPC。

依据是总控 `T01-project-host-read-services-implementation-authorization.md`（7435B，SHA256 `0c96119b2038b1db0d74fc8466926f321c7ebee669cb8949876e417c9e580757`）。本树从批准 `5f910b52c69d86a1076b2032e5d3c63e715947f3` 开始，按固定清单逐项继承 48 个 `5de3fff8aa02c5d6e577938660e9362936d90550` 输入；本阶段不修改这些继承项。保护指南与共同指令分别为 `78df2825…a759`、`e437121a…b0`，不进入产品提交。

## 宿主责任与生命周期

`ProjectHostReader` 只能由真实 Store 的可信 owner 创建；传入 Store 对象不代表获得任何库级目录或单项目许可。owner 必须先持有对应库/项目的实际能力，并在 Store 所在线程串行调用；本模块没有跨线程、并发 writer、文件选择或 renderer 授权接口。

实际数据库读取先拒绝调用方已有事务，再用现有 `Store._read()` 开始一个 `BEGIN`，同事务核实际 `PRAGMA user_version == 3`、预算、历史和返回投影，最后 `ROLLBACK`。拒绝已有事务时不回滚调用方事务，也不暴露其未提交状态。配置的 target3 不能代替实际 header3。

目录后页仅访问已冻结内存，不读数据库、不续 TTL，也不重新授予项目权限。冻结后数据库正常变化不会污染旧页。Store 关闭、真实位置能力失效或宿主退出时，owner 必须先 `reader.close()`，释放所有目录并永久拒绝该实例后续调用；`close()` 不关闭 owner 的 Store。此为后续真实宿主必须接入的合同，本阶段未实现其 I06 生命周期或宣称真实位置许可就绪。

## 私有调用与完整 DTO

- `catalog_start(*, page_size=64)`：先冻结有限完整目录，再返回第一页。
- `catalog_next(cursor)`：消费一个单次游标，返回下一页。
- `catalog_cancel(cursor)`：取消当前游标对应的完整目录快照。
- `workspace(project_id, *, editor)`：读取该公开 UUID 对应真实项目及指定编辑器的完整有界草稿。
- `close()`：幂等释放本实例全部缓存，实例不能重新打开。

参数采用精确 Python 类型，公开项目必须是规范小写 UUIDv4；editor 必须是非空有效 UTF-8 字符串，编码长度不超过 512 字节。页大小为整数，不接受 bool、字符串或浮点。分页没有可改变项目、范围、偏移或页大小的参数；游标不成为身份、文件或写入能力。

每条目录行只含 `projectId/domainRevision/metadataVersion/metadata/operationSequence/checkpointRef`。完整 metadata 只含既有白名单 `name/templateRef/archived/mode/origin`，保留真实 null、名称、归档与模式，不从路径推断或补默认名称。同名项目以真实公开 UUID 区分，归档项目仍在目录。

页只含 `catalogVersion:1/snapshotId/items/total/offset/nextCursor`。所有行以公开 UUID 的 SQLite BINARY 顺序排列；total 是完整集合数量。空目录返回空 items、total0、offset0、nextCursor null，不创建缓存。末页 nextCursor null，并释放全部快照状态。

workspace 在相同目录行字段之外只增加 `workspaceVersion:1/inputSnapshotId/draft`。inputSnapshotId 与 checkpointRef 均来自既有真实证据，且与同事务当前领域、metadata、operationSequence 互证，不调用会写入的 `snapshot/_snapshot/project_get/public_project`。不返回完整领域事实、learningCurrent 或 assistanceAudit 数组。

draft 明确区分：

| 状态     | 完整投影                                                                                              |
| -------- | ----------------------------------------------------------------------------------------------------- |
| 未创建   | `editor/state:"missing"`，没有 generation、present 或内容字段                                         |
| 持久墓碑 | `editor/state:"tombstone"/generation/present:false/boundDomainRevision/contentHash:null/content:null` |
| 内容存在 | `editor/state:"present"/generation/present:true/boundDomainRevision/contentHash/content`              |

JSON null 是存在的内容，保留 present true 及 `digest(null)`；SQL NULL 仅用于墓碑。generation 来自真实持久 header，boundDomainRevision 是内容来源版本，不作 CAS。完整内容与存储 canonical payload/hash、当前 checkpoint 中的同编辑器状态一起验证，不截取文字或只返回 hash。返回值是解码的新副本，调用方改动不能改变后页或数据库。

## 完整证据与有限预算

目录检查 projects/public_projects/app_projects 的完整双向一一对应，而不是只靠 inner JOIN 隐藏缺行。同时使用现有 `format3.validate` 核 domain schema、所有既有 snapshot、外键/完整性、所有项目 genesis、连续混合操作账本、receipt/claim/计划、checkpoint、当前 domain/app 头和内容 hash；这不等于完整 Job context 对账。投影只在这些证据通过后读取；缺 mapping、缺历史/当前证据或损坏均失败，绝不修复。

现有验证器会解码未输出的领域、learning/audit 及历史内容，因此先在同事务通过 SQL count/编码字节 aggregate 对所有实际表预检，再调用验证器。不是仅用最终 DTO 大小代替内部边界。schema 名称取自 SQLite，动态标识符双引号转义；不插入用户给定表名或 SQL。

`ReadLimits` 是 frozen dataclass。每个字段只允许精确正整数并收紧以下默认硬上限，不能放大；单位与拒绝范围如下。

| 字段              | 默认硬上限 | 含义                                                                                       |
| ----------------- | ---------: | ------------------------------------------------------------------------------------------ |
| projects          |        256 | 完整库项目数量，超额整体拒绝                                                               |
| schema_bytes      |     131072 | sqlite_master SQL 的 BLOB 字节合计；对象另限256个、表64个、每表列32个                      |
| validation_rows   |      16384 | 所有实际表行数合计                                                                         |
| validation_bytes  |   33554432 | 所有实际表列转换为 BLOB 后的字节合计，NULL按0                                              |
| validation_work   |  536870912 | `validation_bytes实际值 × (1 + app_operations行数 + snapshots行数)` 的保守重复解码工作预算 |
| metadata_bytes    |       4096 | 完整 metadata canonical UTF-8 字节                                                         |
| identity_bytes    |        512 | editor/内部项目身份的 UTF-8 字节                                                           |
| draft_bytes       |     262144 | 指定 draft 原 canonical payload UTF-8 字节                                                 |
| workspace_bytes   |     278528 | 完整 workspace canonical UTF-8 字节                                                        |
| catalog_row_bytes |       8192 | 每条完整目录行 canonical UTF-8 字节                                                        |
| snapshot_bytes    |    1048576 | 完整目录行编码及数组分隔符字节                                                             |
| page_items        |         64 | 每页最大行数                                                                               |
| page_bytes        |     131072 | 完整页含字段、token及所有内容的 canonical UTF-8 字节                                       |
| snapshots         |          4 | 本 reader 同时留存的目录数；每目录至多一个活动 cursor                                      |
| retained_bytes    |    8388608 | 本 reader 的保守留存计费总额                                                               |
| ttl_seconds       |         60 | 创建开始到到期的绝对 monotonic 秒数                                                        |

留存预付费为每目录 `768 + 项目数量 × (catalog_row_bytes + 64)`，包括完整行上界、tuple/状态/token 余量；在验证/解码/冻结之前核余量，快照槽在数据库工作之前核验。留存计费不是精确 Python RSS 测量；其保证是有限可预测的保守逻辑留存，不是进程内存硬隔离。schema/row/byte/work 预检本身仍需 SQLite 扫描，未声称硬 CPU 截止时间。预算按 reader 实例计，可信宿主应按实际能力管理实例数量与生命周期。

页构造先核完整编码预算，成功才安装下一游标。游标为本 reader 私有随机不透明 token，绑定不可变完整目录、页大小、绝对 TTL 和下一位置；不允许重放或跳页，不保留无限 consumed-token 日志。跨 reader、伪造、旧页、已取消或末页释放后的 token 均失败。消费后后页构造超额会释放整份快照，不留半页或泄槽。首轮失败不安装缓存；容量不足不驱逐尚有效目录、不截断全集。自然过期在下一次目录管理操作时清理，`close()` 主动清理。

游标在本实例随机 reader 标识之外带有从1递增的固定宽度序号及256bit随机后缀，完整编码93个ASCII字符。序号从不回退或复用，失败页也消耗序号；到既有 MAX_VERSION（9007199254740991）时拒绝再分配需要后页的目录/页，但不阻止无需游标的完整一页读取。无需无限 consumed-token 日志，即便随机后缀固定重复，同一 reader 的历史游标也不能复活或覆盖活动快照；跨 reader 还核实例标识。随机源失败/返回非法后缀时安全 state，首轮无缓存、后页释放本次快照。

生产默认使用 `time.monotonic`。可注入 clock 仅供可信宿主/测试，不是 renderer 输入；非有限数值、巨大整数转换溢出、回调异常或时钟回退均返回安全 state，并清理已有快照。

这里只设有限工程拒绝线，不据此声称 Q5、性能、生产容量或真人选择验收通过。

## 错误与验证

错误统一为 `HostReadFault`，只含有限安全 reason：`input/state/structure/limit/cursor/expired/missing`。SQLite 原异常、路径、SQL、内容、stack 不成为返回 DTO。实际未来/回拨 header 和外部活动事务返回 state；证据不一致返回 structure；没有该公开 UUID 返回 missing。已消费/不存在游标为 cursor；本次实际发现过期活动游标为 expired，清理后重放为 cursor。

新测试直接调用真实服务和真实临时 Store3，使用 SQLite authorizer 实际禁止 INSERT/UPDATE/DELETE/DDL/ATTACH 等写操作，并比较读取前后完整逻辑 dump。负对照确认即便 INSERT OR IGNORE 不改变总行数，原 snapshot 写路径仍被 authorizer 抓获。PRAGMA 只放行必要只读种类，user_version 必须无赋值参数；同一 authorizer 的负对照证明同值3和异值4的 header 写都被拒绝，避免 iterdump 不覆盖 header 的证明缺口。完整事务 trace 验证工作区只有一次 BEGIN/ROLLBACK，目录后页不持有读事务。

验证覆盖多项目/同名/archived、freeze 后 metadata 与集合变化、实际 UUID 重开稳定、缺映射/悬空/错误头/snapshot/metadata/draft 证据、未创建/墓碑/JSON null/大内容/hash、跨 reader/伪造/单次游标、绝对过期/取消/末页、槽/总留存/行/整份/页/工作区预算和后页失败、外部未提交事务、实际 header 0/2/4 拒绝。首轮损坏 fixture 曾被已有 immutable trigger 拒绝；只在新测试 fixture 中临时移除并按原 SQL 重建触发器再制造损坏，保留首轮失败原件。

逐命令实际结果、环境恢复、独审意见及冻结输入见本阶段 `docs/reviews/T01/project-host-read-services/`。后续创建/resolution 的精确设计见相邻 `project-create-and-resolution-contract.md`，本阶段未实现其写入口或公开接线。

原 T01 完整范围、44项映射与未闭验收保留在固定 `427ba7da6cc51016e98c15347e8b91a63f2c9232` 的 `project-host-integration-next-plan.md` 和根授权中。FR-001–006/804、四入口、T09完整内容、真实位置能力、编辑/Agent/全恢复/学习、指定同版双审、CI、正常 develop 合并和远端验收均不因本服务完成而被删除。当前阶段不申请 push/PR/merge，也不改变已有 Goal。
