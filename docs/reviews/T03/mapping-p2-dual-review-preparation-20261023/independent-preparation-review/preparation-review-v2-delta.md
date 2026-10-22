# Mapping P2 双外审包准备审查 delta：ff0b99

结论：**首包 R1 / P2 定位缺口在 `ff0b99f0992f5410b96528231035ff7c8c8e1ae4` 关闭。** 结合保留的首包完整准备审查，本包现在可作为两项全新完整独立静态外审的准备输入排队。此为准备可用性结论，不是产品双 Pass、真实任务已创建、GUI lease 或产品运行授权。

## 固定范围与最小差异

首过程包为 `70f4323fd574d7955fcbf7e581b2d06dd1f10e1c`，本次过程修订为 ff0b99；两实际审查树仍是 detached **`c1e44f81723f9c616f669f56481d1b1ada7e57f2`**。产品 da1795、证据 4ec492、批准 base 5f910、repair base 303194 的精确角色与首报告一致。

独立 Git diff 显示只变 7 份 docs：新增 dispatch-v2 的两提示、完整清单、prepared index、correction-readback，并修订 owner generator/template。无产品、测试、依赖、锁、配置或验收改变。首 `dispatch/` 的两提示、index、1028 项清单及 preparation-readback 共五份文件在 ff0b99 与 70f432 **逐字节相同**，原阻断历史未被重写。

## R1 关闭依据

两树自身实际存在 `build/review-session/metadata/full-candidate-tree-c1e44f81.json`；字节身份均为 **273638 B / SHA-256 `a8afd3637dcc7fb613c95bd3009d20294e815a96b2043ed108a67afdef673eb4`**。它与首 70f432 的完整 1028 项清单原字节相同，而首报告已核该清单与 c1e44 的 Git metadata 精确相等。此次没有重新生成一个不同候选或改变条目范围。

新 header 分别明确自己树中该清单的完整绝对地址和 SHA，并说明不要猜固定 HEAD 内不存在的 dispatch 路径。两树的 `dispatch-index-v2.prepared.json` 均与 ff0b99 canonical index 逐字节一致；该文件只含两个请求值和 null，不含另一模型本轮实际状态/意见，不构成互泄。自己的 `metadata/preparation-tools-v2/` 含修订 generator/template 两份原字节和 manifest；独立逐件 bytes/SHA 与 ff0b99 owner 源文件匹配，提示把这两份新增工具列入额外静态范围并禁止执行。

新旧 template 比较只插入两段索引定位/工具副本说明，其余完整范围、历史、原验收、安全/执行/双审门逐字保留。首包的 866/173（含 35 docs 工具）及 11 份恢复、1028 项、59 FR/57 P0/50 原验收、完整 PRD 1255 行、附录 C–G/§10–12、M0 六节、18 真实编号、六新增/17 项包证据边界继续适用，无需因该定位修订重复产品验证。

## 提示身份与现场读回

| 角色 | 提示 bytes | SHA-256 |
| --- | --- | --- |
| ZCode | 44835 | `8106610dac75122b6846c8050e5352f51bd90319179dee838c26ffc372fc1abf` |
| MiniMax Code | 44876 | `48839f37ed03a220ea1f82cf97e67528a4a82fd7f0ee769be47b213e55288662` |

两树自身 `metadata/dispatch-prompt.md` 均等于对应 canonical v2 提示，task-actual 中 promptSha 同步相符。两份 prompt 的三份追加 policy 的 offset/bytes/hash 均匹配当前冻结快照；legacy dispatch-v2 suffix 与首包旧原件逐字相同，没有格式化旧原文来消除历史矛盾。

本次再读两树均保持 c1e44，Git status 唯一受跟踪差异仍是 unstaged AGENTS；各自 AGENTS 都为 15147 B / SHA `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`。实际 task、session、turn、settings、lease、terminalOutcome 全部仍 null；模型/思考/权限只是 requested 设置。首 audit 中看到自身 prompt 已变的可变 metadata，现在已正确对应 v2，未拿它追改首 70f432 历史 readback。

`audit-v2.py` 和实际 `audit-v2.stdout.json`/`.stderr` 保留了上述逐项结果，命令 exit0、stderr 空。该脚本仅 Git、docs 和哈希，不执行 owner generator、安装器、产品或任何验证命令。没有重复 inode 扫描或重新安装；首审六条 setup 原收据/双流、两实体环境与 inode 交集 0 的检查仍为已核历史安装证据，未升级为新树运行验收。

## 保留边界

本次没有新增产品/安装/check/pack/GUI/mock 运行，没有读 STOP 或受限 SDK/witness/descriptor/index payload，没有改产品、提示、旧记录或其他 agent 文件。独占输出仅本目录报告和审计脚本/原始输出/收据/manifest。

两项指定外审尚未真实发生。GUI 仍按 root 报告由 T08 使用，无 lease；原 owner 后续须在资源交接后创建全新任务、读回实际模型/思考/权限与真实 ID，分别取得完整终态、全文报告及逐项处置。旧 303 Pass、本地 Codex 独审、setup 成功或本次准备签收均不能代替该门。完整源码/原验收、父 57 P0、运行/包 CLI/GUI/native、两 OS、干净设备、签名安装、CI/远端及生产继续分别判定；私有 provenance 真实 build/CLI 仍禁，不被本 mapping 静态派发包覆盖。
