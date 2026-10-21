# T03 N0 清单metadata修复独立实质审查

2026-10-22；独立reviewer：`n0_build_review`。

**结论：本固定候选的三writer最小metadata修复、两sidecar完整映射与解析边界在静态交付范围内可接受，无剩余实现P1/P2。第二次configure/build尚未授权；metadata漏项更正后超过已授400000访问，额度须根明确处理，超过原32GiB的拟议累计预算亦须另授，不能据本审查执行。**本结论不是构建成功，不确认原超时唯一原因，也不量化优化收益。

## 权限与固定候选

全文读3192B metadata窗口原文，SHA-256 `a2b2bc77a41c59e5ad4e3322d511cf4704a5e529f86bfbc96ea153e942fa164f`。仅准三writer解析修复、非执行数据sidecar及有限metadata验证；原失败、九源只读、两前门、原timeout/parallel/13命令保持。本reviewer只写本报告，没有修改实现或原件。

最终candidate-input-manifest.json为5211B/SHA `ba8d5036a70a2d37eea5f6602f133fdf32de948f0e6e18f8a81a33467fae026b`。实际三writer字节身份核同：

| 文件 | bytes | SHA-256 |
| --- | ---: | --- |
| `packages/native-location/CMakeLists.txt` | 19815 | `f2b5522b92c5dfc9724b95c35b876ce5015a4955385f614a6da20fb9bce57645` |
| `scripts/build-native-location.mjs` | 30056 | `ca4ef93024762ae5dfd3dc95133f8ab28ae2e63048af0b3a658bfeb98f62045c` |
| `packages/native-location/toolchain-lock.json` | 10474 | `bb74f5117e2efa6e5abf2d45bfaa0788a539dc502eb028f9819b4f8de6739a1d` |

该实现与两sidecar/3192授权/回执已固定于独立提交 `95f07d931eeffd3bdcd52cb21e9fa2d8a1db12bd`，实际parent为失败过程ref7bfd7c493698107fc70913e249d164cdb6515205，恰7路径；本reviewer核三writer current与该Git逐字相同。相对实际首轮输入c80cbcd，只改三writer。九原件current bytes/SHA已与原批准清单核同，完整产品/test仍为12；最终manifest的九身份一致。CMake原nl_pin/前置段及source/审批/平台/目标尾部与c80逐字相同；driver的verify/build/R5/main尾部亦相同，改动集中在inventory schema和纯解析。锁仅把两个Darwin inventory四pin包成严格source+records对象；source原pin、所有工具/源/合同pins及审批字段值未变。保留既有批准字段不等于根授予第二次执行窗口。

## 完整对应与来源保全

本reviewer仅从docs/Git metadata核对source原字节、全部roots/files及sidecar，不打开供应物。两source当前仍与c80固定Git原件逐字相同；28来源追溯链、fb40元数据和gnumake精确补项未被替换。derivation-receipt.json为3024B/SHA `61135378b9b335bf90592780f7f53c94cdbafee6bbdd1a9e51d6f0c1ab4a2942`。

| 集合 | files / roots | 原source bytes / SHA | records bytes / SHA |
| --- | --- | --- | --- |
| resource | 9308 / 10 | 4717464 / `42c30336dbcc6444222f2d2b3760fef04df7a0ec7c236ef849a0f76e7a2caa19` | 4718249 / `c7b4f3152c37a2558fd1d162b3c627b4591d247f9ee0f72256514c560ec8f480` |
| SDK | 33464 / 1 | 14649771 / `ba16d77b0668329b861290b3ef638818bc4c08b295944d39210323c9cda8d3ff` | 14649961 / `26831cc3c72a429f6d0c84abc34743ceeecc63fe7ae1295930f41ee4600efc19` |

独立完整比较42772项四pin与roots顺序全部相同，path/realpath/bytes/SHA无省略、重排或替换。header精确format/count/roots/prefix/suffix；把prefix、逐行raw记录以逗号连接及suffix拼回，逐byte等于原source。sidecar均ASCII+LF且有末LF；resource最大row595B/header1481B，SDK719B/308B，均低于4096/8192；source和records均低于16MiB、files低于50000、roots低于64。合法0B hello.f保持，SDK未按used-only裁剪。没有以新sidecar覆盖旧JSON或把目录/链接假装为regular pins。

## 源码实审与已关闭边界

CMake先核source/records期望和actual SIZE在16MiB内，再nl_pin/hash/READ；不存在先按任意大pin读完再拒cap。source只做固定次数TYPE/字段/roots/count检查，roots缓存为indexed变量；后续字段GET仅对当前小row。字节重建证明并不是“Node先验过所以CMake跳过”：CMake仍独立验证两元数据pins、严格边界、完整source映射、根覆盖/重复，再运行原逐实体nl_pin的realpath/size/SHA核对；仍在project之前。

初版file(STRINGS)加raw CMake list的实现实际失败：resource正确，SDK行数被截为19714而物理行33465；唯一合法`usr/share/man/man1/[.1`在files第19713项，path和realpath的未配对左括号破坏了list分隔。小型单行正例并不能覆盖该后随多行情形。本reviewer核见原完整metadata结果exit1，及时反馈；原失败结果1110B/SHA `8b0fd7da90ff626400cded4297b236146601df16d5cd0555c4f115d9c6466de9`及初始harness/原件保留，没有被后续成功覆盖。这是本次metadata实现失败，不能反向当作原configure ETIMEDOUT的已证原因。

最终v2用fileREAD后可逆@A/@B/@L/@R/@S数据容器保护@、反斜线、方括号和分号，再仅以LF分行；@A最后恢复。encoded列表跨函数返回并保留至实体循环，只解当前item；整join后再整体decode。roots不再经raw list传递。此机制只保护CMake数据容器，不手写解码JSON字符串，不eval/include前后缀或供应文本。

CMake对header/row作有界固定key顺序的完整flat语法匹配，实际转义/值读取仍用JSON parser；不是regex拆大JSON。prefix+sentinel+suffix经JSON parser确认slot恰为files数组，字段/roots/count与原source一致；source重建SHA及canonical records原bytes重建SHA分别核对，拒绝空行、CR、BOM、缺/多LF、CMake规范化/转义漂移。每path摘要键查重，重复或键碰撞均拒；没有增长IN_LIST重复扫描。

Node严格source对象/roots/files、JSON重复key和四pin，每source只完整解析一次，再逐small row核对顺序和对象；UTF-8先作等字节往返校验，避免replacement静默接受坏records。split上限为source count+2，其后重建records整Buffer核原bytes，故额外尾部不能被limit截断后漏检；source bytes亦独立重建。metadata验证后仍对全部v.files执行原checkPin，0B只在实体清单允许。CLI/源/平台/审批和R5不放宽，没有metadata-only绕过产品前门的新CLI。

结构上移除了每file字段读取整份大JSON及增长list查重的二次风险；仍有固定次数全文校验、每row小解析及最多64根的有限containment循环。此为代码结构判断，不是性能测量，不能预测后续configure必然成功。

## 已有验证原件与未重跑范围

仅读实施者保存的真实命令、结果和双流，没有由reviewer重跑。最终Node纯metadata24例全部匹配（含完整两清单、UTF-8/截尾、根/重复/字段/长度及转义）；CMake v2有限19例为5接受/14拒绝，均匹配，包括后随row的未配对括号、括号root及transport token/backslash。v3另2例证metadata cap和digest-key collision拒绝。

v2完整42772 metadata-only CMake-P结果exit0，stdout明确resource=9308/sdk=33464、physical supplier loop NOT RUN，stderr空；原件855B/SHA `b83bcfc82f253b731ae909f35b91be6f5a3a4d73d8d7e01ced21c1676537405a`。本reviewer核当前CMake helper原字节确含在已执行v2 harness中，函数SHA `403946fd393feff41af5cf58ae4c39c240abba560e6866d25c7dccd38890b6ee`与v3记录一致。harness只调用metadata函数，虽定义实体函数但没有调用，无project/compiler/逐实体loop。Node VM也只抽取纯解析段，不执行产品main/CLI，context不提供供应fs读取。

最终Node --check、目标Prettier --check均exit0，最终24例stdout/空stderr已核；static格式写入记录也如实保留。这些是许可内有限metadata验证，不是configure、性能benchmark、编译或产物测试。没有重新执行六verify-only造成大供应重复读取，没有第二次构建。首轮失败继续固定在7bfd7c493698107fc70913e249d164cdb6515205及原目录/日志，先前实际IO与进程未知不被本次成功冲销。

## 计数更正和第二窗口的账界

当前read-and-parser-budget.json为6093B/SHA `d69fdc6b3731ea34a802c2c49034d7d5beec86f5c7387daf017bb4ce225afc24`，保留旧223168口径和逐项更正理由。原供应9745727085B和构建32GiB=34359738368B均未清零或本地扩大；本窗口实体pin验证/读取为0，不包含loader/kernel/cache的未测IO，后者仍null。

首轮声明上界17678194976B不是实测全读，实际IO仍null、CMake完成实体数未知。拟议下一轮两前门payload+metadata声明17755667816B；加首轮上界、两个256MiB收尾reserve和本窗1GiB metadata reserve，保守累计37044475528B，比32GiB多2684737160B。reserve是预算，不是实际字节测量。根须根据具体新候选给下一次精确累计界，当前不能运行第二次构建。

计数也须透明：owner最初报223168（Node4轮×42772、初次CMake resource9308、v2完整42772），它只是显式row校验循环旧数，既不是完整metadata访问，也不是实体验证次数。本reviewer另做一次完整source↔sidecar核对，访问42772 source对象及42772 sidecar对象，共85544解码对象；此前为定位list问题完整扫描42772行括号计数，仅异常行额外JSON解码，另有有限结果/字段阅读。逻辑清单访问、表示层对象解码和纯行扫描不是同一个计数口径，不能只报42772掩盖重复，也不应混充实体物理读。随后全文读根1941B账澄清，SHA `6a977275278d7f9813769f0918cde83399b0754c78f34c99afc6ae0d46b5af4b`：实体guard仍200000，纯metadata逻辑record本窗上限400000，1GiB reserve计入原32GiB。此后owner如实更正：223168只含显式row校验，漏source解析、格式探查、派生和list诊断；不能用漏项合数351484/356604签满足400000。按source/sidecar对象各计一次pipeline访问，owner更正608116，加reviewer128316为736432，再加有限小例/收尾1024/4096后741552。JSON库内部重复不混入逻辑对象计数，byte hash不另算record，但不得因此漏掉完整pipeline访问。原小账与更正理由保留，当前400000不足；750000仅为提交根的精确申请，在正式补充授权前不签额度已覆盖，也不再重复全量。

因此静态实现与完整映射可接收；metadata漏项已经披露，但额度覆盖仍待根精确处理，执行门同时关闭于第二构建及新累计字节界未授。1941不授权40GiB或第二次运行。下一步只能按根对固定候选的精确许可推进；不可延长600000ms、无变化重试、跳CMake门、移project后、删SDK条目、扩大root/CLI/env或改I06消错。native/child/CTest/try_run/addon/Electron/目标OS/生产位置及原Goal仍不在本次通过范围。
