# C1：内部空白创建事务与严格历史

本阶段在真实 JobStore3 已开连接上，增加 Store.commit 唯一委托的空白创建分支。它实现内部持久效果和历史验证；不是正式受信创建服务、只读 resolution 或真实位置许可接口。

批准依据为根8323B实施授权，SHA256 `93528eb38395856af86a76edf9c26822ef406f8a32315282086a509db235d8b5`；正式发送后全文核验，并全文读18372B根合同复核 `517b29bf74765bdca633b2bbc128cd036b7517aae8a7cb47edf900ae3e2e3bad`。固定39602B合同仍为379916/`ff725f2c…a5f3`，未修改其物理归因或预算条件。

## 固定输入和责任

树 `.worktrees/T01-project-create-core`，分支 `feature/weekly-t01-project-create-core`，批准base `5f910b52c69d86a1076b2032e5d3c63e715947f3`。按14299B清单 `c87fd0a1…9726` 逐50路径采用a816原Git/bytes/SHA，单独采纳提交 `ba2c6c293f9fd9e1742c9ab352dae5e3c951f6a4`，没有wholecommit、旧docs或他树环境。独立agent逐项核current=adoptionGit=a816Git，实际parent5f、delta50一致。

唯一五writer为新 `project/project_lifecycle.py`、既有 `storage.py/job_store.py/project/format3.py` 和新 `test_project_create_contract.py`。三旧产品在采纳后可修改，其余47项继续原字节只读，包括project_host、所有旧测试、main/canonical/coordinator/worker。最终相对5f产品/测试为完整52路径，不能把交付只算五项。AGENTS78df保护未stage，共同指令e437和无桌面规则继续。

## 私有调用不授权限

调用形状为：

```text
store.commit(None, None, operationId, None,
  creation={projectCreateCoreVersion:1,
            request:{requestVersion:1,operationId,
                     initialization:{kind:'blank'},name},
            origin:{hostClientId,engineSessionId,permission:'library.create'},
            readerLimits:实际ReadLimits实例}, hook=...)
```

这是C1专属的**未分配项目身份**的内部Store意图形状；与未来正式服务中的完整已分配intent区别命名。operation必须等于原request，project/base/job均必须None，不接受客户端projectId、plan或任意路径。所有旧edit参数含显式空列表均与creation互斥；没有creation时旧plan/hash字节和默认格式保持原样。

request、origin都是精确普通dict和有限精确字段；版本整数不接受bool，UUID为规范UUIDv4，初始化只接受blank。名称合法Unicode、非空白、无NUL，原序列保存，不trim/NFC/casefold；原name≤4096 UTF8B只是初筛，完整metadata等仍须通过下面实际政策。origin的两个ID和permission文字是可信调用者提供的持久业务材料，不认证来源、真人、物理文件或当前scope。此模块不导出能mint真实权限/dispatch/FS capability的工厂，不存在正式create_project_request/resolve_operation或公共注册。

只接受真实JobStore实例、target3、同事务actual user_version3及完整Job3结构校验；纯Store3即使已有app层也写前state拒绝，不隐式建public/claim/Job表。未知调用方事务写前拒绝，不把savepoint释放当已提交成功，也不回滚调用方事务。可信owner须在Store所属线程串行调用。

## 一次外层交易的持久效果

Store.commit先分派互斥新分支，内部实现复用同连接 `_transaction` 的一次BEGIN IMMEDIATE/COMMIT。已有数据库先受冻结reader的硬有限验证guard约束，再核format3与Job3完整真实结构/历史。

1. 先查全库原claim；相同创建request/origin按真实原context、receipt与完整历史返回原结果，不重新分配UUID，不要求项目仍空或仍叫原名称，也不把新的收紧创建reader政策当原请求身份。异request/origin/kind拒绝；全局commits/rounds/app_operations/app_receipts孤儿占用拒绝，不接管。
2. 原claim不存在后才由engine分配真实UUID；新内部/public同值。已有project/public/internal或候选snapshot/checkpoint身份占用拒绝，不用INSERT OR IGNORE吞冲突。
3. 首次INSERT前完成全部候选持久行及读取投影计费。预测hash只用于预算；此时没有持久checkpoint证明。
4. Store委托写projects revision0，走既有seed_project的新增strict分支：app metadata0/seq0、空domain snapshot、null-name genesis checkpoint、origin。strict分支用普通INSERT及读回，不改变旧seed/checkpoint默认行为。实际全量genesis经现history读回验证后，才以实际genesis重建最终context/plan。
5. 同交易写public映射、唯一application claim、创建专属原名称metadata1/seq1、after checkpoint、app_operations、唯一app_receipts和当前head。domainRevision仍0，无Job、领域marker、draft/学习/辅助事件，不把创建伪装成旧metadata claim。
6. 逐全部typed rows与预算候选核同、实际SQL行数/编码总额核同、完整format3/Job3/history再核；任何差异回滚。最后COMMIT后才把结果发布给调用方。after_commit等待/交付失败不删除已成功项目，后续内部精确重试只返回原receipt。

空白创建最终新增恰10条持久行：projects1、snapshots1、app_projects1、app_checkpoints2、app_origins1、public_projects1、operation_claims1、app_operations1、app_receipts1。中间head/metadata UPDATE不重复当末态持久行计费。没有第二库、第二writer、第二Job/receipt或可变意图账本。

业务context/plan/receipt/result精确沿ff725。context只有projectCreateContextVersion1命名空间；requestHash、contextHash、planHash、domain/checkpoint hash各自按原canonical域核验。libraryEvidenceRef仅从真实immutable app_format.migration_id产生逻辑引用，复制库可相同，不是物理ID或原dispatch证明。

## 严格namespace与旧兼容

Job3 application dispatcher先识别精确创建namespace并走唯一新validator，其余旧application仍用原严格validator；Job原完整context/hash不改。mixed `_history` 对创建只允许created origin→序号1的准确效果，before/after均是该次实际遍历已持有的checkpoint；新validator不回调history或Job-ready，避免递归。完整链遍历仍由既有history负责，后续旧metadata/domain/draft行为正常接续。

创建claim还必须与真实app_origins、序号1 application操作、创建receipt三项不可变行逐typed tuple核同，Job-ready再将完整history返回的实际receipt与创建receipt核同。独立审查复现过“旧项目合法domain receipt附伪创建claim”被误接受的反例；修复后用同类真实库核直接validator、Job-ready、重开均拒绝，拒绝前后dump不变。普通format3领域history验证不单独承担Job3全局claim证明。

混入两个tag、bool版本、未知字段、坏requestHash/contextHash/planHash/receipt、旧空项目补认或领域marker均拒绝。旧apply_application遇相同operation的创建claim先identity-conflict，不进入旧claim_context；反向创建遇旧application/Job同样拒绝。新表、kind、DDL、schema_hash、Job hash或默认format2均未改变。

旧格式3验证器对新namespace安全拒绝是明确兼容边界，不声称双向兼容。对照测试从固定a816 Git取旧storage/job_store/format3及其原静态资源到测试私有临时包；使用本树独立Python环境，没有借他树环境或修改实际资源。旧source对同一真实创建库拒绝，当前source重开后验证真实UUID/history。正式启用仍须同版reader/writer及真实能力版本绑定。

## 完整写前计费

只读消费同版冻结ReadLimits实例和原guard，不抄一套可放大的政策，也不改reader。核心实际计费如下：

- 同连接对候选每行每个typed scalar执行只读 `coalesce(length(CAST(? AS BLOB)),0)`，与原reader SQL口径一致，不把Python UTF8长度误充SQLite数据库编码口径。已有所有实际表的总rows/bytes再加精确10行；末态work为 `totalBytes × (1 + app_operations行数 + snapshots行数)`。schema/表/列界沿原reader，先界后物化。
- 校验完整request≤16384B、context+plan≤65536、receipt≤16384、result≤32768；新UUID必须能放入实际identity_bytes。现有每个目录内部ID、完整metadata与目录行同样核实际政策，避免仅新行能读而整库失败。
- 完整新目录按真实UUID排序；snapshot收费严格按冻结reader的 `sum(rowBytes)+2+count`，包括其相对实际JSON数组多1的保守字节。单目录保守留存 `768+count*(catalog_row_bytes+64)` 必须可行。暂存槽位、已用留存、TTL等运行占用仍保持原有限失败，不承诺永久可读。
- 遍历每个有效page_size=1..page_items及其真实offset分组，核完整页，包含36字节snapshotId、93字节非末页cursor、末页null、计数、标点与所有转义。不能只测最大page_items；size3可读而size2末页超额的真实编码反例已纳入测试。
- 初始workspace缺draft，对所有合法editor的最坏JSON编码预留：`'\x01' * identity_bytes` 每个1 UTF8B变6 ASCII转义字节。不能只用512个普通ASCII。完整metadata、workspace字段/refs都计入，bound/generation不凭空补值。

4096个ASCII名称完整metadata实际4178B，写前limit拒绝；4014个ASCII使metadata恰4096B可接受，引号等转义扩张仍按完整编码拒绝。预算不足整体失败、零INSERT，不截名/目录/页。首INSERT之后还以真实所有新增行和整库SQL总量核预测完全一致，核对失败全回滚。

## 当前验证与边界

真实临时SQLite专项覆盖原子10行/真实公开UUID、一个外层交易/无INSERT OR IGNORE、同名、原receipt重试与后续metadata/domain/重开、异请求/来源/kind/UUID/孤儿、损坏原件零修复、严格输入/实际header、纯Store3及缺Job3写前拒绝、19个边界异常与19个真实自有子进程退出/重开、9类实际SQL INSERT拒绝及预算±1/转义/页/editor反例。origin/intent fixture只证内部事务，不证真人或I06授权。

各轮独立命令、完整stdout/stderr/实际exit、首fail与最终代码身份见本阶段reviews目录。首轮两项测试失败为metadata反例阈值选得比合法metadata更大、旧reader临时对照包漏原invalidation资源；修的是新fixture并保首fail，没有把对照包导入失败冒充旧reader对新语义拒绝。旧专项/完整check及独审均按实际最终候选登记，不拿中间结果冒充final。

不运行本机GUI/Electron/e2e/native/HMR/Keychain/模型；不改协议、公开capability、main/preload/UI、默认startup格式。正式create_project_request、resolution、原dispatch物理绑定/当前scope、真实位置首IO、完整Host与I06供方全部后置。原FR-001–006/804、44/57P0、两个目标OS/真人、指定同版双外审、CI/正常develop合并及远端门保留，完整Goal继续。
