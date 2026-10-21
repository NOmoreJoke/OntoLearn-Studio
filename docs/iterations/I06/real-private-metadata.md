# I06 B-M：真实私有 metadata 子集

2026-10-21。仅 main-private Node metadata 供方，无 app bootstrap/公开桥接。`mechanismOnly:true`、`productionAdmission:'unsupported'`、`nodeEvidence:'node-observed-unfenced'` 固定在结果中；没有真实 LocationLease、生产 snapshot 或内容 IO 接口。

## 固定范围

批准 base `5f910b52c69d86a1076b2032e5d3c63e715947f3`；新树 `.worktrees/I06-real-private-metadata`，分支 `feature/I06-real-private-metadata`。按7201B/SHA `feb2f93a2cbc6722b3f7ba61fb4671d34d6f44caeeda2548971bb3a04ecd1b72` 授权、1028B/SHA `c5353e75256cd8a57b02418e0aefbde8677becb125be9a0d240947477ec7ee61` 固定输入及根14477B/SHA `16febc6c5c5174d01ebf00c599ac86b91cb9058ae9687ca1feffee48458179be` 复核实施；原件在本review/inputs。

采用提交 `f63fe6fa0ba9eff944b11b9e4bbd7e6235e43dbc` 恰含两只读件：A inventory 23598B/SHA `0f6a2125d5dea53b5e5badde99401086284d4fd776b0cefadad324e408c786e5` 与专属测试22330B/SHA `7d82c1012bbe7fc35c5faf6eaf167b82d93a357e0b1060db6256ba809a118f49`。没有采用 cohort、e2c/961、旧平台脚本或其环境。新 writer 只有 `apps/desktop/src/main/security/private-resource-owner.ts`、`tests/unit/i06-private-resource-owner.test.ts`；本说明和独立review目录以外零额外路径。AGENTS15852B/78df2825…a759保持未暂存。

## 实际供方与状态

`createPrivateResourceOwner(inventory, binding, options?)` 只供可信 main 内部装配，严格 own-data/strict schema接收process/profile及固定名model-gateway-private-v1的绝对规范根。没有 IPC/renderer 路由；根描述本身不是人类选择、OS身份或生产授权。getter/额外字段/safe布尔/错误形态拒绝且零FS。真实 app profile/sessionData/数据库/worker/retirement来源未接入。

只登记 private-root、credentials、configurations、audit 四角色，不补 profile/database/tasks/retirement。模型根和直属未知项归private-root，三个bucket各自持有后代；真实未引用final、pending、孤儿都观察。名字准入按36位hex/hyphen加对应credential/configuration/audit后缀及.pending-PID-UUID；名字规则不是UUID或内容验证。未知名/额外目录保真实事实并unknown，不为通过而过滤或删除。

Node操作只有 lstat(bigint)、opendir、Dir.read、Dir.close；不打开或读取普通文件/配置/密文/audit/SQLite正文，不调用仓库/decrypt/safeStorage/网络。身份由实际dev/ino无损十六进制字符串及类型/links形成；不是hash、浮点或Windows替代值。目录nlink不作文件alias闭合；实际文件按distinct parent+精确name核links，相同inode final+pending两名而links=3仍unknown。没有全盘alias搜索。

观察先失效旧revision，完整枚举前记录实际根及已知父metadata；缺失根/父只能用实际最近存在祖先记录prospective。初始化失败不清reserve。全体列表先reserve完再取同一revision逐角色投影，避免各owner的reserve把前一票据变旧。映射每个resource的parent/identity/components都作独立值拷贝，符合A捕获树不接受共享对象引用的原约束。

`state:'observed'`仅表示本供方这轮有限观察及A子集投影成功，不表示全应用complete；`inventoryState`仍incomplete/unknown且不能签生产snapshot。失败、权限、缺根/父、超限、映射拒绝与关闭未知保独立reason，不用A缺角色的全局incomplete掩盖子集失败。`inventoryAccepted`仅说明A是否接收这批投影，不认证完整性或OS资源终态。

根/桶/leaf真实metadata先保留，再将不同UID或group/other可写标unknown；普通EACCES/EPERM另保permission失败。它不是原内容仓库0700/0600策略的代替实现或跨OS ACL证明。无法由字符串无损表示的名称保守拒绝，例如解码替换字符U+FFFD（即使字面有效亦保守拒绝）；不转义成另一components。

## 操作槽、取消与生命周期

每个固定私有Node调用先占slot/实际操作计数，再启动Promise。最多2个acquire slot；Dir从opendir开始持续持slot，读完一次/枚举完/业务结果结束都不释放，实际close成功才释放。view区分actualUnsettled、acquireSlots与heldDirectories，不能把其中一个为0解释为全部释放。close失败保unknown及原slot/对象，不用ERR_DIR_CLOSED回填此前失败。

`cancel()`同步失效观察并返回当前计账，实际Node Promise和目录资源仍在原实例，后续真实终态才清槽。`close()`停止新接纳、等当前观察和真实关闭，失败保unknown。等待中的Node调用可能无限pending；5000ms是返回/投影前检查的观察deadline，不是内核系统调用timeout或“5秒必返回”的承诺。没有包装reject清槽或自动OS取消声明。

`beginMutation/endMutation`只是未来可信writer的内部握手，本阶段不执行任何写动作、不提供callback。观察中尝试mutation会失效该轮但不给启动票据；已持票据时observe拒busy。逻辑cancel/close不清未结束mutation屏障；close报告mutation-unsettled，原精确token可收尾，不能恢复新接纳。真实生产writer尚未接入，token/end本身不认证OS写入或Job终态。

## 保留历史、预算与竞态限制

本进程已看到的身份不删。相同逻辑路径变新inode时旧身份retired、另记新身份；A原locationKey不容同址历史/current并存，故保持unknown、保全部旧新事实且`inventoryAccepted:false`。不能删旧项、只报当前、换owner或改A取绿。B-M只保当前进程历史，没有持久恢复，也不报mechanism-restored。

上界不放宽A：根32、记录32768（已知和unsupported历史合计）、组件128、UTF8路径16384B、观察5000ms；可选limits仅收紧entry/根内depth/pathBytes/时间。绝对路径组件仍固定最多128。额外将保留locator/metadata字符串保守计量到16MiB，序号65536耗尽封闭实例。增量枚举在存入前核预算；超额只返回unknown部分事实，绝不截断后宣称observed/complete。A的depth/node/string捕获界仍独立有效。

整轮复核扫描目录和祖先身份，私有子树目录还核变化metadata；祖先外其他目录新增文件不等于锚点换身份。最终投影后再次核整轮deadline/generation。**这些检查不是原生fence：**lstat(child)与按path opendir之间若被替换成symlink，Node仍可能跟随并枚举目标metadata，事后复核不能证明“从未跟随”，ABA也可能逃过双查。当前只对实际观察到的静态symlink拒绝follow；没有声称竞态下原子nofollow或允许在用户目录运行。本阶段实际执行只在独占受控临时fixture内，未知/竞态/unsupported保持保护；生产仍unsupported。若未来消费方需要绝对nofollow/首IO原子性，必须C原生root-relative句柄，不可用本供方或两次stats代替。

Windows缺完整FileId/reparse/ACL/native供方时固定unsupported-platform，不把POSIX字段伪装Windows能力；POSIX临时目录结果也不代表目标macOS15/Windows11验收。

## 验证与证据

真实fixture准备/清理与观察分开：只有测试驱动mkdtemp/realpath、写合成bytes、mkdir/link/symlink/rename/chmod/rm，观察供方不读正文。专项覆盖实际四角色/metadata bigint、合法pending/孤儿及同inode二/三名、symlink、未知子树、缺根/父、同址替换与移名、33代根、收紧entry/depth/UTF8、真实权限与宽写metadata、mutation屏障/克隆、同stack取消/close时Node Promise仍占槽、严格输入与零open/readFile call-through断言。

错误注入分列：after-root-reserve仅模拟初始化拒绝；close-receipt-once在实际Dir.close后模拟收据失败，保slot，不称OS真的close失败。Mac创建非法byte名的EILSEQ是fixture失败原件；Linux byte-name及Windows分支在当前Mac显式skip，不冒称已实测。

本树独立npm ci/uv sync --frozen，专项/采用A回归/完整正常check/verify:sources和独立审查的实际argv/cwd/环境/分离stdout/stderr/exit、首失败、每候选bytes/SHA见[本轮review](../../reviews/I06/real-private-metadata/)。原件保留首次类型错误、首专项失败和后续修订；中间版本通过不挪贴为最终候选。最终结果以固定manifest与独审原文为准。

B-R/B-L、T01宿主/Store/worker/canonical/dispatch、T03源broker/build、native/VFS/两OS与真实生产首IO/公开消费均未实施。无GUI/native/e2e/HMR/Keychain/模型/付费调用、push/PR/merge，原Goal未改；指定同候选双方新审、父功能/CI/正常合并/远端/真人门保持。
