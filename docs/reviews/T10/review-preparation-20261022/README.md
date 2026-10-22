# T10-S1 双隔离树审查准备

本次只准备环境、完整提示和原始记录；未创建模型任务、未操作GUI、未启动Electron、未重跑不变产品验证。原packet、147项manifest、产品与技术工具均不修改。实际创建仍待root短lease，不占用其他任务的后台推理。

## 固定输入与实际执行树

批准base `5f910b52c69d86a1076b2032e5d3c63e715947f3`；产品C `c3c7e90f721344113c4279d663127f9c8d5bda59`；固定证据A `a1e7efef4bd47c97b630753c0e7c4dc34de1d8ae`；两个执行树均为detached `77f2d5048630827ba5220fe092392ded6ab1c697`。77包含流程文档，不改变C的源码/tests/fixture/锁/CI；实际独立核验147项A的Git长度/hash均一致。报告需同时记录产品、证据输入与执行树身份。

| 角色 | 独立执行树 | 唯一最终报告 |
| --- | --- | --- |
| GLM-5.3/最高（预期max）、yolo | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T10-zcode-review-c3c7e90` | 该树 `docs/reviews/T10/round-1/zcode-glm53.md` |
| M3.1-Flash/xhigh、bypassPermissions | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T10-minimax-review-c3c7e90` | 该树 `docs/reviews/T10/round-1/minimax-m31flash.md` |

每棵树的绝对路径/实际HEAD/独立raw/scratch/input见各自 `paths.json`。最终报告不存在，未写占位Pass；actualTask、实际设置与实际lease均为null。新树当前保护AGENTS为de15，两个node_modules和.venv身份/实际路径均不同，不共用可变环境。

## 环境和验证权限

各自 `npm ci --ignore-scripts`、`uv sync --frozen --python 3.12`、`install-electron`真实退出码0；原始输出见各自environment-raw，精确命令/版本/位置见environment.json。Node24.15.0、npm11.12.1、uv0.11.12、Python3.12.12，Electron依赖44.9.0仅安装未启动。此为依赖环境就绪，不是新的full-check或native通过。

每模型 `original-prompt.md` 是完整原prompt：顶层实际路径/验证addendum＋原packet全文＋全量backlog＋当前desktop/common/permissions全文。对应输入副本已逐字比对复制到各隔离树自身round-1输入目录。根目录旧packet及原manifest副本保留原字节，未反写原文件；新addendum明确替代旧主开发路径、旧“只有MD可写”与旧桌面前置。

审者可在**自己的隔离树/env/scratch**执行原验收需要的完整check、复现和独立反例，写自己的日志、缓存、派生构建/测试流及临时验证配置/夹具；原src/tests/fixture/依赖声明/锁/config/验收/旧raw/Git只读。不要把派生目录一概禁写而使实际验证变空，也不能把允许scratch误当允许修改测试或候选。额外GUI互斥由root内部短lease协调，不以用户时段/CLI登录作为前置；未签运行票、被拒工作及其他明确边界不扩大。

全部S1及7技术工具/相关原件双方都完整审，不分拆、不互泄本轮意见，每轮各新完整独立任务。当前准备源文件索引及hash见preparation-manifest.json；独立输入预检只验证准备边界，不代替指定模型报告。正式投影/迁移/生产FS lease、全部父门与双审/CI/两OS/真人/远端仍未关闭。

独立准备预检由`/root/t10_private_review`完成：147项固定输入、两树身份/依赖隔离、18作者路径、完整提示/政策、副本与未创建状态均通过。唯一非阻断历史措辞已在新addendum澄清为“容器已创建、启动前检查失败”，旧原件不改。详情见independent-preflight.md。
