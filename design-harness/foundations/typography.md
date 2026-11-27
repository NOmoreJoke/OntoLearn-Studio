---
title: 排版字体与字号阶梯
slug: foundations-typography
description: 规范中英混排 UI 字体、技术 IRI/SPARQL 等宽字体与少量明确字号层级。
chips:
  - 'Noto Sans SC'
  - 'SF Mono'
  - 'tabular-nums'
---

## Rule

1. **字体栈**：
   - 界面字体 `--font-ui`：`'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', system-ui, sans-serif`（离线优先系统字体，禁引入外部网络字体 CDN）。
   - 等宽字体 `--font-mono`：`'SF Mono', 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace`，专用于 IRI、前缀、SPARQL、Turtle 片段、SHA-256 摘要、快照 ID 与步骤编号。
2. **字号阶梯**：
   - 门户页主标题：`22px–24px`（weight `700`，line-height `1.35`）
   - 工作区页面标题：`18px–20px`（weight `600`，line-height `1.4`）
   - 区块标题（`h2` / 面板头）：`15px–16px`（weight `600`）
   - 卡片小标题（`h3`）：`13px–14px`（weight `600`）
   - 正文与表单控件：`14px`（line-height `1.6`），高密度表格单元：`13px`
   - 徽标、辅助说明、元信息：`12px`（line-height `1.5`）
   - 眉标（Eyebrow）：`11px`（weight `600`，`letter-spacing: 0.08em`）
3. **等宽数字对齐**：进度统计（`2 / 8`）、项目版本号、轮次计数、表格数值列必须启用 `font-variant-numeric: tabular-nums`。

## Why it holds

本体工作台同时承载中文业务概念、英文 OWL/RDFS/SHACL 术语、IRI 标识与 SPARQL 代码块；清晰的双字体栈与克制字号阶梯可确保信息密集场景下依然易读、表头与数值不跳动。

## When it doesn't

门户首次启动欢迎区允许使用 `clamp(24px, 2.6vw, 32px)` 的大标题，但打开项目进入 `AppShell` 工作台后必须收敛为紧凑标题（≤ `20px`），把垂直像素留给编辑器。

## Where it's used

- `apps/desktop/src/renderer/src/style.css`
- `apps/desktop/src/renderer/src/query/typed-results.css`
- `apps/desktop/src/renderer/src/learning/learning.css`
