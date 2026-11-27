---
title: UI 与设计演进治理策略
slug: intelligence-policy
description: 规定所有界面重构必须遵守的硬约束、PRD 优先级对齐与交付检查顺序。
chips:
  - 'Policy'
  - 'PRD §8'
  - 'Design Complete'
---

## Rule

1. **北极星先行**：重大结构或交互改版须先在 `design/prototypes/OntoLearn-Studio-Prototype-v2.pen` 验证布局与信息层级，再写入 `W6` 迭代计划并实施代码改动。
2. **契约与引擎零越界**：界面壳层与视觉精修属于渲染层（`apps/desktop/src/renderer/**`）范畴，严禁为追求视觉简化而削弱 `storage.py` 事务边界、删除 `DraftDiffPreview` 二次确认或伪造检查状态。
3. **测试断言零削弱**：调整视图路由后，必须同步维护 36 条真实 Electron E2E 与单元测试；允许更新导航前置点击（如先切回项目库或切页签），**严禁删除业务断言、增加 `sleep` 或放宽 `skip`**。
4. **必须逐项过完 [never-do.md](./policy/never-do.md)** 方可声称达到 Design Complete。

## Why it holds

OntoLearn Studio 承载了严格的本体一致性、版本快照与学习独立性验收口径；界面必须服务于透明可验证的工程语义，而非用表面美化掩盖状态边界。

## When it doesn't

涉及新增 P1 能力（如全局全文检索、完整专业模式）时，需单独经用户与需求口径确认，不得在 UI 精修中私自塞入未实现的功能占位。

## Where it's used

- `design-harness/intelligence/policy/never-do.md`
- `docs/verification/FEATURE-MAP.md`
