# 本次 direct 消费者独立 delta 审查

本记录由T05依据未参与实现及API顾问的独立agent `/root/directsteps_consumer_independent_review` 实际回复整理。审查全程只读，不写文件、不运行产品/测试/网络/GUI，不代替指定同版双模型外审。

最终限定通过 `d494153de742da2bf6bbff9c857b97e110ecf3dd`，本新delta、组合与原件无新增P1/P2或阻断。

- 终态后再次逐146项source Git/current/candidate/bytes/SHA核同，145只读+1 writer；原测试28706B前缀不变，新测试48273B/SHA `84119922077078cbaf9c4172e66e26d6261b2cde2880f63975e3e89bd9c43b2c`。旧254过程逐项等97297与原指纹。
- 最终ZIP 6413072B/SHA `af85ec2515f9e3da631f202f58b0c7a343b8da36dac89ef9b2e080a91072a8db`，126唯一成员逐byte/SHA/CRC核同，并逐一对应本次实际目录/command原件；18观察与index完整相同、均绑定当前源码SHA。首包d536的5104774B/43成员同样逐一核同，旧scope标签另行勘误、不覆盖原件，也不冒称最终候选。
- 全文读完整stdout和空stderr：lint/format/types/build/ruff通过，前端1125 passed/22 files、Python4906 passed/44既有skipped，145.30s，exit0；12来源核验exit0。argv/cwd/env、独占输出/basetemp及本树cache核同。
- 三图四模板、有序premises、真实首次insert、depth、完整basis均对应原golden。生产叶ID按实际N3原件hash独核，21个source occurrence/pointer/fixture SHA/前像核同。完整外7/native16/child11、restored projection、原rows bytes/digests、全部child batch/originalMatches严格相同。
- roots仅接同次实际strict restore返回的完整fixture view与原payload/rows绑定，dataclass未被当授权，也未造Job。没有另造late-shorter实际图。
- 9个D baseline receipt/events/usage/retained/peaks/caps核同；36 exact成功、36少一票resource/domain拒绝、36失败ledger重用拒绝且D快照不变。72是边界向量数，不是独立场景。
- 旧默认/2 finite7/native15成功规则图及false→error保持。9份SHACL真实report.nt逐实际bnode核六字段/API/原golden，2query完整projection，2pending Validator0/无report独核。

可受限接收本窗口三direct真实消费者。最终18观察=16规范相符+2pending，另1项完整性测试；父M1、正式Job/Store/worker/selected/HΣ、83/E5/repair、指定双外审、CI、目标OS/真人及PR/develop/发布门保持开放。

纯存储追加局部核验同样通过：两完整索引gzip逐1MiB流式解码，与build中保留的未压缩原文件逐byte比同至EOF，原长度/SHA及压缩长度/SHA均等 `index-storage.json`。首原226145369B，最终原226739109B；gzip分别4711729B及4743846B。两个小locator完整对应两ZIP的3/18条观察，成员bytes/SHA、ID/kind/assertion/actualStatus相符。两ZIP与command原件未变，首包过时scope原文未改。此项仅核压缩存储，没有重跑产品/测试或重审不变源码；原限定结论保持。
