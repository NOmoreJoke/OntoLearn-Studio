---
title: 2026-11-26 W7 零代码底层概念沙盒与会员订单场景定舵
slug: memories-2026-11-26-w7-zero-code-steer
description: 记录用户在 Wave 7 规划阶段确认的三项 Steer 决策、Concept A+B+C 组合方案及“先提交设计方案再编码”的执行顺序。
chips:
  - 'Steer Confirmed'
  - 'Zero-Code BA / PM'
  - 'Retail Membership & Orders'
---

## Rule

1. **目标受众（Steer 1）**：面向**完全零代码的业务分析师（BA）与产品经理（PM）**。默认新手视图必须消除 `<urn:...>`、`owl:Class`/`rdfs:Class`、N3 引号类型后缀与裸 `JSON.stringify` Diff，改用 Excel 表、PRD 原文圈词与自然语言下拉造句器承载本体操作，并保留切回标准 RDF/IRI 视图的对照能力。
2. **教学重心（Steer 2）**：聚焦**三元组（S–P–O）等最底层本体元概念循序渐进**，在正式建模前补齐 6 个微概念步骤：原子三元组 → 唯一身份 ID vs 显示名称 → 对象关系 vs 数值属性 → 类模具 vs 个体与层级 → 关系方向性与事件实体化 → 显式断言 vs 规则推导与开放世界 SHACL 体检。
3. **业务与仿真场景（Steer 3）**：新增 **Lv.1 `知味茶饮 · 全渠道会员与门店订单履约`** 零基础场景，配套 4 张仿真业务表与 **双规模数据集（10 行微缩沙盒 + 80 行含脏数据压力集）**；同时完整保留 **Lv.2 `智能工厂 · 设备运维与告警闭环`** 作为进阶工程迁移案例与 E2E 基线。
4. **界面组合方案（Concept A+B + Concept C）**：
   - `Concept A+B`：新增 **`00 三元组与概念沙盒`**（Excel 拆积木沙盒 + PRD 圈词与坏模型重构诊所）；
   - `Concept C`：在 **`01 本体构建`** 提供 `[零代码业务视图 (推荐) | 标准 RDF/IRI 视图]`、前缀胶囊、下拉造句器与三列 **`ReadableBusinessDiff`**，并在 **`04 质量与推导`** 提供 80 行压力仿真与白话证据链。
5. **推进节奏确认**：用户已审核 `OntoLearn-Studio-Prototype-v2.pen` 第 12 组五张画板（`12A`–`12E`），明确指示先将设计方案与原型变更提交 Git，再推进后续编码实现。

## Why it holds

零代码业务人员卡点往往不在按钮多寡，而在“不知道为什么要拆三元组、为什么同名会员需要唯一 ID、为什么购买动作需要订单中间实体”。把元概念拆成独立可玩沙盒并配合零代码辅助轮，才能在不牺牲严谨 RDF/SHACL 内核的前提下让 BA/PM 真上手。

## When it doesn't

当工程用户需要编写精确前缀 IRI、检查底层 N-Triples 字面量或执行既有设备运维工程回归用例时，可随时通过分段开关一键切回 `标准 RDF/IRI 视图` 或切换至 `Lv.2 智能工厂` 案例。

## Where it's used

- `design/prototypes/OntoLearn-Studio-Prototype-v2.pen`（`12A`–`12E` 画板：`Td2Qm`、`XZzbj`、`EHJ8q`、`R7leMd`、`F72Kn`）
- `docs/iterations/W7/plan.md`
