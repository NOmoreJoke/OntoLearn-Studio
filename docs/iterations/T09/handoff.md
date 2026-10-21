# T09 接口与只读交付

## 当前范围

基线版本 `prd-v0.6-learning-1`。公共输入位于 `tests/fixtures/product-baselines/`；课程位于 `content/learning/`。这两处由 T09 唯一维护。文件是内部只读测试输入/课程格式，不是新公共 IPC 契约。原始 PRD 字节不变。

`manifest.json` 固定所有输入、预期、CSV、查询和课程文件 SHA，并绑定 PRD SHA。`coverage.json` 保留 G 的 50 条原文；`cases.json` 给出独立基线、前置操作、具体输入、版本、预期和失败路径。G.5/G.6 为跨模块适配计划；A-10 完整指定评估集仍须 T08 实际提供，固定三个反例只是子集。输入准备、真实执行与发布证据分别记录在 status.md。

## 实际入口

```sh
python3 scripts/verify-product-baselines.py
python3 scripts/verify-product-baselines.py --reset G-base
python3 scripts/verify-product-baselines.py --reset G-map-empty
python3 scripts/verify-product-baselines.py --reset G-behavior
python3 scripts/verify-product-baselines.py --reset E.5
```

reset 每次重新核验 manifest，向 stdout 导出独立原始模型；不继承上一用例、不预填推导、不写 SQLite。T01 批准的应用服务将导出数据经唯一正式 Store 写通道创建新测试项目；T09 不直接添加 Store/worker/协议逻辑。必须记录项目身份、fixture/input/rule/behavior/semantics 版本及 manifest SHA。用例前置操作在新项目中显式执行。

未指定的命名空间、普通工单/通知 ID 和 CSV 行号等见 `conventions.json`，它们属于实现约定，E.5 的 W001–W016 与 PRD 顺序不变。G-base 与 G-behavior 使用标准 rdf:type，与 I01 描述谓词 fixture 不混用。E.5 工单完成不自动把告警置 Closed，两个指标分开核对。

## 各线精确接入需求

- T01：从 reset JSON 经批准内部 API 创建全新项目；需要完整保存 ontology/facts/mappings/queries/constraints/rules/behaviors/scenario 与来源；学习记录应持久化 project/task/attempt/inputVersion、最高提示层级、辅助来源、操作完成、独立迁移成功、检查状态、证据引用、阶段成果。学习记录不宜伪装成正式断言；schema 及写通道由 T01 设计维护。
- T00/各领域：按 `content/learning/checks.json` 为每个实际检查提供只读内部适配器。`LearningService.check()` 调用 `ApprovedTools.execute_check(check_id, context)`；返回 ToolEvidence 必须取自实际持久运行，包含项目/任务/尝试/输入版本、当前成功状态、完整领域结果、依据 ID 与真实辅助归因。没有 adapter 时返回待依赖，不能把 expected 文件作为实际 payload。公共契约由 T00 审定发布，T09 私有 Python 类型不直接暴露 IPC。
- T06/T07：只读消费 G-behavior/E.5 与 cases；T06 专属算法 fixture 不回写公共目录。B-10 保留 E-M4→E-M3；B-11 两通知不可去重；E.5 每种产能两次独立重放。测试输入中的 DSL 是固定计划，需真实领域适配，不是另一个领域执行器。
- T08：接受足以完成任务的 Agent 修改时，T01 的实际操作账本记录 `agent-full-assistance`；导师/项目模式切换、重开或重复检查不能清除。新尝试不能复用被完整代做的已完成数据来声称独立成功；需要全新迁移输入和跨尝试修改来源。传入 evidence.assistance 应由账本计算，不能信任客户端声明。
- T10：通过 `LearningService.report_record()` 获取白名单学习投影；依据 IDs 对应实际工具结果与阶段产物。报告应按数据版本和过期状态分组，区分独立/部分提示/完整示范/Agent完整代做，并排除凭据。导出实际 HTML/包的验证由 T10 完成。

## 资源预约

纯服务/内容候选完成内审与必要验证后，请总控预约本精确 worktree/base/head 的 ZCode GLM-5.3/最高与 MiniMax M3.1-Flash/xhigh。未获预约不操作应用，不运行本机 GUI/e2e/native/HMR。后续集成、双审、PR/CI/merge 和完整 T09 仍在本聊天继续。

## 多阶段证据与实际 Store 探针

query 任务中的 Q-01/Q-02 分别需要 Open/Closed 输入，V-01 需要删除/修复前后两个阶段。适配器必须保存尝试根输入与每个阶段的真实输入版本、快照和结果引用，明确历史阶段与当前终态；不得把历史 Q-01 结果改贴成 Q-02 当前版本。T09 当前内部 `Context.input_version` 绑定聚合检查的当前终态；公共阶段证据契约仍待 T00/T01 批准，正式接线验收前必须提供逐阶段版本/结果对应并测试迟到与跨尝试混用拒绝。

私有 `store_seed_plan()` / `seed_test_project()` 仅用于把 reset 模型写入全新测试项目，使用本树批准 base 的 `Store.commit`，不改 Store/schema，不接受覆盖已有项目。T01 仍负责产品创建/学习记录与正式审批/确认路径。实际临时 SQLite 测试证明版本化输入可还原到 Store，不能证明约束、规则或行为可执行。E.5 导入只保存输入与两套产能场景，预置 expected 不写入项目、推导或当前运行结果。
