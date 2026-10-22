# T03 六棵物理审查树 setup 交付

本包只准备三组 × 两模型的独立审查环境和完整提示。18 条依赖 setup 命令均 exit0；未运行产品、check、sources、e2e、package、包内 probe 或 GUI。尚无指定模型实际任务、实际设置、运行 lease 或指定 Pass。Caller 停止现场未读取、未写入。

## 固定来源与写面

六树按总控 `iteration-control/2026-10-21-weekly-release/T03-T04-review-roots-20261022.json` 的前三组登记，路径、reviewHead、product 及独立输出完整列于 `prompt-index.json`。六树都保持 detached HEAD 和仅 AGENTS.md 未暂存修改；保护规则 15147B、SHA256 `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`。T04 两树未触碰。

原 mapping 树仅新增本 prefix，不改完整旧包、原报告、manifest、8 旧提示或 dispatch-v2。每份新提示前置物理路径、执行范围及三份当前共同规则全文，末尾完整附上对应 dispatch-v2 原字节；`prompt-index.json` 记录原 bytes/SHA、精确 suffix offset 和新全文 bytes/SHA。旧原树与分支仅作历史来源，实际执行只在新物理树。

## 已做 setup

每树实际执行：

1. `npm ci --ignore-scripts --no-audit --no-fund`。
2. `uv sync --frozen --python /Users/kyle/.local/bin/python3.12 --no-managed-python --link-mode copy`。
3. `node node_modules/electron/install.js`。

使用 Node v24.15.0、npm 11.12.1、uv 0.11.12、Python 3.12.12。uv 只运行正常 Hatchling editable 安装 hook，没有产品 import/测试；新环境按本机平台实际安装 Python distribution 数为 mapping17、selection14、profile19，不能拿这些数替换跨平台 lock 全量条目。npm 有意跳过 electron-winstaller 与 fsevents lifecycle，不承诺所有平台工具或 watcher 已验证。Electron install.js 已全文静态读取，只下载和解压依赖，未启动 Electron；本机 arm64 分支未走 Rosetta 的 sysctl 检测分支。

每树实体 `.venv`、`node_modules`、npm/uv/Electron/builder/XDG cache、TMP、scratch、raw、reports、metadata 均独立，位置在每份提示中完整给出。正常 editable 指向本树 engine 源码。基础 Node/npm/uv/Python 安装只读共用；每树三个 `.venv/bin/python*` 链接最终都指同一系统基础 Python，此项明确披露，不声称基础解释器也复制六份。

全量 lstat 六树 setup 生成目录：跨树普通文件 inode 碰撞 0，普通文件 nlink>1 为 0；外指链接共 18，全部是上述基础 Python 链接，其余链接解析后留在各自树内。具体目录、文件、字节、符号链接和 inode 增长见 `isolation-verification.json` 与各 `*-before.json`、`*-after.json`。

这些是目录项的逻辑 inventory，**不是实际 OS metadata 操作次数或 app runtime 计量**，后两者为 UNKNOWN；snapshot 在写其本次 receipt 之前取得，因此不可宣称是最终无自增总量，也不将它并入已停止 Caller 的账。原始安装日志原位保留，并在每份 after 收据以完整文本、bytes/SHA封存。

## 静态验证、首失败与运行边界

`static-command-audit.md` 是独立 agent 的完整原报告，主聊天已全文读回。它完整展开正常调用，区分基线 C1/I04 与 T03-N0 未签票研究。新提示允许后续真实审查在实际阶段内必要运行原未改 check/sources/e2e/package；普通 C1 Mac 也含真实 native recovery，不被静态一律禁用。GUI、焦点、固定端口及默认 Electron userData 由总控内部协调，不能只靠 TMP 假定隔离。本轮不占 GUI；创建/读回短 lease 和实际运行 lease 后续另记。

`I02_HMR=1` 仍会改源而禁止；未签 native/producer/caller、被拒资源研究与受限 SDK/identity payload 均未扩权。各组原包内样例须用本次本树包与冻结合同原 argv，先精确核对原阶段边界；不由此补充授权任意 probe。所有父业务、两 OS、真人、签名、生产及原发布门原样保留。

setup inventory 首跑 exit1：审计脚本误用 `'/python' in basename` 判断基础解释器名称，导致误拒合法外链。失败及完整 18 链接见 `inventory-first-failure.json`，原完整 terminal traceback 保留于 Codex tool chunk `9c68f2`；六份 `*-after-first-inventory.json` 保留首次观察。修正为 `basename.startswith('python')` 后重跑通过；未变产品或依赖，不冒充产品失败/通过。早先静态读文件误猜路径的读取错误也在独立报告保留。

文档身份检查首跑 exit1：检查器猜错 Hatchling editable `.pth` 文件名，实际为 `_editable_impl_ontolearn_engine.pth`，内容正确指本树源码。只改检查器路径后复核，原完整终端与处置保留于 `validation-first-failure.txt`；没有修改安装文件。

新提示以 exact-byte 冻结继承为验收，不交给 formatter 重写旧原文。纯新增 README 单独做 Prettier check；JSON 用 stdlib 结构/身份检查，Python 文档工具只做语法检查，不运行其产品入口。后续 fresh 独审只评本 setup 包与执行边界，不替代指定双审。

## 下一步

封存新候选、完整 fresh 独审及意见处置后交总控预检；由总控安排短 lease，再在正确物理树创建 ZCode GLM-5.3/最高/yolo 与 MiniMax M3.1-Flash/xhigh/bypassPermissions，真实读回实际设置。任何模型本轮意见、状态、runtime 或报告都不得向同伴发现或读取。当前任务与设置留空。
