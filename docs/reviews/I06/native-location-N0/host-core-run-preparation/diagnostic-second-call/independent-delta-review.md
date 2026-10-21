# 第二诊断调用：六值准备增量独审

2026-10-22。仅审准备数据，**PREPARATION_ONLY / NOT_RUN**。结论：授权的六位置精确增量、非cmd参数、新pair只读指纹均通过；无新增 P1/P2。发现的窗口来源 P3 文案已如实纠正，见下文。此结论不是 CLI 运行许可或 N0 技术通过；根读回固定过程后仍须另授002窗口。

## 固定模板与实际读取

唯一模板：`b942e12cd122873109f4bd16d51e06e05ad7005d` 的 `docs/reviews/I06/native-location-N0/host-core-run-preparation/concrete-call/exact-tool-call.preparation.json`，18740B/SHA256 `c5c660d7df87e4d1b158e93b8d42e8816f978df74290a286c982d79456d0d22d`。从固定Git字节读取其arguments，未运行或重新审查旧控制算法。

已全文读当前根准备窗口与T03受限收件文，实际根文件均与本目录快照字节一致：

| 根原件/快照 | B | SHA256 |
| --- | ---: | --- |
| I06-N0-diagnostic-second-call-preparation-window.md / preparation-window.corrected.md | 3110 | c8505d20dfffb560f4fbdafd209b0a3afde55f05d2b7682ab4a33a53d68d76b3 |
| T03-fourth-diagnostic-build-root-closure.md | 1630 | 98d279fb0976fa0b8b1b1d1487656026fb7efdc6b275847920a4ba633e73025b |

实际读取新完整调用JSON、cmd原文本、六值patch、当前与初版静态记录、handoff、preservation-check及新增来源说明。所有命令显式cwd为 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-native-location-N0`；只做Git/JSON/AST/字节/hash及两已授权实物只读，没有执行候选（含guard）、编译、API探针、产品check、native/core/probe/addon或GUI。

## 六位置精确一致

新 `arguments.cmd` 与 `exact-cmd.preparation.txt` 逐字相等。与b942逐行比较，恰六行不同，1起行号为4、5、6、24、240、241；将这六行还原即与b942整个cmd逐字一致，注释、shell首行/终止符、空白及其余文字均保留。

另独立解析两Python here-doc为AST数据，只在以下精确节点恢复旧值后，全AST一致（未eval/exec/import候选）：

- AUTHORIZATION → `I06-N0-execution-002-a0e724fdf90afa98`；CORE_PIN/PROBE_PIN → 已受限收件的新path/bytes/SHA。
- RUN的右侧字符串 → `/execution-002`，BASE和运算符不变。
- 原exclusive `os.mkdir` 与原run-directory `os.open` 的首参 → `execution-002`；其它参数/flags均不变。

这不是全局替换所有001字样。所有非cmd工具参数逐值相同：原I06绝对workdir、login=false、yield_time_ms=1000、max_output_tokens=1000。未改算法、时间/信号/等待/清理、限额、外层env或存在即停行为。本轮未以“修目录”为由复用/移动/删除旧001或创建002；目录未创建和旧原件不变的额外全树核验是主线preservation记录，本子任务未另做FS/进程探针或重复旧大审计。

新调用身份：

| 载体 | B | SHA256 |
| --- | ---: | --- |
| exact-tool-call.preparation.json | 19350 | 42b1f04107e3e2404ed79cdaeed4fa0ac80fea093780dafbd4b16352c3615a60 |
| 完整cmd / exact-cmd.preparation.txt | 17176 | be0d1fc7518e281353206ec25e43f579dba9821035b46ee3161e76aac7fc2705 |
| 实际here-doc stdin（含末尾LF） | 16976 | 9f6f4b99b63aab6be937617aab7c9dad605a5ab5a54a1b54cfc6c33621d4c2a2 |
| delta-static-check.json | 3710 | f71b21e176c9725f0bb89036fd0c2edf9c82ee469245f53c6b12e7c56177d429 |
| exact-six-values.patch | 2418 | 10ca6d263c3aeaad7fd4371c9f4d6360d60264f82df1086a015f3baef2175107 |

## 新pair只读实核与来源边界

根收件的固定供方输入 `d98b503ebe9c477d30d0f36d831cffbeeaf2a988`，过程 `d51a0555e6feb062fc935173222cc142687901a5`，digest `a0e724fdf90afa980f01719fc8cc4d55f158400cf5abe26665c72a2d288cac77`。root closure明确两源采用fc、其余七源/构建闭包受限收件，仅built-unverified/NOT_RUN；本轮不重复204项闭包、依赖witness或旧三轮来源审计，也不将收件摘要当我重跑构建的证据。

实际仅对以下两精确路径读取字节计算SHA，并读metadata，与新pin、窗口、root closure一致：共同绝对目录为 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-native-location-N0-build/build/native-location/n0/darwin-arm64/a0e724fdf90afa980f01719fc8cc4d55f158400cf5abe26665c72a2d288cac77/core/artifacts/`。

| 文件 | B | SHA256 | dev / ino / mode |
| --- | ---: | --- | --- |
| location_core_test | 343920 | d4f5ca322146d9696860a74de4bee2ad27866a2223340669898fb82cbbfeb817 | 16777232 / 66596754 / 0755 |
| location_child_probe | 34120 | 21928ca2b5570055fad4bebcd81fcb658016ca9a738294397a83056b662b87e8 | 16777232 / 66596825 / 0755 |

这些指纹是当前只读观察，不证明运行结果，也不替未来精确调用自己的pre/post核对或冻结窗口。旧 `result.sourceRef` 依六值授权继续保留 `b59239f9c1ec2774c7922f95dfc67db4dc8754e8`；它只是历史模板字段，**不能表示新源/新pair provenance**。未来若获运行，归档须同时绑定新供方refs/digest/pins、精确cmd和002独立授权，不可只按旧sourceRef归类，更不可复制旧001失败结果充新结果。

## 来源叙述 P3：已纠正

首读handoff曾把同名窗口快照称“原首版原字节”、corrected副本称最新，容易误认两份不同历史FS原件。实际本子任务所见两件始终同为3110B/c850…d76b3，都含目录更正。本轮已向主线指出；最新handoff和 `window-provenance.json` 明确：第一次实际落盘已包含更正；更正前全文仅来自主线首轮工具输出，未捕获当时FS hash。

新增 `first-read-window.transcript.md` 为2252B/SHA256 `e2aa4ba47e93a1cf499a7a24d8f61c795d6d2f01be339b787067345cfffd4df5`，可由更正版恰去除后增更正section得到；这是工具文本重建/留存副本，不认证为当时FS原字节/hash。本子任务没有亲见更正前FS文件，不把该副本倒签为FS快照。

`initial-three-value-static-check.json` 原2870B/SHA256 `ac4dd4c8edb57ca6867e5a75061c1cb844a086675392c057ef1c671775a6d58f` 保留三值准备记录。首版规格不完备属于root准备更正，未执行、不是运行失败或第二次重试。最新handoff3851B/SHA256 `40dffe59ab9e8e3a069b7a1b42f9a2e3e4b88897fbec5157bed4293df4f532ed`，来源JSON757B/SHA256 `0649e9a3940ba253e98f2a68956c744258500f6f973e08dbaef7d321bd73fe8d`；来源区分足够，P3关闭，无倒造旧FS版本。

所有核验为静态/只读且工具退出0。未改候选、源码、旧原件、Goal或提交；仅新增此报告，交最终bytes/SHA后停止修改。首次失败根因、新诊断输出、native drain、EXCL、目标OS和全部父门仍未关闭；本报告不授002执行。
