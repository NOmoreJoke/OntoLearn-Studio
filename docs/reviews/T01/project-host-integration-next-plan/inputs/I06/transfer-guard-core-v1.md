# I06 metadata transfer guard core v1

2026-10-21。登记模式：仅纯metadata决策及有界临时token状态；不导出生产FS lease/action/wrapper，contentIo()恒为unsupported。metadata-eligible只表示来自本工厂所绑定owner port的观察在有限规则内未见冲突，不证明真实OS身份、inventory完整性、原子confinement或可读取。没有真实owner时evaluate固定unsupported；没有任何把eligible兑换为IO能力的入口。

## 身份、范围与来源

新树/分支：/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-transfer-guard-core / feature/I06-transfer-guard-core；批准base5f910b52c69d86a1076b2032e5d3c63e715947f3。唯一实现main/security/private-root-transfer-guard.ts，唯一测试tests/unit/i06-transfer-location-guard.test.ts；原I06/e2c产品不动、不复制未批代码。registration SHA4ea82f5408a3d4d15b06cb853905f96902182a275d5d4ec503567192f31ffac8、独立root设计审查SHAabeece37c930c5353b4ab78bf75de575a43e74a87c518f3dcb1a783b4607deeb已全文读回。AGENTS78df/commonff5实际政策适用，原Goal工具仍blocked，不重建或擅自完成。

工厂只接收main将来唯一metadata owner的结构化observe(request,signal) port或undefined，不接受isSafe/allow布尔回调、FS port、真实文件句柄、密钥、safeStorage、外部schema或unsafe测试选项。port是外部可信假设，不在本模块认证其OS来源；测试只注入合成metadata。工厂捕获该port实际对象/方法；只接收由它实际返回的观察，内部校验后复制成不可变视图，不接受caller提交snapshot/token自证。观察provenance限本进程port身份与本地序号，绝不称为真实inventory认证。未来真实owner/平台adapter须另登记和验证。

## 封闭输入

所有raw输入通过一次有界own-data-descriptor捕获，拒绝访问器/非plain对象/符号/循环及有界结构超限，复制到惰性无getter树，再对副本经现有zod strict校验；校验阶段不重读原对象/Proxy。不得保证恶意同进程Proxy trap自身不执行，但不主动读取访问器或把原对象交Zod。类型如下，所有字段必需；none必须恰为{kind:none}。本私有模型不形成公共wire。

- request context：profileEpoch、projectId、checkpointId、requestId为1–128位ASCII标识，generation为非负safe整数，purpose为export或import。openRequest每次创建新的实际对象，连同同值重开也先失效所有旧token/在途观察；绝不通过字段相等复活ABA。一次工厂只有一个当前request。
- descriptor：version=1，sourceRead={kind:files,refs:[...]}或none；inputPackage/final={kind:file,ref}或none；staging/unpack={kind:members,refs:[...]}或none；newProject={kind:writer-location,ref}或none；backup必须none。export必需final，sourceRead和staging可显式none，其余none；import必需inputPackage、newProject，unpack可显式none，其余none。全部refs唯一，数组不能为空代none，不能复用一个ref扮演不同角色。
- owner observation：version=1、profileEpoch、revision非负safe整数、completeness=complete/incomplete/unknown/recovering/failed、platform={kind:posix-sensitive,namespace,volume}、protectedRoots、protectedIdentities、locations。未知平台/大小写/命名空间/identity支持拒绝，未实现Windows或真实macOS适配。owner声明只提供metadata，不是allow决定。
- protectedRoots：每项role=private-root/database/database-wal/database-shm/task-root、absolute规范segments及现有identity或null（prospective）；前四角色各唯一且必需，task-root可省。整private-root含未来后代/prospective路径；其它解析后别名以额外task-root保护范围表达，不以只列三个bucket替代整根。
- identity：kind=posix-devino、volume为规范标识，device/inode为0或非零开头的1–20位十进制串，lifecycle为owner生命周期标识，state=active/retired/unknown、objectType=file/directory/unknown。snapshot中的平台volume及各identity volume必须一致。candidate不能unknown/retired；protected active/retired均保护，未知退役闭合性拒绝。比较别名按volume/device/inode，不因lifecycle不同放行可能复用/退役对象；lifecycle只绑定观察，不谎称Node提供可靠inode generation。
- locations：唯一ref，anchor={segments,identity}必须为可信存在目录的owner观察；suffix为1–16个严格单路径段；identity为现有文件identity或null（prospective）。sourceRead/inputPackage必须存在，final/newProject必须prospective，staging/unpack固定成员允许现有或prospective；所有anchor现有且identity active/directory，现有candidate为active/file；private-root/task-root的现有identity须为directory，DB三者须为file。root自身identity也加入保护别名集合，不依赖另一个数组重复登记。绝无递归scope字段。位置来自owner对ref的观察，descriptor不传物理路径。候选路径=anchor绝对segments+suffix；只是持有home等anchor不等于递归读取它。

路径段长1–128，拒点/双点、slash/backslash、冒号、控制字符、NUL、非ASCII及空段；绝对segments由数组表示，anchor+suffix总计最多32段，空数组仅表示根anchor，候选不得根。保守子集避免未经证明的Unicode/OS alias语义。双向段前缀检查候选实际对象/成员与每个protected root；相等、候选包含root、候选在root下均拒绝。祖先anchor本身含private-root时不误拒不相交单文件，但anchor或candidate的物理identity若别名到任一protected active/retired对象仍拒绝。同次descriptor的实际成员相等/包含或现有成员为相同物理identity也拒绝，location集合必须恰好覆盖refs。

## 固定资源与时间

值仅为私有核心资源限额，不是产品容量/Q阈值：roots≤8、protected identities≤256、locations/descriptor refs总计≤64、每字段≤128字符、路径深度≤32、suffix≤16；preflight深度≤12/总节点≤8192/单对象键≤24/单数组≤512，超限在完整zod遍历前停止。最多16个活metadata token，最多2个实际未settled owner观察；abort/timeout不提前腾观察槽。没有持久inventory/registry或全盘扫描。

observe返回及惰性捕获/验证完成时均按实际单调截止核5000ms，不只依赖timer回调；同步阻塞port不能被本进程强行抢占，超过截止的结果必须拒绝，不宣称5秒CPU隔离。token从evaluate开始计30000ms硬有效期，包含观察等待。只用单调performance.now及本地timer；非法/回退clock使工厂失效，token检查不延寿。异步超时返回固定失败并abort；真正port promise未settled继续占2槽，迟到成功不安装token。上下文变更/close/invalidate主动结束等待，但不伪称owner实际结束。已过期/失效token从活集合释放名额，终态立即清除descriptor/保护及位置大视图，WeakMap只为还被调用者持有的对象保存最小终态，未由强map无限保留旧token。

## 状态、fence及API

- createPrivateRootTransferGuard(owner?)返回openRequest、evaluate、check、revalidate、release、invalidate、close、contentIo。只这些私有API，不接受消费者action或FS callback。
- RequestToken和MetadataToken均为工厂分配的冻结实际对象，以私有WeakMap验证；同形clone、JSON重建、外厂token或错误request/purpose均拒绝。结果只含固定status/reason/token，不返descriptor、路径、inventory或原异常。
- openRequest(rawContext)→request-opened/request token或rejected；evaluate(request,rawDescriptor)→metadata-eligible/metadata token/contentIo=unsupported或rejected。开始前预留token名额，验证descriptor和当前context，再调用owner观察；await后、捕获/校验后更新保护revision前、最终安装token前重新核request/本地失效、实际超时/取消和预算，晚到结果不能覆盖新request。
- 观察profileEpoch须等于当前context。相同epoch的revision只能单调增加；降低拒绝stale。全局保护视图指纹包含platform/completeness/protectedRoots/protectedIdentities，排除按request refs返回的locations；same revision但保护视图改变视为conflict、失效旧token并将本工厂封闭失败（须新工厂/外部owner修复）。token另绑定自己的完整locations视图，revalidate位置变化仅使该token stale，不把正常候选文件变动当inventory协议损坏。更高revision先失效所有旧metadata token，再允许新evaluate安装新token；外部owner真实变更发布前失效协议未实现。
- check(request,token)仅同步检查本地对象归属/当前context/状态/deadline/已知owner revision，是as-of本地状态，不向owner询问、不认证外部仍新鲜。revalidate(request,token)重新观察并严格比较原revision/保护视图和该token位置视图，await后重复归属检查；新revision/内容变化失效，重新evaluate才能取得新候选；不自动更新token/延寿。无external atomic fence，不能用成功revalidate后await arbitraryFs宣称安全。
- release(request,token)原子进入released，仅首次成功；invalidate()先同步失效当前request及其token并abort在途，再允许外部发布变化；openRequest/close亦先失效。已released/expired/invalidated不恢复，即使generation/profile/原字段后来相同。close终态，之后不接纳。
- 本地检查/撤销在线程同步切点排序；撤销先执行则之后check拒绝，check先执行只给瞬时metadata结果，不承诺后续IO许可。跨await必须revalidate，仍无实际FS fence。
- contentIo()恒rejected/unsupported，不解析消费者或执行任何IO。不给可执行生产lease、bind、read/write/publish/cleanup、文件句柄或unsafe工厂。未知真实owner/FS时生产消费者调用数为零；单测不能把合成port的eligible当X1–X6。

内部失败仅invalid/unsupported/incomplete/stale/conflict/budget/cancelled/expired/released/closed，返回固定安全值，不抛owner原异常、不借公共GATEWAY码。内部异常用私有WeakMap记录固定reason；对未知throw值不执行instanceof/读取属性或prototype。snapshot/descriptor getter或port异常被安全拒绝，无路径/私有id/内容进入结果或日志。本模块不创建日志/文件/server，不调用Store或模型，失败局限该核心/request。

## 必要验证

严格角色/none/额外键、超限预检；整根双向包含/同路径/prospective/anchor不误扩大；active/retired alias与unknown/不支持平台；各scope字段/同值重开/ABA/外厂/clone/释放/关闭；revision升降/同revision内容变/不可变复制；跨await撤销/超时/真实未settled两槽/预留token上限；clock回退、异常不泄露；没有FS方法且contentIo始终unsupported、消费者零调用。全check及source归档核对静默执行，保留首失败和最终通过原件。本阶段没有App/bridge接线，不启动本机e2e/native或产品窗；实际FS/owner/平台、T10/T01接线、指定双审/CI/父门另保留。
