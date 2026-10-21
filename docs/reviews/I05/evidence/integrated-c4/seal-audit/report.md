# I05 C4 封存独立只读审计

**Full Pass（本次证据真伪、完整性与报告归属范围）。** 未发现可证实的缺件、计数错误、源绑定错误、实际运行结果误述或需要改变候选的阻断。本报告不能替代指定模型双审、产品功能全范围审查、CI、正常合并或发布门。

## 固定对象和操作范围

实际全文阅读主线 `integrated-c4-verification.md` 及 status 最新 C4 段，核对产品 `1a79731091e671c497824c94e12dae34a4e8609b`、完整测试头 `40c18ea1b9ce4fef9a5235718fd7e622e2d06cc4`。被审文案、status及manifest的原字节副本和SHA在本目录 `audited-*` / `audit-bindings.json`；未修改主线。

执行遵守当前AGENTS78df和common ff5f9f（含worker唯一归T01、无桌面约束）。本人只运行文件/Git/哈希/JSON核对与PyInstaller静态归档读取，未导入执行包内产品模块、未运行产品/pytest/构建、未操作容器、GUI/Electron/CUA，未写候选任何源/测试/配置/文档/归档，也未创建或更新Goal。所有新增文件只在本人ignored `build/c4-seal-audit/`。六份最终审计脚本、stdout日志、JSON结果及观察器初始失败均保留。

## 1. 全归档实际读回与排除差集

实际打开gzip/tar，逐一读取1254成员所有原字节，而非仅hash压缩文件。raw压缩6,516,119 bytes，SHA `eae749d05ac61b9cc726626f008507b3484d1ba8b1980f9f7a33eb0f51871acc`；1254唯一普通文件合计62,425,493 bytes，全部名称/长度/SHA及原路径当前字节完全相符。没有重复名称、symlink、绝对路径或父目录逃逸。

原 `build/i05-integrated/c4` 实有1287份文件：1253入档＋34明确排除；另外1份封存脚本位于原目录外，故归档1254，不是1254＋34简单相加。完整集合无遗漏/多余。34项原件长度/SHA逐一核对，包括排除的二进制、源码transport及合成SQLite/lock。归档所有成员均检查文件名、目录名和魔数，没有SQLite/WAL/SHM/lock、venv/node_modules/cache/pyc、ELF/Mach-O/PE可执行文件；没有任何嵌套tar/zip，因此含SQLite的portable-v2未被偷偷嵌入。原件可能存在合理副本，本审计没有去重或删件。

结果和逐成员索引：`01-readback.json`；实际字节副本在 `readback/`。封存脚本本身也逐字节在档，没有将本次独立审计反向塞回原archive造成自引用。

## 2. 源恢复、执行绑定和包内实际代码

完整1238源码成员逐项读取固定40c18ea Git blob并重算SHA：除受保护AGENTS用同提交inputs-c2/AGENTS-current.txt恢复外，全部直接等于对应固定blob。恢复配方实际适用，未承诺重建原gzip容器字节。205当前主机执行输入全部重新实核；容器205一致的原收据存在，本人未重新进入容器。对原checkout64保护源再次逐项实际核对expected/actual/当前字节一致。

与原204输入相比，195份原字节保持；改变恰为授权七个语义源＋两份直接旧测试，唯一新增输入为string_identity回归。没有worker、Store/coordinator、canonical、依赖/锁/build/CI、桌面路径越权变化。

独立实现审查原44文件索引：42份逐字节入档，两份完整Git tar按各自精确recipe实际重建，分别与原source-1a79731/source-83868b4的长度、SHA和全部原字节一致。原44索引和receipt完整保留。stdio原202文件索引：192份入档，10份明确仅SQLite/空锁排除，各行原件SHA/长度及集合全部核清；不承诺从归档恢复原DB字节。本人旧红回归103份复制及两份被排除的固定Git源码tar也与原件相符。

本人再次直接读取Mac、最终Linux和保留首Linux引擎的CArchive/PYZ，**没有执行这些程序**。逐个提取七模块code object，与固定1a源码在归档co_filename下编译的结果直接相等（含嵌套code/constants），marshal SHA也等于原记录。三者都是本版finite6实际代码。首Linux引擎SHA与最终Linux完全相同：`184c8542aaf8c189f980ad35984db5734b769f3a386895619cc8f5563e4cbdcc`；首包记录runtimeAcceptance=false，不能从旧源码缓存导入5推导首包运行5。主报告已准确更正这一区别。Mac引擎SHA `fd4b5ab3ca97334c81a4363bb1c9141bf1db9ebbeaf1f555e456b47510e4841f`。

完整结果：`02-source-code.json`。

## 3. v1/v2 driver、同输入旧红与新绿

保留的pre-guard v1 driver SHA875dd5…与guard版e05448…不同。source-01确实没有launch.json/开跑SHA；README和主报告明确此限制，没有把后来e054字节归给首轮。source-02有实际e054启动绑定；主Mac包/Linux源包三个v1启动SHA也为e054。其完整比较SHA74ab416c…相等只证明内容相同，不等于首轮driver有开跑时哈希。

v2每组launch绑定4a064f…driver。v1→v2 fixture spec实际差异恰为format与第四规则when的第三term由typed变plain，输出仍typed；两版seed SHA及snapshot不同。六组v2确实使用同一新seed hash6627b153…和同输入snapshot，未以v1绿替代v2。

实际重读十组×19＝190份认证payload和public结果。逐项直接重算payloadHash/rowsHash，解码全部JSON-pointer分片，比较完整payload每个leaf；metadata/实际job的完整三字段implementation一致，成功job/resultRef身份相符。六组v2另外每组19份原stored semantic row/public/stored rows逐字比对（共114），原序列化payload字节也严格等于canonical JSON。约束/断言/本体/派生资源的完整内容可由保存的fixture spec和实际reasoning载荷取得，180个资源角色ref全部独立重算匹配，完整validationBinding仍在原payload中。

两旧Mac/Linux C3包各完成19个succeeded任务及19份payload后才oracle失败，命令receipt真实exit1。实际旧producer/job/meta/payload是完整finite5三字段，host/reference产品1a与目标旧engine SHA分开记录；没有硬编码finite6提前挡旧版。实际旧reasoning均为5结论/5trace；max1错误不conform、min2错误conform、各17个oracle不符，都是同一个字符串身份缺陷的表现。summary的ruleConclusions7/ruleTraces8明确为oracle规模，observedReasoning保留5/5原值。

新v2独立源码、Mac包、Linux源码和包四组每组19任务、7结论/8trace、完整SHACL报告全部正确，比较SHA均 `eb51f12c63c9ea6abac3cd745aeab887ab9b0f3310071da0fe0c2c2901f8cb2b`。旧两组比较SHA306d87…一致。新每组2802行，旧每组2288行（含header）；完整原始身份与binding没有为跨运行比较而删除，仅比较副本替换临时result身份及去binding包装。结果：`03-payloads.json`、`05-attribution-parity.json`。

## 4. 独立实现、历史与原始失败

独立实现报告原文SHA `d053c56b49f635ce6fbe3e1a6c44f0bc55c4816b5a2da3b68684336d0fd61a97` 与主报告一致，明确其范围不是主线全check/包/B1/native。522项33.31秒原日志和命令在；旧12、新worker18、新stdio18、historical2共50个完整record重新逐leaf解码，1343＋1802＋1802＋382＝5329行一致。

真实旧finite5原payload/rows hash与旧receipt再次直接计算相等；两份真正新historical结果的metadata历史标志、payload inputSelection=historical及所选result一致。历史identity记录准确包含current/historical拒旧结果，以及分别改变engineVersion、executionSemanticsVersion、dependencyLockHash的三个独立拒绝。34 pure cases、8 lexical、12并发、4次TrueFilter私有副本、selected不重算记录都在，未扩成所有AST/标准符合性承诺。

不利原件未省：targetNode范围外首suite stderr、strict decoder格式首check失败、1837后1847完整check；Linux两次359通过/1失败及各自command exit1、最后360通过9.32秒；源码6/实际resources导入5和mtime/pyc header的原观察；第二次pytest缓存仅保留当时观察与归因边界，没有伪称保存其旧code object。原型v1确实修改全局TrueFilter的fresh负证据、修正版、独立pure首oracle错误、旧版全unbound BIND对照、计算parser.name导致观察器扰动和修正raw都在。准备阶段未单独重定向的工具异常仍只按说明保留，不冒称有不存在的原stderr文件。

`first-affected-exit.txt`/`second-affected-exit.txt`属于另两次已通过的主机受影响测试，不能错认成Linux失败退出码；本审计实际采用linux-cli-commands/second中的source-affected exit1及对应Linux原log。该归属与主文案不冲突。本人脚本初始也误猜了这些文件名、原生outputDir和格式日志措辞，已依据原始结构修正；相关观察器失败脚本/log保留，未据此报产品缺陷。结果：`06-history-failures.json`。

## 5. 主check、B1、包与真实原生原件

主完整日志直接支持672TS/1847Python、80.09秒，sources12；两平台构建exit0，各7实际stdio＋17 C4，源包suite原字节相等。两平台各12原口径＋12 fresh记录逐项读取完整结果源包一致，18/180断言及4 ontology口径、首JSONL到达/warm/进程结束时间分离正确。每运行时28拒绝为27入口零network事件及1库JSON-LD到urllib.Request后拒绝，校准1/拒绝命中0；未把HTTP接收器说成产品服务。

引擎400/409文件及37,648,261/43,884,087 bytes逐文件求和相符。Mac app561,718,169 bytes；Linux raw app0保留，独立postcheck校正363,183,298 bytes，未把0当实数。许可来源仅精确匹配实际Mac PBS3.12.12、Linux aarch64 3.12.15 BUILD20261013，不扩至其他平台。

Linux源码和包首次list,json完整报告均2 passed、无retry/flaky/skipped，24.980798秒/25.075055秒；各7附件都可定位，driver base64 body解码与单独原JSON逐字相等。本人用Node JSON.stringify重算三窗口时点完整results：源 `b1220b32e7da8f408cbac647494bfbcbea4ee3c81fa66fa1a76618d3e8a5bd46`、包 `4d011d1880e6748674ed51382b8a5e1129eab1d4f94c25e049a07af6dd48f85a`；每套三个时点完整值一致，reasoning/query/validation行158/194/279，project/snapshot/revision/job/operation保持。

三个窗口visible、重建窗口focused且外部xdotool/XGetInputFocus可见，实际crash/hang GTK窗口、crashed/unresponsive事件、inspectorClosed=true、hangMonitorEnabled=true、noSandboxSwitch=false在原件齐全。慢COUNT三时点仍running/null resultRef，最终同job显式cancelled/null。bridge reload和失败/取消也完整。此为审既有隔离Linux原字节，不是本人重启窗口或给Mac/Windows本版native背书。结果：`04-native.json`。

## 结论使用限制

本次全归档审计Full Pass，无需改候选来处理本审计问题。Q6十二项、FR505通用比较/多head、D3/D4及其他负责人决定继续开放，没有由本次修复默认采用；无签名/干净设备、生产、容量或所有RDF/SPARQL/SHACL标准符合性结论。两指定模型新完整候选审查、真实CI、正常合并和远端核验仍是后续门禁。
