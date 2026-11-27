---
title: 色彩系统与语义 Token 映射
slug: foundations-colors
description: 提炼自原型 V2 的浅色学术工作台色板，所有组件必须消费语义 CSS 变量。
chips:
  - 'paper / ink / hair / accent / signal'
  - 'tokens.css'
---

## Rule

渲染层必须通过 `apps/desktop/src/renderer/src/tokens.css` 中定义的语义变量引用颜色，禁止在组件样式文件中直接书写裸十六进制色值（详情见 [roles.md](./colors/roles.md)）。

- **Paper（底面与层级）**：`--paper-bg: #f5f9f7`、`--paper-surface: #ffffff`、`--paper-subtle: #edf5f2`
- **Ink（文字层次）**：`--ink-primary: #172621`、`--ink-secondary: #52645e`、`--ink-muted: #71837d`、`--ink-inverse: #ffffff`
- **Hair（边框与分割）**：`--hair-border: #d8e3de`、`--hair-strong: #b8ccc4`
- **Accent（品牌主青绿）**：`--accent-primary: #0f766e`、`--accent-hover: #115e59`、`--accent-soft: #e6f4f1`
- **Signal（状态信号）**：`--signal-info: #0369a1` / `#e0f2fe`、`--signal-success: #15803d` / `#dcfce7`、`--signal-warning: #b45309` / `#fef3c7`、`--signal-danger: #b91c1c` / `#fee2e2`、`--signal-hint-bg: #fff7df`

在 `tokens.css` 中保留既有别名 `--bg`、`--text`、`--secondary`、`--muted`、`--border`、`--accent`、`--soft` 分别指向对应新语义 Token，确保渐进迁移期间零样式回归。

## Why it holds

浅青灰纸面底色（`#f5f9f7`）配高对比墨绿黑主文（`#172621`）与沉稳青绿强调色（`#0f766e`），契合“本地优先、理性可信、低视觉疲劳”的本体学习与建模工作台气质；将颜色收口到语义角色后，可由确定性 lint/单测拦截色值漂移。

## When it doesn't

- **高对比焦点环**：浏览器原生或无障碍聚焦环（`:focus-visible`）固定消费 `--signal-info`（`#0369a1`）以保证与青绿主按钮区分度。
- **第三方只读图表/语法高亮库**：若外部库仅接受 JS 常量，须从共享 Token 映射表读取，不得另起一套配色。

## Where it's used

- `design/prototypes/OntoLearn-Studio-Prototype-v2.pen` 全局变量表
- `apps/desktop/src/renderer/src/tokens.css`
- `apps/desktop/src/renderer/src/style.css`
