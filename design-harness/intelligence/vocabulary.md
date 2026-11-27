---
title: 人机共享界面词汇表
slug: intelligence-vocabulary
description: 统一产品设计、代码组件与测试沟通中的界面概念命名，消除需求 brief 歧义。
chips:
  - 'Shared Vocabulary'
  - 'Portal / Workbench / Rail'
---

## Rule

在讨论、原型命名与组件开发中统一使用以下精确词汇：

| 中文词汇           | 英文/代码标识                                        | 精确含义                                                                                                  |
| :----------------- | :--------------------------------------------------- | :-------------------------------------------------------------------------------------------------------- |
| **门户态**         | `PortalShell` (`projects` / `learning` / `settings`) | 不依赖单一编辑画布的全局一级视图：项目库、学习路线图、模型与隐私设置。                                    |
| **工作台态**       | `AppShell` (`workspace`)                             | 已打开项目后进入的专业实操环境：左分组菜单 + 中单一模块编辑器 + 右可收起辅助栏 + 底反馈栏。               |
| **双模闯关菜单**   | `GroupedCourseNav`                                   | Concept A+B 融合的左侧导航：门户快捷入口 + 按 `01`–`08` 认知顺序排列的模块列表（带当前关卡状态徽标）。    |
| **统一右侧辅助栏** | `UnifiedAssistantRail`                               | 宽 `320px`、可一键收起至 `0px` 的右侧单栏，内含 `[课程导师 \| AI 助手]` 双 Tab。                          |
| **上下文顶栏**     | `ContextTopBar`                                      | 工作台 `56px` 顶栏，展示项目名/版本、保存态、引导/辅助模式、检查点/任务抽屉开关与右侧栏收放开关。         |
| **上下文抽屉**     | `WorkspaceDrawers`                                   | 承接“检查点恢复”与“后台任务状态”的按需弹层，替代旧版在页面中部长期平铺的巨大区块。                        |
| **四段式错误卡**   | `ErrorDetails` (`what / why / fix / detail`)         | 面向初学者的可恢复错误表达（PRD §8.6），默认折叠底层错误码/技术细节。                                     |
| **概念沙盒**       | `FoundationSandbox` (`00 三元组与概念沙盒`)          | 位于 `01 本体构建` 之前的零代码前置模块，分步训练 S–P–O 三元组、唯一 ID、属性区分、事件实体化与开放世界。 |
| **零代码造句器**   | `ZeroCodeTripleBuilder`                              | 用 `[主体对象 ▾] — [关系/特征 ▾] → [关联对象 \| 填写数值]` 下拉拼接代替手写 IRI 与 N3 字面量的编排器。    |
| **PRD 圈词与诊所** | `PrdConceptClinic`                                   | 以四色下划线在 PRD 原文中标出实体、关系、属性与规则，并对照诊断“二元直连坏模型”的重构练习卡。             |
| **业务可读变更表** | `ReadableBusinessDiff`                               | 替代裸 `JSON.stringify` 预览的三列表格（变更动作 / 业务可读事实 / 影响说明），底层 JSON 折叠按需展开。    |
| **双规模仿真开关** | `DualScaleDatasetSwitch` (`10行微缩` / `80行压力`)   | 同一业务案例提供 10 行清晰图谱微缩集与 80 行含同名/空值/异常值脏数据的真实压力集，供建构与体检切换。      |

## Why it holds

建立唯一词汇表后，后续 `W6` 与 `W7` 拆分、原型标注与代码模块命名可以一对一映射，减少跨端沟通损耗。

## When it doesn't

底层 Python 引擎与 `@ontolearn/contracts` 的 RPC/DTO 字段保持既有契约命名不变（如 `guided` / `assisted`、`MentorPanel` 内部桥接名称），仅在 UI 壳层与文档中使用上述词汇。

## Where it's used

- `design/prototypes/OntoLearn-Studio-Prototype-v2.pen`
- `docs/iterations/W6/plan.md`
- `docs/iterations/W7/plan.md`
