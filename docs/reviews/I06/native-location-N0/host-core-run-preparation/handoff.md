# N0 Darwin fixture 修复与 host core 执行准备交接

2026-10-22。源码候选已完成静态修复和独立审查；执行准备仍为 PREPARATION_ONLY_BLOCKED。没有预处理、编译、链接、运行二进制/测试、加载 addon、FS/child 实验或 GUI 操作。

## 采用输入

固定源码 ref：`b59239f9c1ec2774c7922f95dfc67db4dc8754e8`。准备合同修订固定 ref：`fbebc7c716a55e7f3f017b69a1d0b8074f1aab87`。后续交接归档提交仅增加本过程文档，不改变九件源码；新构建必须采用上述源码字节，不能继续使用旧 b657 产物。

唯一源码改动相对 b1c54c3de840e657aba07906587681f6415085d6 为 Darwin include sys/stdio.h，以及 root rename 改成 renamex_np(...,RENAME_EXCL)，见 darwin-exclusive-rename.patch。location_core_test.cc 为 29706B，SHA-256 `f1684029430f28918fd4caa062eb8d250f97d5d34aa3ab65c517e44954525037`。其余八源、Windows fixture 区块及28条断言逐字不变。AGENTS 保持原受保护工作区内容且不纳入提交。

实际供应 SDK27 的五件头/手册及原供应 metadata 已核原始字节/hash；RENAME_EXCL=0x4、renamex_np 声明及10.12+门、full-C namespace与 EEXIST 语义已留 sdk-rename-declaration-evidence.json。新编译、符号解析、实际文件系统支持未证明；不靠旧 depfile 替新产物签收。失败 path 不提前更新、无普通 rename fallback，但仍是绝对源名字操作，不能外推持续 namespace 围栏或生产 publish 能力。

## 独立审查与处置

source-fix-independent-review.md 固定 b592，8702B，SHA-256 `12e953f27264b24e77e1bb025e8333ea1380b953a516aadbbb6778ce257935e1`：目的覆盖反例源码层闭合，未发现本次两行 diff 新确定阻断。

run-preparation-independent-review.md 保留 b592 首审原文，11167B，SHA-256 `f0b04ff57dba81f0e5a6141e6be0903b3f8c137eca7f928ee4ba9202f2d9cafb`。P2-RUN-01 指出继承信号缺口；fbebc7c 的 plan/JSON 已要求本次 core 子进程 exec 前 SIGCHLD=SIG_DFL、无 SA_NOCLDWAIT、SIGTERM 默认及空 mask，probe 继承且无外部 reaper。现有 executor 未证明可落实则不执行；没有开发新 runner 或改 host 配置。处置与独立点读跟进分别保留，不改写首审结论。

run-preparation-followup.md 固定 fbebc7c，4676B，SHA-256 `18278769a9fd629a16425bff7bc26f0d67f093a974c301271de4005e7bd371f3`：P2-RUN-01 在文案层关闭，未发现新增准备合同阻断；仍不构成执行批准。首审原件此前尚未收录 fbeb Git 树，跟进首次 git show 128 已如实保留，随后按原件核符；本最终归档同时收录首审和跟进。

## 交根后仍需的实件

1. 根路由 T03 采用 b592 的九源、授权必要重构建；再供应新 inputDigest、两个精确绝对实物的 bytes/SHA、实际 used/terms 及新增 renamex_np 解析证据。旧 provider-readback/superseded-artifact-pins 只保历史，不进入运行 argv。
2. 现有 executor 给出可审的实际执行控制：明确0/1/2、两份独占原始流、child-only 信号状态与进程限制、唯一 wait、未 reap 的 owned group 有界 TERM/KILL，以及 finite 记录；不临时扩开发 runner。当前 resolvedCoreArgv=null，不能猜目录或替换为旧路径。
3. 根确定安静环境适用边界并给精确一次执行窗口。若连 OS 自动 crash 提示也须零影响，应提供相应隔离 CLI 环境；CORE0 不证明这个条件。现有消息仅授权准备及最小源码修复，不授权运行。

一次 core、至多两次内部 probe spawn、无重跑；资源/时间/原始 stdout 与 stderr 上限及失败清理均见 plan.md/execution-plan.json。/tmp fixture 不由 TMPDIR 隔离，也无外部创建 receipt；未知残留不凭 prefix/mtime/PID 删除。kill、退出或目录缺席不签 native drain。宿主 macOS27.0.1 arm64 的未来运行最多属宿主受控 case，不能替 macOS15/Win11 或完整 N0 验收。

## 本轮实际验证与证据

九源 hash/精确 diff、先前52路径保护、SDK原件与供应记录比对、原旧二进制只读 hash、JSON/文档静态检查及独立审查已完成。第一次路径读错及窄查找失败保留 preparation-read-failures.json；首轮格式检查 exit1 与修正后 exit0 保留 plan-format.json，修订后检查见 plan-format-r2.json。最终 scope 检查见 final-scope-check.json，本目录清单另附 manifest.json。未把这些检查称作编译或运行通过。

旧历史交付/审查及主线状态不改写；未 push、未创建 PR、未改变 Goal 或总控状态，不签完整 I06/N0 完成。
