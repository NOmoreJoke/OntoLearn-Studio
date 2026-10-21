# 显式 integer 文本消费者独审

本记录由T05按独立agent `/root/illtyped_entry_consumer_independent_review` 实际回复整理。审查者未参与本轮实现，只读单路径采用、新case及本轮证据；未运行产品/测试/GUI/网络、未写文件，也未重审旧D数学。

最终限定通过候选 `df2fa46d1979af918a56f39aea7f61622456f81a`，未发现本delta P1/P2。

- 146项逐一source Git/current/candidate/清单bytes+SHA核同，145只读+1writer；原48273B测试前缀不变。新test58366B/SHA `b80cd4ae1c4622675124d7df0ed90ef3546440611644e94c89ce4a9c8b7f2ff3`。旧393逐项等37ab及原指纹。
- 新helper透明委托parse/Validator，计算后取golden，断言有效。strict→wide→strict→legacy四stage真实调用0/1/0/0；三次拒绝均parse-data/INVALID_LITERAL_LEXICAL，且无report。wide实际report.nt按原BNode结构解析，conforms=false及Datatype六字段与原API、原golden相符，不补value。
- 原not-an-int的lexical/datatype与两事实在parse图/Validator before/after完整一致。C-input `/cases/12` 原文本、UTF8 SHA/pointer与当前semantic/test SHA核同；RDFLib NORMALIZE_LITERALS及转换表keys/转换器identity调用后均未变。没有夸大为全部进程或并发状态验证。
- 新专用capture及unset旧持久capture符合范围；旧测试正常临时回归，其固有临时观察不冒充本次新增证据，不新增旧D快照归档或216MiB索引。
- 最终ZIP11768B/SHA `3b59e78dfe3e5e1be0c2e31a981922d152639c34db01499601ddc8159b0219c9`，18唯一member逐byte对应本次command/新case实际目录，bytes/SHA/CRC均核同；仅1case/4stages，index actual/expected等原observation。
- 完整stdout、空stderr、argv/cwd/env/result核同：npm check exit0，1125TS/22files、4907Python passed/44既有skipped，144.41s；本文件20项通过；12sources exit0。

此结论仅显式integer文本组件采用及真实消费补充，不倒改旧illtyped pending或strict拒绝历史，date仍待决，不签正式Job/Store/worker/selected/HΣ、83/E5/repair、父M1或指定同版双审/CI/OS真人/PR/develop门。
