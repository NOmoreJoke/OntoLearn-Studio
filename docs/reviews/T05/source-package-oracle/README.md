# T05 固定纯输入的独立外部 oracle

已实现417项外部业务expected及字段/来源约束，包含全部320 datasets和三个固定case-set。当前280项规格已定、137项保留必要字段pending，**全oracle尚未完成**；这些不是产品通过数。代码及数据不依赖I05 harness是否修好。

唯一代码为 `scripts/build-i05-source-package-oracle.py` 和 `scripts/test-i05-source-package-oracle.py`；交付数据在 `tests/fixtures/quality/i05-source-package-oracle/`，全部位于引擎输入/包资源之外。没有读取新I05 probe/tests/generator或其运行输出作为依据，没有运行/import产品、RDFLib、pySHACL、DB/native/GUI，没有安装或借共享环境，也没有模型/网络/付费/push/PR/merge。

固定输入为0e42a0fe349054a92817cb4d463bccdc15f6c042下的inputs 8205267B/SHA47c66ffe18613eb8cc1af6365dcfc9d866821f22c48f96d9f44725f8f7c59eaa和manifest21202B/SHA0b91c1a9366d170b5614d94c20006054a5a959be235e0f46cb150cf32335193a。按Git原字节复制并先核identity；任何hash、ID、投影、selector变化均拒绝。

业务来源为525c已收T05独立手选expected（767826B/872205…）、原C/explanation goldens、已采Q6与finite UTC设计、ee2b合同及root许可的literal接口声明。每项分别给输入sourceRefs与expectedSourceRefs，不能把source指针误当expected权威。原83全部数学图/matches/typed comparisons/heads由有限手选集合映射；83全部保留，repair不执行，E5仅当前片段。原106 operations/54 learningChecks/50 cases保not-executed，并保原操作/上下文引用及完整setup/steps，不升级原repair/保存/行为/历史验收。

纯构建可复现；stdlib自测实际覆盖完整inventory、RDF词法与string身份、query全部行/None、SHACL六字段/缺value、UTC/integer差异、预算代数、typed false/multihead/disabled、scope、DAG有序premises/occurrence roots、raw aliases、A1否例及来源/尾项/类型/哈希篡改。`record-command.py`只允许启动本模块固定build/check/test命令，保argv/源SHA/原双流/exit；不是业务runner或源/包collector。

最初构建一次误用productCases的id键，已保当时builder原字节及工具结果转录（不是伪造原双流）；检查固定原件后改为caseId。后续实际命令双流原件均保留。另自查时将版本标签改为批准合同的精确i05-reasoning-result/2、/3与i05-finite-7、8，并增加防回归断言。没有执行产品来选择预期。

12项非标准date首错按root明确许可的旧预登记断言复用，authority单列为pre-registered legacy regression assertion，不包装为独立固定库分类证明。native15/child11字段名已按literal-only固定声明补齐；完整预算准入/typed值、少数错误优先/DTO/捕获来源仍逐项pending，不借历史绿测或小图规模填平。详见 `docs/iterations/T05/source-package-oracle/field-policies.md` 和coverage.json。

当前验证仅oracle自身的构建/check/stdlib测试和Git/源码静态身份，不代替npm check/pytest/source/probe/package运行。这些产品命令在本窗明确未授权，因此未执行。新树base为5f910b52c69d86a1076b2032e5d3c63e715947f3；受保护AGENTS保持15852B/SHA78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759未stage。旧date525c和其他冻结树不动，原Goal不改；正式Job/selected/83E5repair/wholeH、SQLite/S1/parentB1、双外审/CI/目标OS/真人/develop门仍开。
