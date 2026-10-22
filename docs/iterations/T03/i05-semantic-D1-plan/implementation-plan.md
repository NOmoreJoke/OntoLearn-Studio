# T03 I05 D1 精确实施方案（首审修订，待独立delta复核）

2026-10-22。此交付只完成 D1 **方案准备**：固定 D0 协议的精确采用面、真实四 writer 基线差异、依赖/锁方案、D2/caller 协作接口、验收与后继运行门。没有产品修改、安装、resolver、build、编译、probe、fixture、原件解码或运行结果。D0 有限设计收件不等于批准本方案，也不等于批准任何组合、源码采用、工具、运行或平台。

## 1. 已裁定技术方向与精确采用前置

1. **基线与职责冲突先于实现。** 初版文档基于 `c3eb0694daad26527cc3a1eb0127ed5033f2be25`；本修订基于首审封存 `d014b925e2c9bb246a71621a919d7f9a412f6c57`，四 writer 仍逐字等原批准 `5f910b52c69d86a1076b2032e5d3c63e715947f3`。profile 已限定收件产品 `a4d1457fc6a1f1d1832296a8dcdb2ef42da75b98` 的四 writer 与当前树 `56a852321d72c6665044242d24064bf3523302d3` 相同；S1 产品 `0ad7e0a75cc4583918b057885631934c0a9bd859` 与候选 `30319412daf8ae4745987babf7bbed93c53b6b42`、过程 `3c396070c74fbf09cf319b0230c6f96ed2858482` 的四 writer 相同。限定收件的代码原件和过程身份不自动构成正式集成 base。
2. **23/26 锁冲突。** profile 依赖基线是 3 个直接依赖、23 包完整 workspace/dev/build lock；S1 是含 XLSX 的 4 个直接依赖、21 包 lock。保留双方功能的直接依赖是 6 项、包版本集合为 26 项。固定 D0 CR-S 明文要求完整 **23 包锁**。不能删 `openpyxl/et-xmlfile/defusedxml` 凑 23，也不能把 26 视作 D0 自然允许。控制方已明确技术组合保留全部 XLSX/semantic 依赖、采用26包设计；精确组合仍须前向协议 delta、新精确 descriptor/锁采用与独审；旧 D0 66 文件原字节不改。
3. **Git 观察不等批准。** 当前 local `develop` 实际为 `1b6df7a220fc9a67d7046133a340085f03f0a96c`，主题 `Merge pull request #2 from NOmoreJoke/feature/I01-storage-invalidation`；现行 common 仍明确批准 `5f910b52…`。两者的 build/entrypoint 已不同，具体原差异见审查目录 `develop-writer-diff.md`。控制方已实际 git ls-remote 核远端正式获批 develop=5f，确认local1b6是旧I01祖先；作者普通Git静态核is-ancestor exit0，未联网复验。无需fetch/reset/checkout或等待新基线批准。本方案沿正式5f记录差异，不从local ref推批准。
4. **接口维护者不同。** T03 唯一拥有四 writer；D2 的 consumer、semantic/resources 未转 T03。caller 外部信任/验签/收据维护和 root 的批准原件也不属四 writer。此方案为其列出可审查输入输出，不在其源码抢写实现。旧 tests、CI、T01 contracts/Store 等也没有扩大授权。

**控制方最新技术裁定：** 正式基线5f无需重新申请；组合保留 S1 三项 XLSX 与全部 semantic 依赖，逐包核两固定锁来源/版本/artifact hash/许可缺证，设计全集26。a4d仍只是已收语义材料、不是正式集成base；不能盲目拼接两份锁。后继精确采用必须落实前向新profile/CR-S/lock-count、四schema/字段职责/manifest/consumer mapping及独立审查；proposal版本3.0.0的完整delta设计见 forward-protocol-delta.md。当前不生成实施锁或新组合/consumer pin，不继承旧指定Pass。

## 2. 固定 D0 采用，不以本方案摘要替代合同

完整规范是下列 **c3eb0694 固定文件原件**；每个字节身份见 `readonly-input-manifest.json`。消费者须同时遵守 JSON Schema2020-12 strict shape 和 protocol/consumer 所有跨字段规则，不能只检 required 或数量。本方案只安排落地步骤，未复制/重写旧 schema。

| 完整文件                                                      | 固定版本 / 用途                                                                             |
| ------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| `docs/iterations/T03/i05-semantic-build-protocol/protocol.md` | 2.1.0；CR-S/A1/A2/C/A3/A4/R/H                                                               |
| 同目录 `consumer-contract.md`                                 | 2.1.0；source/frozen/caller 精确合同                                                        |
| 同目录 `build-provenance.schema.json`                         | `i05-source-package-parity-build/2`；ID `urn:ontolearn:i05:source-package-parity-build:2`   |
| 同目录 `build-receipt.schema.json`                            | `i05-build-receipt/2`；ID `urn:ontolearn:i05:build-receipt:2`                               |
| 同目录 `runtime-validation-receipt.schema.json`               | `i05-runtime-validation-receipt/2`；ID `urn:ontolearn:i05:runtime-validation-receipt:2`     |
| 同目录 `runtime-header.schema.json`                           | `i05-semantic-runtime-header/1`；ID `urn:ontolearn:i05:runtime-header:1`                    |
| 同目录 `profile-descriptor.json`                              | `i05-semantic-build-protocol-profile/3`；批准 pin/null/空仍保持未批准                       |
| 同目录 `field-responsibility.json`                            | `i05-d0-field-responsibility/3`；四 schema 全部 1241 显式 property pointer（含 union arms） |

作者完整读取 protocol/consumer/descriptor；四 schema 全量内容读取时仅将完全相同的重复子树指向已展示的原 schema JSON pointer，没有摘要替代字段。随后按完整 JSON 递归静态核 propertyIndex：provenance669、build receipt56、runtime receipt366、header150，合计1241；唯一/全集/required/shape（type/const/enum/$ref）全同。该静态索引不认证 JSON Schema 引擎或真实证据。

D0 final-manifest 为当前 66 文件包的外部身份入口；它是设计交付清单，不能作为 build receipt、caller 信任根或运行通过凭据。root closure 只有限接收 D0 静态设计；本方案不补写其未审运行与资源。

## 3. 四 writer 的最小改动设计

下述是 **后继授权实施的精确变更面**，此交付不做变更。四文件每个原 bytes/SHA/gitBlob、全部实际 refs 和 current 等同性见 `baseline-comparison.json`；完整原依赖锁文本按包无损分块保存在 `dependency-plan.json`。

### 3.1 `packages/engine/pyproject.toml`

独立语义依赖候选以 a4d 当前398B/SHA `bcc8825b1f2902a66ae539e687df57e5b2554247f48a48a65215601a77958365` 为只读材料，保 Python `>=3.12,<3.13`、包名/版本/script/backend/description。直接依赖固定 `pyparsing==3.3.3`、`pyshacl==0.30.1`、`rdflib==7.6.0`，不把全部八个 runtime 都升级成无理由的直接依赖。

root 已裁定正式组合保留 S1，拟直接依赖按名字排序为 `defusedxml==0.7.1`、`et-xmlfile==2.0.0`、`openpyxl==3.1.5`、`pyparsing==3.3.3`、`pyshacl==0.30.1`、`rdflib==7.6.0`。S1 原顺序调整只有 root 组合候选可做；不默删安全 XML parser 或间接声明。仓库根 `pyproject.toml` 的 workspace/dev 约束不修改，除非 root 独立扩权；现有 hatchling build-system 约束也不借 D1 重构。

### 3.2 `uv.lock`

语义候选使用 a4d 已有28440B/SHA `86dfe82d952e2c88edcfc5658f488f6e1f0d04b4ec3b1e6f5c5d3bc4f57e8b73` 的 **完整23包**作为精确设计基准，不以 resolver 重建、手写 hash 或“当前最新”替代。18 个 old5f 包加 `html5rdf1.2.1/owlrl7.6.2/prettytable3.18.0/pyshacl0.30.1/wcwidth0.9.2`；`ontolearn-engine` dependencies 和 metadata.requires-dist 与 pyproject 三项完全相同。

runtime 八包为 rdflib7.6.0、pyshacl0.30.1、pyparsing3.3.3、owlrl7.6.2、prettytable3.18.0、wcwidth0.9.2、html5rdf1.2.1、packaging26.3。边：pyshacl→owlrl/packaging/prettytable/rdflib[html]；owlrl→rdflib；rdflib→pyparsing；rdflib optional html→html5rdf；prettytable→wcwidth。不能丢 html extra，因为当前 checkout 不直接导入 html5rdf。

root/dev/build 全闭包也保留：pyinstaller6.22.3、hooks-contrib2026.8、setuptools84.0.0、altgraph0.17.5、macholib1.16.4（darwin marker）、pefile2024.8.26 和 pywin32-ctypes0.2.3（win32 markers），pytest9.1.1/ruff0.17.1 及测试依赖。完整列表/每包原 block 中的 registry、sdist、所有 wheel、hash/size/upload-time、platform marker、extras、workspace metadata 逐字保留于 dependency-plan；不是只列八个包的快照。lock target `==3.12.*` 与 workspace `>=3.12,<3.13` 一致。

S1 原 lock23393B/SHA `9f5b6d2b93d994a3e4f8a46ce5cccae99d4e024ea7531ab62dd8e85d6aa1152e` 另保三个包及 openpyxl→et-xmlfile。组合按控制裁定保26包版本全集：18共有包无版本/artifact hash冲突；exact block差异有ontolearn-engine依赖metadata、rdflib html extra、setuptools尾空行，不能只按同名版本盲并；许可未在lock中提供且未读实际原件。详见union-source-audit。但 **resolver 兼容、实际 artifacts、安装依赖与运行未经验证**。后继精确组合采用阶段再选择获准 resolver/版本、明确离线/联网/缓存权限、刷新锁并保真实stdout/stderr/exit及首错；不得把本方案的集合并集当作真实 lock bytes/hash。之后由独立 reviewer 核 requirements/markers/extras/全平台 artifacts 和 bootstrap工具，再形成真实 dependencyRef，不能预填。

### 3.3 `scripts/build-engine.mjs`

不能把 a4d13264B 的整份 profile wrapper 复制到 S1 或 develop。其 default 包含43 fixedInputs guard、旧 `sourceRef=0475d0…`、17 module profile采集、旧 contracts/v2 glob，且 guards 的 pyproject/lock 已锁三直接依赖字节；S1 whole-file replacement 又会删这些 guard。后继由唯一 T03 在 root 明确组合候选中做最小函数/分支合并：

1. 先对 **完整 argv** 分派。新 dedicated flag 只接收单独 `['--i05-source-package-parity']`；重复、`=value`、额外参数、与默认/其他flag混用应在任何安装、metadata或build子进程前拒绝。此是 wrapper 新设计，不伪称当前 wrapper 已实现，也不在本票调用。
2. 旧43到新33共享22路径，其中13同字节、**9冲突=2依赖+7源资源**；另old-only21/new-only11，合并加mapping4为拟parent/default58。完整逐项身份/owner/采用/guard版本/旧入口回归见 `guard-scope-matrix.json` 与 `guard-migration-strategy.md`。历史a4d scope保原43+原wrapper/entrypoint共45路径，另批独立source/output根按原无参build和旧83项profile入口可复现；新parent/default-v3用完整58 guard，新semantic-v3用33，不能在同一checkout要求9冲突的两版字节同时成立。21old-only须原owner供兼容/移植真实pin；不删guard、不glob、不把旧flag永久拒绝称保留。
3. 新分支以固定 descriptor 的23 canonical、四T01 resources、两I05 assets、四writer组成33 distinct source paths，另列精确 descriptor/schema/批准collector工具身份。前后 Git clean、ref/path/blob/bytes/SHA逐项实核；pyproject/lock在inputs和writers两账完全同值。AGENTS保护M不冒成输入dirty；其它guarded path真dirty即拒绝。固定source22不借wrapper维护。
4. 专用 target=`packages/engine/src/ontolearn_engine/semantic_source_package_probe.py`、name=`ontolearn-semantic-parity`、onedir、`--contents-directory _internal`、`--optimize 0`。规范 descriptor 隐藏导入顺序/集合精确照录，collect-all只rdflib/pyshacl/owlrl/html5rdf，metadata八包，canonical23加prettytable/wcwidth/packaging；排除descriptor完整12项，特别移除旧profile对rule_revalidation的排除仅限新分支。严禁 collect-all engine/quality、collect-data engine 或 contracts/v2 glob。
5. 仅逐文件 add-data：四contracts对应 `contracts/python/contract_v2.py` 与 `contracts/v2/{schema,registry,errors}.json`；两probe_inputs资产到 `provenance/i05/source-package-parity/`；同一批准 `uv.lock` 到 `provenance/uv.lock`。不带 states/dependencies/fixtures、旧profile输入或外部 oracle；T01 resources新原件与旧default contracts不能互换。
6. 新输出的 dist/work/spec/cache/evidence/log 根由 root 另批唯一 `{compositionRef}/{platform-id}` 前缀，不得复用旧 `build/engine`、`build/pyinstaller`、`build/profile-d2` 或仅以当前cwd形成授权。schema提到根ID不授权真实目录。`shell:false`、受审参数数组、退出/信号/stdout/stderr原件保全。任何真实新 layout 不合D0闭包先保首错做前向delta，不能动态放宽。
7. 新四writer中的 wrapper只编排批准source/collector，不内嵌第二套 permissive schema、动态读取外部 locator 或把已接受D0文档当获准执行配置。精确collector/archive/RECORD/许可工具属于D3后续票，源码位置与身份由root先批准；本方案不写reader/helper/spec/builder工具，也不复用未经批准I05/I06实现。wrapper接入前须fresh review工具自身与调用方。
8. E0后由外部collector按D0顺序插入唯一 provenance，包外directoryManifest/buildReceipt再后出。不能在打包前写假最终 provenance/hash，不能以旧profile `d2-build-inputs.json` 代新完整 schema，不能在build阶段加入runtimeLoaderCode或通过状态。

三scope具体入口、旧profile83项/限额/报告非claims与9项冲突全SHA表在 `guard-migration-strategy.md`。新parent无参default分支只有全58逐项owner采用、新26锁/consumer/writers实际pin及旧入口迁移验证均到位后才能获批构建；历史root不混26锁或6891源，单独保留旧功能，不把其旧运行证据继承给新scope。所有未来实际guard/composition pins仍null。

### 3.4 `packages/engine/entrypoint.py`

a4d入口1232B与S1入口1232B的SHA分别 `9abf0c22943cfae9f6f43893586626027bf9f4fc7318100465c0179aba69fe31`、`7653ddf2d0dda19f1a12b1ed93afa694f722f84d7ec95d979d33268d946afc47`；同字节数不表示可互换。root后继组合须通过逐owner迁移保 profile exact flag guard、S1 mapping guard/受限错误、storage/worker/contract/resources和default路径。旧profile在新parent调用同canonical旧profile模块main([])，不换成full417；83项原asset/报告false/失败exit语义不弱化。I05/T01提供与新七源资源兼容的实际probe/资源/旧only源码pins并验证，未完成parent不获批，不称已保留；历史独立root的原flag保持明确可复现入口。

新 canonical probe 自身是独立 frozen target；parent入口另增加受审精确分支：最早在任何默认business/types导入前检查任意位置的 `--semantic-source-package-probe` 或其`=…`形式，再仅允许完整两项三数组之一，传给 **同一个canonical consumer main**。不修改argv后交默认main、不吞额外参数、不靠prefix接受重复、不新exec alias。D2须明示canonical main的实际调用签名和argv责任，T03只配合分派；不凭旧2cf推未来签名。exact非法argv按D0前置exit2，原受限stderr与真实数组由caller保留；本方案不自创新安全码。parent runtime模式需D2提供明确模式来源，不从构建名称猜测；其root批准build/wholeparent证据另收。

## 4. 源码22 / 实际23 / self-pin与固定资产

`profile-descriptor.json.canonicalModules[0:22]` 的22项供源由既有 `6891a5842302859a531cf82767c5a482417bc274` 固定，原owner保留维护权。每项完整ref/path/bytes/SHA/blob在 readonly-input-manifest，已用普通Git原bytes核同；没有import或运行。T01四资源同该供源并受既有 adoption `dd972b79adf4d378636a7d41a6b0e3e08c0d5ca1` / process `79d63cc1f403ee857a3af2a98f8870db9a6a910d` 约束。两assets按descriptor固定2cf源与原bytes，417/320等实际业务payload不在本票重算/模拟。

第23 `semantic_source_package_probe.py` 的 `2cf0c3328de464e15a3fa9cdbfdf6aa88d0b4a64`、93848B、SHA `b3456f021afdbd53ec8677bf317a5ffdff636b55bae760eb8b7fec6e399e41b9` 只是已收 source-only 的 **consumer祖先**。D2按新strict header/失败合同必有代码delta；新actual consumer commit/bytes/SHA/blob必须完成D2后由owner外报并经root接收。不能把此旧SHA写为未来approvedConsumerPin或让consumer内嵌自身新hash。

source header声明仅固定前22；source实际loader观察23，source23 actual bytes/SHA/code由caller用包外root批准新pin核回。frozen声明inputs.modules共23（新consumer来自实际新ref）；其模块actualSource和observedSource23为null，因为包内没有原source证据。bootstrap是另列 `bootstrap-main` 不计入23；`distribution:pyshacl.validator`亦另列，不计入23；前三semantic函数和Validator.run共四绑定。绝不把23变成24/25混计。

## 5. 协作前置与任务依赖

| 步骤 / 维护者                | 精确输入                                                      | 必须交付与后继依赖                                                                                                                              |
| ---------------------------- | ------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| P0 root                      | 本方案、四writer实际refs/hash、D0固定合同、S1/profile限定收件 | 明示集成base与依赖23/26裁定、四writer改动范围/9冲突+21old-only逐owner采用、33/58/历史45 guard与旧入口迁移、前向协议采用路径；未批准继续保持null |
| P1 T03（D1实际依赖票另开）   | 正式5f与P0批准精确组合采用、真实pyproject/lock                | 只依赖配置/实际锁候选与完整差异、首错/验证；dependencyRef由实际commit后外报；不含runtime成功                                                    |
| P2 I05/D2                    | 固定四schema/descriptor及P0 delta、新批准依赖                 | canonical consumer严格解析/header/错误合同；新source23实际pin、mode/调用签名、责任接收与fresh独审。未完成前wrapper不能绑定旧hash冒新码          |
| P3 root/caller维护者         | 根信任入口、严格合同、P2 interface                            | prelaunch验签/批准绑定和postlaunch header/失败receipt收集的独立实施票与审查；不能由probe自批，也不授权T03抢源码                                 |
| P4 T03/D3及root指定工具owner | P1/P2/P3已收版本、完整D0/前向delta                            | 四writer最小分派/guard/collector接线，真实工具源码pin/CLI协议、全静态审查与独审；禁止用D0示例/selfcheck作工具证明                               |
| P5 root E0资源窗             | 精确composition/source33/工具/证据根/平台工具链               | 批准构建环境/资源/安装网络策略/输出根/费用/停止界限后才真实build；原件→provenance→directory→buildReceipt；root独立核批                          |
| P6 caller+I05 E1/E2          | 已批准同一buildReceipt和实际原件                              | source/frozen/parent分别按scope启动；fresh/cold/warm loader/完整JSONL、失败原件、独立外部比较；另出immutable runtime receipt                    |
| P7 root正式门                | P6 scope结果和原parent/B1/S1差距                              | 完整指定模型双方独审、目标两OS/CI/真人/develop等原门，各自真实验证，不能由D1完成自动关闭                                                        |

P2/P3接口设计与P1静态方案可并行，运行不互相等待来授权；P4采用和P5/P6真实运行必须等其全部精确依赖到位。另有旧profile/default迁移依赖：I05负责旧83项probe，T01负责新CONTRACT及已转路径，其余原owner按完整58矩阵供兼容实际pin；T03只维护四writer，不自行修共享源来使guard通过。root若调整owner须先具体交接，不能拿本表作自动转权。

## 6. 验签/批准绑定入口（caller与root的后继接口）

D0没有定义密钥、证书、公钥指纹、签名算法或现成验签函数。**SHA256只是完整性，不是授权签名。** 本方案将“验签入口”明确为caller的外部受信批准接收边界：root另指定可信记录来源及其认证/签名机制；如采用数字签名，密钥来源、算法、canonical message bytes、rotation/revocation和负例须另审，不能此处发明已存在签名。

caller后继入口的输入必须是root受信渠道提供的批准记录原件身份（现存ref/path/bytes/SHA/blob）和其绑定的同一build receipt、profile、composition、source/dependency/wrapper/consumer/toolchain/evidence根身份；不是从bundle/header给出的locator加载。接口语义名可称 `verifyApprovedBuildBeforeLaunch`（**拟定语义，不宣称现有API**）。入口先验证信任来源/签名（若root选用），再严格解析四schema和全部跨字段规则；无批准、失败、域外路径、输入/目录差异均返回not-started与D0 exact code，不能dispatch子进程。

预启动核验：完整源33与新consumer、descriptor/collector身份、RECORD/artifact/许可/工具已审全证据包身份、最终所有普通文件的root exe/provenance/directoryFiles和目录manifest、无别名/软硬链接/escape、闭archive表/父子raw witness、Python和code域、四function/checker分域全部同批准值。caller可接收root已审且hash闭合的固定包，但必须亲核该包原bytes身份和完整目录；不能只信approvalStatus字符串、exit0或一张receipt截图。验证成功返回供 **一次确切启动** 使用的不可混用批准上下文，context必须保build receipt原hash，不改原收据。

postlaunch入口（拟语义 `bindRuntimeEvidenceAfterLaunch`）把原stdout/stderr/headerRaw/terminalRaw/实际argv/exit/signal同该预启动上下文回绑：exact shape→保真实partial/failure→headerPayload逐字段投影→完整有序observations→独立scope比较→后出runtime manifest/validation receipt。launch后再找批准不能补救prelaunch缺口；caller拒绝不能伪造成child exit2。比较器与oracle来源、comparisonReport须独立真实版本，sourcePackageEquivalent/externalOracleMatched/originalOperationPassed互不等价。

## 7. 当前完成状态与停止边界

初版只读81清单与原delivery-manifest/author-checks保持首交历史，不能继续声称81个live快照当前全匹配。首审实际candidate为 `ae28572c91b78933c35996f0d80e81c03b96edf0`，报告已在d014封存，结论NEEDS_CHANGE，F1/P2与F2/P3原件不改；本修订只申请独立delta复核，不自签关闭。当前policy从3172B/7b54…变3160B/2032…已全文读，80匹配+1live漂移单列repair记录，不触发产品重测。

本修订仅新D1两前缀文档：补完整58逐项guard矩阵、三scope策略、旧profile入口可检验迁移和精确 `function.__code__` literal；未改D0/产品/锁/旧tests/CI/其它树，无/tmp scratch、无产品执行。新repair-checks/disposition/delta-manifest记录旧新身份和首审保留关系；未来candidateRef=null，作者不stage/commit，主agent实际candidate后由原fresh reviewer独立delta。其余运行/许可/平台/指定双审/正式门均待验。
