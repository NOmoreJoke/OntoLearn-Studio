# T05 七池声明分配 oracle delta 独立审查 R1

2026-10-22。审查者为新独立 agent，未参与本候选实现。受审实现候选 `6be26aa8c5282429332daf221701df1d409abf48`，其 parent／delta base 为 `0cb1a37fe2a68e671d241721cede80621545dfd8`，仓库 base 为 `5f910b52c69d86a1076b2032e5d3c63e715947f3`，分支 `feature/T05-source-package-oracle`。

## 结论

**限定通过，无阻断本次声明分配 delta 收件的 P1/P2。**

七域 sorted-divmod 已独立表达为 declared expectation 和有限模型关系；没有升级为 actual OriginalAllocation、17L、planDigest、budgetUsage、真实 capture 或完整预算准入。全部417原业务 expected 与输入／上下文绑定不变。整体仍 280 specified／137 pending，`wholeOracleComplete=false`；本审查不关闭这些缺口或任何产品／父级门。

## 范围与固定状态

先全文读总控 `T05-declared-allocation-oracle-delta-window.md`、`T05-source-package-oracle-limited-root-closure.md`、受审树最新 AGENTS 和旧外部 oracle 独审 R1。随后全文读两个脚本的本次 delta、新字段说明／source receipt／candidate receipt，核五件 JSON 的完整结构与逐项声明模型、coverage／budget gaps、candidate manifest、命令原件及源码快照，并比较必要旧上下文。

本轮相对 delta base 为32路径：7个获准 writer 修改、25个新证据／文档；旧交付101件中另94件字节未变。当前 candidate manifest125成员加自身共126件，成员集合精确等仓库 base→candidate 的完整变更集；每件 current bytes=固定 Git bytes=清单 bytes/SHA，未遗漏尾项或把历史 manifest 当当前 writer 版本清单。

实际验证前 HEAD 精确为候选，index空，工作区只有受保护 AGENTS M；该文件15852B／SHA `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759` 未变。审查者不提交、切分支、修改候选或旧树；本报告为唯一新写文件。

## 独立来源

三个新增原件与指定 Git blob 全字节核同：

| 原件 | bytes | SHA-256 | 本 delta 使用范围 |
| --- | ---: | --- | --- |
| de37ff6 integration plan | 36922 | 990555ae61b086d40c33212115728bd1914063af25e34b3815345decc85ed66d | L72–80，声明七池／排序／同child预算／不回流 |
| 851e624 saved-restore plan | 45463 | 3f72f07ba535983ca324226be769de2c157303b35b723aa107bf4e6252a1f41b | L103–109，ID／ordinal／disabled／dummy与实际捕获分层 |
| 6891 first-fixed-inputs | 57687 | e5fe75cbf07436660fc475b5ac6c176c40fff35f00e1aad1250b7d967ef149d5 | 139项选择性采用 metadata，非整树／运行权威 |

独立核139项 path唯一、sourceRef均为6c；`/files/51` semantic和`/files/56` restore是write-existing。候选准确注明这是初始选择性采用，不能推出后续writer未改、规范ref为Git祖先、整树自动采用或真实行为通过。声明权威来自明确 delta 窗口及固定规范条款，没有从新 probe／产品输出或实现算法反推公式。审查未读取产品算法，也未采用新fee WIP或DTO研究。

## 模型、字段与边界核查

1. **七池及完整定义。** work16777216、input_bytes262144、output_bytes262144、trace_items8192、firings1024、head_occurrences16384、bindings1024逐名绑定，各域含义分立。n为完整定义数量且含disabled，N=max(1,n)≤100。按完整rule_id的Unicode码点序分余数，原definitionOrdinal只定位原列表位置。未使用保存顺序、数组ordinal、locale或Unicode归一化决定额度。

2. **独立逐ID公式核对。** 审查另用不import builder／产品的stdlib脚本，直接从固定纯输入提取完整原定义／disabled，先构建每域相同商，再对前余数个排序位置加1，独立核全部88个specified声明模型和93个child记录。完整子记录键、exact int（排bool）、ruleId、sortedPosition、original ordinal、disabled bool及七域全部额度吻合；各域单独求和恰原总额。定义输入重排仅改变ordinal；disabled保槽，不能回流／抬额／重分配。

3. **ID与空集合。** 关系只接受明确完整的exact list、非空exact str、唯一ID、有效Unicode、字符与UTF8≤16384、至多100定义；disabled必须明确、唯一且属于完整universe。没有strip／NFC／截断。测试覆盖非ASCII与跨BMP码点、分解／组合字符仍不同、无效surrogate、ASCII边界、多字节UTF8边界、重复／非exact字符串／bool／外来disabled。空公式自测给批准的匿名dummy：ruleId/ordinal=None、空definitions/matches、要求真实空batch；不捏造dummy disabled标志或实际batch对象。实际RuleSpec exact类型和真实发行仍在外层必需门内，不由JSON metadata通过替代。

4. **有限关系及负例。** `declared-seven-pool-allocation`只核本模块自有完整声明模型；递归exact model检查完整keys／types／tails。新增负例包括删最后child、额外usage字段、bool冒充ordinal／额度、总计不变但余数转给错误child、disabled翻转、把actualCapture标true、允许reset／重分配。手写三规则七域精确值提供独立结果锚，1..100规模守恒／相差≤1与重排／全disabled／空集合覆盖提供不同性质约束；自测不只是条数或generator镜像。

5. **适用范围完整。** 417项新字段中301为null；116相关ID的有序分类完整对应coverage：88 specified＝82 eligible profile＋6 fullview/profile；26 pending＝25 records缺显式完整disabled声明＋1 fullview Turtle缺universe／disabled／ordinal；2 not-invoked＝repair原profile不执行和DAG Turtle前门拒绝。即使records的rules为空，也没有把缺失caller metadata偷偷补成空disabled或编造slot。所有26项原本已在生产typed／capture／费用pending内，本轮新增其精确声明缺件，未据此捏造额度。具体ID完整列于coverage的declaredAllocation，并以固定输入逐ID核同。

6. **声明和实际证据分离。** 输出明确namespace=declared-only、actualAllocationCaptureProvided=false、actualUsageProvided=false。compile/evaluate共享原Budget、不得reset／跨child借额／未用回流表达为需满足的合同；JSON布尔声明不认证真实对象身份。同次opaque关系与原trust gate保持不变。82个profile预算gap的真实allocation value仍None，32个生产／恢复链actualAllocation仍None，新增关联仅指声明ID／状态，actualCaptureValue也仍None；没有预填完整17L、usage、planDigest、caller对象、账单或首错。

## 旧语义与缺口保持

独立逐字段比较旧0cb1a37与本候选全部417项：原业务expected、family／operation／id／顺序、dataset／projection／sourceRefs、参数、contextStatus、case-set位置、业务状态、比较政策与原动态关系均相同。原source authority引用前缀保留，只为相关声明增加三个精确来源；新增字段没有改变RDF图、query／SHACL、typed数学、原83／E5／repair或原106 operations／54 checks／50 cases的执行权威。完整context ledger逐值不变。

构建依实际pendingFields重新计数，并非在实现中硬写280／137。全局状态和coverage计数一致；137仍包括完整预算／typed／capture／legacyDTO／scope来源／精确拒绝投影等原缺口。新增七池子式只关闭自身可明确部分，不关闭整体预算／oracle、source/package、formal Job／selected／whole-H、SQLite HOLD／S1／parent B1、指定双模型／CI／两OS／真人／develop门。

## 实际验证

审查者只实际运行下列两个获准oracle命令，各一次；没有向既有commands目录事后写入“独审原双流”，结果由本次工具输出及本报告记录：

| 检查 | 本次结果 |
| --- | --- |
| `python3 -B scripts/test-i05-source-package-oracle.py` | exit0；47 tests passed，`Ran 47 tests in 3.485s` |
| `python3 -B scripts/build-i05-source-package-oracle.py --check` | exit0；五件完整bytes/SHA相同，417／320，280specified／137pending／false whole |
| 独立stdlib／Git | 全126件身份、32delta、旧94原件、固定source原Git／139采用metadata、新三命令argv／源SHA／原双流摘要／attempt源码逐字一致；delta whitespace通过 |
| 独立纯输入公式／语义比较 | 88模型／93child全部七域／排序／ordinal／disabled吻合；全部417原业务expected与绑定、完整context ledger不变 |

五件本候选产物：

| 文件 | bytes | SHA-256 |
| --- | ---: | --- |
| oracle.json | 5920695 | 7ae1c1311f71bfbcc76d5ab9592eebb66f39410ef9e0871965951de35dc77023 |
| coverage.json | 154032 | 95d7395761fbabe97c1fd81d1d05eb44bb8094f7266d977de42fdff349d28bd9 |
| sources.json | 9872 | f2db5b1ad84ce4c7f97e1b9e30e23c63f3902f60dc92e1441f945d8dfed35c64 |
| schema.json | 9106 | 74889cca94e90d62b2a456087946cfdd35f7a716039729091892a0bcda13f7c5 |
| budget-gaps.json | 362492 | e68188ddefae4488fa6cf7762549508b78a3d87551f27cb24b9c9998f7948e9d |

本审查没有运行产品／probe／pytest／npm／build／package／RDFLib／pySHACL／reader／helper／native／DB／GUI／网络／安装／共享环境，没有使用T03票，没有模型外发／付费／push／PR／merge或Goal操作。旧候选、报告、manifest、命令及首失败历史均保持。本结论仅覆盖声明分配delta和其纯模型证据。
