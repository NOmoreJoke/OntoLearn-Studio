# T03 P2 固定 17 case 新候选

结论：新候选的 source 与实际新冻结包均执行单一 `--mapping-probe`，17 case 完整匹配执行前独立写定的 oracle；两个外部引用 case 的 socket API 计数为零，CSV 四类超限均匹配精确错误定位。三个额外参数均 exit 2 / 空 stdout / 固定 stderr。这里的 17 个 case 共用一次进程退出码，不是 17 个独立子进程。

候选基线 `30319412daf8ae4745987babf7bbed93c53b6b42`，分支 `fix/T03-mapping-p2-boundaries`。产品差异仅 `mapping/probe.py` 和 `tests/test_mapping_entrypoint.py`：保留旧 11 项，追加固定六项；CLI entrypoint、caps、依赖、锁和构建配置不变。当前 AGENTS 15147 B / SHA-256 `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4` 是独立 overlay，保持 unstaged。

## 实测证据

- fresh `npm run check` exit 0：ESLint、Prettier、类型检查、638 TS 测试、构建、Ruff 和 1116 Python 测试通过。
- `npm run verify:sources` exit 0：核对 12 个归档源文件。
- fresh `npm run package:dir` exit 0：构建本树独立的新 mac-arm64 目录包。engine 4622464 B，SHA-256 `c4c8d80cb78323a0c7dc28978893197d477809764a0ac2a2c336734cfd1be031`。
- 固定 verifier exit 0：真实 source 与真实新包均 exit 0 / 空 stderr / 严格完整 oracle；包拒绝 path、script、URL 三种额外参数（分别 exit 2）。source `-O` 另一次实际执行 exit 0，严格匹配同一 oracle。
- 实际 PYZ 的 probe/source/plan code object 与本树源编译对象一致；仅递归归一化 `co_filename`，没有通过系统 Python 执行包内 code。包内 lock 与源码 lock 哈希一致，4 个许可证字节一致；440 项 engine inventory 已归档。
- `actual-receipt.json` 是实际 raw receipt 的逐字节副本：28825 B，SHA-256 `5ad2ea0f5dd16463cba097b60127188ba7d41eff5b5e2b4ca138d8c2d37a076f`。其 17 条 `allCaseRecords` 记录内部结果、断言、同 run 外层 exit；新增六项另记录实际细节与预期。旧 11 项维持原有结果输出，不虚构它们未输出的位置。
- `fixed-probe-v2-expected.json` 在新实现与执行前独立写定：3123 B，SHA-256 `e7a8c0d3e0e9152d56da781a1705837e7987ac44cc4e450a8707293e2641eebc`。`oracle-before-run.json` 记录冻结事实；没有从新 stdout 生成 oracle，也没有覆盖旧 `project-probe*.json`。

| 新 case | 实际结果 | 精确定位 sheet / row / column |
| --- | --- | --- |
| external-cached-formula | `001`、`只读已保存值` | 设备 / 2 / 2 |
| external-hyperlink | `001`、`显示文本` | 设备 / 2 / 2 |
| csv-file-limit-located | SOURCE_LIMIT | 空 / 0 / 0 |
| csv-column-limit-located | SOURCE_LIMIT | CSV / 1 / 0 |
| csv-cell-limit-located | INVALID_CELL | CSV / 2 / 1 |
| csv-row-limit-located | SOURCE_LIMIT | CSV / 50002 / 0 |

三个被测 API 为 `socket.socket`、`socket.create_connection`、`socket.getaddrinfo`。guard 覆盖全部固定输入构造和解析；每次尝试先计数再抛出异常，不会访问网络。计数是同一 invocation 累积值，每个新 case 记录当时累计值，全部为 0；不能理解为 17 个隔离 counter。guard 退出时恢复三个原始对象，成功、异常、三个 API 故障、吞异常后仍检出非零的负例均已测试。依赖 import 先于 guard，证据域不包括依赖 import、所有 OS 网络原语或 GUI。

## 首次失败与修正

完整原始双流、UTC、argv、cwd、exit、起始源 identity 均保留于本树独占 `build/mapping-p2-boundaries-20261023/commands/`。`command-records.json` 收录 14 个受控 command receipt，`raw-evidence-manifest.json` 收录 74 个原件（不含 cache/tmp）。无覆盖首次失败、安装共享环境或泛化 kill。

1. 首次 Ruff 检查发现新增测试三个长行；首次 format 检查发现两文件需格式化。仅格式化授权的两文件，复验通过。
2. 首次 targeted 为 1 failed / 11 passed：新增成功恢复测试直接比较 Python `run()` 的旧 tuple facts 与 JSON array。仅把该测试比较收敛到它要验证的 `boundaryEvidence`；实际普通和 `-O` entrypoint 的完整 serialized oracle 断言始终保留。随后 targeted 12 passed，完整 check 1116 passed。oracle 和产品预期没有调整。
3. 实际 package/source verifier 首次运行即通过，没有采失败 stdout 改 oracle。

## 边界及复核

现有 caps 原值：8 MiB 文件、64 MiB 展开、50000 行、256 列、32768 字符 cell。合成数据仅内置 CSV/XLSX，无外部路径、真实用户文件、DB、GUI、nativecaller、HMR、I05 或 SDK；没有新 selector 或通用执行入口。`registeredBusinessCapability` 仍 false。此为候选包 CLI 实测，不代表生产用户文件、GUI 或目标平台验收。

独立审查由主 agent 安排；本交付不自行指定、派发外审或替代独立审查结论。原 303 旧包的 11-case 入口不足已另在 manager assessment 留证，本候选没有更改原审树、原包或旧报告。
