静态结论：两项 P2 合同矛盾需修正后再冻结实施输入。

审查版本：39999B，SHA256 `647ebc71a51cb6b912aaf9a15c96409cc97a21623cf6bed5c3ea4419e8559eba`。

1. **retired 规则可能永久阻断同库重开。** [§2.1/§3.2](/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-model-gateway/docs/iterations/I06/project-location-capability-and-cohort-offer.md:37)要求残留继续保护，并一概拒绝与 retired 身份相同的 DB；这与 §5 同库、同 UUID 主动重开冲突。应明确区分私有永久保护项与数据库生命周期项：保留 inventory，只有真实 released receipt、精确对象身份和新 DB purpose 能允许数据库重新获取；私有项始终不得例外。

2. **最终名占位与不覆盖发布互相冲突。** [创建用途表及发布规则](/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-model-gateway/docs/iterations/I06/project-location-capability-and-cohort-offer.md:63)若先以 `O_EXCL/CREATE_NEW` 创建最终叶子，关闭候选后 no-replace publish 必然撞本方占位；删除占位再发布又引入窗口。建议最终名仅作 authority 内的父身份＋basename 预留，SQLite 在独占 staging 文件组完成后一次 native no-replace publish；外部抢占则保留 staging 并拒绝，不覆盖。

另需收严 [多链接闭合表述](/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-model-gateway/docs/iterations/I06/project-location-capability-and-cohort-offer.md:39)：不仅“所有已知名字均受保护”，还须实际不同目录项数与 linkCount 闭合。例如 nlink=3、仅发现 final/pending 两名必须 unknown；无需因此扫描全盘。

其余未发现新增阻断：固定 engine 引用、迟到初始化和真实未 settled、首内容 I/O gate、同 SQLite 实例 VFS、disabled-model binding、两 OS 待验证及唯一 owner 边界均明确。跨进程 native fence、ABI、锁和发布耐久性仍是后续阶段必须实证的前置。

已全文读回准备指令、最新 common、AGENTS及固定 T01 计划；未读取未批 runtime，未测试、构建、启动 GUI 或修改文件。本结论不替代指定模型外审。
