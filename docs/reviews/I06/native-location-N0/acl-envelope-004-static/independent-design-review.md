# 004 envelope静态后继：独立窄审

结论：**本轮静态准备可收件，无新增实质P1/P2；不批准成功修复、源码实施、API探针、第七构建或新CLI。** 现有证据不能补齐同一完整性/absence缺口，组件继续fail closed。fgetattrlist只是待root另审的条件设计选项，当前不能签其宿主支持、合法无ACL对象可接纳或完整正反验收通过。

## 固定范围与实际核对

基准0c20804537cca79578e0344870b4a3f24eb76998。本轮全文读最新AGENTS/common、I06-execution004-failure-root-closure.md及I06-acl-envelope-004-static-preparation-window.md；未改变原授权边界。主候选proposal.md实算15069B/SHA256 ef54cf8ad19a77c4273201c4ad52889ab2413d25fe6d8d2977b669fb15519a21；handoff.md2599B/257264ee214de57a74fa4b141a892c83f64a7e4a012d6622c179c71ac54368d6；controller-criteria.md1005B/a37bb9512e3339920d7d7793858d4766f0dc353892cb0d180f9d5030ff39a983。

已读evidence-and-preservation.json（11114B/c5bafccb5e28367305c9f842501f9851b671b58b2eb749868498befe7554226f）、upstream-fetch-record.json（3993B/784e552e1927a299a686b2655780ba3c26fd50533ab9f9b3dd8d5abe43e2ce54）及六份新来源摘录：XNU手册/缓冲合同/security packing和SDK attr/kauth/unistd。必要旧Libc仅点读固定Git的statx 142–219和filesec所列valid/get/set/query片段，没有重开旧源码审查、控制算法或供应史。

本审实际以Git/stdlib/hash核根两新规则、九源current与固定Git逐字相等及既定SHA，静态算诊断67B/合108B，并核实际SDK三份whole bytes/SHA与声明、摘录每一源行段相符。XNU上游完整响应体的SHA/下载量是主线fetch记录，当前只独立读保存摘录；没有重复下载完整上游，不能从摘录重算whole-source SHA或证明installed身份。

所有shell显式cwd为本I06树；未import产品、编译、测试/npm、运行native/API/ACL/FS/DB/进程探针、扫描fixture、清理/kill、GUI、外部审查任务或Goal操作。唯一写入是本报告及自身格式化，不改产品、方案、摘录或旧失败原件。

## 两布尔诊断：不解锁，也不默认重建

方案按总控补充标准明确区分诊断收益与修复证据：0/0、单缺位都仍缺独立完整性/absence合同；自然1/1也只能令另一运行的旧合取继续，不倒填004、不保证后续正反例。production门与fixture门是不同决策点，不能因fixture先失败就删门求绿。该论证与固定Libc有效位实现相符：UUID值即使全零，setter仍可置presence；query成功也不表示presence为1，非零位值4/8同样有效。

可选诊断仅在原read_acl_fixture失败断言前，以既有值作非零布尔归一，固定stage/两布尔、至多一次条件fprintf、不新增/重排查询或owner调用；不打印UUID/UID/FD/路径/成功遗留errno。格式的两实参仅0/1，实算新行67B含LF，和旧异常行41B合108B；单行低于96B，原流预算未增。保存/恢复errno、stdio成本未知非零、不重试输出、原require/cleanup不变均写清。此只是独立审计时可能另授的诊断，不是本轮推荐后继，不应启动默认“布尔→第七构建”链。

## fgetattrlist：独立响应见证的条件与拒绝路径

新官方固定XNU ref为f6217f891ac0bb64f3d375211650a4c1ff8ca1ea。所存getattrlist手册明确FD对象、RETURNED_ATTRS实际mask、REPORT_FULLSIZE所需总长、PACK_INVAL无效默认值、4字节packing及attrreference相对自身的有符号offset。手册同时警告普通返回可静默截断，引用可越出实际buffer。方案未把返回0、合理总长或零初始化当完整。

关键packing2051–2074仅在va_acl支持且非NULL时置security actual位；否则可省略或打包零长度占位。2792–2813对明确NOACL按空header计算大小。因而**security位缺失不能区分无ACL和未返回属性**；PACK_INVAL/卷级支持不能补这个缺口。方案正确保持UNSUPPORTED，不将placeholder当absence，也不增加卷/路径探针。有效且完整明确NOACL与count0仅分别是absence/present-empty候选，并未承诺目标对象或文件系统实际返回它们。

条件边界包括一次额外同held FD调用、固定4096B应用buffer、不扩容重试；最小前缀、所需mask、总长、固定字段顺序、memcpy解析，以及signed offset、溢出、变量区范围、attr_length、magic/header校验。缺位/截断/零长/矛盾均非成功。ACCESSMASK来源只保证权限位，目录LINKCOUNT不等stat nlink；方案保留原stat安全门并明确目录不能直接替换。若后续获实施窗口，精确required mask/packing布局、权限比较mask与payload长度/count算术仍须在新候选具体冻结，本轮没有给未写解析器签安全通过。

原同FD fresh fstatx、OWNER/GROUP/MODE getter与原stat一致、安全条件、原query错误、ACL副本ownership/valid/empty规则保留。新完整header即使满足，和原ACL表征矛盾仍拒；正count任意ACE拒绝，不用raw count代替owned ACL校验。ENOMEM/BUDGET、EACCES或EPERM/DENIED、其余不支持/畸形UNSUPPORTED、释放或未知ownership RETAINED优先是待批准错误表，不伪称当前行为。free一次、filesec_free void无结果、内部成本未知均未被候选4096B掩盖。

## 未决项、反例及所有权

同FD约束对象，不提供跨fstatx/fgetattrlist的原子metadata/ACL时点；相等identity/owner/mode也不是lease或ABA证明。方案对此明确设未决条件：若原验收要求单一原子快照，候选不足，不能声称保留全部语义。SDK attr.h处于UNSTABLE块，kauth原始布局和所读公开kernel都不是跨版本/installed合同；符号/目标SDK/ABI及新增头的构建闭包仍由T03另审。

仅允许将条件选项交root决定是否继续，不为其预选新构建或运行。未来最小writer明确仍是Mac metadata/私有有限解析及Darwin配套fixture两路径，不扩ABI/core/Windows/Node/TS/控制算法或锁；新增接口并非本次诊断许可。若没有适用于本对象的独立absence合同及可接受快照语义，就保持拒绝，不能缩减目标或把“安全拒绝”当完整可用性验收。

必要反例已覆盖该层关键歧义：返回0缺位、PACK_INVAL零占位、超buffer总长、负offset/越界/溢出、短或非法header、NOACL与empty混同、任意ACE、标量/identity矛盾、目录link差异、非原子跨响应、分配/释放失败及未知ownership。本轮只是静态反例要求，没有实际注入或证明全部异常可测；内部heap/系统调用/wall硬界、目标正反可用性及完整父N0仍未关闭。

## 检查原始差异与最终边界

本审工具f70681的首个自制SDK摘录包装重构断言exit1；前序规则/九源/诊断字面量断言已执行，失败不改候选。随后bc25a1按实际三SDK whole bytes/SHA及摘录逐个源行段核对exit0。本报告只认精确行段内容相符，不将自制SOURCE/空行包装的整段重构声称通过；这不是产品/API失败或运行验证。

主线告知原字节security摘录EOF空行导致默认whitespace检查非0，准备保留原件、单文件单命令blank-at-eof例外。该来源格式不要求重选范围或改写原文；默认失败与例外结果应分别归档。本审未代跑或提前签其未完成archive-checks结果。

本方案和handoff准确维持003/004失败、drain/fixture未知、目标双OS/EXCL/父N0、指定同版双审/CI/真人/远端及T01 wholeH/SQLite保护HOLD和已拒线。无需本轮局部修订；通过仅限此冻结静态准备收件，不替根决策或指定模型外审。报告冻结交出后停止改写，后继仍待精确授权。
