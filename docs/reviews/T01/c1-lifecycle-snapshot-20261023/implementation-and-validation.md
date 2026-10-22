# C1 Stage A：生命周期诊断值快照

基线 `650433962f37055f1c15b29130e28b9ad776f0e8`，源码提交
`d0b1756e85eb17c524b44c4f5557e62d738d5c62`。本次只修 `transition.lifecycle`
被后来事件污染的问题，不改变进程分类、归属、清理、超时或恢复验收。

`updateEntry` 只读一次生命周期，使用 `structuredClone` 生成深值快照；分类与记录共用该对象，
并共用一次 `Date.now` 的 `classifiedAtMs` / `consumedAtMs`。事件原始时间、接收时间与
采样起止均保留。消费时间不代表逐行采集时间。

原 classifier 块 SHA-256 仍为
`68238542607e8992a4b58f38fa1b2c82a58bb3bbbbd874fff1de435dfb104c89`，与650逐字一致。
observer、产品、原e2e、依赖锁、CI均未改。937个原跟踪文件的字节核对只有driver发生变化；
新加的是有限检查脚本与本方记录。AGENTS 为最新 de15 保护覆盖，不提交。

## 实际验证

- `node scripts/check-c1-lifecycle-snapshot.mjs`：实际提取源码函数，10项通过。
  同一脚本读取冻结650源码时6项通过、4项失败，准确暴露历史记录污染、嵌套别名、两次读取和后继快照污染。
- 独立审查全文核两路径与完整差异，未发现新增P1/P2；独立运行新10项通过、旧4项失败，另3组边界检查通过。
  这些是纯Node受控检查，没有启动native CLI。
- `npm run check`：实际exit0，UTC 2026-10-22 18:17:08.736868–18:22:03.012811。
  lint、格式、类型、构建、Ruff均通过；1125项TS通过，2969项Python通过、44项跳过。
  Python耗时267.31秒是本轮记录，不作性能结论。
- `git diff --check` 通过。仅新增过程Markdown另做定向格式检查，不因文档归档重跑整check。

整check stdout 8689B，SHA-256
`6ad30cccc4fb1896eb9d67bb2631321bcaad03e6d02b75f0cbd0c5136143f5b4`；stderr为空。

## 输出路径勘误与原件

首个wrapper的大小写替换错误只改了tree名，未改大写C1的输出根。因此首轮安装、有限检查和整check
实际写在本方上一轮 `T01-C1-native-runtime-20261023/raw/` 的新slug中。
实际cwd、`node_modules`、`.venv`、workspace链接及Python editable来源均为本次隔离树。
原wrapper SHA-256 `2ab0bd7378b40b48ce0d52ee54694e7a531701616862699f4d976b2bae65c81f` 未改。

独立复核没有发现因此借用旧可变安装或改变验证对象的具体证据，不机械重跑整check。
原收据保留真实位置；本次输出根的 `prior-runner-actual-output/` 仅是字节一致副本，不算新执行。
修正后的 `run_capture-02.py` 留给后续新运行，SHA-256
`f828a95bfc933742896e377b723bd7b347aa464791765b25e0451f77361fd439`。

完整双流、收据、937文件基线、路径勘误、独立原始检查与保护核验均在仓库外：
`outputs/20261022_review_backlog/T01-C1-lifecycle-snapshot-20261023/`（相对本体根目录）。

本次没有GUI、native新run、OS/ABI探针、push或merge。650与native02/03原失败不回写。
Stage A只关闭诊断别名问题，不作为native整体通过或指定模型双审。
