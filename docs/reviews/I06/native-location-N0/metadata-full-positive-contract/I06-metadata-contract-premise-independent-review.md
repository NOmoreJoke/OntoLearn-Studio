# I06 N0 元数据合同前提：独立追溯

2026-10-22。结论：**UUID presence 是后继实现的保守见证，不是原用户要求或 ABI 必需条件；未查见 N0 必须以单次原子 metadata/ACL 调用完成观察的原条款。** 这两点不能直接导出删除门或将缺省 ACL 当成功。现材料仍未证明受控无 ACL 正例的有效 absence 合同，不能批准仅有条件拒绝的修复，也不能以所有正例均 `UNSUPPORTED` 完成功能。

本审查只追溯合同前提，不重复签收 004 静态归档，不批准源码、构建或运行。003/004 失败及其未知保持。

## 范围与直接核对

只读树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-native-location-N0`，实际 HEAD 为 `904cc2675c37387621954bb5a39a055c09d492b3`，Git 状态仅既有 ` M AGENTS.md`。先全文读本树 AGENTS、共同指令及根 004 静态窗口/失败闭环；后续只读相关 Git blob、合同/源码行段和既有官方来源摘录。没有产品 import、测试、编译、native/API/ACL/FS/DB/进程探针、网络搜索、fixture 扫描/清理、GUI、Git 变更或 Goal 操作，不分析 SQLite 或 heap/OS 资源接口。唯一写入为本报告。

实际计算的固定主依据：

| 固定 ref / 文件                                                                                                    |  字节 | SHA256                                                             |
| ------------------------------------------------------------------------------------------------------------------ | ----: | ------------------------------------------------------------------ |
| `9ff1c92e78cc0bed1e37b71ea7f00a57ad231f7c` / `docs/iterations/I06/native-location-supplier-plan.md`                | 49472 | `34c4307e42c349b5d4fc40d0960655454727570eb565c4fc1c3d521663c57624` |
| `1f3b053d8a69d1f7ddb1e29c143f648d910fe689` / `docs/iterations/I06/project-location-capability-and-cohort-offer.md` | 46365 | `561ec272c07f0c0f026c9aa17b717b99d3e110e31cb4ee45f0663254e9517443` |
| `fa1a7e4155f3afee4a1b3409f9ab8804cc620186` / `packages/native-location/src/platform_macos.cc`                      |  7675 | `28f9c736e59a24cb050b706628aca26283a513fa3c019fdf58dd14e7d3f8a5be` |
| `1217e0f63a9c62b72e01046ef5fbc5c53434251a` / 同 Mac 文件                                                           | 12579 | `d944a4901b6d3f516f18ab436aed9ec56a78eb1bbd12d1949ebf6a6e171825ce` |
| `1217e0f63a9c62b72e01046ef5fbc5c53434251a` / `packages/native-location/tests/location_core_test.cc`                | 37928 | `2517eb970ef39f37dd99ca9945909331df937d4dd43ce53b74eb722bf47a7053` |

下文简写 `9ff`、`1f3`、`fa1a`、`1217` 分别指上表完整 ref。004 新静态材料均绑定 `904cc2675c37387621954bb5a39a055c09d492b3`，不是受审产品变更。

## 1. 正例可用性必须保留，但不是所有目录都应接纳

原 N0 窗口 `I06-native-N0-source-implementation-authorization.md:24–32,40` 要真实 held 对象的身份/links/ACL、受控独占临时 fixture 和正向/替换/alias/关闭等真实证据。`9ff` 主方案第 192 行也以两目标 OS 受控临时 root 的真实对象与 acquire/关闭证据作为阶段结果，不是“安全拒绝即完成”。

现有设计接受的最小 Mac 正例域，是当前 UID、目录/普通文件类型正确、无 group/other 写、目录 nlink 非零、普通文件 nlink=1，且确认没有扩展 ACE 的受控对象。保守 ACL 策略见根 `I06-controller-native-N0-source-prereview.md:31–39`；它明确不是最终用户目录的完整支持政策，也允许拒绝未知/不支持/非空 ACL。不能由此推成“所有合法文件系统上的无 ACL 对象都必须接纳”，也不能把 APFS 首批实验提案升格为最终产品限制（`9ff:63`）。

但**在已冻结目标环境中成功建立、满足该策略的受控空 ACL 正例必须可用**：`1217` 测试第 131–147 行建立受控目录、成功应用 `acl_init(0)` 并建立 sub/member；第 511–534 行要求 empty fixture 的 owner/root 返回 `NL_OK`，并实际关闭；第 565–585 行另要求 root、member 及替换后的新对象正常观察成功。main 第 729–735 行没有允许这些正例全部 `UNSUPPORTED` 后仍给通过的路径。

这里的“空 ACL setup 成功”不等于 OS 必须保留某一种表征。003 remedy 的 `validation-scope.md:18–24` 已区分 P1 明确 absence 与 P2 自然 present-empty；不得强造第二表征或把一个冒称另一个。需要保证的是合法正例能经有证据的适配路径被接纳，而不是强制 UUID 位或某种原始 header 恰好出现。若新实现只接受罕见 present header，常见受控 empty setup 一律拒绝，则仍未完成本阶段的正例验收。

## 2. 真实 ACL 验证是原要求；UUID 完整性门是实现选择

`9ff:50–61` 要从实际 held 对象读取 ACL、不 path reopen，解析错误及未知规则拒绝；原精确允许策略还须冻结。根源码窗第 26、30、32 行继承该对象绑定、安全拒绝和受控边界，没有指定 `FILESEC_UUID`/`FILESEC_GRPUUID`。

已批准首轮源 `fa1a` 的 Mac 第 58–85 行先 `fstat`，后独立 `acl_get_fd_np`，仅接受有效且明确 empty 的独占 ACL，`NULL` 为不支持；当时不存在 UUID presence 门。这也是“原设计并非单次原子调用要求”的直接历史证据，不代表旧查询已正确支持 absence。

UUID 门由 003 失败后的 remedy 引入：`acl-null-003-remedy/proposal.md:15–18,29–32,55` 用所读公开 Libc 的完整/短 security 分支差异，推导 UUID/GRPUUID presence 可作完整 envelope 的保守见证；该文明确称其为实现级推论。根 `I06-acl-null-003-remedy-source-window.md:7,14` 批准的是这条特定源码路线及缺见证仍拒绝，未把两个 UUID 字段追加为产品业务需求。`1217` Mac 第 160–172 行的注释和条件与此一致。

所以，替换 UUID 门**可以是保持原目标的技术修复**，不必把它当成必须由用户降低要求才能改变的字段。但必须先有同 held 对象、语义充分且错误可区分的 ACL 状态证据，保持安全门和实际 ownership/cleanup；不能单独删除门、吞 `NULL/ENOENT`，也不能仅凭 `query` 成功或 valid=0 签 `acl_checked=1`。004 静态候选第 11–17 行保留了这些反例，现材料不足以推翻它们。

“公开 Libc 不是 installed 二进制身份”是正确的证据边界；本次所读原合同没有要求证明 installed libSystem 与某公开 commit 逐字同源。若正式平台接口合同已足够明确，适配可依据该合同，再在固定 OS/runtime/产物上做真实正反验证；不能自动把取得系统库源码同源身份证明增加为 N0 必须交付件。反过来，只有某公开实现的条件分支、没有足够接口语义时，也不能把它当作跨版本合同。

## 3. 未查见单次原子快照要求，仍须处理真实竞态

原边界有明确层次：`1f3:39,123` 是应用误选、静态 alias、生命周期/普通路径竞态和自有并发，排除任意恶意同 UID 进程/全盘 DLP；`9ff:57–61,192` 区分 held 对象与持续 namespace，N0 只有对象级受控 fixture 证据，生产 open/publish 围栏缺口保留。根 N0 源码窗第 32 行和首源码预审第 37 行再次明确 ACL 快照不签持续许可。

固定 ABI `location_abi.h:7–24,83–90,129` 规定受信 harness 提供 live borrowed 对象、adoption 前保持稳定、gate/epoch/资源责任；metadata 只有 `acl_checked` 与 `held_object_only`，production admission 固定 0。没有“所有 metadata/ACL 字段必须来自同一个原子内核时点”的明文。`fa1a:62,70` 原本就是两个调用；且一个 C 函数调用本身也不自动证明内核字段的原子一致性。因此不能仅以“候选增加第二次调用”认定违反了已冻结 N0 需求。

但不能把“没有单次原子要求”解释成任意拼字段安全。后继完整设计仍须说明：

- 一直消费原 held FD，禁止 path reopen；借用 FD 不能在 adoption 中被 harness 关闭/复用，普通 member 替换仍要由实际返回对象身份及 expected filter 拒绝，不能借第二次查询回到名字。
- 自有权限/ACL/namespace mutation 与观察如何受同一 native gate 或受信 harness 协调。现 ABI 的“stable”不能未经说明就自动等同“冻结全部权限字段”；如需要此受控前提，须在装配合同和测试中具体列出，而非声称 OS lease。
- 多次观察中 identity/type/owner/mode/links/ACL 的矛盾必须非成功；相等不能签持续稳定、ABA 不可能或跨调用共同原子时点。root/member 已换、epoch 撤销或 TTL 到期、晚返回和失败资源仍须按原 owner 收尾。
- 对无法证明的外部变更窗口，保持 N0 `held-object-only` 和生产拒绝，并如实列未覆盖。该分层不能被拿去开启 N1/VFS/生产许可；也不应为了 N0 新增任意恶意同 UID 围栏或不可证明的全时原子快照条件。

这里最小工作是明确已有观察语义和自有协调，不是先发明新的 OS 锁。若后继要把观察升级为持续位置许可，才需正式重开对应更强保证；当前未授权。

## 4. 新候选提供部分合同证据，absence 仍未证明

004 静态来源中，官方手册摘录给出了同 FD、返回属性 mask、`REPORT_FULLSIZE`、4 字节 packing、相对引用及静默截断警告；这些足以作为完整设计中核验**实际返回 payload**的依据，强于 UUID presence 的间接推论。声明、未写解析器的正确性及当前目标支持仍是不同证据层。

但保存的 XNU security packing 摘录第 2–15 行（固定 `f6217f891ac0bb64f3d375211650a4c1ff8ca1ea:bsd/vfs/vfs_attrlist.c:2051–2074`）只有 `va_acl` 受支持且非 NULL 才设置 security actual 位，其他分支可省略或给零长占位。这里不能把缺位/占位当 absence；完整 NOACL header 与 count0 的区分也不能证明目标 empty fixture 实际返回它们。004 proposal 第 41–52、58–66 行准确保留该限制。

这只能得出“现有材料未证明完整 absence 接纳合同”，**不能得出所有公共 API 都不存在此合同、系统不可能支持，或完整目标应永久缩减**。我没有新增 API 枚举/网络搜索，也没有核本机真实响应；不作超出材料的否定。

## 5. 建议的最小下一步

建议根受限接受本次前提审查，交原 I06 补一份**面向完整正例可用性的合同/设计**，而不是批准仅布尔诊断或条件解析器去追求绿色：

1. 先固定 N0 的观察语义：受信 harness/自有 gate 能保证哪些稳定性，哪些只是本次 held 对象观察；明确没有新增单次原子快照或持续许可要求，同时保原普通替换/alias/撤销/关闭反例。
2. 对已批准候选提出对象级 ACL 状态表：API 返回成功/失败、缺属性、明确 NOACL、有效 empty、任意 ACE、畸形/矛盾，各用哪个正式语义区分。逐项标明依据是正式合同、特定公开实现、还是待实测；尤其说明原受控 empty setup 为何有足够的成功路径。不能用 unsupported 占满所有合法正例，也不能把只有可能出现的 header 当已证明接纳路线。
3. 若现有正式语义仍不足，应先补精确对象级 absence 合同/目标版本适用依据；若缺的是实际表征而合同已允许判断，可另提一次有限、能改变路线的受控响应实测设计供根审批。该实验应事先说明各结果怎样决定采用/放弃方案，不能再次仅区分两个不解锁的布尔位。本审不授实验。
4. 只有完整路线的输入域、成功/失败、同对象/自有变更协调、解析/ownership 和正例验收冻结后，才值得精确源码窗口、T03 增量构建及实际目标验证。若无法补齐，准确列当前接口合同/平台证据缺口并保持组件未完成，不能将 fail closed 报成可用功能交付。

无需为改变一个实现级 UUID 见证或澄清未曾要求的单次原子性，先询问用户降低功能/安全目标；这些属于可审查的常规技术设计。若真正需要改变原威胁边界、最终平台/用户目录范围或原安全政策，则仍须明确决定，不能以本报告自行缩减。

本报告没有宣布 absence 已可安全接纳、候选接口已适配或任何运行通过。指定同版双外审、目标 OS、CI、真人、远端合并以及 T01 原 HOLD 等既有门不由本审关闭。
