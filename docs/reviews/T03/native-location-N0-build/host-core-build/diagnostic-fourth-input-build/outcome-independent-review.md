# 第四次诊断新输入：实际构建结果独立审查

2026-10-22。结论：未发现阻断本轮成功构建归档的新增问题。证据支持固定输入d98b503ebe9c477d30d0f36d831cffbeeaf2a988的唯一第四次新输入构建成功，仍仅 **built-unverified / NOT_RUN**。诊断源码已编译链接，但没有native产物执行或owner-create诊断输出；首次owner-create根因、EXCL行为及完整N0均未证明。TS test在本轮仅由Git前门验证身份，没有运行其单元测试。本报告不授权第五次构建、运行或额外trace。

## 真实构建与输入

只读Git HEAD、原命令1 stdout、结果fixedInputRef及最终supplierCommit均为d98b503ebe9c477d30d0f36d831cffbeeaf2a988。digest为 `a0e724fdf90afa980f01719fc8cc4d55f158400cf5abe26665c72a2d288cac77`，使用独占core目录，授权为7b58202ce147c25ba31a45d61a066166b80ca57e。新两源、锁八叶、完整12的采用前审查沿6399B prebuild报告，本次未重读九源blob或I06长审。产品范围相对固定输入的只读Git diff为空。

`build-once.result.json`：1012B／SHA-256 `be65c19abd952eb244f3e9d77e9cac591bc32d8cb5b0a8b4bd8d081b26ade457`。真实driver PID75394、exit0、outerDispatchOutcome=returned、attempt ordinal4、newInputNotAutomaticRetry=true；起止2026-10-21 UTC20:36:36.016629至20:37:17.120343。没有用外层工具退出码替代真实driver结果。

`driver-raw/supplier-log.0065.json`：21113B／`1f4817c4c3808509f201a87ac3f266b50bad012d596c6c92bbd73ea7b5959303`。13个index0–12均有positive PID、status0、signal/error=null、failures/cleanupErrors空，firstFailure=null、persistenceFailures空。0–10为Git状态／HEAD／九源blob核验，11 configure，12只构建location_core_test、location_child_probe，parallel2。初始complete-readonly/preflight的processExecution=false不描述随后真实构建子进程。

11原stdout明确完成9308 resource与33464 SDK逐physical pin验证，再完成AppleClang identification／ABI检查、配置和生成；11 stderr为空。12原stdout记录core三TU和child一TU的编译及两目标链接完成，stderr为空。build-once原stdout最终为built-unverified、tests NOT_RUN，原stderr为空。未见额外构建、CTest、try_run或产物执行命令；旧三轮原件和历史失败不由本轮成功覆盖。

## 冻结产物和静态证据

本审对获准两个新产物各读取／hash一次，共378040B，均与冻结pin精确相同；inspection前后pin按path/bytes/SHA比较亦相同：

| 产物 | bytes | SHA-256 |
| --- | ---: | --- |
| location_core_test | 343920 | d4f5ca322146d9696860a74de4bee2ad27866a2223340669898fb82cbbfeb817 |
| location_child_probe | 34120 | 21928ca2b5570055fad4bebcd81fcb658016ca9a738294397a83056b662b87e8 |

原位路径为 `build/native-location/n0/darwin-arm64/a0e724fdf90afa980f01719fc8cc4d55f158400cf5abe26665c72a2d288cac77/core/artifacts/` 下对应文件。`artifact-pins.json`：1385B／`37fa5a3d8e22d7582b2277af723c53a142ca8878f830f1ac9792bb4bc03f39ea`。

原10项file／otool／nm inspection回执均positive PID、exit0、signal=null、timeout=false，20个实际stdout/stderr路径casefold后唯一，全部原stderr为空。归档file/摘要记两者为arm64；本审由otool原load commands复核platform1/minos15.0/sdk27.0、libc++.1.dylib与libSystem.B.dylib导入、dyld loader、rpath数0；core原symbol table有11个 `_nl_*` 外部符号。

独立比较新core undefined原文与第三轮原文，新增／删除均为空，`_renamex_np`仍为 `(undefined) external _renamex_np (from libSystem)`。link exit0及该归属只表示静态链接接受动态导入，不代表运行时resolver、Mac15实机或EXCL行为验证。新增有界owner-create诊断源码的编译链接也不能证明首次失败已修复，未观测到该诊断的native输出。

`artifact-static-summary.json`：4553B／`5225307de2b5954491adb063f09815c0a7a23fcc5e94111d633221490cc51cc0`；`actual-difference-summary.json`：1002B／`3f2d2c20b5f6d49ed2302c51da1ef87dceb4196c8ec709e57a81fd2ec803f0f1`。

## 真实依赖、alias与链接增量

本审各读取一次当前used877对象和第三轮used877对象，第三轮原字节摘要与当前priorEvidenceSHA256吻合；两个归一化路径集合恰同，新增／删除为空。四个本轮depfile归档bytes/SHA与当前记录均相符；一次静态分词加纯词法normpath复得1798tokens、877唯一项，集合精确等于当前used。

5项当前source-fc6237 pin逐项等完整12清单；870项prior-direct的嵌套approvedWitness逐项等第三轮记录；另2项是第二轮legacy alias catalog，unknown0。由此复用既有witness，没有重新全量映射42772或读取新供应记录。

`used-dependencies.json`：2245258B／`e6a402c9776aa95a3036b3cb0208d6d63187366e73fc145df473bda3bcb761bf`。来源覆盖是depfile与既有pin/witness的对应，不是独立compiler-open轨迹；本审未读取SDK/source供应payload或hash header。

两alias当前回执的linkname、词法目标、approvedRegularPin及followed device/inode/bytes/mtime均与原第二轮catalog回执相符。原操作仅lstat/readlink/stat-follow-alias，无header内容读取或rehash。本审只比较回执，没有重复实际操作。`sdk-alias-current-identities.json`：2792B／`6ffa7818f5c0ca80f01069b00de76ff1227fd29aacf1f6dcb47e06e3a579a0c5`。当前alias元信息匹配不等于已经独立跟踪编译器实际打开的对象。

四条compile command逐项等保存的compile_commands原文，两条link-driver command按target定位后逐字等归档link.txt，四显式object pin有保存，本审未重hash这些对象。`compile-and-link-evidence.json`：12826B／`1eead0bce6e461efb677940037875bc781a709ade063388926431e50eceb0896`。compiler probe implicit信息不替代最终linker选中记录；selected stub／archive／member、嵌入第三方及runtime闭包继续PENDING，没有新增-t/-map或重建。

## collector、历史失败与原件闭包

差异collector实际一次调用PID77170、exit0、起止UTC及完整原双流均保存，stdout的1798／877、5+870+2、unknown0、selectedMetadataRecords0与归档相符，stderr为空。`used-analysis-execution.json`：497B／`6d6b56814b5196c8e680b5202c90885472b266fcd581d743765c975041ac0e96`。本审静态比较本轮collector和上一冻结版本，实际差异仅本轮D／prior／digest、legacy alias仍定位第二轮目录、source类别标签；未增加供应枚举或构建操作。selected-new-dependency-records为空、metadataBuffersRead为空，未将条件分支冒称已执行。

构建前whitespace原full exit2及owner expected0断言停顿必须保留。`prebuild-whitespace-check.json`：1157B／`113c0d9f38bbe496fcae8d62cbfef49a7f11a716086b26380d4132e9bcfd0281`。本审解码base64原stdout，明确只有source-adoption.patch第5行原始diff空白上下文，原stderr为空、精确排除后filtered0。receipt记该断言发生在receipt／输入manifest／commit／dispatch前，不是构建失败或第五次重试；没有修剪源或raw patch。本次不重跑whitespace检查。

小清单分别记92份driver raw/快照、17份generated、144外部原位文件／3022047B；本审仅读清单和重点原件，不重复完整原件归档hash。input-closure的29文件加self属于固定d98时的历史输入身份。后验.gitattributes从2条增至52条精确stream -text、无glob，实际2070B／`ad82bb91a06b30e546653139d0b5ed84890384a8034920b1af8c5ae66c117b8e`，由postbuild-process-delta明确分阶段，不将当前属性字节冒充历史输入pin。

后验whitespace小receipt已读：full exit2仅generated62处／7文件，filtered0；它与prebuild raw patch第5行是不同过程阶段。本审未重跑、未逐项重取所有空白诊断，不签全量whitespace0。最终owner完整Git index bytes/SHA实检尚未发生，本报告不预签；新的最终闭包须另存，不能覆盖旧失败。

## 账和独审范围

`read-account.json`：1929B／`f77c7e6c531d536e314e14028b6d3ce1d9c4551c22c465a0ea2d609cdc807192`。本轮先付构建声明72958464344B/80GiB，余12940881576B，旧供应9745727085B独账保留；实体保守342176/400000，首CMake完成仍unknown、不当0。metadata从根1328343带入，含171088及pre2000、owner15000、作者结果独审15000、close10000、root另15000，为1556431/1800000、余243569。root独审票与本审票分别保留，未自行释放任何旧预留。actual OS/compiler/loader IO仍null，不是性能测量。

本审主记录为当前877、prior877、dep tokens1798，合3552；连同provenance／reference读取、manifest、commands、inspection、alias、小receipt及重复小文本比较，保守宽访问上界8000，低于本审15000。应用累计读取保守小于8MiB，低于16MiB预付；主批只读缓存实际4938753B，另有有限小receipt/文本读取均计入上界。该数字是应用字节读取计票，不是OS IO/RSS实测。当前与prior大used各仅解析一次；没有重复全mapping或产物hash。

本次只新建本报告。除各一次静态hash两个获准产物外，未读取供方SDK/cache/payload、九源blob或I06长审；未运行inspector、driver、构建、测试、native、GUI/HMR或付费服务。所有历史失败、未知drain及未验证门继续保留；后继native CLI由原I06准备并另获精确授权，不能从此成功构建推导运行许可或首次owner-create根因结论。
