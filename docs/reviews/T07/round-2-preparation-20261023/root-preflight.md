# T07 R2 root 创建前预检包

状态：**仅准备；新外部任务0，GUI RELEASED，等待root预检与内部创建调度。** 不是指定双审Pass，不复用前一轮Z结论。

产品头 `f9a1157c2fff06c8bef17fa1ec44d8eb1ebacad3`；base `5f910b52c69d86a1076b2032e5d3c63e715947f3`；新reviewHead `fdfd908e36a85140078aa1509f091de369157973`。只新增准备/依赖安装，没有无变化产品重测、native补采或候选改动。

## 两具体完整输入

### zcode

- Workspace：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T07-zcode-review-r2-f9a1157`。
- 输入：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T07-zcode-review-r2-f9a1157/docs/reviews/T07/round-2-input/full-input.txt`。
- 242491 B / 1700 newline；SHA256 `513da17b6f17e8004244cbc72c8f98dbc55a837862bd9c4d6d5c5ae80814c87d`。
- 要求设置：GLM-5.3 / 最高 / 完全访问；actualSettings、freshSID、原turn、terminal现均null，不能预填。
- Operator唯一收据：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T07-zcode-review-r2-f9a1157.runtime/metadata/operator-identity-receipt.json`（TEMPLATE_NOT_SUBMITTED；须由创建owner真实填写，审查模型只读）。
- 唯一报告：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T07-zcode-review-r2-f9a1157/docs/reviews/T07/round-2/zcode-glm53.md`。
- 唯一probe cwd：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T07-zcode-review-r2-f9a1157.runtime/scratch/probe-copy`；须真实cd/pwd后相对脚本运行，不能只用绝对脚本路径。
- 935 tracked文件中934等固定Git源，唯一例外是传播的AGENTS政策；25个f9候选原字节副本另列，status.md流程差异不说成产品变化。
- 148项必读清单，所有actualReadCompleted=false；完整EOF靠未来真实工具链证明，不能以准备期hash自签读完。

### minimax

- Workspace：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T07-minimax-review-r2-f9a1157`。
- 输入：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T07-minimax-review-r2-f9a1157/docs/reviews/T07/round-2-input/full-input.txt`。
- 242581 B / 1700 newline；SHA256 `525ac36e5e505c103760501ada799c4399b3780559891a3a1b6b28f8e2ed8ede`。
- 要求设置：M3.1-Flash / xhigh / 始终授权；actualSettings、freshSID、原turn、terminal现均null，不能预填。
- Operator唯一收据：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T07-minimax-review-r2-f9a1157.runtime/metadata/operator-identity-receipt.json`（TEMPLATE_NOT_SUBMITTED；须由创建owner真实填写，审查模型只读）。
- 唯一报告：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T07-minimax-review-r2-f9a1157/docs/reviews/T07/round-2/minimax-m31flash.md`。
- 唯一probe cwd：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T07-minimax-review-r2-f9a1157.runtime/scratch/probe-copy`；须真实cd/pwd后相对脚本运行，不能只用绝对脚本路径。
- 935 tracked文件中934等固定Git源，唯一例外是传播的AGENTS政策；25个f9候选原字节副本另列，status.md流程差异不说成产品变化。
- 148项必读清单，所有actualReadCompleted=false；完整EOF靠未来真实工具链证明，不能以准备期hash自签读完。

## 创建前root核对

1. 两完整输入均与各自role副本逐字一致，旧完整输入作为原字节suffix；新正文完整内嵌前批两作者报告、两独审、PROCESS_FAIL与7项处置。
2. 新根及scratch均固定fdfd；原base→f9全25路径/14项与PRD全文、全部历史/75原件(35log/png)/9final仍保留；没有缩delta。
3. 两环境及scratch各自physical node_modules，两个.venv独占；setup仅uv sync frozen/no-downloads和npm ci ignore-scripts，四命令exit0。setup stdout/stderr和首错保留，依赖安装不算产品验证。
4. 实现/测试/配置/锁/验收只读；模型仅写新报告、明确本方runtime日志/报告/reviewer元数据；AGENTS M不stage，旧输入/报告/证据保持。
5. 完整stdout/stderr和目标直接exit，不管道tail/head/grep；自动审批拒绝保原理由停该目的，禁换脚本/包装/路径/工具。
6. 同步本任务实际UI模型/effort/权限、官方fresh SID和原turn/附件身份收据，缺UNKNOWN不自行agent/list/sessionget/globalconfig/父目录发现；无C4窗口交接前不创建。
7. R2当前peer意见禁读，前一轮已终态封存只作历史；7项责任是登记，不虚称其他owner已接收；父能力、完整E5、CI/远端/双OS/发布/Goal保持原门。

## 保留的准备首错

`preparation-first-error.txt`记录系统Python不支持tarfile filter参数；未运行产品，未发生自动审批拒绝。原Z新根保留，改用路径校验+仅regular文件/目录解包后继续，没有删除/重建现场。初次读取旧统一input-manifest.json也不存在，已按目录中两个精确role manifest修正；未扩搜其他任务。

独立预检报告另列 `preparation-audit.md`，以实际结果填写；本文件不代替root实际预检或正式指定双审。
