# T03 私有 provenance 实施交接

四产品实现及独立复核已完成，最终产品候选为 `830cdd1d198bf549b563925a3a47f7f9444710bd`，分支 `fix/T03-i05-private-provenance`。目标测试 **98 passed in 1.94s**，Ruff、format、Node语法、ESLint、Prettier及四产品diff检查通过。没有执行真实全仓prepare、PyInstaller、native、full-v1/B1或GUI；root approval、semantic parity仍未取得。

授权四产品：`scripts/build-engine.mjs`、`packages/engine/entrypoint.py`、新增`semantic_build_provenance.py`及其测试。合同36587B / SHA `9d97a6a233b47abc23064a9a8f8330080d62f39b3db981de14a148880e202a04`未改。I05独占probe/tests、依赖、锁、原始两JSON未改；AGENTS15147B / de15f6ce overlay保持unstaged。相对合同基线`2fdd85375300bfbfa797588c348a205e1030ef6c`仅四产品及本目录文档有增量。

构建使用独占UUID产物和外部绑定，保留旧产物/绑定与发布归档；入口保留FLAG/selector并传播退出码。reader提供严格有界解析、source/PYZ/loader及资源身份核对，两个后置API只观察已加载对象，不导入目标。I05需在observer之后显式加载native；精确消费接口见`module-implementation-agent/implementation-and-consumer-api.md`和`consumer-interface-clarifications-v1.json`。

独立完整首审针对`32d943`发现F2/P2：distribution Python首读上限过宽且源码/代码来自两次读取。修复先经旧代码两项回归失败，再改为一次2MiB受限读取共同派生身份。独立delta在`830cdd`重做反例并关闭F2，四产品范围内未发现其他必修矛盾。两份报告已由主控全文读取：

- `final-independent-review/module-final-independent-review.md`：11615B / SHA `0c610bf50b8d3aa9914534e1cd2465be29df2702231f5d60a227f88de1e7fa44`。
- `final-independent-review/830cdd-delta/module-final-independent-review-delta.md`：6896B / SHA `2ac911d2e9991c16c58218afcb5756c4a657c6933870c9457cb1b1c5537606e3`。

主控35份初始原件、11份修订原件和独审9份文件均经size/SHA复核。首次style/test失败、04测试假阳性、恢复源码身份、归档脚本失败、raw日志尾空白及其检查范围分别保留，未用后续成功覆盖。原日志的尾空白意味着整个历史证据提交不宣称全diff无空白错误。

后续由root正式交接I05最新完整修复源和消费probe，整合后冻结最终source commit；真实构建、最终完整目录及external binding应先固定，由root提供expected SHA及独立运行窗口。现有外部executor先验证实际完整目录再spawn，保留argv/exit/双流，再关联reader证据。此交付不能代替observer集成、实际PYZ/native或source/package语义验证，也不自行授予执行批准。没有push、PR、合并或占用GUI。
