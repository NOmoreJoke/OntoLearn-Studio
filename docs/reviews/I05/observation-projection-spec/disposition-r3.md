# R2-01 的 R3 最小作者处置

R1/R2正式Fail全部保留；作者不自定R3 Pass。R2报告为18390B / SHA256 `cf13c0d1b4fd7fad1aa0f6856a0db9e9b177a7e2da1137b8e7a0d362fca3aaa3`。本次实际revisionBase为 `755326a26306f5bce0f36c172bd4994c7340f235`，其亲代 `d1a736bae1c36d3521d1b0c21037fb566f52e14e` 保R2审查原件/root receipt，755另保root空白差错说明。原base `5f910b52c69d86a1076b2032e5d3c63e715947f3` 与历次候选/过程ref不重写。

作者已全文读取R2 report/proof/root receipt及root whitespace receipt；proof全部247命令记录解析，230条重复Git身份记录逐字段与实际固定Git字节核验承接，17条其他命令和完整结果读取。没有执行旧审查脚本或覆写其proof，没有读费用WIP、产品算法或actual。

## R2-01：本端canonical wire先于数学集合

修订仅改变既有 `model.py/spec.md` 两个tracked设计文件，增加R3测试/证据，不改schema、cases、纯输入、37完整值/math、旧测试或任何旧报告/双流/manifest/receipt。当前状态为“最小修订已完成作者验证，待root指派独立R3 delta审查”。

`matches` 现在固定按 expected schema→observed schema→expected全graph槽wire gate→observed全graph槽wire gate→原同artifact全域共享映射执行。每端使用其自身layout，`canonical_graph_slots/canonical_graph_wire` 核该端原标签、原词法的完整三元组N3 key升序、完整RDF identity唯一性和既定typed/N3表达。门只读输入，不能先set化或排序/删别名来修复wire；language在identity key中仅casefold，wire排序key仍按该端原拼法。

完全相同JSON重复仍由schema `uniqueItems`先拒，这个既有有效门没有被否定。两个不同JSON的EN/en同RDF identity别名即使已排序，也被新门拒绝。graph之外的when/heads/evidence/source occurrence没有被全量排序或去重，重复位置和尾项继续保留。两端都canonical后才做共享BNode映射，因此左a→x/b→y、右p→y/q→x可用a→q/b→p通过，不退回逐下标raw exact。

表达门使用既有有限生成格式：typed exact字段/类型、UTF-8、IRIREF/label和language-datatype关系、RDF三元组位置；N3只读取本serializer生成的一个token并做n3 roundtrip，不执行Turtle/产品parser或第三方库。显式xsd:string冗余拼法、非规范Unicode escape、未转义换行/tab、非法IRIREF等即使schema仍放行，也不能作为canonical wire。数值/date词法不做值转换、不宽化datatype政策；raw/source原文及quoted lexical不重写。

原 `projection_identity_equal/identity_domain_equal/graph_isomorphic` 继续是数学身份关系，可描述同一集合的不同枚举；不是wire接收器，直接identity-only结果不能oracle-match。完整consumer必须调用 `matches`。这一区分保留R2抽象关系测试的含义，不追称其已覆盖wire；新R3完整入口反例单列。

## 新字面反例和实际回归

`selftest.py/selftest-r2.py` 原字节不变，R3 runner承接原32方法。首次R3为32+8=40方法actual exit0，随后按root提醒补schema仍放行的表示反例和typed交叉正例，第二次32+9=41方法actual exit0；两次原分离stdout/stderr分别保留，不覆盖首次记录。

- 全37原expected的85个graph槽逐槽通过新wire gate，完整golden无需修改。
- rdfs/cycle rdfs8、domain-depth2末basis3、scope/fresh facts9分别逆序：schema合法/identity可相同，但expected或observed任一端这样改变均拒绝，输入不被自动修复。
- rdfs/rules/facts/basis的完全相同JSON重复仍由schema拒绝；已排序EN/en别名在typed/N3两种图均被新identity-unique门拒绝，单个合法EN拼法仍与en按身份对应。
- typed/N3各端自身canonical的交叉BNode改名正常通过；反转某端原wire仍拒绝。
- 有序重复inputs/evidence正常保留，删除任一尾项拒绝；quoted lexical、numeric01/1、raw/source边界继续由原32和新字面测试验证。
- 显式xsd:string与simple literal、非规范escape、未转义控制符、非法IRIREF等schema允许时完整wire入口仍拒绝；不泛化为全RDF库实现。

这些都是detached serializer数学反例，不是产品成功对象、新业务输入、capture/来源或资源准入证明。所有旧未证权威、真实库/费用/runtime/旧metadata/source-package门和wholeOracleComplete=false保留；R1安全stage/API/language/shared mapping修复不变。

## root原始diff空白与真实检查边界

指定不可变 `r2-independent-full-diff.stdout.txt` 为128276B / SHA256 `13c4471bc5518f354b8315220c14b8fbd5f722c722075ed93c1fc29183b01477`，包含原始diff上下文空格。原件不trim、不format，root的空白检查/依赖未检查误commit说明原样保留，这不是产品失败。

R3实际全原base diffcheck仍exit2，诊断只指向这一件旧raw transcript；**没有全check绿**。另做精确只排除该单件的范围检查exit0，以及本次revision755 delta检查exit0。实际argv、exit和双流在 `r3-validation.json`；full-check stdout用lossless UTF-8 JSON string保存，text反编码字节/SHA等于原流，未trim，避免另制造一份带上下文空白的raw文本。这个编码不改变旧raw原件。

完整candidate仅在检查结果已读取、唯一历史失败来源核定、精确排除检查及新delta检查完成后提交；不让失败命令自动触发依赖commit。新manifest-r3与实际提交后另名receipt不覆盖旧身份，不预填未来ref，明确self排除。提交后完整current=固定Git=SHA、index空和仅保护AGENTS M再回root；独立R3审者尚未给出结论。
