# I06 A：保护清单与整组生命周期纯机制

2026-10-21。批准base：5f910b52c69d86a1076b2032e5d3c63e715947f3；独立树I06-project-inventory-lifecycle，分支feature/I06-project-inventory-lifecycle。只新增两模块及两专属测试，不复制e2c/961/其他未批准实现或环境。实际授权7045B/SHA20c9c0c6006746a54e286d391e49fac728810889a8165e13838d82667779708f、根独审12219B/SHA556c6b838cf8e0c6a209a5a3633286128a1687bb208d25ce91191e56bd56647e已全文读，原件在本轮review/inputs。

## 可交付的边界

全部结果固定 `mechanismOnly:true`、`productionAdmission:'unsupported'`。opaque owner/observation/snapshot/cohort/engine票据只在本厂实际对象内有效；clone、同形JSON、旧epoch和另一工厂对象不授权。代码没有FS、SQLite、网络、safeStorage、真实句柄或通用IO callback，不提供生产首内容IO能力。模型与项目内容不进入该状态模块。

完整性仅表示被该核心接收的有限合成metadata及owner状态一致；不是实际OS身份、完整应用inventory、持久retired恢复或T01真实release。缺少B供方/持久来源/原生lease时实际生产仍incomplete/unsupported。A不改变961的contentIo、数据库保护、现有Store或公共DTO；不关闭B/C/D/E、目标OS、父I06/FR-002和发布门。

## Inventory

`createPrivateResourceInventory` 固定八类owner：profile、private-root、credentials、configurations、audit、database、tasks、retirement。期望集合运行时冻结；缺任何owner、未恢复retired、失败或混revision不能complete。只有本厂实际owner对象可登记观察；所有观察绑定同process/profileEpoch/revision，metadata从own data descriptor有界复制，拒getter、循环、额外字段、结构/字节超限。Proxy trap本身可执行，但重入不能修改本核心；不宣称CPU隔离。

主要顺序是registerOwner→reserve/beginMutation→beginObservation/observe→issueSnapshot/checkSnapshot。mutation同步失效旧观察和快照；失败不删已有保护。profile同值重开也增加内部epoch、失效旧owner/观察/票据并保留retired记录。snapshot及其所有集合深冻结，外部修改原数组不影响核心。

资源分private-deny/profile-container/database-managed，保留parent身份、精确components、identity、present/absent及active/retired/released-retained状态。prospective用absent+null identity；实际materialize可登记原位置的新identity，已有非空identity不得偷换。清理后旧pending可以absent-retired保留路径和历史身份，不当作当前目录项去重复计linkCount；仍不删除保护。现存私有文件的distinct目录项数须与linkCount闭合，nlink=3只见两名是unknown；DB多链接亦unknown。这只是输入一致性，不是真实alias认证。

`trackDatabaseRelease`仅接受受限的真正native Promise，不接受thenable、自报0或任意callback；该原Promise在本厂终生单次归属，不能并发、已settled或跨profile复用为另一资源的释放凭据；等实际成功后将原稳定内部记录转released-retained，失败进入unknown且保留记录。观察更新不替换内部record对象/出生owner，避免迟到release写丢或清新组。关闭/profile变化不提前腾实际Promise槽；0个持有不删持久路径。released-retained也不授再次打开权，未来还要新可信intent、真实T01释放与原生重新仲裁；profile精确DB例外未在A实现。

限额：root32、资源32768、每路径components128/UTF-8 16384B；捕获深度12/节点700000/累计字符串16MiB另作拒绝上限。观察票据最多2/5000ms、活快照最多16/30000ms、实际release Promise最多2。无真实native acquire，逻辑观察票据不冒充实际FS槽；实际Promise不因等待超时释放。clock必须有限、单调且可精确容纳30秒截止，原生performance.now为默认，内部测试clock与只收紧的revision/sequence上界不提供IO权。序号耗尽永久fail closed，旧票据不复活。

## Cohort

`createProjectCohortLifecycle`用固定holder角色显式表示main/task/engine/Store/worker及I06所有直接、间接持有链；health-probe只有显式登记才纳入。engine身份是本厂机制对象，不认证实际Supervisor或child。准备候选必须给新engine对象；同UUID主动重开仍新epoch。普通view refresh/同engine瞬断仅返回原机制身份，不误触全组重建。

prepareTransition停止旧组新接纳；候选私建、registerOwner、track真正Promise的initialize/binding/Store-ready/Job-ready/scope-ready及模型状态，再同步publish。旧组全部实际机制release且未settled清零、候选必要角色/绑定完成才可一次发布；缺项/失败/过期均不部分发布。enabled要求完整模型持有链；disabled仍需安全模型binding，已登记的间接旧资源须释放，不能用缺owner假作模型不可用。本层结果永远unsupported，不能据此安装生产候选。

`track`以native Promise品牌、精确prototype/无own keys和本厂一次性归属跟踪实际终态；逻辑cancel只标取消，不腾槽。这里的child/store-connection严格指整个cohort对engine/Store的永久拥有关系寿命，须未来B/T01用永久stopAndDrain聚合全部实际子进程/连接终态；不是可重启transport session或普通RPC的Promise。该聚合寿命在新组ready时仍可pending；candidate/active期间它若终态（无论成功失败），该组立即quiesce、候选发布失效且不再新接纳；已draining时正常结束则继续实际release。普通同Supervisor短session瞬断只走noteViewRecovery和原T01恢复政策，不因本机制清grant或全组重建，A不认证session-ready；供方不得把短session Promise冒充上述永久寿命。release失败保持unknown/未释放，旧完成不能给新cohort补ready。

全厂picker1、acquire2、操作256、每owner32、保留cohort32；transition1、active/candidate各1。候选30秒，排空等待5秒，同一cohort同时仅一个等待；等待返回unsettled不清实际槽。生命周期票据累计65536为额外保守内存/序号防护界，耗尽封闭实例，不是Q5或性能承诺。capture后、publish指针交换前再查时钟/当前性，超时捕获不关闭旧active或安装半候选。默认单调clock，回退/极大不可精确加TTL值终止接纳；JS timer不承诺底层操作已取消。

## 审查与验证

本轮独立实现审查原文、首失败、逐项处置及最终实际结果见[review目录](../../reviews/I06/project-inventory-lifecycle-A/)。独立审查不替指定GLM-5.3最高/M3.1-Flash xhigh同候选外审。

本轮只运行本树独立npm ci/uv sync、四新路径专项、正常check和sources；不运行Electron/e2e/HMR/native、Keychain、模型或付费，不push/PR/merge，不改原Goal。最终代码/测试hash和实际命令以冻结manifest与原始记录为准；不把合成机制测试提升为真实FS/owner/Store/VFS/平台或生产证据。
