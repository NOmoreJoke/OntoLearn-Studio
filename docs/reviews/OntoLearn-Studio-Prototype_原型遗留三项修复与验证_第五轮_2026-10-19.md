# OntoLearn Studio 原型遗留三项修复与验证（第五轮）

日期：2026-10-19。对照：PRD V0.6 的 8.3、FR-004/705/802 及附录 E；第四轮 A-01 残余 / B-03 / B-04 与更新后的修复验收要求。

状态：定向静态、实际渲染、独立复核及仓库检查通过，A-01 残余 / B-03 / B-04 已关闭。旧审查的实例占位误报在此更正，不扩大为 M0 或发布验收结论。

## 1. 先纠正旧审查证据

本次在 Pen 中读取 `resolveInstances: true` 的展开结果并实际渲染，发现原件在修改前已经为 32 个 AppShell 实例设置了斜杠路径覆写，例如 `SvPUC/lNRb1`、`VVbfi/FUiuL`、`bybVu/P5Dnb` 和 `bhL4U/LYJoZ`。旧审查只按简单节点 ID 计数或自行递归解析，漏掉这些实际生效的覆写，因而误判“连续三轮仍全是状态/主动作”。上一份采纳评估也未发现该漏项，此处明确更正。

修改前的原件哈希仍为 `5552936777cfb75deac1437f20cd0b00640f30387fc912a04855ce88c7c39c57`，与备份和旧清单一致；不是核验期间文件被另行改过。修改前原生展开已有 30 个导师模式、2 个项目模式，32 个具体动作及 7 个底部动作禁用；保存状态均为“已自动保存”。

因此，本轮不把已有文案冒充新修复。旧报告关于“实例占位”的判断应撤回；模板自身的默认文案、设计态标识和两处状态/动作表达仍有优化价值，实际修改如下。

## 2. 实际修改与逐项结论

| 评审项 | 本轮处理 | 验收证据 | 当前状态 |
|---|---|---|---|
| A-01 残余：具体且单一的主动作 | AppShell 模板默认改为“查看下一步”；取消页“从快照显式续跑”改为“从快照新建运行”，Agent 提示同步明确新运行与历史运行的边界。保留其余 31 屏已正确的动作、全部 7 个禁用状态。 | 原生展开的 32 屏矩阵；预览映射/执行查询/运行检查/比较场景在相应流程中存在；取消页及禁用页真实渲染；结构/文本差异。 | 已关闭 |
| B-03：导师/项目模式 | AppShell 模板默认改为“导师模式”；保留 30 个导师与两处 Agent-Diff 的项目模式覆写。 | 32 屏矩阵与全部 Agent 标题区渲染；两个 Diff 页核对项目模式。 | 已关闭 |
| B-04：自动保存与底部状态 | 模板默认保存文案“已自动保存”、底部类别“项目状态”；工作台及 1280/1024 响应式页标注“原型设计态”，保留 V1.3 例外。保存查询页改为警示色“查询待保存”，不再一边待保存一边宣称已保存。 | 31 屏设计中的已保存状态与 1 屏待保存状态；底部当前/已过期/已取消/待确认/历史等上下文保持；全量相关区域渲染、响应式页及版本例外核对。 | 已关闭 |

比较结果页已呈现两场景结果，其主动作“下一步：查看成果”符合当前语境，保留；“比较场景”已在运行详情页提供。PRD 8.3 的例子不要求对比完成后反复比较。约束错误页、行为测试页等已有具体操作也按页面内容保留，不机械套用旧填充表。

通用的九个 Button/Badge 组件定义未改，仅修改 AppShell 内部实例及必要的屏幕覆写。没有新增/删除节点、改变业务数据或修改 E.5 固定轮次内容。

## 3. 验证方法、范围与结果

### 原生读取与差异核对

全部 .pen 内容通过 Pen MCP 读取和编辑，未直接解析或重写文件 JSON。修改前后分别保存原始 schema 快照及 `resolveInstances: true` 的展开文本/布局诊断；原生工具负责处理斜杠路径、组件继承和实例覆盖，避免沿用旧提取器的漏项。

- 56 个顶层节点（含组件定义）、32 个 AppShell 实例、2676 个展开文本节点，修改前后数量及身份保持。
- 14 处结构属性差异，42 处展开文本差异；其中 33 处是模板与工作台版本行增加设计态标识，2 处是响应式标识，其余为模板默认文字、取消措辞和待保存查询状态。完整差异限定在本轮预期范围。
- 模式保持 30 导师 / 2 项目；底部动作保持 25 启用 / 7 禁用；32 屏的模式、动作和底部状态均无占位内容。
- 原件已在 Pen 保存，再同步仓库副本。旧版保留为 `before.pen`；PRD 与历史审查报告不改写。

可重复核对命令（仓库根目录，Python 3.12）：

```sh
uv run --frozen python docs/verification/prototype-v5-2026-10-19/verify.py
```

该脚本只读取 MCP 证据快照及已归档输出，核对矩阵与差异，不修改 .pen 或证据文件；不能把离线快照检查当成对未来任意新版原型的验证。原型再次修改后须重新取得快照和渲染。

### 实际渲染与布局

已在 Pen 中查看修改后的模板、取消页、保存查询页、项目模式及其基准过期例外、响应式页；另导出 32 个工作台页、模板和两份响应式设计共 35 张原生 PNG，并逐项查看顶栏、Agent 模式与底栏的 5 张检查拼图。目标文字均可读，未发现新增重叠、裁切或模式/禁用状态回归。

原生布局诊断由 34 条变为 30 条，新增为 0。剩余诊断包括原有禁用表列、禁用底部按钮、表格操作列及自然语言范围说明等；未在本轮全面修复，不能据本次定向通过宣称整份原型不存在布局问题。全局状态组件展示中的“主动作/次操作”是组件分类示例，通用组件标签也不等同业务页占位，未为清除字符串而改写。

### 仓库检查与独立复核

`npm run check` 通过（lint、格式、类型、4 项 TS 测试、构建、ruff、11 项 Python 测试）；定向 `verify.py` 通过。`npm run verify:sources` 和三方哈希核对通过；新增本报告的同步归档后清单共 13 项。`git diff --check` 通过。

独立 agent 重算结构/文本差异并核对截图，确认九个通用组件未变、没有新增布局诊断，三个目标区域可以关闭；同时要求保留旧提取误报的更正及既有布局边界，已落实。此次在这些证据通过后才登记关闭。

未改桌面/桥接代码，不以普通 health 冒烟替代设计验证；此次不重跑桌面 e2e、打包或 CSP 探测。

## 4. 可复核文件

- [32 屏验证矩阵](/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio/docs/verification/prototype-v5-2026-10-19/screen-matrix.md) / [CSV](/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio/docs/verification/prototype-v5-2026-10-19/screen-matrix.csv)
- [结构差异](/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio/docs/verification/prototype-v5-2026-10-19/structural-diff.json) / [展开文本差异](/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio/docs/verification/prototype-v5-2026-10-19/resolved-text-diff.json) / [摘要](/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio/docs/verification/prototype-v5-2026-10-19/summary.json)
- [修改前 schema](/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio/docs/verification/prototype-v5-2026-10-19/before-mcp.json) / [修改后 schema](/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio/docs/verification/prototype-v5-2026-10-19/after-mcp.json)
- [修改前展开证据](/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio/docs/verification/prototype-v5-2026-10-19/before-resolved.json) / [修改后展开证据](/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio/docs/verification/prototype-v5-2026-10-19/after-resolved.json)
- [检查拼图 1](/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio/docs/verification/prototype-v5-2026-10-19/inspection-1.png)、[2](/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio/docs/verification/prototype-v5-2026-10-19/inspection-2.png)、[3](/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio/docs/verification/prototype-v5-2026-10-19/inspection-3.png)、[4](/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio/docs/verification/prototype-v5-2026-10-19/inspection-4.png)、[5](/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio/docs/verification/prototype-v5-2026-10-19/inspection-5.png)
- [原生渲染图](/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio/docs/verification/prototype-v5-2026-10-19/screens/) / [原版备份](/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio/docs/verification/prototype-v5-2026-10-19/before.pen) / [验证脚本](/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio/docs/verification/prototype-v5-2026-10-19/verify.py)

修复后原件与仓库 .pen 的 SHA-256：`91e35a93c77a6bcf641f5f559f455fe5425715382a267d379ca92d05f5042d34`。

本轮只核销三项原型内容与状态表达。自动保存、取消、真实任务执行与持久化仍待 M0/M1 实现及运行验证；关闭原型评审项不等于 M0 完成或产品通过发布验收。
