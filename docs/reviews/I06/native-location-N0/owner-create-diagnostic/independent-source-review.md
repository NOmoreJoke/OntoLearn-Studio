# owner-create 有限诊断输出：独立源码审查

2026-10-22。固定产品 ref `2d0443c037919f8655214daf4af7f184e0613fd9`，相对 `7d496da72d4f32bd23c7475f572496640570368b`。仅静态核对授权诊断变更及本轮主线实际检查原件；不替指定模型外审、构建供方采用、目标运行或 N0 通过。

## 结论

本次单 test 诊断源码的有限静态审查通过，无新增 P1/P2 或越出该窗口的源码变更。新行提供同一次 owner_create 返回的有限失败信息，不将旧失败放行。**完整 npm run check 仍退出 1，不能宣称整套检查通过。** 后续分别补跑的五阶段退出 0 不抹去该 lint 失败。

本报告不签 C++ 可编译/可运行或新诊断已被真实观测，不授权构建、native 运行或重跑原失败 case。此前唯一运行窗口已消耗；旧 owner-create 通用标签仍不能确定底层根因。

## 授权及实际范围

已全文读根 `iteration-control/2026-10-21-weekly-release/I06-N0-owner-create-diagnostic-source-window.md`：2995B，SHA256 `0a60e2098e389917a19e519195f251c7183815f5d6749d8e8bcee083b6559c50`。许可仅修改 core_test 五个 CLI 标签及失败回执，保留其余八源/断言/原件，不授权 native 编译或执行。

全部只读命令显式 cwd 为 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-native-location-N0`。实际读取固定两 ref 的全差异、helper/五个 CLI 调用/Node bootstrap/main 上下文、九源字节身份、本轮 summary/result/raw，以及必要的未改动 TS lint/skip 源码。只运行 Git/stdlib 字节、JSON、静态文本及宽度算术检查，exit0；未执行候选代码、测试、native、编译或镜像输出测试。

唯一产品变更 `packages/native-location/tests/location_core_test.cc` 当前与固定 ref 相等：30037B，SHA256 `4cec7d67ba66fdf47d0ae26ba056372dc437e67ac076e768a548c334bd260319`。相对基准全 Git diff 只有该一件路径，没有其它源码或旧 tracked 证据变化。

## 具体源码核对

1. `make_owner`（固定新源码379行起）仅加 `const char* case_label=nullptr`。原 `nl_fixture_owner_create` 仍只有一次，返回值保存在原局部 status/owner；失败条件为 status 非 OK 或 owner 为零。新增唯一 fprintf 位于旧失败 cleanup/require 之前，仅在失败且标签非 null 时执行。
2. 五个 CLI 处标签恰为 `metadata`、`child`、`partial-child`、`revoke-concurrency`、`budget`；均为固定 ASCII 字面量。输出只有标签、status 的 int 表示及 owner 是否非零的 0/1，不输出 owner 数字/地址、路径、FD、业务内容或推测 errno。`%.18s` 给出长度上限；固定字节+18字节标签+11位 signed int+1位布尔的宽度上界为75B（含LF），低于160B。此为静态上界算术，不是实际格式化运行。
3. 第六个 Node bootstrap 调用仍是 `make_owner(*tree)`，默认 null，不输出新增诊断，也不误标成 metadata；成功路径亦无新增输出。没有新增 owner/child/native 查询或调用次数。
4. 逆去新增默认参数、唯一三行诊断块、五处标签，整个新文件逐字还原旧文件。因此 cleanup/owner_close/abort/require、旧通用 failure 行、case 顺序、返回、EXCL、资源上限和其余逻辑均保持原字节。28条 static_assert 原样相同，不能用标签变更放宽既有断言。
5. 其余八源逐件比较两固定 Git blob 均相同，且九件实际 hash 与 source-static-check 逐项匹配。全 ref diff 只有单 test，也证明这两个 ref 之间旧 tracked 原件未改。没有借此重新审查整套架构或更改旧报告。

## 真实检查结果：读回而非本子任务重跑

已全文读本轮 `checks-summary.json` 及九个 result JSON，独立核对所有 argv/exit 与18个 stdout/stderr 实际字节/hash。主线执行结果如下：

| 主线命令 | 实际退出与范围 |
| --- | --- |
| npm ci --offline --ignore-scripts --no-audit --no-fund | 0；本树依赖准备，stderr 有既有依赖 deprecated 警告；非 native 编译 |
| uv sync --frozen --offline --python /opt/homebrew/bin/python3.12 | 0；本树 Python 环境/本地 engine 包准备，非 native-location 编译 |
| npm run check | **1**；lint 在未改动 TS 文件189行 prefer-const 停止 |
| npm run verify:sources | 0；12个归档源 |
| npm run format:check（单独补跑） | 0 |
| npm run typecheck（单独补跑） | 0；contracts/unit/desktop 类型检查 |
| npm test（单独补跑） | 0；16文件，637通过、1跳过 |
| npm run build（单独补跑） | 0；Electron Vite 输出构建，不是应用启动或 C++ 编译 |
| npm run engine:check（单独补跑） | 0；ruff check、202文件格式、1052 Python 测试通过 |

原 npm-check.stdout 448B/SHA256 `4fbc7edf7841ba4e7d4baf952aae8320519d4e0b521129cba2e91d32b63c720c`，stderr0B；原 check 命令以 && 串联，后五阶段原来未执行，单独执行是补足其各自结果，不是第二次完整 check 绿。失败路径 `tests/unit/i06-native-location-owner.test.ts:189` 的 let current 未重新赋值，原源 SHA256 `e0946f7daf1236045d0198d989cf718ea40227d63b76e5a1407eaa1b0d501b04` 与基准相同、属于八件冻结源；本窗口未获修改权，本报告不要求越权修它。

result 记录本轮移除 I06_NATIVE_LOCATION_TEST_ADDON/I02_HMR/ROOT_SOURCE_PATH、UV_OFFLINE=1。固定 TS214–215行实际为 addonPath 环境门与 describe.skipIf(!addonPath)；TS摘要的1skip不能当 native addon 通过。纯 TS synthetic 测试、普通 Python engine 单测及 Vite 构建不证明新 fprintf 的编译、真实输出或目标 OS 行为；主线 summary 明记 newNativeDiagnosticActuallyObserved=false。

本轮静态源码结论与上述主线检查范围分开：C++ 新诊断没有获得编译或运行证据，也没有用 TS/Python 的通过掩盖它。

## 原件保护和证据身份

当前五件保护文件 AGENTS/package.json/package-lock.json/pyproject.toml/uv.lock 的 bytes/hash 实际匹配 preservation-check，未改；AGENTS 为既有 protected SHA `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`，未 stage。preservation-check 的61件旧原件/4manifest核验另属主线已保存记录，本轮没有重复大规模旧审计；本轮 Git差异已独立证明固定 ref 间旧 tracked 原件无变化。

本轮读取的过程文档身份（均非产品运行通过凭据）：

| 过程文件 | B | SHA256 |
| --- | ---: | --- |
| source-static-check.json | 2894 | 869f28780a2b47fcf851d93c6a761e0c79ef9f766c77c0e73641ed99fef94724 |
| checks-summary.json | 7030 | 470225407129806504eb882c617103b6c84e2c76118f26edc706fa631625e506 |
| preservation-check.json | 1166 | c84b79f1791e83e1894ccb7e5e7b551229956fce43a75c8a0eba31fa47278dba |

仅新增本独审报告，不修改产品、旧证据、依赖、AGENTS、Goal 或提交。下一次构建/精确运行必须由根与 T03 另作采用和授权，不能从此次静态结论取得隐含权限。
