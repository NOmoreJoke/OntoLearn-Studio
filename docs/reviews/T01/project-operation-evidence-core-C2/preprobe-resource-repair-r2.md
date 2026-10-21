# C2 资源前门：2c425后的精确修订

固定产品 `ab792c494db09ada1f20d0a598c3e0c96c338992`；实现提交0223d70的parent为保留2c425及其两条实际阻断的过程aa199fb，随后ab792仅校正一条旧测试断言的目标表作用域。只改原两个writer；52项原423b、原额度、profile1/canonical/Store/Job/schema/锁保持。旧256/5b、2c425及其141专项/check、57对原流均保留原身份，不能覆盖本版。

## 三项实际更正

1. 在任何非内建表的行号枚举前先走有界完整table_xinfo，拒所有hidden/generated列，以及ASCII大小写不敏感的rowid、_rowid_、oid和内部_t01_rowkey。该前置本身只通过固定内建sqlite_master枚举，不递归进入未验表的行号路径。后续内部枚举、metadata和point集合统一用明确的_rowid_；合法负数、INT64两端保留，不套selector的safe-integer限制。
2. 最终_cost完整行读取把 `_rowid_=?` 保留在独立外层WHERE，highest-column typeof仅作CASE副条件。原2c425把等值条件藏在CASE，真实300行计划走Rewind/Next，以263503票先发生超过300KiB局部复制；本版单行计划必须实际SeekRowid，真实表不能Rewind/Next。计划测试已扩大到实际SELECT/WITH/PRAGMA全部路径，含最终完整行、metadata、原筛选/投影、JOIN、费用SQL及有限纯行号枚举，不能只挑native/point测试。
3. `_rowids`关闭自有cursor时捕获全部BaseException。已有first时保持同一原对象并置cleanup_failed；没有first时保关闭的原MemoryError/KeyboardInterrupt，以及_Cursor.close原SQLite有限映射。既有本次事务ROLLBACK、未知caller事务不动不变。

0223的首次正常check实际3128通过/1失败/44既有跳过，唯一旧empty-child断言错误地禁止已收费的sqlite_master metadata。ab792将断言限到目标job_blobs，保真实目标正文前拒绝；首失败完整日志及唯一流水均保留。

新增19个小型正常表/spy用例：保留名大小写8、独立单行Seek1、close首因/原异常9、signed-int64两端1。连原计划测试的20项目标实际通过；close9项再以真实_Cursor.close映射边界单独通过，没有在测试中复制异常映射。没有新增损坏文件或大输入反例，旧已存在报告/日志仍原件保存。

## 固定证据与审查

module60251B/SHA256 `e47f2689dcbf9519aeb3f64026094545e41f5401f309520bc805eb85f3fb56c8`；test70063B/SHA256 `8b03aeac29e0a6ca1f53c8b3a81aef31b6110d8f722a4b275e6a7a10ed77cd6f`。完整54在本版candidate-manifest；正常check/source实际终态、160专项原流水、实际全路径EXPLAIN及原始工具流在本版checks/evidence索引。各run均独立basetemp，不复用第一失败文件。

原focused01的11份中间失败流水已在此前轮转丢失，原日志/工具exit仍在；本版不重建、不把该遗漏说成完整。首低预算反例、focused04关键拒绝账、rowid遮蔽及独审300行反例均已原样封存，不受此遗漏影响。原C2旧430条归档与19044报告未改。

不同agent对本新fixed独立复核，结论由其唯一报告签出；作者只报告实际检查，不自签Pass或恢复供方。整个交付继续限同一已启动真实JobStore3的内部有限事实读取，不授生产权限、原物理dispatch/current scope、profile2/组合56或formal resolution。指定双外审、CI、目标OS/真人及父验收门保持；无外部服务、用户数据、GUI/native/模型/付费/打包/push/PR/merge动作。
