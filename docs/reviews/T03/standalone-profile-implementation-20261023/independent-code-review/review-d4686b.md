# standalone profile 四源首轮实际代码独立静审

结论：**d4686b 当前不放行单文件 unit：1 项 blocking P2（F1），无新 P1；另有1项非阻断P3（N1）。** 已完成实际四文件全文静读及原parent差异核对。实现主体具备精确profile、独立产物、文件FD两流、CArchive/PYZ/marshal前预算等实际代码；但新生效合同仍混用parent路径/launcher/阶段叙述，必须由唯一代码作者先修、冻结新vector，再独立审精确delta。方案审查、静态脚本exit0或函数存在均不能把这项P2关闭。

严格静态；没有import/执行产品、unit、Node stub、prepare/finalize、build/CLI/help、archive目标、native、安装或GUI。本审只使用全文文本、AST/JSON/hash、固定Git对象和自有只读静态脚本；没有执行source生成器，没有Node --check，没有改四源、contract、保护文件或原proposal，也没有commit。唯一写面为本independent-code-review目录。

## 1. 冻结身份与全文覆盖

提交 **d4686b1769b5925190a9e7afcc23b92d5db04d4d**；parent **c706f8f581785053278f26e48d21d7bebadf09f6**；tree **ef6885d15032841a549a7bc179cee2434b44a1af**。Git product-only差异正好以下四路径，工作区四文件逐字节等冻结对象。过程材料没有混入product commit，AGENTS覆盖未纳入。

| 文件 | bytes / 行 | SHA-256 |
| --- | --- | --- |
| scripts/build-engine.mjs | 22269 / 683 | 8170aea2762477d36c425d086463a6b7ce3a60ad0eecb30b7218fd5c308ff905 |
| packages/engine/src/ontolearn_engine/semantic_build_provenance.py | 83012 / 2165 | fbfc995d0ba324cc4c9b6586570054f21b53ae8ec9eab374c256d01c72857524 |
| packages/engine/tests/test_semantic_build_provenance.py | 105310 / 2653 | ec04fc359b9ff58bb41e2ed13255bb6b7902b3309044573d6bbd4f8faf13f989 |
| docs/iterations/T03/i05-semantic-parity-profile/private-profile-contract-v1.json | 45744 / 1143 | 4708d5ae4b0b9cedc71e23e33cbfd3efbb710fe3d5edcce1a6f00ece2c7c649f |

精确源票7567B/SHA337f9a4f1b9f67ca8f9e7a4f80a770acad739ec187b77bae6233810fdeee992a及其指定root preflight12097B/SHA73929cb901ee7a19cf84408f07993da6b90d37127cc98de7c42a3d57f225784a已先全文读取；没有扫描其他private文件。本轮适用其新增“完整两流”及“bounded CArchive AND PYZ/marshal”要求，不能仅沿旧方案。

全文段：builder1–350/351–683；reader1–420/421–850/851–1300/1301–1750/1751–2165；unit1–450/451–900/901–1350/1351–1800/1801–2230/2231–2653，包含原BUILDER_UNIT与新STANDALONE_BUILDER_UNIT两个完整Node字符串。contract1–400/401–800/801–1143，最后合并输出局部截断以pathDomains/bindingKindRules完整JSON子树及955–1030原文补齐。不是只读新增diff、AST函数名或author静态计数。

## 2. F1 [P2 blocking] 新合同内部仍使用parent路径、身份时态与验收范围

位置：新contract L909–910、L912–921、L935–956、L975（均为d4686b固定对象）。

可直接复核的矛盾：

| 合同字段 | 当前实际值/叙述 | 同合同及代码实际standalone要求 |
| --- | --- | --- |
| pathDomains.inputs.rowPath L936 | `fixed ontolearn_engine/probe_inputs/<name>.json` | fixedInputs/inputMappings的frozen row是`provenance/i05/source-package-parity/...`；sourcePath才是同包probe_inputs。当前conversion还称照抄fixedInputs而sourceRoot仍src，无法描述这两个域 |
| pathDomains.contract L948–950 | 源仍旧`docs/reviews/T03/i05-m08-provenance-20261023/private-contract-v1.json`，frozen仍旧`provenance/i05-private-contract-v1.json` | 新contract源及bundle均在fixedLayout/reader STANDALONE_*明确为独立路径 |
| pathDomains.entrypoint L953–956 | `packages/engine/entrypoint.py`，旧external-launcher/PYZ-only domain | 新target为canonical semantic_source_package_probe.py；runtime canonical PYZ与外部target-CArchive/fullbinding必须分域 |
| bindingKindRules.file.launcherRule L975 | `ontolearn-engine`必须可执行 | 新fixedLayout/schema/实际inventory检查的是`ontolearn-semantic-parity` |
| identityRules.finalPins L909 | 将`current2cf/6891/401a`旧声明当当前叙述，仍收entrypoint身份 | 当前实际源基线c706、已采用M08 a633，与历史组件来源分域；standalone guard不含parent entrypoint，未来组合由root外部冻结，不能任意HEAD自批准 |
| identityRules.noRuntimeExecutionNow L910 | `only static/unit/build helpers permitted` | 当前精确票禁止actual prepare/finalize/build；contract API定义不能授真实helper运行权，unit亦须独审gate后另START |
| requiredNegativeTests | 仅旧8条，主要旧parent/reader域 | 新profile、跨profile/旧contract、35/source-frozen映射、mirror关系、bounded CArchive AND PYZ/TOC/member/decompress/marshal/ref/code graph预算，以及三个child原流/控制JSON/IO等是本次必需验收，不能在本适用合同中缺省 |

触发反例不需运行：只从同一JSON取`fixedLayout.embeddedContract`与`pathDomains.contract.frozenPath`，即给出不同路径；依pathDomains准备独立包会找旧M08合同，依fixedLayout/实际reader则找新合同。对inputs亦会得两种frozen位置。简单JSON/格式/contractSHA一致检查不会暴露这些语义冲突，因为这些描述字段当前没有关系断言。源码多处正确常量不构成忽略生效合同矛盾的理由。

最小修复：仅修新contract全适用域，明确source与frozen映射、独立target和launcher、runtime/external证据域、历史/实际/未来root批准来源、无运行授权及本次新增负例要求；保旧M08合同、parent和I05源不动。重新计算newcontract真实bytes/SHA，更新reader两常量与必要unit预期。加入关系断言覆盖上述domain与fixedLayout/inputMappings/targetCode，以及本次必需测试分类，避免仅改5个字符串后留下其他旧适用叙述。新hash不应嵌入contract自身或reader源hash造成循环。

本项已实时报告主控，主控定点确认并保持unit gate关闭。本首报不替尚未出现的新commit签收。

## 3. N1 [P3 nonblocking] 哈希IO失败时仍宜保无条件原流path引用

位置：builder `parityChild` L443–480；unit新Node字符串已有“evidence read IO failure”用例。

触发：child已经向两个FD写入原流，之后`parityStream`读取stdout哈希抛EIO。代码保原始文件，receipt.ioError如实记录、complete=false，stdout identity/captureRange设null，这些拒绝行为正确；但已知stdoutPath也不在receipt独立保存。它不等于原件丢失，按固定phase目录仍可定位，因此不夸成P2。

建议：receipt始终列stdoutPath/stderrPath，identity/hash/range失败仍null或UNKNOWN，不伪造complete或摘要；补IO负例同时断言文件引用仍存在。保持helper四字符串/standalone六公开返回不变，也不重跑child补流。主控表示愿随F1交作者窄修，本首报保持P3等级。

## 4. 已完成的实现级静态审查依据

### parent兼容与写面

builder从`function fail`到`buildEngine`结束的整个原函数块与c706逐字节相同，包含原helper、publish归档/回滚和默认返回；新增standalone支路没有调用publishEngineCopy，原entrypoint未改。CLI现在exact选择空args/唯一新flag，其他组合拒绝，符合新增固定profile接口。

unit原58个顶层function/class定义逐个AST相同，原BUILDER_UNIT字符串逐字节相同，八包sys.modules前缀清理/None/近似名/深child/首次fake_module抛setup异常的逆序恢复、native无fallback、strict解析/资源/外部binding等原断言没有退化。新增imports和新unit不冒这些测试已运行。

reader15个原定义因profile/可选bounded/notice/launcher支持修改，已全文核默认分支：prepare/finalize/load/external入口在IO前exact profile选择，默认parent继续旧contract/路径/四返回；anchor默认二赋值；parent post-evidence新增profile格式保护不接受standalone冒parent；parent原archive helper保留旧域。此为代码兼容审查，不是parent运行回归Pass。

### profile/35源guard与布局

_profile只接受exact str两枚举、返回MappingProxy布局；私有evidence加不可变profile，post校验重新核root/interpreter、standalone contract/schema/expectations/anchor，不缓存runtime成功。preflight只走有界文件/metadata/anchor get_code，无主动target/supplier/native import；post模块和native verifier维持真实sys.modules/spec/origin/loader及code检查。

_collect_standalone_manifest由AST取pins、验证22名字顺序、35 unique guard exact等contract，dirty和逐源字节等HEAD检查在采用前；32个非本次写面guard的Git blob与c706一致，未读取两sealed payload正文。五buildInputs固定顺序，lock/contract重复row一致；target与canonical private probe的bytes/source/code指纹必须相同。任意HEAD字节一致仍只产false-rootApproval候选，root外部批准未被取消。

prepare将fresh root或exact builder证据预留作为唯一路径，parent与ancestor symlink/foreign prefix/已有其他成员拒绝；嵌套provenance/contract/anchor按xb创建，四返回路径明确。inputs从旧source根核后只发新frozen row；lock逻辑uv.lock→provenance，四公共资源精确文件；无whole-v2或ontolearn_engine collect-data。licenses按实际声明/NOTICE/AUTHORS映射、准备时复核原字节、xb镜像。源码snapshot/_dist_inventory单次CODE_CAP Python读取仍保留。

### 实际archive/预算

_BoundedPYZ先核header/magic/offset/TOC长度，marshal_preflight在C反序列化前限制节点、深度、容器、声明长度/引用，拒active/cyclic/非法ref、错code字段和EOF；TOC列表逐名/type/整数/range/非空成员重叠/casefold/NFC检查，member解压前逻辑cap，zlib EOF/trailing/unconsumed/长度不符拒绝。实际code graph在归一化/marshal.dumps前另有展开payload/nodes/depth预算。

_bounded_archive先FILE_CAP读launcher、cookie/PKG/TOC闭合范围、TOC byte/记录数/正向推进/名字/type/option/非option唯一/物理区间/压缩声明逻辑cap检查；target及PYZ exact名/type，runtimehook为固定允许表，未知hook停报delta。compressed物理范围不与解压长度混算；target通过有界解压、marshal exact CodeType/EOF后才比较，仅递归归一co_filename、flags0/dont_inherit/optimize0。新分支不使用旧PyInstaller reader先无界处理再补查。

actualPYZ内部namespace exact24；供应22+private2、八包Python inventory、anchor分别真实extract/code指纹，unknown内部拒绝；target-CArchive另核后发targetCode四键。runtime返回只声称canonical PYZ，external verifier用root expectedSHA、strict targetCode/profile/provenance+完整目录inventory确认，未自批。native只观察已加载ExtensionFileLoader与实际origin/文件身份；source签名域不等同，未知保留。

### 三个child原两流/控制域

standalone prepare/PyInstaller/finalize各用独立wx文件FD作为spawnSync直接stdout/stderr，完整env/argv/cwd/PID/UTC/status/signal/error/ioError/overflow/文件bytes/SHA/range分录；无parent maxBuffer截流路径或outer补跑。nonzero仍可说明流完整，但不会返回成功；throw/overflow/signal/IO故障complete=false并停后继。receipt/control证据写失败固定拒绝并保原流，N1仅涉及故障时独立ref可改进。

控制stdout仅在完整原流已核后检查≤64KiB，fatal UTF8、BOM非JSON起始、重复解码key、未知/missing key、非string、额外token/非JSON空白均拒绝；接受形状exact4，raw文件不以JSON解析替代。helper path、finalbinding path/hash及standalone公开exact6均显式核，旧产物和原证据不覆盖。

### unit文本覆盖（未执行）

已逐个审新增profile正反例、unknown profile IO前拒绝、old contract/cross-profile/evidence改root/Python/anchor、unknown内部与第三方child、source/frozen/mirror/buildInput、NOTICE/AUTHORS/caps、exact证据预留/dirty/symlink、真实格式synthetic CArchive+PYZ、code/target/anchor缺失/篡改、TOC/member caps/duplicate/overlap/压缩域/trailing/marshal EOF、malformed marshal refs/声明/code fields在load前拒绝、loader graph在normalize前预算，以及新Node FD两流/失败/overflow/strict control/IO/64KiB边界/大原流/UUID保存等文本。

synthetic archive只给格式真实的惰性bytes/code对象，不执行它们；Node run/io/uuid是stub。它们不是现实PyInstaller产物/native/语义运行证据。单文件历史101或新增Node预期28均不当实际通过数；现阶段unit没有运行。

## 5. 结论、后继与原件

自有static-audit.py.raw仅对固定Git/AST/JSON/hash核对，exit0；这个exit0表示审计脚本完成，static-evidence仍明确F1 blocking、unitGate NOT_RELEASED。没有用它替代代码语义审查或产品单测。本目录保存原script/stdout/stderr、vector/关系/parent差异证据与本首报；F1/N1另列findings-d4686b.json供精确delta复核。

下一步仅由唯一作者修F1（及选定N1）并给新commit/vector；本首报不覆盖。独立actual delta审到0新blocking P1/P2后，才由主控按精确源票放单文件unit；首失败必须保全，不反向把本静审称unit运行通过。真实I05 consumer、完整loader JSON join、A一次、root binding批准及fresh source/frozen full-v1 B各一次、parent/平台/GUI/业务/发布均另门未验。
