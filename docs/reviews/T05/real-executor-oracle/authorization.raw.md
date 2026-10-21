# 真实规则执行下一阶段：独立预期与新候选准备

2026-10-21，总控在原完整产品 Goal 内授权以下两条可独立推进的准备工作。不是 E1 正式集成、I05 新产品实现或指定双审通过。Q6 及决定单规范版本已由人类采用，不再询问。

## 已核输入

- I05 接口事实：固定文档提交 `400259f3899cf7b9edbdf36afe652fbd7f1fc52f`，22096B，SHA256 `502d7c70f670a6cc9c20e8683f0141468edaf45c1acc825fdcc6e3c71999fcae`。根已全文读取，并核对九份 C4 源码的 Git blob、完整字节/hash及当前相等。
- 供方独审11560B，SHA256 `eef6bd0e580e91fb122af723f60030dd55d358125f8f2bf9e9ab83f87b61e5ed`；根已全文读取，三份归档成员均核 hash。两项文档准确性问题已修。它是有限静态文档审查，不是新运行。
- T05 下一阶段计划固定 `6e4f19bd95d6b8850879ebb770ef003ffd9d9a61`，18158B，SHA256 `79eca34c6326a7a6d1733c971e26c4e0690efd8fa65b73600fea955d2f8daa65`，根已读且独立计划审查已接受技术和范围。
- T05 机制产品固定 `1e3e0ee1d9d5b70f1f59233d0a3c64f6d85fd2cb`；根私有阶段收口 `T05-profile-mechanism-stage-root-closure.md`。这里只批准静态读取七代码路径以形成接入方案：`quality/__init__.py`、`quality/rule_calendar.py`、`quality/rule_comparator.py`、`quality/rule_firing.py`、`quality/rule_numbers.py`、`quality/rule_profile.py`、`quality/rule_terms.py`（完整前缀 `packages/engine/src/ontolearn_engine/`）。不复制、不 import、不执行或修改这些代码；真正采用依赖另在精确实施决定中固定。

## T05：完整独立 oracle 准备，唯一作者

原 T05 会话 `01a15bce-021c-74e0-a7ac-a899380b424a` 继续，原 worktree/feature 不变。现阶段新增内容仅限：

1. `tests/fixtures/quality/real-executor-acceptance-inputs.json`：冻结输入映射及完整独立预期。
2. `docs/iterations/T05/real-executor-independent-oracle.md`：有限推导范围、逐案推导和完整性依据。
3. `docs/reviews/T05/real-executor-oracle/`：本准备阶段输入绑定、独立审查、首失败/修订历史及交付收据；不写实际执行结果或假 run.log。

读取固定 T09 `873c8c051b9870aa12fc7e1dbbd3e0c358e7c380` 的已批准17原输入文件及其 conventions/reset，以及本线原 `fr505-extension-cases.json` 的22扩展和固定 profile/spec。17 是文件数量，不当作17次已执行案例。旧输入/22扩展及已收口20机制路径保持原字节。

逐案例、阶段和 reset 独立推导完整 asserted、有限 RDFS 新增、自定义结果、全部实际规则匹配/head和依据预期。每条 RDFS 预期记录结果、公理原三元组、直接前提、所用有限规则/规范依据、推导层次及输入 ref/hash；明确结果集合为何完整、哪些输出不应出现。同结论多匹配/多依据保留；RDFS 单稳定 witness 与规则全部匹配分开。FR502 不新增穷尽全部形式证明路径要求。

不得调用 I05/T05 被测 reason、matcher、wrapper 或读取实际输出再生成 expected；不得新增第二推理器生成 golden。可用标准库做 JSON/原件/hash/结构检查，推导由独立人工式分析给出并经独立 agent 审查。源 term 规范形式和原 raw/source 分开，已丢原文显式 unavailable；不得逆造。结果不是当前产品事实或实际运行证据。

完成独立审查、关闭具体问题后本地提交，交完整 fixture、推导、独审和输入/输出 hash。本阶段不创建 E1 测试、不运行新图执行集成、不修改公共契约/Store/Job/worker/依赖/锁/UI，不推送。待实际执行器批准并按正式依赖顺序合并后，另做实际 E1 联验。

## I05：新隔离候选的具体接入方案

原 I05 会话 `01a15744-136d-7000-abad-46de101eadaf` 继续。仅新增 `docs/iterations/I05/profile-integration-new-candidate-plan.md` 及 `docs/reviews/I05/profile-integration-plan/` 的方案/只读输入绑定/独审/收据；保持 C4 原1284路径和205执行输入、产品与测试原字节，不重跑旧绿、不修改候选。

使用已交准确接口和上述七路径静态读取，给出一个可直接批准的精确新候选方案：隔离 worktree/分支与固定 base；原 C4 保留及候选替代关系；七代码路径同字节依赖采用方式和唯一维护者；真实图→完整有限 RDFS→同一冻结 closure 的真实匹配→唯一 evaluate_bound_batch→全部结果/依据，不造第二 matcher。

列出新增 profile 词法入口/受控定义 IR/全部比较与多 head 的必要产品和测试路径、兼容/版本策略、query/SHACL旧合同保留、新 source/位置的真实来源与 unavailable 边界。特别说明 `semantic_turtle.py` 如需修改的最小反例/具体 delta，不能全局关闭 ill_typed；Catalog/定义/公共错误/producer/Store/worker哪些实际依赖由 T01/T03/I06提供，哪些纯后端计算可先独立验。新 source 不能由 term 或调用方自报获得认证。

独立静态审查已发现具体包布局差异：C4没有quality包；上述固定 `__init__.py` 的旧服务懒导出访问时还依赖不在七路径内的 `definitions.py/planning.py`，旧 fresh-subprocess兼容测试也直接导入它们。方案必须冻结实际消费的 rule_* 符号、包布局及测试范围；七路径不能冒充旧quality完整服务。若需要额外依赖，向T05取得精确路径/必要性/固定字节，不整包或整commit复制；当前不增加其采用权限。

引用 T05 唯一 oracle 准备，不平行造第二份 expected。提出新专项、完整 check/source/package与源包同输入、失败/取消/晚到、版本/历史/selected保护及原指定双审/CI/合并安排。方案完成自己的独立审查、本地 docs 提交后交总控；此授权不创建/切换/修改新产品树、不批准 future4 转交、不采用未批准 worker/coordinator实现。

## 不变的门

唯一 Store writer、正式定义/引用/快照/版本与 producer 权威、当前/历史分区、完整57 P0及附录/父验收全部保留。用户当前桌面不用于 GUI/Electron/native/HMR/审查应用；真实隔离入口仍未核验。指定同版本双模型、实际完成报告、双 Pass后推送/PR、真实 CI、正常 develop 合并和远端核验不变。已有 Goal 不重建、不假称恢复或完成。
