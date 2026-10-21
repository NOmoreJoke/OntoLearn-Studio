# T03 N0 首轮构建结果与清单复杂度独立定点诊断

2026-10-22；独立 reviewer：`n0_build_review`。

**结论：首轮实际driver失败，CMake configure的dispatch被spawnSync记录为ETIMEDOUT；CMake build未尝试，没有可签的构建或测试通过。** `nl_inventory`存在显著的重复大JSON处理和增长列表查重风险，是须处理的静态嫌疑；现有原始日志不足以证明它是本次超时的唯一根因或确定停在某一行。修复/新增运行须另获根精确授权，本报告不实施产品改动或重跑。

## 读取范围和实际输入

仅只读新增结果/原始日志与双流、当前固定CMake、已固定resource/SDK元数据，以及纯计数算数；未重读hash供应实物/SDK/cache/归档，未执行driver、CMake、probe、benchmark、验证、测试、进程检查或任何FS实验。唯一写本诊断，不改三writer或I06九原件。

实际批准输入ref `c80cbcd193f8cb64a98c97378bbdf61756701e27`；supplier的Git HEAD stdout与此一致。preflight记录的三writer是CMake13648B/9455d850…、lock9189B/e9e18a77…、driver27325B/14e15fdf…。当前所读CMake仍为该9455d850固定身份。

唯一构建目录：

`build/native-location/n0/darwin-arm64/ab080da43ab7edecf6511fc8b0b2ee3ace6c9712512ec906f941ae22261c791a/core`

最终 `supplier-log.0060.json` 21825B，SHA-256 `e0cd0a86deeb7137253181b16c9f7f7def0cd942abc96a0b7e4734a2a5c913c9`。`build-once.result.json` 1079B/SHA `ae861105f5e3f408cb11fcb5abced4ddf20ce794a819eca9f8024f4ee712af4f`；`build-once.stdout` 894B/SHA `560df9d174d9b1e2f416edd7a89857a5c5f101e8d86e568d848b9b0d9e17155d`；stderr 0B。它们为本次结果依据，不用进度转述或外层wrapper出口替代driver实际出口。

## 已观测结果

精确原命令为 `/usr/local/bin/node scripts/build-native-location.mjs --target darwin-arm64 --component core --build`。结果JSON记录driver exitCode=1、outerDispatchOutcome=returned；外层封装命令返回0不表示driver成功。起止17:46:19.002859—17:56:35.704776 UTC，整个外层过程约616.702秒；这包括preflight/Git等，不是configure自身CPU时间或逐步计时。

| 阶段 | 原始记录 |
| --- | --- |
| Node输入前门 | complete-readonly，mode=build-preflight，gaps空，lock SHA/inputDigest与该目录匹配；这不是built-unverified。 |
| 0：产品状态 | git status exit0、stdout空，outputValidation=matched。 |
| 1：HEAD | exit0，stdout为c80cbcd换行，matched。 |
| 2–10：九source Git blob | 均exit0、outputValidation=matched、无stderr错误；未由此运行I06产品。 |
| 11：CMake configure | call-returned、attempted=true、child-pid-reported=73337；run status=null、signal=SIGTERM、error.code=ETIMEDOUT。 |
| 首失败 | commandIndex=11、phase=spawn-result、code=ETIMEDOUT，与run error一致。 |
| 11双流 | stdout和stderr各0B，fd状态closed；无编译诊断或阶段进度文本。 |
| 12：CMake build | phase=planned、dispatch=not-attempted/false、run=null、两个output仍not-opened；没有继续build。 |
| 日志/清理 | persistenceFailures空、该失败命令cleanupErrors空，最终snapshotPhase=command-final；首因未被覆盖。 |

实际configure argv固定Unix Makefiles、绝对gnumake/clang/clang++、SDK、arm64、最低15.0及RelWithDebInfo；原源码该工具dispatch的timeout为600000ms。ETIMEDOUT已发生可以如实记录；不能把整个外层616.7秒精确说成configure运行时间。

实施者同时报告没有CMakeCache、compile_commands、objects或两个目标产物；本复审依其本次观察陈述，没有另行扫描产物树。日志本身只足以证明没有成功返回configure、build未dispatch及无工具双流，不能从0B单独证明CMake停在哪行，也不能证明未曾产生任何子compiler活动。没有产物/测试通过可用，tests仍NOT_RUN、dependencyClosure仍PENDING_POST_BUILD_AUDIT。

## 当前CMake的静态复杂度

`nl_inventory`读完整manifest到局部NL_JSON；`nl_get`每次对完整NL_JSON执行string(JSON GET)。每个file的nl_pin为path/realpath/bytes/sha作4次GET，外层又读realpath1次；每个root的containment循环还再次GET根。计数/初次roots处理也使用完整manifest。

因此完整遍历时，大JSON操作数为：2次LENGTH + R次初始roots GET + N×(5+R)次逐file GET。用实际固定元数据计算：

| 清单 | files N | roots R | manifest bytes J | 全文JSON操作数 |
| --- | ---: | ---: | ---: | ---: |
| gnumake resource | 9308 | 10 | 4717464 | 139632 |
| SDK | 33464 | 1 | 14649771 | 200787 |
| 合计 | 42772 | — | — | 340419 |

这并不是每file解析一个约数百字节的小pin对象。按每次string(JSON)处理输入文本的保守模型，规模为O(N×(5+R)×J)，J又随N增长，具有二次规模风险。理论重复文本操作数×输入bytes约3600192503025B（约3.6TB）；**这是参数文本规模，不是实测磁盘IO、内存分配、实际解析时间或供应读取费用**。CMake具体内部实现/缓存、调用分布和CPU占用未作profile，不能把该模型伪装成测量。

另有 `if(p IN_LIST seen)` 对不断增长的CMake list逐file查重。若按线性成员查找模型，两个清单非重复路径对的比较规模约603217694；这是第二项二次风险，不是实际比较次数观测。每次pin的文件SHA和realpath校验本身则有独立供应IO成本。

`nl_inventory(resource)`及`nl_inventory(SDK)`均位于project之前，且当前没有阶段输出。故“没有Cache/objects、双流空”与前门耗时一致，但同样不能排除其它pre-project步骤或工具启动因素；没有trace/进度/stack证据证明本次已经进入哪一个清单、处理了几项或耗时归因比例。本报告不将静态嫌疑升级成确认唯一根因，也不把超时归给尚无编译诊断的I06源码。

## 须另批的保守最小修复范围

建议根只授三既有构建writer及派生元数据的有限解析改造，不改I06、不换工具/SDK/目标、不改变运行边界：

1. 保留driver和CMake两道完整前门及逐file绝对路径、realpath、bytes/SHA、root containment、重复/数量/0B等规则；把大manifest的一次解析或受pin约束的小记录读取作为目标。较稳妥方案是从已固定JSON仅派生小header+逐行四pin JSON记录，固定sidecar身份、与原JSON集合逐项核同，原JSON及历史原件保留；driver一次解析，CMake仅对当前小记录调用JSON getter。sidecar格式/类型/字段/行数/总量上限与原manifest对应均须明确校验，不能只信调用者口头“已验”。
2. roots在进入file循环前一次取出缓存，不逐file重新解析整份manifest；同一file的realpath复用已取值。查重改为路径摘要键的已见集合并存原path，重复或摘要碰撞均拒绝；避免增长list反复扫描。这些只改常数仍不足以单独解决N×J问题，不能把“每行先GET整个file对象”误当单次解析，因为该GET依然输入整份大JSON。
3. 加有限阶段进度/开始完成计数，使以后可以区别resource、SDK与compiler probing；不输出额外供应内容、不产生全路径刷屏，不新增进程探针或benchmark。固定原件/JSON对照只读推演和静态独审后，仍需根授权新的精确configure/build窗口。
4. 新三writer/lock/sidecar pins须固定完整12产品/test及过程身份，新inputDigest和独占新目录；本次目录、0060首失败、空双流和所有旧snapshot不覆盖。原600000ms/parallel2及首失败停止策略保留，不能无变化循环重试。

不得用正则盲拆JSON、跳过CMake输入校验、把校验移到project后、删SDK条目/缩成root摘要、放宽未知字段/CLI/环境、扩大roots、调长timeout“求绿”、加入测试/try_run/产物加载，或改只读九源来绕过问题。若实现超出上述具体数据格式/解析范围，先给精确delta由根另批。

## 未观测和计账限制

`build-once.result.json`中measuredActualIOBytes=null。Node前门完成和CMake部分执行可以记录，但不能虚构CMake成功校验了多少files/bytes；上述3.6TB文本模型尤其不能记为实际供方读取。后续费用仍按授权分账：原供应阶段9745727085B不清零，本次构建阶段实际已耗和未知部分保留；无法测细粒度时区分声明校验上界、成功/中断和实测，重试前据剩余guard精确预算，不自动扩32GiB。

PID返回及SIGTERM/ETIMEDOUT记录不证明完整进程树/资源已经排空；本复审没有额外进程探针或清理，因此保该未知，不泛kill。当前也没有证据评价macOS15、Windows、Node/Electron、native资源终态或生产位置。唯一首轮失败已保留；需要的下一步是精确解析修复授权与新候选静态核验，不是把准备或wrapper成功记成N0通过。
