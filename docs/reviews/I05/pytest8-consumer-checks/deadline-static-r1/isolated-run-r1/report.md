# I05 单次受控 full_run 实际终态独立增补

结论：Not Pass。原唯一节点已经一次自然完成，未重试；381项观察后仍触发固定120秒合作式边界，剩36项未开始。64MiB报告上限未触发。本报告只复核既有实际流和固定身份，不证明隔离带来性能提升、并发负载因果、whole-H或容量，也不预签后继选择性计数器方案。

## 实际节点、终态和身份

实际argv精确等于最终受审计划3448B/de0d所列唯一节点：`test_full_jsonl_is_complete_inventory_not_self_signed_equivalence`，自有 `isolated-full-run-01` basetemp/JUnit，未改selector或内部观察。stdout全文和JUnit独立读取，实际collected1、failure1、error0、skip0；断言失败为status1，而非收集器返回0。pytest摘要128.28秒、launcher129.251390秒；收据记UTC 2026-10-22 19:15:22.765597至19:17:32.017287。

- 实际执行收据9751B / `173bf6bda55fdaa6cbc34e36fc94e6ba4667224f4a502ad3708b3fdbbd131da7`。
- stdout1831B / `b6ba3b323101da52625bfabf694552a9865ea87c500de50c5dfd19499066a110`，stderr0B；两分流原字节及收据逐件hash核同。
- JUnit732B / `af21ef1ec6fb27b3f023a3d417bdef8361798796804d0cdba6a2facc13eac720`。
- JSONL46185358B / `169f9223141912fb2e53878119de82f1c343c3b1fc6df859688f25ae25fc418b`，原件仍在本树 `build/i05-pytest8/isolated-full-run-01/semantic-full-v1-diagnostic0/observations.jsonl`，本审未改写或压缩替代它。

该流383条记录恰为header、381条observation、terminal。header fullInventory与selectedInventory相同且均417项；381条记录ID与terminal completedIds逐项同序等于inventory前缀，36条unstartedIds精确等于余下后缀。collectionComplete与fullSuiteCollectionComplete均false，未把输出过一行等同原操作成功。

终态首失败精确为 `utc-date/public-budget-43460` / `semantic.validate_shacl_text` / `shacl-text/validate` / `COLLECTION_DEADLINE`，terminal elapsed127.175700秒。剩余包括public-budget-43461、D1变序、graph-limit以及offline案例；完整36项见analysis.json，未删除或换作通过。

## 合作边界与计时范围

最后一个观察的唯一attempt从858127.140885666至858148.375435208，elapsedNs=21234549875，returned=true；随后记录cooperative-boundary-stop。probe仍为此前已读2996源码，CollectionBoundary先check、真实调用、记录returned/capture、再check。流中的“调用已返回而总预算超时”与这一后check控制流一致；不是OS在120秒强杀，也不是该SHACL案例已完成验收。

现有流按每项start/end求和为125.524543秒；checked-call区间并集之和123.991978秒；观察区间内不在checked-call中的差值1.532565秒；terminal elapsed减观察区间之和1.651158秒。区间并集避免嵌套双计，这些仍是instrumented墙钟范围，不将差值全归JSON编码，也不能从调用区间拆出canonical、sys.setprofile、audit或调度成本。

报告实际46185358B低于67108864B，首失败也不是OUTPUT_REPORT_LIMIT。header仍记录120秒、67108864报告bytes及deadlineIncludesPreflight=true，417声明和原观察顺序保留；没有调预算、少跑观察或更换JSONL领域。本轮也没有产生完整417项结果，因此不能宣称deadline或完整性已解决。

## 40项绑定与后继整合的分界

2026-10-22 19:19:38.505863 UTC，本审在后继T03采用前对实际收据40个beforeFiles逐件读取当前文件并核bytes/SHA，全部同。包括probe102749B/2996、test76628B/`d7947f3e90a7226b28aada7f7b6ba0c09393d25295700da2d8ffa65e353b2f68`、配置1527B/`74763669b19190b980849bee07c53f0c0bc145417ca488a540333803a3ed3d14`及当时build脚本。作者收据声明运行前后绑定同；本审是结束后的逐件读回，不声称连续监测了运行期间每一时刻。

随后按固定来源提交 `553a63ce700477e288be895b33269b1d5ecbdc0f`（parent513db）补核：差异恰为2配置、generator、probe/test五路径，40绑定中38件对应Git blob逐hash同。另两领域明确区分：AGENTS为未暂存15147/de15政策overlay，提交内仍历史1056B原件；`.venv/pyvenv.cfg`不在Git，已在上述物理读回中核同。不能把这两个已知领域差异当运行源漂移。

该提交固定本次source运行内容，明确尚未采用新reader。父任务后继才接T03四路径，可能改变build/入口/reader；本审不再拿后继物理文件与本次旧绑定比较，不把后继采用误报为run期间变化，也不背书它的正确性。fixed-git-binding.json与analysis.json保完整40行和核验时点。

## 资源与审查边界

运行来源仅是新受控pytest进程及总控管理下T01/T03重检查暂停的窗口。收据自己明确其他模型/backend和host负载unknown；T07/T08后台仍存在的上下文由父任务告知。本审未检查或终止任何系统进程，不称整机无负载、不将更后失败位置归因于隔离，也不量化任何性能提升。父任务告知CPU已释放，本审未独立见证调度释放，不占用新验证窗。

本审实际只执行固定Python3.12标准库对既有JSONL、分流、JUnit、文件hash及只读Git的检查；未运行产品、pytest、formatter、linter、CLI或OS实验，未重复读取大源。旧11489报告、旧15成员manifest及plan-delta的manifest均核原字节未动；所有新增仅在本 `isolated-run-r1` 子目录。

原一次性失败停止规则已满足，应保留Not Pass和首边界，不追加同样运行。后继owned CallCounter选择性监控仍须另作源码设计与独立审查，先处理API语义、foreign hook/tool占用、真实code计数及异常恢复/清理/身份契约；本报告没有为具体方案或实验预签通过。
