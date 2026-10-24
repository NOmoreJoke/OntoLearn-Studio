# T01 package087：固定748的指定双审与处置归档

受审实现提交为 `748008a6a15091e8c5376b53a9348002eee7a207`，受审 develop 基线为 `5f910b52c69d86a1076b2032e5d3c63e715947f3`，范围38 commits/525 files。随后仅追加本目录中的原始报告、任务回执、处置及归档映射；没有改变受审实现、测试、配置、依赖、验收或原运行产物。证据追加提交不冒称重新构建/重新测试后的产品候选。

## 本次实际结论

- [MiniMax最终报告](minimax-report.md)：新任务`mvs_77babee60113426c8b116e4558dc4b8a`，M3.1-Flash/xhigh/始终授权；当前内部演示PASS，正式HOLD。[实际终态与全文回读](minimax-task-receipt.json)。
- [ZCode最终报告](zcode-report.md)：新任务`session_027a762669c045969489f7595d6730b9`，Start Plan/GLM-5.3/最高/完全访问；当前内部演示PASS，正式HOLD。[实际终态与全文回读](zcode-task-receipt.json)。
- [逐项意见处置](opinion-treatment.md)：N1/N2、records16、scratch计费，全部Top10及MM§5#11–39分类覆盖。限制仍在，不称已修复；不放宽未ACK/UNKNOWN、origin、计费或noReplay。ROOT独立核验后接收集成门。

报告和回执按原字节归档，所有文件的原路径、字节和SHA256见[manifest](manifest.json)。报告内绝对路径为审查时的原始引用；GitHub读者可按下表读取对应归档原件，不要求访问审查机路径。

## 历史原件映射

| 原件                           | 可访问归档                                        |
| ------------------------------ | ------------------------------------------------- |
| package087第一对MiniMax BLOCK  | [原报告](history/package087-pair001-minimax.md)   |
| package087第一对ZCode内部PASS  | [原报告](history/package087-pair001-zcode.md)     |
| package087第一对完整处置24902B | [原处置](history/package087-pair001-treatment.md) |
| package085 MiniMax BLOCK       | [原报告](history/package085-minimax.md)           |
| package085 ZCode报告           | [原报告](history/package085-zcode.md)             |
| package085处置10836B           | [原处置](history/package085-treatment.md)         |

当前交付限定macOS15 arm64未签名目录包，“非正式分发，仅限内部演示”。C4–C6、D8、086失败、087 guard首败与旧BLOCK保留；正式签名/公证、完整legal/_distutils、跨平台/参考设备/D2、损坏SQLite HOLD、真实LLM、恢复演练等未关闭。完整FR和0/17由总控逐条另核，本归档及子链合并不自动计完成。
