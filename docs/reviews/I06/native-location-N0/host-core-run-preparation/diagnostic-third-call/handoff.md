# 第三次诊断调用：固定准备交接

状态：**PREPARATION_ONLY / NOT_RUN**。原I06树及feature分支从 `6fda0648299ae7e7d7d049ad5852e6d61b1618c5` 接续。本次只准备调用数据并只读核新pair指纹；没有执行cmd/Python payload、native/core/probe/addon、API/FS探针、构建或GUI。record不构成第三次CLI许可。

## 来源与固定调用

根准备窗口全文原字节与第五输入受限收件文已保存在本目录，bytes/SHA见 `delta-static-check.json`。唯一模板为固定 `1151b8d03cd381100bfc1b1804d3927110621f51` 的 diagnostic-second-call/exact-tool-call.preparation.json arguments，原JSON19350B/SHA256 `42b1f04107e3e2404ed79cdaeed4fa0ac80fea093780dafbd4b16352c3615a60`；其当前原件保持。

新完整调用为 `exact-tool-call.preparation.json`，19615B/SHA256 `4c14304e4e4be6b041f60596aa581ed277af40e79d4499f9d2e8bf9e38d8cbe5`；完整cmd原字节另存 `exact-cmd.preparation.txt`。

- record：`I06-N0-execution-003-0d5223985fcd9761`。
- cmd：17176B/SHA256 `ed84b73de7178ba8340843ed54b63d6cf45e6f683074833ad1f4a356df3aede3`。
- here-doc stdin（含最后LF）：16976B/SHA256 `a67944783c48d1fb0e888d1ce6991665873881a482a91a6673c979425c8c07d1`。
- 非cmd参数原样：workdir `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-native-location-N0`，login=false，yield_time_ms=1000，max_output_tokens=1000。

## 六值窄增量

只改AUTHORIZATION、CORE_PIN、PROBE_PIN三赋值，以及RUN后缀、exclusive mkdir首参、run-directory open首参三处目录字符串execution-002→execution-003。恰六行（1起4/5/6/24/240/241）、六个表达式值；三赋值注释及所有其它文字/空白/算法/tool参数相同。恢复六值后全Python AST相同，逐行反向还原后整个原cmd字节一致。没有全局替换历史001/002文字或改变BASE。

精确差异见 `exact-six-values.patch`，文本/AST/原始字符串身份的静态核对见 `delta-static-check.json`。原清环境独立-I/-S CLI、信号/取消/等待/未知语义、限额、流预算、cleanup及目录存在即停行为全部保持；本轮不重审已收件旧17KB算法/旧长审查或002失败原因。

## 新pair身份与来源边界

真实I06产品 `fc9853f3521faced3a3b88ab8254310c9748a6a6` / 过程 `6fda0648299ae7e7d7d049ad5852e6d61b1618c5`；T03输入 `0514d37e32e31ae569e583bb56ec225ebc0483e6` / 过程 `8528ccb3d68de4f31ee1e10bd984084e0f7f418c`；新digest `0d5223985fcd9761c60cee55d4c258af9b8204c8b0131df1535928cd1953c8fb`。

两实物位于T03树该digest的core/artifacts；只读bytes/hash/dev/ino/mode与根窗口及新pin相符：

| 实物                 |      B | SHA256                                                           |
| -------------------- | -----: | ---------------------------------------------------------------- |
| location_core_test   | 344096 | 65cca109ce2a43b24c94fc013b5e91127548d4be3d39de5330024128ffdb8039 |
| location_child_probe |  34120 | 12d355d3cc43fc5c39b6e8689d7e0dabb6909b8dfd7a7deed6322f3351d80e48 |

完整绝对路径及metadata见调用JSON和静态核对记录。以上只是准备期的只读身份核对，不替代未来获准调用的pre/post检查，也不证明新终点诊断已经运行。原result.sourceRef仍保留b592历史模板语义，**不是新源/新产物provenance**；未来归档须同时绑定真实fc9853/T03 refs/digest/pair/cmd/准备ref及另授窗口，不修改raw求表面一致。

## 保持与下一边界

源码、锁、既有准备/001/002失败及五轮构建tracked原件未变，AGENTS原WIP保持，见 `preservation-check.json`。本次未创建execution-003运行目录，不复用、移动或删除001/002，不扫描/清理未知fixture或杀旧PID。未来003若已存在，原调用存在即停。

独立agent仅审六值及新pair来源，最终报告 `independent-delta-review.md`。本目录有限manifest排除自身；固定过程提交号在提交后的回复给出。本轮无产品改动，不重跑npm check或旧源验证。

总控读回固定准备后仍须另授第三次精确CLI。当前只built-unverified，stage/errno及002具体根因仍未知；第三次是新编译诊断输入准备，不是自动重试同一pair，不追认001相同分支或后续case/EXCL/目标OS/父N0/功能门通过。无第六构建、native运行、GUI、凭据/外部模型/付费、push/PR/merge或Goal变更。
