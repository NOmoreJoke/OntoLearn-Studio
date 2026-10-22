# 26 包组合的前向协议 delta 方案（v3 proposal，未采用）

控制方已明确正式获批 develop=5f（其实际ls-remote核实；作者未联网），local1b6是旧祖先，不需fetch/reset/checkout或等待新base批准；技术组合保留S1三项XLSX和全部semantic依赖。**旧c3eb D0 66文件及其23包设计全部冻结。** 此文只给出可逐项实施审查的前向新版本方案；没有创建v3 schema/profile/lock/consumer，没有新指定Pass。

## 1. 版本与范围

拟新规范目录为 `docs/iterations/T03/i05-semantic-build-protocol-v3/`，实际新建/采用须root另明确路径与owner。拟protocol/consumer版本 **3.0.0**，profile format=`i05-semantic-build-protocol-profile/4`、profileId=`i05-source-package-parity-v3`；四schema的新format/ID如下。新解析器只对当次已批版本严格校验，不能为兼容静默接受旧profile+新锁，历史v2原件仍只在其历史批准scope中使用。

| schema原文件名保持                     | 拟新format                        | 拟新ID                                          |
| -------------------------------------- | --------------------------------- | ----------------------------------------------- |
| build-provenance.schema.json           | i05-source-package-parity-build/3 | urn:ontolearn:i05:source-package-parity-build:3 |
| build-receipt.schema.json              | i05-build-receipt/3               | urn:ontolearn:i05:build-receipt:3               |
| runtime-validation-receipt.schema.json | i05-runtime-validation-receipt/3  | urn:ontolearn:i05:runtime-validation-receipt:3  |
| runtime-header.schema.json             | i05-semantic-runtime-header/2     | urn:ontolearn:i05:runtime-header:2              |

拟v3只处理完整lock从23到26及其精确来源采用，不把runtime/source计数混改。**26=workspace/dev/build/全部platform锁package记录；23=actual/frozen canonical modules；22=source header supplier声明；8=专用semantic runtime distributions；33=23+4resources+2assets+4writers。** bootstrap与pyshacl.validator仍独列，四functions/checker域、collection计数/预算不变。

## 2. 逐包来源与差异裁定

`union-source-audit.json` 对全部26包逐项保两固定lock的originRef/path、version、原blockSHA、全部artifact URL/bytes/SHA及许可缺证；`dependency-plan.json` 完整无损保18/23/21三份lock原文分块，不省marker/extra或全平台wheel/sdist。

- 18共有包没有版本冲突或artifact identity冲突；这只是固定文本事实，不是resolver兼容/真实安装证据。
- 原block有三种差异：ontolearn-engine需要把dependencies/metadata.requires-dist合成六精确项；rdflib必须保profile的optional html→html5rdf（S1原block没有这一段，不能选S1覆盖）；setuptools仅尾空行差异。其他共有block同原bytes。拟选profile原block为共有/semantic基准、mapping原block为三XLSX新增来源，仅engine六项metadata由后续真实锁生成/核验，不在本票手拼锁。
- 新三项defusedxml0.7.1、et-xmlfile2.0.0、openpyxl3.1.5取0ad/303/3c同字节锁；openpyxl→et-xmlfile边保留。所有包许可在lock文本中无完整实际原件；逐项licenseApproved=null，不能从package名、上传时间或artifacthash推许可。实际artifact/METADATA/RECORD/原LICENSE/NOTICE/COPYING、分类/义务/费用须在授权E0补证；本票不读installed或原件archive。
- pyinstaller hooks、setuptools、OS markers和所有wheel/sdist继续完整保留，union设计不升级任何版本。若后续resolver输出任何版本、artifact、marker、extra或hash新差异，按实际首错/delta逐包明列并root重收，不能把目前“无版本冲突”推广为未来无风险。

## 3. 完整 schema 与字段职责 delta

机器可读 `forward-schema-change-index.json` 是从固定四schema/完整1241索引静态递归得出的 **每个待改literal的精确JSON pointer**；是change-list，不是已经生成的新schema。落地时：

1. 四schema均独立完整生成新文件，更新其$id、format const、顶层profileId const至v3。runtime receipt中完整嵌入headerPayload的format/profileId const也须同步header/2；不能只改独立header schema而漏receipt内重复子树。所有变更位置由change-index列全。
2. 其余全部properties/required/additionalProperties/type/null/enum/oneOf/anyOf/$defs和本地$ref逐字同固定c3eb，完整1241 property pointer集合、required标记与type形状不变。本轮不增加宽泛additionalProperties，也不把distributions.maxItems从8盲改26；版本/const变化后不能引用旧schema原hash。title/comment须真实描述v3前向依赖delta，不能仍声称仅D0原设计。
3. field-responsibility拟format升级`i05-d0-field-responsibility/4`、normativeCrossFieldRules指新3.0.0全文；actors/责任/18exact codes保持同义。重新从完整四schema生成全1241 propertyIndex，shape.const仅change-index所列值升级。完整唯一/全集/required/shape重新独立核验，不能以“旧1241通过”代v3通过。
4. CR-S新增精确dependency规范：新dependencyRef绑定合并六直接依赖pyproject+完整26package锁；各包唯一标准名/version、全artifact/hash/size、markers/extras/workspace/tooling按新批准profile闭包；rdflib[html]边保留。旧文中“完整23包锁”只在新全文改为26并明确不同维度。其它CR-S来源23/22、functions4、resources4/assets2/writers4、33 paths及原引用闭包全部保留。
5. CR-A1/A2/C/A3/A4/R/H继续完整，不因锁扩展弱化路径/actual证据/CodeType/失败/收据无环或caller信任。必须全文移入新规范并审，不用本delta表替代旧全文。实际锁selected artifacts仍按真实OS选择；全平台源表仍保完整。

## 4. descriptor、manifest、consumer mapping delta

| 对象                                     | 拟精确delta                                                                                                                                                                                                                                                                                                      | 必须保留 / 未完成身份                                                                                                                                                                                                                                    |
| ---------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 新profile完整descriptor                  | format/4、id=v3、protocolVersion3.0.0；schemaIds新四ID；contractPaths仍指新同目录完整文档。新增明确`lockPackageCount=26`、`lockPackageVersions`完整26名版本表、`dependencyDirectRequirements`六项、`semanticRuntimeDistributionCount=8`、`sourceDeclaredSupplierCount=22`、`canonicalModuleCount=23`，防计数混淆 | 原canonical22、四resource、两asset、exactargv/collections/exclusions/function/path/code域全部保持；第23历史祖先仍标ancestor，approvedConsumerPin/DependencyPin/Composition/Toolchain等在实际候选产生并owner/root接收前null，executionAuthorization=false |
| 新source/dependency/wrapper/工具manifest | 输入pyproject/lock的两账同新真实dependencyRef/bytes/SHA/blob；wrapper/entrypoint采用新真实wrapperRef；descriptor/schema/sourcechecker工具新真实pins在被依赖前先commit/审。最终manifest依实际new文件完整列原bytes，不预填未来自身hash/processref                                                                  | 23+4+2+4仍33distinctsource；profile/schema/工具作为附加元数据，不混增canonical；旧final-manifest与D0旧66不改、不被新manifest虚称新批准                                                                                                                   |
| D2 consumer严格映射                      | format/profile/四schemaID pin升级，只接新批准26lock/descriptor；source declared22、actual23；frozen声明新23与consumer新pin；完整header/2及receipt映射同版。dependency身份输出实际新lockSHA；invalid旧format/newlock混搭拒绝                                                                                      | 原new-code祖先2cf不能冒新pin，consumer不能自hash/自签approve；actualSource/frozennull、Python域与失败原观察保留；新增26不产生26loader条目                                                                                                                |
| caller/root批准入口                      | 精确钉新schema/profile/consumer/lock/wrapper/collector/newcomposition及实际buildreceipt；header/2→receipt/3嵌入schema映射同步、原raw核同；旧v2approval/指定Pass对新组合无效                                                                                                                                      | 原prelaunch可信来源与postlaunchraw/失败/observedPaths完整核验；真签名机制仍由root单独确定，不拿新version字符串当批准                                                                                                                                     |
| 许可/依赖证据                            | 若专用semantic8包闭包保持不收XLSX库，则XLSX仅完整26锁来源不冒已安装/已打包；单独目标仍按八runtime和实际buildTools实证                                                                                                                                                                                            | parent包含S1/XLSX时须独立parent完整依赖/目录/许可profile与root批准范围，不用本semantic8项schema掩盖额外runtime。其scope/是否需单独11runtime schema由parent专票明示，未决则parent全包门保持待验                                                           |

## 5. 新增 build 输入与 guard

source33账本中的pyproject/lock两项必须在inputs和四writers两账同步新身份；D2新第23、wrapper/entrypoint也由真实候选供pin，前后clean核实际原bytes。新descriptor/schema/collector/runtime-witness工具源作为附加已批元数据输入，不算进33，不能漏保。

root正式parent组合还须为S1新增mapping包四个源码建立精确guard输入：`mapping/{__init__.py,plan.py,probe.py,source.py}`。原0ad固定bytes/SHA/blob已静态列union-source-audit并列入81条输入manifest；这里只核原bytes，没import/运行。它们是parent build输入候选，**不是新semantic canonical23新增模块**，不得因此把新profile隐藏导入或source声明扩成27/26。完整旧43→新33关系为共享22（13相同、9冲突=2依赖+7源资源）、old-only21/new-only11；并集54加mapping4为拟parent/default58。逐项原ref/bytes/SHA/owner/三scope采用见guard-scope-matrix.json；7源资源冲突为CONTRACT python与v2 errors/registry/schema及engine resources/semantic/semantic_execution，不能只改两依赖。历史a4d独立root保旧43+两writer45 guard及原无参build/83项旧profileflag；新parent58逐owner兼容迁移供实际pin，新semantic仍33。旧profile入口/83报告/限额/非claims的必要回归和未批门见guard-migration-strategy.md，不能删guard或永久拒旧flag称兼容。

新依赖artifact三项需真实selected/all-platform身份与实际安装/许可证据，不能只给一个requirements字符串；新root审批记录/原件根由后继资源门明确。任何新增输入（如parent另有运行时data或toolchain布置）只有获准精确source清单/用途后加入，不能wholepackage discovery扩写。

新增三scope guard/profile关联字段须在新descriptor明确guardVersion、scope、sourceGuardPaths、guardManifest身份与入口/owner采用状态，未来真实pin=null；这是拟定新profile元数据，不在本票生成新schema或扩大23/22模块。parent58有独立parent完整profile/许可及批准，不能混进专用semantic provenance33或借其8distribution证明wholeparent。源路径数、26lockpackages和实际23canonical/声明22分别核对。

## 6. 验收与独立审查

首审F1指出旧43迁移缺7源资源冲突；本修订另核全43字面与Git、58 scope矩阵和9冲突/旧入口责任，只申请原fresh reviewer独立delta，原NEEDS_CHANGE不覆盖。本文同时保静态26表/来源和新版本delta完整性要求；既有D0作者check、fresh review和指定模型Pass均不继承。后继完整新规范与consumer/四writer候选实际产出后：逐字核全schema/descriptor、全1241索引、26锁各package源/artifact/marker/extra与六直接项、23/22/8/33计数不混改、全部source/consumer/receipt映射及negative cases。fresh独立agent完整读回并保首报告，原T03/root按实际候选接收；若产品/配置/依赖变化，指定双方全新审查与真实OS/CI等原门另做。

新协议格式本身不是运行授权；本票停在方案和静态检查。resolver/安装/环境probe/build/archive解码/sourcecompile/get_code/native/417/B1/S1/parent/GUI/外审均未执行，不能出运行Pass或预填实际pin。
