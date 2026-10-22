# T05 显式 UTC date 文本入口消费

本轮验证三个输入：原 C 日期在 strict / integer-illtyped-report-v1 两数据策略下均真实 true/空报告；仅更换原 data 唯一日期的两个衍生分别真实 MinInclusive false 和非 Z offset 在 Validator 前拒绝。完整正常检查实际exit0：前端1125 passed/22 files、Python4910 passed/44既有skipped（148.15s），本文件23项通过；lint/format/types/build/ruff通过，stderr空。12归档来源核验exit0。

## 固定来源和范围

从原树/分支的 `0019036f81375d40af186b00e57957e9c0a5713d` 接续。唯一产品采用路径 `semantic.py` 原样来自 I05 固定 `6891a5842302859a531cf82767c5a482417bc274`，65749B/SHA `60008130fe0db368ea87948c2c8f079b1161f2aa951693b69635558ed1f56a07`，采用提交 `1cccff3`。不采用 I05 专用测试或整提交，语义维护仍属 I05。

产品/测试候选 `107208858229ef518c458aec96a29d4d2b366c46`：原测试58366B/SHA `b80cd4ae1c4622675124d7df0ed90ef3546440611644e94c89ce4a9c8b7f2ff3` 前缀逐字节不变，只追加301行/3参数化输入；新71658B/SHA `c0897f85943b5655bfbe44caabf788bb43cb148567e218c3c0f78d2c8d2bc029`。146受控=145只读+原测试1 writer，fixture/golden未改。

原旧474过程保持固定0019036 Git身份。当前只有总控精确授权的一处旧过程格式例外：`illtyped-entry-consumer/archive-run.py` 的scope相邻字符串合并，2564B/SHA `6cf289c57a50d58fd57f05404d4b10fb4aec12b527d77256f453f9ba64768873` →2553B/SHA `1c674533fb283be09287de7904be8afa6c390bf1065d6c6d4aa1c9650c09317b`；完整AST及所有运行常量值相同。格式提交及最终运行候选 `8e6f469ac7a64a1b3ec43edb13a8dc976ee8c4c4`。其余473当前路径不变。旧脚本没有执行，旧manifest/ZIP/观察没有修改或重生成。授权、原字节、精确patch、前后AST保存在本目录，不声称当前474全同旧pin。

## 三输入与实际报告

原输入为只读C文件 `/cases/11` 的 `C-inclusive-date-entry`，按JSON载体解码取原data/shapes；没有额外文本替换。原C用现有golden的 `ifI05ExplicitlySupportsXsdDateOperatorExtension` 条件分支。两个衍生只在测试内把data唯一 `2000-01-01Z` 分别替换为 `1999-12-31Z` / `2000-01-01+00:00`，shape不变，预期来自本窗口明确授权，分别独立ID/输入hash/数据hash并绑定来源关系。

| 输入     | 实际stage                                                               | Validator调用 | 结果                                                |
| -------- | ----------------------------------------------------------------------- | ------------- | --------------------------------------------------- |
| original | legacy-before → utc-strict → utc-integer → legacy-after → old-api-after | 0/1/1/0/0     | 两次新UTC均true/真实空报告；其余INVALID_SHAPE无报告 |
| before   | utc-strict                                                              | 1             | false，真实MinInclusive完整六字段                   |
| offset   | utc-strict                                                              | 0             | date-value阶段RDF_TERM_INVALID，无部分报告          |

原C五stage属于同一输入的隔离对照，不是五个独立规范格。新UTC入口精确返回 `i05-shacl-text-2`、实际dataPolicy、`utc-date-range-v1` 与report。旧legacy入口/version和旧check_shapes不改变。exclusive仍不支持；本次没有扩大约束白名单或复用规则comparator。

observer只透明委托原parse、check、date-value和Validator.run，不生成/修改结果。真实RDF报告（含两次空报告的conforms triple）、报告文本、数据图前后、parse图和实际返回均保原件；随机BNode按结构核，不伪造value。false的六字段为focus `urn:m1:s`、path `urn:m1:p`、value原 `1999-12-31Z`^^xsd:date、sourceShape `urn:m1:shape`、MinInclusiveConstraintComponent、Violation。真实API与RDF逐字段一致，原日期lexical/datatype及两事实不变。所有预期均在实际调用后选择/构造，未喂入计算。

每stage核RDFLib NORMALIZE_LITERALS和转换表keys/每个转换器identity调用后不变；只证明这些具体状态，没有宣称全部进程或并发状态隔离。输入全文/两文本SHA、pointer、衍生关系及semantic/test SHA为内容绑定，不是Job/actor认证。

## 原件和失败处置

只启用新 `M1_DATE_OBSERVATION_DIR`，unset旧graph和integer持久capture。完整check实际回归旧18观察、完整性与整数B；固有pytest临时观察不作为新增交付，不重打包旧3个D大快照或再生成216MiB索引。新增capture恰3输入/7stage/3真实RDF报告。

首次append长行lint经格式化修正，原前缀不变。首正常check `date-normal` exit1停在新/旧archive脚本格式检查，尚未pytest；总控授权旧路径格式例外后必要重验 `date-final-normal` exit1，因本轮遗漏创建basetemp父目录，2044项fixture setup统一FileNotFoundError，2910通过，date消费者未执行。完整35,422,850B失败stdout按要求保留，不藏失败或重写为语义结果。已记录mkdir -p并以同一候选/断言重验 `date-completed-normal`。没有修改预期、排除路径、放宽检查或改配置取绿。

新过程仅本目录，另明确登记上述唯一旧过程格式例外。完整argv/cwd/env/双流/exit、有限manifest与新小ZIP逐成员bytes/SHA/CRC可复核，原件包 `date-completed-normal-originals.zip` 为28879B/SHA `84b91228096764c6e21a105e594a4075306b09768e32f63c237f45fe3395f724`，49唯一成员，逐byte/SHA/CRC及实际来源核同。最终身份和统计见receipt、archive成员清单及独立审查。

独立agent已限定通过，无本delta P1/P2；逐项核验49成员实际来源、原RDF报告/两事实/调用数、146来源、旧前缀和格式例外。审查者未运行产品或写文件，详见 `independent-review.md`。

## 验收边界

date用户政策已定；这只是显式date组件的真实消费补充，旧date/illtyped pending和旧strict拒绝历史不倒写。正式Job/Store/worker/selected/HΣ、83/E5/repair、父M1、指定同版双外审/CI/平台/真人/PR/develop门保持。无GUI/native/e2e/HMR、模型凭据、付费、push/PR/merge或新Goal；SQLite损坏保护/HOLD及被拒资源分析停止不变。
