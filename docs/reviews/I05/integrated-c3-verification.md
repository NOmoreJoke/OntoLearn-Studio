# I05 / B1 C3：确定性依据修复与验收

本次产品源 `69598f30c9052a0a07f3d8e7fc4277626385678b`，完整测试头 `b04569032e94c093e42b7fdc9fcd890df0e832e4`。实际基线仍为 I04 PR5 `5f910b52c69d86a1076b2032e5d3c63e715947f3`；正式全范围冻结 head 由 candidate-3.json 记录。最新状态只维护在 [status.md](status.md)。

## C2 原件及本次修复

C2 `2e33785` 在封口后由独立最小探针发现完整输出不稳定：相同源码、锁和输入，六个新进程 seed1/2/3/5/7/11 的 domain/range 结果集合相同，RDFS basis 及下游 rule basis 却选择不同事实。原件 [19成员清单](evidence/c2-basis-counterexample/manifest.json) 保留所有完整输出、脚本、输入及固定源；总控另独立读回核验。原反例是直接真实库调用，不能冒称六次 Store/worker；零退出由冻结driver断言和summary支持，没有独立逐进程数值收据。

C2 指定模型任务实际为0，没有第三方 C2 NotPass。其固定清单、输入和本地旧绿全部保留，[真实终态](round-2/observed-outcome.json) 明确禁止派发/推送，不能以旧绿给本版通过。

本次唯一推理逻辑改变为每轮候选按 `(output, ordered direct inputs)` 完整键排序，再选首次新增结论的有效 witness。保持模板内 direct-input 顺序，后轮不覆写已有proof；不是按依据长度寻找最短证明，也不枚举/合并所有替代证明。basis仍是该匹配各输入已记录proof的原始事实/公理并集，完整规则匹配保留，规则不反馈RDFS或后规则。规则结果仍不等于相对断言/RDFS的新增差集，多层来源可以共存。

语义及 resources 身份同步为 `i05-finite-5`，执行版本断言同步；共享 source/package suite 增加 domain/range 完整 witness oracle、逆插入和无关事实。唯一新增测试文件包含9个完整oracle及跨seed一致性检查。未改锁、依赖、query/turtle helper、error_adapter或已交接T01/T03/I06路径，未引入T05比较/多结论。

## 本次实际验收

| 验证                           | 真实结果                                                                                                                                                     |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Mac无窗口 `npm run check`      | lint/format/type/build/Ruff全部通过；672TS / 1774Python，Python76.85秒。                                                                                     |
| `npm run verify:sources`       | 12份归档源通过；原checkout64保护源零变化，最新AGENTS78df保持dirty/未stage。                                                                                  |
| Mac / Linux新目录包            | 两平台实际 `package:dir` exit0；Mac没有启动Electron。                                                                                                        |
| 两平台 `verify-i05-runtime.py` | 完整suite源包相等，各7项实际包内stdio，native许可来源精确匹配。新增witness和原literalIdentity均在同一真实包内执行。                                          |
| 两平台 `verify-i04-package.py` | 各17项真实包内回归，公共326/11/30/9/7/41/51例通过。                                                                                                          |
| Linux受影响源码                | 133项通过11.18秒，含新seed回归、真实执行、selected及范围；不冒称Linux全仓check。                                                                             |
| Mac与Linux各自完整B1           | 各12原S1口径＋12真正fresh-process记录；完整结果源包相等；每运行时28拒绝用例，受控接收校准1/拒绝0，入口socket/DNS/urllib尝试0，库级JSON-LD backstop真实拒绝。 |
| Linux源码bridge/native         | 2项通过23.6秒；完整真实结果、reload/取消及实际崩溃/无响应恢复。                                                                                              |
| Linux打包bridge/native         | 2项通过25.0秒，同样实际条件。                                                                                                                                |

原生两次均首次使用list,json reporter，完整JSON及解码driver body保留，没有沿用C2“先内存缺口再补采集”的证据。三个可见窗口、外部XGetInputFocus、实际GTK crash/hang提示、inspector已关、hang monitor开启、noSandbox=false；三个时点完整结果hash和项目/snapshot/revision/job/operation保持，慢COUNT仍running、最终显式cancelled且null resultRef。独立读取完整JSON、重算JSON.stringify结果hash及driver base64与原字节比较均通过。

所有native都在本线无host mount的 `ontolearn-i05-isolated-20261021-v2` 中，产品命令 `docker exec -u node`，独立Xvfb/Openbox/fixture。CAP_SYS_ADMIN只供真实Chromium sandbox，源包chrome-sandbox root:root4755；没有隐藏窗口、关闭hangmonitor或stub提示。负载fixture27事实/9模式×10与原时限不变；B1测量仍是18/180，不能混作容量阈值。

Mac引擎 SHA `18142f71595c47f4e5a4c379c13f6bd00ac7aca6418c7564fc4451b1ec208118`，引擎37,641,909 bytes / 400文件，app561,711,817 bytes。Linux引擎 SHA `22beae772922c06c340ad904c414e2581cb52ce783fb9c44d379791e338ee4da`，引擎43,877,727 bytes / 409文件，app实际363,176,938 bytes。锁仍86dfe82d…，无依赖升级。原Linux测量manifest仍有脚本Mac-only app路径造成的0和旧limits文案，原字节不改，旁附实际独立目录求和校正；0不作为Linux app实数。

完整版本/库/插件/导入/资源/动态链接/许可证、测量原值和命令日志见 [C3证据清单](evidence/integrated-c3/manifest.json)。原生许可只覆盖实际Mac PBS3.12.12与Linux aarch64 CPython3.12.15/BUILD20261013，不外推其他平台。OS缓存未控制，未量化性能提升或宣布容量通过。

## 独立反例与真实上下游

独立边界测试原提交f107458（本线b045摘入），同一249行文件在固定26为7失败/3通过，在固定695为10通过1.70秒。它实际覆盖6新进程×9完整场景×两种无关输入/三种插入顺序；没有硬编码版本5制造旧版红。原C1/C2红、695导出绿和前后绑定都保留。

独立C3审查原文 SHA `4d4e4d011dd8a37a6cdb2a5851665dae1371985bf538b807ee621852949e4930`，在本次变更范围Pass，C3-BASIS-1实际关闭。其独立6seed×8场景×3变化/版本，C2 domain/range/多轮有两种完整输出，C3每场景仅一种；三类完整手写oracle与独立关系闭包支持检查通过。另212上下游测试13.06秒，以及8个真实新worker/stdio成功任务＋1个真实旧finite4 producer，通过完整payload、分页、来源、项目state及版本隔离。

真实旧finite4结果在新coordinator仍可按原producer鉴权读取且字节不变，但作为新finite5任务的selected输入明确IDENTITY_CONFLICT；foreign或finite4声明的纯投影来源REASONING_SOURCE_MISMATCH。这没有新建跨版本兼容通道，不把未知声明当已认证历史。T01拥有Store/公共投影的版本规则，未被本次放宽。

该agent没有执行本线包、全check、native或外部双审；本线结果与其独立运行分开归属。71份独立原件清单与报告完整保全。探针tar解包参数、错误noise predicate、旧C2红误加绿色断言、首环境缺pytest、选择已superseded结果被正确拒绝等原失败及修正均保留，不把探针错误改写成产品回归或抹掉原C2失败。

## 恢复与边界

实际源码导出1182文件，204执行输入在全部新验收之后主机/容器零漂移。1181跟踪成员逐项与固定b045 Git blob字节一致；受保护AGENTS可由同commit的inputs-c2/AGENTS-current.txt恢复。大transport源码gzip不重复塞进证据归档：固定Git＋该指南快照可恢复每个成员，完整清单/传输hash/恢复核对保留；不声称证据压缩包本身包含15MB transport的原gzip字节。独立695的43MB Git tar也已用固定 `git archive --format=tar 695…` 实际重建并逐字相等，保留原71件索引与精确恢复配方，运行输出/脚本/失败日志均无损入档。

新证据归档只存合成运行数据，排除DB/SQLite/WAL/SHM、writer-lock、环境/缓存和app二进制；真实旧C1/C2包仍独立保留，不能给C3抵验收。C3包在own release，身份/文件清单可核验；不承诺从raw归档直接恢复签名app。

C1全部原意见与延期理由继续见 [处置](c1-disposition.md)；C2词法、GRAPH、全局隔离及原始签号IB-1关闭证据未覆写，本次完整新包再次覆盖。既有前导分号容忍、混合RAND/SERVICE错误先后、有限函数/类型范围等仍明示，非完整标准一致性。关于float32/64、日期时区、FILTER丢行与规则比较整任务失败的差异，仅为固定库静态事实，不采纳T05政策或新增比较能力。

Q6十二项及其他产品决定保持逐项待负责人。FR505完整比较/同条多结论、业务编辑器、签名/干净设备、Mac/Windows本版native、生产/容量均未由此完成。两指定模型对新完整C3的实际任务/终态/全文报告及处置、真实CI、正常合并和远端核验仍是原Goal门禁；当前没有可用隔离审查入口或用户明确桌面时段，不操作当前桌面，也不以CLI替代指定应用审查。

独立封存审计全文 [原件](evidence/integrated-c3/seal-audit/report.md.raw)，SHA `abad623d230cd66831471c6ff492d164af91eac62497716bd5f527d3b02be0fb`。逐221成员/233原文件差集、71独立索引、1182源码恢复、204执行输入/64原保护源、两套native完整body与Node重算、全B1/stdio/C4计数实核一致，未发现遗漏或新增阻断；只读审计未重跑产品，不替代指定双审。原归档921393e6…未因加入审计而改写。
