# Mapping P2 全新双审包：准备就绪，排队待派发

两棵新树与完整审查包准备已完成，独立准备审查发现的R1/P2索引定位缺口已在v2关闭。主控已全文读取首报告10144B / SHA `badd8805e2a85b8fedbf242966d6c0d4d1f969168e649e8501f2a3555c593ccf`及delta4828B / SHA `301e9d453b919d2e7b67678f75b467a3d79bfe92d2f6158cf73992037db43061`，并逐件核验manifest的9份文件。此为准备可用性结论，尚未创建两项指定外审，不是产品双Pass。

两树均detached在同一完整HEAD：**`c1e44f81723f9c616f669f56481d1b1ada7e57f2`**。

| 角色 | 新树 | 请求设置 |
| --- | --- | --- |
| ZCode | `.worktrees/T03-mapping-P2-zcode-review-da1795` | GLM-5.3 / 最高思考max / yolo |
| MiniMax Code | `.worktrees/T03-mapping-P2-minimax-review-da1795` | M3.1-Flash / xhigh / bypassPermissions |

绝对根为`/Users/kyle/Documents/工作/知爻/本体/`。实际task/session/turn、实际模型/思考/权限、lease与终态全部null，请求设置不能冒充实际读回。AGENTS15147B/de15保护覆盖是各树唯一unstaged差异。

产品`da1795b20c3c0d47ae975fe3371e802092a4b429`；既存证据`4ec492f07d261164283a939c65b5e835c30e561e`；批准base **`5f910b52c69d86a1076b2032e5d3c63e715947f3`**，repairbase **`30319412daf8ae4745987babf7bbed93c53b6b42`**。实际reviewHEAD不能用其中任何一个角色替代。完整共同HEAD追加文档，原173工程（包含35份docs工具）和全部138项非docs工程逐blob等于产品；没有改产品、旧验收或依赖锁。

## 使用v2完整提示

提示过程固定ref为 **`ff0b99f0992f5410b96528231035ff7c8c8e1ae4`**。从本主控仓库按该ref读取`docs/reviews/T03/mapping-p2-dual-review-preparation-20261023/dispatch-v2/`；首70f432的dispatch保留为历史，不使用其缺定位的首提示。两实际审查树保持c1e44，不切到过程ref。

| 角色 | 完整提示 | bytes | SHA-256 |
| --- | --- | ---: | --- |
| ZCode | `dispatch-v2/mapping-P2-zcode-full-prompt.md` | 44835 | `8106610dac75122b6846c8050e5352f51bd90319179dee838c26ffc372fc1abf` |
| MiniMax Code | `dispatch-v2/mapping-P2-minimax-full-prompt.md` | 44876 | `48839f37ed03a220ea1f82cf97e67528a4a82fd7f0ee769be47b213e55288662` |

各树自身`build/review-session/metadata/dispatch-prompt.md`是对应v2提示原字节；完整1028项清单在自身`metadata/full-candidate-tree-c1e44f81.json`，273638B / SHA `a8afd3637dcc7fb613c95bd3009d20294e815a96b2043ed108a67afdef673eb4`，新header已明确自己的绝对路径与SHA。自己的prepared index及修订工具/模板也有原字节副本与manifest。它们是后加ignored metadata，不冒充已进入固定HEAD；源文件/版本/读取范围明确分列。

## 完整输入与实际准备

完整旧866项路径与全部历史阶段继续保留，缺失11份历史文档按固定blob恢复；完整候选1028项、完整PRD1255行、59 FR/57 P0、50原验收、附录C–G/§10–12、M0六节、真实Z1–Z7/F01–F11共18编号均可定位。没有“原15问题”门。两历史报告、主控草案与新模型判断分别记录，不互传本轮新审意见。

原P2实际包17项、六新增边界、三拒参、source-O、三模块source/PYZ、440项inventory与74份原件保留；新树未重新执行。17共享外层进程退出码、累计三socket API观察、成功B2坐标与四CSV真实issue定位的边界均写入提示，不扩大为全系统网络/逐case独立退出或全部依赖语义证明。

两树六条独立安装命令均exit0，普通文件inode集合各16095、交集0，基础Python只读symlink单列。安装在4ec开始，之后仅增加文档；不声称c1e44新运行。没有重pack/check、产品、GUI、私有provenance build/CLI；无需因本次定位修订重装或重测。

当前状态：**QUEUED_PREPARED_NO_ACTUAL_TASK**。GUI仍按根交接调度（最近报告T08持有），本线不持桌面。原owner只在根给短lease后创建双方各一项全新完整任务，真实读回设置与ID；完整终态、全文报告与全部意见处置后另判产品双审。父57P0、GUI/native/两OS/生产、CI/远端及push/PR/合并门保持；STOP与受限payload不因本包扩权。
