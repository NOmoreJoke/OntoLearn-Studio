# 3ef2f69 最小cleanup delta独立复核

结论：**本次最小delta的静态预算/持有审查通过，1316050中receipt失败的外层局部引用清理项可关闭。** 未改费用、caps、委托前预留或最终快照顺序。实际专项/全仓验证由根另行运行，本审未代跑，不将测试源码存在写成运行通过。

## 固定身份与范围

- ref `3ef2f6952ed1a4f852da31c0bef7e8d8679752a5`，parent `1316050a895a787b7b94bbe18e99efcb3cd141d2`。
- main `semantic_profile_restore.py`：50276B，SHA-256 `aa3d51c1ccc487ce21a78560ad6cdf7a6485cc86f746c29ee329e6a0bc4c4d09`。
- limits test：21089B，SHA-256 `4eed5e316f0033080b3f2761b83ddcd53f093f18a6e2aa48706619d109872a8c`。
- `candidate-3ef2f69.json`的72项逐Git bytes/hash核同，仅上述2路径相对parent变化，另70项逐字不变。budget完整文件不变；main AST只有`restore_profile_batches`变化。`_restore`、projection生命周期、entry context、A16前票、usage/peaks求值顺序及全部cap沿用已复核1316050。
- 只读该最小diff及必要函数上下文、3个新增故障回归；未重开71循环/trie/scanner/parse等未变审查。完整hash记录在`delta-3ef2f69-audit.json`。旧两份审查与证据保留。

## 失败与成功生命周期

core:1190先把`children/parse_usage/caps`初始化None，覆盖入口失败尚未赋值的路径。

`_restore`成功返回后，这三组普通local可能暂持native tuples；constructor、usage或peaks求值失败均进入有限error分支。finally的1257在decoder.drop/ledger.cleanup之前把三个local置None；1258–1259在已有error时清outcome。随后清decoder、rows引用、cache/pools，才cleanup ordinary live并finish失败。因而新公开RestoreFailure的本函数frame不会保留这五个局部的native中间结果；不是先归零live再持有该children前缀。

正常构造完成时，三个临时local也清None，outcome作为唯一成功转交对象保留；decoder普通临时被清理，finish成功后仅return outcome，不产生第二份receipt或后置分配。不退款、不重用ledger、末slot无部分发布不变。

若清理/终态动作自身抛出BaseException，1267–1269在继续抛出前清outcome与decoder；不会因终态失败仍从此函数成功返回receipt。本结论限定于这次外层locals及成功转交，不扩大为任意解释器/C扩展故障的所有traceback帧均无对象。

## 回归与收费

新测试对constructor、ledger.usage、ledger.peaks三个实际receipt故障点注入MemoryError；断言只有目标故障一次、有限RESTORE_INTERNAL、原异常不作为context/cause、ledger failed/live0，并遍历公开traceback本函数frame核`children/parse_usage/caps/outcome/decoder`五项均None。测试使用实际捕获native case，不用伪child替代。

本审没有执行这3个故障案例或全专项；运行通过须引用根新候选真实记录。本次静态采集使用Git/hash/stdlib AST，无产品import、共享env、GUI或外部调用。

新增清理均为固定5个local赋None和固定异常分支，已在原A16 128N+128 traversal/固定metadata块内，无新增树walk、hash、UTF8、序列化、trie/PV费用或新的retained scalar/object；所有先前收费均在receipt usage/peaks快照前，finally没有新debit。BR-01/02/03已关闭的前票来源在本SHA不变。

预算与持有独审目前无未关闭的本范围源码意见。原性能/RSS、指定双模型、CI、跨OS、正式producer/selected/长期保存授权边界保留；本静态结论不替代这些门。采集结束，可解除本候选冻结。
