# I06 B-M 独立实现审查

2026-10-21，审查者 `/root/i06_design_review`。**通过本轮获批 B-M 真实私有 metadata 子集的独立审查：冻结实现、专属测试及说明未发现新增范围内阻断。**结论不是目标OS、完整应用inventory、原生首IO能力、公开接线或指定双方外审通过。

## 范围与固定输入

实际树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-real-private-metadata`，分支 `feature/I06-real-private-metadata`；批准base `5f910b52c69d86a1076b2032e5d3c63e715947f3`，采用commit `f63fe6fa0ba9eff944b11b9e4bbd7e6235e43dbc`。已实际核该commit只增加A inventory及专属测试两件，当前原字节/SHA与fixed-inputs一致，未把cohort或e2c网关当正式依赖。

先全文读BM授权7201B/SHA `feb2f93a2cbc6722b3f7ba61fb4671d34d6f44caeeda2548971bb3a04ecd1b72`、fixed-inputs1028B/SHA `c5353e75256cd8a57b02418e0aefbde8677becb125be9a0d240947477ec7ee61`、根方案复核14477B/SHA `16febc6c5c5174d01ebf00c599ac86b91cb9058ae9687ca1feffee48458179be`及新树AGENTS15852B/SHA78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759。common17891B/e437121a08053544c2a09151ac5183baf15b5fa67a3a604891aaa9e77ba971b0与此前全文所读版本实算未变。

模块744行、专属测试687行、static-preflight及说明均已全文读取。必要原件包括三轮专项receipt/日志、最终源归档、类型/lint终态及正常check/source终态；没有以中间通过替换首失败。

| 对象 | bytes | SHA256 |
| --- | ---: | --- |
| apps/desktop/src/main/security/private-resource-owner.ts | 25763 | f9667954fd7efe96a563287a0d7d6f5fcdfa7b8d9a0146c1651487d375885a54 |
| tests/unit/i06-private-resource-owner.test.ts | 30354 | 633403a489542b6fd1130a8d4e05c8b7ebc81874b3c24b648e32d80c2fbcdad3 |
| 只读A private-resource-inventory.ts | 23598 | 0f6a2125d5dea53b5e5badde99401086284d4fd776b0cefadad324e408c786e5 |
| 只读A i06-private-resource-inventory.test.ts | 22330 | 7d82c1012bbe7fc35c5faf6eaf167b82d93a357e0b1060db6256ba809a118f49 |
| docs/iterations/I06/real-private-metadata.md | 8657 | 594ee998d487f20d4fc7f56aca6fd9bf6b8ae9e1d799ee8024eee3b4d4a00e7f |

inputs/frozen-before-check.json的以上五件均逐bytes/hash核当前相符。after.2归档的module/test也逐字等当前f966/633。

## 核心判断

**真实来源与闭包。**唯一真实Node调用为lstat(bigint)、opendir、Dir.read/close；没有普通文件正文open/readFile、内容仓库、凭据、SQLite或网络调用。operation(start)是模块内部固定调用点，不是对外通用IO callback。binding/options先own-data捕获再strict schema；getter/额外字段、非法预算及非规范根在FS前拒绝。四个owner仅private-root/credentials/configurations/audit，全局缺席profile/database/tasks/retirement不补空，因此observed和inventoryAccepted不等于完整应用complete。

**接纳和Dir寿命。**249–290行先reserve slot和active计数再启动实际Node Promise；finally只在该Promise实际结算后减少active。Dir把同一acquire slot跨read保留至close成功；实际关闭回执未知保原Dir/slot和releaseUnknown，不能由业务结果、cancel、timeout、ERR_DIR_CLOSED或重建假清零。递归先关闭本Dir再深入子目录，未知关闭仍阻止该轮observed。当前这些机制只覆盖本供方自己的固定调用，不认证未来全部应用写者。

**mutation与迟到。**cancel使generation/revision失效，但不清mutation；close阻新接纳并等待running/关闭，未结束mutation明确unknown。精确token收尾允许在close后完成，但不重开接纳。running时beginMutation先失效观察并返回busy，不发可启动写票据。旧profile/A owner失效后投影拒绝，不能以晚扫描补新组的来源。endMutation仍只是未来可信writer内部握手，当前没有用它认证真实OS写入或Job终态。

**真实metadata与保留。**identity以实际bigint dev/ino无损编码，parent及所有A投影值独立复制；没有以hash或浮点制造OS身份。静态symlink/未知类型拒递归，未知项/孤儿/pending/未知目录保事实且unknown。当前文件按跨四角色distinct位置闭合nlink；目录nlink不套文件规则。旧消失/被替换身份保retired，原A不支持同址历史/current时返回unknown并保旧新事实，未删历史/改A取绿。条目、根、深度、UTF8路径、保留字符串及序号均有有限拒绝门；预算失败只给unknown部分事实，不宣称成功截断。

**整轮时限与A投影。**扫描await前后检查generation/deadline；四角色列表全部reserve后才取revision逐一observe，避免互相使票据过期。643–648行在同步投影后再次核整轮deadline/generation，并在过期时降为unknown投影；A后起的各票据TTL未被冒充整轮期限。5秒不是系统调用timeout或必返承诺，未settled实际调用仍占槽。

## static-preflight处置

4852B/SHA `dd5679192defd59b585d20acf4e5a8206b694ab95eb34acd0e1d710487d159a8`的实施中建议不是最终通过报告。本轮回读实际修正：

1. mutation取消/关闭屏障已保留，专属测试500–534行有精确token、cancel/close及后续拒绝对照。
2. 内部failure采用私有WeakMap；未知throw的code descriptor分类完整置于catch内，分类失败归固定io；observe另有拒绝收尾，不把未知异常读出到结果。没有继续使用未知throw instanceof。
3. 最终投影后整轮deadline/generation复核已落地；本审仅静态确认该分支，没有另行运行慢IO/时钟注入探针。
4. Node nofollow原子性和5秒非系统调用timeout仍明确保留，未被误判为已修复或本阶段通过的原生能力。

## 实际测试证据口径

这些运行由owner/platform agent执行，本审只读取并核原件，没有重复运行47专项或旧A/整库检查。

- bm-agent-first：exit1，38pass/7fail/1skip，绑定ae7984…模块及931546…测试；首失败保留。
- bm-agent-after.1：原模块ae7984…，精确定向两例仍2fail/45skip；不是整套失败重跑结论。合法同bucket多个条目/硬链接投影因共享parent对象不符A捕获树的原因，最终resourceValue独立复制已修正。
- bm-agent-after.2：exit0，47pass/2skip；before/after均绑定本最终f966模块、633测试及只读A0f6a。stdout/stderr实际bytes/SHA逐项符合receipt，原源归档逐字等当前。两skip是Linux非法byte名与Windows分支；当前Mac fixture结果不冒称macOS15/Windows11两目标OS通过。真实mode-000用例与错误注入用例有分列。
- 最终unit类型和模块lint receipt均exit0。full-check-first与sources-first receipt均实际exit0；stdout已读到1052 Python通过和12归档源，stderr均为空。本审没有自行运行这些检查，也不把receipt扩成原生/生产证据。

close-receipt-once明确是在实际Dir.close后模拟收据失败，不是OS close故障实证；after-root-reserve是初始化故障注入。call-through readFile/readFileSync/open断言与实际目录/链接/权限fixture相互补充，不是全套mock。首次fixture EILSEQ及其他原始失败未被洗掉。

## Node未fence残余与授权判断

lstat→按路径opendir之间存在替换窗口，opendir可能跟随新symlink并枚举目标metadata，事后stats不能撤回或排除ABA。当前说明准确限定静态symlink拒follow，不声称竞态下原子nofollow；模块所有结果仍node-observed-unfenced/productionAdmission unsupported。当前实际执行只受控独占临时fixture，既无app bootstrap/公开桥也没有用户目录运行许可。按已冻结B-M授权，这属于明确后置C的剩余限制，**不因此要求本轮增加native或擅自扩权**。未来若移入用户目录或需要绝对nofollow，必须另批root-relative原生方案；本报告不允许其当前直接消费。

B-R持久来源/fresh/安装级writer、B-L旧仓库/网络/完整underlying、T01真实profile/数据库/worker/dispatch/永久寿命、native/VFS/两OS、首内容IO和生产接线均未实现或验证。当前进程历史与真实四角色子集不能伪mechanism-restored、LocationLease或完整全局snapshot。

本审未运行任何产品/探针/测试/构建/安装、用户内容或凭据/网络/GUI/native/e2e/HMR，也未修改code/test/AGENTS/Goal或旧证据；仅写指定本报告，无commit/push。指定模型同候选双方新审、父I06/FR-002、CI/正常合并/远端及真人门保持。若最终代码或验收输入变化，应按实际delta再审，不继承本报告给变化后的候选。
