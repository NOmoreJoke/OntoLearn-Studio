---
title: 设计决策记忆索引
slug: intelligence-memories
description: 汇总已由用户明确拍板的 UI 与交互偏好，后续会话无需重复追问。
chips:
  - 'Steer Memories'
---

## Rule

所有已经由用户拍板的界面品味、布局结构与范围边界决策，必须作为原子 Record 存放在 `design-harness/intelligence/memories/` 下并在开工前读取：

- [2026-11-25 W6 核心壳层与菜单重构定舵](./memories/2026-11-25-w6-steer-decisions.md)：确定 Concept A+B 融合菜单、右侧双 Tab 合并以释放中间编辑器宽度、同步建立 Design Harness 与全模块视觉精修，以及“先更新 `.pen` 原型，再设迭代计划”的执行顺序。

## Why it holds

避免后续子任务或新对话反复就同一导航方案或侧栏布局向用户重新提问。

## When it doesn't

若用户主动提出推翻某项已记录的视觉方案，应新增日期化的记忆文档并标记旧文档为已被取代。

## Where it's used

- `design-harness/intelligence/memories/2026-11-25-w6-steer-decisions.md`
