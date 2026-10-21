# T10 导出与迁移

日期：2026-10-21（Asia/Shanghai）。Owner：聊天 `01a15bce-0a94-7870-9694-f100e78f406a`。

- 工作树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T10-transfer-export`。
- 分支：`feature/weekly-t10-transfer-export`；核验 base/head：`5f910b52c69d86a1076b2032e5d3c63e715947f3`。
- 启动状态仅 `M AGENTS.md`；保护 SHA：`db1fb184809932a27c5bfd8c91b72837d719cdbdc07d7a83860e5cba38529786`，不暂存。
- 已建立本功能 Goal，已实际回执总控。原 AGENTS 的架构计划链接在此基线缺失，已读取归档的 `docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md`。

## 责任与下一交付

只新增启动提示授权的 transfer、project-transfer、renderer/transfer、T10 单测/fixture、docs/reviews/T10 与 docs/iterations/T10 路径。不改公共契约、Store、writer、主进程/preload/App、锁、CI 和根调度文件。

当前实施：只读候选包结构/角色/路径/哈希/选项检查、安全纯文本 HTML 报告和独立页面、完整合成输入/预期、恶意样本、必要测试与独立只读内审。内部候选包版本明确未批准，不能进入产品导入或承诺恢复/重跑/重放。

当前阶段：上述私有准备实现已验证；T10 新增 Python 60 项、TS 17 项通过，最终整仓 check 为 647 项 TS / 1,112 项 Python 与构建全通过；headless Chrome 11 组攻击均为字面文本，无执行/外联。独立内审两项 P2 及延伸路径修复后复核通过。详情见 verification.md 与 internal-review.md；正式集成/父功能未关闭。

总控修正提示已全文读取，SHA `fc753a0fb54752ede1406689f3f7d5563f1f4bc391d0f1946d663c7bd60589a5`。完整包不强制原文件/推导/运行历史/会话；未选不得写入。无原文件仍可完整恢复当前状态，仅不可直接重跑；缺运行输入仅不承诺对应重放，不误降模板。

T09 获批只读输入版本 `873c8c051b9870aa12fc7e1dbbd3e0c358e7c380` 的 manifest 与 17 个固定文件已逐项哈希核验，记录在 evidence/approved-input-reference.json。仅核验固定输入，没有消费变化中 HEAD、未批准服务或用 expected 预填 Store；不增加产品通过数。

已在安全边界接收全文第九节及无桌面政策（共同指令 SHA `9717f699e14b5941e15d90269f33cbebc32ef9bec6e7439739be848753419880`），随后读取默认权限政策与 external-review-permissions.md。AGENTS 当前受保护 SHA `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759` 已实查；不暂存。权限只扩大两应用执行模式，不改变只读外审/模型/双审/付费/凭据或桌面边界；已透传独立内审 agent，未因此重跑产品检查。

## 依赖和完整验收

- T01/T00：批准的完整 checkpoint、原子只读导出和新项目原子发布导入，以及精确格式/角色 schema；当前 Store.state 不覆盖完整撤销与应用状态。
- T09/T08：真实逐 attempt 学习检查/提示/代做证据的受限投影；禁止由客户端自报独立掌握。
- T07：可支持的真实运行语义和重放输入验证。
- I06：vault、最小外发记录、端点凭据与发送授权始终排除，不能导出数据库整文件绕过选择项。
- 保留 FR-1000/1001/104、A-06–08、G.6、12.4/12.5、全部父功能和跨模块门。
- 尚未执行：正式接线、跨设备续编辑/查询/重跑冲突/撤销、真实学习联验、双平台包内与原生验证、指定双方新审、push/PR/CI/合并/远端和发布。

本机只允许无窗口 CLI/unit/Python/build/unsigned 目录包，不启动 Electron/e2e/native/HMR，不读取凭据或外发业务数据；指定审查应用等待总控预约。
