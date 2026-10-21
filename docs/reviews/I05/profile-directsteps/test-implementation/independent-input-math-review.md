# 独立纯输入与数学预期核验

本报告由未参与产品实现的 directsteps 独立测试作者编写。仅使用固定 6c 输入、合同和手工推演；没有运行候选产品，没有从 actual 反造 expected，也没有将 expected 传入生产。作者只写新测试及本过程前缀。此报告证明预期来源和覆盖边界，不签署产品实现通过。

## 固定依据与核验身份

测试树为 `I05-directsteps-tests`，分支 `feature/weekly-i05-directsteps-tests`，起点 adoption `78e9cf7f26dc039e99ec6725d7de8a396d1298d2`。原产品 139 路径固定为 `6c1eec41091a997f898cb448bfc7d4000c154307`，base 为 `5f910b52c69d86a1076b2032e5d3c63e715947f3`。`input-readback.json` 保存所有 raw 的完整读取与字节/SHA，以及 139 路径逐项当前/Git核验。新测试不是 T05 原五图的覆盖声明。

全文读取的正式窗 5942B SHA `9e9091f4f5f565e437bc45ee74476cb5f77e19858fcef783892f54d4adf50f55`；固定合同 34958B SHA `c947430801e6b3cca113c15a856704c3d5bed418efa9083d67819830a6961fba`，来自 T05 `057d2d96aaaac92d59f593678fc265fd13eace78`。另已读 budget/source 申请、139 清单、latest AGENTS/common 原件。条款行号均指上述 raw 合同：§2 L24–41、§3 L43–82、§4 L90–127、§5 L129–149、§7A L175–185、§8 L221–226。

精确源码锚点是固定 6c 的 `packages/engine/src/ontolearn_engine/semantic.py`：`_key` L215、`_finite_closure` L385–448、`_profile_term` L755 起；真实叶发行在 L958–973，实际 RDFS union/evidence 在 L1073–1087。只读这些旧发生点并未替产品编写实现。新增 private ledger/sink 的接口与错误名来自主线及模块作者同步；实现尚未供本树，接口适配和真实运行仍待主线。

## 预期表示与四个实际规则向量

下表中 `t`=`rdf:type`、`sc`=`rdfs:subClassOf`、`dom`=`rdfs:domain`、`ran`=`rdfs:range`，其他值全部是完整 `urn:` IRI。测试函数直接构造真实 `TermInput` records，经原 `prepare_profile_material` 和新实际生产 API；下列 expected 仅作断言。`L(T)` 表示旧真实叶 ID 的确定性预期（既有固定哈希算法在测试中计算），`S(n)` 表示已插入 step n。没有将符号或预期叶 ID 喂给生产。

| 输入 records（按原始顺序） | 手工推导的完整步骤序列 |
| --- | --- |
| `(x,t,A),(A,sc,B)` | step0=`rdfs9-type-via-subclass`，result=`(x,t,B)`，premises=`[L(x,t,A),L(A,sc,B)]`，depth1 |
| `(p,dom,A),(x,p,y),(A,sc,B)` | step0=`rdfs2-domain`，result=`(x,t,A)`，premises=`[L(p,dom,A),L(x,p,y)]`，depth1；step1=`rdfs9-type-via-subclass`，result=`(x,t,B)`，premises=`[S(0),L(A,sc,B)]`，depth2 |
| `(p,ran,C),(x,p,y)` | step0=`rdfs3-range`，result=`(y,t,C)`，premises=`[L(p,ran,C),L(x,p,y)]`，depth1 |
| `(A,sc,B),(B,sc,C)` | step0=`rdfs11-subclass-transitive`，result=`(A,sc,C)`，premises=`[L(A,sc,B),L(B,sc,C)]`，depth1 |

独立推演：候选只能读取本轮开始的 closure。domain-depth2 第一轮只有 domain 候选，x:A 随排序插入后本轮不重新枚举；第二轮才有 x:A 与 A→B 的 type 候选，故 step1 必须引用 step0 而非叶，depth=`1+max(1,0)=2`。它的三叶 union 与两个直接前件不是同一字段。其余三个图第一轮各只有一个新结果，终止轮只枚举重复候选，不增加步骤。无规则反馈，所有原 L/union 路径仍需实际 API 保留。

另有 literal range 护栏向量 `(p,ran,C),(x,p,"not an IRI"^^xsd:string)`：真实 range 发生点要求 subject 为 URIRef，故没有新 RDFS，`directSteps.steps=()`；仍有两个真实 seed。空步骤是显式载体，不以缺字段代替。

## 首见证排序、稳定性与重复候选

同规则竞争输入是 `(x,t,B),(B,sc,Z),(x,t,A),(A,sc,Z)`，以及该 raw 顺序完全反转。两个候选均 result=`(x,t,Z)`、depth1。原排序先比相同 result，再比有序 premise tuple；第一前件 `(x,t,A)` 小于 `(x,t,B)`，故首 witness 必须为 A 路径，第二前件是 `(A,sc,Z)`。两轮各枚举两个候选，共四次实际 `candidate`、只一次 insert；重复和未选中的候选仍计 D。反转 raw 输入不能改这个选择，也不能把两个前件排序成无序集合。

更强的跨规则向量是 `(x,t,B),(B,sc,A),(a,dom,A),(x,a,y)`。旧 subclass 循环先生成 type 候选 `[x:t:B,B:sc:A]`，后面的 domain 循环再生成 domain 候选 `[a:dom:A,x:a:y]`。result 同为 x:t:A；比较有序第一前件时 `<urn:a>` 小于 `<urn:x>`，因此实际首插入必须选后生成的 domain witness，depth1。真实候选生成顺序应是 `[type,domain,type,domain]`，而载体只有一个 domain step。这明确区分“生成时捕获”与“排序后首插入时捕获”。

若两个候选的排序键完全相同，排序保持旧稳定生成序；测试不增加 rule/depth/source tie-break。对于这四个有限模板，result 和两条完全相同的有序前件已确定模板语义，无法凭空构造带不同实际语义且全键相同的真实 IRI 向量。本测试保留原 key 的可观察选择，不杜撰一种新的 tie 规则。

## late-shorter 在当前完整成功闭包中不可达

合同 §2 保留首次 witness，即使以后有较短者也不覆写。这是防御不变量；不能因此声称现有五图或本次真实图已经出现较短后发现。

固定源码 L393–395 在每轮开始新建 additions；L403–429 完整枚举四类模板，只读 round-start closure；L431–447 才统一排序并插入。令 seed 的最早轮次及 depth 为 0，round r 表示第 r 次完整候选枚举后插入。归纳证明如下：

1. 第一轮的前件只有 seeds，因此任何新结果首 witness depth=1。
2. 假设所有在轮次 <r 首插入的结果，其 depth 等于最早插入轮次。round r 的所有前件最迟在 round r−1 已存在，因此其 depth≤r−1。
3. 若 round r 新结果的两个前件都在 round r−2 之前已存在，同一固定模板在 round r−1 已完整枚举；当时结果若尚不存在就会插入。因此这个结果不可能到 round r 才首次出现。
4. 所以 round r 新结果每个实际候选至少有一个前件最早在 round r−1 出现，其 depth=r−1；结合上界，选中 witness depth=`1+max(...) = r`。
5. 一个 depth=d 的可行 witness，其前件最迟 round d−1 可用，故模板最迟 round d 会被完整枚举。首次插入轮次 r 不会大于任何可行 witness 的最小高度。后续 round>r 不可能新发现 depth<r 的 witness。

此证明要求完整成功枚举、闭包单调、规则不反馈；均对应当前实际调用流程。资源中断不会形成可发布成功 carrier，也不能被包装为 late-shorter 成功例。已向主线报告，并获主线认可此精确验收边界。

受控 helper 防御测试故意绕过完整图枚举：先插入 x:B depth1，再插入经 x:B 的 x:C depth2，然后尝试以 `(x,t,A),(A,sc,C)` 两个 seed 再 insert 同一个 x:C（假想 depth1）。模块作者确认 `insert` 只供真实首插入，重复 insert 必须 `DIRECT_STEPS_INVALID`、failed/drop、禁止 finish 发布旧 prefix。该序列仅验证 private helper 拒绝误用，绝不记作真实 engine late-shorter 覆盖；真实后轮重复候选通过 candidate 观察并无二次 insert。

## seed 身份与原始 occurrence

独立 alias 图有 8 个 raw records：两条 DatatypeProperty 声明，加 p 的四条 literal（plain same / explicit xsd:string same；Word@EN-us / Word@en-US），加 q 的 integer01 / integer1。依合同 §3 L66–78：两对别名各折为同一 seed 身份，而两个整数词法不同，故真实 seed 数为 `2+1+1+2=6`。None、显式 dtype、language_raw 和两类 source 全部保留 raw occurrence 原顺序，不能为了选 N3 代表改写输入。测试逐字段比较所有 termSources 原 TermInput/source 与全部原 occurrence，并核 readonly fullview。identity 编码单独验证 IRI 与 literal 不碰撞、语言大小写同 identity、整数词法不折叠；三字段 TripleKey 以每项 8 字节大端 UTF8 长度编码，含非 ASCII/转义文本，不能 delimiter 拼接。

## 整体边界与待真实验证清单

生产与恢复都必须通过真实 API：四图完整 native/wire/fullview 签名；新 /3、finite8、schema2；外7/内16/实际非空 child11；ordinal/depth 既有 integerHex 投影；恢复禁止重新 reason/match。规则向量 `(x,p,y)` 经一条实际 rule 输出两次相同 `(x,out,y)`，roots 必须返回 firing0/head0 与 firing0/head1 两个 occurrence，不裁剪完整 view、不将 rule 输出反馈为 finite 输入。

攻击性 wire 只改变测试接收物料及相应 payload/rows digest，不改变生产输入或 expected witness：遗漏载体、末步/前件/深度、缺步/加步、加假叶、ordinals、方向、自前指、rule/result、原 union/source 尾字段、版本和未知 key 均应整任务有限拒绝。旧 /2 finite7/schema1 默认仍用真实原 API，newnative 只移除新增载体并还原版本后必须与 oldnative 全字段相等（含原 L）；旧 reader 拒新 key。Turtle 明确拒新解释入口，不能暗中补 structured seed。

所有四 D 域在 producer/restore/roots 各自实际 baseline 上取得 usage 或 peak，测试 exact 与差1；这是预算边界测量，不生成数学 expected、不供生产黄金结果。还核控制票 0/127 在容器前拒绝，128 exact begin，scan 同时计 work；完整 events 四域连续、累计单调，一次使用、lower-only override。固定 caps 是合同整数展开，不能当已实测容量。事件票、future cleanup 预付、控制票可使 failed live 非零；测试不声称物理 GC 或全部 live=0。observer 只在 actual completed/transferred/failed/receipt 成功调用后 append 有限 fee 原件，不供结果、不重算票、不留 native/PV 引用；显式 receipt fault 覆盖 observer 时无该方法事件，不补造。

四种受控 MemoryError/末 child revalidation 注入验证 finite public error、无成功 prefix、无新增 native/PV 逃逸；不制造真实 OS OOM。所有旧 tests/assert/skip 未改；没有把受控 monkeypatch 当真实成功算法或正式 Job/Store/权限链。

本树未具备新产品模块和共享接线；没有运行 pytest 或以 import failure 充测试。自己的 frozen uv 环境安装成功；最终 Ruff/format/AST 及 139 逐项不变检查见 `static-final-*`。首次 Ruff 失败 50 项及其双流原件保留在 `01-ruff-initial.*`，随后只整理新测试导入/格式。真实集成 API、预算 exact/差1、错误清理和旧回归仍须主线逐 Git 采用本提交后运行，实际费用由 `I05_DIRECTSTEPS_FEE_EVIDENCE_DIR` 每 run 独占目录观察导出。任何失败保留首原件并据实际接口适配，不以静态通过代替运行证据。
