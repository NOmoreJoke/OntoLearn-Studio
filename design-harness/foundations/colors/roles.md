---
title: 语义色彩角色规范
slug: foundations-colors-roles
description: 禁止业务组件 CSS 裸写 hex，所有状态表达必须绑定语义角色并配文字或图标。
chips:
  - 'Zero raw hex'
  - 'WCAG AA'
  - 'PRD §8.9'
---

## Rule

1. 业务 CSS（`apps/desktop/src/renderer/src/**/*.css`，`tokens.css` 自身除外）严禁出现裸 hex（`#xxx` / `#xxxxxx` / `#xxxxxxxx`）。
2. 每个色彩必须按用途落入五类角色之一：
   - `paper-*`：背景画布、卡片底面、分组浅底（禁止纯白之上再叠高饱和彩色背景）。
   - `ink-*`：正文与说明文字层级；正文最小对比度需满足 WCAG AA（`#172621` 与 `#52645e` 在 `#ffffff`/`#f5f9f7` 上均达标）；`--ink-muted`（`#71837d`）仅用于次要元信息、时间戳与禁用提示，不得用于大段正文。
   - `hair-*`：1px 边框与分割线（优先边框区分卡片而非重阴影）。
   - `accent-*`：每屏唯一最高优先级主动作、当前选中导航项与激活 Tab 指示。
   - `signal-*`：完成/草稿/过期/告警/错误/离线提示六类状态，**严禁仅靠颜色区分状态**（PRD §8.9），必须搭配明确中文标签或图标。

## Why it holds

在 8 个学习/建模工作台模块间切换时，语义一致的色彩信号让用户一眼分辨“已保存 vs 待确认”、“当前结果 vs 已过期历史”、“成功通过 vs 验证失败”，同时避免多作者迭代各自引入相近但失调的灰/绿/红色值。

## When it doesn't

透明占位（`transparent`）与纯白/纯黑遮罩（`rgba(..., alpha)` 模态遮罩）可使用语义化遮罩变量 `--overlay-scrim`，不计入业务裸 hex 违规。

## Where it's used

- `apps/desktop/src/renderer/src/tokens.css`
- `apps/desktop/src/renderer/src/learning/mentor.css`
- `apps/desktop/src/renderer/src/agent/agent-sidebar.css`
