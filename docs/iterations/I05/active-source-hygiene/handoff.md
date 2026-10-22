# 两自有活跃源的格式与 lint 修复

本组件从固定 M06 候选 `401a6844d25b8990606ae82fc85f932cac352d40` 切出独立 tree，只修改 probe 与其测试两条产品路径。旧 M06 的红→绿单例及旧 10 条 lint/整体格式失败记录均保留；本次不回写旧候选，也没有修改 ignore、expected、selector、资源 pin、公共错误码或共享依赖文件。

实际改动分三项：两源按本树独立环境中的固定 Ruff 格式化；`_b1_observation` 内同一个 rdflib 导入的三 alias 排序；为 timed、build 与四个 lambda 的六处显式绑定本轮九个对象，均为同名可选 keyword-only 默认参数。

先行独立生命周期分析确认当前 caller 同步立即调用，没有观测到跨轮 late-binding 运行错误。显式绑定表达本轮对象归属，不据 warning 虚构旧代码错误。默认值保存同一对象强引用，不复制、冻结对象；原地变更仍可见。私有签名确实增加可选 keyword-only 参数，已有 timed 三位置参数及其他零参数调用保持兼容。创建默认值仍在各 timed 的计时起点之前，不承诺真实耗时、回收或物理内存不变。

应用后独审未发现 P1/P2。严格撤去六处九个默认绑定并恢复唯一 import alias 排列后，完整 probe AST 与 401a 相同；完整测试 AST 无需处理即相同，COMMENT 序列也保持。M06 guard/test、同步 caller、底层调用表达式与参数、CollectionBoundary 前后检查仍为原 AST。该结构证据不覆盖运行时反射、未来调度/异步或实际语义运行。

本次真实两源 Ruff check **exit0**，输出 `[]`；两源 format check **exit0**。格式前后另核完整 AST 相等。自有 `.venv`、独立 cache、copy link mode，沿用原锁准备工具，未借其他 tree 可变环境。未执行 pytest、B1、canonical、full417、新 probe、打包、DB 或 native；没有把两源静态通过扩大为 fullcheck、产品验收或外审意见关闭。

下一整候选由根协调接 T03 的精确三路径 manifest/lock/build 供应；不主动复制旧 23 包锁。完整 `npm check` 的 pytest 会通过现有 full_run fixture 真调用 `run_fixed_suite("full-v1")` 并加载 canonical，因此须与根明确该实际运行范围及全部资源/身份门，不通过 skip、删 fixture 或换假成功绕开。接线或依赖变化后需实际完整验证与同版双方全工程审查，含原 retained 范围。冻结入口当前仍缺真实 frozen build provenance，包内 parity 尚未接通。

核心证据位于 `docs/reviews/I05/active-source-hygiene/`：原独立生命周期材料、应用后独审、实际工具双流及结构证明。所有来源字节和首次失败/更正均保留；后出组件清单只封本组件，不声称 T03 供应已采用。
