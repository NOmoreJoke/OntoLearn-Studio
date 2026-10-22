# 累计计量静态证明 — 候选，仅准备

基线4690d9aed65f62aa635fc79e59b6eb53d2620d4b。未调用、导入或模拟 runner；无 compiler、检查器、native/API、GUI、DB、网络或产品修改。当前 NOT_CALL_READY。

## 单位与预扣

metadata 单位是容器、字段或数组成员的逻辑记录访问；重复解析、候选验证、映射、构造、输出均再计。字符串字符、regex字节扫描、哈希、Make字符转义、路径字符规范化、pipe字节、OS系统调用不是“一字节一记录”。它们分别受输入/输出/捕获字节上限约束。CPython启动导入内部与OS/loader真实I/O仍不可观察，本计划计入显式module discovery，不冒称内核/库加载硬上界。

PhaseMeter在main任何输入之前保留emergency3000，进入preflight预扣20000；第一次control预扣12000，dependency预扣61000。主账最终保留96000，阶段失败和未使用部分不退款。重复enter同阶段不再加票，每次work只增加该阶段累计upper。snapshot只读取固定scalar，不扫描账本；phaseReserved与四phase预扣对账，upperWorkDebits与四upper对账，actualLogicalVisits为null而非把上界说成实测。运行meter只是限流；下列静态充分性另行成立才可供root接受。

输入JSON先预扣3×unit_cap+8，再做字符结构计数，再调用无hook的json.loads。U=容器+对象字段+数组成员。三倍包括解析节点、物化和后续直接结构取值；后续跨行验证/再次输出另收费。深度≤12。固定输入pins实测文本U1069≤1100，descriptor U1179≤1200（仅文本profile，不读其指向工具）；plan≤768、meter-plan≤256、history≤128、authority≤96。畸形/超cap在native decoder前停止。重复输入解析重新收费。

输出使用自己的builtin dict/list有界编码器，预扣3×整个record cap，含构造、字段/成员遍历和序列化。进入容器前先检查本地U余额，不在序列化中走未收费json.dumps容器遍历。json.dumps只接收有界标量；无sort_keys、default/hook或用户对象。record中的meter snapshot包含本次输出费用，固定snapshot构造也包含在fee。字符串≤4096、整数宽度/float有限、深度≤12、record≤2MiB。需要更大上下文时显式INCOMPLETE，不扩票或截断冒称完整。

## preflight ≤19372 /20000

- 固定authority/plan/scalar取值、源/路径/SDK/目录创建与控制准备：2000，进入阶段先扣。
- 六JSON输入cap总3548：3×3548+6×8=10692。
- descriptor两组总≤117，先扣8×117=936后构造path→五scalar元组；不复制整行、不重复sum/set遍历。
- pins恰117，先扣32×117=3744；七字段取值、五scalar比较、realpath/stat五项、输出六字段构造、重复/别名/集合校验与物理sum都在该单遍内。未再访问unique.values求和。
- 显式module候选≤512，先扣3×512=1536，再直接迭代sys.modules.values；无tuple预复制。
- execution-attempt输出96×3=288；九个bounded_read各16=144（包含绑定proof文本）；attempt与source各写16=32。

## dependency ≤60075 /61000

进入阶段先预扣61000；固定工作128。三次输入读48。Make token每次append前扣1，最多3072（超限在第3073次append前停）；规范化/去重先扣3×3072=9216。路径保留插入顺序，不排序，排序费用为确实删除该操作而非库排序免费。

旧witness未来再读3156859B并核固定SHA，不复用本次内存。先扣24×880+64=21184，只在covered数组的固定缩进范围逐行取normalizedPath标量，三个外层字段名检查/比较、单标量JSON解码、map去重/插入/ordinal合计保守24/行；references与approvedWitness深层内容仅当opaque bytes，不json.loads、复制或输出深层图。行号与全文件SHA一起绑定来源，不等于现在header/open身份。

source-evidence固定3621B核SHA后按128U解码392；≤7 SDK候选先扣35；≤1024唯一path绑定先扣10×1024=10240。未知第65条在append前停止。输出entries每条最多对象4U+array成员1U，1024×5+pending65+固定root/snapshot≤5248U；输出fee15744，写16。总128+48+3072+9216+21184+392+35+10240+15744+16=60075，距61000余925。无locator、index、SDK/header读取或immutable-membership签收。

## control ≤11658 /12000

build-intent1050U×3+write16=3166；117个before行及snapshot均在1050内。六命令各固定构造/描述符/清理48，加planned96U、terminal96U及两次compact-dispatch32U，四次写各16：880×6=5280。dispatch文件只放index/phase/attempted/pid，避免重复整record。两次artifact读/32U输出/写共256；post元数据先扣12×117=1404；build-terminal128U输出/写400；余量固定128。合计10634；select预扣128×8=1024，合计11658。最终terminal的pending≤64已计入128U。SDK post检查、flags/env等固定取值在prepaid固定/命令费内。

capture循环中poll/read/write/字符流操作字节和固定scalar；select的记录另计：只注册两fd，stdlib selector每个ready fd单次最多返回一条key/event，故一次最多2。全六调用共享128次select上限，每次在调用和native集合创建前扣8（每个事件4），空唤醒也不退；最多256event，共1024。调用次数在snapshot外保留selectCallsCombinedAfter；到限是UNKNOWN/incomplete停止，不重试，不承诺可持续600秒。两个EOF record更新在每命令固定48内。总生产端raw流16711680B，一次emergency65536B，合计16MiB；所有六调用共享，封顶后无lookahead/drain/discard。取消flag固定scalar；当前leader至多terminate/kill两event且另扣emergency64，未知descendant始终保留。

## emergency ≤3000

首次捕获异常先进入已保留emergency，再error_info32（最多12次=384，包含读/写/fsync/close的首错与收尾、两层包装）；当前leader控制最多64。最多failed-command terminal、build-failure和一次stderr，各192U×3=1728，两次文件写32，合计2208；保守留792。正常成功终止后无继续分派；错误序列无无限重试。嵌套细节超192U或meter错误只能输出literal EMERGENCY_CONTEXT_INCOMPLETE，不称完整；第一次os.write短写/失败不重试。突然死亡/存储不可用可能仅有先前intent。

## 字节、历史与门禁

未来只提新128MiB：owner64（helper输入8、record/source输出8、artifact8、capture16共40；外部closure24），author32、root32。helper所有输入在open/fstat之后、读取内容之前按size预留；文件失败不退款，source与JSON输出按实际构造长度在写前预留。当前输入总保守小于8MiB（含2MiB depfile、3MiB witness），输出和两次4MiB artifact另分。字节上限是应用请求/记录范围，不是实际OS/compiler/loader I/O实测。

未来完整联合票目前不能确认可行。owner runtime改为96000（20000+61000+12000+3000）；当前声明余104737，仅余8737给两个外部复核及当前准备未知缺口。旧103000方案撤回，不能削减peer票硬塞余量。另列更保守的peer各40000**额度提案**，合计176000，单纯算术超过当前声明余量71263，若全加将2321263>2250000。peer额度不是已实现/已接受的充分性证明，完整外部方法仍待root决定；71263是该额度提案差额，不冒称不可再优化的最小必需缺口。当前作者准备UNKNOWN还未纳入任何补票，完整实际缺口因此未闭合。runner明确拒绝joint proposal大于history声明余量；没有使用布尔true替代计量证明。

新entity独立提4096（未授权/未加账）：保守覆盖raw token仅作metadata文本、规范化身份至多1024、opaque历史880、module候选512、前后身份234、SDK候选7、固定输入/目录/输出身份≤128，总2785≤4096；重复前后身份也保守再计，完全不借旧8192。即使将raw token3072的每个拼写再当额外实体也不能在此4096内假称覆盖，届时须停交口径差额，不能改票；当前定义实体为规范化的输入/输出/候选身份，token出现次数在metadata重复费内。若root接受4096，entity525552余74448。byte提案若接受则build109161860136余28277093336、combined118907587221；这些均未应用。
历史owner实际UNKNOWN；原1000和root4000、原16628与256MiB、历史author过量/补票、所有失败/unknown/255保留，均不可借用、退款或追认。删去preparedPreflightDebitUpper/1467/8055门禁，authority须同时绑定真实runner/plan/pins/descriptor/meter-plan/history/计数proof SHA与source ref/SHA，明确新96000 runtime、176000额度提案以及当前不适配余量的停止门、128MiB分票及capture/reuse/defer范围。没有该未来root票不调用。所有原第九节、同版双模型、两OS/真人/CI/父N0/远端门仍在。

## 本轮作者准备计量异常

独立报告全文已读：11797B/SHA273bf71ed9d07126afee31e8630c8469bd191068a147b76c218b283ec52b3583。作者一次witness实读pin/schema成功；但原4600专项漏算re.findall生成3字段列表后再list==遍历3成员，两遍最低5280，较专项至少多680，其它outer/path/set等UNKNOWN。作者已停止新增读取，原6000各分票全部保留不借用；owner对建议4600不足负责。未来行费从16改24，显式覆盖outer1、regex三字段物化3、结果成员构造3、比较3、固定比较列表3、path解码1、map查询/插入2以及固定边界/标量保守8，总24；此修订不是对已发生准备超票的追认。当前2145263是root已增加一次的声明保留账，绝非本轮actual或充分上界。
