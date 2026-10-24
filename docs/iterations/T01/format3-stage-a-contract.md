# Store3 Stage A 实际内部合同

这是本地候选的Store-ready基础，不是公共协议、Job-ready、全局claim或已启用业务能力。施工来源为批准5f，加本T01可恢复提交；12个共享基础路径虽已移交，本阶段仅改storage/project及新增test_project_format3，不消费未批准业务源码。

## 入口及迁移

`Store(path, migration_hook=..., *, target_format=2, backup_path=None)` 默认和模块FORMAT_VERSION仍2；显式3取得与批准JobStore相同`.writer-lock` OS lifetime lease后重查源存在性。实际既有0/1/2源必须先一致SQLite backup到新目标，integrity校验、fsync文件/Unix目录，保存备份文件SHA256及逻辑dump摘要；进入同一迁移事务后再核源摘要，变化即拒绝。备份/错误副本不自动删除、不覆盖。空白3直接创建。0/1→2→3全部处于一个外层事务，失败完整旧库，after_commit实际3；旧/default2重开实际3拒绝。已打开的裸旧Store连接不能据此声称自动撤销，正式入口需同lease与连接排空/两层ready。

SQL唯一实现为 `project/format3.py:TABLES/TRIGGERS`，由实际同连接安装；不另存可漂移schema。app_format保存子schema1/hash、migration UUID、真实源格式/备份hash；app_projects当前头；app_origins不可变genesis来源；app_drafts保留header代次墓碑；app_learning当前attempt版本；app_assistance不可变事件；app_operations项目序列；app_checkpoints/receipts不可变证据。原域表/约束/不可变trigger全部只读核验；旧可选retirement表仅在显式迁移缺失时新建，格式3缺失则拒绝，绝不opening-time修坏库。原snapshots/commits/结果/run/round原行不改写。

旧已知commits只索引实际存在者，不填造缺失revision；genesis记录真实domainRevision、实际known sequence及legacyHistory complete/partial。新domain操作从genesis真实revision向前连续，其项目sequence从已知旧操作数量向前连续。源码`history_coverage()`是唯一私有形状；unknown历史不称从未发生。

## 实际JSON与证据

完整checkpoint envelope精确字段：checkpointVersion1、databaseFormatVersion3、applicationStateSchemaVersion1、project（内部身份）、domainSnapshotRef、domainRevision、operationSequence、coverage四项、historyCoverage、application。application实际包含metadataVersion、metadata（name/templateRef未知为null、archived、mode、origin）、drafts完整header/载荷、learningCurrent完整记录、assistanceAudit完整不可变记录。空是实际空集合，缺项/额外键/不合法类型不被coverage标签掩盖。canonical=`ensure_ascii=false,sort_keys=true,separators=(',',':'),allow_nan=false` UTF8，identity=SHA256 canonical字节。

新domain-only receipt完整字段为 receiptVersion1、project、operationId、operationKind=domain、operationSequence、planHash、domainBeforeRevision、domainAfterRevision、domainMarkerRef、applicationBeforeCAS/AfterCAS空列表、beforeCheckpointRef、afterCheckpointRef、committed=true。真实marker、索引、receipt、前后checkpoint/原域快照及当前头互相校验；单个checkpoint加载同样不能信任只含引用的假receipt。已迁移旧操作无完整应用receipt，`project_receipt`明确legacy-not-recorded，不倒填历史。

Stage A没有应用mutator，故所有checkpoint的应用状态必须是不可变genesis默认。任何实际CAS/学习/辅助操作上线前，必须由后续唯一adapter扩展真实应用变更/receipt/历史校验；不能直接SQL填表后冒称完成。domain提交仍只经原Store.commit；成功domain no-op推进revision/sequence而不虚增dependencyVector；精确重试返回原marker且不再分配receipt/序号。

## 只读与故障边界

`actual_format`读取真正user_version；`project_checkpoint(project, identity=None)`和`project_receipt(project,operation)`仅显式3可用，返回私有JSON不注册runtime。重开3只读验证，不做DDL/补表/新备份。完整Store验证另核integrity/FK、所有旧快照hash、合法结果kind、精确domain/app SQL和不可变trigger、严格记录类型、真实origin和sequence/receipt/checkpoint一致性；故障固定分类，不解析文本。公开错误码与有限启动exit/TS/Python matcher仍待同版公共合同，当前Format3Fault仅内部固定category，不当公共schema。

专用fixture自建临时SQLite，含批准原make_legacy的事实/revision但缺历史反例、人工编辑/墓碑/结果/run/round、备份后并发变化、锁前exists竞态、每实际DDL及提交边界的异常/取消/模拟磁盘/真实os._exit、坏结构/假checkpoint/假receipt与实际5f旧reader。跳过仅源格式不存在的阶段，不计通过。正式Job-ready/同一operation_claims job/application迁移、受信确认/全部CAS/完整恢复、统一公共JSON与真实打包/指定双审仍待下一阶段。
