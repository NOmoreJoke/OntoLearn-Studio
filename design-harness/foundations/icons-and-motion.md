---
title: 图标体系与克制动效规范
slug: foundations-icons-and-motion
description: 锁定 Lucide 线性图标口径与 140-200ms 语义动效，严格尊重 reduced-motion 与无定时器的渲染护栏。
chips:
  - 'Lucide 16-18px'
  - '140-200ms'
  - 'prefers-reduced-motion'
---

## Rule

1. **图标体系**：
   - 对齐 `.pen` 原型的 **Lucide** 线性风格（统一 `1.75px` 描边、`16px` 按钮内图标、`17px–18px` 导航与品牌图标、`13px` 徽标图标）。
   - 禁止在组件中手绘风格不一致、线宽混乱或大面积填充的装饰性 SVG；局部关系图（RDF 节点/边图）除外。
2. **动效语义 Token**：
   - `--motion-hover: 140ms cubic-bezier(0.2, 0, 0, 1)`（按钮、导航行、卡片悬停态）。
   - `--motion-arrive: 180ms cubic-bezier(0.2, 0, 0, 1)`（抽屉、浮层与 Tab 切换呈现）。
   - `--motion-drawer: 200ms cubic-bezier(0.2, 0, 0, 1)`（右侧辅助栏收起/展开与移动抽屉）。
3. **无障碍与工程约束**：
   - 必须在全局 CSS 包含 `@media (prefers-reduced-motion: reduce)` 将过渡与滚动动画归零。
   - 渲染层业务组件与 Hook 严禁使用裸 `setTimeout` / `requestAnimationFrame` 驱动视觉动效或伪加载状态；全部由 CSS transition/state 驱动。

## Why it holds

学习与建模工具的核心是清晰与稳定感；克制的短时过渡只用于帮助用户感知面板收放方向，不制造炫技干扰，同时遵守项目零裸命令式定时器的工程护栏。

## When it doesn't

Playwright E2E 自动化测试环境或明确声明 `scroll-behavior: auto` 的页面锚点跳转，不应依赖过渡动画结束才触发交互。

## Where it's used

- `design/prototypes/OntoLearn-Studio-Prototype-v2.pen`
- `apps/desktop/src/renderer/src/style.css`
