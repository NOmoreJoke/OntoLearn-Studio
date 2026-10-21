# 第二次诊断调用：固定准备交接

状态：**PREPARATION_ONLY / NOT_RUN**。本轮只保存调用数据、静态差异及新 pair 的只读指纹，没有运行 cmd/Python payload、native/core/probe/addon、API 探针、构建或 GUI；record 标识不构成执行许可。

采用总控首次窗口及随后“固定目录增量更正”。首轮工具全文读取的原版内容见 `first-read-window.transcript.md`（由该读取文本留存，未捕获当时文件 hash）；第一次实际落盘快照 `I06-N0-diagnostic-second-call-preparation-window.md` 已包含更正，最新原字节另存 `preparation-window.corrected.md`，来源区分见 `window-provenance.json`；新构建受限收件见 `T03-fourth-diagnostic-build-root-closure.md`。首版三值静态准备记录为 `initial-three-value-static-check.json`；其目录冲突来自首版准备规格不完备，未曾执行，不是运行失败或重试。

唯一调用模板为 `b942e12cd122873109f4bd16d51e06e05ad7005d` 中 concrete-call/exact-tool-call.preparation.json 的 arguments。最新固定副本为本目录 `exact-tool-call.preparation.json`，完整 cmd 原字节另存 `exact-cmd.preparation.txt`。仅改变 AUTHORIZATION、CORE_PIN、PROBE_PIN 三项赋值，以及 RUN 后缀、exclusive mkdir 首参、run-directory open 首参三处目录字符串。总计六行/六表达式值，精确 patch 和 AST 除六值一致记录见 `exact-six-values.patch` 与 `delta-static-check.json`。没有泛化全局替换。

- 新 record：`I06-N0-execution-002-a0e724fdf90afa98`。
- cmd：17176 B，SHA-256 `be0d1fc7518e281353206ec25e43f579dba9821035b46ee3161e76aac7fc2705`。
- here-doc stdin（含最后 LF）：16976 B，SHA-256 `9f6f4b99b63aab6be937617aab7c9dad605a5ab5a54a1b54cfc6c33621d4c2a2`。
- 其它工具参数逐值不变：workdir `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-native-location-N0`，login=false，yield_time_ms=1000，max_output_tokens=1000。
- BASE、独立 `-I -S` CLI、外层 env、所有限额/信号/等待/清理及存在即停行为保持。新调用仅以 execution-002 为新目录；本次未创建该运行目录，旧001五件原始结果及全部旧 tracked 原件保持。

新 pair 供方输入 `d98b503ebe9c477d30d0f36d831cffbeeaf2a988`，过程 `d51a0555e6feb062fc935173222cc142687901a5`，digest `a0e724fdf90afa980f01719fc8cc4d55f158400cf5abe26665c72a2d288cac77`。两实物均在 T03 树该 digest 的 core/artifacts 内；实际只读 bytes/hash 与受限收件相符：

| 实物                 |      B | SHA-256                                                          |
| -------------------- | -----: | ---------------------------------------------------------------- |
| location_core_test   | 343920 | d4f5ca322146d9696860a74de4bee2ad27866a2223340669898fb82cbbfeb817 |
| location_child_probe |  34120 | 21928ca2b5570055fad4bebcd81fcb658016ca9a738294397a83056b662b87e8 |

精确绝对路径、dev/ino/mode、来源窗口与指纹记录均见 `delta-static-check.json`，全工具参数见调用 JSON。旧模板 result.sourceRef 仍为 b592，按本窗口六位置边界原样保留；该历史字段不能代表新输入源。新来源应以以上 T03 refs、digest、pair pins 及新授权窗口辨认，不能把旧字段/旧001运行结果改记为新来源或新运行证据。

独立 agent 只核这次六位置增量和 pair 来源，不重审旧控制算法/API报告；最终报告为 `independent-delta-review.md`。本目录有限 `manifest.json` 排除自身；过程提交号由提交后的最终回复给出。

仍须总控读回固定过程并另授一次002 CLI，才能执行这一精确调用。当前只 built-unverified，未观察新 case/status/owner_nonzero 输出；此前 owner-create 失败根因、native drain、EXCL/目标OS及全部父门仍未关闭。
