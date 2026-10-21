# I05 → T01：6c1 对象持有分量与最小私有接口响应

2026-10-22。结论：**固定6c1目前不能给出已闭合的实际H数值上界；现有C票不能直接代入H。可以交付部分有限结构式，以及未实施的lower-only私有envelope设计和精确writer申请。** 不调高cap，不把16Mi机械减半，不宣布8Mi不可能，也不把所有worker责任转给I05。

本轮只读Git文本/stdlib AST与hash，不import或执行产品、测试、worker、SQL/native、GC/对象采样、allocator/OS研究或GUI。唯一依据为实际消费的 `6c1eec41091a997f898cb448bfc7d4000c154307`，不是91e或当前工作树产品。root请求和13392B T01分析均全文读取，后者SHA核同 `10238c74616ab3b05a990ca830c82ce496e82630217cbbfc3b9b097678be6aaa`。本报告涉及的定点源身份见 `sources.json`；没有重审旧139全包、257MB过程或预算ZIP。

## 1. 两处C事实成立，单位和寿命不能直接映射H

以下源位置均指6c1的 `packages/engine/src/ontolearn_engine/`。

- `semantic_profile_input.py:96–128`：`A=Q+D+3M`，`M=8388608`；C的objects cap为`8A+2048N+4096`，ledger先开64个逻辑控制项。`397–436`的`_encode`先建safe投影，再于408行固定reserve `M+64`后委托iterencode。因此到该预留点至少为`64+M+64=8388736`，其余live非负。它不是先分配了8388736个实际对象。
- `semantic_profile_production.py:98–116,209–227`：projection前`8M`、rows前`2M`、catalog前`2M`，成功路径三票未退，合计`12M=100663296`。`_encode`临时票的finally只回到其进入时live；不会退掉此前production大票。成功`transferred()`不清live。
- `semantic_profile_input.py:522–607`还在json.loads前预留`8*len(data)+64`，object_pairs_hook是在decoder已形成pairs后才校验字段。原C是独立保守收费/持有票，不是实际H allocator；原17L的work也不是objects。不存在本轮已证明的`H=C`或统一换算系数。不得修改C预留、工作收费或用新H抵销它们。

## 2. 能静态证明的结构分量，以及它们尚不是什么

为了避免偷换单位，以下`U`只计**明确的应用容器壳、占用字段/元素引用和说明中明确的新标量壳**。它不计CPython容器余容/表、frame/iterator、字符串内部表示、第三方/native对象或永久导入基线；因此不是合同H。每个分量还需固定实现的`κ`和委托scratch界才能映到H，未证明的系数保持未知，不能填1。

| 分量                     | 可证明的有限式/前提                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | 未闭合委托与同时持有                                                                                                                                                                                                                                                        |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| material/typed codec     | `ProfileMaterial`13字段；四个preimage/material bytes各≤M，input+source≤2M；rules≤100、records≤100000。对实际精确类型树可计`V`节点、`E`字段/元素引用、最大深度32及各schema实例数，`U_tree=V+E`是显式树壳/引用的保守出现次数模型，aliases按出现计、不据相等值去重。                                                                                                                                                                                                                                                   | json decoder的text、pairs、tree与typed重建并持；`_syntax_native`展开kwargs临时dict；raw definitions与canonical重编码仍可能并持。bytes长度不能代替这些数量或native委托系数。                                                                                                 |
| Graph/context            | 成功parser graph、asserted副本、closure各自T≤100000；occurrence≤300000，词法sidecar scalar≤262144。Turtle sink在`semantic_turtle.py:617–619`先add后检查，故拒绝瞬间还要覆盖第100001条；records分支先限100000条。prefix/namespace/parser元数据不能只由T推算。                                                                                                                                                                                                                                                        | 输入Graph、`_profile_graph`的asserted copy、closure、context terms/occurrences/frozenset、registry snapshots、旧/新disabled context可能同时在场。RDFLib Memory索引、term/解析器和namespace分量需要`κ_graph/κ_term/κ_parser`；当前没有数值证明。                             |
| closure proof membership | 令A为初始asserted triple数，W为原GraphBudget全程work上限1000000。初始proof sets成员出现次数为A；每次新增basis的成员数≤输入sets长度和，而`_GraphBudget.union:374–376`在创建set前付这项work。故所有已保留proof sets的成员引用总数`P_leaf≤A+W`，并非粗暴的A×T。                                                                                                                                                                                                                                                        | 只界proof-set成员引用。set壳/余容、输入list、union scratch、sort key/cache和Graph仍需另计；不得把`A+W`当完整native结果或H。                                                                                                                                                 |
| matcher/native           | 原17L全部保留；bindings/firings/trace等按原`_PROFILE_POOLS`分配，不按N重复扩大。`_finite_matches:470–484`先构造updated，再检查next_matches容量；故需覆盖旧matches、next_matches及额外pending updated，不能只按成功列表长度收费。                                                                                                                                                                                                                                                                                    | compile plans、budgets、originalMatches、controlled list/tuple、prepared batches、firing/evidence/basis引用和数值运算临时值均并持；`κ_mechanism`及异常scratch尚无H证明。                                                                                                    |
| safe投影最终结构         | 对成功完成的safe投影或已付entry charge的失败前缀，令V为相应`value()`访问节点数，P为实际`charge.nodes`，则V≤P≤1000000；未获charge的失败调用和scratch另计。17种获准dataclass字段数均≤17。每节点自有最终结构贡献≤`6+2e`，e为其直接子访问数：list/dict更小，dataclass为`3+2f`，int包装≤4，bytes包装≤6。访问森林`Σe=V-R≤V`，故`U_safe≤6V+2(V-R)≤8P`。719–722行同一个projection累计result/source/definitions；另有695行structured records输入的fresh P_in，以及production227行catalog的fresh Pcat，必须按真实阶段分别计。 | 这只界最终safe容器壳/占用引用/新hex字符串壳，输入scalar已在native根计，不重复当新对象。payload/wire/implementation外壳与digest对象不由这棵safe遍历生成；dataclass中间dict、fields/approved tuple、UTF-8临时bytes、递归frame和encoder scratch不在8P内；不是`H≤8P`或8Mi证明。 |
| 实际production rows      | 实际路径是`semantic_execution.py:737–745`，不是通用`_rows:299`。令c为`encoded.decode`字符数，`c≤len(encoded)≤M`，`r=ceil(c/8192)≤1024`。外层list壳/引用r、r个内层list壳/引用各1、最多r个片段str壳合计`U_rows≤1+4r≤4097`。                                                                                                                                                                                                                                                                                           | serialized整串、源encoded bytes、safe/native/payload、迭代器及rows encoder仍同时持有。`len(encoded)+len(rows_encoded)≤M`在两者生成后才检查，失败峰值不能预先使用成功合计M；两次encoder各自M界和既有并持都须覆盖。                                                           |
| capture/返回根           | `CapturedSlot`3字段，`ChildAllocation`3，`OriginalAllocation`4，`ProfileComputation`14。令K为实际capture slot数（成功校验K=max(1,len(raw_rules))≤100）。slots list壳/引用与slot壳/3字段为`1+5K`；allocation子tuple壳/引用与child壳/3字段为`1+5K`，另有rule-id/disabled tuple、allocation壳/4字段、computation壳/14字段及receipt根。                                                                                                                                                                                 | 这些是外壳/引用式，不含字段指向的完整对象子图。不能漏material、native、actual definitions/catalog、五份输出bytes、wire(payload/rows)、receipt；capture和outcome的别名要按持有者分别记引用。                                                                                 |

这些式子覆盖成功前缀和相应失败前缀的显式结构；`8P`尤其不包含生成过程的scratch。尚未得到所有未闭合委托的H系数，**本轮没有可合法代入8Mi的最终数值和式**。

## 3. 可组合的峰值形式与真实寿命

对实际actor，先由共同所有权模型给每个分量定义同单位H函数：`H_j(s)=κ_j(structure_j(s))+scratch_j(s)`，不得由caller填写大小或默认系数。I05可交的组合形式为：

`H_I05 ≤ B_I05_import + max_s [Σ H_j(s) + H_I05_failure(s)]`。

其中s至少包含下表；同一个阶段内相加，不能把各自最大值误认为互斥。

| 阶段                    | 必须并持的根/委托                                                                                                                                                                                                                                    | 能证明的转交/释放点                                                                                                                                                              |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| decode/prepare          | caller原bytes/typed输入的I05别名；decode text+pairs/tree；typed规则与sources；projection/canonical bytes；各自ledger/receipt                                                                                                                         | `_encode:432–436`丢safe/output/encoder/chunk/data局部根，返回bytes仍在caller；`decode_rule_definitions:674–680`丢其tree等局部根，RuleDefinitions返回内容仍活。不是live归零证明。 |
| reprepare/graph/reason  | 原material和新checked同时；input/source/definitions校验副本；Graph/context registry/disabled旧新context；structured records在graph/context生成后还调用fresh P_in及encoder重建original_bytes；asserted/closure/proofs、plans、matches、native正在形成 | production用字节相等校验，不是object identity复用证明；`_same_bytes`成功不能据此扣掉相同内容的另一对象。callee返回只消除其局部引用，不代表所有alias或registry持有已消失。        |
| projection/rows/catalog | checked/native、safe_result/payload、source/defs编码、encoded/serialized/rows/rows_encoded、actual catalog投影、allocation/capture/receipt                                                                                                           | `_execute_profile`未提前清全部这些局部根；catalog在它返回后运行，但wire/capture仍保payload/rows/native。仅字段确已转交或最后持有根已消除且委托cleanup已闭合才退H。               |
| 返回/失败               | ProfileComputation的上述完整根；失败期间error/context/traceback/frame的持有；caller/T01仍活别名                                                                                                                                                      | `capture.drop:131–135`仅清capture自身字段，成功outcome继续持有；production `finally:251–258`清局部根，`transferred()/failed()`只是C状态。不能据此签实际H释放或GC。               |

`semantic_turtle.py:492–560`的`_CONTEXTS`含Graph/terms/occurrences/frozenset/snapshots等强引用，context自身由weakref跟踪，expire才移除entry；disabled重绑可另发context。必须计注册表内容与callback/frame持有，不能把“有weakref”当作已释放证据。I05没有显式给整个失败链的实际frame/native缓存H界。

I05永久导入分量也不能省略：`semantic.py`导入RDFLib/pySHACL等；`resources.py:14–31`加载contract模块、registry bytes及implementation；typed dataclass、模块全局、context registry基座等按每actor计，除非T01有严格同一对象归属证明可以避免重复。固定lock/版本只锁实现身份，不证明这些对象数量。T01文中CPython3.12.12是其运行时描述，本轮未重新验证实际child build，更未用版本名称证明解释器/native heap上界。

T01仍负责 `B_T01 + B_I05 + max_s(H_T01(s)+ΣH_I05,j(s)+H_failure(s))≤8388608` 的wholechild闭合、实际process绑定及同库全部active/retired/failed/unknown actors和parent并持≤16777216。I05只交自己分量与明确前置；parent book/channel/cleanup、bootstrap/monitor/receiver/transport、admission/reservation及实际终态由T01维护。原scalar/物理监督不变，也不代替对象证明。

## 4. 最小lower-only structural envelope私有设计（尚未实施）

建议独立的私有版本 `i05-object-envelope/1`，并明确其当前只是一项接口提案；原MATERIAL/C/17L/semantics版本和原计算语义不自动改变。

1. **任何实际decode/encode/projection之前先有结构plan。** 对实际exact bytes roles，用有界UTF-8/词法扫描计算JSON节点/字段/数组项/深度/字符串宽度/最大token、typed schema实例与边数；原typed输入先exact type/字段grammar，再按出现次数计数，不能调用foreign len/iter/协议。扫描自身的定长深度栈、计数器和hash scratch也需先有对应分量界。仅有后验tree或事后dict/receipt无效。
2. **实际绑定而非caller声明。** plan绑定真实input/source/definitions的domain、长度、原始bytes digest及definition material；N、原17L各actual slot及disabled/zero-rule情形；原parser身份、6c1源/固定lock/runtime-build与新接口实现hash、capture模式。只复用原始字节或同一精确类型根，不以相等摘要冒认同一对象。parent的plan描述是数据，child必须从实际收到的原件重建校验；不能单靠传输dict、bool、exact class或版本字符串发行可信H。
3. **作用域guard贯穿发生点。** I05内部从已核原件派生私有ScopedEnvelope，不公开接收caller自报counts/H值的构造器。T01另把它与自己真实actor/reservation生命周期连接；I05私有类型不是Job/来源认证。decode→syntax_native→prepare/_encode→production reprepare→graph/reason→projection/encoder→rows→catalog/capture必须消费同版guard。各阶段先从实际结构与已证明委托系数预留，再调用原函数；guard自己、duplicate roots和transition并持也计入，失败先付仍不退工作。native/capture阶段不能仅用最后safe tree计数补证先前峰值。
4. **必须覆盖opaque与失败。** 现成json.loads/iterencode、RDFLib/parser、数学及runtime委托若没有适用κ/scratch证明，就标unknown并保持未准入；不能只因为扫描得到V/E就声称C backend满足。若拟改受控codec以消除某项opaque委托，须另授具体实现/兼容证明，不能本窗暗换。异常frame/registry/返回alias未证明结束时保留相应分量；返回receipt只记录已执行的预付/转交，不授过去执行许可。
5. **lower-only和受理域。** 所有guard额度只能取既定actor/library残余额度的下界，残余额度由T01真实组合提供，不能提高原cap、修改17L、截断输出或机械减半。若无法证明覆盖当前完整已受理域，不得把全拒或缩小到样例域称为等价修复；新有限版本/支持域改变须另授，当前门继续保持。不得减小原C收费以让H过门。

最小接口形态为 `plan_i05_envelope(actual_raw_or_exact_typed, fixed_pin)` → 无权限的结构descriptor；`bind_i05_envelope(actual_roots, verified_plan, actual_actor_budget_binding)` → 仅内部ScopedEnvelope；原实际codec/production入口接收私有guard并在每个发生点消费。这里的actual_actor_budget_binding须由T01正式接线提供，本设计不伪造它，不给caller传一个expected dict后直接进入计算的旁路。

## 5. 具体writer申请与继续保持的门

本轮**没有任何产品writer**。若root安排下一阶段，建议先批准可独立验收的codec/projection分量接口，而非宣布wholechild已闭合：

| 候选writer                               | 唯一拟改内容/仍需前置                                                                                                                                          |
| ---------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 新 `semantic_profile_object_envelope.py` | 私有版本/结构scanner与分量plan/发生点guard；不能发行Job或actor权限。先证明scanner自身界和每项κ出处；未知委托不签H。                                            |
| `semantic_profile_input.py`              | `_read_syntax_json/_syntax_native/_project/_encode/_prepare_profile_material`在解析/展开前消费同一guard，转交/失败根明确；原C和完整grammar/输出不变。          |
| `semantic_execution.py`                  | `_ProfileProjection/_profile_json_bytes/_execute_profile`发生点消费guard，按实际one-cell rows及源/defs/catalog并持；旧默认执行不接新公共参数。                 |
| `semantic_profile_production.py`         | 真实material再校验、capture/allocation/返回与失败根转交，禁止把capture receipt当准入。                                                                         |
| 新专用测试 + 新过程prefix                | 仅未来获授后：全原受理域的符号覆盖、先付/失败前缀、同一原件/实现/actor绑定、重复/外来guard拒绝、alias不早退、C/17L不改、完整输出无截断；本轮未创建或执行测试。 |

上述最小申请**仍不解决Graph/native/permanent-import分量**。若要真正闭whole H，另需对 `semantic.py` 的`_GraphBudget/_finite_closure/_finite_matches/_profile_reason`、`semantic_turtle.py` 的实际parser/Context registry、`quality/rule_firing.py`的compile/evaluate及其固定数值依赖逐项给适用分量证明；需插发生点guard时再精确申请这些writer，不能借codec申请默认扩大。`quality/rule_profile.py`原17L保持只读。

最直接的缺口清单是：`B_I05_import`、decoder/encoder的κ和scratch、Memory/term/parser/namespace系数、机制临时值/异常界、projection scratch/容器运行时系数、registry/所有alias最后释放的可组合证明。这些均不是已知为零。其余T01自控部分不交由I05代写；不重启被拒的SQLite资源接口线，不改Store/profile启用或物理HOLD。

本响应可以用于下一精确窗口讨论，不能用于降低worker票、启用新process、签准8Mi或关闭父功能。Q6不重问，date未选择，无新Goal、push/PR/merge。
