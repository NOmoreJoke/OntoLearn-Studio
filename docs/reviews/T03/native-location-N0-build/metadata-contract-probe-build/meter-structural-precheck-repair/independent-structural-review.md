# R7 新作者独立静态首审

固定候选 `68ffbb9dfab5790a1c076cf770e208b17eaa8d1b`，base `4fc8ea8c089d85c101dc11cf1494bd7a4808d492`。结论：**R7 的本次源级结构计量修复及其局部逻辑上界获得静态支持；整包仍为 HOLD / NOT_CALL_READY。** 没有通过最终拒绝或不可达分支倒推费用充分。另有一项需要最小修正的当前控制文档算式 C1/P3。未来 metadata/entity 均未获资金，外部、运行及父级门禁仍开放。本报告不授权候选、未来版本、fund、auth、attempt 或调用。

## 独立身份、前付及允许操作

本作者是新的独立审查 agent；没有复用前作者已耗尽的 8000 票。首次文件探索前先写 `independent-author-prepayment.json`：固定新 8000 metadata / 4194304B，pins 1200/262144B、完整源与模型 3300/1310720B、delta1 1000/524288B、delta2 1000/524288B、闭合 1500/524288B；另有 1048576B 字节 reserve。metadata 不借、不退、不超；报告闭合额度保留。两次精确 delta 本轮均未使用，不能提前批准下一候选。实际 metadata、application/OS I/O 未被计量，仍为 null/UNKNOWN；本报告的固定前向预留不是实际消耗或历史合规证明。

仅普通文件/Git/文本字面字段/算术/哈希操作。没有 import、call、extract 执行 runner/reader/helper/任何局部函数，没有 fixture、模拟、dryrun、compile、py_compile、compiler、API、DB、网络、GUI、安装、版本/环境/能力探针、产品测试或 physical/heap/OS 资源分析。没有重新读取 product/source/.cc、SDK/tool、880 witness、42772 index、旧 binary 或 descriptor/pins payload；代码中这些路径的字面值不等于 payload 读取。没有读取 installed selectors 或 saved selectors payload；仅引用旧 N 作者已完整显示/核哈希的历史观察，不推称当前安装 freshness。

仅写新前付声明和本报告；不改实现、测试、配置、旧 Q/N、受保护 M 或其它树，不 stage/commit/push/PR/merge，不创建/暂停/重建 Goal 或聊天，不派生其它 agent。

## 冻结身份及实际读取

树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-native-location-N0-build`，branch `feature/T03-native-location-N0-build`，实查 HEAD 与分配候选相同。入口只有已授权保护 `AGENTS.md` M；该文件完整读取，15852B/SHA256 `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`，未 stage。当前 AGENTS 操作约束适用；冻结 Git 中的旧指南不替代它。本窗禁止候选运行，故没有以通常代码/文档检查规则恢复任何被本窗禁止的命令。

全文读了 P/inputs 三条规则、当前 M、P manifest/static-checks、完整当前 runner 44695B、reader 57301B、完整 proof/entity（含历史基线）、joint table/call matrix/unchanged context/README/method-plan/preparation-ledger、D 七控制件。旧 N 首审 23440B、delta1 17239B 与 owner-disposition 5178B 均全文读取；首审尾部 seal 没有被省略。第一批组合输出确实发生工具截断，截断落在 entity 基线；已单独完整重读该 12668B 文件，不把截断当全文。runner 和 reader 用连续分段完整显示；pipeline 重复读源计入下面字节表，没有把重复磁盘输入伪称 held-buffer 免费显示。

P manifest 5421B/SHA256 `8fd5b5eb9eb6051a08dd985267a2b2e20c84844a777c3edc35646eeece3e1050`。20 payload / 185645B，加 manifest 共 21 件 / 191066B。逐项实际核 current bytes/SHA == manifest == 固定候选 Git blob；manifest 自身 current == Git。实际 base→candidate 名单也恰为这些 21 路径。manifest 对完整源的 current/Git 配对核验属于完整源与模型阶段，不是初始只读规则、manifest、M 的 pins 阶段；其两份 payload 382132B 均已列入。

旧 Q `meter-remedy-after-controller-review` 的 base/candidate tree ID 同为 `eb14a55db8766bb880fa603d1d26bf0c9a10822f`；旧 N `meter-schema-init-repair` 同为 `abb242e43db7dd87a36edeabebf5a3e33c24b396`。两个全路径 base→candidate 及工作树 diff 均空。没有通过重读冻结工具/witness/source payload 来证明它们。index diff 空。固定 runner diff 和旧 N→新 P reader 完整有限 diff 已读：改变的是结构 scanner/decode/Account、路径与费用/phase/profile、原 preliminary 检查融合及新字段；原 raw/LC/driver/schema/read/write/binding 语义没有额外改动。

## R7-A：旧显式 stack 缺口已被实际移除

Runner 172–214 与 reader 126–168 现在保留 `depth/array_bits/pending_bits` 和固定 scalar flags/counters。没有 input-dependent `stack` 容器、逐 open 的 `[char,bool]`、append/pop 或 indexed frame member。两个 bit mask 在 depth<12 检查成功后才左移；close 匹配当前 type 才右移。把旧两个成员状态映射到顶层 bit 并随 open/close 移位，保留了父容器 type 和 array pending 状态；不是把仍然存在的列表改名成 VM 内部。

引号/转义和裸标量的连续字符只走 byte recognition。`bare` 遇结构/引号/ASCII JSON 空白边界才重新进入结构分支，故长 number/true/null 不再为每个字符反复投影“当前数组成员”。字符串内的冒号、括号、逗号不进入结构分支。这里明确沿用已有字符/字节识别域；不将显式结构记录的创建/访问划入字节域。

Runner 188–209 / reader 142–163：先检查 S<4c+8，再计本动作；array-value start 先检查 U<c 再增加 U、改变 pending；open 也先检查 U<c，再计 U，之后才检查 depth 并更新 packed state；field colon 先检查 U<c 再计 U。array 内 open 可能同时需要 member 和 container 两个 U：只有第一个尚有余量时可以先记 member，第二个没有余量就终止，既有 prefix 仍在 c 内，不会先创建另一个 frame。depth13 失败时虽已保守计一个 U，尚未发生新 packed frame shift。闭合/逗号/相邻值等非法流也有独立 S cap，不能借“未增加 U”无限访问 packed state。

旧浅数组内大量空数组的反例现在在下一个 member/container U 前终止；旧重复标点且低 U 的路径在 S 前终止。完整 raw 已在 read/hash 阶段保存；这些早停不截断、覆盖或丢弃源文件尾项。原 type/depth/EOF 检查与后续原生语法检查保留，没有提高任一业务 cap，也没有把允许的 zero-U scalar 一概拒绝。

## R7-B：独立推导 S、U 和失败前缀

令 C 为容器数，K 为对象 field 语法出现次数，A 为数组 member 出现次数，u=C+K+A。重复对象 key 仍按语法出现分别计 K，不能利用原生 dict 覆盖退款。对完整被原生 JSON 接受的 UTF8 输入：

- open/close 动作至多 2C；colon K；comma 至多 K+A。
- key 字符串起始 K；其余 value 起始至多 K+A+1；这个宽式可重复涵盖 container 起始。
- 可选首 UTF8 BOM 另至多 1。其余合法空白、字符串内部及裸标量连续字符不增加 S。

故 S≤2C+4K+2A+2≤4u+2。这个关系由语法分解得到，不是从 cap 检查“成功返回”假定得出。容器 type/pending bit 的转移与正常 JSON member 边界相符，因此成功扫描的 U 覆盖其 native graph；u=0 的 root scalar 仍在 8 动作 slack 内。原生 decoder 接受的固定 scalar 扩展也没有增加 field/container/member 图；这里不把原生 decoder 描述为独立的严格标准 JSON validator。

非法输入不需要上述成功语法关系：局部每次 shape 在任何动作/语义 U 前检查，始终有 S≤4c+8、U≤c；mismatched close、missing field/value、incomplete quote/container、depth、连续标点、native syntax rejection 都不靠事后 U 检查支付此前扫描。UTF8 decode 错误发生在固定 setup 后、结构状态迭代前，已付款且没有 native graph。bytes 不是 JSON bytes、cap/type/F 等错误也不需要先触碰输入图。

Reader 171–187 在首项 latch 检查后立即置 decode_failed=True；F/structural_prepaid/per-file type/remaining 检查均在 shape 前。c=min(Umax−acceptedU, 原 per-file cap)，没有把全局余量和本文件限制分别扣两遍。只有原生 decode 成功后才把 U/accepted S 接受一次并清 latch。任何 admission、UTF8、scan、native 或成功更新中途异常都不会清 latch；之后再 decode 在 raw 前拒绝。

有 f 次成功、总接受 U0 后，至多一次真正失败的 scan 能进入。其 c≤Umax−U0；扫描失败情形 f≤Fmax−1。总 S≤4U0+2f+4(Umax−U0)+8≤4Umax+8Fmax。全成功情形 ≤4Umax+2Fmax 更小；F 已满后的一次拒绝不扫描，属于独立 admission256。即使失败被 peer 的内层 control-review catch 保存为 finding，随后仅有 raw_review 和输出，没有新的 decode 循环；主层异常也只做一次有界失败输出。没有将 poison 当作任意外部重复调用的无限拒绝票，只审当前实际 caller。

这些推导也覆盖 Umax 已耗完但仍有 F 的 scalar（c=0）、空输入、异常退出及 native 已产生部分 prefix 后失败。原生调用只发生在有界 shape 返回后；语法可接受 prefix 中的 container/field/member 已受 U 控制，非法多余 adjacent value/key 不能让原生 parser无界继续构建一个图。原生固定错误/待完成 token 由既有 8F 常量与固定错误/包装项覆盖；不声称测量了 decoder 内部 allocation 或任何 OS 工作。

## R7-C：实际前付、全部调用及 per-file 义务

Runner 217–222 先 work16，检查 cap 的精确 int/nonnegative，再 work(8c+80)，然后才 UTF8/shape/native。完整为 native(3c+8)+structure(5c+72)+admission16。json_shape 只有这一个 caller；旧直接 preliminary shape 不存在。独立查到的八处与 matrix 相符：preflight auth96、meter256、history128、method256、plan768、pins1100、descriptor1200，总 c=3804、F=7；dependency source-evidence128、F=1。固定 SHA 先行的 opaque prior scalar path `json.loads` 不是通用 shape caller，仍在未变 24×880 路径项，不重读其 payload。

Reader 39–66 的 Account 在 config/file access 前支付固定 raw/output/error 费、native(3Umax+8Fmax)、structure(5Umax+72Fmax+256)；structural_prepaid 仅在成功付款后设 true。role 先被 main 678 验证，随后构造 Account；没有隐藏的其它 Account/shape 入口。以 whole role 上界预付之后，不再 per-call 退费或补扣同一 native 3U。phase/full-role reservation 不是代替源上界的唯一依据；上面的 S/U 及有限 caller 是其独立依据。

只有 decode 调用 reader shape。实际 decode sites：profile 的 meter/history（589）、control attempt（624）、config256（687）、method256（706）、producer records（736）、dep receipt（739）、owner attempt（761）、各 peer facts256/index768/completion64（778/788/799）、peer call-plan（813）。所有原 preliminary256/768/64 都作为同一次 decode 的 per-file cap 保留，同一 saved raw、一次 scan、一次 native；不是删掉先前语义约束，或偷偷保留免费的第二遍。原 producer/control hash gate、index/facts/completion SHA gate 与 per-file 次序保留。

Owner 的 F22 足以涵盖包括 build-failure 在内最多十份所选 producer JSON、config/method/meter/history四份、dep/attempt两份和两个 peer 的各三份。peer 全 producer JSON 至多28、config/method/profile四份、dep/callplan/attempt三份，≤35<40；即使原件含失败记录也在这个有限表内。每个失败仍保留全票。main 不会扫描目录或为寻找其它对象增加解码。JSON 进入后所有后续 graph 遍历仍由原固定控制/binding/raw/输出项付款，native3U 不是这些后续重复访问的代用品。

新增结构项 S+U+64F：S 付每次显式结构/值起始的识别及 packed-state 语义动作；U 独立付每次 field/member/container reservation。64F 分为 admission/latch/cap/counter16、固定 scanner setup/type/raw-boundary/return tuple及两成员16、native成功/失败与accepted/latch字段16、EOF/type/error/summary wrapper16。具体 decode 字段读写（latch、prepaid、F、U、accepted S）是固定每次有限项；新 snapshot 三个字段也保留输出构造/编码费。没有输入长度相关的 frame member/list 被塞进64F；没有另一个显式语义集合在逐字符路径创建/遍历。一次 scan 外拒绝另有256。这里是在已经声明的 semantic-record/event 模型中成立，不能改说每条 Python 指令、每个 scalar VM 对象或真实 application/OS 工作的上界。

因此 whole reader structure≤5Umax+72Fmax+256；runner 另16F，≤5U+88F。native3U 与 shape 结构项分别保留。对 reader 全局 native 的成功 prefix+至多一次失败 prefix，同样用剩余 c 而非每次完整 Umax，无漏付和重复扣 U；不再沿用旧晚扣 3×units 的模型。

## 完整费用与实体分类：源相同部分有条件继承

独立算术如下，全部为前向逻辑模型/提案，不是实际或最小必需值：

| 项 | 独立核对 |
|---|---:|
| runtime 新结构/admission |5×3932+88×8=20364|
| preflight 新增 |5×3804+88×7=19636|
| dependency 新增 |5×128+88=728|
| peer 每位新增 |5×12288+72×40+256=64576|
| owner 新增 |5×10240+72×22+256=53040|
| preflight 完整模型 |20292+19636=39928≤42000|
| dependency 完整模型 |60075+728=60803≤62000|
| control / emergency |51690≤60000 / 2208≤3000|
| M phases |42000+62000+60000+3000=167000|
| peer 完整 metadata |200616+64576=265192≤268000|
| owner 完整 metadata |46576+53040=99616≤103000|
| 四角色 metadata 提案 |167000+103000+268000×2=806000|

旧 pre20292 已含七次 native11468，所以只加结构/admission19636，没有再加一次 native。dependency 也只加728。Peer 完整展开为 native37184 + structure64576 + file2304 + bindings12288 + outputs6144 + raw131072 + streams104 + fixed6400 + init4096 + error1024=265192。Owner native30896+structure53040+file2304+manifest2304+result3072+fixed8000=99616。预付位置、实际 caller 与 proof 数量相合；phase guard 只是额外防线，没有被用来论证遗漏工作为零。

实体域独立保留旧 runtime206976、peer136296各位、owner47680 的完整分类（native图、token materialization与normalize重复、117逻辑alias/descriptor/pre/post、512 module view/member、opaque880 outer projections、SDK/binding/receipt、控制event/cleanup、raw16T/init4096、report/index/receiver/parent/external重复），只在源相同范围继承。新 structure/admission 20364/64576/53040 分别进入实体域，不能借 metadata 或字节抵消：runtime227340 + peer200872×2 + owner100720 =729804；proposal737280，head7476。

原生 graph、shape reservation、后续 source/projection/binding、output/encode、跨角色重复均分项存在；scalar bit-state替代旧显式列表不是实体定义排除。旧 N 首审已指出的 token、alias/module/opaque、重复 driver tuples 等类别，旧 delta 已给具体修补并保留 R7 open；本轮完整现源及有限 diff 没有撤销那些修补。未发现新的 source-path entity escape。这个支持是固定源与既定语义分类模型的完整逻辑支持，不扩大为未观察 library/VM/OS 内部的资源证书。

## 原 R1/R5/R2/R4 和绑定仍保留

R1：reader 402–464 只有初始 index<0 的 finish 可以 return；一旦开 LC header，缺 body/kind 在下一 header/EOF 拒绝。唯一 allowed key cardinality 包含 cmd/cmdsize，section/tool/count/minOS/typed binary command对应仍在。空中间/最后 body、重复/缺字段、未完 section/tool 的原文本反例仍关闭；未执行样例。

R5：peer Account 完整 raw init 付款在先，367–395 只允许一次 init，先记初始化次数，再构造17/67/12 schema，raw_review535为唯一调用点。owner 不调用；没有重新引入每字段 split/set/union 或 finish 遍历集合。50 CC1 literal、driver20L+48W metadata 和raw16T实体 recurring tuple分类仍保留。

R2：reader566–673、676–846 和 runner main/capture 的真实 source/auth/process/token/hash、四阶段index/argv/env/cwd/path/backend/timeout、phase/reservation/null-actual/no-refund、PID/EOF/error/cleanup、monotone event/capture 与最终1 compile/5 static/NOT_RUN/dependency核对保留。新 42000/62000/60000/3000、167000/103000/268000/806000、737280 与 history2249263/750737 在 runner、meter-plan、method、reader expected profile、call-plan 一致。实际 runner/proof/method/reader/procedure hashes 都有 current=Git=manifest 基础；method 的 reader/procedure 声明以及 meter-plan proof/method SHA 对上当前清单。将来 root 仍必须绑定实际 auth/config/parent identity；当前准备 pin 并不证明未来已绑定。

R4：read_once/byte/hash/before-after identity/exclusive save/first+cleanup error 等未变；receiver originals30MiB、runtime40/owner52/peers36+36，总164MiB，当前 reader<64KiB、proof<32KiB。owner tail20.28125≤22MiB，peer tail含controls/config/output/external≤6MiB。外部五源S3751936，一次held read+copy write+index blob read 3S11255808，加all-aux≤1048576，合12304384≤12582912。仍条件于该精确有限流程，不保证未来实际多一遍read/copy可免费，也不观察父进程退出/完成单。selector源码只继承旧完整显示历史，无当前安装证据。

## C1 / P3：OPEN，当前 control-method 的 phase 算式未同步

`D/control-method.md:5` 当前写 `M167000=pre22000+deps61000+control60000+emergency3000`。右侧和为146000，pre/dependency仍是旧值；真实 runner73–85/92–110、reader567–582、meter-plan及新 proof使用42000/62000，合167000。这个错误不能用“只是文档”说成已一致，也不能将 phase guard 的新值拿来替旧右侧付款。

最小修复：仅把该当前式的两个 phase 值改为42000/62000，并更新必要 manifest/static-check/pin过程证据；不需要改变 scanner 或提高guard。`dependency-method.md:5` 的60075/61000在末尾已有明确60803/62000后继说明，建议同次将旧句标成historical，避免当前方法段内出现两个未标历史的依赖上界。后者是同一文档一致性修复，不是新源缺口。

C1不会推翻本报告独立从现源推导的R7 S/U/费用局部支持；但本固定候选整套当前文档一致性尚未闭合。应先保留本首轮报告，再由 owner 真实提交修正候选；如果请求本作者 delta，只审真实已提交的精确变化，不能编辑本报告后冒充首轮已通过。未提前审未提交版本。

## 缺口、未授权门禁与历史

当前 metadata2249263/3000000，余750737；提案806000将为3055263，缺55263。实体521456/600000，余78544；已分类upper729804超余量651260；proposal737280将为1258736，缺658736。这是该提交模型和票的准确差额，不是实测消耗、最小必需或应当自动提高的 guard。bytes164MiB不变；当前build109067488296加未来171966464=109239454760，guard137438953472余28199498712；combined若另接受则118985181845。一个域的可行性不能给另一个域fund。

当前 guard 未提高，future tickets未fund，无auth/attempt/runtime观察。runner862按当前806000>750737会拒绝；本审没有利用该不可达性替代对后续source/dependency/native路径的推导。root关于前向资金及guard的决定独立后置，不能从本R7局部PASS导出whole/root/future验收通过。

旧2.25M/2.6M guard版本、所有失败/UNKNOWN/255、旧票、24000隔离、v1仅pins/report保留、旧owner实际UNKNOWN、旧author5280已知最低及其它UNKNOWN原样保留。新静态预留不追认过去。T01损坏SQLite/wholeH/原owner、被拒physical分析线、原selected-link/backend/stub/archive/compiler-open/headers/loader/ABI/current installation/drain、I06/父N0、指定同版双模型/CI/两OS/真人/remote/develop/full57门禁仍开放；没有对其新分析或试跑。

## 已知命名文件读取与本轮闭合

下表是普通文件输入及有限diff源payload的保守账，不是物理OS或全部工具内部I/O测量。Git元数据、parser/VM和缓存实际仍UNKNOWN。初始pins与完整源阶段按事先固定子票分别记账；没有将完整源比较偷放入262144B pins子额度，也不动delta票。

| 阶段/命名输入 | Bytes |
|---|---:|
| 初始pins：M、三规则、manifest、staticchecks |28779|
| 完整源：第一批P完整模型（包含被截断后另补读项的第一次读取） |44006|
| 完整entity补读 |12668|
| runner四个pipeline源读取 |178780|
| reader四个pipeline源读取 |229204|
| 旧N两报告+owner，含首审第二次尾部读取的保守全长 |69297|
| D六份完整control/plan/history/budget/method文档 |32137|
| runner/control/dependency有限Git diff old+new源上限 |101492|
| reader旧新完整有限diff源输入 |112657|
| 完整current/Git/source-model 21配对核验 |382132|
| 完整源/模型阶段合计 |1162373|
| 闭合阶段已做保护M复核 |15852|
| 报告readback前累计 |1207004|

pins28779<262144；完整源1162373<1310720；闭合已保留524288，足以覆盖本报告一次写/读/seal及固定identity收尾。两个delta1/2仍各1000 metadata/524288B未用；字节reserve1048576未用。文件统计/有限Git tree/hash核对没有SDK/tool/witness/index payload读取。metadata各阶段固定1200/3300/1000/1000/1500，实际仍null，不以本账或大数虚构实际合规。

本报告最终一次有界readback和seal长度/hash另记；此首轮文件将保留，不为下一候选覆盖。最终处置：R7固定源模型局部SUPPORTED；C1当前文档算式OPEN；全包HOLD / NOT_CALL_READY，fund及外部门禁未决。

## 首轮作者最终 seal

本次唯一完整报告readback 21811B；同一 held buffer 追加本 seal 后直接计算最终 bytes/SHA，不再读取报告。已知命名文件读取累计 1228815B。闭合已知payload为保护M15852B + 报告首次写/唯一readback各21811B + 本seal追加写，低于524288B；actual metadata/application/OS I/O仍UNKNOWN。HEAD仍68ffbb9dfab5790a1c076cf770e208b17eaa8d1b；仅保护M和两份独立作者新文件未提交，index空。两次1000 delta均未用，未提前审下一候选。R7局部SUPPORTED，C1 OPEN，最终HOLD / NOT_CALL_READY。
