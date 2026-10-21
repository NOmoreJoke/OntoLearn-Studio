# I06 A：保护清单与 cohort 纯机制总控独立读回

2026-10-21。结论：固定 `6a38fcb8135343ba5e62a8a8effe57b18c3de00c` 的四新产品/测试路径与7045B实施授权一致，本次独立静态及原件读回未发现新的范围内阻断。四项P2有真实原始反例、修复与最终验证；候选、完整check和65成员证据包可以绑定。可以交root作为**内部纯机制阶段**技术收口依据，不是I06/FR-002、真实inventory/lease、首内容IO、目标OS或指定外审/发布通过。

本审仅Git、文件读取、stdlib JSON/ZIP/hash/集合断言与代码数学推演；未import或执行产品、TypeScript探针、测试、构建、native/GUI、凭据/网络。下列运行数字来自已实际读取的owner/独审原件，不冒称本审重跑。唯一写入为本报告；不改产品、owner证据、共享state或Goal。

## 固定范围、来源与归档

树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-project-inventory-lifecycle`，分支 `feature/I06-project-inventory-lifecycle`，base `5f910b52c69d86a1076b2032e5d3c63e715947f3`。首尾实际HEAD为6a38，状态仅保护AGENTS未暂存，无产品WIP。

已全文读取7045B/SHA `20c9c0c6006746a54e286d391e49fac728810889a8165e13838d82667779708f` A实施授权、此前本审12219B/SHA `556c6b838cf8e0c6a209a5a3633286128a1687bb208d25ce91191e56bd56647e` offer报告；AGENTS/common沿前次已读相同固定输入和本轮startup/独审回执核身份，不将旧ownership文字覆盖最新交接。两模块685/671行、两测试546/636行已完整分段读取；A说明、处置、独立最终审查与两次原始审查探针全文读回。

实际base→head **68条新增路径**：恰4条授权产品/测试+64条本阶段docs/原件，没有修改或复制e2c/961旧网关、guard、平台脚本、index/engine/task-service、Store、canonical、preload/renderer、依赖锁、build/CI或旧测试。用实际Git差异证明零额外产品，而不是仅相信文档“自包含”。

| 固定产品/测试 | bytes | SHA256 |
| --- | ---: | --- |
| apps/desktop/src/main/security/private-resource-inventory.ts | 23598 | `0f6a2125d5dea53b5e5badde99401086284d4fd776b0cefadad324e408c786e5` |
| apps/desktop/src/main/security/project-cohort-lifecycle.ts | 23585 | `bcbb73449395757b0cb6260b1299366e1a25de5bcc16c161f145a1f7674fcdb9` |
| tests/unit/i06-private-resource-inventory.test.ts | 22330 | `7d82c1012bbe7fc35c5faf6eaf167b82d93a357e0b1060db6256ba809a118f49` |
| tests/unit/i06-project-cohort-lifecycle.test.ts | 25548 | `f90dd23b6f30e4e641197db6cb93a0fae4786948e489d4985b38f37ec0bf2fea` |

独立核manifest66记录全部当前bytes/SHA=固定Git；加manifest和packaging-verification两自排除件恰68条实际delta。ZIP有65唯一安全仓库相对成员，无绝对路径/..，CRC正常、成员集合等manifest.zipMembers，逐成员当前/固定Git/bytes/SHA全部一致；没有解压执行。`inputs/frozen-code-before-final-check.json`5件（四文件+A说明）逐hash核同，最终全check所用代码输入未漂移。

| 外部绑定件 | bytes | SHA256 |
| --- | ---: | --- |
| evidence.zip | 100052 | `4b24eb70a7d06fea57ba82921b35cfdbafb35548071070b3707e15955aa003c9` |
| manifest.json | 19765 | `203b1a67f465569b3e91ebf403b3688a1031435a57c39daa581e3d4d2bf08691` |

manifest不自列、ZIP不含自身/manifest/后出的packaging-verification；固定Git与实际delta提供外部绑定，不借“清单自己声称完整”作循环认证。

## Inventory实际行为

八个owner角色由运行时Object.freeze的固定数组定义；内部register/complete与inspect复用不可变全集，缺任何角色不complete。opaque owner/observation/snapshot在工厂私有WeakMap中按实际对象查，结构克隆、跨工厂、旧profile epoch、同值profile重开后的原owner均不能获权。context只认process/profile两个有界字段，不靠renderer UUID或safe布尔值。

capture仅精确own data descriptor复制：普通/空原型对象及稠密数组，拒getter/符号/额外shape/循环或重复对象引用、非有限数；depth12/node700000/累计string16MiB，单string16384，资源32768、root32、components128与每路径UTF8 16384B。内部metadata与components、返回owner集合/protected快照深冻结，外部随后改原数组不改状态。Proxy trap可执行，busy fence阻同核心重入变更；这不是CPU/恶意同进程代码沙箱。

reserve/beginMutation先bump使全部旧观察/快照失效再合并；同一revision各owner才可共同完成。观察票据每owner一张、全厂最多2张、5000ms，捕获前后均核时钟；任何expired/坏shape/冲突使owner unknown并保旧保护记录。完整观察不能省略该owner已有记录。retirement必须明确mechanism-restored，否则unknown；缺失/failed初始化不当empty。profile/private根必须实际存在于接收的metadata列表，confirmed-absent不能绕过这两个根要求。

资源分private-deny/profile-container/database-managed；parent身份+精确components、category/kind和已有identity不能被重新观察换成不相干对象。prospective的null identity允许以后明确materialize；absent-retired允许保历史identity但不当当前目录项算linkCount。现存private文件按OS身份分组，distinct location数必须等links，同组links不一为unknown；DB links>1为unknown。这里只验传入metadata的一致性，**没有真实OS观察或全盘alias认证**。

merge保稳定RecordState及出生owner，只更新不可变resource；release闭包捕获的仍是Map内同记录。跨profile旧记录变retired但不删除，旧release只能更新其原记录，不改新owner/新记录。released-retained保留路径/身份和保护，不成为重新打开权；private角色不能调用DB释放，也不能经raw输入声明released-retained。

trackDatabaseRelease只接本厂当前database owner和1–16精确唯一ID；types.isPromise先验证native品牌，再拒非Promise.prototype和任何own键，拒thenable/Proxy/装饰Promise。原Promise在成功登记后进入私有WeakSet，终生一次，结算/close/profile都不移除；可在一次调用给多个原资源，不能把已用Promise复用给另DB/新profile。最多2个实际未settled释放，未终态前始终占槽；成功转原记录released-retained，拒绝标unknownRetirement并保retired，不因timeout或close提前清零。失败unknown未提供自动恢复是保守闭合，不是假成功。

快照上限16、非续期30000ms、revision/sequence安全整数耗尽及clock回退/throw/NaN/不可精确加TTL值均fail closed。startProfile同字符串仍增内部epoch、清owner并保retired；close不清未settled或残留。没有FS/目录读、SQLite、原生句柄、密钥、网络、文件能力或通用IO callback。

## Cohort实际行为

固定holder角色包含main/task/engine/Store/worker和I06直接及间接链，health-probe显式登记才纳入。private WeakMap/WeakSet区分owner/transition/cohort/engine/token实际身份；使用过的engine对象不能重用于新transition。prepare捕获exact四字段后再次核clock/revision/current，完整条件成立才quiesce旧组并安装一个candidate；捕获耗时过期不关闭旧active或安装半候选。

每条被接收的operation只绑定一次真实native Promise，本厂WeakSet永久防复用；kind的Store-ready/Job-ready/scope-ready/model/child/Store-connection等有role限制。全厂pending256、每owner32、picker1/acquire2跨epoch全局计数；cancel只标cancelled，不delete pending。subscribe不确定保槽并quiesce。**只有原Promise回调真实fulfilled/rejected才移pending与owner.pending**，cancelled/旧candidate/owner draining的late成功不补initialize/binding/ready。

release成功仍须该owner所有被登记Promise已settled才released；失败保持draining/failed，不能用一次返回、自报count0、逻辑abort、5秒等待或清pending map证明释放。waitForDrain每cohort复用同一Promise/timer，超时只返回unsettled；close只停止接纳并quiesce，实际槽继续保留，cleanup release仍可登记。retained cohort32与lifetime token65536为有限工程界，耗尽封闭实例不绕epoch。

publish同步核：唯一live transition、candidate当前、旧组每owner released、必要6角色、各initialize/binding、Store-ready/Job-ready/scope-ready、model enabled/disabled互斥；enabled须完整间接链，disabled时若间接owner已登记则必须released。它接受pending的**已登记**child/Store永久寿命，拒其余pending或cancelled工作，交换指针前再查clock/epoch/current。所有成功/失败结果带mechanismOnly和productionAdmission unsupported；不存在生产main指针/模型grant接线。

新增P2修正对被登记child或store-connection永久寿命在candidate/active的终态，无论成功或失败，立即quiesce整组并失效candidate；已draining时正常结束继续实际release。该kind明确是整个cohort永久stopAndDrain聚合寿命，不是可重启同Supervisor短session；普通noteViewRecovery只在active+同engine实际机制对象下返回原cohort/epoch，不清grant或强行重建。

**证据边界必须保留：**A并不认证所有真实资源均已注册，机制演示甚至可以没有child/Store寿命Promise；它只核被接收的有限owner/Promise事实，不把任意native Promise的fulfilled认证为实际child退出/OS锁释放。真正B/T01必须保证整个实际持有链/永久寿命/metadata/原生lease充分且可信，才可能消费这些状态。当前无B/持久retired/真实T01release时生产仍unsupported/incomplete；不得拿pure publish、synthetic complete或opaque机制engine对象当实际Supervisor、位置能力或两层ready证明。

## 四项P2：原件与最终关闭

已全文读raw/independent-inventory-first.txt和independent-second.txt：两探针均原owner独审实际运行node --input-type=module，本树TypeScript内存转译/data-URL import，原脚本和合并工具输出保留，exit0只说明探针执行成功，**输出实际证明旧候选存在缺陷**。stdout/stderr未分离的限制没有被补造。本审没有重跑它们。

| 问题 | 真实红件与修复判断 |
| --- | --- |
| 导出必需owner集合可删改 | 首红inventory-independent-red为1fail/33pass，因测试顺序不能重现另一项；修正反例后red-both真实2fail/32pass。现在Object.freeze固定八角色，测试实际splice尝试后仅两owner仍不complete。关闭。 |
| reobserve替换RecordState丢release事实 | 同red/red-both实际期望released-retained却得到retired；现在merge保稳定记录+birth owner，track→重观察→resolve测试核原记录release，跨profile晚回不归新组。关闭。 |
| 旧/并发Promise冒充别DB release | inventory-promise-red在1018源码真实2fail/34pass，跨DB同时及已fulfilled/新profile均被旧代码接受；现在成功登记即WeakSet终生一次，新增直接反例通过。关闭。 |
| child/Store永久寿命已结束仍publish/接纳 | cohort-lifetime-red在a9bf源码真实4fail/30pass，candidate/active×child/Store各不draining；green真实34pass。现在settle统一quiesce/失效，兄弟owner也拒新接纳，普通refresh/disconnect有对照。关闭。 |

红件对应旧source快照SHA已在manifest核同。首两红源18439a…已含另一clock修正，不能假称等最早c885独审源；原独审报告准确区分。寿命green输入cohort c857506e…后来只补永久拥有关系注释，最后bcbb7344…已由完整final check重新验证；没有把green旧hash冒称最终hash。

首inventory lint no-control-regex失败及cohort初始prefer-const/MAX_VALUE失败保留。cohort-agent-first-failure是工具转录，缺逐命令原流/exit，本审不把它提升为分离进程原件。原始日志尾空行使全证据git diff --check exit2；packaging记录精确raw排除后scoped exit0。不能把完整raw检查写成全绿，也不为满足whitespace清洗原件。

## 最终实际验证与冻结绑定

已读完整final-check stdout/stderr/JSON、sources-final、70专项、安装环境命令原件和所有上述红→绿关键输出；各argv/cwd/exit均来自新树。正常check依次真实完成lint、format、contracts/unit/desktop typecheck、vitest、electron-vite无窗口build、ruff check/format及pytest，未启动Electron或native。

| 原件 | 实际终态 | 范围 |
| --- | --- | --- |
| specialized-after-all-fixes | exit0，70pass，0skip | 最后逻辑修复后；cohort之后仅注释，最终由全check覆盖 |
| full-check-final | exit0，17 TS files/700 TS、1052 Python | 5个最终冻结代码/测试/说明输入逐hash绑定 |
| sources-final | exit0，12份归档源 | 同树最终候选 |
| npm ci / uv sync --frozen | 各exit0 | 新树路径与新.venv有实际原件；无新增lock/config差异 |

首完整check的694TS/1052Py只属中间候选，不替最终700。owner最终独审形成时full-check-final仍进行，该报告不声称最终check已过；后出的disposition与raw才记录真实终态，时态未倒写。本审现在读到终态0并核冻结输入未变。

未发生真实FS/metadata供方/持久retired恢复、native句柄/跨进程fence、SQLite VFS/ABI/锁、Store/worker/宿主或公开UI接线、两目标OS/native/真实凭据/人类验收。父I06/FR-002、指定GLM-5.3最高与M3.1-Flash xhigh同候选新审、CI、正常develop合并/远端门均未关闭。A内部源码技术收口由root另行决定，本报告不自动授权后续B/C/D/E或更改Goal。
