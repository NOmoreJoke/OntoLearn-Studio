# M06 局部修复交接

在固定 2cf 的隔离 tree 中，只修改两条自有产品路径：

- `semantic_source_package_probe.py`：scope 入口先检查缺失 counter，使用既有 `ProbeFault("INTERNAL_ERROR")` 拒绝，再访问 canonical 模块与业务输入。
- `test_semantic_source_package_probe.py`：增加一条空 module/dataset 映射的精确失败用例，验证稳定错误先于模块查找；没有业务成功替身。

两源与原未应用提案的拟字节完全一致。移除新增 guard 和新增测试函数后，AST 与固定 2cf 各自相等；其他已跟踪产品文件未改。旧 2cf、旧 packet 和两方全部历史报告保留。

真实运行仅限根批准的新增 nodeid：先只加入测试，在原 guard 缺失时 **exit1 / KeyError**；再加前置检查，**exit0 / 1 passed**。分别保存 `m06-regression-red-01.*` 与 `m06-regression-green-01.*` 的双流和 exit。环境在本树用原锁 `uv sync --frozen` 独立准备，独立 cache、copy link mode，锁未改，没有借其他 tree 的可变环境。

两源 AST 与 diff whitespace 检查通过。**整体两源 lint、格式检查仍未通过**：当前 10 条 I001/B023 与同工具检查固定 2cf 的结果按新增行位移后完全一致；两旧源格式检查同样失败。新增 guard 与测试片段格式检查通过，但不能替代整个文件或 fullcheck。原失败、真实输出和首次大显示截断限制保留。没有整文件格式化、添加 ignore、修改 expected 或将历史失败继承为通过。

本次 independent triage 证明依赖及共享边界事实，M08 的集合措辞 P3 已在独立后出 `triage-disposition-r1.md` 更正，封审六输入未改。应用后的窄审与后出 manifest/过程收据另行固定引用。本次只交付局部候选；全部外审意见及整体门仍待新整候选处理。

后续由根协调 T03 的精确 manifest/锁/build 供应与目标基线、T01 的 ownership 正式边界。新整候选还需修复这两自有活跃源的必要格式与 lint；B023 须独立核真实闭包生命周期，不能把它一概称排版或机械修改 expected。源依赖、配置或验收变化后，双方对同一新整候选重新审完整工程及 retained 原范围，不仅审 M06。完整 check、真实打包/包内相同样例及其余原门均未被本局部用例豁免。
