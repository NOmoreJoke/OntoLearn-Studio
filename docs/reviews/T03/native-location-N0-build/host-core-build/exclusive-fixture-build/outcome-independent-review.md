# EXCL fixture 新输入第三次构建结果独立审查

2026-10-22。结论：未发现阻断本轮成功构建归档的新增问题。证据支持固定输入 15163b380035a3b402d5dbb485ab6d3d05e4e559 的唯一第三次新输入构建成功，状态仅 **built-unverified / NOT_RUN**。新 `_renamex_np` 导入已有静态链接证据；运行时 resolver、EXCL 文件系统行为、目标 OS、addon 及完整 N0 仍未验证。本报告不授权运行、第四次构建或新增 trace。

## 实际执行与固定证据

只读 Git HEAD、原 driver 命令1 stdout、build-once.result 和最终 supplierCommit 均为上述15163输入。新 digest 为 `227052c230da782ca62c20600e418f52e938378bd92f2961d7543f03ac43551c`，使用独占 core 目录；授权仍为 a5849a47abadee1e27cae1270bbbd213f3e1c0aa。源采用、锁六字段与完整12已由此前 prebuild 独审固定，本次不重复长源审查。只读 Git 产品范围 diff 相对15163为空。

`build-once.result.json`：1000B／SHA-256 `8d7fb668c8ca384420bab1d0cadd0e355f00e98908bc6156cbcc2c2dc7671cd3`，记真实 driver PID28056、exit0、outerDispatchOutcome=returned、attempt ordinal3、newInputNotAutomaticRetry=true，起止2026-10-21 UTC19:35:37.064879至19:36:23.522704。使用真实 driver 结果，没有以外层工具exit0冒充。

`driver-raw/supplier-log.0065.json`：21113B／`a2d0de5f00284bdf2743026a3c63df5b4cafb1f321192cb75ada6e371a10dbbe`。13个index0–12均completed、positive PID、status0、signal/error=null、failures/cleanupErrors空；firstFailure=null、persistenceFailures空，supplierCommit匹配。0–10为Git前置状态／HEAD／九源blob，11 configure，12只构建两个授权目标、parallel2。preflight的processExecution=false仅描述初始只读前门，随后构建记录另有真实子进程。

11 stdout明确9308 resource与33464 SDK的metadata映射、逐physical pin完成，之后compiler identification／ABI检查和配置生成完成；11 stderr为空。12 stdout记录core三TU及child一TU编译、两目标链接完成，stderr为空。未见测试或产物运行命令。首轮超时、第二轮成功及其失败诊断均不能被本轮覆盖，也不从三轮结果量化性能。

## 冻结产物与新符号

本审对获准两个新产物各静态读取／hash一次，合378024B；均精确吻合当前冻结pin，并与inspection前pin按path/bytes/SHA比较相同：

| 产物 | bytes | SHA-256 |
| --- | ---: | --- |
| location_core_test | 343904 | 229faf9fcf15ccbbc9e0e8fefefb1c91c016fc2ea6fea2df92998392e14e812b |
| location_child_probe | 34120 | be916e5252b21e6671c6bd2f32301f8581c1b32ce87f78a4a7b0f8314fb2a6b2 |

产物位于 `build/native-location/n0/darwin-arm64/227052c230da782ca62c20600e418f52e938378bd92f2961d7543f03ac43551c/core/artifacts/`。`artifact-pins.json`：1385B／`bcc5e589eb31e2bb900104e6b748907313c30cb726ac4791e3aabe64dc7dfd49`。

已读10项inspection的原双流及最终results：indices0–9，各有positive PID、exit0、signal=null、timeout=false；20个实际输出路径casefold后唯一。原始file输出均为Mach-O arm64；otool load command均platform1/minos15.0/sdk27.0，导入libc++、libSystem，loader dyld，无rpath。core有11个 `_nl_*` 外部符号。没有重跑file／otool／nm或执行产物。

独立比较旧core nm undefined原文与新原文，唯一新增 `_renamex_np`、唯一移除 `_rename`；新symbol table原文为 `(undefined) external _renamex_np (from libSystem)`。结合本次link exit0，可称链接器接受了该来自libSystem的动态导入；不能把undefined导入写成已观测运行时resolver或EXCL行为。min15也是构建／load-command证据，不证明macOS15实机运行。

`artifact-static-summary.json`：4553B／`c32e570e2e1ad51036aa01f6115ab6d0fd0293d40ed85875a5325720fafa6b78`；`actual-difference-summary.json`：1839B／`cf55fb9888344791e88c49373bd6da9a5ab1aa19fafc72d7afaab0320c370de7`。

## 有界真实依赖差异

本审读取当前877 covered对象、旧第二轮875covered+2unmatched对象并比较路径集合：两者恰同877。当前priorEvidenceSHA256与实际旧used JSON摘要吻合。四个新depfile归档bytes/SHA均与当前used记录相符；一次静态分词并作纯词法normpath得到1798tokens、877唯一路径，集合精确等于当前used，新增／删除均空。

5项source-b592的pin逐项等当前完整12清单；870项prior-direct的嵌套approvedWitness逐项等旧记录；另2项来源为旧alias catalog，unknown为0。sys/stdio.h为旧direct witness已有路径，2415B／`a8078ae1cba1a46a66d0de6fe7f13bbc969cdb7e78fc2d4b9a5c5cdaaf16126b`。这轮差异不要求新供应记录。没有重读SDK/source大清单、42772映射或header内容。

`used-dependencies.json`：1819818B／`6f1671e82582f801c5159e41e471b67dfdd7abb449a163b4f36ac2ce07d7dd70`。此处来源覆盖是归档depfile与既有pin/witness身份的对应，不是独立compiler-open轨迹。未重复hash供应payload。

两alias回执只记录lstat/readlink/stat-follow-alias。独立比较其linkname、词法目标、followed inode/device/bytes/mtime和approvedRegularPin，与旧catalog receipt相同。当前物理别名身份已有这次受限只读操作的原回执；本审未亲自重做操作，未打开或rehash目标header。`sdk-alias-current-identities.json`：2792B／`6ffa7818f5c0ca80f01069b00de76ff1227fd29aacf1f6dcb47e06e3a579a0c5`。不能由元信息相等推成已跟踪编译器实际打开的对象。

四compile command与生成compile_commands原文逐项相同，两link-driver command与归档link.txt逐字相同，四显式object输入pin有保留，本审未重hash这些对象。`compile-and-link-evidence.json`：12826B／`b7cfca11c862bbe235652f4a5fa96d3326c4ccb79e91fa5b4c13fe7de476b724`。compiler probe implicit记录不替代最终linker选中跟踪；selected stub／archive／member、嵌入第三方和runtime闭包继续PENDING，无新增-t/-map或重构建。

## 执行纠正、归档和预算

差异collector的实际一次调用有PID29836、exit0、起止UTC及完整stdout/空stderr，输出1798／877、5+870+2、unknown0、selectedMetadataRecords0，与归档相符。`used-analysis-execution.json`：509B／`1ca182fb7bb1ac676176cf08de10b23c329ed014beb061d7674972d27882abd0`。已静态读collector实际代码：未变路径走旧witness，本轮无added路径，selected-original-record分支未用；metadata buffer读取0、全42772映射0符合本轮输出，未把未来条件分支冒充已执行。

`collector-precheck-correction.json`：454B／`95bb87261267e8fb2ab9e29083572d23d4b00d589066d66b2018ccbb3b833c90`。它保留一次不必要内存转义规范化的AST SyntaxError，明确在写脚本／collector dispatch／供应读取之前。之后原始脚本及纯deps检查通过才首次执行；不能把该前置失败写成实际collector失败重跑。已知initial-plan-correction的算术断言亦保持历史。本审自身只读核对曾误假定新link row仍有path字段，触发KeyError（原工具chunk afc8ce）；随后按target定位既存link.txt补核后半段，没有重hash两产物、重跑collector或再次解析大used JSON。

清单记92个driver raw／快照、17个generated原件和144个外部输出／3020856B；本审核其小清单与重点原件，不重复owner最终全量Git index字节闭包，不预签该未发生结果。input-closure的30项是15163时的历史过程pin；后验.gitattributes扩展由小delta明确区分，当前54条均为精确stream -text，无glob，未用当前属性字节替换历史输入身份。现有产品范围diff为空。

现有whitespace回执是full exit2、62处／7个generated原始文件，filtered exit0。没有trim原raw，不签全量whitespace0；本审未重跑此检查。

`read-account.json`：1909B／`b8f19493430715693461b8ff3c2686d0f7b40e3b03a37e46a5f2ab3bee9bb475`。64GiB下构建阶段声明55068578800B，余13650897936B；供应9745727085B独账保留。实体保守256632/300000；metadata含有限预留1313343/1500000，余186657，旧1100000超255及1100287关闭界保留，未用预留未自行释放。上述是应用声明／预留，actual OS/compiler/loader IO仍null，不是性能或全IO实测。

本审宽口径主记录包括两次当前877对象读取、一次旧877对象读取及一次1798原dep token，共4429；再将provenance／reference访问、manifest、命令／inspection、alias与小receipt等全部保守纳入，总访问上界10000，小于独审15000预付。应用累计读取保守小于10MiB，小于12MiB读缓冲预算，含对当前used文件另一次纯摘要字节读取；每次对象读取累计计入，没有把纯摘要扫描虚构成新增供应记录，也未声称OS IO实测。

本次只新建本报告。除各一次hash获准新产物外，没有供应实体读取／hash、全SDK/source/sidecar映射、I06长审回读、inspector/driver/构建/测试/产物执行。成功构建、新符号静态证据及所有失败／更正与PENDING应共同保留；任何运行或新构建需另一个精确授权窗口。
