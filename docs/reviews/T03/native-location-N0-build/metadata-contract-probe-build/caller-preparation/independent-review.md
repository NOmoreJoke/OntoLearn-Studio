# Fresh caller 独立源码审查

结论：**NEEDS_CHANGE / NOT_CALL_READY**。本审查独立覆盖固定候选的完整 14 件材料与整个 caller 源码；不接受作者的 upper 为已成立，不以最后 HOLD 或有限 cap 推导遗漏动作免费。发现 3 个具体异常路径缺陷，另有 1 个完整上界证明缺口。这里没有运行 caller、其任何局部函数、prepared runner/reader、模拟或 fixture。

## 固定身份、授权与读取范围

- 工作树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-native-location-N0-build`，分支 `feature/T03-native-location-N0-build`。
- base：`f2b2159c1060b10f73f0baba6ca1cdebd6a38677`；实际候选/入口 HEAD：`6815495c010e8eac617baa8c061d8ed3cfd90eec`。
- owner manifest：3607 B，SHA-256 `4f2d47484f3f1454590e2ee0032faa55dbfdc86631ddf4895403f111c1c6636e`；其 13 件 payload 共 86832 B，完整 14 件共 90439 B。
- caller.py：43314 B，SHA-256 `55bb6afe958101ca4420eacb1033f58ad6bea1da70fbf610761ee694f31c40ba`。
- 已分别读取当前文件及固定 Git blob，独立核实每件 current = Git = manifest；base→candidate 精确路径集合只有这 14 件，均在 caller-preparation。入口 index 空，入口 status 只有受保护 AGENTS.md 修改与本人新前付文件。未修改、stage 或 commit。
- 当前保护 AGENTS.md 已完整读取：15147 B，SHA-256 `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`。旧 78df 身份只属历史时点，不作为本次保护身份。
- 完整读取 root 的 `T03-real-caller-static-preparation-window.md`、当前 `desktop-operation-policy-20261022.md` 及 `developer-common-instructions.md`。桌面偏好更新不扩大本静态窗口的执行禁止；本线没有新桌面 task lease，未抢用 CUA。
- 完整阅读 README、SOURCE_BOUND、schema、unsigned template、runtime fees、owner-pre-review、计划、静态检查及账。源码一次读入 held buffer，输出以连续片段补齐；之后 source span 与推导均取 held buffer，没有重复读取未变源码。
- 需要历史接点时只读既有 meter-forward-binding 的 README/preconditions 小 metadata 和原 unsigned authorization template。未重开 frozen 37 件的 runner/reader/identity/tool/SDK/descriptor/witness/index/raw/binary 源码或载荷。

前付已在首次 candidate 访问前用普通文件保存为 `independent-prepayment.json`：固定 6000 metadata / 2 MiB，分为完整源码关系 3500 / 1048576 B、精确 delta 1500 / 524288 B、封存 1000 / 524288 B。各阶段不借、不退、不超；metadata/application/OS 实际消耗均 UNKNOWN。完整材料读取不复用其他线票，未创建任何新 runtime 身份。检查与命名保守账见 `independent-check-record.json`。

## 具体发现

### F1 · P2：短写后失败会丢失已消费的原始尾部

位置：caller.py 594–609、636–639、794–804、843–845。

capture 的一次 read 可请求 65536 B；601 行先把全部 raw 放入进程内 bytearray，然后才在 605 行写 raw 文件。可达静态反例：内核返回 65536 B，首次 write 只保存 1 B，下一 write 抛 OSError。此时 65535 B 已从管道消费，saved 只计 1 B；尾部只在 streams 内存中。terminal 只持久化 read/saved 长度、已保存部分 hash 与错误；最后 emergency 也没有尾部 bytes。wrapper 退出后尾部不可恢复，实际外层工具也无法从只含错误 JSON 的 stderr 重建它。HOLD_FULL_ORIGINALS_RETAINED 此时不能证明 full originals retained。

这一点独立确认 owner OPEN #1，不能用读写长度不同替代原始 bytes 保全。单次 read 上限本身不保证失败后的持久保留。

修复验收：明确 pending raw 的归属与有界持久化失败路径，保存已消费但未写成功的逐字节尾部及定位/长度/hash，保留 firstError 与后续 sink 错误。若所有真实持久化路径失败，应明确记录 genuine persistence failure 和真实外层观察，禁止声称 full originals retained。补足该路径的元数据/entity/应用字节完整费用；只缩小 read 而仍不保全 pending tail 不足以关闭。后续经授权验证至少覆盖首次短写后失败、首次直接失败、fsync 失败与完整 EOF；本次仅静态推导，未执行这些场景。

### F2 · P2：目录切换失败时漏掉新 fd，并模糊重试旧 fd

位置：caller.py 153–169。

154 行成功 open 返回 new 后，155 行 close(fd) 若抛错，156 行尚未更新 fd。except 只知道旧 fd，再次 close 旧 fd；new 没有后续拥有者或 cleanup。因此新 fd 泄漏的所有权路径被隐藏。旧 close 抛错也不能证明旧 fd 仍打开，不能把无条件第二次 close 当成已证实安全的补偿。

这一点独立确认 owner OPEN #2。修复验收：新旧 fd 在过渡期间都须有明确拥有者；失败记录须区分首次旧 close 与新 fd 清理结果，避免对状态模糊的旧 fd 盲目重试。覆盖 open 失败、旧 close 失败、新 fd cleanup 失败和私有 mode 校验失败的静态控制流，并把新增 cleanup 费用纳入模型。不要通过吞掉旧 close 异常或只在成功路径赋值来关闭问题。

### F3 · P2：nonce 目录 close 会替换已保存的写入首因

位置：caller.py 728–732；write_bytes 335–357；外层异常记录 852–858。

若 write_bytes 已抛出带 exclusive-output-write-or-fsync 首因和 cleanup 的 Fault，而 finally 的 os.close(noncefd) 又抛 OSError，外层捕获的是后者。原 Fault 仅残留为 Python 异常上下文，error_value/terminal 并未遍历或持久化该上下文，因此原始写入首因及其 cleanup 会从正式记录丢失。SOURCE_BOUND 第 45 行“First cause is never replaced by a cleanup cause”不成立。

修复验收：显式保存 nonce 操作的 first 与 cleanup，将 nonce 目录 close 错误追加为清理原因，继续把原 Fault.first 作为第一原因；也覆盖仅 close 失败的情况。对所有 finally 中无保护 close 做有限静态核查，不以当前 Fault 包装存在推定嵌套 finally 安全。

### F4 · P2：完整运行 upper 缺逐项证明，当前数值只算术成立

位置：SOURCE_BOUND 29–46、50–62；caller.py 91、104–129、148–197、309–318、360–363、396–510、568–639、785–845。

本次独立重算 27624 metadata / 26392 entity 的加法正确，但不能接受为已证明的完整上界。具体未闭合点：

1. 每 file 216/200 的展开为 72 path + 48 stat/identity/mode/presence/close + 96 chunk metadata；entity 为 72 + 48 + 64 + 16。source 实际包含 path.parent/name/parts 的重复取用、parts 的长度视图及 slice、component 遍历、前后 identity 的 7 元 tuple 与成员投影、chunks 容器/append/遍历与 join。文档未给出这些动作各自归属及最坏次数，24×3 和 32×3 不能自动涵盖重复 materialization 与遍历。写路径和失败 prefix 如何映射同一 fee 也需逐项说明。
2. JSON 8c+80 把 native3c 和 scanner/结构5c 合并声称足够，但 object_pairs_hook 实际接收 rows 容器、pair tuples，遍历每个 pair，投影 key/value，检查重复，再建立新的 result dict。需要把 native 原图/rows/tuples/newdict、scanner 结构动作、重复键失败和每对象固定开销明确映射到 c 及 F 的独立系数。承认 hook 非免费，不等于证明 3c/5c 已覆盖。
3. fixed4096 的 1536/1536/896/128 只是类别预算。需要整个 admission、128 imports、keyset/set/dict/iter views、predecessor、reader facts/completion、planned/attempted/dispatched 的 common 重建、terminal/meter/error/cleanup slice、JSON 编码 native graph、emergency/顶层失败的完整逐行或源段映射；成功路径与可达失败路径应分别合并求最大，不能把每个大类归纳成一个未经展开的 allowance。
4. 每 select 256 目前仅注释声称 backend/list/key/tuple maximum。需说明确切 KqueueSelector 的本调用（两个注册 pipe、16 次 select、32 entries、register/unregister/close）对应的 native event/key/tuple/list/lookup/return 投影上界与计数边界。现有静态源码和一句继承费用不足以独立确认该 256 适用于本 caller；这不授权去探测平台或执行 selector。

这一发现独立处理 owner OPEN #3，保持证明 OPEN。它不是已测得超票，也不声称 Python/OS 物理分配已计量。修复验收：提供完整有来源的映射、系数、各路径上界与 literal arithmetic；若实际新增费用导致票额不足，诚实更新未拨付 proposal 和 aggregate，不能为目标重分类或提高旧 cap。F1–F3 的修复也必须加入该证明。

## 全源关系审查结论与边界

| 检查面 | 静态观察与当前结论 |
| --- | --- |
| 根信任 | admit 397–425 以 root 实际调用给出的独立 digest 比较固定路径 admission bytes，再信任其内容；authorized=true、模板、自算 hash、0600 不是独立信任来源。真实 out-of-band digest/nonce/time/rootDecisionId/原工具记录仍须未来 root 创建并保留。 |
| 精确调用 | 426–509 绑定实际 loose ref、caller/source、auth/config、controls、固定 argv/cwd/minimal env；入口检查自身 argv 与 -I/-S/-B，解释器 alias/canonical stat/权限。静态绑定可见；实际调用、元数据和权限未发生或未现场验证。stat-to-open/exec TOCTOU、loader/ABI 不由这些 pin 关闭。 |
| 四身份 | admit 检查四个固定 role key、非空有界字符串和 distinct 值；实际 human/model/task 身份须 root 外部认证。静态字符串不等于实际身份，当前未创建四份实际 admission/config。 |
| 防重入 | 全局 O_EXCL active.lock、永久 token/role mkdir、全局 nonce O_EXCL 限定串行和单次角色 claim；按同一 outputToken 最多四 role。失败 claim 不删除以重试。本地机制可静态识别；F2/F3 清理缺陷须修。真实并发、实际文件权限未运行验证。 |
| 生命周期 | 只对本次实际 Popen 对象操作；真实 planned→attempted→returned/start/end、exit/signal/timeout 有独立字段；owned leader terminate/wait1s、kill/wait1s。未用旧 PID 或进程组。真实调用与状态尚不存在；descendantDrain 保持 UNKNOWN。 |
| raw 与错误 | 有限 read/event/write/select 次数和 EOF/exit0/错误条件可见；F1 阻断原始 bytes 保全结论，F2/F3 阻断完整 cleanup/首因结论。不能从最终 HOLD 反推遗漏已安全处理。 |
| 父进程末尾 close | terminal 写在后续 fd close/unlink 之前，末尾失败会使实际外层 exit 非零；下一阶段 trusted admission pin opaque root observation bytes 并 attest outer exit0。程序未解析其全部语义，这一边界文档已明示；未来 root 必须保留真实外层原工具观察，不能用 child terminal 代替。 |
| reader completion | 642–680 从真实 method.stderr、facts、report、原 index/archive-manifest 构造 8 字段 completion，含实际 code 与 hashes；成功还要求 facts 状态/空 findings/空 stderr/exit0。当前没有真实 completion，静态关系不代替 reader/原始资料审查。 |
| 保护范围 | 本 candidate base delta 仅 C 中 14 件；旧 37 件和历史 native snapshot 不因此更新。未读其禁止载荷，也未修改 Q/N/P、产品或其它树。 |

所有 candidate 材料及入口都已读到；owner-pre-review 不是独审证书，其 OPEN 问题已逐项处理，未借作者声明充当 independent proof。未运行 JSONSchema 引擎，因此只报告 schema/template 的文本、JSON 与源码关系审查；没有宣称 schema engine 验证通过。作者记录的 AST/static checks 是候选证据，不冒充本审查新运行的检查。

## 费用与可运行性裁决

每 role 的字面式重算：

- metadata = 4096 + 37×216 + (8×1200 + 7×80) + 16×256 + 32×16 + 96×8 = 27624。
- entity = 4096 + 37×200 + (8×1200 + 7×80) + 16×256 + 32×8 + 96×4 = 26392。
- proposal：每 role 28000/27000；四 role 112000 metadata / 108000 entity / 13 MiB。全部未拨付，完整 upper 尚缺 F4 证明。

当前 2291263 metadata 加原 future 806000 再加 caller112000 = **3209263**，超过旧 3200000 **9263**。entity 521456 + 737280 + 108000 = **1366736**，超过旧 1300000 **66736**。build 109086362664 + 164 MiB + 13 MiB = **109271960616 B**，现 guard 137438953472 B，余 28166992856 B；combined old supply 119017687701 B 不因此改写。

裁决保持 **METADATA_AND_ENTITY_NOT_FIT / NOT_CALL_READY**。原 future 与新增 caller 均未 funded；即使字面票额覆盖加法，也不能绕过 F1–F4。新 global guard 只能在未来 root 真实窗口显式批准，既有 unsigned 模板/本报告不批准上调。旧 native37 snapshot 不改，原 806k/164 MiB/entity737280 不借给本审查。

## 关闭条件与封存边界

先把本固定候选独审结果冻结并由 root 完整读后 commit；若 owner 修源码，则产生新的真实 candidate ref/manifest，后续只用原保留 1500 metadata / 524288 B 精确 delta 复核，不重开未变全文。新修复若超出该固定 delta，应停在缺口并由 root 明确处理，不能借完整源码/closure 剩余票。当前没有修 source、没有运行 proposal、没有 runtime 身份或 actual attempt。

F1–F3 修复及 F4 完整证明关闭后，仍须未来真实 root admission/四角色/parent outer observation、实际 loader/ABI/drain/full acceptance 及所有原 formal/product gates；本静态独审不替代这些门。当前 developer/common 的独立外部模型、CI/多 OS/human/develop 等适用门也未在此完成。

本报告与检查记录的格式、封存身份由 root 收到的 final bytes/SHA-256 确定。封存后不再写本文，不修改候选原件；最终检查只涉及本人新文件及小型 Git/保护状态。
