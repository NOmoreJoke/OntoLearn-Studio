# 第六次ACL remedy新输入：结果独立审查

2026-10-22。结论：未发现阻断本轮成功构建及受限静态归档的新增问题。固定输入bfe137f371361f9fda446d5cbe6b3079c5433ee5的唯一第六次新输入构建成功，可接受为 **built-unverified / NOT_RUN**。本轮没有运行core/child或三份Darwin ACL fixture；空ACL/absence、单ACE拒绝、invalid-FD、003 remedy效果、installed libSystem行为及N0均未验证。本报告不授权第七构建、native/API/ACL运行或追加trace；最终index闭包另由owner实检。

## 实际driver与构建范围

只读Git HEAD、driver命令1原stdout及最终supplierCommit均为bfe137f371361f9fda446d5cbe6b3079c5433ee5。build-input-plan及前门实际digest同为 `1526093e58aeaa43cd5c96dfc911dd032759df27c039bf3d11eacfb1e6cbfd50`。B为 `build/native-location/n0/darwin-arm64/1526093e58aeaa43cd5c96dfc911dd032759df27c039bf3d11eacfb1e6cbfd50/core`。产品范围相对固定输入的Git diff为空；不重复已完成的8078B prebuild源／锁审查或8750长审。

本轮driver回执按三个原件合读：planned记原Node CLI、cwd、fixedInputRef、attempt6及startedAt；dispatched记PID47416；result同PID、exitCode0、finishedAt、NOT_RUN、artifactExecution=false、noRetry=true。不能将较简result字段补造为其本身包含argv/ref。`build-once.result.json`为198B／SHA-256 `0e242252d83b44cfc4f72a6c365e83b1c571a6ad6cbbd098a49246050410c5bb`；planned为546B／`de992787767b6fff3053ceccca3cfea24cb17353a299141a2d8784dc187ba527`，dispatched为73B／`da00fc83a3084d6aaf286033495691376b0210aa898321624bf1f619b9637f8d`。这是同PID的真实driver结果，不用外层工具exit0替代。

`driver-raw/supplier-log.0065.json`：21113B／`547b867f04002630eec0e13aacca27d0541584e71966f55ace915477bcbf57ff`。13个index0–12均positive PID、status0、signal/error=null，failures/cleanupErrors空；firstFailure=null、persistenceFailures空。0–10为Git状态/HEAD/九源blob，11 configure，12仅构建core和child、parallel2。初始complete-readonly的processExecution=false只描述preflight，随后有真实构建子进程。

11原stdout明确9308 resource和33464 SDK逐physical pin完成，然后compiler identification/ABI、configure/generate完成；11 stderr为空。12原stdout记录四TU编译、两目标链接成功，stderr为空。build-once最终stdout为built-unverified/NOT_RUN，stderr为空。没有try_run、CTest或生成产物执行。

## 冻结产物与十项只读检查

本审仅对两个获准新产物各读取/hash一次，共396776B，均精确等冻结pin；inspection前后pin按path/bytes/SHA比较相同：

| B/artifacts下产物 | bytes | SHA-256 |
| --- | ---: | --- |
| location_core_test | 362656 | 17fb8b48ec3e79cfd36015edc4047bbd390ac0145dd2c40b1c20850455771f60 |
| location_child_probe | 34120 | 5b9978c2e7bbb8d3ee51d3d94d95ab4797ac01337654180cf121d89dc3e05b98 |

`artifact-pins.json`：1385B／`6bf5b4735982f15eb3cb9a02f1bcb379807cf5da778dce8056e5f0e56eaa1c51`。10项inspection实际argv/target/标签/双流路径逐项等plan，各有positive PID、exit0、signal=null、timeout=false；20个输出路径casefold后唯一，原stderr均为空。未重跑file/otool/nm。

从原file和otool流核两产物arm64、platform1/minos15.0/sdk27.0，仍导入libc++.1与libSystem.B，loader为/usr/lib/dyld，无rpath。core保持11个 `_nl_*` 外部定义。min15是静态构建/load-command证据，不证明Mac15实机运行。

独立比较新旧nm undefined原文：core新增17项（ACL构造/权限操作、filesec init/free/property/query、fstatx_np、mbr_uid_to_uuid、printf），仅移除 `_acl_get_fd_np`；child无增删。该结果逐项等actual-difference-summary。新导入与实际link exit0是静态链接接受证据，不证明API已调用、ACL remedy已成功或公开Libc源码即installed实现。`_renamex_np`仍是既有libSystem导入，EXCL行为仍未运行验证。

`artifact-static-summary.json`：5004B／`c4700df55f9f0c3e858a4bd17361d18b5c265f9799b37966b31ae8f3932efda0`；`actual-difference-summary.json`：3612B／`fdd4581c06b698e522cf078ef2bafd5d779dbe68d1a9c7f3a5da7338e07ec46e`。

## 真实dep差异与三条新selected

current used880及P5 used877各读取/解析一次，priorEvidence摘要与实际P5字节相符。独立路径集合比较只新增membership.h、ntsid.h、uuid/uuid.h，无删除。870项prior-direct嵌套witness逐项等P5；5项当前source-1217 pin逐项等完整12；2旧alias与3selected之外unknown0。selected三个path集合恰等新增集合，其witness逐字典等当前used对应条目。

四个本轮depfile归档bytes/SHA逐项匹配；一次分词/normpath得到1808 tokens和880唯一项，集合等current used。由P5保存references重建每TU旧集合并对比：child57→57、core696→696、Mac178→178；仅test874→877，新增上述3头，无TU删除。没有重读旧五轮大日志或源blob。

`used-dependencies.json`：3156859B／`c7a1c91c0d6cbb0e9f1daf087c79413c65973d5cc2c128b03a22c2196b2d3357`。这些是depfile路径与pin/witness的对应，不是compiler实际open轨迹。

`selected-new-dependency-records.json`：8372B／`3a36a386af5e943e7f2095304dc363bf3cd94ccf2090e2b31488d96a615bd4ab`。独立核每条rawRecordUTF8的bytes/SHA、JSON四pin与保存pin相同；sourceMetadataPin和recordsIndexPin均逐项等当前锁SDK descriptor。然后仅在该已固定records文件的三个byteOffset定点seek，核前一字节LF及完整raw字节相等：

| SDK usr/include相对路径 | 保存header bytes | rawRecord bytes | byteOffset |
| --- | ---: | ---: | ---: |
| membership.h | 8889 | 353 | 8668529 |
| ntsid.h | 1209 | 343 | 8771210 |
| uuid/uuid.h | 2711 | 351 | 8949613 |

三次定点共读取1050B（1047B原行加三个边界字节），未hash/读取整个索引，未扫描前缀重数行号。lineNumber17901/18174/18670作为原保存label保留，本审独立确认的是offset与原行；不虚称重新证明了行号。index大小与pin一致，但整index bytes/SHA沿owner已有全pin查验与原映射证据，不冒称本审再次验证。

三条lstat身份回执均regular、bytes等批准pin、payloadOpenedOrHashed=false；本审未重做header lstat，也未打开或hash header内容。header内容SHA是已批准记录中的身份，不是本次独审新测的payload hash。原供方95f07d及source/index双pin追溯保留，不能据定点行和元信息推断编译器实际打开的对象或runtime行为。

## 条件索引遍历、collector与链接

本轮真实出现新增全局依赖，故使用了预批条件票。已读collector实际代码及执行原件：一次PID49406/exit0、原stdout/空stderr吻合1808/880、5+870+2+3、unmatched0。script13079B／`c5cd936a8e0f55627c7e5d187ccd6813d60eb6636e07aad637dc2c7349f7f705`与执行plan相同；execution回执157B／`34d9526d148bcc3861d3aefed61d673f201f28b0ec83cd0ec057e231b8ae3a68`。

代码/回执明确一次遍历两个批准records索引，共解析42772条index记录、读取19368210B，小于64MiB，选出并保存3条；不是“只解码3个JSON对象”。sourceRecordsDecoded=3是selected身份计数，不能抹掉独立的index_visits42772。fullUnchangedSourceSidecarMappingPasses=0仅指未再做source↔sidecar完整映射；不能写成没有读批准index全体。此前SDK头行/首记录的2条格式探查另记在owner预留，不当零、不冒充第二个正式42772 pass。上述均由owner执行，本审没有重跑该条件遍历。

旧两alias只记录lstat/readlink/stat六操作，其linkname、词法目标、approved pin与followed inode/device/bytes/mtime回执同原catalog；本审只比较小回执，不重做操作或读取header。`sdk-alias-current-identities.json`：2792B／`6ffa7818f5c0ca80f01069b00de76ff1227fd29aacf1f6dcb47e06e3a579a0c5`。

四条compile command逐项等生成compile_commands，两条link-driver command按target定位逐字等归档link.txt；四显式object pin有保存，本审未重hash对象。`compile-and-link-evidence.json`：12826B／`595a2fc61d9e8883c05a078402828b28e8549049058a30057047858347459064`。最终selected tbd/stub、archive/member、嵌入第三方和runtime闭包继续PENDING，不用compiler probe implicit信息替代，不额外trace或重建。

## 原件、预算与未验证门

小清单记92份driver原流/快照、17份generated、144个B原位文件/3104411B；本审只核重点原件和清单，不重复完整归档hash。input-closure的30文件加self为bfe137时历史过程身份，后验属性从2→52精确stream -text、无glob，仅过程保护，不修改完整12或冒充历史输入字节。最终owner delivery manifest/index实检尚未生成/完成，本报告不预签。

prebuild whitespace原full0/filtered0。后验原始base64 stdout完整保留，实际full2；本审直接解码并导出62处/7文件：51条trailing whitespace、6条space-before-tab、5条末尾空行。初次派生JSON漏6条space-before-tab后已纠正，原始stdout未改；不能把早先56条派生数当完整结果。普通范围filtered0不等于全量whitespace0，不trim生成原件。本审未重跑检查。

`read-account.json`当时2390B／`2996a3d7c056af486734f72f49d23bec9eeb70d2f25ad5c861bff29fad76e3b1`。build声明108738235432B/128GiB，余28700718040B，旧supply9745727085B独账保留；combined118483962517/147184680557。实体保守513264/600000、已知完成470492，首CMake仍unknown。metadata1784519+171088+pre2000+owner15000+作者审15000+close10000+root另15000+条件42772+selected256=2055635/2250000，余194365。已用条件pass/3selected及2格式探查如实分账；root与作者票分开，旧消费/预留、255超额和未知drain不重置或释放。actual OS/compiler/loader IO仍null，不能量化性能或全IO。

本审主读取为current880+prior877+本轮dep1808，共3565；另核旧references1805、witness/provenance、3selected和3定点行、有限manifest/command/inspection/symbol及小receipt。按宽口径保守总上界12000，低于本审15000票，未使用root另票。主批应用读取6759767B，三个seek1050B，另有有限脚本/receipt/小文档读取，累计保守小于10MiB，低于16MiB预付；不声称OS IO/RSS实测。大used各仅解析一次，产物各hash一次。

本次只新建本报告，没有产品/源修改。除上述两个获准artifact静态hash及三个records定点行外，未读SDK/cache/header payload或完整供应/源池，未读8750长审、未重做旧算法审查，未执行build/native/test/inspection/API/ACL/GUI/付费行为。三fixture及ACL remedy尚无运行证据，installed libSystem及内部资源/真实ACL门不由静态链接关闭；SQLite拒绝线及wholeH/父平台/目标OS/外审/CI/真人等门保持。
