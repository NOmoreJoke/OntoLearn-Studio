# 有限 UTC date 实施最终候选独立增量审查

结论：固定产品 `6891a5842302859a531cf82767c5a482417bc274` **有限通过本窗组件审查**。首候选的三项新测试阻断均有最小修正及真实正常 check 关闭；本次未发现未闭合的来源、日期域、target/value、费用或报告阻断。首候选 `1e91ad6` 的不通过结论和原失败记录保留，不追认成通过。

## 固定范围与来源

树为 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-shacl-date-policy`。本次 delta parent 为 `1e91ad6fd4216aee6537ec2a6b5a4585bde5e97f`，实施起点为 `65e31d331b315c245e1f921c3558bb7886adbd27`；只读设计 SHA `1457aea0ba8b15ed0d137492dd648bc846e9757e067cf2cf506b70949aa996cc`。已全文读首轮实际失败和本轮完整正常 check 原双流、命令环境及 validation；静态读取两个固定 ref 的真实差异，不借 working WIP 替代版本。

| 最终输入/证据 | 字节 | SHA-256 |
| --- | ---: | --- |
| `packages/engine/src/ontolearn_engine/semantic.py` | 65749 | `60008130fe0db368ea87948c2c8f079b1161f2aa951693b69635558ed1f56a07` |
| `packages/engine/tests/test_semantic_shacl_entry.py` | 14604 | `61a3e92c298fa37483d203a8ad59dcafc9ec0ff61cf6d30b043267b7ca048c98` |
| `packages/engine/tests/test_semantic_shacl_date_policy.py` | 26924 | `bd8e332a1b55ebdf183f1effdd37126a61233931edaa8d2239e0a20d9179b765` |
| `candidates/02-test-corrections.patch.raw` | 3115 | `59fb28fb57a368cb4d8d601436b917209177197b57e76ff8ba7c0e5195df6a30` |
| `candidates/02-source-inventory.json` | 32390 | `9a1c6ee6ec41665f89bb5378f5b98d0b7055f0ffd20b92320e2f105787fd34b4` |
| `candidates/02-postcheck-source-inventory.json` | 36265 | `ee69f73cbd2bfb0e89946215275cfb54ef45ecf250417b910843834cb94116e1` |
| `runs/check-02/command.json` | 1694 | `886667cf872486c944b00b3a06376e5173e5e8ede4ffbaab3e4ec5b244bd5bae` |
| `runs/check-02/stdout.raw` | 14184 | `c492347d2ed9d7876c9869cc05eb1abe0e08d50a48248068d3559aed4e81ee67` |
| `runs/check-02/stderr.raw` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `runs/check-02/date-evidence-inspection.json` | 8113 | `54454feea1fad6916bed7e7ee3d29f8f390a477110a7e30fdf9fa267efc7d3a2` |
| `validation.json`（本次读取版本） | 10963 | `da9f8ddac25d60595f9c31fd95fed70aeae1f1d20c626e38e4268705ec25e17a` |

完整解析并逐项以 Git/stdlib 核对两张新清单：146 个 path/bytes/SHA 前后相同，current 与固定 `6891a58` Git 相同，143 个既有只读来源保持。相对 `1e91ad6` 只有新 date 测试变化；semantic.py 和已返还旧测试的字节均未再变。相对实施起点仍恰三个授权路径；旧整数测试仍仅第 300 行未知策略 v1→v2 那一处，不借此改任何旧断言或 golden。

首审原件 `independent-review-1e91ad6.md` 仍为 9516B、SHA `286bc4cd6d54eed5fa5ba8f05bfbbd591eee3de6d1977de13c0ef58b0682c80a`；本报告没有覆写它。首审包含完整授权输入身份及未变实现的逐项静态审查，本轮只针对三项修订和新实证复核。

## 三项首失败的关闭

| 原项 | 最终变更及判断 | 关闭证据 |
| --- | --- | --- |
| R1，P2，预算两向量证据 ID 碰撞 | 新测试 `reject` 增加显式可选 suffix；私有少一票使用 `private-999999`，公开超界使用 `public-overcap`。默认仍取原错误码，文件防覆盖断言和两个资源错误预期保持。 | check-02 中三个预算向量分别落盘，身份/文件哈希对应；公开超界不再被防覆盖 AssertionError 遮住。原 check-01 同码冲突记录保留。 |
| R2，P2，相对 IRI 前门预期错误 | 原相对 IRI 向量固定 `INVALID_TURTLE`，另新增坏空白绝对 IRI 向量覆盖 `ABSOLUTE_IRI_REQUIRED`。固定 parent 的 parse-before-IRI-check 代码与首跑实际结果共同支持该修正。 | 新两个向量均按各自既有前门拒绝、Validator0；未改 parser、date 域或旧 golden。 |
| R3，P2，SELECT 返回形状误认 | 新隔离测试断言完整既有 `type="SELECT"`、`variables=["s"]`、二维 `rows=[["<urn:m1:s>"]]`。固定 parent `semantic.py:227–228` 一直如此。 | 新完整断言通过；query 产品实现未改，不再以字典行预期要求修改旧接口。 |

这些不是把已采日期预期改为 actual 求绿：日期域、before/equal/after、原 C 扩展条件分支、完整六字段、零调用拒绝、cap、手工费用算式均未变。相对 IRI 与 SELECT 纠正有未改基线依据，证据 ID 修正仅使两项不同输入可分别保存。

## 未变实现的实质确认

`semantic.py:1414–1447` 双侧原词法有限域及精确库值检查、1473–1487 的全部 bound 校验和混合拒绝、1516–1525 的正反 date/nondate pair 门均保持首审字节。inclusive 等值通过，exclusive 白名单未开放；无 target 仍核 bound，无 value 不造范围违规，无关合法 date 不受新增全图 Z 门影响。共享 property 的各 NodeShape target 分别遍历，全部实际 value 检查，缓存仅本调用按 class 建立；scope 仍在 bound 后、实际 value 前。

默认私有 helper/旧 check 继续 legacy；新公开 API 两策略必填、exact str、UTC 独立版本 v2，旧入口版本和全局版本不变，整数宽点不扩大。全门通过后一次真实 Validator，原 options、真实 conforms、原 value lexical/datatype 和六字段抽取保持。未发现把 allocation、预置结果、规则 comparator 或预期数据供给 Validator 的路径。

新测试 observer 委托原 parser、原 charge、原 Validator.run，不供应 conforms/report；预期在返回后比较。原 C 条件 golden 只在调用之后读取参与断言，未作为产品输入。私有降低 cap 和畸形 native value 是单列故障注入，不冒充公共受理或真实库兼容性的替身。

## 费用与原始 RDF 独立核对

费用小计仍由固定源码逐项重算，而非从 actual 回填：collector `C(n)=3+3n+n*ceil(log2(max(2,n)))`；计划24、bound30、value固定16，公开恰界 `70+23*43460+6*25+8*25=1000000`。创建 Graph 查询、含 StopIteration 的拉取、构键、保留、排序预约及日期域/兼容检查均在相应操作前先付；重复关联/操作数不借日期结果缓存逃费。该政策单位不声称对解释器每次内部引用、库 CPU 或物理分配逐一计费。

本独审仅用 stdlib 读取本轮全部117份 date JSON，独立从保存的原始 N-Triples 按 ValidationResult 重建六字段及 conforms，再比对返回和实际调用；未见差异。34 次真实调用为22 true、12 false；83 个前门记录均零调用且无成功 result。逐份 RLE 的金额×次数合计等于 used，initial-used=remaining，失败 requested 大于余票，未见负余额或伪平衡。root inspection 的结论另与此核对一致，未将其汇总直接当独审依据。

| 真实预算向量 | 实际结果 |
| --- | --- |
| `exact-million` | 公共默认 initial1000000，used1000000/remaining0；Validator1、true、空报告。 |
| `private-999999` | 同真实输入的私有 lower-only seam；initial999999，used999999 后下一笔1票先付失败；Validator0、result=None。 |
| `public-overcap` | 更大真实公开输入、默认 cap1000000；used1000000 后下一笔1票失败；Validator0、result=None。未称其为公共“差一票”输入。 |
| D1 EARLY，三序 | 各自 parsed RDF 摘要及完整 work/RLE 相同；bound6006+value360036=366042，date-value 阶段 `RDF_TERM_INVALID`，Validator0。 |
| D1 LATE，三序 | 各自 parsed RDF 摘要及完整 work/RLE 相同；used1000000 后下一票 `GRAPH_INPUT_LIMIT`，Validator0，不继续搜更具体错误。 |

原整数78份观察/14次真实调用的保存 RDF triples 也独立抽取六字段比对一致。shape26份观察/9次调用及其既有完整报告已读取；此旧 observer 不提供与新 date 同样的原始 N-Triples，未据此虚称新增原始证据。旧77 DAG、26 shape、70 integer 与新106 date 实例均由本次正常 check 承载。

为固定所读观察集合，分别将目录中的 JSON 按文件名排序，逐项取 `{path:文件名,bytes,sha256}`，以 `json.dumps(...,separators=(',',':'),sort_keys=True)` 的 UTF-8 字节求 SHA-256；此处只记录摘要，没有改写记录：date117成员 `e0238872675fad03f314d6312cbcae06998aea89ca03b70c552a7a3063ed07dd`，integer78成员 `cb87f3181a9f8464fe53473b4217e1893cd33dd9dc5a85bf5e73bb5590181c5a`，shape26成员 `d249a16fa45d020f3893b402711d8eef72b30b341ba9e6342d5262c90280f211`。

## 实际验证与有限边界

root 正常 `npm run check` 实录 2026-10-22T00:42:08.353588+00:00 至 00:44:52.251320+00:00，163.8976051659556 秒，exit0；完整 stdout 证实 lint、Prettier、类型检查、1125 TS、build、ruff，以及 Python5166 passed/44 skipped/1 warning。warning 是原整数测试坏 decimal 的既有序列化提示，未屏蔽。独立 .venv 环境仍为 Python3.12.12、RDFLib7.6.0、pySHACL0.30.1。12归档源由未变 sources-01 正常 exit0 实核；两候选间只改新 date 测试，无变化未重复该验证。

本独审没有运行产品、第三方库、测试、worker、数据库、formatter、GUI/native/e2e/HMR 或模型；只做固定 Git、AST、stdlib 文件/记录/哈希审查并新增独审报告。实际运行均来自 root 上述记录，静态 oracle-plan/invoice 不是运行 Pass。当前有限通过只覆盖这组组件政策、真实报告、费用和既有回归；不等于所有输入穷举证明、whole-worker CPU/native/H、T05 消费或正式 execution/Store/Job/selected 成功，不解除 SQLite HOLD、指定双方外审、CI、平台/真人和合并门。

本报告写定后停止写入；首报告及首跑原件保持原字节，后续格式与 Git 交付由 root 处理。
