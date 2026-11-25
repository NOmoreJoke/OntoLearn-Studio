# OntoLearn Studio Design Harness

> 北极星来源：`design/prototypes/OntoLearn-Studio-Prototype-v2.pen` + `docs/prd/PRD-本体学习与落地Agent工作台.md` §8（交互与体验需求）。

本目录以四层架构（Foundations / Intelligence / Components / Commands）沉淀 OntoLearn Studio 的前端设计真值与确定性约束，确保后续 `W6` 分屏重构与全工作台视觉精修保持一致的信息层级、色板语义与可用性底线。

## 目录结构

| 层级             | 文件                                                                                                                                                           | 职责                                                                 |
| :--------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------- |
| **Foundations**  | [foundations/colors.md](./foundations/colors.md) / [colors/roles.md](./foundations/colors/roles.md)                                                            | 语义色彩角色、对比度与旧 Token 兼容映射                              |
| **Foundations**  | [foundations/typography.md](./foundations/typography.md)                                                                                                       | 中英混排字体栈、字号阶梯与等宽数字规范                               |
| **Foundations**  | [foundations/spacing-and-layout.md](./foundations/spacing-and-layout.md)                                                                                       | 4px/8px 间距阶梯、PortalShell/AppShell 双壳层与 `1440/1100/390` 断点 |
| **Foundations**  | [foundations/icons-and-motion.md](./foundations/icons-and-motion.md)                                                                                           | 单一 Lucide 图标约束与克制动效 Token                                 |
| **Intelligence** | [intelligence/policy.md](./intelligence/policy.md) / [policy/never-do.md](./intelligence/policy/never-do.md)                                                   | 10 条硬性禁区与样式门禁                                              |
| **Intelligence** | [intelligence/vocabulary.md](./intelligence/vocabulary.md)                                                                                                     | 人机共享界面术语表                                                   |
| **Intelligence** | [intelligence/memories.md](./intelligence/memories.md) / [memories/2026-11-25-w6-steer-decisions.md](./intelligence/memories/2026-11-25-w6-steer-decisions.md) | 已拍板的 `Steer` 设计决策沉淀                                        |
| **Components**   | [components/patterns.md](./components/patterns.md)                                                                                                             | 核心壳层与复合交互模式规范                                           |
| **Components**   | [components/screens.md](./components/screens.md)                                                                                                               | 全屏视图及 `empty/loading/error/full` 状态矩阵                       |

## Design Complete 五项验收门禁

1. **Foundations 合规**：全部颜色、字号、间距、圆角、动效走 `tokens.css` 语义变量，零业务 CSS 硬编码裸 hex，无风格冲突的杂乱自绘 SVG。
2. **全状态覆盖**：每个组件覆盖 `default / hover / active / focus-visible / disabled`；每个页面覆盖 `empty / loading / error / full` 及长文本换行边界。
3. **多视口真实审查**：桌面端 `1440px`（含右侧栏展开与收起宽屏态）、紧凑屏 `1100px` 与移动端 `390px` 抽屉态均需经真实渲染截图核验，无横向溢出或遮挡。
4. **可访问性与 PRD 合规**：键盘可达、`focus-visible` 清晰、不纯靠颜色区分状态（PRD §8.9）、每屏仅有一个视觉最高优先级主动作（PRD §8.3）。
5. **确定性护栏闭环**：`W6-3` 落地样式扫描单测后，须同步跑通 `npm run check` 与全部 36 条真实 Electron E2E。
