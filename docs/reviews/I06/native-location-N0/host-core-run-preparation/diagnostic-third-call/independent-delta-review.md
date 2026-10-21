# 第三次调用准备：独立六值增量审查

2026-10-22。结论：六位置文本/AST一致性、新pair只读指纹及来源、最终handoff边界均通过，无新增阻断。**PREPARATION_ONLY / NOT_RUN**；本报告不授第三次CLI，不证明新终点诊断已运行、具体根因或任何N0/EXCL/目标OS验收。

## 实际输入与审查范围

基准过程 `6fda0648299ae7e7d7d049ad5852e6d61b1618c5`。全文读取实际根准备窗口及第五构建受限收件文，与本目录快照逐字一致：

| 原件 | B | SHA256 |
| --- | ---: | --- |
| I06-N0-diagnostic-third-call-preparation-window.md | 2610 | 073bf0e4c0b867984ecc67c4b9b772fcac5f37503e9cf0ea1561d5288c5788ea |
| T03-fifth-endpoint-build-root-closure.md | 1691 | 34e741dcc5ef88fe9956edab81eb393d309f6eebfae6db477a0c865ec5d7bdb0 |

唯一模板从固定Git `1151b8d03cd381100bfc1b1804d3927110621f51` 的 `docs/reviews/I06/native-location-N0/host-core-run-preparation/diagnostic-second-call/exact-tool-call.preparation.json` 读取其arguments：19350B/SHA256 `42b1f04107e3e2404ed79cdaeed4fa0ac80fea093780dafbd4b16352c3615a60`。

实际读取新fullcall JSON/cmd文本、patch、delta-static-check、冻结handoff/preservation，以及授权的两个新实物。所有只读命令显式cwd为 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-native-location-N0`，只做Git/JSON/AST/字节/hash与两实物metadata读取，工具退出0。没有执行候选（含guard）、编译、native/core/probe/addon、产品check/API/FS探针或GUI；未重审旧17KB算法、旧长报告、002结果或供应史。

## 六位置与完整调用身份

新JSON.arguments.cmd与本目录exact-cmd.preparation.txt逐字相等。与固定模板全cmd比较，恰六行不同：1起第4、5、6、24、240、241行。将六行逐一还原后，全cmd原字节一致；其余注释/空白、shell前后缀及历史文字不变，未全局替换001/002。

独立解析here-doc为AST数据，仅在六个指定表达式恢复旧值后全AST相等（不eval/exec）：

- AUTHORIZATION改为 `I06-N0-execution-003-0d5223985fcd9761`；CORE_PIN/PROBE_PIN仅采用授权新path/bytes/SHA。
- RUN的右侧字符串 `/execution-002`→`/execution-003`，BASE/运算符不变。
- 原os.mkdir和run-directory os.open首参 `execution-002`→`execution-003`，其余参数/flags不变。

非cmd参数逐值相等：本I06绝对workdir、login=false、yield_time_ms=1000、max_output_tokens=1000。信号/等待/取消/错误/清理、限额及目录存在即停行为没有在本轮改变；此为精确差异证明，不是重新执行控制算法验证。

| 载体 | B | SHA256 |
| --- | ---: | --- |
| exact-tool-call.preparation.json | 19615 | 4c14304e4e4be6b041f60596aa581ed277af40e79d4499f9d2e8bf9e38d8cbe5 |
| 完整cmd / exact-cmd.preparation.txt | 17176 | ed84b73de7178ba8340843ed54b63d6cf45e6f683074833ad1f4a356df3aede3 |
| 实际here-doc stdin（含末尾LF） | 16976 | a67944783c48d1fb0e888d1ce6991665873881a482a91a6673c979425c8c07d1 |
| exact-six-values.patch | 2418 | 773f02aaf1bf418d4191d5c0df935b56c36a835f1a2fded84aef6cfff23358cf |
| delta-static-check.json | 3606 | 961b3a7b36a48852360f23ad7612c0b13fc44b312aea7c8c317666fc17ebf560 |

## 新pair：实际只读身份及来源

新来源绑定为I06产品 `fc9853f3521faced3a3b88ab8254310c9748a6a6` / 过程 `6fda0648299ae7e7d7d049ad5852e6d61b1618c5`，T03固定输入 `0514d37e32e31ae569e583bb56ec225ebc0483e6` / 过程 `8528ccb3d68de4f31ee1e10bd984084e0f7f418c`，digest `0d5223985fcd9761c60cee55d4c258af9b8204c8b0131df1535928cd1953c8fb`。根closure受限收件为built-unverified/NOT_RUN；本轮只读其全文，不重复205项构建闭包、依赖或旧轮审计，不把owner报告冒作我重跑构建。

两实物共同精确绝对目录为 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-native-location-N0-build/build/native-location/n0/darwin-arm64/0d5223985fcd9761c60cee55d4c258af9b8204c8b0131df1535928cd1953c8fb/core/artifacts/`。实际只读bytes/hash/dev/ino/mode均与新pin、窗口和delta记录一致：

| 文件 | B | SHA256 | dev / ino / mode |
| --- | ---: | --- | --- |
| location_core_test | 344096 | 65cca109ce2a43b24c94fc013b5e91127548d4be3d39de5330024128ffdb8039 | 16777232 / 66738069 / 0755 |
| location_child_probe | 34120 | 12d355d3cc43fc5c39b6e8689d7e0dabb6909b8dfd7a7deed6322f3351d80e48 | 16777232 / 66738076 / 0755 |

这是准备时只读身份，不是运行结果或持续不变保证；未来获准调用仍依精确窗口及原pre/post核对。旧result.sourceRef依授权保留b59239f9c1ec2774c7922f95dfc67db4dc8754e8，仅为历史模板字段，不能代表新fc9853源、T03新pair或003运行。未来归档必须另附新refs/digest/pins、cmd/固定准备ref与新一次授权，不改raw求表面一致或复用旧001/002结果充新证据。

## 最终交接及剩余边界

已全文读冻结handoff4397B/SHA256 `84f88c9edd9335c7fd24175b111f272c1e370e88f2c8e47d55888bf0c9193c4f`，与上述实际数据一致，明确无第三次CLI许可、未创建003、不复用或删改旧001/002、旧sourceRef不能表示新来源；终点/errno/具体002根因尚未知。新编译输入的准备不是自动重试同pair，也不能追认旧case/EXCL/平台通过。

preservation-check686B/SHA256 `8fa69c46cc303b30415828a5b3b73176c8ff752948200ea240cd3a60e35930eb` 明确单tracked diff/模板字节与protected work范围，原AGENTS 78df…a759、旧准备/失败/五轮构建原件保持。其全树保持及003未创建是主线已保存记录，本子任务未扩大为FS/进程探针或重复历史审计。

本轮唯一写入本报告，不改候选、产品、旧文档、Goal或提交。最终bytes/SHA交出后停止修改；根仍须读回固定新过程并另授精确一次CLI。没有第六构建、native执行或额外清理权限；独立准备审查不替指定模型、CI、目标OS与父门。
