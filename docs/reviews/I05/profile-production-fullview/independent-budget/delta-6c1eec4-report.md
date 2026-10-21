# 6c1eec4 独立预算 delta

结论：**本次 delta 通过，BR-F01、BR-F02关闭**。首审固定原件保持；结论仅涉及实际四路径修复及必要上下文，不替代指定双模型、全仓check、真实Job/selected/worker/H或父I05验收。

产品 `6c1eec41091a997f898cb448bfc7d4000c154307`，上一固定产品 `f677d8a3a642ef7ac7bf389218d43564762bcd9a`；工作树不变。完整139项current=Git=新candidate bytes/SHA已独立核实；130readonly仍等adoption，另外5writer亦逐字等f677。相对f677仅以下四路径变化（82+/12-）：

|路径（packages/engine/ 下）|bytes|SHA256|
|---|---:|---|
|src/ontolearn_engine/semantic_profile_input.py|40378|f4d76b68e6bd5f27d4e1c0ee7b26435117b1dd762a4b2a16503d41afd1841f74|
|src/ontolearn_engine/semantic_profile_production.py|10975|00822bb6851a25f8ca6c47cba73d22483b10694161a2732337e1a0a2bdb56b97|
|tests/test_semantic_profile_input.py|12085|eaceece4cc903ee6b46abcad809a02a8cebb376573ad801b4175d4fa59fb70cc|
|tests/test_semantic_profile_production.py|11705|ad116e7e66cdad97c49e6fdf772042bf188d91f4ff53dbfdbb575ac6f7b04cb0|

准确清单、新candidate身份及首审所有原件未变核验见 delta-6c1eec4-inputs.json。完整git diff逐hunk读取；没有改产品/旧证据/环境/分支/索引。

## BR-F01关闭：票据前移且不增总额

production.py:98–115：enter stage6后立即debit hash 4M，发生在任何projection/三次摘要委托前；stage7的旧4M debit已删除。stage8 Catalog仍用原按实际len先扣 `_hash`。五个原摘要的来源界是 input+source≤2M、defs≤M、payload+rows≤M；最后一项的联合长度门在两次wire摘要之前，因此4M覆盖实际五次，失败路径也不会先执行无票摘要。无第九stage、无重复收费或扩cap，原C五域默认公式未变。

实际固定旧反例（674 hash cap）重跑：stage6 MATERIAL_LIMIT/hash，stage6/7实际摘要调用0，state failed/context为空。4M块差1（674+33554432−1）也先拒绝，调用0。实际整次 hash exact33555208成功，记录五次委托的 `used.hash=33555106`（已含4M），最终usage33555208；正常未降限对照成功。原首审used674时先跑三个摘要的行为已消失。

原件 delta-6c1eec4-original-counterexample.stdout.raw/对应argv记录。第一份 delta-6c1eec4-probe 原样保留：它沿用旧自适应算法，从“第一次委托前used”取低限；修后该值已含4M，所以其33555106不是原674反例，合法跑完五个已付摘要后在stage8 Catalog再扣102时失败。该诊断不判产品缺陷，已用另外的新文件固定原674和差1，不覆盖前次证据。

## BR-F02关闭：控制票先开户，builder先reserve

input.py:74–95不再创建checked list/复制tuple；保留原exact override tuple身份。≤5项，每项先exact tuple2、exact str白名单、exact int非bool、非负，才重复检查先前已经验证的项；新内层range最多10次比较，不对未校验foreign成员调用len/iter/hash/比较。仍拒绝重复、bool和6项tuple。

begin:97–131先要求new并立即转running，再exact Q/D/N及范围门；只从固定参数和≤5项已验证override计算effective objects lowercap。control_limit<64在创建六个计数/阶段容器之前拒绝。通过门后，live/peaks直接初始化objects64；不是先分配再reserve，也不加64到cap。0/63无法借容器初始化取得超界预分配，失败后原prepare清理将ledger设failed，不能重新begin。

64控制票的归属是固定bootstrap元数据，既不是raw/source/native数据，也不是可重复使用的对象余额。按比现有容器票更保守的“每dict对象+键/值引用、每stage list对象+8引用，并另计五个新caps整数”计数：caps≤16、used≤7、live≤5、peaks≤5、stage arrays≤18，总51；剩余13覆盖这些固定构建的iterator/短暂单元素乘法builder/固定计算临时对象。dict键/域元组为模块常量；调用者已存在的exact ledger、override tuple及其成员不是这里新复制的容器。构造验证和开户谓词是固定≤5域控制前门，不是按用户数据大小遍历的额外stage，也没有把它说成大数据遍历已扣traversal。新代码的注释将“effective lowercap检查通过即开启控制票、初始化64只是记账”写明，避免后置补票解释。上界是逻辑对象/引用合同，不是CPython allocator/RSS精确字节。

input.py:469现在先reserve原 `4*len(rules)+len(disabled)+4` 再ids=[]；production.py:59现在先reserve原4objects再slots=[]。既有后续append扩展票和捕获record票不变，没有把一笔票同时支付两个builder。新未发现绕过lowercap、重复begin、foreign协议或新数据大小循环的路径。

实际0/63：caps/used/live/peaks/stage_visits/stage_bounds六者全None；原tuple身份保留。64：cap=live=peak=64，再reserve1拒绝、live仍64。新产品测试还实际验证0/63失败终态及不可复用。保留旧cap公式，未触及restore_budget、16c、原L或其他130readonly。

## 验证和生命周期

独立用本树只读 `.venv/bin/python -B` 运行上述probe及两新增测试文件：**54 passed,exit0,1.00s**。完整argv/cwd/开始结束/退出/无超时/双流SHA在各 delta-*run.json/raw；仅PYTHONPATH和禁止pycache变量指向本树，没有安装依赖或借他树环境。probe源保留.py.raw，无新.py参与全仓ruff。

正常C成功对照的全局usage与首审完全相同：hash33555208、scan_copy872478369、traversal402655275；改变是hash发生时序和控制容器前门。4M从stage7挪stage6不会改变stage traversal16J上限，失败仍由外层清capture/checked/record等局部，公开finite error不带原异常链。没有改receipt字段、retention_owner、转交或清理代码。

同probe再次实际fullview smoke成功：J98723、外7/内15，R usage/peaks/retention与f677相同；returned retention.objects202953、scalar1496642，operation terminal live0。restore.py/restore_budget及其测试未变，所以首审43项fullview专项依据仍绑定相同源码，不无变化重跑全套。未发现新同时持有或预算池转移。

因此BR-F01与BR-F02在此固定delta关闭；首审其余有限结论保持。不把root报告242专项、正常npmcheck/38exec或实现者证据登记为本轮独立运行；本轮没有重跑全仓、生产/GUI/网络/模型，也不量化性能或声称全进程内存界。
