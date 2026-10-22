# T03 最终计量增量独立审查

## 访问前预扣

本报告先于任何本轮文件读取独占创建。本轮完整保留新独立票8000 metadata / 2097152B应用读取，失败与未使用部分不退款，不借旧作者/root票；不是actual或OS I/O实测。

metadata方法：结构化材料只解码有限manifest/final pins/meter-plan/history/disposition，预扣4000覆盖总U≤1000的解析/物化/有限直接取值（3U+8每文件）及最多23文件pin核验。call-plan和其它文件以有界文本读取，不整份JSON解码或遍历其大型字段数组；文本字符/哈希不是metadata记录，必要有限字段/表项检查另在第二阶段预扣2000。固定源码与proof静态控制流审查不执行、不AST遍历或抽取运行；有限分项、引用与对账使用该2000。报告/收尾预扣2000，固定有界段落/表项，不遍历历史大账。总计8000，阶段不相借；遇有疑似不足先停止并报准确边界，不追加访问。

byte方法：唯一允许的有限文件总≤23，单文件≤64KiB、单次总≤384KiB；必要固定Git blob对照另≤384KiB、必要文本二读另≤384KiB、报告及收尾另≤384KiB，总保守≤1572864B<2MiB。原窗口/closure包含在首个384KiB；不读tool/SDK payload、117身份内容、880witness、索引或旧大包。固定Git身份和文件SHA由单次读取保留，不重复线性搜索或重读补数。

上述为访问前记录；最终结论见下文。无执行权限。

## 本次固定身份核验

固定ref bff478ae35cd90fbc894354b859b3e38e795fe83。有限10文件current与固定Git逐字、bytes/SHA一致；未访问身份文件或旧witness。五个小JSON结构U的全标点保守上界合406，native解码费用≤1258；22项manifest对象加至多10项文件核验另保留≤400，均在预扣4000内。已知此步骤应用payload读取181324B。文件pin：

```json
{
  "run-once.py": {
    "bytes": 43415,
    "sha256": "3dc707524d9d0faae0d76e037aa84e18c9c23b4b1450ba2a02ad369ba2a21fd7"
  },
  "call-plan.json": {
    "bytes": 9557,
    "sha256": "4f91b5a9f15d6f8e279dbc0b64abb735c899c3352824a4d9bed32bbac0b35fd5"
  },
  "meter-plan.json": {
    "bytes": 995,
    "sha256": "a374b3381022646639593c1cb2e961fb47a9626ed7ddb17ee67f77d76619596a"
  },
  "meter-history.json": {
    "bytes": 1058,
    "sha256": "a800ac78d630b8deb34cf951209f0c430d5595f7c864239a89f16247c11d9ef2"
  },
  "control-method.md": {
    "bytes": 4432,
    "sha256": "51688e2be2d061adcb2dcb1d247c9ceea0de0631677953f94fdeecebfc9a0d70"
  },
  "dependency-method.md": {
    "bytes": 3316,
    "sha256": "2ebf033adc52151a42b697f80ca9ecfcbd178ef4eb134871f843a84133268149"
  },
  "meter-preparation/meter-proof.md": {
    "bytes": 9621,
    "sha256": "d6993a89d168cdf4e4736a98e3bce64ead60ccb65d14c79c9b959347d872ed3c"
  },
  "meter-preparation/independent-meter-delta-review.md": {
    "bytes": 11797,
    "sha256": "273bf71ed9d07126afee31e8630c8469bd191068a147b76c218b283ec52b3583"
  },
  "meter-preparation/disposition.json": {
    "bytes": 2159,
    "sha256": "7336af84ff719853ed0e73131cab42af076e48fe7510c357639105af6ff206b0"
  },
  "meter-preparation/final-candidate-pins.json": {
    "bytes": 1407,
    "sha256": "5df3598d7c3091e635f2e089f72231de5586aa18517577b8f75cbcd36fdb8047"
  }
}
```

## 命名单源码例外

按root新明确例外（1650B/c675fd0b3603e8f63b96e64f23aa438d5b5203ba01302cf899dd90c69318cc79），只读取一次selectors.py 19536B/SHA b16e673c110fd6a362414308ef73ffc3c15125c87361333b309791735931040d，前后dev/inode/size/mtime等固定pin；未import/exec/call。例外与读取共21186B，使用现有票，无新payload枚举。

## 最终结论

**不通过完整计量充分性；仍 NOT_CALL_READY。** 本报告针对最终43415B版本，不沿用历史42725B报告的结论。共享128次select上限、先扣后select、UNKNOWN停止、历史账隔离和实际hash绑定均可静态确认；但8/次的selector费用仍漏掉已可见库及caller字段访问，完整joint还漏独立owner收尾metadata方法。entity4096只能在明确的“去重身份库存”口径下接收，不能冒作宽口径候选访问上界。没有执行任何候选代码或验证运行结果。

### F1 / P2：select每事件4不足，完整control证明仍未关闭

位置：`run-once.py:571–586`（共享次数、8票、返回集合和逐事件读取）；本次唯一读取的固定`selectors.py`中`KqueueSelector.select`、`_BaseSelectorImpl._key_from_fd`。

已确认的改进：只注册stdout/stderr两个READ对象；Kqueue路径以`max_ev=max(len(self._fd_to_key),1)`传给control并只为返回项append ready，因此在对应kqueue返回契约下，一次返回至多2个ready项；调用上限128在调用之前检查，8票也先扣，空唤醒不退。触顶明确失败/UNKNOWN，不能声称能等满600秒。

仍未覆盖的记录：Kqueue每个kev的list成员访问、`kev.ident`、`kev.filter`、`_fd_to_key[fd]`查询、`key.events`已至少五项，尚未计ready tuple/list的构造和caller解包。非空读分支还必有`key.fileobj`、`key.data`、`fds[...]`三个字段/映射访问；EOF分支也有key/EOF记录及unregister路径。因而“2事件×4=8/次”不能覆盖对应显式记录访问。若六命令共享128次调用均有两条ready且正常完成读/EOF，按上述八项的窄下界已是2048，而书面只列1024；现有control11658的分项证明不能直接签收。这里是允许控制流的静态上界反例，不是运行复现，也不声称本机已实测超12000或物理资源失守。

`DefaultSelector`还由模块`_can_use`选择，可能退到其它已列类；候选没有记录/约束实际backend。fallback类的集合构造也不能自动按kqueue四项费继承。该模块导入时的内部能力选择不是本审执行行为，仍属既有解释器/loader未证明边界。

最小修订：针对接受的backend明确列出返回集合构造、库内字段/映射、caller逐事件及注册/注销/清理的完整账；可固定并记录backend或覆盖所有实际允许fallback。提高调用前费用并重算control/runtime，或给出不重复占用的完整整体摊销证明；不能把未分配的JSON余量默认为补账。保持128、空唤醒收费、失败不退、日志cap和UNKNOWN边界，不要求运行或模拟selector来修此证明。

### F2 / P2：all-parties缺独立owner收尾metadata；24MiB也不涵盖全cap归档

位置：`meter-plan.json:10–18`，`meter-proof.md`“字节、历史与门禁”；`run-once.py:852–856`。

176000只由runtime96000、author40000、root40000组成。原方案另给owner external closure 24MiB，但没有其读取终态/依赖、归档全原流、形成pin清单、读取两独审报告/处置/提交的metadata分票和方法。helper的96000不是这些额外动作的可退款余额，不能借两peer或当前准备票。即使两peer各40000后来能证明，all-parties仍没有完整覆盖该owner阶段。

若owner要独立形成全部原件SHA清单，已允许raw capture16MiB + record/source输出8MiB +一次artifact≤4MiB即可到28MiB，尚未计固定control输入及peer报告；24MiB closure不能证明覆盖所有允许的完整归档。不能以实际日志“应该很小”作构建前证明，也不能省略尾件。

最小修订：把owner closure单列，固定完整对象数/byte与结构上界，读取前收费；或明确由哪一已独立计票的接收者承担完整归档及真实owner必须处理的剩余动作。下面给一套可实施设计模型，不是当前已实现/已获接受的方法。

### C1 / 口径未决：entity4096不能同时表示两种计数

位置：`run-once.py:697–701,757–775,855`及proof实体段。

4096的2785算式是1024去重binding身份、880旧row、512module、234前后identity、7SDK、128固定对象。它可以作为明示的新“身份库存”profile的保守提案；本审没有发现它声称覆盖全部OS/compiler实际open，且不需要为了库存cap另加动态EntityMeter。

但宽口径“规范化候选访问”包括最多3072次normpath后、去重前的canonical候选，再加1024次binding遍历；descriptor117也与pin前117/后117分开访问。按这一路径口径，3072+1024+880+512+117+117+117+7+128=**5974**，不在4096内。此处不把原始未规范化字符当实体，也不计OS内部未知项。若root继续宽口径，建议新的独立8192票及该5974表，原旧8192仍不借、不退；若root接受库存口径，需明确它与历史宽计数的关系，不能事后重分类旧账。call-plan还保留`newApplicationSDKResourceEntityCap:8192`，同时另列fresh4096，下一版应明确旧字段历史性或统一为真实新profile。

## 其余静态核验及关闭边界

- 旧preparedPreflightDebitUpper/1467/8055门已删除。真实auth绑定runner/call-plan/pins/descriptor/meter-plan/history/proof/source，历史owner/current author实际仍null；旧票不可复用。176000>104737会在attempt/child分派前拒绝，未发现一个布尔true能绕过该预算门。
- opaque行费24显式包含旧findall生成及列表再比较，先整体扣880×24+64才访问已固定SHA的covered区。深层references/approvedWitness不解码、不复制进结果；ordinal+whole-file SHA边界明示。这里受限认可对应费用结构，沿用已核验880 schema，不新增旧witness读取，也不把它当现时header/open证据。
- preflight书面算式19372、dependency60075以及无selector项的control10634算术吻合；依赖输出每条最多3字段的dict加container/array member是5U，5248包含1024条、pending64及root/snapshot；最终terminal128U和intent1050U能容纳固定源列出的有界结构。输入3U解码与输出3U编码是明确的语义记录收费模型，需要root接受其抽象；不是CPython/loader内部所有访问、heap或OS I/O实测。
- 仅builtin结构编码，容器进入前检查U，超深/过大明确INCOMPLETE。取消/close/terminal持久化等首因分离及一次stderr回退保留；已看见当前Popen leader限定的terminate/kill、单次attempt/独占输出和无产物执行路径，未新增group/旧PID清理、索引或API fallback。
- 历史独审的event“无界重复”部分可在128次数上限意义关闭；每事件费与完整control仍按F1保持OPEN。旧entity512已撤回；4096按C1仍需口径接受。旧行16已改24，但这不追认本轮作者4600或6000合规。作者5280只是已知最低项，其他及owner当前actual仍UNKNOWN；本报告不补数、不退款、不改账。

## 完整外部审查方法的具体设计

以下是**待实现、待独立核验的方法**，不是另给一个额度便宣称充分。它保留所有原流、所有控制/终态和所有依赖/产物；入场不足即UNKNOWN/HOLD，保存全部原件并申请下一有界review阶段，绝不丢尾、截断后签通过或重新编译来补审查票。root可选择更紧的经证明方法，不把此设计当最小必需成本。

### Owner收尾 profile

一次顺序读取至多64个明确对象，同时hash、累计byte和生成manifest；不读witness、SDK或工具payload。不parse全部重复planned/dispatch JSON，只核归档完整性，并解码build终态、六command terminal、dep receipt、artifact-before，结构U≤5984（128+6×96+5248+32）。验证报告实际状态和对象完整；bindings/ABI完整语义审查由下面两个互相独立peer承担。读取两peer报告并逐项处理，不沿用历史通过。

建议前置费模型：3×5984 +8×9 JSON额外费 +16×64文件元信息/固定pin +3×512 manifest结构 +3×256 owner结果/处置结构 +2000固定scalar与两报告事实 = **23352**，可取**24000 metadata**的明确profile。两个报告的事实集合各≤256，超过则不静默截断，owner阶段另报缺口；2000包含其有界读取/处置，不拿别的阶段余量补。无排序/重复线性搜索，manifest按固定对象表；git/index内部物理I/O仍不冒称已测。

字节建议owner closure32MiB：全cap原流16+record/source8+artifact4=28MiB，固定control/源/配置及两peer报告/manifest在余4MiB内另设联合cap，文件恰一次读取/hash，不重复。不能直接沿用旧24MiB。runtime owner40MiB与closure32MiB、两peer各32MiB合**136MiB**；这只是新的可证明profile设计，当前128MiB未获接受也未改账。

### 每个peer的完整入场与费用

每个peer独立读取同一固定版本、同一全部原件集合；不互看本轮结论。固定表≤64文件，raw12流总≤16MiB，artifact≤4MiB，结构records/source总≤8MiB，固定配置/本次审查输出合计≤4MiB；单pass同时hash、核byte/终态/对象名。无source/SDK/工具payload新扫描。承认这仍是trusted-host记录方法，不是实际compiler-open、loader/dylib attestation。

所有JSON先做不物化字段集合的字符/深度/单位预检，再按总结构U收费后普通decode；原件全部完整保留。总U≤12288，最多40个JSON；它涵盖helper最大成功/失败profile≤8448U、plan/meter/history≤1152U及manifest/接收配置等≤2688U。重复解析和输出必须重新收费，profile只允许一次解码；单遍map无sort/next线性重找。每个dep binding至多8独立验证单位，D≤1024；核source SHA或固定witness SHA+ordinal/SDK evidence ordinal、绝对路径/root域、pending与完整数，pending不是覆盖通过。

raw全12流先只做字节/行/有限语法边界计数，不构造token/list，也不靠regex findall事后补费。定义T为完整语法投影的容器/字段/arg或symbol/load-command成员合计（含每个record本身），最多4096；计数扫描的字符串字节工作与CPU不是metadata记录，真正物化、映射和检查之前先扣5T+8×12。随后完整解析各工具记录并检查compiler实际argv/selected-link线索、file格式、otool依赖/load commands、nm全部符号/undefined、source导入白名单/禁用前缀和ABI声明对应；未知语法、记录超量或缺字段均不签通过。若T>4096，保存未解码原流并交精确新票请求，不为满足上限忽略尾项。格式语法投影及收费实现本身须先审查；当前没有实现这个peer helper。

审查结论/发现/处置事实输出R≤2048U（不塞整段raw或旧witness图）。每peer费用完整模型为：

`P = 3U +8Fjson +16Ffiles +8D +3R +512固定 +5T +96`

代入U12288、Fjson40、Ffiles64、D1024、R2048、T4096，得 **73632 metadata**，可取**75000/peer**。这明确覆盖JSON解码/物化/一次检查、文件前后身份/hash表操作、binding验证、原流语法记录三阶段及报告构造/序列化的有界profile；byte32MiB与record/U/phase cap同时适用。它比40000大不是“最低需求”，而是这里所列完整profile的充分性设计上界；其它实现可省操作后重证，不能删审查面硬凑40000。

上述75000复用已收fixed witness来源与已审runner的确定性SHA+ordinal方法，**不独立重建旧880映射**。若root要求每peer独立重建该映射，再单独允许一次3156859B文字读取，按已核schema24×880+64加21184，得94816，可取**95000/peer**；byte改36MiB。该额外读取现在禁止，不能借本报告的设计擅自运行。任何新SDK/unknown mapping、selected backend/stub/archive实际身份仍需另行有限证据；无法从verbose/符号推出的项保pending，不用普通libSystem名字签关闭。

完整未来joint应写成 **新修订runtime充分上界M + owner24000 + 两peer各自所选P**，而不是只M+两个peer额度。M因F1尚不能沿用96000当充分值。方案只是让root有具体可审的流程和票模型；即使一组上界超当前余额，也不证明不可优化或必须提高guard。当前新审后root声明余额96737、历史异常未知等仍由root维护；本报告未加任何runtime/closure/peer/entity票，也未修改guard。

## 实际检查与未验证

本次实际仅固定文件current/Git bytes/SHA核验、小JSON解码、逐段源码/证明/计划文本阅读、精确rg定位，以及命名单selectors.py静态语义证据。未运行AST或候选；未import/exec/call/模拟任何候选函数、selector或OS接口，没有compiler/inspector/native/API/fixture/GUI/DB/网络调用，无工作树写入、版本/能力探针、额外agent、执行授权、push/PR/merge。

本次未读原供方实验算法、117身份文件、其余114工具payload、880witness、索引/旧205/原37包。历史报告仅验证固定字节身份，历史候选问题据disposition定位；不声称重新审了旧42725字节。没有故障注入、运行资源/ABI/目标OS/I06 runtime证据。T01损坏SQLite/wholeH HOLD、原第九节/无桌面、被拒操作停止线、指定同版双模型/CI/真人/父N0/远端门保持。

## 本审票收尾

8000 metadata分项全保留：固定数据4000（五小JSON标点U上界406，对解析/物化/直接取值3U+8费1258；有限manifest/pin与本审结果构造/打印预留后保守≤3000）；文本/有限静态事实2000（没有大数据结构复扫，定位/表项/语义证据保守≤1500）；报告/收尾2000（有限literal段落/表项；初始预扣、三次追加、至多两次小文案封存和两次报告hash均计入，不遍历历史，保守≤1500）。均为限定本审操作的静态保守收费，非实际全VM/OS次数实测，无借票/退款/追认旧超票。

本次至多16个命名读取对象，只有10个有限candidate文件做current/Git两域对照。已知初次固定数据payload181324B、两root窗口5784B，selector例外+源码21186B；文本分段与定位即使保守按4次完整runner和一次完整meter-plan、proof、call-plan计算，及报告/最终runner pin≤128KiB收尾读取/写入，总保守**≤1MiB**，低于访问前1.5MiB分项联合保留及2MiB票。未把重读当免费；selectors源码只有一次读取，余源码阅读在事先有界的文字复核票内。报告唯一输出，不作Git提交。
