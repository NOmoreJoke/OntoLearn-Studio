# cb8 受审实现到纯证据提交的桥接

本次只提交审查、处置、状态和归档索引。依据仓库外 Goal 第五节第8项：流程证据的单纯追加不自动使代码审查失效，但必须记录与受审提交的对应关系，不夹带实现或验收变更。ROOT已明确授权本次12路径本地 evidence-only 提交；不授权push／PR／CI／merge。

## 受审身份与证据

- base：`583c05c7870ba0f8f642e3eeea1d0590e5859ca2`。
- 受审实现head：`cb8c9b7a5d780544b2910901ec9141236905d65c`；tree：`b8010eea4e04f962598a80d767b7a9ea24d2d7e7`。
- 原受审源1344叶、base差异58叶；同版5构建与package094物理成员912已验。后继新增文档不将这组历史数字改写成新实现数量。
- ZCode实际新任务 `session_96ad36fbad31a8ac57ef0340ed1aa9fe`，Start Plan／GLM-5.3／最高／完全访问；原自然终稿与两次证据更正均归档，末稿492行66144B，SHA `7ae49a3b9c6bd5229dedbbd21a9054f8e2531e68fc04f41613b6131c0acea4ae`。
- MiniMax实际新任务 `mvs_3ae3cb08cd12417e99ca9fac3ab68fbf`，M3.1-Flash／xhigh／始终授权；自然终稿646行78500B，SHA `a893ab0a1d8782fe5c03d0944963f2eab17abb222f792dfa39bc24d6578f6a7f`。
- 两方均原真实本范围附条件通过，所有原意见见[逐项处置](disposition.md)，不视为无条件发布通过；原件版本、任务和仓库外raw针见[归档索引](artifact-manifest.json)。

## 唯一允许的文件差异

`docs/m0-checklist.md`仅追加T02阶段状态引用，既有M0条目、勾选和验收文本保持。其余11路径均为新增文档／原稿副本／JSON索引；原six round01–03 untracked报告不stage。明确列表如下：

- `docs/m0-checklist.md`
- `docs/reviews/T02/status.md`
- `docs/reviews/T02/fr200-fr201-20261024/round-04/zcode-glm53.md`
- `docs/reviews/T02/fr200-fr201-20261024/round-04/minimax-m31flash.md`
- `docs/reviews/T02/fr200-fr201-20261024/round-04/archive/zcode-glm53-original-final.md`
- `docs/reviews/T02/fr200-fr201-20261024/round-04/archive/zcode-glm53-first-correction.md`
- `docs/reviews/T02/fr200-fr201-20261024/round-04/archive/all-opinions-disposition-original.md`
- `docs/reviews/T02/fr200-fr201-20261024/round-04/independent-zcode-disposition-audit.md`
- `docs/reviews/T02/fr200-fr201-20261024/round-04/independent-minimax-disposition-audit.md`
- `docs/reviews/T02/fr200-fr201-20261024/round-04/disposition.md`
- `docs/reviews/T02/fr200-fr201-20261024/round-04/artifact-manifest.json`
- `docs/reviews/T02/fr200-fr201-20261024/round-04/evidence-only-bridge.md`

## 提交后精确读回

本文件所在的后继本地提交以cb8为唯一父提交；实际新head／tree必须由提交后真实Git读回，不在提交前预造自引用SHA。仓库外 `outputs/20261025_t02_evidence_only_close_031/EVIDENCE-COMMIT.json` 记录受审head→证据head／tree、每路径原／新Git blob和mode、完整patch针及提交文件列表；完整 `cb8-to-evidence.diff` 同处保留。该回执与本文件共同构成精确桥接，ROOT收取真实新head后再核远端门禁。

核验要求：除上列文档外，所有原tracked文件的bytes／SHA／mode及Git blob保持；5构建与package094包针保持；AGENTS政策覆盖15147B未暂存；旧7报告逐字保持；Git index在提交后为空。报告原稿不格式化，raw副本逐字相等；仅新撰状态、处置、索引、桥接及m0引用做文档格式检查，不复跑产品。

本次不改生产实现、测试、依赖／锁／配置、cap、验收标准或包，不stage仓库外outputs／数据库／.mimosa／AGENTS或旧WIP。独立HOLD、旧首败／UNKNOWN、2/17和待远端状态均不改变。文件相加造成的新tracked总数仅是证据叶增加，不是新功能、运行结果或再次产品验收。
