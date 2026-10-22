# I05 source/package probe：独立静态 delta 审查 R2

结论：**限定通过本轮源码静态 delta**。R1-01、R1-02、R1-03 在新候选中静态关闭，未发现新增阻断问题。R1 原候选与 Fail 报告保持原字节；本结论不把未执行的测试、产品、source/package 等价或任何发布门写成通过。

独立审查者为 source_package_static_review_r1。仅写本报告及 review-r2-proof.json，没有改受审文件；没有 import/exec 产品、probe 或 tests，没有运行生成器、pytest、npm、ruff、formatter、构建、安装、native、DB、网络、GUI、外部模型或物理资源测量。

## 固定候选与真实 delta

- base：5f910b52c69d86a1076b2032e5d3c63e715947f3。
- 原候选：0e42a0fe349054a92817cb4d463bccdc15f6c042；R1 Fail 收件：cf15439a72207e622d2f8baa8d476a363107f5c6。
- 本轮候选：2cf0c3328de464e15a3fa9cdbfdf6aa88d0b4a64。
- 从R1收件到本轮是11件 Git delta，含新增 candidate-r2-manifest；从旧候选算是13件，多出的两件为R1报告/proof，不混为产品改动。
- 新manifest的77件 payload 共13091580 B；末核逐件 current=固定Git=manifest。manifest明确排除自身与后继审查/过程件，不能称为整个仓库的所有文件。
- probe：93848 B／b3456f021afdbd53ec8677bf317a5ffdff636b55bae760eb8b7fec6e399e41b9。
- tests：73466 B／8055c398ca4d03bb99bdec06f599db1c342b2bc6a49a0a247e2ffc54c8652da5，70个test函数；未作pytest收集或执行。
- generator：60354 B／e58dd4efd1c64952b6555b98c65271fc7e82d7b99b198d848d69f5a7c9dcde0b。

全文读回R1、r1-resolution、review-chronology，并按固定Git核所有实际delta。未变部分继承R1的静态范围，另以77件新清单重新核其字节身份。完整清单、命令结果及本报告身份另见proof。

## 三项闭环

### R1-01：静态关闭

CollectionBoundary L151–184 使用传入的同一 monotonic 起点；run_fixed_suite L1712–1884 在资产/身份/import前取得 start，并在首项之前纳入preflight耗时。每项boundary仍复用该全局start，未把120秒按call或case重置。call 在实际函数前和返回后检查；真正返回值先记录，再作返回后检查，因此First parse晚回121时不会再启动ontology/query等下一调用。

_checked_call覆盖dispatcher的parse/query/legacy/profile/shape/shacl-text/offline以及scope prepare/project、material/compute/expectation/restore/roots和B1各阶段；原canonical callable/参数没有被probe替换。原83的逐term decoder也经过边界，但不重复保存大量中间term值。scope的包装调用和offline嵌套分支均会将BoundaryStop向外传递，未归成业务已知拒绝。

BoundaryStop的130/stopping与1/deadline-boundary在外层单独处理；stage/API、实际returned、callCounts和incomplete保留。opaque调用本身仍不能硬中断，代码不宣称实际process stopped/reader join。

新增测试源码以真实parse先返回，再令同一时钟变121、累计70→121或取消flag变true；另让真实preflight返回后时钟121，要求零业务调用。断言下一canonical阶段未启动、完整18/4图保留、退出码与安全状态分别正确。这些测试未运行，静态闭环不等于其运行passed。

### R1-02：静态关闭

CollectionBoundary保存每次attempt的stage/API/start/end/returned/elapsedNs，只在call真正返回后把原真实引用加入completed。_partial_value L1646–1691只读投影这些返回值；_partial_outputs L1694–1699在失败observation中输出，stage/API同时进入顶层与安全diagnostic。unknown仍是INTERNAL_ERROR，原异常文本不被输出。

B1的First/Warm每个成功阶段都独立入completed，含完整query/reason/report及resultSerialization原bytes；Warm/shacl失败不再抹掉First或Warm先前成功阶段。未返回的call仅有attempt元信息，没有虚构value。

生产的material、实际compute、同次expectation分别记录；ProfileComputation的失败快照完整保五组原bytes/wire/native/material/definitions/catalog/allocation/capture/direct receipt。restore未返回时不会进入completed或发布partial restore view；已完整成功的restore/root若后续阶段失败，可按实际返回保留。新逻辑没有重签expectation、重造allocation或把JSON结果变成输入；九个mutation及原A1边界不变。

新增测试分别在真实First完成后令Warm SHACL抛异常、在真实producer签发后令restore抛异常，并核完整先前结果/五bytes/原allocation及expectation、精确失败stage/API、无partial restore view、无私密异常消息。用wraps保标签，成功结果来自原canonical函数；没有fake成功Graph/producer。原66测试未删除，新增4个函数后共70个。

所有新增partial输出仍经过原JSONLWriter的item/report/terminal限额；不能完整编码时仍失败而非删字段。新增保留量的真实峰值或全suite容量没有执行证据，也没有被本审查量化。

### R1-03：静态关闭

generator报告尾部改为rstrip LF后追加恰一个LF，固定报告已核非双LF；报告和来源manifest只反映该generator/过程说明变化。两份运行JSON与cf15439逐字不变，仍417 observations/320 datasets；全部原83/C13/106/54/50输入及状态未删改。

static-verify不再用单一无ref diff覆盖候选；现在分别核base→解析后的固定commit、base→当前tracked、staged、unstaged，并对每个允许文档前缀的untracked文件执行no-index whitespace check，其他untracked路径拒绝。独立实际执行base→2cf0、staged及unstaged检查均exit0；原R1的base→0e42 exit2仍在Fail证据中。

后继static-verification-r2.json不属于候选payload；本轮额外读取其最终2138 B／b1a71cf69703c78aa34753df1c56258f58a5982624bcc631d1cd825e6b791ff4，核固定ref、各diff exit0及未执行标志，并针对该最终字节实际作no-index check（exit1且stdout/stderr为空，允许的有差异无格式错状态）。没有把redirect刚创建空文件时的自检当成该JSON的最终内容身份证明。该件目前未暂存，root最终过程提交仍需对实际stage状态核验。

## 顺序与不可变证据

review-chronology的五条timestamp/recordType/含LF原record SHA已直接与指定原session核对，实际使用Python零基ordinal：R1结束06:13:00.799Z→请求全文读06:13:07.563Z→全文读回结果06:13:07.618Z→cf15439收件06:13:15.710Z→首源码修复06:14:36.850Z。本轮没有将WIP或后修文件冒称原R1通过。

本审查首次核chronology误按一基index，断言失败；定位为索引基数后以零基逐条核五件成功，未修改chronology。该检查首错记入proof，不是产品失败，也不遮盖R1 Fail。

原R1报告10425 B／de645efa00f9b127698ccbcd3b2ea1da3a58a9deab042f3d37af16da9c01e60f和proof20674 B／ba8ce46a077baf253a4f69dec4a290dd318e0d91b7b550673615f28d18f7afff、旧candidate manifest均保持原字节。22供应模块、四资源与lock/打包writers未变；AGENTS仍15852 B／78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759且未暂存。

## 不关闭的门

本轮只关闭三项源码静态问题。实际hook计数、真实API结果、完整JSONL运行、故障回归、source/package同输入与独立oracle、T03锁/环境/build来源、code fingerprint loader/cache稳定性、许可证及父包均未验证；当前锁与frozen前置拒绝仍是既定限制。原S1/Store HOLD、B1 fresh实测、whole-H、指定双模型、check/package、CI、目标OS、真人、develop和远端门继续保留。
