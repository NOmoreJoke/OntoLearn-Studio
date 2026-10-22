# T03 对 I05 semantic build offer 的接收设计拟稿

2026-10-22。结论建议：**纯设计可接收，但必须连同本件 §3 的最小协议增补接收；原两份 schema 原样进入实现为 needs-change。** 依赖、独立 profile、parent 保留、外部后置 provenance、包外收据和完整验收方向可接受；root executable 的 runtime 映射、嵌套 archive 与第四函数的归档来源表达须先冻结。拒绝把缺件填成 unknown 后仍称 accepted，或以任意 locator、源码 SHA、缩减 suite 来绕过这些缺口。

这是独立 helper 给唯一四 writer 维护者的可审核建议，**不是原 T03 owner 最终接收，也不是 root 批准**。原 T03 须全文读本件、报告和输入清单后明确接收/驳回/逐项处置，再由原会话提交固定文档候选并另派独立静态复核。本件仅建立后继设计依据；未授实施、锁采用、安装、build、外部见证生产、consumer 测试或任何进程运行。本件与 R7 native 窗及其计量票独立，不等待 meter，也不借用其额度或资源。

## 1. 固定输入与证据等级

- 本树：`.worktrees/T03-i05-semantic-offer-owner-review`；branch：`docs/T03-i05-semantic-offer-owner-review`；base/读取时 HEAD：`5f910b52c69d86a1076b2032e5d3c63e715947f3`。
- offer candidate：`6ba273a892b18a5ebaedc07aea6f36584999adcf`；最终过程：`21f9d4d288e8bd462b2252018578590110c08691`。下文 `O` 为该 candidate 的 `docs/iterations/I05/semantic-build-offer-draft.md`；`P`、`B`、`F` 分别为同 candidate reviews 前缀下的 `profile-descriptor.draft.json`、`build-provenance.schema.json`、`final-build-receipt.schema.json`。定位同时给 JSON 字段与固定 Git 行号，不依赖本树不存在的 checkout 路径。
- O 为 55,286 B / SHA-256 `9a48791f24e3b9149d3416a82284248092bce113d9c0f269a62b5887a2fb4c09`。两 schema 都是草案，未变成运行协议；P 的 `acceptedCompositionRef=null`、`executionAuthorization=false` 保留为原件事实（P L1–26、L539）。
- 总控已直接核 current=Git=manifest 的 46 payload 加 manifest 共 47 件；此处引用该限定收件，不重复全量重审。R1 10,450 B 为 Fail，R2 7,286 B 为限定静态 Pass；两项原问题的关闭只说明职责/旧 owner 标签修订成立，不包含本件新指出的表示问题或真实运行结论。
- 本轮亲读 O 全文、P 全部字段、B/F 的完整 JSON 结构和值，以及 delivery/final-manifest/R1/R2；B 通过持有完整 JSON buffer、按全部 properties/$defs 分段显示阅读，未运行 schema 生成器或 validator。106 Git 来源、43 guard（30 同/13 异）、33 路径和 417 清单依赖固定 R1/R2 独审，另在有限必要点抽核，不宣称本轮重新读全这些来源。
- 2cf probe 仅抽读 L1–115、L572–706（另一次不相关范围 L1390–1550 也实际读过）；6891 resources 全文读 L1–97。前者 L598–601 仍 frozen 总拒绝；L103–108 要求 6891 锁/八库，不能把 source-only 封存理解为当前 5f 环境可运行。后者 L14–20 是同一 `resources.CONTRACT` 对象，并无已有 sys.modules 注册。
- 原 M0 文件不在本 base 的命名路径，按合同已经说明的本地原件定位，只读了主目录原文 S1/B1 相关段（L43–63、L145–169）；不伪造 Git 归属。ADR-0001、I01 ADR-0002 全文读，仅用于核 parent/存储与打包边界，不据旧状态文字重判当前进度。

有限输入的 ref/path/bytes/SHA、实际阅读范围和抽核结果见 [input-evidence.json](../../reviews/T03/i05-semantic-build-offer-adoption/input-evidence.json)；审查意见见 [owner-design-review.md](../../reviews/T03/i05-semantic-build-offer-adoption/owner-design-review.md)。本件没有修改 offer 47 原件。

## 2. 逐项接收建议

| 项目                               | 建议                     | 接收的具体设计与必要边界                                                                                                                                                                                                                                                        | 固定依据                                       |
| ---------------------------------- | ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------- |
| 依赖与唯一锁                       | accept（设计）           | 保 rdflib 7.6.0，提议 pyshacl 0.30.1、direct pyparsing 3.3.3；先审完整 23 包锁、extras/markers、各平台 wheel/sdist，再由 T03 实施。5f 的 20,999 B 锁与 6891 的 28,440 B 锁分别记身份；不复制旧 venv，不造第二锁，不以同版本代同 artifact                                        | O L19、L25–34、L105–120                        |
| parent 与独立 profile              | accept（设计）           | 独立 exact builder flag `--i05-source-package-parity`、name `ontolearn-semantic-parity`、onedir/`_internal`/optimize=0，target 新 probe。parent 原默认/旧 flag/guard 保留；新 parent flag 只转发三组 exact argv，非法 argv exit2，不落 default。独立包不代 parent `package:dir` | O L29–34、L83–103、L251；P L7–26               |
| bootstrap/类发行                   | accept（设计）           | 第23 canonical probe 和 CArchive bootstrap 分别见证；早期 `__main__` guard 转 canonical main，不由 `__main__` 发行类型，不拿同名同 hash alias 冒单一对象。真实 canonical PYZ 项缺失拒绝                                                                                         | O L103、L128–130；2cf probe L8–13              |
| 33 路径与旧 guard 迁移             | accept（设计）           | 23 canonical+4 资源+2 资产+4 writer 恰 33 路径；保 43 guard 逐项迁移，parent guard 不删。独立 profile 解 rule_revalidation exclude，definitions/planning、worker/Store/Job/旧 probe 等仍排；不 collect-all engine/quality，不 glob v2                                           | O L38–85；P L456–511；固定 R1/R2               |
| 后置 provenance/收据无环           | accept（设计）           | source/descriptor 已有 commit → 构建/实际 archive/code 见证 → 普通 data provenance → 包外完整目录 manifest → 包外 receipt → 过程 commit。provenance 不 hash 自己，外部文件不进入目录，也不预填自身未来 commit；签名改字节新 receipt                                             | O L124–136；F L14–184                          |
| runtime 根文件/归档表示            | needs-change             | 按 §3 A1/A2 收敛封闭路径域与容器 ID；schema 现有 file 字段无法准确覆盖根 executable bootloader，嵌套 PYZ 及 Validator.run 见证归属不够明确。不能只填一条不实际存在的路径或“codeEqual=true”                                                                                      | B L821–918、L1416–1619、L1633–1753；O L136     |
| Git/installed/archive/runtime 四域 | accept，连同 §3 A2/A3    | Git blob/原 bytes；installed artifact/RECORD/许可；actual archive raw member/code；runtime actual loader/function 是不同证据。Validator.run 的 source 为 installed-distribution-source，不伪造 Git ref。builder 的 archive completion 不预签 runtime loader/cache               | O L140–150、L170–193；B functionBindings/$defs |
| actor 责任与 exact 错误码          | accept，明确新码尚未实现 | 采用 §4 分工及错误表。probe 不读包外 receipt/source/log/installed 原环境，不自行批准 composition；caller 缺批准不得 launch，启动后逐 header/runtime 回绑。未知异常不得转成功                                                                                                    | O L154–189；P L524–538                         |
| I05 消费 delta 次序                | accept（设计）           | T03 dependency → I05 受限 consumer delta → T03 包装/见证实现 → root/owner 批准实际 composition；另设本件协议修订冻结点，不能把 docs schema 自动加到 runtime                                                                                                                     | O L34、L154–164、L242                          |
| 八 distribution/许可/环境          | accept（验收要求）       | 全八库 actual artifact→installed→archive/data/metadata/license/NOTICE/COPYING；Python/stdlib/bootloader/dylib/platform runtime 单列。宿主 wheel 不代表 Windows；typed 费用与库分类缺口保留，不以版本/License 字符串消账                                                         | O L105–120；合同 raw L180–182                  |
| 完整 417 与 T05                    | accept（验收要求）       | source/独立包/parent 分开全量采集、全结构比较，再各自对独立 oracle；full-v1 417，B1 两 selector 不能拼成 full。T05 固定首 oracle `3d8f4ee` 当前作者报告 417/37 纯自测、280 specified/137 pending，未独审/收件；O L236 的28项是旧快照，不能当新通过                              | O L195–242；本窗外控最新状态                   |
| B1/S1/正式门                       | accept（保留）           | 另12 B1 fresh 纯语义 trial；原12 S1 真实 SQLite snapshot 独立保留 HOLD。parent package:dir、正式 Job/Store/selected/H、57P0/C–G/PRD10–12/六迭代、指定同版双模型、CI/两OS/真人/develop/远端门全部保留                                                                            | O L244–260；本地 M0 S1/B1 原文                 |
| 以静态 Pass 替运行/缩验收/借票     | reject                   | schema 解析/AST/数量与 hash 不证明 archive、loader、许可入包或 source-package 等价；不得删 417、原 S1、parent、错误首件或原保护来“修绿”，不借 R7/旧 Q/N/P/native 票                                                                                                             | O L264–266；外控窗口                           |

这里的 accept 只表示可供 owner 接收的设计选择。原 schema 原样实施被本件明确判 needs-change；§3 的采用差异是可审核的修订提案，owner 尚未在本件作最终批准。

## 3. 最小协议增补（不改 offer 原件）

### A1 · 明确 bundle-root 与 meipass-root，覆盖 bootloader

**具体反例。** O L90–100 将 executable 放 bundle 根，`_internal/` 是 `_MEIPASS`；L136 又规定 runtime 映射相对 `_MEIPASS`。B `runtimeComponents` 允许且要求记录 `pyinstaller-bootloader`（L1649–1656），`bundleFiles` 却仅有 `{path,bytes,sha256}` 且禁 `..`（L1684–1708）。根 `ontolearn-semantic-parity[.exe]` 的 bootloader 无法用 `_MEIPASS` 相对安全路径指向：`../ontolearn-semantic-parity` 被拒，`ontolearn-semantic-parity` 则指向不存在的 `_internal` 子文件。复制一个同名文件到 `_internal` 也不是实际启动的 bootloader。F 虽有根 executable，B 此字段没有链接或根域，不能靠读者猜测补齐。

**最小设计修订。** 在后继 schema 新版本中，所有“最终包文件”统一为 `bundle-root` 相对路径，包含 `runtimeComponents.bundleFiles`、distribution bundleMappings 的目录/容器实体、license bundleFile 与 dynamicChecker.bundleFile。`payloadFiles` 继续只为 `meipass-root` 相对、排唯一 provenance；两域必须在字段定义中固定，不允许实例任意选根。四资源/两资产/lock/probe 的 bundle 内读取仍保持固定 `_MEIPASS` 白名单，不扩其访问能力。

一个实际文件在两张账中出现时，必须满足 `bundlePath == "_internal/" + payloadPath` 且 bytes/SHA 相同。根 executable 只能经 approved descriptor 的 exact name 和 F.executable 指认；B runtime 的 bootloader 映射指向同一 bundle-root executable，全文件 bytes/SHA 可与其他组件重用，但角色与原 artifact 责任分别记。这个方案不试图把 PE/Mach-O 内 bootloader 片段伪称为独立文件。需要片段证据时由 A2 的受限容器见证表达，不造假文件。

包外 source artifact、installed 原文件、logs、witness 均明确属于固定批准证据前缀；Git source 仍是 Git 根域。禁止绝对路径、`..`、反斜杠、drive/UNC、NUL、空/`.` segment、重复规范名、大小写/Unicode/平台别名冲突和 symlink 逃逸。root/caller 在获准前缀内 resolve containment 后只读，不能把源字符串拼成可执行命令。schema 现有 pattern 只是第一层语法，不能替代实际文件和平台身份核验。

**处置。** owner 可连同本增补接收方向；进入 builder/consumer 实现前必须先冻结新 schema/descriptor 的 exact ref/path/hash，并由独立复核确认上述域一致。不得在当前 v1 实例里静默改变 path 意义。

### A2 · 显式 archive 容器链及第四函数的实际模块见证

**具体反例。** B `archives` 只有 `path/kind/bytes/sha256/inventory/...`，没有父容器/member 引用（L821–918）；`module.actualArchiveCode` 是单一 `archivePath/archiveSha256/memberName`。若实际 PYZ 是根 executable 的 CArchive 中一个 member，目录里没有 `PYZ.pyz` 普通文件。填虚构根路径不真实；把 archivePath 写 executable 又无法同时表示 executable 的 bytes/SHA 与嵌套 PYZ 的 bytes/SHA。把容器链编码进任意字符串 `exe!PYZ` 也违反明确的 file path 域。

另一个来源缺口：`Validator.run` 来自 `pyshacl.validator`，不是23 canonical 内任一模块；B functionBindings 保 `moduleName/codeConstIndexPath/expectedFunctionCode/actualArchiveFunctionCode`（L1416–1619），却没有该 distribution 模块的强制实际 archive 模块绑定。一般的全 TOC 记录或一个模块名不足以唯一指明“哪一个容器、哪个 raw member、从哪个模块 code 按哪些 co_consts index 抽取”，无法阻止把四个 actual 指纹全从 compile 结果填入。O L147 要求的真实提取义务应变成显式关联，而非自由注释。

**最小设计修订。** 新版本只增加数据见证，不增加 probe locator：

1. `archives` 改为有唯一 `archiveId` 的封闭账：实体要么为 final bundle 内 exact file（`kind=CArchive/external-pyc`，bundle-root path/bytes/SHA），要么为已列父 archive 的一个 exact member（`kind=PYZ`，parentArchiveId/memberName/raw bytes/SHA）。父项必须先出现；本 profile 容器链最多 `bundle executable → CArchive member PYZ`，若 actual toolchain 超此布局，先报版本 delta，不接受递归任意 locator。外部解码后的 raw 保存件另属批准 witness 前缀，不能冒 final 文件。
2. 每一 TOC 名称唯一，完整 inventory 按实际序/类型/raw bytes/SHA保全；父 member→子 archive byte/hash严格核同。archiveId 仅引用本 JSON 账项，禁止路径表达式/URL/cwd fallback。最终 directory manifest 只列真实普通文件，不为嵌套 PYZ造文件。
3. canonical23 的 `actualArchiveCode` 使用 archiveId+exact memberName/raw bytes/SHA/code fingerprint；bootstrap 使用 CArchive 中 exact script；不把 canonical23 扩为 distribution 代码域。另加仅 `pyshacl.validator` 的 `distributionCodeBinding`，同形保 selectedArtifact/installed-source/RECORD→实际 archive 模块 code/源编译指纹。
4. 四个 `functionBindings` 都要求引用一个既有 module code binding ID，再以 `codeConstIndexPath` 同时遍历 source-compiled module code 和 actual-extracted module code；expected/actual function 指纹均从各自对应域取得。前三个引用 semantic binding，第四个唯一引用 pyshacl.validator binding；模块源码 SHA 不得填任何 code 指纹。必须保所经索引及 exact CodeType 检查，不用 name 搜索猜函数。
5. dynamic checker 是 bundle data 的唯一 `resources.CONTRACT`，不要求它凭空进入 PYZ；builder 字段改称 `expectedBundleSourceCode`，只代表批准 data bytes 的 source compile 结果。真正 `runtimeLoaderCode` 放 caller 接收的运行证据/header，启动前只比 source↔bundle data，启动后再比 actual checker loader。不得在 builder completion `runtimeParity=not-run-by-builder` 同时把未观测 actual runtime loader 写成已验证。

前三项是实际归档表示的必要闭口；第4项补齐 O 的函数提取义务；第5项消除 B.dynamicChecker.loaderCode（L1355–1395）的阶段歧义。若 owner 选择保留旧字段名，也必须用新 schema version/comment 和跨字段规则固定其“构建域 expected、非 runtime 观测”意义，不沿用一个值覆盖两个阶段。

### A3 · installed 根与 RECORD 逐行保全

B 的 `installedRelativePath`（例如 L2349–2413）是受限相对路径，但原安装根和 RECORD 行到此路径的映射规则未明确。本件不声称已读取任何真实 installed RECORD，更不能编造 pyshacl 当前安装的实际内容。设计必须允许完整 RECORD 行原样保全并在固定安装根中核定：原 RECORD 行是证据数据，不直接作为探针可打开的 locator；另记批准安装根的封闭 ID 与规范根内相对路径。若原行用上级相对路径指脚本，只能解析到该批准环境根内的实际文件后核 bytes/hash/角色，不扩大到环境外任意文件；逃逸、缺件、重名不接受。所有 dist.files/RECORD 行逐项 disposition，`bundled` 必须非空 mapping；omit/build-only 必须有 owner 审过理由，runtime 必需不得 omit。保 RECORD 本身及摘要；不是删掉不便映射的行。

这是一项实现前定义要求，不是本轮对实际安装内容的新实测发现。typed 费用、库分类/许可法律义务的未决项仍保持缺口；B 的自由文本 classification/noticeReview 不自动等于已审核结论。

### A4 · 外部批准与运行收据不互相倒填

F `runtimeValidation` 与 nullable `runtimeEvidenceManifest`（L206–235）须明确跨字段关系：`not-executed` 时 null；`collected-pending-comparison`/`compared` 时非 null，且绑定完整 evidence manifest 和 comparator/oracle 身份。`compared` 仅说明比较实际发生，不等于匹配或原操作通过；比较结果单列。构建 receipt 已获批准作为 launch 前输入，后续运行证据产生一个新的包外 validation receipt，引用原 build receipt hash 与 runtime manifest，不改已批准 receipt、不改变 embedded provenance，不与等待中的 runtime 输出形成环。F 若保原 runtime 字段，它在 build receipt 固定为 not-executed；后续 schema 另精确定义 validation receipt，禁止将旧字段原地回填破坏 launch 前绑定。

本件只给关系和采用差异；没有新增实际 schema 路径、receipt 实例或可信载体。由原 T03/root 在后继 docs 窗明确精确路径/版本/hash及维护者再实现。

## 4. 责任和 exact 错误边界

| 主体                       | 必须生产/核验                                                                                                                                                                                                             | 不可越权                                                                                                                                |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| T03 唯一四 writer producer | 实际 approved refs/clean 输入、selected artifacts/installed/RECORD/metadata/许可；真实 build/logs/工具身份、完整 archive/代码/函数/data/runtime映射；后置 provenance、完整目录和包外 receipt。缺证保首错，不能产 accepted | 不自行批准 own composition，不把 builder completion 写成 runtime/oracle/parent通过；不接管22供应/4公共资源维护权                        |
| root/外部接收方            | 实际 owner 接收记录、组合祖先/patch、33 source 身份、工具/提取器/外部原件、完整闭包与许可、A1–A4无环/域关系，批准确切 build receipt/evidence bundle                                                                       | 一句批准摘要不可替代真实 hash 绑定证据；设计接收不可扩大为运行授权                                                                      |
| 获准 external caller       | launch前核批准固定证据包/receipt、当前完整目录/exe/provenance与同一组合；source另核实际checkout；launch后保全部 JSONL/exit/signal并回绑 header digest/ref/runtime code/terminal                                           | 缺批准不启动；不以exit0覆盖 mismatch；不让 probe访问外部 locator；不把source=package当oracle正确                                        |
| I05 probe                  | strict bounded provenance/声明关联；固定4资源/2资产/lock/实际Python域，23 canonical与四函数/checker actual loader/对象；输出 declaredCompositionRef/provenance digest及 external-unverified                               | 不读外部Git/owner/source/profile/logs/artifact/installed/receipt，不批准 composition，不解码archive；不嵌自己SHA或未来ref，不改公共资源 |

三组完整 argv 固定为 `["--semantic-source-package-probe", "full-v1"]`、`[flag,"b1-semantic-1x-v1"]`、`[flag,"b1-semantic-10x-v1"]`。source `python -m canonical`、独立 executable、parent flag 入口均用同一 canonical main；flag=value、单 flag、未知 selector、额外 args 拒绝。任何新增 source/probe/schema pin 都显式 delta，不用旧2cf自 hash冒新源码。

| 主体/阶段                     | exact 安全码（沿 O L182–189 的后继协议提议）                                                                                                                                                                                                                     | 终态与处置                                                                                       |
| ----------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| build 输入/域/archive/license | `BUILD_INPUT_IDENTITY_INVALID` / `BUILD_CODE_DOMAIN_MISMATCH` / `BUILD_ARCHIVE_INCOMPLETE` / `BUILD_LICENSE_MAPPING_INCOMPLETE`                                                                                                                                  | build非零，完整原stderr/first错误保外部，不生成accepted provenance                               |
| caller launch前               | `APPROVED_BUILD_RECEIPT_UNAVAILABLE` / `APPROVED_SOURCE_BINDING_INVALID` / `BUNDLE_DIRECTORY_MISMATCH`                                                                                                                                                           | not-started；无probe成功/业务开始                                                                |
| probe provenance/域/资源      | 现有 `FROZEN_BUILD_PROVENANCE_UNAVAILABLE`；新增 `BUILD_PROVENANCE_FORMAT_INVALID` / `DECLARED_COMPOSITION_FORMAT_INVALID` / `BUNDLE_PROVENANCE_RESOURCE_MISMATCH` / `LOADER_ARCHIVE_CODE_MISMATCH` / `CODE_DOMAIN_INVALID` / `DYNAMIC_CHECKER_IDENTITY_INVALID` | 前置exit2；图业务未开始，import已经读过公共JSON的事实如实记录；不fallback sourceSHA/外部文件     |
| probe未知异常                 | 原 `INTERNAL_ERROR`                                                                                                                                                                                                                                              | exit1/incomplete；安全诊断不泄路径/异常栈/业务原值                                               |
| caller launch后               | `HEADER_PROVENANCE_BINDING_MISMATCH` / `RUNTIME_EVIDENCE_INCOMPLETE`                                                                                                                                                                                             | 外部failed/incomplete，保 stdout/stderr/exit/signal，不反写probe原件，不判equivalence/oracle通过 |

新码尚未由2cf实现；此处仅建议 owner 明确接收 exact 拼写、生产主体与 exit 意义。新增码在私有 probe/caller 证据协议定义，不擅改公共 errors catalog。已有 resource/lock/dist/Python 前门保留；source 现有 `LOADER_SOURCE_CODE_MISMATCH` 与新 frozen code 码分域保留。

## 5. 后继集成与精确窗口建议

以下是给总控的提案，**不是本件发出的执行票**。每窗启动前必须固定实际 base/head、唯一 owner/树/branch、文件白名单、输入/工具/artifact hash、输出/证据前缀、允许操作、资源/进程数/timeout/停止策略；失败保第一原件，新 candidate/delta复核，不自动重试/安装/修版本。写锁若仍被占，受阻的是相应实现窗，不阻塞本次 owner 纯设计接收。

1. **D0 协议文档窗。** 原 T03/root 全文读并处置本件；精确冻结 A1–A4 对应新 schema/descriptor/source-only consumer 规范的版本/路径/hash，明确 archive witness/最终目录/validation receipt数据责任。保 offer 原47件，不追改历史。先完成本件固定文档 commit 与独立静态复核；这一步可在无任何 native/meter票下完成。
2. **D1 T03 dependency 窗。** 仅唯一维护者改 `packages/engine/pyproject.toml`、`uv.lock`；固定完整23包解析delta、extras/markers/所有平台artifact和现行npm锁一致性要求。锁实际变化后独立冻结 dependencyRef。执行 sync/install 需本窗另明定；本件未授。供 I05 先做静态pin/错误路径设计，不用旧锁假运行。
3. **D2 I05 consumer 源码窗。** 仅 I05 的 `semantic_source_package_probe.py`、专用 test/docs及 D0 精确批准 schema 读取路径。保22供应/T01公共resources/checker不动；新 LOCK_BYTES/SHA/八库、16MiB provenance cap、strict JSON/schema/路径域、23自身pin回报、actual function/checker loader、exact错误码/argv与安全输出显式实现。先冻结 consumerDeltaRef及新第23 pin，不能静默接受5f锁。
4. **D3 T03 包装源码窗。** 唯一维护者改 `scripts/build-engine.mjs`、`packages/engine/entrypoint.py`及另授的专用证据工具路径；完整33 guard、独立profile/隔离dist-work-spec-cache-log、parent原入口保留、A1–A4外部 collector/提取器实现。冻结 wrapperRef，root/owner批准真实 compositionRef；descriptor/source/tool须是可恢复固定Git输入，不取任意HEAD。
5. **E0 环境/实际build/archive窗。** 在独立环境按完整锁安装真实artifact，保每件artifact→installed→RECORD→许可/metadata→bundle账，真实build/完整logs/全TOC/raw archive/code提取，sourcecompile只针对批准 bytes、不执行业务。先证同解释器sourcecompile↔actual archive所有23/bootstrap/四函数/checker，再生成后置provenance/完整目录/包外build receipt。code域不一致即保首错回D0/I05/T03算法版本delta，不能改归一字段消差。此票明确允许安装/build/compile/archive解码，和本窗完全不同。
6. **E1 code域运行微验窗。** caller持root批准收据，仅在获准隔离资源进程内对全23/四函数/checker验证真实loader、fresh/cold/warm/cache重复get_code及Python patch/build/cacheTag/magic/optimization；不因 cacheTag同即假定稳定。缺get_code/exact CodeType/原对象或差异拒绝，先产微验证据；该票不是完整业务suite或B1票。
7. **E2 完整consumer/source-package窗。** 同批准composition/asset/policy/case序，source与独立包分别full-v1全417、完整JSONL/图/rows/SHACL六字段/typed/wire/payload/definitions/source/allocation/DAG/root/失败诊断；否例含strict argv/provenance错/重复键/超cap/路径逃逸、错版/alias/尾资源/外联拒绝等。caller先launch前核证再启动后回绑；完整结构比较与独立oracle分判。明确允许进程数/物理准入/timeout/readerjoin/停止方案；不借12k/8k/native票。
8. **E3 T05 oracle与数学判定窗。** 先固定 `3d8f4ee` 全ref/path/bytes/SHA、417逐ID映射和37自测原件，经独立审查/正式收件；280 specified/137 pending及actual child allocation准入、12 date首码逐项列账。缺独立expected保持pending，不拿source输出固成golden。T05若需delta走自己的树/owner，不在T03跨写。
9. **E4 B1/parent/S1/正式门独立窗。** source/包×1×/10××3fresh另12 B1语义trial；parent `package:dir`及同suite另验；原12 S1真实snapshot须T01原owner、SQLite损坏输入HOLD和合法physical/H准入满足后独立执行。正式Job/Store/selected链、指定同版双模型/CI/Windows/macOS/干净无系统Python/断网/签名安装/真人/develop正常合并及远端核验逐门走实际候选。独立artifact或内部静态审不能替代。

## 6. 缺证、验收口径与保留边界

目前缺真实 approved composition/owner终态、实际 T03 dependency/wrapper 与 I05 consumer delta、新 schema runtime采用、真实 installed/八distribution与runtime许可闭包、完整actual archive/code/loader/cache微验、后置provenance/外部批准receipt、417各端运行与比较、T05独审接收及137pending/费用/分类/日期首码处置。它们分别进入上述窗口，不合并成笼统“等meter”。D0纯设计接收不依赖R7结束；E0及以后仍须独立真实前置。

完整采集保 O L232–240 的 cap 与终态：descriptor1MiB/input8MiB/总9MiB、case≤512（actual417）、item32MiB/stdout64MiB/terminal64KiB预留、120s monotonic逐stage前后；新provenance16MiB只经D0/D2另审。逻辑cap不是CPU/native/whole-H许可；opaque调用不可即时deadline打断。完整item先预算，硬停半行原字节保留/incomplete；exit0只表示所选采集完整，可含known rejection/missing-context/not-executed；exit1 harness/unknown/预算不完整，exit2前置非法，130仅协作stop边界，hardkill用真实signal/null。cancel request、stopping、目标真实停止/readerjoin/引用释放分开。

full417与320datasets、83数学/106操作/54checks/50产品上下文和C13不删；repair77旧数学未执行、四E.5片段、五unresolved等不升级。两B1 selector各一个measurement不代表full；collectionComplete/fullSuiteCollectionComplete/sourcePackageEquivalent/externalOracleMatched/originalOperationPassed分判。BNode仅约定图同构，完整有序rows/多重行/词法/typed字段不删；只预先列runID/time/真实locator/编译域允许差异。typed费用与库分类缺口继续列缺，不靠hash/数量收件消失。

原 B1 的1×/10×是四ontology图22/184；十ontology28/190是full另案，不能混。另12 B1纯语义fresh试验不填原12 S1 snapshotLoad指标；原S1不得用数组/0秒/旧storage_probe绕SQLite损坏输入HOLD。FirstAfterS1已热，fresh只表示新进程，OS cache未控制；未实测性能不量化，Q5未定不造容量线。

本轮只普通Git/文件、stdlib JSON/hash和既有Prettier3.9.10文档格式；未 import/执行产品/probe/builder/spec/reader/helper/局部函数/fixture/模拟/pytest/compile/archive解码、版本/能力探针、安装/network/DB/native/GUI。未读旧binary/toolpayload/SDK/witness，未改四writer/锁/CI/公共契约/任何别树；未stage/commit/push/PRmerge，未新Goal/用户线程。AGENTS保护M及其15852B/SHA原样保留；与本件新增路径以外的变更须由原owner处理。

本件建议不解除原SQLite损坏HOLD、被拒物理线、whole-H/owner、指定同版双模型、CI、两OS、真人和develop/远端门；最终状态仍以项目唯一状态文件为准，本件不维护完成度。
