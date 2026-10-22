# 首次执行前固定的工作单位账单

本账单在首个产品测试执行前固定。只解释设计§5.1下本候选的操作拆分，不改变固定费率、cap或域。每个集合C(n)=查询1+next(n+1)+key(n)+保留(n)+sort预约(1+n*k)=3+3n+n*k，k=ceil(log2(max(2,n)))；C(0)=3，C(1)=7，C(2)=11。排序内部比较包含在预约中，不再次按实现比较次数收费；计划引用读另计。

单NodeShape、单property、单minInclusive合法date bound：

- 关联24：nodes C(1)=7、node引用1、target C(1)=7及引用1、property links C(1)=7、保留node计划1。
- bound30：properties C(1)=7及引用1；min C(1)=7、bound引用1、类型分类1、原词法7与库值1、保留bound成员1；空max C(0)=3；保存property→bounds计划1。故bound阶段54。
- value固定16：node计划读1、link读1、bounds计划读1、path C(1)=7及引用1、focus缓存查询1、focus集合C(n)的常数3、缓存保留1。
- 每个空path focus：focus收集3+k、focus引用1、空values C(0)=3，合7+k。n=43460时k16，每个23。
- 一个focus的m个date值相对空集合增加：values收集3m+m*k_m，加每值value引用1、bound引用1、类型分类1、bound域/库8、value域/库8，合m*(22+k_m)。6值150，8值200。

公开真实输入n43460，分别在两个focus放6/8个互异合法date值：54+16+23*43460+150+200=1000000。预期真实Validator1、true空报告、余额0。相同图私有降余额为999999是另列故障注入，最后1票操作前拒绝、Validator0；公开再多一个focus需要1000023票，固定cap拒绝。原子费用由observer只委托真实charge并RLE记录逐次成功金额/次数/阶段，失败单列，不能从actual回填预期。

D1每份focus缓存C(20000)=360003。100个同targetClass关联按固定Node/Property/Focus/Value序排；最早path的非Z date先域错，最晚path到达之前资源耗尽。每组用原序/逆序/固定旋转的同RDF三种文本，实际解析图hash/首错误阶段/费用/RLE相等。此票仅界新增preflight；不声称库CPU、native对象、worker或H证明。

独立oracle在执行前纠正了原拟2/3值方案的算术：2值应46而非48票，原总额999998不是真1M；未将该草稿作为运行候选。采用其建议6/8值算术解，但24/30/16仍须由本候选静态与真实observer共同核验。旧测试v1未知参数冲突已按总控单参数授权变v2，具体原件/授权/精确diff保留在inputs和最终产品diff；原SCOPE断言不变，新测试另验合法v1+None是TEXT_TYPE_INVALID。
