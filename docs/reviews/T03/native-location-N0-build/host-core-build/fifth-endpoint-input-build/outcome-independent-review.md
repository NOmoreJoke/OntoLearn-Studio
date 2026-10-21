# 第五新输入：Mac终点诊断实际构建独立审查

2026-10-22。结论：未发现阻断本轮成功构建归档的新增问题。固定输入0514d37e32e31ae569e583bb56ec225ebc0483e6的唯一第五次新输入构建成功，状态仍仅 **built-unverified / NOT_RUN**。四终点诊断源码已编译链接，但终点日志、实际errno、002 UNSUPPORTED根因、EXCL及N0运行行为均未观测。本报告不授权第六次构建、工具扩查或产物执行。

## 实际构建与证据身份

只读Git HEAD、driver命令1原stdout、结果fixedInputRef及最终supplierCommit均为上述0514。新digest为 `0d5223985fcd9761c60cee55d4c258af9b8204c8b0131df1535928cd1953c8fb`；授权仍为a447556e2cbbd81ede38bf2148714e5f1f59fbfd。单Mac采用／锁六叶／完整12沿7287B prebuild独审固定，本轮未重读九源blob或I06长审。产品范围相对0514的只读Git diff为空。

`build-once.result.json`：1005B／SHA-256 `d2f3ae8ad4e177246a9580c766aa4e06ad416f8d6f9aa6c7984ccc2bb1d8422f`。真实driver PID8423、exit0、outerDispatchOutcome=returned、attempt ordinal5、newInputNotAutomaticRetry=true；起止2026-10-21 UTC22:03:06.447086至22:03:51.579125。不以外层工具退出码替代driver结果。

`driver-raw/supplier-log.0065.json`：21087B／`c7d80e7dd91e0007fea1d49b911d6b32137dbb69c344e39b1b6332f1935cdbf0`。13个index0–12均positive PID、status0、signal/error=null，failures/cleanupErrors空；firstFailure=null、persistenceFailures空。0–10为Git状态／HEAD／九源blob，11 configure，12仅构建core／child、parallel2。最初preflight的processExecution=false只描述前门阶段，随后另有真实构建子进程。

11原stdout明确resource9308与SDK33464的metadata及逐physical pin验证完成，再完成compiler identification／ABI检查、配置和生成；11 stderr为空。12原stdout记录Mac/core/test三TU和child一TU编译及两目标链接成功，stderr为空。build-once原stdout最终built-unverified/tests NOT_RUN，stderr为空；没有CTest、try_run或产物运行记录。

## 两产物及静态范围

本审对两个获准新产物各读取／hash一次，共378216B，精确吻合冻结pin；inspection前后pin按path/bytes/SHA比较相同：

| 产物 | bytes | SHA-256 |
| --- | ---: | --- |
| location_core_test | 344096 | 65cca109ce2a43b24c94fc013b5e91127548d4be3d39de5330024128ffdb8039 |
| location_child_probe | 34120 | 12d355d3cc43fc5c39b6e8689d7e0dabb6909b8dfd7a7deed6322f3351d80e48 |

原位目录为 `build/native-location/n0/darwin-arm64/0d5223985fcd9761c60cee55d4c258af9b8204c8b0131df1535928cd1953c8fb/core/artifacts/`。`artifact-pins.json`：1385B／`b710ddca85187bb8894b1184c5c4c8a7e1f007bff85c3f5d92429d06da4d90f6`。

10项既有file／otool／nm回执均positive PID、exit0、signal=null、timeout=false；20个stdout/stderr输出名casefold后唯一，原stderr均为空。本审从原流核两者arm64、platform1/minos15.0/sdk27.0，libc++及libSystem导入、dyld loader、无rpath；core有11个 `_nl_*` 外部符号。

新core undefined原文相对第四轮新增／删除均空，`_renamex_np`仍标 `(undefined) external _renamex_np (from libSystem)`。静态链接成功及导入归属不能代替运行时resolver、Mac15实机或EXCL验证。未执行新增Mac四终点诊断，不能据编译关闭具体002根因或实际errno门；新增stdio日志有I/O成本，不是零成本证明。

`artifact-static-summary.json`：4553B／`24cdb69c1d585a1d8a2cf57c53cba3e91b9f4b3f71b913390d59cd49204b8d54`。

## 本轮真实依赖差异

当前和第四轮used大JSON各读取／解析一次；当前priorEvidence摘要与实际旧JSON吻合。两者全局归一化路径集合恰同877，无新增／删除；870项prior-direct嵌套approvedWitness逐项等旧记录，5项当前source-fc9853 pin逐项等完整12，另2项legacy alias，unknown0。

四个新depfile归档bytes/SHA均与当前记录相符；一次静态分词及词法normpath复得1805tokens、877唯一路径，集合精确等于当前used。相对上轮1798tokens，增量7全部来自Mac TU：171→178。两侧Mac depfile归一化后的新增引用恰为下列SDK usr/include相对路径，删除为空：

- `_printf.h`
- `_stdio.h`
- `c++/v1/cstdio`
- `c++/v1/stdio.h`
- `stdio.h`
- `sys/_types/_va_list.h`
- `sys/stdio.h`

七项全部已在第四轮全局used中，其逐项existingGlobalWitness与当前对应witness相同。因此是既有全局依赖在Mac TU中新增引用，不是新供应对象；不能将“全局增删为空”误写为“每TU没有变化”。

本审初次辅助比较混用了current已normpath与prior裸literal，除七header外出现location_abi.h的src/../同义路径假差异。随后只补读两份小Mac depfile并对两侧作相同normpath，精确恢复七项／无删除（工具c5305b）；没有再解析大used或全四dep，也没有重复hash产物。新增349个token访问及小receipt重读计入本审预算，不把此比较纠正当产品问题。

`used-dependencies.json`：2691563B／`e174d62be6b4560e756362ed714b603fc9c044592b548afa3797a82c3989dd34`；`actual-difference-summary.json`：18017B／`2d69c66edc8db362b4805def9b193485ab82e9b0fdd4a55377567cee416e3d70`。这些对应关系不是独立compiler-open trace；没有读取SDK/source供应metadata或header内容。

两known alias回执的linkname、词法目标、approvedRegularPin、followed device/inode/bytes/mtime均与第二轮catalog回执相符。实际只记录lstat/readlink/stat六项元数据操作；本审不重复操作或rehash header。`sdk-alias-current-identities.json`：2792B／`6ffa7818f5c0ca80f01069b00de76ff1227fd29aacf1f6dcb47e06e3a579a0c5`。alias身份匹配不等于已追踪编译器实际打开目标。

四条compile command逐项等生成compile_commands原文，两条link-driver command按target定位后逐字等归档link.txt，四个显式object pin有记录，本审未重hash对象。`compile-and-link-evidence.json`：12826B／`e81c383f330599dcbd36789ea6543fcb53632399fe1d946d06a7882f0029127f`。最终selected stub／archive／member、嵌入第三方及runtime闭包仍PENDING，不以compiler probe implicit信息替代最终选择，不增加trace或重建。

## collector、原件及检查阶段

差异collector真实一次PID8760／exit0，有起止UTC和完整stdout/空stderr。stdout1805/877、5+870+2、selectedMetadataRecords0、unknown0与归档吻合。`used-analysis-execution.json`：493B／`0d7ca4a8d85b8b7ea2e3e62b53b1fb3ecebd94b8df016ee55c0988059f52aa11`。本审静态比较collector与第四轮，差异仅D、prior、digest及source类别标签；legacy alias仍定位第二轮catalog。selected-new-dependency-records为空、metadataBuffersRead为空，全42772静态映射0，未打开新供应对象。

小清单分别记92份driver流／快照、17份generated和144个外部原位文件／3029917B。本审核清单与重点原件，不重复owner完整归档hash或预签最终index实检。input-closure的30文件加self属于0514时历史输入；后验属性扩展仅为过程原件保全，当前52条均精确stream -text、无glob，不改完整12或拿当前属性字节冒充旧输入pin。

本轮prebuild whitespace回执full0、filtered0、双流为空，未trim raw patch；不能套用上轮patch第5行诊断。`prebuild-whitespace-check.json`：385B／`307fbcca0310c5d6c658a57caf1dd23bc5245bba5a6c5654e655698676a039ac`。后验generated原raw的另一检查full2，仅62处／7文件，filtered0；不签全量whitespace0、不修剪原始生成物。本审未重跑检查；最终owner完整Git index bytes/SHA实检待后续，不提前宣告闭包通过。

已知7287B prebuild报告内只读误查rootclosure-authblob的exit128及纠正继续保留，属于当时审查辅助查询，不是本轮产品／构建失败，未因此自动重试。旧四轮、001/002、未知fixture/PID、首ETIMEDOUT/drainunknown及旧255超cap与关闭界均不得覆盖或清零。

## 累计账及本审上界

`read-account.json`：1540B／`0c558588191c7e9745dff293b70381310293b40ef14d077ae99816e085123b21`。构建声明90848349888B/96GiB，余12230865216B，旧supply9745727085B独账，combined100594076973/112824942189；实体保守427720/500000、已知完成384948，首CMake仍unknown、不当0。metadata1556431+171088+pre2000+owner15000+作者审15000+close10000+root另15000=1784519/1800000，余15481。root票与作者票分开，旧预留不释放。

本审主记录为current877+prior877+新四dep1805+旧Mac171=3730；补核两小Mac349后4079。另将provenance/witness、reference、小manifest、命令／inspection、alias、diff与小receipt等按宽口径计入，保守总上界10000，小于作者独审15000。主批应用读取缓存实际5869017B，Mac小补核63726B，加初始有限小文档读取，累计保守小于8MiB，小于16MiB预付；没有使用root另15000或释放未用票。应用读取与记录上界不是OS IO/RSS或性能实测，actual OS/compiler/loader IO仍null。

本次只新建本报告。除各一次静态hash两获准产物外，未读九源blob、I06长审、旧四轮大日志、SDK/cache/供应payload或全42772映射；没有重跑inspector、driver、构建、测试、native、GUI或付费操作。新pair的后继精确调用仍须原I06准备并另获根运行授权；本轮成功构建不证明根因、errno、EXCL或父平台门已关闭。
