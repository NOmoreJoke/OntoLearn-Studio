# T03 N0 工具供应材料独立只读审查

2026-10-22；独立 reviewer：`n0_build_review`。

**结论：本阶段材料、分片和探针证据在下述只读范围内可接受；总体供应仍为 incomplete，不能采用为已闭合工具链，更不能签构建、目标 OS 或 native 通过。81个系统 cache 对象未 hash、内部传递依赖解释及组件条款缺口均明确保留，全部候选审批 false。**无须因这些已如实披露的缺口否认已完成的 CMake 提取、SDK/resource 清单及13条元信息探针。

## 授权、审查输入与读取边界

全文读原6465 bytes授权 `T03-native-N0-tool-extraction-and-supply-inventory-authorization.md`，SHA-256 `1e47f7fa6d12763a41fd20f9b06e8a71821aa8d7d58d0bd21e3c3c14d3583a34`。该阶段工程guard是200000项/8GiB累计读取；本报告仅审截至原末账2699211379B的材料阶段。后续另授10GiB的81 cache定额补充另有窗口，本报告不预判该补充结果，也不覆盖其读取。

本 reviewer 仅读取本目录 JSON、JSONL、文本和已有脚本文本，对 docs 元数据/分片字节重算 SHA，对记录作计数、集合、摘要和算数核对。没有执行任何已有脚本、重新提取、探针、版本命令、构建/业务/native/FS实验；没有重新打开/hash实际归档、大型SDK、compiler或系统cache对象。供应物原始内容 SHA 是材料 agent 的实测证据，本 reviewer 的独立核验是证据文件自身身份及其内部对应，不能冒称独立重测实物。唯一写入本报告；原件、原报告、产品、锁和审批均未改。

固定原阶段关键输入（本 reviewer从 docs实际字节重算）：

| 文件 | bytes | SHA-256 |
| --- | ---: | --- |
| `evidence-manifest.json` | 14884 | `eb36202a3da0e4f0693e800ca36e0c25a1b10dbf4003b64339249683ada22f78` |
| `candidate-pins.json` | 12011 | `d17e5ab336d71f622904adcc806adb1789b70555679768372ee2ab52e5fb6b2d` |
| `index.md` | 4986 | `f98762eac7f65fb4dabc7efff5be9f8a3e152acebb5ee333c5f576b9c7f1461e` |
| `inventory-parts.json` | 2631 | `305f1b395387c50e096fbec718a00a771786c206846075f3592c71e78141d23a` |
| `probe-index.json` | 39108 | `668019c57bb9350ee43a0341fda97a2d7193157aaa506d278422a844fabb4763` |
| `unhashed-system-cache-objects.json` | 24420 | `a0a368c44eec7843270d9f65a517bf43fa546e3766aeeb3fceeea82b80c6f08c` |
| `read-budget.json` | 378 | `32ef2836d14e348f6e5919eeade542d08322f48d109f2c01d6c88f657587bd42` |

原 evidence manifest 的92个 records全部 bytes/SHA匹配，包括分片、probe双流/预执行/结果、脚本及条款副本。它不循环收录自身；owner后加的授权原文副本也不在该材料manifest中，授权身份另核。verification.json的91是其生成时验证的先前证据数量，随后它自身列入末版92条manifest；没有据此推成遗漏一份供应物。本独审及后续dyld增量文件不属于该固定manifest，不要求倒写原件。

## CMake提取与首次失败

提取记录绑定原source-index `e6eea559…`、官方归档89454352B/`4b7b7370…`及checksum唯一basename，未替换成latest。两个JSONL共9041条 archive member记录：8839 regular、189 directory、13 symlink；路径唯一，常规文件合计252707197B，逐项archive/actual模式、bytes及SHA字段一致。合法0B `Modules/IntelVSImplicitPath/hello.f`保留，未被非空工具约束误拒。

归档省略的外层父容器另记1项（mode0700），所以实际提取对象9042并不与9041原member矛盾。首失败文件明确保存首轮因缺省容器而停止、regular提取0/probes0、原空目的地；第二轮使用新的 `cmake-distribution-v2`，没有覆盖失败目的地或抹首因。报告声明安全顺序、无extractall和无额外/缺失member；本 reviewer核这些记录之间的一致性，没有再次遍历tmp树或重读tar来重做提取审计。

CMake26639440B/`80cbc0d5…`、CTest29114000B/`3c91499c…`的授权预期与提取/预执行pin记录一致；两条真实--version双流均为4.4.4。这可以关闭本窗的精确版本观察，不能代替configure/build或任一测试。

## 分片、覆盖与摘要

11个供应JSONL（前10片各5000，末片3092）合53092条；2个CMake JSONL为5000+4041。全部13片的bytes/SHA/JSON记录数与inventory-parts一致。供应path唯一，其类型计数为11003 directory、33944 regular、8145 symlink；加CMake9041和隐式容器1，共62134，低于200000项guard。没有把directory/symlink误当必须有file SHA的常规文件。

本 reviewer按候选给出的排序和JSON canonical规则从现有分片重算下列对象摘要，均精确相符：

| 对象 | 条目 | regular声明bytes | canonical记录SHA-256 |
| --- | ---: | ---: | --- |
| 整个canonical SDK树 | 52590 | 931393813 | `5c18955bb10578d36788191207541206a8d51aacac219b1828aefa8c638a1811` |
| toolchain usr/include | 7 | 30603 | `54b8b9e26aadc942bdc835a13b829eee559777b17e63b73e4f89aafce22c8ee7` |
| compiler clang/21 resource/runtime树 | 380 | 80801250 | `00759e8350f201c6b54d57b5760b85328faf037b20ff62cf61829f4e6c22f9fa` |

SDK 33464个regular全部带SHA，resource/runtime的363个regular全部带SHA。供应记录明确涵盖headers/modules/framework stubs/SDK库与settings，不是仅列SDK根摘要；实际xcrun返回的MacOSX27.0.sdk别名、canonical MacOSX.sdk、compiler include指向SDK的链接及相应realpath分别记录。现有symlink记录的realpath均落在声明合法roots内，无声明外例外。静态枚举脚本文本采用完整root walk且不跟随外部symlink，未见将业务路径混入供应遍历的机制。本审查确认该范围及记录完整对应，不能只凭分片证明当前物理树没有后续变化，采用前仍须按根的精确授权核验实物。

按已有SDK JSON记录构造可供driver的roots+files四pin字段（仅33464个regular）作纯内存序列化算数：紧凑UTF-8为14649770B，indent2为16055278B，均小于16MiB=16777216B，且files<50000。故未发现SDK清单“必然超driver上限”的未来P2；不需扩大产品上限。此为既有数据计算，不是生成或运行采用manifest，也不将52590个全type行直接塞入regular file pins。链接/目录原始身份仍保存在全量供应记录。

## 13条真实探针与边界

probe-index中的13个label唯一；逐项与其预执行JSON、结果JSON、candidate executable pin、stdout/stderr副本字段和bytes/SHA对应。各命令timeout30秒、各执行一次，均exit0、无signal/timeout，13份stderr均0B。全部原argv、cwd、明确传入环境、path/realpath/bytes/SHA及起止时间都存在；没有用静态plist冒充这些命令。

| 类别 | 固定实际命令 | 观察值 |
| --- | --- | --- |
| CMake/CTest | 提取绝对binary各--version一次 | 4.4.4 / 4.4.4 |
| Xcode | /usr/bin/xcodebuild -version | 27.1 / 27A9275 |
| SDK/解析compiler | /usr/bin/xcrun的SDK path/version、find clang/find clang++共4条 | SDK27.0及固定Xcode工具路径 |
| Clang | 实际clang/clang++各--version及-print-resource-dir，共4条 | AppleClang21.0.0、clang/21 |
| make/git | /usr/bin/make --version、/usr/bin/git --version | GNU Make3.81 / Apple Git2.54.0 |

环境为保存的继承元信息子集，PATH沿用原值；不将其说成未来driver的最小构建环境，也不据此免除工具/包装器和runtime供应核验。成功版本命令只证明这些精确元信息，不能签macOS15、宿主构建、Windows、Node/Electron或native资源终态通过。

## guard末账、依赖与条款缺口

分片中恰81个regular的sha256=null，均为NOT_READ_GUARD_FULL_CACHE_SET_WOULD_EXCEED，path集合与unhashed-system-cache-objects完全相同；bytes合计7046515706。其余regular均有完整SHA记录，重复物理对象有明确复用身份而非假装再次读取。cache组另1个1503877B map已hash；map不是cache body。

算数按原阶段末账独立复算：

- 8589934592 − 2699211379 = **5890723213B**剩余读取额度。
- 7046515706 − 5890723213 = **1155792493B**最低guard增量。
- 2699211379 + 7046515706 = **9745727085B**，超过原8GiB；这一最低增量仍不包含继续解释内部image依赖可能需要的额外读取。

126条静态load edge有原记录；21个缺独立落盘对象的系统install name在现有cache.map证据各有一次精确名字命中。本审查核21条记录及与声明的对应，未重读实际map/cache。名字/地址文本命中不证明cache所有body身份，也不证明其嵌入image全部传递依赖已列齐或实际被某次构建加载。index/candidate/hash-report明确说整体INCOMPLETE_EXTERNAL_SYSTEM_RUNTIME_CACHE_GUARD，未以map代替实物hash或完整依赖闭包。

有一项必须保留的时间层次：supply-declaration-final.json的read_bytes_before_hashing、remaining_read_budget=7170636196、minimum_additional_read_budget_for_full_candidate_hashing=1278399410，以及“image membership not yet proven”，属于较早声明。不能把这些混作末账；最新read-budget/hash-report/candidate和本报告使用2699211379/5890723213/1155792493及后来map证据。已向owner指出，owner将另文澄清而保原始阶段记录，不倒写历史。这个早晚层次不改变总体incomplete，也不是供应通过依据。

terms-index保存Xcode/Apple SDK Agreement原RTF、LicenseInfo的EA2002/GM及CMake BSD许可位置；本地有限查找未齐GNU Make/Git等独立组件完整notices、系统cache per-image条款，均显式列gap。没有把GNU版本输出或Xcode总协议替代所有独立许可，没有代接受新条款。candidate的toolchain/execution/source/bindingMinimum/testAssembly审批全部false，root adoption required=true；此次材料交付没有自行切为true。

本阶段证据及诚实缺口可接收，完整供应采用保持待根核验。后续cache读取增量应以另批窗口和新增记录审，不改本阶段未读事实；构建前供应与构建后真实used headers/depfiles/link inputs、目标行为仍分别待证。没有借材料审查关闭R5之外的执行窗口、I06九源、生产接线、D2或原Goal。

## 追加：固定81项dyld读取增量的有限静态复核

此节仅追加，不修改上文原8GiB阶段事实。全文读后续2347B精确授权，SHA-256 `b9da09643f78d64e506e20fd4c81d8b8a058c49134124b18b46e9580b449b95c`，并核tool-supply中的授权副本与根原文逐字一致。它仅将累计guard提高至10GiB=10737418240B，允许原a0a368固定81项各一次流式哈希；未扩目录/架构、原62134项计数未增加，也未新增进程或编译/加载许可。

本 reviewer只读新JSON/JSONL/文本及6548B读取脚本的源码；没有运行该脚本、重读/hash cache实物、再次探针或扫描目录供应物。以下是对材料agent既有实测记录的独立元数据复核，不是第二次物理hash。

| 新增固定证据 | bytes | SHA-256 |
| --- | ---: | --- |
| `dyld-delta-manifest.json` | 1777 | `391975b7c4fe46a01801d2d921970269becdd1f880981b633fb111eb20a8a00c` |
| `dyld-delta-complete-inventory.jsonl` | 72003 | `c068eab60f2cbd8a46dcfa18701a319613ad3066f674d64c1dda65017e664d92` |
| `dyld-delta-read-events.jsonl` | 116944 | `645403562beb8d3c3ed43d89ea879ca938eb1d1754fcd52da26b13fe1d026c36` |
| `dyld-delta-cumulative-read.json` | 277 | `f54dad793f5b93a55ec7c88dde12e896bb5147b29fa332ae3feedc41ef16589e` |

新增manifest的10个records全部bytes/SHA匹配；独立重读旧docs元数据核旧92条evidence records及原pending list、budget、candidate、manifest、index五件固定身份均未变。没有倒改旧unhashed列表为“过去已完成”，没有把新原件塞入旧manifest。本报告本节也不属于这两个已固定manifest。

对81条complete inventory逐条与原pending列表按序核对：ordinal=1..81、path唯一、expected_realpath等于原realpath、expected_bytes等于原bytes且等于bytes_read；没有新增、遗漏或替换对象。每条都有完整64位小写SHA-256字段、开始结束、正向时间和COMPLETE_IDENTITY_AND_FULL_HASH状态。前后记录的device/inode/mode/bytes/mtime_ns/ctime_ns六字段完全相等，bytes符合固定值。脚本静态可见先lstat常规非链接身份/realpath/size，O_NOFOLLOW打开后fstat匹配，按剩余大小流式读取并计实际返回bytes，EOF检查后再比较fstat/lstat；未见新目录枚举、内部image提取或执行机制。fstat比较通过由脚本及成功记录证明，但未把未单独序列化的fd stat或未采集的其它stat字段冒称逐字段原始证据。

162条事件恰为每项一个preflight-identity-matched和一个complete，顺序与inventory一致；preflight所带累计为前一完成值，complete内容与对应inventory逐字段一致。逐项累加实际bytes得到7046515706B；末条累计和result/budget/supplement一致。first_failure=null、pending_exact_paths空、81/81完成，未从空字段推导实际资源排空或跨文件原子快照。

新费用独立核算如下：原累计2699211379 + 新增7046515706 = **9745727085B**；10737418240 − 9745727085 = **991691155B**剩余。没有计零重置、减掉旧耗费或误把原8GiB的1155792493B最低增量当实际新读取量。此账口径为原累计加获准81供方body实际返回bytes；新增授权/JSON证据读取是元数据，记录未将其冒称第二次供方body hash。

**增量结论：固定81项cache供应对象的身份和完整hash缺口，可按这些记录在本次授权范围内关闭。**上文“81项未读”是原阶段历史；新增候选补充准确保持runtime内部image传递依赖、postbuild used闭包、跨文件原子快照均未证明，组件条款仍缺，五类approval全部false，root adoption required=true。因此总体工具链供应/采用仍未闭合，没有因为cache身份完成而签构建、macOS15、Win/双OS、Node/Electron、native终态或生产位置通过。
