# 批次纯复核：独立功能、安全与契约审查

结论：**通过固定候选16c58c6d0ca56491c7134c4866f9bed5e0f722c5的本轮独立实现审查，无需要修复的P0–P3实质问题。** 结论限于按原child限额的一次给定批次内部一致性复核、获批partial组合与相关测试，不证明I05已消费、真实图匹配完备、恢复/selected/生产授权或父产品通过。逐操作预算完整独审由另一个独立审查承担；本报告不代签该结论。

## 固定候选、授权与字节闭环

实际工作树为`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T05-profile-revalidation`，分支`feature/weekly-t05-profile-revalidation`；Git base为`5f910b52c69d86a1076b2032e5d3c63e715947f3`，受审/current HEAD为`16c58c6d0ca56491c7134c4866f9bed5e0f722c5`。先`cf93fe8`逐项采用dbb固定21输入，再新增3路径并精确适配1条采用测试；相对5f共有24产品/测试/夹具路径，不能表述为整个差异仅3路径。

实际全文读本树AGENTS15852B/SHA`78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`、common17891B/SHA`e437121a08053544c2a09151ac5183baf15b5fa67a3a604891aaa9e77ba971b0`及review目录三份授权输入：

- 纯实施授权5884B：`c26d5b90b158ea8e241d48d3129a8e53ffd5720fd3fb76ea9a1e13c502442161`。
- 批准采用清单5994B：`d5486d92359fae36363dcf01270394f31e15a92ba16a614a0ba62b2baa621461`。
- partial导入测试精确适配2178B：`d8d9b467534338b59d137fa0127a8f4c5eabb5f9548785cb65950d35b81b1699`。

只读固定330fcedb297792e0addd55557688509550c3b26a提案的实际API/表示/完整算法/验收与范围条款，没有重开已冻结比较数学。逐21从dbb Git blob重算bytes/hash，均与批准清单相符；其中20路径当前原字节等dbb，一条imports测试仅在授权范围适配。全部21采用项和3新增项的当前字节逐一等16c固定Git blob。完整24路径绑定见`independent-code-input-binding.json`。未改产品/测试/loader/依赖/配置、未触旧树、未提交/push/切分支或重建Goal；本审只在本review目录写独立证据。

## 实现与契约核对

全文读184行`rule_revalidation.py`、592行新专项、30行fixture、imports适配前后；并检查实际调用的canonical rule_firing、rule_profile、rule_terms原路径，未读未批I05/T01候选。

`rule_revalidation.py:86–96`通过固定17字段表读取exact ProfileLimits，逐值exact int而非bool、限定0到旧默认上界，再创建独立冻结副本。接口要求keyword-only limits/disabled，没有默认原限额或调用方Budget。原生类型门在使用外来对象的长度/真值/比较之前执行；深层值交由现有有界typed encoder/原compile/evaluate处理，没有额外深层预扫。输入的数值shape不证明其实际来自该child可信分池，调用层来源/整次账本仍是前置。

`:138–165`明确区分disabled、无生产batch空定义与真正空batch。disabled要求原matches为空且saved=None，仍完整compile；enabled非空定义缺saved拒绝。saved为真实空批次时不走definition-only，全部false输入照常evaluate。定义非法/编译预算不足安全失败，不把disabled状态当定义已验证。

`:163–170`fresh compile一次、原original_matches tuple原样evaluate一次；不通过true firings重建、排序或截断原输入。原compile/evaluate校验全部false/true输入、全部比较、重复match、多head与输出原子性。保存的firings和facts以原typed编码完整编码一次，两条payload连接边、digest与profile逐项有界比较；source/revision/definition_digest/policy、bindings/when/proof/basis/所有head和比较均受完整字段编码约束，不是仅对head数量或自报hash。

`:173–183`只在完整canonical相等后逐组、逐comparison验证exact记录与tuple边界，对每个left/right出现调用同canonical模块的check_value。字段相同的手工ProfileValue、mutation后重hash、alias模块或反序列化对象不因此获得真实发行身份。没有把新鲜计算值替换进保存对象，没有修复损坏记录或发布部分通过结果。值发行身份仅是机制一致性事实，不是producer权限。

`:121–128`保留resource的安全reason/classification/location；其他错误或意外Exception统一Internal，结果只可能是两个固定字符串。新代码没有新增日志、异常文本/原文投影、网络、Store写入口、公共协议或包root导出。运行期Python异常上下文不作为输出或日志；本轮并不审计调用方异常展示链。

控制池实现没有按组重置/借池；三个Budget均用同一冻结原限额副本。新模块没有另开默认池、重排matches或调用旧逐组复核。下述运行证据支持相同输入的replay费用对应；本报告不以单个样本代替完整逐行费用证明，也不把synthetic控制池边界/注入耗尽改写成I05真实allocator/自然耗尽或整次生命周期验收。

## 测试真实性、导入适配与原失败

新专项覆盖source40000旧成功→旧逐组资源拒绝→新成功、多规则/多head/重复叶依据、全部false、原bindings顺序、tight原limits、disabled/缺batch/真实空batch、完整连接边和后项篡改、当前发行身份、原子失败及safeerror。对late false后错误仍实际执行后续比较；损坏source等不回显原文。测试中的两池故障注入明确标记为dependency fault，控制上界/N100算式明确标记synthetic，并非I05真实运行。

fixture是手选小输入/预期RDF集合和版本元数据，没有读取actual生成golden、第二图matcher或恢复器。实际预期集合与规则输入相符。完整FR/profile九域/图匹配不是该小fixture声称的覆盖。

导入适配仅替换第一个fresh子进程测试：真实quality/rule_firing导入、rdflib/rdf_terms未导入、全局logging/decimal/int政策未变、原__all__与unknown AttributeError保留；缺失definitions/planning用find_spec is None且四个旧lazy名字均ImportError，失败后不缓存。无skip/条件放行/假模块。第二个manifest测试的实际函数字节与dbb相同，原五项hash断言保留。这只验证获批partial组合，不声称旧完整lazy identity兼容通过。

读回首失败原件：原采用组合imports测试1failed/1passed、exit1；新增专项attempt1为132passed/exit0，扩大后的attempt2实际1failed/145passed、exit1，原因是测试错误预期alias parser可发行，而canonical typed encoder实际先拒绝。最终改为断言该拒绝并另构造alias记录/真实pickle roundtrip拒绝，attempt3为146passed/exit0。原lint首失败及修后输出亦保留。没有删除首失败或将作者日志记成本审执行。

## 本审实际命令与结果

本审通过subprocess实际执行，原argv/cwd/ref/returncode、完整stdout/stderr和hash都保存到同目录receipt。没有重复正常npm check、verify:sources或受影响全suite，也未安装依赖。

`uv run --frozen --no-sync pytest packages/engine/tests/test_quality_profile_revalidation.py packages/engine/tests/test_quality_profile_imports.py -q`

实际exit **0**，**148 passed in 1.49s**，stdout260B、stderr0；见`independent-code-tests.receipt.json`及原输出。

`uv run --frozen --no-sync python docs/reviews/T05/rule-batch-revalidation-implementation/independent-code-probe.py.raw`

实际exit **0**，stdout4768B、stderr0；脚本/完整输入构造/完整观察输出及receipt原字节保留。探针没有改测试或实现：

- 独立手写source40000规则、完整两match（s2/f2先、s1/f1后），手工断言全部facts；原compile+evaluate成功，usage为work1085586/input182041/output82902/trace26/firings2/heads2。旧同池逐组实际RULE_INPUT_BUDGET/resource，已用input262144；新返回batch-consistent，replay usage逐项等原。saved-encoding为work247147/output82902/input0，saved-issuance因无comparison为0，control used331813≤limit1082571。这是给定输入机制见证，不是图执行器或时间/内存容量证明。
- 16项仅append回调Probe覆盖limits字段、disabled、definitions/catalog/matches/saved顶层、saved五字段、catalog字段、定义source、TermInput.kind、保存source与comparison tuple。全部安全失败且hooks始终[]。原专项Foreign抛异常测试本身不能排除“调用后异常被wrapper捕获”，所以此独立探针使用append而不抛异常确认本次边界；没有因此放宽类型门。
- 在副本建立后仅由探针受控hook修改原限额work=0，独立副本仍保原值且复核成功，实际确认没有借用调用者原limits对象。此hook不代表生产支持回调或并发篡改。

## 固定四路径与保留门

- 新模块6288B：`9e9258cfefdef56f369dad6bb7838afd22478ea6714e4322b2d872d12616200e`。
- 新专项23773B：`8876220e84e6124d327c39d6335957a8d5625afcdcd057b962a80da9be5c4676`。
- 新fixture1069B：`ceddb98931b2e9a92448503c35f00db8d15457a41541841f89759c3c982cf581`。
- 获批imports适配2133B：`70e9c87e4cec7ee159734eea807c7b04f7a81f37c687a7dc491c9e3597751c46`。

没有本机GUI/Electron/native/HMR/e2e、凭据读取/模型外发/费用。正常全check由作者执行并封存；独立预算逐行、根最终核验、指定同版双审、CI/正常合并与远端门仍各按实际完成状态。源码import不等于D2包内可用。I05可信原tuple/全false输入载体和整次分池/重试账本、严格JSON恢复逐字段认证及独立R成本、T01成功producer/不可变输入/权限/持久窗口/撤回GC均不由本次通过关闭。
