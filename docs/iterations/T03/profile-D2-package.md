# T03 D2 固定输入源码／包对照实施

2026-10-21。固定产品 `a4d1457fc6a1f1d1832296a8dcdb2ef42da75b98` 已完成正常检查、新 unsigned macOS arm64 目录包、最终应用内 engine CLI、83 输入严格对照、旧探针、参数拒绝、三项资源负例和静态归档核验。当前实现范围内未发现剩余实施阻断；内部最终独审通过，总控已限定接受唯一 `wcwidth` 原生签名域变换，并对固定 profile 的未收第三方闭包未见新增阻断。本件为固定候选交付，仍待总控对完整 D2 原件作最终读回，不据此无条件收口。完整 T03 Goal 仍 blocked，本件不重启 Goal，不代替 B1、父功能、目标平台、指定外审、CI 或正常合并。

## 授权与固定输入

授权原件 `docs/reviews/T03/profile-D2-package/authorization.md.raw`（8088B，SHA-256 `5c9739565b5df031f8bf663616ba451fed1c86aabae56dd3cf1d38ade50cf2d5`）；逐项清单 `approved-readonly-inputs.json.raw`（20169B，SHA-256 `7778309e8beec0f5ff8ac89531f1a70282f12f257beebae4ff8d7899f393e4b1`）。旧 D2 合同 `b34158977bcfefdc8d218131d00cfe68d4415003` 保留。

现有 `feature/T03-profile-build` 树先在 `fbf36723a29bb19b0337b78a492c46620c9bd590` 分开逐字采用 I05 固定 `0475d0ec6c486a63c7e8f62f11f35181da6b2576` 的 18 个运行源码／资产和 24 个验证输入，再在 `418b5288014d3b7285c8b67b4d82086ed6541d2f` 实现两处 writer，在 `a4d1457fc6a1f1d1832296a8dcdb2ef42da75b98` 显式固定 PyInstaller 优化为 0。采用不转移 I05／T05 维护责任。

对批准基线 `5f910b52c69d86a1076b2032e5d3c63e715947f3`，完整功能／验证范围恰 46 路径：D1 配置／锁 2、I05 运行采用 18、本件 writer 2、验证采用 24。全路径及 bytes／SHA／原 ref 在 `final-inputs-and-executions.json`，不能只审最后两文件。另 23 个基线资源／源码只读；总计 67 个只读输入均已核当前字节、固定 Git blob 与批准清单一致。D1 pyproject 398B／`bcc8825b1f2902a66ae539e687df57e5b2554247f48a48a65215601a77958365`，uv.lock 28440B／`86dfe82d952e2c88edcfc5658f488f6e1f0d04b4ec3b1e6f5c5d3bc4f57e8b73` 均未改。保护 AGENTS.md 不暂存；旧 T03 两树不写入。

本件仅新写这份主说明和 `docs/reviews/T03/profile-D2-package/` 证据。不改旧合同、规则机制、预算、业务模块、测试或锁；没有接入 rule_revalidation、旧 definitions／planning、XLSX 或 T01 新运行面。

## 两个 writer 的最终行为

`scripts/build-engine.mjs` 在实际构建前核 43 个固定运行／资源／D1 输入的长度与 SHA，并拒绝它们及两个 writer 相对 HEAD 的未提交差异。17 个采用 Python 模块转成唯一 canonical 名，quality 包根是 `ontolearn_engine.quality`；七机制无 alternate alias。保留原 onedir、clean 和现有输出路径，显式 `--optimize 0`；collect-all rdflib／pyshacl／owlrl／html5rdf，八分发 copy-metadata，必要 hidden-import 及三旧模块排除。业务模块不以构建前动态导入方式取证。

构建只用本树 Python 3.12.12 与 uv frozen 环境；真实 metadata 记录 PyInstaller 6.22.3、engine 0.1.0、八依赖精确版本、每个发行文件长度／SHA、requiresDist、实际 license 字段和许可证。版本为 rdflib 7.6.0、pyshacl 0.30.1、pyparsing 3.3.3、owlrl 7.6.2、html5rdf 1.2.1、prettytable 3.18.0、wcwidth 0.9.2、packaging 26.3。

包内 `provenance/d2-build-inputs.json` 记录真实组合 a4d、固定来源 ref、43 输入、两个 writer、17 canonical 名、精确 argv 及 metadata。包中仅放唯一固定输入资产 `provenance/i05/profile-probe-inputs.json`（1839011B，SHA `6c6ffc3a1a57d1817583c0a71d24e2847cc5d2d673848878c6e6e72dfe6c39de`），既有九合同及锁保持原字节。

`packages/engine/entrypoint.py` 对 argv 任意位置的 profile flag 或等号变体先做排他检查。只有唯一 `--semantic-profile-probe` 才移除 flag、调用同一 canonical `main([])` 并保留真实退出码；混用 worker／storage、额外参数、空参数、路径或 URL 均在导入业务前固定空 stdout／32B `PROFILE_PROBE_ARGUMENTS_INVALID\n`／exit 2。既有 storage、worker、contract、resources 与默认分派保持原逻辑。

固定 probe 源码无改动：源码从固定相对路径取资产；frozen 只从 `_MEIPASS` 规定位置读取，无 checkout／网络回落。保输入 2MiB、每计算 payload+rows 8MiB、整批 64MiB、83 输入约束；120 秒是外部真实进程硬时限，不把内部观察点称作抢占。

## 实际运行与判读

完整命令、cwd、环境、硬时限、真实 exit、完整 stdout／stderr 及其 bytes／SHA 见 raw ZIP 的 `runtime/*.execution.json` 和旁侧原件；41 条执行记录汇总在 `final-inputs-and-executions.json`。源码／包采集均用固定输入，未从 expected 字段重建业务投影。

| 实际动作                                            | 结果与边界                                                                                                                          |
| --------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| a4d 正常 `npm run check`（04）                      | exit 0；630 TS、2582 Python，零 skip；正常 lint／类型／格式／构建链通过                                                             |
| 同候选 `npm run verify:sources`（06）               | exit 0，12 份源文件核验通过                                                                                                         |
| 新 `npm run package:dir`（08）                      | exit 0，主机 macOS 27.0，目标 darwin／arm64、Electron 44.9 unsigned 目录；应用身份 null，未启动应用                                 |
| 源码 83 输入（05）                                  | exit 1，stdout 14006950B，stderr 0；无硬超时                                                                                        |
| 最终 App 内 engine 83 输入（10）                    | exit 1，stdout 14006514B，stderr 0；在 checkout 外 cwd，无硬超时                                                                    |
| 严格 JSON 深比（11）                                | exit 0，211961 节点；类型、数组次序、重复键和未知字段严格处理，仅下面 9 项差异                                                      |
| 外部固定 oracle 源码（09）／包（12）                | 各 exit 1：78 math-observable-fields-pass、4 failure、1 not-executed                                                                |
| 旧 contract／resources／storage 源包六命令（14 内） | 各 exit 0，contract 10 节点一致；resources 17 节点仅 frozen false→true；storage 20 节点一致，measurement 保留各自真实观察不要求相等 |
| 源码 4／包 8 参数拒绝（14 内）                      | 全部 exit 2、stdout 0、stderr 固定 32B；包括 flag 前后混用和等号变体                                                                |
| 三份独立 final-engine onedir 资源负例（14 内）      | 仅复制体分别缺资产、同长坏 hash、2097153B 超上限；各 exit 1、stdout 0、21B `PROFILE_PROBE_FAILED\n`；原引擎／资产 hash 未变         |
| 归档静态审计（15）／实际递归目录（16）              | 各 exit 0；审计只读，不导入或执行产品代码                                                                                           |
| 证据脚本 -O 拒绝（07、17）                          | 各 exit 1、stdout 0；非优化模式 guard 不是可被 -O 消掉的 assert                                                                     |
| native 有限观测复现（18）                           | exit 0；只观察签名域差异，不替总控接受差异                                                                                          |

严格深比的唯一例外是 `identity.frozen`、`identity.resources.frozen` 两布尔 false→true，及 `identity.modules[0..6].sourceSha256` 由已校验的固定源码 SHA→null。payload、rows、未知字段、布尔／数值类型、顺序、82 个实际 batch hash 和 78 个完整结果的 payload／rows／8MiB／单元格约束均独立核验；没有放宽 comparison 或资源状态。

E.5 round 1／2 仍为 RESOURCE_LIMIT／semanticInput／RULE_INPUT_BUDGET，round 3／4 仍为 RESOURCE_LIMIT／semanticWork／WORK_LIMIT；原 resource／R-risk／null 位置字段保留。transfer:repair 仍因 ORIGINAL_INPUT_CONTEXT_INCOMPLETE、缺原规则而 not-executed，不能因元数据说 fullContext 就称可执行。原始 exit 1 没有变成全量数学成功。

数学覆盖仍为 49／89 图、24／40 匹配（15 接受、9 false）、16 heads／R04 leaf。false 的原 match carrier 存在，false ComparisonEvidence 不存在。本件证明固定计算与包一致及已覆盖观察值，不能推出剩余数学字段、父工作流或整个平台通过。一般资源身份仍 i04-infrastructure-v1／0.1.0／D1 锁；成功计算 payload 身份为 finite7／0.1.0／相同锁。

## 最终实物、归档与哈希域

实际包内引擎：`release/mac-arm64/OntoLearn Studio.app/Contents/Resources/engine/ontolearn-engine`，6077232B，SHA `99adbd67fe7f1cfdb07684bc09165d6b4eda29e42b631a09574f7a95ba2e9ba7`；与 build/engine 副本原字节相同。源码 stdout SHA `a16699f47c5fc8de6658d1dc5a1c422796daf0f3bb4dbed520ffce0577ed74e0`，包 stdout SHA `dddc3a8183d8ecccfb8b52e218831dbceed207ddff69057f228c20c85a395055`。

`archive-audit.json` 829115B，SHA `a5878ca164d57996bf4bcd25c63b0386621b875f0ae1dbcc0db423449afcba65`：实际 CArchive 12 项／PYZ 749 项、30 引擎模块（17 采用＋13 基线）、693 个递归 code 对象以及入口 2 个 code 对象。source→frozen 仅递归归一化 co_filename；其他 Python 3.12 code 字段保留并匹配。PYZ／marshal 原字节、源码 SHA、归一化 code 指纹和最终 engine SHA 分域记录；不混称相等。406 个松散或 base_library code 检查未发现 quality alias；所收八依赖 308 个源码模块代码指纹一致。

12 项规定资源全原字节符合；八 dist-info 共 55 文件（含 10 许可证）与实际构建 metadata 符合，无许可证或 metadata 缺失；343 个实际文件的 inventory 全列 bytes／SHA／symlink，独审另读回。四 collect-all 库必要 data 亦逐项核验。完整 PYZ／CArchive 原目录、五 TOC、warn／xref、spec、provenance、依赖原 metadata 与 licenses 的哈希均封存，未以源码 AST 或固定标识冒充归档证明。

未收第三方模块、developer／type-hint data 和源 console entry 完整清单保留在 archive JSON，各有源 bytes／SHA。包括 pyshacl.assets.make_builtin；pyparsing AI／tools；prettytable 的独立 CLI／colortable；wcwidth 20 个动态 terminal grapheme overrides；packaging 的 _structures、dependency_groups、direct_url、errors、metadata、pylock。不能据此声称八分发全 API／所有环境分支都随包提供。所需闭包及动态 fallback 的静态依据已由内部独审和总控按固定 profile 入口分别审核，未见新增具体阻断；不由此放行完整 SHACL／任意第三方接口，不新增业务复测或自行 collect-all 扩容。

`wcwidth/_wcwidth_c.abi3.so` 源 1389136B／SHA `385bccbd2efdcf0e0d4288d8f4ae5586b7ac5797965b8f79268188ae5b5e8d62`，包 1381184B／SHA `f5e36bc58a9605c02f499e9622b6af4c6a430fe66eb3b007e7a5f3d588f5e31e`，原字节不同。独立 Mach-O 只读解析与 otool 原输出证实 10 个 section 描述／payload 字节完全相同、signature offset 同为 1378224；此前 prefix 仅 __LINKEDIT.filesize@1096（8B，45648→37696）与 LC_CODE_SIGNATURE.datasize@1444（4B，10912→2960）不同，之后签名域不同。有限 prefix 观察不改变 code／JSON 规范化规则，不把 raw hash 说成一致。总控已全文读取独立二进制／闭包审计并限定接受这一实际 pair；没有 Keychain、身份签名或凭据调用。

总控最终独立报告 17664B／SHA `d8afa69fe977fe00aac723be7faa0fe431d83791199086c5ae9fb27b700981b4` 与限定裁定 2981B／SHA `d1cb81202a08c4e38b218146d6c5efab2ff39ef270fd456d069a70dbe9a5c8dc` 已由我全文读取并逐字封存为 `root-native-and-closure-review.md.raw`／`root-exact-native-decision.md.raw`。总控独审另逐页核 CodeDirectory 源337页、包85页真实SHA256全符；最终 CS_ADHOC、无Team、空CMS。签名容量内有16B非零尾填充 `f7f76d1d4179ae6dac49ec9dcbf8c5cb`，逐字等原签名同偏移残留，仍在包raw hash中固定，不能写成全零或赋任意padding豁免。现有日志没有逐so codesign argv／子进程审计；结论来自原字节／签名结构、RECORD→cache index→cache/build/App链、实际工具源与日志相互印证，不冒称亲见该系统调用。

该裁定只接受 source `385bcc…`→package `f5e36…` 这一已核thin-arm64 pair。任何hash／arch／signature offset／签名前差异变化，或另一native变换，都需另交具体pair。没有新增native归一规则或放宽原JSON9差异／Pythonco_filename-only规则。只解除本次构建差异待决项，不提前关闭完整D2、包／平台／全P2／父／指定外审／CI／合并等门；保持a4d及原raw，不重打包、不复跑无变化产品。

## 失败保留与审查修正

第一轮内部独审发现构建只在 provenance 写 optimize 0，却未约束 PyInstaller 实参，遂仅在两个 argv 行加入 `--optimize 0` 并冻结 a4d，之后跑当前正常检查／源 probe／目录包／最终引擎。原 418 检查／源码记录 01–03 保留，不冒充 a4d 的最终运行。

证据脚本原依赖 assert 的地方可能受 -O 影响；外部 capture 现入口非 assert 拒绝优化、自身记录 hash／optimize／产品 HEAD，并清理设定 PYTHONOPTIMIZE=0；严格 validator 和 archive auditor 也入口明确拒绝非 0。07／17 实测拒绝。04–06 是修 capture 前的原始记录，不能回填当时没有采集的 collector hash／head 字段；产品对应 a4d 的事实由当时 Git 冻结、后续 provenance 和67只读＋两 writer 字节闭环证明。原记录不修改。

13 首轮旧探针 suite 因源 `python -m ontolearn_engine.contract_probe` stdout 为空而 JSONDecodeError、exit 1。5f 原 contract_probe 与 resources 模块只有 main 定义，没有模块入口；该命令 exit 0 不代表探针执行。仅外部脚本将这两条源命令改为 `python -c 'from ontolearn_engine.<module> import main; main()'`，仍同一 canonical main，未改产品／增加探针。14 以 v2 标签真实重跑该 suite 并通过；13、首轮两命令及外部原脚本 cli-suite-first.py.raw 全保留。原合同说明不回写。

闭包补审中，曾将 PrettyTable 路径简述为普通 wcswidth，后又把 wcstwidth 的默认 term_program=True 误记成 width；这两条口头简述均撤回。实际 PrettyTable 调 width／align，不显式传 term_program；`wcwidth.__init__` 按 WCWIDTH_PYTHON／C 扩展可用性分别导出 C 或 Python 实现。Python width／align 签名为 False，resolve_terminal(False) 直接返回 None；实际 C 源／包内嵌 width 声明及随发行 pyi 同为 False，True 是 wcstwidth。这里保留静态声明证据，不冒称额外执行验证 C 默认分支。固定 semantic.check_shapes 直接 Validator(...).run()，不调用 pyshacl CLI 的 PrettyTable table 输出；固定 profile 可达性依据见最终独审及总控限定结论，不能因83结果相同或某一fallback存在就推出任意终端／API等价。

上述实际源码和原生声明另封 `dependency-closure-static-evidence.zip`（57442B，SHA `a5f05699f38b0b6fd6e24a7e6b3f8c9f0723578b6784c6eec3a19df0016baf0f`），15成员逐字读回；旁manifest列各源文件原SHA。只读源码／read_bytes，不导入库、不启动新产品运行，原runtime ZIP不改写。

固定 oracle 直接提取已批准 ZIP 的 compare_oracle.py、project_inputs.py、input-manifest-v2.json，三成员长度／SHA 均核准；第四个 oracle fixture 是逐字采用原件。外部 helper 只采集、严格比对、资源复制、归档或 hash，不重做业务算法、不重新投影 oracle、不以 mock 冒充资源失败。

## 证据封存与未完成门

`docs/reviews/T03/profile-D2-package/runtime-evidence.zip`：3707625B，SHA `51e628ca57615123df296601605f2081f6bb261935fc192bf938f6b2afe593fc`，158 个成员全部读回核长度／SHA；manifest 为 `runtime-evidence-manifest.json`。包含所有首失败、真实非零退出、空 stdout／stderr、18 组主命令及21个v2子命令、外部代码、固定 checker 原容器、五TOC／warn／xref／spec／provenance。完整引擎与负例副本留在 ignored build／release，不把产品二进制提交 Git。

内部最终独审已按固定 a4d／完整 46 路径完成，我已全文读取 `independent-review.md`（21527B，SHA `24db94b7283038e04cee14f223a06a1a46e506d4dcefb546d1d04a3c3866b4d0`）：无剩余实施阻断，三项 P2 已关闭。该报告写作时保留的 native 接受门随后仅由上述总控精确裁定解除，不回写原报告或改写raw历史；完整 D2 固定交付仍待总控最终读回。指定 ZCode GLM-5.3／最高及 MiniMax M3.1-Flash／xhigh 未实际运行，本轮新增 0 次；普通内部 agent 不替代指定审查。未启动 GUI／Electron／native交互／e2e／HMR／焦点／Keychain／模型／付费 API；没有 push／PR／merge。macOS arm64 unsigned 目录不等同 Windows 或其他平台、身份签名、安装器、UI 或生产证据。父验收／B1／CI／远端核验等原门保留。
