# T03 D2：固定源码与包组合合同（文档准备）

2026-10-21。此件可供总控批准下一阶段的精确施工范围。**本轮不施工、不采用源码、不安装或执行产品/probe/package。** I05 `0475d0ec6c486a63c7e8f62f11f35181da6b2576` 已获根受限读回收口：1902B / SHA `32d13ceac16d0db45222ac129c5a22f2c132004d5a17169e5386115fcaaa747d` 已全文读，可作本合同技术来源；以下组合仍须明确接收与施工授权才实施。D1 两配置固定 fd87，原 T03 Goal 保持 blocked，不重建。

本轮唯一主文档即本文件，证据仅 [review 目录](../../reviews/T03/profile-D2-fixed-input-package-contract/)。准备授权 3959B / SHA `ceb03cbf23fdde33ec71406b09be909457075a2969b08868200a91f745bf9ed1` 已全文读。唯一逐文件来源清单为 [inputs.json](../../reviews/T03/profile-D2-fixed-input-package-contract/inputs.json)：所有条目有固定 ref/path/bytes/完整 SHA，含 AST import、原基线继承、仅源码验证依赖；不把候选清单自报当已验证安装或包。

## 1. 实际固定输入与采用表

I05 来源统一为 `0475d0ec6c486a63c7e8f62f11f35181da6b2576`，不是旧 C4，也不是其可变环境/whole commit。已从固定 Git 核合同 6295B / `471ce2922e301322b33791d953fd86e05864db180921cdbcf607e2d2b80fb7d3`、probe 13391B / `2b2dabd91745b4b4c2a3fad39b6386e4edd985189336bf029d9b07a638fc7bf6`、资产 1839011B / `6c6ffc3a1a57d1817583c0a71d24e2847cc5d2d673848878c6e6e72dfe6c39de`、candidate-inputs 32937B / `aa22b70ce65f27c16361b04f32c74a9e2d8de105d1611d70d6e5338f2e4e7b86`。

### 1.1 十份 I05 产品源码（未来只读接收；相对前缀 packages/engine/src/ontolearn_engine/）

| 文件                      | bytes | 实际采用理由                                                       |
| ------------------------- | ----: | ------------------------------------------------------------------ |
| resources.py              |  2927 | 原 5f 动态 contract/lock 加私有 semantic_identity；默认仍 i04      |
| semantic.py               | 52609 | 唯一实际 reason、RDFS/join、profile 计算与预算                     |
| semantic_error_adapter.py | 15426 | 原四字段公开 error 与私有安全 diagnostic 边界                      |
| semantic_execution.py     | 32917 | 同一 execute_profile_records、完整 payload/rows/摘要               |
| semantic_offline.py       |  1351 | 既定离线保护                                                       |
| semantic_profile_probe.py | 13391 | 唯一源/包 canonical main；固定资产和 identity                      |
| semantic_query.py         |  6448 | semantic 的实际静态 import 闭包，含 RDFLib SPARQL parser           |
| semantic_samples.py       | 33858 | I05 固定十文件集合及 legacy 源测试的实际样例依赖；不是另一个包 CLI |
| semantic_scopes.py        | 13051 | execution 的 legacy scope import 闭包                              |
| semantic_turtle.py        | 33916 | strict term/N3/IRI、issuer/context、来源/禁用规则绑定              |

AST 递归列出的引擎 import 均落在这十份、下列七模块或批准 5f 的父包/storage_probe 等既有模块。semantic_samples 虽不在 profile main 热路径，十文件源集合和 legacy 回归依赖它；只以明确 canonical hidden-import 收集，不赋予新 dispatcher。无额外 fixture 文件读取；probe 运行读取面仅固定输入、schema 和 resources 所列 contract/lock。第三方 import 为已批准 D1 闭包，未提出新依赖。

### 1.2 七份 quality：同位置、同 canonical 名（固定 dbb；0475 中逐字相同）

固定 `dbb6b36e9259aa79a1fd908b5cfede3064f0c074`，前缀 `packages/engine/src/ontolearn_engine/quality/`：

| 文件               | bytes | SHA 前缀 |
| ------------------ | ----: | -------- |
| `__init__.py`      |   548 | 9a5130c2 |
| rule_profile.py    | 11987 | b40b73f6 |
| rule_terms.py      |  6176 | 218c4790 |
| rule_numbers.py    |  7372 | 6b080a55 |
| rule_calendar.py   |  4047 | 6a2e43b0 |
| rule_comparator.py |  1750 | 9a495876 |
| rule_firing.py     | 19149 | 5116aa3e |

仅 terms 相对旧 1e3 更新，完整 SHA 在唯一清单。机制 profile 为 `OntoLearn-rule-comparison-profile/1`，预算 `mechanism-budget/1` 不变。六 rule 模块的计算 import 闭包只含所列同包模块和 stdlib；父包四个旧 lazy exports 仍不可调用。**不接收 definitions、planning、rule_revalidation，不扩 root exports，不 collect-all/collect-submodules quality，不复制第二 matcher/比较器或 probe。** T05 保留维护权，T03/I05 只读接收。

### 1.3 唯一新包资产、D1 与批准基线继承

- 只把固定 `docs/iterations/I05/profile-probe-inputs.json` 原字节映射到包 `_MEIPASS/provenance/i05/profile-probe-inputs.json`。这是实际执行资产，不是旧 1840687B projection manifest；二者 JSON 值相等而原 bytes/SHA 不同。静态遍历实际资产只发现一个 `expectedIncluded` 字段且为 false，没有 expected 数据键。
- D1 只读保留 `packages/engine/pyproject.toml` 398B / `bcc8825b1f2902a66ae539e687df57e5b2554247f48a48a65215601a77958365`、`uv.lock` 28440B / `86dfe82d952e2c88edcfc5658f488f6e1f0d04b4ec3b1e6f5c5d3bc4f57e8b73`，来自 fd87；0475 两份也逐字相同。不再 resolver 更新，不加 B/XLSX。
- 批准 5f 的 `packages/contracts/python/contract_v2.py` 和 `packages/contracts/v2/{binding-regressions,dependencies,errors,fixtures,frame-fixtures,registry,schema,states}.json` 共九份原字节继承；0475 未改。打包仍按原映射 `contracts/python`、`contracts/v2`，保整个真实 `provenance/uv.lock`。不复制第二公共契约。
- 其余 14 份引擎基线源/data 为 `__init__.py`、`__main__.py`、contract_probe.py、coordinator.py、invalidation-v2.json、invalidation.py、job_store.py、memory_guard.py、process_environment.py、protocol.py、rdf_snapshot.py、storage.py、storage_probe.py、worker.py，均只读沿批准 5f，未采用 T01 新 runtime、其他任务/worker 接线。现有 `--collect-data ontolearn_engine` 保原必要 data，不收整仓 docs/tests。

### 1.4 同树实施与完整 5f 差异

现有 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-profile-build`、`feature/T03-profile-build` 可以作为候选组合目标：D1 两份已核逐字 fd87，D2 两份仍逐字 5f，只有保护 AGENTS 脏，未有 I05 源码。这只是可行性，**本件不授权接收**。建议根明确该树/起点 HEAD、只读采用清单和两文件施工窗口；I05 冻结树不改，未来维护分别仍属 I05/T05/T03。若根改用另一独立树，须重新固定实际 base/组合/ref，不能跨树拼绿。

运行/资产范围相对 5f 正好 **22 条**：D1 两份 + I05 十份 + quality 七份 + 唯一资产 + T03 D2 两份。完整路径已列入 inputs 的 `expectedPackageOnlyEngineDeltaPathsFrom5f`，其中 resources 是覆盖批准旧文件，其余新源码按固定 blob 接收；D2 两份会产生未来新字节，当前没有虚构其 SHA。桌面源码、公共 schema、Store/worker 和 B 面均无新差异。

为使同一组合的正常 check 实际覆盖新增语义，而非只跑旧 1052 Python，还需根逐项批准 **24 条只读验证文件**：0475 的 15 份 `packages/engine/tests/test_semantic*.py`、`tests/fixtures/quality/profile-v1/` 六份固定 fixture、`tests/fixtures/quality/real-executor-acceptance-inputs.json`、两份绑定文档 `docs/reviews/I05/profile-integration/{I05-profile-P1-fixed-inputs.json.raw,T05-profile-iri-approved-seven-inputs.json.raw}`。全名/bytes/SHA 在 inputs 的 tests/fixtures/bindingDocs，不能手改测试修绿。原 I03 boundaries 文档继承 5f。额外 19 份 T09 原件/manifest、FR505 扩展仅用于源引用追溯，另列 originRefsReadonlyNotAdopted，不因本件自动复制进 checkout 或包。

因此拟完整功能验证差异为 22+24 条，另加实际本线授权 docs/过程证据；已有 D1/接收记录 docs 继续保留，不是运行模块。外部 oracle 工具另在本线外部证据目录按下节固定成员提取，不作为产品或 pytest 模块安装。AGENTS 保未 stage；不是 whole-commit/cherry-pick 0475 的 117 条或共享环境。

## 2. 唯一入口与真实退出语义

### dispatcher（未来只改 packages/engine/entrypoint.py）

新 profile 路由先识别尝试调用该 flag 的 argv：仅完整单 token `--semantic-profile-probe` 有效。此单 token 移除后从 `ontolearn_engine.semantic_profile_probe` 导入同一 canonical main，并 `raise SystemExit(main([]))`。该 flag 与任何额外 token 混用（包括与 worker/storage flag 混用、位置颠倒）或 `--semantic-profile-probe=...` 均固定 stdout 空、stderr 精确 `PROFILE_PROBE_ARGUMENTS_INVALID` 加一个 LF（32B）、exit2，不进入默认 stdio/worker，不开放路径/JSON/脚本/URL选择器。只处理 profile 尝试，其他批准 5f 路由顺序和受限语义原样保留。

源命令为独立环境 `python -m ontolearn_engine.semantic_profile_probe`，零参数；源码的额外参数由固定 main 自己拒绝，保持同一错误字节和 exit2。不把 probe 文件按路径加载成另一个模块名，不另造 DTO、计算 wrapper 或测试 Job。正常包 flag 调用 main([]) 后保留其真实返回值。

### 固定预算、失败与外部监督

| 域                             | 固定合同                                                                                                                         |
| ------------------------------ | -------------------------------------------------------------------------------------------------------------------------------- |
| 输入                           | 精确 1839011B/SHA6c6ffc…；上限 2097152B，格式 i05-profile-input-projection/1，83 mathInputs，expectedIncluded=false              |
| 路径                           | 源仅 checkout/docs/iterations/I05/profile-probe-inputs.json；frozen 仅 _MEIPASS/provenance/i05/profile-probe-inputs.json，无回落 |
| 单次                           | payload+rows 原 8388608B；depth32/1M节点、rows≤10000、cell≤8192字符不改                                                          |
| 聚合                           | 67108864B；追加前逐完整 case 预检，预留 2097152B 元数据，最终逐 chunk 复核；不截尾                                               |
| 时间                           | 单次集合 120s，仅 case/输出边界检查；采集者必须对真实进程外部硬超时 120s                                                         |
| 完整采集                       | stdout 一个完整 JSON+换行；有 failure/not-executed 则 exit1，全部成功才 exit0                                                    |
| 非预期/资产/身份/时间/聚合错误 | stdout 空、固定 `PROFILE_PROBE_FAILED` 加一个 LF（21B）、exit1，不输出半个 JSON或原堆栈                                          |

显式 triples≤100000、入口文本≤1MiB、sidecar terms合计≤262144B、scalar≤16384B、图 1M work 与稳定 child 分池按固定源码保留。边界计时不是可抢占 CPU/内存上限，外部硬 timeout 才约束整进程；不要放大预算、删 source/false match/head 或缩资产来取 exit0。

采集器在产品外记录 argv/cwd/隔离环境、开始/耗时、pid/所属进程组、timeoutSeconds=120、timedOut、真实 returncode 或 timeout 时 null、完整 stdout/stderr 的 bytes/SHA。timeout 保留已产字节，只终止所属命令/有界子组，不宽泛清理用户进程。各命令单独收集，不以 `&&` 或 `|| true` 掩盖 probe 的 1；超时或半个 JSON 不能算完整对照。

固定历史 30/31 已只读解包并核原 manifest：30 实际 14006950B / `a16699f47c5fc8de6658d1dc5a1c422796daf0f3bb4dbed520ffce0577ed74e0`、stderr 空、exit1、未 timeout；31 外部 checker 也 exit1。全部逐 case 状态和原执行记录见 [historical-observation.json](../../reviews/T03/profile-D2-fixed-input-package-contract/historical-observation.json)，这是旧固定原件读取，不是本轮新运行。

- 78 success 的完整数学输出可对照；成功覆盖49/89图、24/40唯一 matches（15 accepted/9 false）、16 heads及R04叶 witness，不能说89图或40匹配全通过。
- E.5 round1/2：error=`RESOURCE_LIMIT/resource.limitExceeded/{resource:semanticInput}/retryable:false`；diagnostic=`RULE_INPUT_BUDGET/resource/ruleId:R-risk/location:null`。round3/4：resource=semanticWork；diagnostic=`WORK_LIMIT/resource/ruleId:null/location:null`。四项均 failure、无 result，不是 skip 或成功。
- transfer:repair：not-executed，reason=`ORIGINAL_INPUT_CONTEXT_INCOMPLETE`，原输入无规则；fullOriginalInputContext=true 这个元数据不能替其 eligible=false。禁止继承 R-risk/空规则“补绿”。

## 3. 精确源码/包等价域

先独立核每份 stdout 为无重复 JSON key、无 NaN/Infinity 的完整文档，集合83条、caseId唯一且顺序等固定资产。按递归精确类型/值比较；字典键顺序不参与语义，数组顺序/重复项参与，不把 bool 与 integer 混同，不解数值字符串、不将 missing 当 null。

**业务 JSON 唯一允许差异如下，逐项先验证预期值后再从比较投影中剔除；不得删除整个 identity。**

| JSON Pointer                        | 源                                             | 包                      |
| ----------------------------------- | ---------------------------------------------- | ----------------------- |
| /identity/frozen                    | false                                          | true                    |
| /identity/resources/frozen          | false                                          | true                    |
| /identity/modules/0..6/sourceSha256 | 对应 dbb 七份实际 .py 完整 SHA，顺序等 MODULES | 全部 null（冻结字节域） |

七个 `/identity/modules/*/module` 与顺序必须相同且是固定 canonical 名。除此之外所有 JSON 字段逐值相等：顶层 format/scope/counts/inputBytes/inputSha256/limits/collectionComplete，四个非通过声明，productCases/learningChecks/originalOperations/unresolvedInputContexts/nonClaims；83 case 的 caseId、sourceRefs、输入投影摘要、上下文、scopeNotes、purpose、status 及全量 result/error/diagnostic/reason。未知新增字段也参与比较，不允许随意忽略。

success 的完整 payload（含 reasoning 全树）、rows 和两个摘要全比较：rdfs/rdfsEvidence、warnings、catalog、definitions/顺序/版本/摘要、rules、graphBudget、termSources全部 occurrence/pointer/digest/revision/text/span、proofLeaves、mechanismBatches、originalMatches 全 true/false bindings/when/proof、accepted firingGroups/all heads/evidence/basis、完整 typed bytes及其 digest，均不剪枝或改序。False ComparisonEvidence 当前没有载体，不能声称独立验了不存在的 false operand trace；已有 false original match 及无 firing/head 必须保留。

每 case 还按源码同一编码域独立复核 payload UTF-8 canonical JSON 的 jsonPayloadDigest、完整 rows 的 rowsDigest、rows拼回payload、batch payload hex/SHA和全尾行；不能只比较数量或一组摘要。输出 bytes/SHA 原件分别保存，因上面七 null/两个布尔有差异，不强求两份 raw stdout 同 SHA。

实际 identity 的其余内容**不能作为自由差异**：八 distribution 名/版本逐一等 D1；contract resource 九 hash/registryHash 和完整 lock hash逐字绑定。`identity.resources.implementation` 必须仍是 `i04-infrastructure-v1/0.1.0/86dfe82d…`；success 每个 `payload.implementation` 必须是 `i05-finite-7/0.1.0/86dfe82d…`，与实际 semantic_identity 分支一致，不能把默认 runtime 身份升级成 profile 已正式注册。源码路径/构建平台、工具版本、engine/PYZ/pyc/最终 app 文件 hash 只记外部构建证据，不混进业务比较的任意豁免域。

源码/包等价通过至多说明固定合同重现；两边同样的四资源失败仍失败。**外部 oracle 的完整对照另作一项**：从固定0475 `oracle-comparison/original-evidence.zip`提取 compare_oracle.py（26097B/32067f2a…）、input-manifest-v2.json（1840687B/7c24323e…）、project_inputs.py（23730B/c93d284c…），另用固定 oracle767826B/87220503…；完整成员和容器SHA见inputs。checker在产品外读expected，纯输入资产只按 JSON 值与原projection校验。分别对新的source stdout与package stdout调用同一checker，source-style固定short-no-revision，原style不放宽；保存两套actualArtifact SHA/coverage/逐83项结果/真实exit1。不能把checker的78数学一致+4failure+1not-executed改称整体业务通过。

## 4. 仅两产品文件内的构建改动合同

未来 T03 只写 scripts/build-engine.mjs 和 packages/engine/entrypoint.py；D1/十源码/七模块/输入只读。以 Node fs/crypto 在 build-engine.mjs 内校固定清单，生成只读 `build/profile-d2/provenance/d2-build-inputs.json`：明确实际组合 ref、每源/asset/contract/完整lock bytes/SHA、Python/PyInstaller版本、八发行 metadata/许可证记录和实际构建参数。可由脚本 `spawnSync('uv', ['run','--frozen','python','-c', 固定内嵌元数据读取代码])` 获取 importlib.metadata/files/hash；它只读构建元数据，不 import 产品、不跑计算。JSON再 add-data 至 `provenance/d2-build-inputs.json`；不新增 C4 inventory 脚本，不造第二业务 probe。

清单是构建前输入承诺，不能自包含最终 engine/PYZ hash。最终 engine、实际归档和 provenance 的绑定放产品外收据；严禁用自报 SHA 代实物。出现输入未知 WIP/缺字节/未获根消费批准即停止并报具体路径，不改其他owner文件补洞。

PyInstaller 配方保5f uv frozen/clean/onedir、输出隔离、rdflib collect-all、engine必要data、原contract/lock资源；在此最小增量：

- 明确 hidden-import 十份 canonical I05 模块和七个 canonical quality 名字；不以通配符代实际17名，不收整engine其他新业务包。
- 补 collect-all pyshacl、owlrl、html5rdf；prettytable/wcwidth/packaging/pyparsing代码由真实导入闭包及必要明确 hidden-import收集。八distribution逐项 copy-metadata，保原rdflib/pyparsing项；recursive-copy-metadata pyshacl仅辅助，不假定覆盖extra。全部实际数据需求按安装分发文件和TOC核，不为遗漏再安装未批extras。
- 对每个实际dist-info的LICENSE/LICENCE/COPYING/NOTICE及licenses子树建立固定相对映射，保全文与归属；copy-metadata已含的文件不重复造修改版。若尚未被带入，则在同一build脚本中逐个add-data至只读licenses/distribution/相对路径。实际包必须有八库代码/metadata/所需data/许可，不能用源venv存在背书。
- add-data唯一1839011B固定资产和构建输入provenance；明确exclude-module quality.definitions/planning/rule_revalidation。凡实际调用排除服务失败即返owner/root，不stub、不吞必需缺失错误“修绿”。

## 5. 实物归档、未多收/缺失/alias的证明链

以下方法仅合同，本轮没有执行PyInstaller或归档reader。固定工具来自D1的PyInstaller6.22.3；已只读其本地archive_viewer/reader源码核CLI和读取API。未来在同一组合/解释器记录工具实际版本及SHA。

1. 构建前校17源/资产/九contract/uv.lock及14基线引擎源/data；保每项源码原bytes SHA。记录实际venv distribution/WHEEL/metadata/许可身份与完整闭包，normal import分析不能自动证明extra资源完整。
2. 保存新build的Analysis-00.toc、PYZ-00.toc、PKG/COLLECT TOC、xref/warn、真实argv/env/exit及新engine字节SHA。以 `pyi-archive_viewer -l -r <实际engine>` 另输出实际CArchive及PYZ完整目录；不能只读build输入清单。
3. 产品外用CArchiveReader打开实际新engine，再open_embedded_archive读取实际PYZ；对各entry保存canonical名/type/偏移/长度/提取后原始marshal字节SHA，读取不exec产品code。先从PKG/PYZ原始TOC顺序记录统计名字/重复数，再同reader映射核对；不能让reader转dict时覆盖重复项。连同onedir文件树检查：quality恰7名、每名唯一，无definitions/planning/rule_revalidation、无对应.py/.pyc/别名文件或额外源目录；I05十名各存在，engine新增代码仅批准集合，旧baseline额外闭包必须逐项能归5f，不允许整C4新业务模块混入。
4. 为连接源与冻结字节，对17份实际源码用同解释器、实际优化级别编译但不执行，按PyInstaller实际filename变换核code对象；仅递归规范化co_filename这个路径元数据，保其他code/常量/嵌套code/行表/qualname，分别算规范代码指纹。与实际PYZ提取code逐一比较；全归档也按指纹查同份quality代码被重复装成其他模块名。若PyInstaller还有其他实际变换，先保存差异并精确评审，不能扩大规范化抹去逻辑差异。原.py SHA、marshal/PYZ/最终engine SHA始终分域，不能要求相同，不能伪报inspect恢复.py。
5. 从最终unsigned应用extraResources的实际engine再次核hash/目录/归档，与本轮build副本绑定。直接核其_internal内资产、完整uv.lock、contract和八dist-info/许可原bytes SHA；路径以实际onedir布局确定，不虚构未来路径。构建输入provenance全文+hash从包内实物读回，与外部输入/TOC收据逐项比。资源清单必须实际命中原字节，不以“清单打印了期望标签”为证据。
6. 包内唯一probe的七模块name/spec检查、同一真实reason的成功机制发行与源码/包全输出等价，补实际使用路径的同模块/精确类约束证据。它没有打印任意全部class对象，故不声称仅凭names已证明一切动态alias；结合实际归档规范名唯一、全代码指纹/源码检查排除另装实例。发现无法由现有证据关闭的身份缺口返根，不新增第二产品probe或monkeypatch sys.modules。

以上是可执行核验链而非当前包通过。metadata/许可或模块一旦缺失，保首失败和最小两文件修复，形成新候选并必要复验/新审；不改固定业务预算或原数据。

## 6. 后续批准后才运行的同树命令与采集顺序

采用集合及两文件实现须形成一个新固定实际组合HEAD，再开始下列验证。每条单独保存原命令/终态/完整输出，不能复用0475历史绿或D1独立环境结果冒称新组合绿。新环境/缓存/日志/输出独立，npm ci保锁，uv只sync --frozen；不更新锁。当前本轮均未执行。

| 顺序 | 实际命令/检查                                                                                 | 需要保留的证据与解释                                                                                                                                                                                                                                                                                        |
| ---- | --------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1    | 同组合 `npm run check`、`npm run verify:sources`                                              | normal lint/format/types/TS/Python/build与源12；实际收15语义tests后才算其回归；失败原件保留，不删测试换绿                                                                                                                                                                                                   |
| 2    | 外部hard120s监督 `.venv/bin/python -m ontolearn_engine.semantic_profile_probe`                | 完整source stdout/stderr/真实exit，83状态、固定资产与identity；预期完整采集exit1                                                                                                                                                                                                                            |
| 3    | 产品外固定checker分别对source实际输出作全量oracle对照                                         | 上节固定四依赖；coverage/逐83actual/checker真实exit1；不宣称全业务通过                                                                                                                                                                                                                                      |
| 4    | `CSC_IDENTITY_AUTO_DISCOVERY=false npm run package:dir`                                       | 正常新unsigned目录包；配置本已mac.identity=null，不读Keychain/签名凭据，不自动启动App；保存build与pack原件/新产物全hash                                                                                                                                                                                     |
| 5    | 实际最终应用extraResources/engine/ontolearn-engine（Windows为.exe）`--semantic-profile-probe` | 仅CLI；外部hard120s；新raw全量/实际资源/归档证据；不启动Electron。macOS实际目录从产物枚举确定                                                                                                                                                                                                               |
| 6    | 源/包各零参数与额外参数矩阵；flag与其他flag前后混用、空外部JSON路径、URL、任意token           | profile尝试stdout空/固定stderr/exit2；源多参同合同；不接受外部输入、不落默认服务                                                                                                                                                                                                                            |
| 7    | 外部递归精确比较本节source/package JSON，再对package输出独立跑同checker                       | 只有两个frozen和七null差异；完整业务/失败/identity逐值相等；记录equivalence和oracle两项独立结论                                                                                                                                                                                                             |
| 8    | 同新包 `--contract-probe`、`--protocol-resources`、`--storage-probe --scale 1 --trial 0`      | 前两者与同组合源码 `python -m ontolearn_engine.contract_probe`、`python -m ontolearn_engine.resources`比较真实合同/资源身份。storage源 `python -m ontolearn_engine.storage_probe --scale 1 --trial 0`，保完整结果/查询/Store一致性；耗时、RSS、临时DB页数等实际环境度量单记，不要求跨运行相等或据此量化改进 |
| 9    | 实际最终engine/PYZ/资产/contract/uv.lock/metadata/许可/源码收据读回                           | 按§5把最终app、独立build、实际归档和输入绑定，不只测build目录CLI                                                                                                                                                                                                                                            |

CLI运行cwd使用本轮独立外部工作目录，清理外部PYTHONPATH/可变注入；静态核frozen locator与实际_MEIPASS只读数据/无checkout symlink。不得修改I05冻结资产或删除他树文件来测试fallback。负例、缺资源或超限测试若需要修改副本，须另由根授权具体只读产品副本/隔离目录/矩阵，不能破坏最终受审包或伪造失败。

外部checker具体argv（在根最终批准的同组合root解析相对路径，未来才提取/执行）：

```text
.venv/bin/python -I build/profile-d2-external/compare_oracle.py
  --oracle tests/fixtures/quality/real-executor-acceptance-inputs.json
  --inputs build/profile-d2-external/input-manifest-v2.json
  --projection-code build/profile-d2-external/project_inputs.py
  --executed-input-asset docs/iterations/I05/profile-probe-inputs.json
  --actual build/profile-d2-evidence/source.json
  --source-style short-no-revision
  --coverage-out build/profile-d2-evidence/source-coverage.json
  --comparison-out build/profile-d2-evidence/source-comparison.json
```

上述多行为一条argv，不是可直接按行拆跑的shell脚本；采集器解析为参数数组、shell=false。package对照只将actual换成package.json、两个输出分别换成package-coverage.json/package-comparison.json，四份固定依赖和实际输入资产保持相同，外部120s监督。提取前后核容器/成员SHA，不执行projection的project()/Inputs加载器、不重生成输入；checker只调用其既有definition输入格式映射。预期checker exit1也须原值保存。

D1正常回归及同输入CLI通过不代Windows/macOS两个目标平台/干净设备、窗口/真实无响应/安全存储/B1，Linux不替代目标平台。本机不运行Electron/e2e/native/HMR、不抢焦点、不用凭据或付费入口。指定同版ZCode GLM-5.3最高和MiniMax M3.1-Flash/xhigh双新审、双方真实通过后push/PR、实际CI/正常develop合并/远端核验，以及I05/T03完整父范围全部保留；本件不建立桌面预约或假称队列运行。

**下一授权需根明确：** 0475受限收口对应的实际组合树与起点、18条只读源码/资产接收、24条source-only验证接收及外部四依赖的精确提取路径、T03仅两产品文件施工、必要外部采集/归档比较证据脚本目录与执行范围。没有这些不以本件自行施工；若根审计改变任何固定输入，重绑定清单和受影响合同，不能沿用本轮旧SHA当新组合证明。
