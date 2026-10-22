# F1 精确修复独立复核

结论：**SETUP_DELTA_PASS_ONLY，F1/P2 CLOSED**。候选 `49cd9092f98485baeb961b2e857aef47fba71c26` 已关闭首次独审的 C1 证据输出隔离缺口；本次精确 delta 未发现新问题。首轮 `SETUP_NEEDS_CHANGE` 原件保留，不将它改写为通过。本结论只用于 setup/提示包，不是产品验证或 ZCode/MiniMax 指定 Pass。

审查者仍为独立 Codex agent `/root/t03_physical_setup_independent_review`。唯一新增本报告及 `independent-delta-checks.json`；未改作者候选、首报告、配置、产品、测试或锁，未安装、未运行任何产品/check/e2e/build/fixture/package/probe、未调用作者 bootstrap/repair/validator/make-prompts、未提交。未读取 Caller/fee WIP、受限身份载荷、指定模型本轮意见/状态或 app runtime。

## 固定身份与完整 delta

仓库 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-mapping` 实际 HEAD 为上述 49cd，工作区原有 AGENTS.md 仍仅未暂存修改。对比首报告流程 ref `2b49d1dd883574f4f895d1b650c62ff1dd72059c`，Git delta 精确等于 14 payload 与新增 F1-delta-manifest，未夹带其他路径。

F1 manifest 3555B，SHA256 `c8e730b080844aa3020c479c1e4c73b3a0316e5927823e7867746b0c66988e9a`。14 payload 合计 315582B，均从固定 Git 原件逐件核 bytes/SHA，并核当前工作文件相同。完整读取 README 增补、bootstrap 一行修复、make-prompts/validator delta、新 repair-environment.py 全文、F1-environment-repair 六条完整回执、validation 与 manifest。全部受影响 JSON 独立解析，Python 文档工具独立 AST 解析，无作者脚本执行。

六份新提示逐份全文字节核对：相对上轮完整正文仅新增 c1Evidence 映射、覆盖继承值和保首失败说明，没有其他正文变更。对应 prompt-index 除全文身份、suffix offset、新映射外所有原字段不变；六份冻结 dispatch-v2 suffix 均保持原字节。正常 C1/I04 权限、原 HMR/未签 N0/producer/caller/受限载荷禁令及完整报告、实际设置、资源和发布门均未改变。

首轮报告仍为 9622B/SHA `0034969ebf895fa84da27d014600de74e5f630b6e2bd873a8b04c153cf4643d8`，checks 仍为 20596B/SHA `29d5adaf607a92d2b03354f31a3c5b37a6f41c832e5e1a04456947a69c542ffb`，均逐字等于首报告流程 ref。e95 的旧 candidate-manifest 原字节未改，仍是首次输入声明；新修复身份另由 F1 manifest 承载。

## F1 关闭证据

`bootstrap.env_for().values` 新增 `I02_EVIDENCE=<自己的物理树>/build/review-session/raw/c1-evidence.json`。因为生成 shell 中该 export 覆盖继承值，旧值不会再流入原 C1 `finally` 的 mkdir/writeFile。六份实际 environment.sh 与修复回执 after identity 一致；逐份去掉这一个新增 export 行后，bytes/SHA 精确还原首轮独审所读环境身份，未暗改其他路径、flags、cache 或依赖。

独立复核另行给每个纯 shell 人为注入 `I02_EVIDENCE=/independent-not-written/stale-c1-evidence.json`，只执行 `/bin/sh -c '. "$1"; printf "%s" "$I02_EVIDENCE"' sh <本树environment.sh>`。六次 exit 均为 0，stderr 均空，stdout 均为各自唯一 c1Evidence 路径。没有写入人为 foreign 路径，没有启动 Electron，也没有生成 c1-evidence.json。完整 argv、注入值、stdout/stderr/exit 与各环境身份已写入独立 checks JSON。

作者 F1-environment-repair 的六条 argv/注入值/完整 stdout/stderr/exit 也逐项核回本树 `metadata/environment-isolation-repair.json`，没有用摘要替代。每树 metadata 从 4 个普通文件增至 5 个，总 bytes 精确等于记录的 before bytes 加本次新 receipt 的真实大小；“after-before-this-receipt” 快照不计自身的解释准确。六份环境与六份新 metadata 文件普通文件 nlink 均为 1，12 个 inode 互不相同；原依赖未重装，原安装日志身份未变。本次变化只涉及这些已知文件，未因不变依赖重复全量 inode 扫描。

六树实际 reviewHead、detached 状态与仅保护 AGENTS.md 未暂存状态均不变，AGENTS 仍为 15147B/SHA `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`。这里记录的是逻辑文件/字节增长，OS/app 实际 metadata 操作量仍为 UNKNOWN，没有向停止 Caller 补账。

## 保留的前置与限制

新提示明确每次真实重跑前由 owner 分配本树新 raw 轮次路径以保留首失败；固定默认路径是本次首次 C1 输出位置，不代表可以覆盖已有证据。后续操作应在 source 环境后使用 owner 分配的本树新轮次值，仍不得改冻结测试。

默认 Electron userData、GUI/焦点和固定端口仍须总控在实际运行前协调；本修复未宣称已经隔离应用数据或取得运行 lease。普通未改 C1/I04 不被 N0 禁票泛禁，N0/producer/caller 专票亦未被这项正常测试输出修复扩大。实际指定 task/settings/lease 仍未发生或由后续真实收据决定。

本次没有产品功能、原生恢复、包、跨平台或生产运行证据，没有性能测量。README/文档工具有限检查与纯 shell 回读只支持 F1 输出路径修复。原首失败、全部验收及指定双审/CI/真人/远端/发布门继续保留。可以据此将 setup 修复包交总控预检和后续资源调度，不可据本报告宣布产品或指定审查通过。
