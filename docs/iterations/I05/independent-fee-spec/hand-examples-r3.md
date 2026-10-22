# R3 独立手算、完整 prefix 与失败小账

本文件先给字面算式，再由不 import reference/Ledger 的独立审计器重加 artifacts。它不把同一模型生成 expected 当证明。未改 R2 原手算、19 个旧小程序、8 个 control/累计/BLOCK 字面程序；那些旧通过只保持其原范围。

## 1. 同一完整 baseline:G-base

输入仍为原 18 asserted+10 ontology、84 term/source occurrences（75 IRI+9 S）、R-risk 的 4 when/0 comparison/1 head；三前像71713/61981/15485B，Q133694/D15485/N1；binder material85953B/SHA5bc7b79b64ae371f95078a21eb152fb90e7884a1380764d2b9823a879bda9f8d，逐字段来源和全部 bytes 在 v3 baseline material 文件。无未知收费变量由 owner 后供。

额外C0 source票独立按完整出现计：84个term.source+1个definition.source=85次。28行source编码和text字节手算总20036/11460，definition1312/1003；故新总source验证3×20036+1312=61420、合成digest3×11460+1003=35383，相比旧21348/12463增加62992work、40072scan、22920hash与112动作。alias只省持有，不省出现验证；原始INPUT/完整key/hash也未去重。

八 data handles 的累计 slots=`3747+84252+180+9916+27036+11921+12481+5=149538`，不含 control64 和 receipt。IFR3 比原 receipt 多 reason2+ordinal8=10B，R=`782+10=792`；F=`14+12×5+20×1=94`；H01 work=`94+3×8+149538+4×792=152824`，scan3168、hash810；receipt objects95/scalar1616。与 R2 相比 work+42、scan+40/hash+10、并持+2objects/+20scalar，不能忽略 receipt 自身。

M0 新静态 compile 为 `4×3+3+785+1=801work/785scan`。其余原数学动作相同。因此完整 work 为：

| 钱包   | 手算                                                         |    work |
| ------ | ------------------------------------------------------------ | ------: |
| C0     | R2完整明列3215450 − 原H01152782 + 新152824 + 2×(20036+11460) | 3278484 |
| ENTRY  | 编码72136 + raw2752 + IRI21624 + S392 + fingerprint79676     |  176580 |
| G      | 原完整 seed/sort/round/predicate/join字面合计                |  185814 |
| M0     | 原140761 + 位置/完整Catalog受控compile801                    |  141562 |
| WIRE8M | 原全量byte gate，编码扫描已由C0收                            |       0 |

完整九域：C0 scan2275119/hash823438；ENTRY input70540/scan2752/hash79676；G scan131220；M0 input57705/output21421/scan3867/hash52783/binding1/firing1/head1/trace1。payload298403+rows334379=632782≤8MiB；G185814≤1M、M0141562≤16777216、C03278484≤3240385920，原 cap 不变。新 baseline 正常成功，不把全部输入拒掉。

| prefix    | 动作                          | C0累计work | 全owner live objects/scalar |
| --------- | ----------------------------- | ---------: | --------------------------: |
| 1         | control64                     |          0 |                        64/0 |
| 2         | H01整向量+receipt             |     152824 |                    159/1616 |
| 3         | material3747/85953            |     152824 |                  3906/87569 |
| 4         | C0完整arena84252/3800788      |     152824 |               88158/3888357 |
| 5         | raw12585                      |     165409 |               88158/3888357 |
| 6         | input encode+copy143426       |     308835 |               88158/3888357 |
| 7         | input hash71713               |     380548 |               88158/3888357 |
| 8         | source encode+copy123962      |     504510 |               88158/3888357 |
| 9         | source hash61981              |     566491 |               88158/3888357 |
| 2401      | rows hash完成                 |    3278045 |              149697/6819815 |
| 2402      | Catalog hash439               |    3278484 |              149697/6819815 |
| 2403      | release projected             |    3278484 |              137216/6524772 |
| 2404–2409 | material/四arena/wire逐项释放 |    3278484 |                12080/272442 |
| 2410      | terminal control释放          |    3278484 |                12016/272442 |

中间所有2410项双 tape均给出，没有省略 prefix。全峰149697/6819815；终态留 native11921/270826+receipt95/1616=12016/272442。receipt 的 status/每池已付九域和峰/17L/首错/执行hash/footer均由独立 decoder 验证。

## 2. 六个真实完整入口失败

这些输入原字面保存在 R2 adversarial，R3 重新从 JSON 完整入口计算。表中 h/s 为整程序静态累计证明，R 为新 receipt 长度；失败全部 H01Paid、终态所有引用0、无成功前缀。

| 输入                         | 真实首错与序号                    | 执行项数 | h/s/R       | C0已付work | ENTRY已付work |
| ---------------------------- | --------------------------------- | -------: | ----------- | ---------: | ------------: |
| late-input-invalid-integer   | INVALID_LITERAL_LEXICAL/27        |       32 | 3/2741/692  |       7586 |           819 |
| false-then-type-error        | RULE_COMPARISON_TYPE_MISMATCH/191 |      198 | 5/12153/792 |      23485 |          3191 |
| uncontrolled-head-zero-match | INVALID_RULE/52                   |       58 | 4/6773/799  |      14681 |          2037 |
| uncontrolled-head-disabled   | INVALID_RULE/52                   |       58 | 4/6863/797  |      14785 |          2037 |
| variable-predicate-disabled  | INVALID_RULE/41                   |       47 | 4/6367/798  |      13893 |          2037 |
| resource-before-late-lexical | RESOURCE_LIMIT/53 input_bytes     |       58 | 3/7089/694  |    2416695 |        502398 |

late integer：ENTRY编码337+三个term节点33+raw13+IRI80+两次已完成fingerprint356=`819`。C0原输入扫描/绑定1986+H01（82+9+2741+2768=5600）=`7586`；没有第三个成功 fingerprint 或成功输出。其 receipt scan2768/hash710，释放本次实际开过的3handles。

false 后错误：两 comparison occurrence 都执行，第一次 false 写 trace1不触发 head，第二次真实 domain mismatch终止。M0已付10168、input4418、scan1199/hash3888、output/firing/head0。H01=94+15+12153+3168=15430，C0原8055+15430=23485。静态部分相对 R2 新增3when+3head+18Catalog+1check=25work；不能 false 后跳第二比较以躲开错误。

零匹配和 disabled：都在完整静态 head 第52项拒绝，未进入 join。已知不受控 predicate 虽另一槽为变量仍必须拒绝；M0已付1217=input1073+其余节点/compile144、scan27。disabled 的原封输入长度不同影响静态 h/s/R 和 C0，不改变该检查。when predicate Variable 在第41项结构门拒，M0已付1091/input992，没有 plan hash。

资源先于词法：ENTRY已有 input250824/work502398/scan21/hash251289，第53项请求 input50202/work50221；`250824+50202=301026>262144`，整向量零扣，input仍250824/output0，之后语义坏 literal 没执行。H01=82+9+7089+4×694=9956；所有实际引用释放。该完整分析60项、实际58项含拒绝+清理，分析尾段只保留真实未到达词法错误，不冒充付费。

本次第一次新测试错误预期event49，失败原件保留。R2 collector对象图共享2个source，而保存JSON读回6个独立source；二者JSON值相等、Python别名图不同，不能称同一内存输入的完全复现。旧收费代码按id去重是未经纯规范证明的省票：两source验证=100120，六occurrence验证=300360，差4×50060=200240 work/scan；ENTRY所有occurrence编码/指纹始终相同。旧dry首拒48→读回多4项→H01再1项=53只解释旧路径。最终R3提案明确取消这项身份省票，两个对象图均收六个50060B完整验证；其共享/不共享完整程序hash、执行hash、amount和paidPrefix全部相等，均event53。按最终相同H01计算，旧id去重共享图C0会是2216455/scan1606533，最终两图均2416695/scan1806773；这段是两个提案版本的数学价差，不是产品actual。原R2错误/输入与pre-revision source都保原件，待fresh审者独立核。

## 3. 114 项和差1边界

固定114分析共231960事件，严格执行231899事件。113项新程序在原分池 cap 内；E.5 round4严格首拒为 event13687，M0 input已有255390/work404606，请求12342/work12631，`255390+12342=267732>262144`。静态新增801work导致已有work较R2多801；仍由原 input cap拒绝，未抬cap，已发生binding16/firing15/head15/trace15不退款、不发布15条成功前缀。整个13755项分析不能冒充执行，实际13694项含清理。各项均列逐池精确金额、首错、H01/receipt和原17L预测，现行动态权威继续独立 pending。

原19+8字面程序里的成功/差1/零票、disabled/dummy、重复restore、重复roots和末项首错及 allocator 余数仍使用其原固定小票格式与 literal expected，不把 IFR3 的大程序票偷偷塞入旧golden。R3 的整向量拒绝与 failed0清理已由上表六个真实入口另行验证；R1 F2/F3已独审关闭的小模型不因本次修订重写。
