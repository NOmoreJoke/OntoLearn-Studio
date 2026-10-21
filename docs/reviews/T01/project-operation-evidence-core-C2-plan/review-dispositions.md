# C2 方案意见处置与证据边界

最终主方案42685B，SHA256 `e7db89cb52cc75707d0e7a00e637e97701bea7e7d49f623ef464cb1baf44b96b`。这是文档方案，不是已实施/运行的C2核心；所有专项仍待根另批。

| 意见                                                  | 具体处置                                                                                                                           | 最终结论依据                                                         |
| ----------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| P2-C2-01 旧history wrapper吞SQLite busy/I/O及控制异常 | §4门在execute/fetch/iteration先转独立EvidenceControl(Exception)，不属旧捕获族；资源/未知模板也穿透，finally保首因                  | 独审原报告保留静态反例及修订全文复核；不是DB运行发现                 |
| P2-C2-02 rounds无run/零轮合法阶段                     | §8细分runNULL+progressNone非成功、run存在零轮及成功全链；§6追加rounds.job反查再run正查，拒有结构孤儿/跨run，不扫描无结构JSON猜归属 | 最终补审f52949/b4d2f2，原14393B独审前缀未改，只追加1517B             |
| P3-C2-03 结果全行关系                                 | §8冻结dependencies/manifests/projection/kind/原cache_key公式及存在payload的同版row、rowId/ordinal唯一                              | 按实际Store.publish/_publish_job静态源码；cache NULL不否定原受理     |
| 预算1 昂贵费用SQL前未冻结工作检查次序                 | §5明确metadata-only→工作预扣→精确费用SQL→证据预扣→正文；UTF8/UTF16系数、NULL/int/固定开销具体                                      | 独立静态20MiB×33扫描反例；无SQL运行                                  |
| 预算2 seen去重不限制重复查询工作                      | MAX_QUERY_COUNT65536、MAX_READ_WORK536870912与证据seen分账，重复SQL/投影照扣，metadata返回前预留固定上界                           | mapping_status→vector及重复snapshot真实调用图支持，未声称CPU/RSS改善 |
| 预算3 iterencode单个大scalar会先分配巨chunk           | §3/5 scalar先字符计canonical长度，再真正分块escape；keys亦同，不先deepcopy/encode                                                  | 独立stdlib20万个U+0001首chunk1200002B，不是产品或DB测试              |
| 预算4 最后ROLLBACK可能被耗尽guard阻止                 | 总65536内留BEGIN/ROLLBACK各1控制槽，业务最多65534；finally独立释放，不受业务/证据/work耗尽挡；cleanup真失败保首因                  | §10明确未来±1及恰耗尽后in_transaction=False，未倒称实际已运行        |

两独审最终均无未解决本审设计问题。事务独审15910B/SHA `3af0cf66dafce54cfcc2fa9174ec428385e26667d0c2552b3938fcc31f99a605`；预算独审35416B/SHA `7e672b9134e77ef9df73fc9706486e94976d7bc8d27f39dde14853282df017a1`。历史dcebb/ff93/1724结论各保其时态，不当最终e7db实施Pass。

主线新方案按真实冻结源调查和独立反例修订；一次apply_patch因格式行匹配失败原子拒写，后用唯一目标文本精确替换，原工具保留。没有运行产品、DB、C2专项、新子进程、网络、模型、GUI/native，也没有改C1原59、a33根收口或52基础产品。只做文档格式、AST、Git与hash检查，不重跑无变化C1。

rootclosure的2650B原字节已单独存C1新过程证据并提交a33cc80，不能把该过程文件或C2方案计入423b原59。并行dispatch方案由另授权、另作者/独审、另路径进行；本C2提交只含本C2新docs，不采用并行提案为实际代码接口。

根需另决定52只读采用、两新writer、EvidenceView及全部gate/预算/输出/清理规则的实施授权。正式物理绑定/current_scope、真实frame/page/envelope及公开Host/首IO/双外审/CI/合并/父FR仍未关闭；原完整Goal继续。
