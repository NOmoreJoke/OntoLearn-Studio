# I06 B：真实保护资源供方与排空准备方案

2026-10-21，**仅文档、待逐阶段批准**。建议先做独立真实 metadata 观察供方，再做持久保护记录和实际操作排空；不整包采用旧网关，不把 A 的 synthetic complete/publish 或 native Promise 品牌升级为生产授权。当前 `productionAdmission` 仍为 `unsupported`。

## 1. 固定来源与本次边界

本次文档起点为 `6a38fcb8135343ba5e62a8a8effe57b18c3de00c`，树 `.worktrees/I06-project-inventory-lifecycle`、分支 `feature/I06-project-inventory-lifecycle`；批准产品基线仍 `5f910b52c69d86a1076b2032e5d3c63e715947f3`。6a38 四产品/测试及其全部原证据、e2c、961 均冻结。只新增本文和 `docs/reviews/I06/project-inventory-real-owner-B-plan/`，不创建代码树、安装、import/执行产品、测试或真实运行 IO。

已全文读取 4183B/SHA `869e9c9568a52776b212238506700735b58de3b15cd709941b99d294cd8264c9` 本轮指令、固定 1f3 的 46365B 位置/cohort offer、12219B 根 offer 复核、7045B A 授权、13636B A 根读回及 1791B 收口。offer 的工具截断段已单独补读。最新 AGENTS/common 及实际交接记录按当前字节读取，不用历史 ownership 覆盖 T01/T03。

完整逐路径 ref/blob/bytes/SHA 在[52 项输入清单](../../reviews/I06/project-inventory-real-owner-B-plan/inputs.json)；e2c 原始实现的 metadata 和 lifecycle 事实分别由两名 agent 静态读取，报告不包含运行结论。本文的接口、路径和测试均为**实施申请**，不是现成 API 或当前可写范围。原 FR-001/002、901/902/904、57 项 P0、父 I06/FR-002 和原 Goal 维持。

## 2. 最小可独立推进阶段

所有未来代码阶段应从核验后的批准 5f 建独立树/分支；批准基线若变化，先重列实际接口与 delta，不沿用本方案假装已批准。以下具体名称是建议，不创建目录或分支。

| 子阶段                   | 建议树/分支                                                                  | 唯一 I06 产品与测试申请                                                                                                                                                                                                                     | 能证明的退出结果/前置                                                                                                                                                                              |
| ------------------------ | ---------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| B-M 真实 metadata 子集   | `.worktrees/I06-real-private-metadata` / `feature/I06-real-private-metadata` | 新 `apps/desktop/src/main/security/private-resource-owner.ts`；新 `tests/unit/i06-private-resource-owner.test.ts`；精确采用下表 A inventory/专属测试两件                                                                                    | 从受控临时目录实际枚举 I06 私有根、所有后代/残留/pending，真实 metadata 和未结束 FS 操作记账；不调用内容仓库；不合成任何缺席 owner。全应用 inventory 仍 incomplete/unsupported，无宿主接线或写凭据 |
| B-R 持久保护来源         | `.worktrees/I06-private-retirement` / `feature/I06-private-retirement`       | 新 `apps/desktop/src/main/security/private-resource-retirement.ts`；新 `tests/unit/i06-private-resource-retirement.test.ts`；B-M 供方仅在其冻结并获精确采用后消费                                                                           | §5 格式、唯一控制位置、所有权及真实有限写路径另批；临时目录恢复/损坏/崩溃边界可独立验证，不执行模型/项目内容 IO；跨进程仲裁/OS 耐久未证时仍 unknown                                                |
| B-L 实际操作与模型持有链 | `.worktrees/I06-real-model-drain` / `feature/I06-real-model-drain`           | 新 `apps/desktop/src/main/security/private-operation-lifecycle.ts`；新 `tests/unit/i06-private-operation-lifecycle.test.ts`、`tests/unit/i06-model-cohort-drain.test.ts`；§3 所列仓库/模型路径分别批准；A cohort 与必要最小修订须另列 delta | 先独立实现内部 pre-admission/真实完成槽，再分仓库应用；完整网关运行消费须 T01 canonical/dispatch/资源终态前置，不能靠假 Engine 实现通过联验                                                        |
| T01/C/D/E 后置           | 不在 I06 建代码树                                                            | main/index、engine、task-service、Store/worker、canonical、native/VFS/build/公开桥/UI 均不在本次或 B-M/R/L 自动窗口                                                                                                                         | 真实所有权覆盖、首 IO fence、同 build VFS、两目标 OS、实际主指针/ready/许可与公开消费另批；B 不能解除生产 unsupported                                                                              |

每个实施阶段的说明/证据建议分别为 `docs/iterations/I06/real-private-metadata.md` 与 `docs/reviews/I06/real-private-metadata/`、`private-retirement.md` 与对应 review、`real-model-drain.md` 与对应 review；均须随阶段精确授权，不由本文变成新写权。现有测试一律只读，新测试使用各自独立临时目录/依赖/日志，不借其他树环境。

### 2.1 现 A 四件完整采用决定

| 6a38 文件                                                      | SHA256                                                             | 后续采用建议                                                                           |
| -------------------------------------------------------------- | ------------------------------------------------------------------ | -------------------------------------------------------------------------------------- |
| `apps/desktop/src/main/security/private-resource-inventory.ts` | `0f6a2125d5dea53b5e5badde99401086284d4fd776b0cefadad324e408c786e5` | B-M 逐字采用；仅接收其真实私有子集，缺 T01/profile/retirement 来源不补 synthetic owner |
| `tests/unit/i06-private-resource-inventory.test.ts`            | `7d82c1012bbe7fc35c5faf6eaf167b82d93a357e0b1060db6256ba809a118f49` | 随 inventory 精确采用；仍是合成机制回归，不能算真实 FS 证明                            |
| `apps/desktop/src/main/security/project-cohort-lifecycle.ts`   | `bcbb73449395757b0cb6260b1299366e1a25de5bcc16c161f145a1f7674fcdb9` | B-M/R 只读；B-L 获批后逐字起点，§7 修订单列，不直接依赖整 6a38 commit                  |
| `tests/unit/i06-project-cohort-lifecycle.test.ts`              | `f90dd23b6f30e4e641197db6cb93a0fae4786948e489d4985b38f37ec0bf2fea` | 随 cohort 采用；新增真实资源测试另文件，不倒写 A 原件或历史通过                        |

不整 commit/cherry-pick 6a38 的 68 路径，不复制 e2c/961 的源码、环境、平台脚本或旧测试充当批准依赖。未来实际采用须核 5f→阶段候选完整差异，根逐路径确认。

## 3. e2c 最小闭包、采用理由与不能隐含采用的依赖

下列均固定 `e2c269ad78a78e1a042cadc93b1c81a874707153`，SHA 全表见附表。原 offer 的八条路径并非可单独复制运行的闭包。**B-M/R 不采用任何旧内容仓库/网关代码**；B-L 下表也须分批准确 delta，不能借目录授权整包抄入。

| 原路径（`apps/desktop/src/main/model-gateway/`） | 实际供方/必要改造                                                                                                                    | 建议采用窗口与唯一写者                                                 |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------- |
| `private-directory.ts`                           | 持目录/文件、mkdir/open/link/publish/close；所有实际 FS 开始前登记，元数据观察不复用 read/list 内容接口；吞 close 错误要保留 unknown | B-L 仓库第一批 I06；不是 B-M 的依赖                                    |
| `configuration-repository.ts`                    | journal 初始化 scan、append 与 close 供方；运行时 import source 的 canonical 函数意外拉入 engine/contracts                           | B-L 仓库批 I06，先批准解耦 canonical 的精确新路径与 diff               |
| `ciphertext-repository.ts`                       | 所有历史密文、pending、孤儿；open scan 在操作队列外，初始化先登记                                                                    | B-L 仓库批 I06，无 Keychain 的合成密文字节测试只能证明文件/排空        |
| `persistent-audit.ts`                            | 历史审计、pending 与 open scan/append；gateway import 是 type-only，不因此引入网络                                                   | B-L 仓库批 I06                                                         |
| `model-service.ts`                               | readonly engine、context、serial tail 及并发非 tail 调用；需要新 cohort 构造/接纳/排空                                               | B-L 模型批 I06，须 canonical 与真实 T01 供方                           |
| `gateway-application.ts`                         | source/projector/core/material/grant/active 持有链；void close 不是 drain                                                            | B-L 模型批 I06                                                         |
| `stored-result-source.ts`                        | 底层 RPC 与逻辑 abort 分离、实际 source lifetime                                                                                     | B-L 模型批 I06，T01 request/dispatch/后台 operation 完成合同到位后     |
| `stored-field-projector.ts`                      | 持 source 的间接链，必须重建和等待其真实请求                                                                                         | B-L 模型批 I06                                                         |
| `credentials.ts`                                 | 密文/加密边界及同步不可取消操作；Electron SafeStorage 是 type-only import，不强制 Electron runtime                                   | B-L 仓库/模型按实际闭包 I06；禁止用成功构造代 backend 可用             |
| `policy.ts`                                      | 仓库及网关真实依赖的私有 schema/固定错误                                                                                             | B-L 对应仓库批 I06；不复制第二 canonical                               |
| `gateway.ts`                                     | credential/audit boundedWait、grant/material 与 transport 的真实链                                                                   | B-L 模型批 I06，不能漏 underlying credential/audit                     |
| `transport.ts`                                   | request/response/socket 的真实终态；当前 sendOnce 结算不等资源 close                                                                 | B-L 模型批 I06；无模型网络测试的阶段不得声称此链已验                   |
| `await-boundary.ts`                              | 超时/abort 包装会早结算；保 logical outcome 与 resource completion 两条通道                                                          | B-L 模型批 I06                                                         |
| `electron-safe-storage.ts`                       | 实际 Electron app/safeStorage runtime 装配                                                                                           | 后续明确隔离平台窗口，I06 私有适配；B-M/R 和无 Keychain B-L 子阶段只读 |
| `finite-fixture-policy.ts`                       | 有限 fixture，不是真实模型/数据来源或生产 field model                                                                                | 全程只读来源；不采用为生产准备成功证据                                 |

配置仓库 `:11`→source `:3–7`→contracts/v2/errors + T01 `EngineError` 是真实运行时依赖。建议后续仓库批另批准新 `apps/desktop/src/main/model-gateway/material-canonical.ts`，仅移动原确定性序列化函数；同时明确修改 configuration-repository 与 stored-result-source 的 import，旧字节不覆盖。此举只解除无关 runtime 依赖，不改变 journal digest；等价旧/新 digest、边界 fixture 和依赖闭包均须实际验证，不在本轮实现。

model-service `:2–22` 的 Model*、modelGatewayError、validateModel* 在批准 5f 公共导出里不存在。不能复制 e2c canonical 七件、造私有同名 DTO/stub 或改用 any 解编译。T01 必须先给精确新合同/批准采用窗口；未到时完整模型批保持待实施。main/index、engine、task-service 当前唯一 T01，e2c 仅是旧调用图证据；不能把其 constructor/ready/stop 当现在已兑现接口。T03 source broker 与 pyproject/uv.lock/build-engine/entrypoint 四文件不转。

## 4. 完整保护资源与真实观察供方

### 4.1 八类 owner 与实际来源

| A 角色         | 必须提供的真实来源/登记者                                                                                  | 缺席/失败时结果                                                                          |
| -------------- | ---------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| profile        | T01 trusted main 的实际 userData、sessionData/profile 根及所有会写这些根的应用 owner；不是 renderer path   | 无真实根/写者清单则全局 incomplete；不以固定 userData/engine.sqlite 替可选位置           |
| private-root   | I06 在任何 mkdir/内容初始化前 reserve `model-gateway-private-v1` 整根及未来后代；未识别子目录/残留也不能漏 | 根缺失仅可记录有真实父对象依据的 prospective，不把任意 ENOENT 当空；初始化失败保 reserve |
| credentials    | I06 实际 credentials bucket、所有 final/pending/孤儿/未引用密文                                            | 不调用 decrypt/open 内容仓库来发现全集；Keychain 失败不清保护                            |
| configurations | I06 实际 configurations bucket 全部 journal 与 pending/未知项                                              | 当前 configurations[]/最后一条配置不是范围；损坏/权限/枚举上限 unknown                   |
| audit          | I06 audit bucket 全部历史及 pending                                                                        | 10000 是追加门，不是“恢复只扫前10000”；保留多余/异常项并 unknown                         |
| database       | T01 实际主库、WAL/SHM/journal/writer-lock、候选/备份精确组与原生 owner                                     | B-M 不造数据库 owner；已 release 的残留仍 retained，重新打开另取权                       |
| tasks          | T01 实际 worker/Store/临时写入资源及剩余任务持有，T03 源文件仅按其真实 owner 交有限观察                    | 不读文件 broker 当 DB 权；未知临时/间接写者不算完整                                      |
| retirement     | B-R 受控持久 metadata 来源，恢复旧 profile/private/DB 历史与未结算事实                                     | 缺失/损坏/跨实例冲突 unknown；不能由 fresh constructor 或 native Promise 自证恢复        |

private-root 记录直属非 bucket/未知项；三个 bucket 各自产生其真实后代记录。每一资源只由一个明确供方持有，不重复登记整文件来凑数量；上层根的 subtree deny 是后续原生策略范围，不是“列出根后 A 已认证全部后代”。retired owner 的记录和新 owner 的记录以进程/profile/资源 incarnation 区分，不能让同路径新 inode 冒充旧 id。

e2c 实际 final 名准入为 `[0-9a-f-]{36}` 加 `.credential`、`.configuration`、`.audit`，该文件名正则本身不是 UUID 内容验证，共用临时名 `.pending-<PID>-<UUID>`；它不是 final 名加后缀，PID 也不是释放证明。内容仓库的 names 先拒绝未知名，list 再过滤 pending，不能拿该 list 作为完整 inventory。metadata 供方必须按实际目录项完整观察，未知名、额外目录、symlink/reparse、设备和不支持类型都不能忽略。root/bucket 不存在、目录损坏、初始化未完成和文件存在但未引用必须分别表达；不为通过观察而删未知/pending。

### 4.2 B-M 观察及 mutation 握手

1. 可信装配者注入实际根描述，不接 renderer 字符串/UUID 或 `safe:true`。B-M 只在临时目录驱动中证明本 I06 子集；T01/profile/sessionData 全量登记未实现时不声称已接真实 app bootstrap。
2. 先获取已存在祖先的真实 metadata，分组件记录目标 prospective；同步 `reserve/beginMutation` 失效旧 revision/快照，再允许未来仓库的 mkdir/write/link/publish/cleanup。当前模型根创建前无该握手，必须改 writer，不能只在调用后扫描。
3. 供方内部唯一串行 gate 覆盖其所有写入和完整观察。每次原生/FS 操作先占有限真实槽，实际调用返回/资源结束才减槽；当前正在写的操作先结算，再开始只读全量观察。观察期间禁止本应用其他供方偷偷写；外部路径替换仍可能发生，Node gate 不冒充跨进程 fence。
4. 只使用 directory enumeration 与 metadata 调用，不打开配置/密文/audit/SQLite 正文、不 decrypt、不访问 safeStorage。对已知根完整递归，保留实际目录项精确名、parent、类型、volume/dev/fileId/inode/linkCount 及 observation 身份；POSIX 数值用无损 bigint 表达，不能经浮点截断。B-M Node 结果标 `node-observed-unfenced`，不是 native handle receipt。
5. A 的每 observation 5000ms、并发2、roots32、entries32768、depth128、路径UTF8 16384B 及捕获界全部适用；超额整体 unknown，不截断列表。旧仓库的11024目录项门、4096新增密文门和1024配置journal门不能取代全量保护上界。
6. 同一个 process/profileEpoch/revision 的全部 owner 才能形成机制 snapshot。一次 mutation 会失效其他 owner 观察，因此 B 装配者须重取全轮，不能把旧 roots 与新 bucket 结果拼接。缺 T01 owner 就保 incomplete，不以全是受控临时目录为由补空角色。
7. 当前存在的私有文件按同一观察边界闭合 distinct name 数与 links；final+pending 两名且 nlink=3 仍 unknown。目录 nlink 不冒充文件 alias 数；外部 DB 多链接策略由后续原生用途处理。旧 absent-retired 保路径/旧 identity，不计当前 links。
8. 新身份必须有新 incarnation id，原 id 不得偷换 parent/identity 或从 retired 还原 active；但**同一个 parent+components 被新 inode 复用时，仅换 id 不能满足当前 A**。6a38 的 resources() 对整份 payload 强制 locationKey 唯一，因而旧 absent-retired 与新 present-active 同址会被拒；完整 observe 又不能省略旧记录。B-M 明确将该形态保持 unknown，保留旧/新身份和保护，不宣称完成观察，也不删历史来绕过。§7 列出另批的最小 A 扩展；获批前它是可追溯的功能限制。移名、删除、发布失败同样保留全部已知保护。
9. 两次 Node metadata 相同只能发现一部分竞态，不能证明枚举过程中无 ABA，也不能让调用者随后 path reopen。C 未实现前，任何 SQLite/header/catalog/backup 首内容 IO 仍拒绝。
10. 当前 private-directory 在 win32 主动拒绝；Node `dev/ino` 不可伪装 Windows 完整 volume+128-bit FileId/reparse/ACL 证据。B-M 的 POSIX 临时目录结果限其平台；Windows metadata/native 另批实际 adapter，不永久把产品改为 POSIX-only。

## 5. 持久 retired：唯一控制位置、有限格式与损坏策略

这是 **B-R 新可变 metadata 的具体申请**，当前不创建文件。建议 trusted main 给出实际 `appData/知爻-OntoLearn-Studio/security-inventory-v1` 控制根；它独立于可变 userData，profile 移动不会丢旧根。路径各组件/所有者由可信安装/主进程确定并验证；控制根本身以 private-deny 保护且只读给内部 supply，不从任意 renderer 路径建立。准确 appData/应用身份与多安装并存命名须根/T01 在 B-R 实施前冻结；本路径建议不是已批准默认数据位置，也不是 FR-002 的用户项目位置。

唯一拟写集合：根内 `header.json`、`intents/<sequence20>-<recordId32hex>.json`、`seals/<同名>.json`，以及首次创建这三个已知目录。无覆写、unlink、truncate、replace、任意新子目录或自动 GC；不写项目 DB/Job/claims/业务索引。若旧根/文件冲突不占为己有或删掉重建。每文件使用 exclusive create，完整写入、必要同步、实际关闭并验证后才成功；seal 是独占的新记录，不改 intent。目录/文件创建和未知耐久结果同样登记/保留。真正 no-replace/掉电耐久/跨进程身份仍需 C/目标 OS 证据，B-R 临时文件验证不能解除。

**固定控制树的 bootstrap/self-append 是该 metadata 协议自身的唯一例外，不递归生成 intent：**只有根/T01 另冻结的真实受信 fresh 流程，才可先在内存预 reserve 实际已存在父对象与固定控制根/header/intents/seals 后，独占建立这些固定控制目录和 immutable header。bootstrap 期间禁止任何私有根、profile 或数据库目标 mutation；不解除目标准入。固定控制目录建立/同步、header 完整写入/同步/关闭与身份核验全部确认后，才进入“可追加控制记录”状态。partial、冲突、close/sync/identity 失败或首次来源不明均 unknown，保留原件，不当作 fresh 完成。真实 bootstrap 来源/原语未提供时，B-R 实施前置仍缺失，不能自行推断或承诺生产初始化。

已建立控制树内，按严格 schema/序号/exclusive-create 的 intent/seal **自身**追加由同一私有 writer 协议直接登记、计槽并自保护，不为每次控制记录写再生成上一层 intent；这项权限只限上述固定 metadata 名称与协议动作，不开放任意文件、通用 callback 或目录写能力。控制文件自身属于 deny inventory，实际追加前同步失效旧观察，实际终态/失败仍留在资源清单；所有其他目标仍按下面的先持久 intent+seal 规则，不享有 bootstrap/self-append 例外。

格式提案 `format:1`，header 含 installationInstance、控制根 identity、固定 format/limits；intent 含单调安全整数 sequence、recordId、previous digest、process instance、profile incarnation、有限资源数组（owner role、incarnation id、private/profile/database 类别、精确根定位组件、parent/旧 identity、present/prospective/retired、尚未闭合的持有事实）；seal 只含该 intent 精确 bytes/digest、sequence、实例关联。不得存 key/ciphertext/config endpoint/业务正文、Job意图/重放状态或模型 grant。digest 只做损坏检验，不证明来源可信或 OS 已释放。

建议有限门：32 根/32768 项与 A 对齐；单记录最多1MiB、总记录正文最多16MiB、最多1024 intent/seal 对，路径深度128/UTF8 16384B；对任一上界先拒绝新 mutation，不截断恢复。所有控制文件与 pending 的目录项计入全局保护预算，超额不绕 A 上限。这是保守工程提案，必须随 B-R 正式冻结，不是 Q5 决定或容量/性能承诺。

**持久化先于其他目标 mutation：**除上述固定控制树 bootstrap/协议自身追加外，新 profile/root、将要创建/移名/发布的目标和旧保护集合必须先成为完整可恢复 intent+seal，并取得所需耐久确认；两者确认前不得开始目标操作。目标实际完成再追加后继观察，失败/取消/晚完成只能追加原实例结果。任何 partial intent、孤儿 seal、digest/previous/sequence 不连续、重复实例/名称、权限/identity变化、未知版本或预算超限都 unknown，不重置空表；有效但未 seal 的记录亦保守保留，不能假定未有 IO。

跨重启先验证控制位置/文件身份、完整有限链，再 metadata 重观察全部旧根；旧 fileID/inode 不能永久复用为当前身份，真实句柄不可持久化。恢复的数据库记录统一 retained/unknown，不能根据磁盘内的“released”或进程 PID 不存在恢复 grant/release；需 T01/原生受控恢复另证真实进程和锁。只有明确可信首次安装/独占建立全新控制根且无迁移历史的流程可建立 fresh header；文件 ENOENT 不证明首次安装。来源丢失则原位置接纳保持 unknown，向根报告受控恢复缺口，不自动扫描全盘或要求用户删旧记录。

多 main 进程不可各写自己的序号链：正式 B-R 需要唯一安装级 writer 仲裁和控制根 identity，当前 JS map/按路径锁不充分。受控临时目录只证明单测试实例 add-only 机制；未获 native/目标OS仲裁前生产 B-R 不能自签“恢复已完整”。模型初始化和凭据是否可用均不能控制该来源的存在性。

## 6. 实际 underlying 寿命与排空供方

以下原行为按 e2c 静态追踪，均不是当前新能力：

| 链                                 | 当前实际缺口                                                                           | 未来先登记什么/只认什么终态                                                                                                                                      |
| ---------------------------------- | -------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 三仓库 open/scan/recover           | 初始化在 PrivateOperations 之外；内容扫描失败可晚 close，清理部分吞 close 错误         | 工厂调用前登记 initialization 与每实际 FS；返回实例前核 owner/cohort 仍 current；late instance 只关闭原实例。close 失败保未知 FD/资源，不以 open reject 当已释放 |
| PrivateDirectory/PrivateOperations | run 有32 Promise限额，close allSettled 只覆盖已登记工作；open/read 某些 close 异常被吞 | 所有内部 FS/目录/文件 handle 纳入同一 registry，init/observer/cleanup 不例外；真实 handle close 失败不转 released                                                |
| credential/audit                   | core boundedWait 可先超时/abort，底层同步加密或仓库 append/read 仍可继续               | 每原始操作独立资源槽；logical outcome 可先返回，资源 completion 等真实 read/append/sync/close；不触发本机提示来测试                                              |
| model-service                      | serial tail 不包含所有 catalog/preview/source 请求；close 只等 tail                    | 所有公开/内部 init/catalog/preview/invoke/context/source 操作统一 pre-admission，关闭先阻接纳、撤 grant/material，再排空全部实际链                               |
| application/projector/core/source  | application.close 为 void；source abort 可先 reject 外层并删 active                    | logical cancel 与 actual source 完成分通道；source engine.request 仍不证明 Python 后台已停；projector/core 所有间接引用要重建                                    |
| transport                          | sendOnce 的 settle 可早于 request/response/socket close；destroy 是请求关闭            | 发送前 reserve，记录每实际 request/response/socket 生命周期；终态需全部自有资源真实结束，不能只等 sendOnce/response end；发出的数据不能撤回                      |
| Supervisor/T01                     | request 可超时并清 pending；finish/stop 会 reject+kill，实际 child close 更晚          | T01 提供写帧前 guard、原 operation 真实执行结算和所有 child 永久寿命聚合；RPC reject、pending.size=0、kill 返回均不够                                            |
| Store/worker/native                | B 无这些实现/句柄终态权威                                                              | T01 唯一提供全部 worker、Store连接、SQLite映射/锁及 native lease 释放；B 不制造 OS released receipt                                                              |

供方内部区分 `logicalOutcome`、`underlyingCompletion`、`ownershipLifetime`，都绑定实际 owner/cohort/profile/process incarnation。生命周期开始前先 reserve 有限槽与保护，真正终态才释放槽。`abort`、5秒等待结束、map清零、包装 reject、`close()` 返回和 native Promise fulfilled 都不是独立 OS 证据。聚合 completion 只能由实际对象所有者根据完整真实资源集合结束，不能对外暴露 resolver/自报 count=0。

每个 cohort 的 engine/Store `ownershipLifetime` 表示整个永久拥有关系，覆盖同 Supervisor 曾创建/仍在回收的全部 child/连接，只有永久 stopAndDrain 且全部真实终态后才结束。单 transport session 断开/重连不结束该永久寿命；普通 view/同 engine 瞬断沿 T01 原恢复与 grant 政策。永久寿命在 candidate/active 结束则整组 quiesce；同 UUID 换 engine 对象必须新建 ModelService/Application/Source/Projector/Core、重新 local context，不沿用 readonly engine 或 grant。

private 根/仓库是 profile 级资源，可能被多个 retired/current cohort 暂时引用；不能用某组 close 删除共享根、关闭新组还在使用的目录或清新全局。profile owner 维持实际持有引用与所有未结算，cohort 只释放自己的引用；在所有旧引用真实结束前禁止迁移/复用同一资源 authority。0句柄仍保持久路径 deny。

## 7. A 接口不足与最小修订申请

**不修改 6a38。**静态反例不是本轮新运行测试：

1. cohort 测试 `prepare()` 实际只登记六角色和 fulfilled initialize/binding/ready，即可 publish；未登记 child/store-connection 寿命。原 A 已明确允许这种机制演示。B 绝不能据 publish 得出真实持有链完整。B-L 装配层必须持有真实 engine/Store owner 对象且在创建前登记必要永久寿命；若需要 A 强制机械检查，则只申请在 cohort publish 加“engine 的 child 与 Store 的 store-connection 已登记且仍 pending”的必要条件及两个反例，仍非 OS 认证。disabled-model 也不能省略两项。
2. `track(owner,'fs',fsCall())` 的实参在 track 运行前已启动调用；若 A 此刻 budget/stale 拒绝，操作已经在途。A 目前无操作 reservation/start 门。B-M 可在自己新供方内部完成预接纳，不向生产 cohort 发布；本方案选择 B-L 真实唯一 registry 的内部 reserve-before-start gate，不改 A。若将来统一跨供方预留确需 A 支持，再单独申请最小两步 `reserveOperation`→`attachActualCompletion`。预留即占全局/owner/kind槽，缺 attach/订阅失败保 unknown 槽，只有明确未 dispatch 的内部路径可撤未开始预留；已 arm 不得 timeout清槽。不得加通用 IO callback 或返回 LocationLease 的 scope factory。
3. A inventory 接收 caller 的 `status/retirementSource`，不能验证扫描真实或持久来源。B-M/R 不用新增 `trusted:true` 改 A；只让真实供方把有限观察映射到 A。原型/opaque/native Promise 品牌仅约束机制输入；B 实际来源和足量登记须由源对象、调用闭包及实测证明。
4. A resource 的 id 已绑 parent/identity 且 retired 不回 active，但 `private-resource-inventory.ts:213–220` 的 payload locationKey 唯一约束不含 presence/incarnation。静态反例：旧记录 parent=P/components=[x]/identity=A 变 absent-retired，新记录同 P/[x]/identity=B 为 present-active；即使 id 不同也整体拒绝，先 reserve 新 id 仍过不了完整 observe 必须带旧 id 的检查。B-M 在冻结 A 上一律 unknown，保留全部已知身份；不能以换 id 已足够、漏报历史或修改原 A 绕过。最小扩展申请仅改 `apps/desktop/src/main/security/private-resource-inventory.ts` 的同 location 分组校验及 `tests/unit/i06-private-resource-inventory.test.ts`：允许每位置一个 present 当前项与有界多个 absent-retired 历史项共存；继续拒两个 present 冲突、原 id 换 identity、历史转 active，维持全部历史、计数和 links 闭合（absent 历史不计当前 links）。实际正反例及新候选审查另批，本轮不实施，也不作为 B-M 获批的隐含修改。

必要 A 修订若获批，唯一修改仍为两 A 私有模块及其两专属测试的精确子集；新独立阶段树以 6a38 四件为明确输入，形成新候选/实际反例/重验/独审，不回写旧 A 报告。上述 reservation API 和 mandatory lifetime 检查须在实施前冻结状态转移，不能由 B-L 一边接线一边随意改 A。

## 8. T01 与 native 的精确前置接口申请

均为待 T01/root 逐路径确认的 main-private 合同，不是现有 API，不要求其接受未冻结签名。不得把 T01 新实现读取/fixture 当本轮正式依赖。

- **profile/bootstrap 来源**：由 T01 index 在模型初始化、目录创建、Store构造前提供真实 profile/sessionData、精确 DB组/worker资源 owner 及进程/profile实例；接受 I06 reserve/观察失败即不做该次新位置内容 IO。I06 不写 index。
- **request 完成与 dispatch**：T01 engine 在真实 stdin.write 前同步核原 cohort/currentness/真实 scope；分别提供逻辑 outcome 与实际后台 operation 终态。发送未发生可有限取消；已发送不靠 request timeout 当执行结束，未知按现 claims/context 只读对账，不造第二 Job/意图账本或换 operation 重放。
- **永久 stopAndDrain**：T01 engine 先永久停止新 spawn/request，聚合所有旧/当前 child 的真实 close 与相关自有管道结束；Store/worker 另聚合实际事务、连接、映射/锁、任务及原生句柄。带 source identity 的 receipt 不等同一个 Promise.resolve；发生 close/release 失败保 unknown/unsettled，不能用退出码替代全部其他持有者释放。
- **候选/发布消费**：T01 私建候选实际 Supervisor/TaskService、绑定未来原生 lease；同 child Store/Job/reconcile/hello 与库级目录/实际 project scope 完整成功后，I06 以该 engine 重建链或安全 disabled binding；同步主指针交换由 T01 唯一负责。B-M/R 不提供真实 ready/LocationLease。
- **C/native**：可信 root-relative metadata handle、跨进程 gate、精确身份/links/ACL/reparse、同 build SQLite VFS 与实际锁/SHM/child binding，不能由 Node stats 双检替代。Windows 及 macOS 均保留真实目标平台小阶段；T03 build/锁/源 broker 只提准确依赖 delta，不接管。

缺少任一供方只阻塞其消费层；不要求等全部父 I06 才做 B-M/R，但也不把 B-M/R 通过写成已取得真实首次位置 IO 权限。

## 9. 未来实际测试、冻结与本轮交付

下列全部是**待授权实施后的测试计划**，本轮只静态读取/哈希/文档格式检查，不 import 或运行这些接口。

| 阶段           | 必须实际输入/反例                                                                                                                                                                                                                       | 能证明/不能证明                                                                                                                  |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| B-M            | 每例独立受控临时目录：根不存在/父不存在/permission、真实 symlink/hardlink、同 inode final+pending+nlink3、孤儿/未知名、祖先/根 rename、目录超限、初始化失败前 reserve仍在、观察期间应用 mutation、真实未完成 FS 取消后仍占槽、close失败 | 真目录 metadata 子集与有限计账；不用 stub 替真实链接。可注入错误作补充但明确不是 OS close失败实证；不证明 native原子首IO/Windows |
| B-R            | 新临时控制根/旧根，exclusive冲突、截断 intent/seal、digest/previous/sequence错误、超额、缺失fresh、跨profile重启恢复、pending/孤儿；子进程 crash 点按精确获批窗口，无用户目录                                                           | 受控元数据格式与恢复拒绝；没有目标OS同步/跨进程仲裁时不记耐久或生产恢复完整                                                      |
| B-L 仓库       | 每工厂 init在开始前占槽、真实文件发布link留下双名/失败、实际 in-flight操作+关闭/晚完成/epoch替换、资源关闭失败保留；不用 Keychain/用户内容/模型网络                                                                                     | 真实私有仓库供方；假 RPC/Promise 可测状态，但不替 T01/OS终态                                                                     |
| B-L 网络/T01   | 后续另批无外发受控 loopback或隔离真实进程：包装超时而 request/socket/子任务未结束、所有子进程回收、短session恢复与永久stop差别、child/Store实际close                                                                                    | 未授权前不执行；no-network阶段不声称网络链已验证；T01未冻结不写fixture伪成功                                                     |
| 生产接线/C/D/E | gate前 SQLite/header/catalog/backup IO0、alias单writer、native撤销、同build VFS、真实两层ready/完整scope/同UUID重建、模型不可用且保护仍完整、两OS/包/真人                                                                               | 单独真实联验和验收，不能拿旧A数量或上述临时目录替代                                                                              |

各代码阶段获批后运行受影响真实专项、完整 `npm run check`、必要 sources/package/目标OS及隔离验证；真实 argv/cwd/stdout/stderr/exit、首失败、输入 ref/SHA、受审 candidate、source/lock/artifact 实物保持绑定。环境或产品候选变更后按实际影响重验；无变化不重测。

针对本轮静态审查的具体缺口，B-M 专项必须包含“旧 absent-retired 与新 present 同址”的真实临时文件替换，在未扩展 A 时断言 unknown、历史仍保留且无生产准入；未来 A 扩展另验同址历史/current 正例及两个 present 冲突等负例。B-R 专项须从实际新临时父目录覆盖 bootstrap 每一步失败、header 不完整、自身追加不递归、bootstrap 期间外部目标 IO 为0、未 seal 时外部目标 IO 为0；这些是未来验收要求，本轮没有运行。

本轮交付固定 docs ref、完整输入表、两份源事实报告、独立方案审查原文及逐意见处置、manifest/实际 docs差异。原报告保留原字节，首次格式失败若发生保留，不改 6a38 证据、不借原 A 700/1052 数字当 B 验证。独立静态审不替指定 GLM-5.3最高/M3.1-Flash xhigh 同base/head双方新审、平台/CI/正常合并/远端与真人门；无 push/PR/merge/Goal改变。

## 附表：固定 e2c 逐路径身份

下表由 Git blob 实算，含八条原 B 路径、六条具体额外依赖、仅只读的 fixture 和三条 T01 历史调用图；没有代码复制到本轮证据。52项完整来源另见 inputs.json。

| e2c 相对路径                                                      | bytes | SHA256                                                             |
| ----------------------------------------------------------------- | ----: | ------------------------------------------------------------------ |
| `apps/desktop/src/main/model-gateway/await-boundary.ts`           |   971 | `e0dd898dd90e12b31b76df04a0907288eb14533bb8dd15e8ebb24ed9fc581382` |
| `apps/desktop/src/main/model-gateway/ciphertext-repository.ts`    |  4225 | `31e4bed54746529cecbdd1100db6ccb19840ef1d5367090a5334964a2f01e41d` |
| `apps/desktop/src/main/model-gateway/configuration-repository.ts` |  5292 | `535c66d17ac5172eaee4a5c4781f7e84af1bcad64eb522baa33bb14ad199b19d` |
| `apps/desktop/src/main/model-gateway/credentials.ts`              |  3366 | `8a56addc33468467a733614a96ff4f24489d06144afe44f4dafe873dbc10482f` |
| `apps/desktop/src/main/model-gateway/electron-safe-storage.ts`    |   653 | `724462829544f8c51b0fe1c6ed5335c7b1168cb9379baa7daf69641cf11e9b0e` |
| `apps/desktop/src/main/model-gateway/finite-fixture-policy.ts`    |  1204 | `92e60aa4926242a8280da5ca0c3c5533f1c52f6c9c83e07699cf25eea2d7a78e` |
| `apps/desktop/src/main/model-gateway/gateway-application.ts`      | 13777 | `2542730ba42406c1b2ab86c30f3bacfac2386be2f537b1f166a0a1da2d64f1d4` |
| `apps/desktop/src/main/model-gateway/gateway.ts`                  | 13893 | `3f6005fe33dba7275c0e7a45a640cd94e17e62dc1609347f1c644dcf2f610126` |
| `apps/desktop/src/main/model-gateway/model-service.ts`            | 22132 | `0bfd4360cbaf086b143fbc209e68994cc65496f3f9bce7d3a0bc4609c5a28395` |
| `apps/desktop/src/main/model-gateway/persistent-audit.ts`         |  4665 | `62d77f33293770b3c72a0ede6ab796115ac10ebad8def1e534790015c562f5a8` |
| `apps/desktop/src/main/model-gateway/policy.ts`                   |  2486 | `dd09203ebe7e7f655cee40e01c84149a8c121e48ece916fa816cbc2c320d1ced` |
| `apps/desktop/src/main/model-gateway/private-directory.ts`        | 15060 | `40a9a5d52488a25d3958c171ac3e5df4272eed5d42a97f51a76ee5baeb015a88` |
| `apps/desktop/src/main/model-gateway/stored-field-projector.ts`   | 10374 | `73b1d5e0b1c16f3559259817c7f6a2bd1105c090cfb4abb5fc4c956dc63fce8c` |
| `apps/desktop/src/main/model-gateway/stored-result-source.ts`     | 10155 | `b77f2acf2e93af1e212fa7d3539b63f0090800a86dcb4587d347c3fde0d8e2d3` |
| `apps/desktop/src/main/model-gateway/transport.ts`                |  3256 | `ec417eabbe25cf2340df0f0fc3b82b86740b961f3ef0f84adaa40f923b43aa99` |
| `apps/desktop/src/main/index.ts`                                  | 12088 | `d88c1df806dc913b85a719026640ee6502762153c82c148e57aa32d5dbd9c60b` |
| `apps/desktop/src/main/engine.ts`                                 | 18609 | `d1e8a6a55b718861809570864745d49ef0e9bec3271f49cc2bc4945c8cfdf8ca` |
| `apps/desktop/src/main/task-service.ts`                           | 33131 | `7ed65bd689a8cfa445b4d349a1a996750f67c190600d0f46b2dceb324ebd0a68` |
