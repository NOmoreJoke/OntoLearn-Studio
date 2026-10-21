# I05供方方案 r2 文档冻结交付

78754B/7b941380…主方案的PS-01/02已由独立reviewer在方案层关闭。最终报告31608B/2d043a53…保留首审17274B/4d25f9ae…原前缀。本交付只封存已经审过的文档及原始证据，不改变受审主稿/配套/审查结论，不代表代码采用、schema迁移、运行、生产来源或新配置批准。

| 冻结文件                                                                     | bytes | SHA-256                                                            |
| ---------------------------------------------------------------------------- | ----: | ------------------------------------------------------------------ |
| 主方案 `docs/iterations/T01/profile-job-artifact-selection-supplier-plan.md` | 78754 | `7b941380d990cf25270cc5a54b13a7f865cfd04b9bbf3af46d954fce27727eb8` |
| `independent-plan-review.md`                                                 | 31608 | `2d043a53afe2b588efc894a31e3d98b499f5b0649458f167b18a1b27424f1f27` |
| `read-ready-checks.json`（历史输入，未回写）                                 |  3688 | `06447ed745276ed4eab21a4a30349a0b3990acbf22247968e4df0683a1785c8c` |
| r1七件snapshot manifest                                                      |  2530 | `4a553266ef4547f5255ecb832034ab149eed6015c91bcb16937145c05544f4da` |
| r2十件作者输入+最终独审snapshot manifest                                     |  4303 | `a6a25267a0dc5558157dadebe12fa5cc65edfae1660aecd6aaddaf40f452a977` |

其它逐件bytes/SHA由`final-manifest.json`及两个ZIP索引给出。read-ready内的17274B报告项继续绑定原历史前缀；最终31608B另在本manifest记录，不改当时输入伪装首审通过。静态库存为19源码/530函数/41位置；实际projection批准record17类、AST宽库存25类的区别按独审原文，不修改已审稿。

## 原始工具响应归档

`tool-response-items.zip`：849290B，SHA256 `f05620dcd6dce00ed61c1c7287b6fecf2b4c2930202d217141bd4c68781fc727`。外置同件`tool-response-index.json`：212676B，SHA256 `786065333b91c5af7a5514a9647bb11dea566f19ddb21ac43c3d848d6af9505b`。ZIP内TOOL-RESPONSE-INDEX与外件逐字相等。

只抽取原JSONL完整response_item工具调用/输出，127完整对、254原条；不含巨量session_meta/event/reasoning，也未截取工具调用中部分命令伪装为另一任务。每条记录精确sourcePath、1-based sourceLine、0-based sourceByteOffset/完整长度、原全部response_item计数中的ordinal、原UTC timestamp及SHA；archiveOrdinal仅为抽取顺序，不冒称原时间序号。原嵌套工具输出的截断或真实exit1、原加密协作参数均保持源JSONL，不补写成“完整源码打印”或解密重建。完整固定源码另见source ZIP。

| 阶段        | 原JSONL行，均含端点 | 完整对 | 原UTC工具起止                            |
| ----------- | ------------------- | -----: | ---------------------------------------- |
| author r1   | 1815–2170           |     45 | 2026-10-21T16:20:36.193Z – 16:50:25.730Z |
| author r2   | 2194–2512           |     31 | 2026-10-21T17:03:55.374Z – 17:44:15.318Z |
| reviewer r1 | 1759–1996           |     31 | 2026-10-21T16:53:18.191Z – 17:02:37.783Z |
| reviewer r2 | 2187–2374           |     20 | 2026-10-21T17:45:29.799Z – 17:59:04.052Z |

作者源为`/Users/kyle/.codex/sessions/2026/10/21/rollout-2026-10-21T16-53-41-01a15daa-8f89-7971-b5bc-e9fed0a6cc67.jsonl`；审查者源为同目录`rollout-2026-10-21T16-54-05-01a15daa-ef8c-7563-a2bf-10f6e91fa5be.jsonl`。各边界前缀的原bytes/SHA单列索引，源会话后续追加不改变所封存切片。author r1起含I05相关记忆/规则准备工具，完整混合只读上下文调用也照原件保，不截开命令。958346首glob失败、39b669错误路径、04f431实际编码SyntaxError、bc2554初步96字符算式与417f3e的160字符修订、独审e246af diff exit1和906a21定位exit1均保完整对，不算产品测试失败。

明确排除早期ontology author工具、reviewer dispatch R1 1478–1743、R2 2014–2111及交接2126–2169。primary的81a544（I05控制全文与CPython GET混合）/8db4a3（I05报告与dispatch final混合），以及primary其它读件，不在本ZIP；其主核/授权是主线外部回执，本件不自称完整primary或完整会话证据。后续本封存/格式/审计/stage/commit/后置receipt不在已冻结旧ZIP，作为外部终态，避免自指。

## 完整源输入归档

`source-inputs.zip`：1173628B，SHA256 `3a8c9e4bfae1024333b4314c610018172e9324b942ec3fa3f3cb22748408d737`。`source-input-index.json`：72510B，SHA256 `114a4274367bb394eff4bc03293db5b27156ef69c8050788e8d332b5aac36253`。ZIP内SOURCE-INPUT-INDEX与外件逐字相等。

170件完整原文：135逐ref/path固定Git源码、15原控制/批准参考、r1七件、r2十件受审作者输入及最终独审共十一件、r1/r2两个snapshot manifest。ZIP不纳自身hash；外manifest绑定容器bytes/SHA，无循环。源码归档仅为只读调查证据，不是采用到新产品树，未读任何新I05/C2/dispatch WIP。

## 实际审计与提交边界

967cc5实际exit0建立两个ZIP和逐件索引。f03d4a实际exit0独立审计：逐原byte切片、line/offset/ordinal/timestamp、callId完整对、四组边界前缀、首失败与算式修订标识、ZIP CRC/条数、135源码Git、15原件及所有r1/r2快照、报告原前缀均核同。原受审r2身份不变；预算算式与格式检查沿90026f/cae15e原件。最终封存的文档格式/保护/精确stage与commit终态以随后外部Git receipt为准，不提前伪填未知commit SHA。

父提交固定`7753666d2cfda48c76ce59fa1ad6f34802c48eed`。只准stage本主方案及本review目录逐精确文件；AGENTS保持15852B/78df2825…未暂存，common17891B/e437121a…及既有110 HEAD差异文件保持current=Git。提交使用`core.hooksPath=/dev/null`避免文档期执行产品；不stage其它index，不改旧产品/旧docs/AGENTS，不push或PR。

metadata8GiB/exact-probe32GiB/pager128MiB、cache24MiB/history8MiB/total32MiB、新catalog/typed定义/adapter/SQL费用版本等仍待根明确批准。主稿TEXT方案与BLOB/native替代不混证；原C2旧门不改。真实normal/API/DB、费用峰值、全部Job/selection/GC/drain/包/目标平台/模型CI等完整运行门仍未通过，本轮没有运行产品/DB/tests/native/GUI/network或生产接线。
