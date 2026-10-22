# I05 protocol3：F1 精确 delta 独立复核

结论：**DOCUMENT_DELTA_PASS（仅纯规范修复）**。新候选 `15401ec287e33becc09ad7154388b4814644cd47` 已关闭首审 **F1/P3**；本次 delta 未发现新增问题。原 d355 候选及首报告 NEEDS_CHANGE 保留，不改成历史 Pass。这不是协议实施、实际依赖/parent 兼容、构建、运行或指定双模型通过，也不授予任何执行窗口。

## 固定关系与范围

唯一树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-i05-semantic-offer-owner-review`，分支 `docs/T03-i05-semantic-offer-owner-review`。入口 HEAD 实际为15401ec，index空，tracked dirty仍仅保护AGENTS。首候选 `d355d384470d6de30c28229945cb77a65cca3dd4`；首报告已封于 `289fa9877e864a5ae5aa4f3b0593f6d454dce351`，也是本次 repair base。

独立核 Git delta 恰15路径：3既有文件修改、11新repair payload及1 delta manifest。14 delta payload共131545B；manifest19571B、SHA256 `d07d3eceb67d40826ac653161b0eadff66ff872c0d79eb541f4229440bb99ff1`。候选整个新prefix共59文件，58payload3857741B加本manifest19571B，总3877312B；每件current=固定Git=新manifest bytes/SHA。新manifest自身也与固定Git/hash相符。

base原47件中的44件逐byte保持；唯一3改动是profile-change-index、materialize-documents、protocol-selfcheck。完整descriptor、四schema、field responsibility、dependency/guard及合同正文、consumer/接口、原candidate-manifest、首报告/checks、原首Fail/全部旧日志、54旧负例与15有效变体、原26新反例均没有改变。原D0/D1、产品、四writer、锁、tests、CI不在Git delta。没有重开未变规范作无变化整轮审查，也未把3.8MB清单当作已执行产品证据。

## F1 / P3：CLOSED

修复后的索引新增一行 `#/independentParentProfile`：old=null、new=null、newProperty=true。descriptor仍原字节；旧descriptor确实没有该键，而新descriptor有明确null。独立以键存在性和类型敏感JSON逐值比较重新计算全部顶层变更，精确21行与索引一一对应；删除这一行后，其余20行逐值等首候选原索引。没有靠改变null、填parent批准或删字段来掩盖缺口。

生成器仅把条件改为“键是否存在不同，或值不同”，因此absent→null不再被get(None)合并。本次没有执行生成器；已读其完整精确Git diff，并以stdlib AST核语法。新生成规则与本次21行实际结果相符，没有改其其它输出、旧输入或物化阶段行为。

protocol-selfcheck新增独立的profile_index_relations：

- 计算presence-aware实际变化键，索引pointer唯一且与变化键全集相等；
- 每行只接pointer/old/new/newProperty四键，newProperty为布尔并等实际旧键存在性；
- old/new与真实旧新descriptor值逐项同类型深度相等；
- main在原design_relations及原26反例之前执行新索引检查，原断言没有删改。

新增三个有限反例的完整JSON均解析并核其真实mutation：一是删除新增null行；二是在新profile增加唯一未索引的 `syntheticUnindexedNull:null`，其它profile值不变；三是把已有新增null行的newProperty从true改false。独审使用自己写的presence-aware预期索引计算与mutation应用，三例均独立拒绝，没有调用作者工具。它们分别覆盖首缺口、额外null新键和伪称旧属性，未用无关字段损坏制造拒绝。

这关闭的是精确profile变更索引与其有限检查的可追溯性缺口，不证明parent已经有独立已批profile。原actual pins、批准记录、依赖/consumer/collector/writer/toolchain及scope根仍null/空、executionAuthorization=false；这些文件本次未变。

## 日志与实际检查

完整读取本次处置、checks、全部新日志原文；逐件bytes/SHA与固定Git核同。作者新增自检首跑exit0的stdout实际记录21行索引、3个presence反例拒绝，原26反例继续拒绝；stderr0B。formatter write/check及处置格式日志与checks记载一致。作者的exit0是封存文档日志事实，不是本独审重新执行作者工具或JSONSchema引擎的结果。

本独审只普通文件、只读Git、stdlib JSON/hash、类型敏感集合/值比较和文档AST。未执行materialize或protocol-selfcheck、未import产品，未安装、resolver、compile/pycompile、build、probe/collector/archive/loader/DB/native/GUI或模型运行；未读fee/caller停止现场、SDK/二进制/witness/受限归档payload。不暂存、不提交，仅新增本delta报告及checks。

独审自身两次辅助检查错误及完整stdout/stderr保存在independent-delta-checks.json：首次额外意图检查猜错合成null键名（5ecf09，AssertionError），此前身份/21行索引及三例独立拒绝已完成；随后一个展示器假定mutation value总是列表/对象，遇第三例标量false产生TypeError（f87c4e）。两者只修正本独审的ad-hoc文档检查，没有改候选或作者断言。最终按实际pointer/type核验通过；不冒首跑全绿或产品失败。

原完整首审对来源、失败保全、信任、真实CodeType、26/23/22/8/33分维与45/33/58 scope、G02/G03分工及未验父门的结论继续适用。后续由原T03全文读回本报告并封存，再交总控精确设计接收；产品采用和运行仍另有明确前置。
