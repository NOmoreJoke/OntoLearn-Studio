# T07 R3 两侧隔离依赖实际安装（setup-only）

两侧均已按总控单次 setup-only 票完成五条精确命令，十个真实子进程整数退出码全部为 0；唯一一次独立的实际安装后静态审查已通过，无 P1/P2 阻断或必需 setup 证据缺项。固定产品仍为 `f9a1157c2fff06c8bef17fa1ec44d8eb1ebacad3`，两新根仍 detached `7fd17f93ebb4b68bac69faec15cb657e60c90729`，准备提交为 `3b4591258d62607224b39cca31db7304cd15b5c7`。未重建、切换或清理根目录。

授权票原件 10996 B，SHA256 `2b6dada1ddd4f4270b94c7924a85095a5df14b50349744e91bb8a5673ef5566d`。此前按短称 `weekly.private/...` 直接读取返回不存在；仅按精确票名定位至总控已给定工程内的 `iteration-control/2026-10-21-weekly-release/.private/` 后全文读取并核对字节。该路径定位没有启动或重试任何安装命令。

| 角色 | UTC 开始—结束 | node / npm / uv | npm / uv 子 PID |
| --- | --- | --- | --- |
| ZCode | 2026-10-22 23:26:01—23:26:39 | 24.15.0 / 11.12.1 / 0.11.12 | 98398 / 98985 |
| MiniMax | 2026-10-22 23:26:40—23:27:11 | 24.15.0 / 11.12.1 / 0.11.12 | 99563 / 191 |

每侧按票原 argv 各一次：node `--version`、npm `--version`、uv `--version`，然后 `npm ci --ignore-scripts --no-audit --fund=false`、`uv sync --frozen --no-python-downloads`。没有 shell、argv 换路、重试或 fallback。各自完整替换环境包含独立 HOME/TMP/XDG/npm/uv cache、两个 0600 空 npm 配置；不叠加宿主环境或凭据。使用票指定的现有 CPython 3.12.12，只读基解释器 SHA 在安装前核对，禁止 Python 下载。缓存初始为空；使用票明确允许的锁定依赖 registry 获取，未借旧可变缓存，也未声称离线。

`execution-summary.json` 保存所有实际 argv/env/cwd/PID/UTC/真实退出与两流身份，原始两流及命令/链前后向量位于每侧 runtime/setup。每条命令前后核对本角色 root 的 1020 源文件、scratch 的同 1020 源文件、236 项必读及输入 sidecars/原 metadata；每侧全链向量一致，四份锁/当前指南及完整输入未改。原 16 处历史空白保持，原读账仍未预签 EOF。操作限时和捕获边界没有触发，不宣称整棵进程树隔离或硬配额。

npm 两侧原 stdout 均为 added 440 packages；静态元数据逐项与原锁核对的安装包 package.json 为 438，另两项为本侧 workspace 链接。uv 两侧均安装 14 个分发，版本逐项匹配原 uv.lock；其原 stderr 中的 Building/Built ontolearn-engine 是本次获准 uv sync 内的本地 editable 依赖构建，保留完整原文，不计作产品 build 或运行验证。npm 的 rimraf/inflight/glob 弃用警告原文保留，未为处理警告修改锁。递归收集的 Python 元数据文件为每侧 105 份，包含 12 个 vendored METADATA；后继静态比对首次把其中 tomli 当作顶层分发而 KeyError、exit1，完整首错与转录来源保存在 static-metadata-first-error.json。改按顶层 site-packages 范围核对后，14 个实际安装分发均匹配原锁；安装命令未重跑。

`static-installed-isolation.json` 与每侧 installed-metadata.json 仅由标准库读文件/JSON/hash/stat 生成；未运行安装后的工具或导入产品。两套依赖普通文件 inode 交集为 0；声明的可变目录身份互异，无跨侧可变依赖链接。Python 执行文件可指向票指定的共享只读基解释器，本侧 editable/pth 指回本侧源。scratch 仍无依赖；未下载 Electron/browser 二进制。每侧 role-installed-facts.json 只含本侧安装事实，聚合票/独审/总清单保留在 owner，不向未来模型暴露 peer 的本轮记录。

旧准备包及 PLAN_ONLY_NOT_EXECUTED 是早先阶段的原件，不回写成当时已安装；本目录与后继 role-only 回执记录本次实际安装。原 pytest/vitest/npm check 同目的拒绝 hold 未解除，没有产品 test/build/DB/probe/stdio/native/GUI、新任务或外部发送；原 PROCESS_FAIL / Pair 0、M P2/P3 未决、Definition 身份守卫及父级未验项保持。模型后续可全文核现成原 check/raw，证据不足仍须标未证。

封存安装命令双流和前后向量的理由是提供独立可核对的真实执行证据；不封存 node_modules、venv、registry 缓存或业务数据库。最终单一 manifest 将固定票、命令记录、完整原始包、静态核对及独审报告的 bytes/SHA。

独立审查原文 actual-setup-independent-audit.md：11884 B，SHA256 `c543a4ba43d9ba621dbc52c8ca90411c7db1a8cd1e087faaed4a26e96c71d426`，owner 已全文读回。审查只证明本次 setup 执行证据和静态安装隔离；未做独立现场进程监控、全链网络审计或产品运行验证。最终 setup-manifest.json 是本次单一固定清单；同名 .raw.tar.gz 保存两角色 setup 原始证据及各自不含 peer 正文的后继审查回执。
