---
title: 核心交互模式规范（Patterns）
slug: components-patterns
description: 定义双模闯关导航、统一右侧双 Tab 辅助栏、顶栏上下文与抽屉模式的组件行为边界。
chips:
  - 'GroupedCourseNav'
  - 'UnifiedAssistantRail'
  - 'ContextTopBar'
---

## Rule

1. **双模闯关左侧栏（`GroupedCourseNav`）**：
   - 分三组：`门户`（`我的项目`、`学习路线图`）、`核心工作台`（按 `01 本体构建 → 02 数据映射 → 03 本体查询 → 04 质量与推导 → 05 行为定义 → 06 情景推演 → 07 迁移练习 → 08 导出与成果` 排序）、`全局设置`（`模型与隐私设置`）。
   - 未打开项目时，工作台列表呈现引导空态提示或禁用态（须带 `aria-disabled` 与文字说明“打开或创建项目后可用”）。
   - 底部固定紧凑型 `本地引擎状态` 条：正常时显示绿点与版本摘要，断连/异常时高亮并提供一键检查/展开诊断。
2. **统一右侧辅助栏（`UnifiedAssistantRail`）**：
   - 默认宽度 `320px`，支持顶栏开关收起为 `0px`；展开时顶部提供标准 `role="tablist"`：`课程导师`（`MentorPanel`）与 `AI 助手`（`AgentPanel`）。
   - 两个 Tab 切换时使用 CSS 显隐或受控挂载策略保持未提交输入框草稿与已展开提示状态；从学习路线图点击某关卡进入模块时，自动展开右侧栏并切换至 `课程导师` Tab。
3. **顶栏与上下文抽屉（`ContextTopBar` + `WorkspaceDrawers`）**：
   - 检查点恢复（`ProjectCheckpointRestorePanel`）与后台任务列表（`durable-job`）不再平铺在工作台下方或上方，改为顶栏两个带计数徽标的胶囊按钮，点击后以右侧/顶部抽屉展开。
   - **单一主动作原则**：任何弹出抽屉内的操作不得抢夺中间编辑区主按钮的视觉权重。

## Why it holds

将高频导航、低频管理、辅助陪练与编辑器本身拆清职责边界，可使 `1440×900` 视口下编辑器有效工作面积提升约 40%–60%。

## When it doesn't

当发生致命连接中断（`connection` 离线对账）或工作区冻结（`workspaceFrozen`）时，必须在工作区中心显式覆盖可恢复操作提示，不得藏在抽屉内。

## Where it's used

- `design/prototypes/OntoLearn-Studio-Prototype-v2.pen`（`Component / AppShell`）
- `apps/desktop/src/renderer/src/shell/`（`W6-1` / `W6-2` 创建）
