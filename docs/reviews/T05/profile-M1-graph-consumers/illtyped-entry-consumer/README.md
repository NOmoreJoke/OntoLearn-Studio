# T05 原坏 integer 的显式文本入口消费

候选 `df2fa46d1979af918a56f39aea7f61622456f81a` 的一次完整 `npm run check` 实际exit0：前端1125 passed/22 files，Python4907 passed/44既有skipped（144.41s），lint/format/types/build/ruff通过，stderr为空。12归档源核验exit0。

新增一个独立case复用原 `C-illtyped-entry` 的原data/shapes和独立golden。真实显式入口返回 **conforms=false的Datatype报告**。四stage只是同一case的对照，不是四个规范案例；旧18观察及原pending历史不改写。

## 单路径与冻结

原树/原分支从 `37ab2d5c02d459794ee9ceb80d677e8123308711` clean接续。146固定输入57733B / SHA `7d7ea0593c1424d8fe9f489a18e50f90446a6789a6c8dc16e01b14ab11c1aff7` 全文核同。唯一供方替换 `semantic.py`，从I05固定Git `91e98074a334931648e9b7c8f58a3b5e8f93a642` 原样复制为采用提交 `ec4195e`：新58495B / SHA `1a2bfd40bc30a7a4ba5f90ab79cba5d9e0a4311b028681d8ceced528e1982075`，旧56037B / `c45fda962a3aa272490d683abbec96175e21ca32de94afb1d2de006b02a3c56e`。不采用I05专用测试/过程、不整提交cherry-pick，维护责任仍属I05。

唯一writer仍是原测试文件，只在原48273B前缀后追加helper和1测试；原前缀逐byte不变。新58366B / SHA `b80cd4ae1c4622675124d7df0ed90ef3546440611644e94c89ce4a9c8b7f2ff3`。146受控=145只读+1writer；所有fixture/golden及旧393过程/主文/ZIP/gzip保持原字节。

## 实际入口与报告

| stage         | 实际调用                                   | 实际阶段及结果                                          | Validator.run |
| ------------- | ------------------------------------------ | ------------------------------------------------------- | ------------- |
| strict-before | 新API，data_policy=strict                  | parse-data拒绝INVALID_LITERAL_LEXICAL，无report         | 0             |
| wide          | 新API，integer-illtyped-report-v1 / legacy | 正常返回entryVersion=i05-shacl-text-1及完整Datatype报告 | 1             |
| strict-after  | 新API，data_policy=strict                  | 同样前门拒绝，无report                                  | 0             |
| legacy-after  | 原parse_turtle→check_shapes链              | parse-data已拒绝，check_shapes未进入，无report          | 0             |

只有wide通过真实 `validate_shacl_text`，显式 `data_policy=integer-illtyped-report-v1`、`range_policy=legacy`。observer透明委托原parse与Validator.run，不生成或回填结果。原RDF report、text report、实际数据图before/after与parse图均保存；随机结果BNode保原件、按结构比较。

API和RDF六字段严格一致：focus=`urn:m1:s`、path=`urn:m1:p`、value=`"not-an-int"^^xsd:integer`、sourceShape=`urn:m1:shape`、DatatypeConstraintComponent、Violation。原golden在实际计算后取出比较conforms/components；六字段在新增断言中独立核对，未改golden、未把expected喂入入口，也没有补造缺失value。

原坏integer lexical/datatype/illTyped和两条事实（p值与Focus类型）完整保留，Validator前后无数据变动。输入完整UTF8、C-input的`/cases/12`（第13项）、全文/两文本SHA与当前semantic/test SHA绑定，属于内容来源，不是Job/actor认证。四stage核RDFLib NORMALIZE_LITERALS及转换表keys/转换器identity调用后不变；这是具体状态不泄漏证据，不宣称所有进程状态或并发行为已验。

## 新capture与原件

正常check仍实际回归旧19测试（旧18观察+1完整性）以及新增1测试。仅设置新 `M1_ILLTYPED_OBSERVATION_DIR`，明确unset旧 `M1_GRAPH_OBSERVATION_DIR`；旧测试沿独占pytest临时目录正常运行，其固有临时观察不作为本次新交付，不归档旧D快照或再生成216MiB索引。原48273B观察器与断言不改。

新增capture仅一个case、四stage、一个真实RDF报告。`entry-normal-originals.zip` 11768B / SHA `3b59e78dfe3e5e1be0c2e31a981922d152639c34db01499601ddc8159b0219c9`，18成员/1case。完整argv/cwd/env/双流/exit与全部新增原件封存，逐member bytes/SHA/CRC核同。来源前置/最终冻结清单、固定candidate和observation/ZIP构成实际绑定，不虚构逐run146数组。

首次新helper lint的长行/导入排序及过程scope字符串长行失败均保双流，后续lint/format通过；未发生产品运行失败。完整来源、旧393冻结和原测试前缀见 `preflight.json`、`controlled146.json`、`frozen-old393.json`、`audit-result.json`。新过程仅本目录；manifest只排除自身精确路径，产品/纯过程ref另在总控交接消息给出。

新B报告只是显式API/policy对旧illtyped pending的组件补充，不倒写原strict拒绝历史，也不签正式执行链。date政策仍待用户，未自动选择。正式Job/Store/worker/selected/HΣ、83/E5/repair、父M1、指定双外审/CI/目标OS/真人/PR/develop门保持。无GUI/Electron运行/native/e2e/HMR、凭据、外部模型、付费、push/PR/merge，Goal未改。
