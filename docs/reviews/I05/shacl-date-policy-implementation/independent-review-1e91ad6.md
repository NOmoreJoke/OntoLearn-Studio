# 有限 UTC date 实施首候选独立审查

结论：固定候选 `1e91ad6fd4216aee6537ec2a6b5a4585bde5e97f` **不通过完整验收**。实际正常 check 有三项新测试失败，其中证据身份冲突由本独审先静态发现，另两项是新测试误认原有接口。未发现对应的 date 产品算法阻断；不能以这一静态结论抹去真实失败。本报告固定首候选与首跑，后续修订另作 delta，不追改本报告或首失败原件。

## 范围与身份

树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-shacl-date-policy`；产品 parent `65e31d331b315c245e1f921c3558bb7886adbd27`。全文阅读本窗授权、单参数返还、最新规则副本、固定设计、独立 oracle 计划、工作账单及三个实际产品差异。产品从固定 Git 读取；不采用后续 working 字节作为首候选。

| 输入 | 字节 | SHA-256 |
| --- | ---: | --- |
| `inputs/I05-shacl-date-policy-source-window.md.raw` | 3932 | `88050b7aa5333e4dd40fa98e9a9ccef9c369a890a4ce6932f9b1a2fec8880988` |
| `inputs/I05-shacl-date-policy-fixed-inputs.amended.json.raw` | 57291 | `ffff4f5ed781280b138ad8887c3235e7880211e5c68551422e496166385f1106` |
| `inputs/I05-date-policy-existing-test-single-parameter-amendment.md.raw` | 2080 | `0a5c681f73024c73a72a59238485f7a073af99aa6da45e27510c2a858d8e22e9` |
| 固定设计 `docs/iterations/I05/shacl-date-policy-design.md` | 22938 | `1457aea0ba8b15ed0d137492dd648bc846e9757e067cf2cf506b70949aa996cc` |
| `semantic.py` | 65749 | `60008130fe0db368ea87948c2c8f079b1161f2aa951693b69635558ed1f56a07` |
| `test_semantic_shacl_entry.py` | 14604 | `61a3e92c298fa37483d203a8ad59dcafc9ec0ff61cf6d30b043267b7ca048c98` |
| 新 `test_semantic_shacl_date_policy.py` | 26691 | `0750cc381091c2f1832d17f04f793550d3b296d31b02f28786a0337b54afb722` |
| `atomic-work-invoice.md` | 2551 | `abca2779d8efd333485a9b253b993d726da3b2a2372ef15691684144d679c88d` |
| `independent-oracle-plan.md` | 19383 | `f96abc097a5186548f1881ddcfde382896d22215a27b5e09c7c01b415ae40ff6` |
| `candidates/01-source-inventory.json` | 32271 | `0f5d1a726f4b98b61454b239c06e0f0bf01511a17e4fe1f8d79e8e37a2b4ecb4` |
| `candidates/01-postcheck-source-inventory.json` | 36265 | `0898331a2b69fd38d48baf6e8a0c41eb01deaeceff93f387882aaaf45b56d950` |

已完整解析清单并逐项以 stdlib 哈希和 `git show` 核对：146 个候选来源与固定 Git 对应，143 个只读成员保持 parent 来源；首跑前后清单的每项 path/bytes/SHA 相同。外部现行授权、返还和 updated fixed-inputs 与本轮 raw 副本逐字相同。实际产品差异恰三路径。旧测试全部字节仅第 300 行未知 range 参数 `utc-date-range-v1` 改为仍未知的 v2，原错误断言不变。

## 阻断发现

### R1 · P2 · 同一测试两向量的证据身份冲突

位置为新 date 测试第 77、175–177、183–185、622、631–633 行。`reject` 以错误码作为 suffix，record 身份是 test nodeid 加 suffix；私有余额 999999 与公开 43461-focus 超界都使用 `GRAPH_INPUT_LIMIT`，因此得到同一输出文件。启用本轮证据目录后，第二条被 `assert not target.exists()` 拒绝，遮住本应由 pytest 捕获的产品资源错误，公开超界向量的独立 JSON 未落盘。

本独审在首跑终态前仅用静态源码定位并上报；首跑 traceback 随后实际确认第 176 行防覆盖 AssertionError，且内层真实产品先抛 `GRAPH_INPUT_LIMIT`。建议给两向量明确不同 suffix，保留防覆盖断言、两项原错误预期、默认 cap 和首证据，不覆盖或删除首跑记录。

### R2 · P2 · 新测试把相对 IRI 的原解析错误误写为后置 IRI 门错误

新测试第 520 行把 `<relative> ex:p 1 .` 预期写为 `ABSOLUTE_IRI_REQUIRED`；首跑真实结果为 `INVALID_TURTLE`。固定 parent `semantic.py:119–125` 已先调用 `parse_graph(..., base_uri="urn:ontolearn:i05:")`，解析异常统一转为 `INVALID_TURTLE`，然后才执行 `_shacl_text_iris`。本次未改该链。

建议新测试按既有解析前门固定 `INVALID_TURTLE`，另以能经过 parser 的坏空白绝对 IRI 单独覆盖 `ABSOLUTE_IRI_REQUIRED`。这是原接口和错误阶段的纠正，不是放宽 date 域、吞异常或放松旧 golden；不应为此修改产品 parser。

### R3 · P2 · 新隔离测试误认既有 SELECT wire 形状

新测试第 551–553 行预期 `rows=[{"s":"<urn:m1:s>"}]`；首跑实际为 `[["<urn:m1:s>"]]`。固定 parent `semantic.py:227–228` 明确返回 `{"type":"SELECT","variables":variables,"rows":rows}`，rows 一直是二维数组。

建议断言完整既有返回的 type、variables 与二维 rows，不修改 query 或原测试。该纠正与 date 范围比较无关；未发现已采政策要求 query 改为字典行。

## 产品静态实质结论

AST 对照确认只改变三个既有定义 `_shapes`、`validate_shacl_text`、`_check_shapes`，增加 `_UtcDateWork`、`_UtcDatePreflight`、`_utc_date_fields`、`_utc_date_term_key`；其余既有定义未改。全局语义版本、SH 谓词白名单、旧 parse/query/reason 和正式 execution/scopes 未改。

`semantic.py:1414–1447` 在原 Literal lexical 上先核 11 字符、ASCII、固定格式及有界年月日和 Gregorian 月日，随后立即要求库值是精确 `date` 且年月日一致；不转换 offset 或改写 Literal。bound 和实际 value 两侧都调用该门。第 1473–1487 行无 target 也校验所有 bound，拒绝同 property 的 date/nondate bounds 混合；第 1516–1525 行包含非date bound 遇 date value 的反向混合。无相关 inclusive 约束的 date 属性不新增 Z 禁令。

NodeShape、property、focus、value 均以固定字段排序；每个 NodeShape 保留自身 target/property 关联，共用 property 不跳过另一个 target 的值。focus 缓存仅在本调用按 targetClass 首次建立，命中仍计费。事实 scope 仍在所有 bound 之后、实际 value 之前。当前模板不允许隐式 class target、复杂 path 或继承公理，因此按显式 rdf:type 取 focus 的前提保持。缺 target 实例或 path value 不虚构范围违规，缺值 minCount 留给真实 Validator。

新公开政策与 exact str 前门、版本 v2 明确绑定；legacy 继续 v1，私有 helper 默认 legacy，整数宽点仍只在数据对象的精确 integer illtyped 门。所有新前门通过后才一次真实 `Validator.run`，options 和六字段抽取保持，未发现后处理 conforms、补造报告或借结果回填准入。

## 原子费用与真实记录

逐源码独立重算 collector `C(n)=3+3n+n*ceil(log2(max(2,n)))`，排序公式的整数 bit_length 与规定 ceil 等价。Graph 查询创建、包含 StopIteration 的 next、键、成员保留和排序预约均在对应操作前 charge；有序 term 读取、缓存查询、重复关联及每个操作数日期检查另计。该单位不等同 Python 解释器内部每次引用、CPU 或物理分配成本。

单节点计划 24、bound 计划 30、value 固定 16 的账单与固定源码相符；公开图总额 `70+23*43460+6*25+8*25=1000000`，不是从 actual usage 回填。首跑实际恰界记录为 Validator1、true/空报告、used1000000/remaining0。私有少一票记录 initial999999、used999999，下一笔 1 票在 date-value 阶段拒绝，Validator0/result=None。公开再多 focus 的产品拒绝可见于首失败 traceback，但受 R1 影响没有独立落盘的该向量 JSON，不能称其证据已完整。

D1 每组三种序列化的 parsedGraphs 摘要及完整 work/RLE 相等；EARLY 实际 date-bound6006、date-value360036，合366042后 `RDF_TERM_INVALID`；LATE 实际 paid1000000 后下一票拒绝 `GRAPH_INPUT_LIMIT`。两组均 Validator0/result=None，与独立次序及费用推导相符。

首跑 115 份 date 记录包含 34 次真实 Validator 调用；本独审用 stdlib 读取原始 N-Triples，按 ValidationResult 节点独立提取六字段，与返回报告比对未见差异，未导入 parser 或产品执行验证。原整数观察 78 份、14 次真实调用；shape 观察 26 份、9 次调用，随同首跑保留。它们证明对应实际观察，不替代整包成功结论。

## 首跑与限制

全文读 `runs/check-01/stdout.raw`（33123B，SHA `cdbae419dc96daf2910c03f4ae725dac4f67bdbdff8d3f39d560cead65b2a0cc`）及空 stderr。command 实录正常 `npm run check`，2026-10-22T00:11:16.739162+00:00 至 00:14:12.806620+00:00，176.06970491691027 秒，exit1。lint/Prettier/类型检查、1125 TS 测试、build、ruff 通过；Python 实际 5162 passed、3 failed、44 skipped、1 个原有坏 decimal 序列化 warning。没有将 stderr0 或部分阶段通过改写为 check 通过。

环境实录为本树独立 .venv、Python3.12.12、RDFLib7.6.0、pySHACL0.30.1；sources-01 正常退出0，实际核12归档源。command 原件只存命令/环境/时间/退出；146 源前后身份采用独立 inventory 原件关联，未声称存在嵌入字段。

本独审未运行产品、库、测试、worker、数据库或 formatter，仅静态 Git/AST/stdlib 读取与哈希核验，新增本报告。oracle-plan 和 atomic invoice 是前置静态依据，真实观察来自 root 首跑。新测试修复后必须以新固定候选和实际结果关闭三项阻断；不得沿用首候选通过。本报告不替代指定双方外审、CI、平台/真人门，也不表示 T05 消费、正式 execution/Store/Job/selected、SQLite HOLD 或 whole-worker/H 证明完成。
