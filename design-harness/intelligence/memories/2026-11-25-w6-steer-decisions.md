---
title: 2026-11-25 W6 壳层与菜单重构用户定舵（Steer）
slug: memory-2026-11-25-w6-steer
description: 记录用户在 W6 启动前拍板的三项交互决策与执行顺序要求。
chips:
  - 'Concept A+B'
  - 'Single Right Rail'
  - 'Full Polish'
  - 'Prototype First'
---

## Rule

1. **导航心智（Concept A + B 结合）**：左侧菜单按认知顺序组织为「门户总览（项目库 / 学习路线图）」+「01–08 业务工作台（带实时课程关卡状态）」+「系统设置与引擎状态」；学习路线图作为独立全屏总览页，点击任一关卡可一键进入对应工作台并自动聚焦右侧导师任务卡。
2. **释放中间编辑器宽度**：将 `MentorPanel`（课程导师）与 `AgentPanel`（AI 助手）合并到右侧单一 `320px` 可收起辅助栏的 `[课程导师 | AI 助手]` 双 Tab 中；支持一键收起右侧栏使中间编辑器扩展至满宽。
3. **同步精修范围**：除壳层分屏外，同步建立 `design-harness/` 并对所有工作台子模块的视觉密度、留白、卡片层级与空/错误状态做一轮精修。
4. **先原型、后计划、再实现**：先升级 `.pen` V2 原型并经渲染验证，再制定 `W6` 迭代计划并分批实施代码改造。

## Why it holds

这是用户基于真实体验对当前“单页瀑布流 + 四栏拥挤”问题作出的明确产品决策，也是面向 `H1`（5 名真实新手可用性测试）的核心体验前提。

## When it doesn't

在实施 `W6` 期间若遇到需要改变 PRD 业务语义（如新增 P1 自动写工具或改动存储契约）的诉求，不在此项界面定舵授权范围内，须另行确认。

## Where it's used

- `design/prototypes/OntoLearn-Studio-Prototype-v2.pen`
- `docs/iterations/W6/plan.md`
