# D1 精确方案 fresh 独立审查

结论：**NEEDS_CHANGE（纯方案）**。26包组合来源、完整四schema/1241字段关系和新版本delta的主要设计成立，但“保旧43 guard/默认功能并采用新33 source”的实施方案漏列7项同路径不同字节冲突。加上已承认的pyproject/lock两项，至少9项旧guard需要具体迁移/作用域与owner采用处置。另有1项P3 literal排版问题。当前没有实施或运行批准，不能标D1精确方案已完整接收。

## 固定候选与审查范围

- 实际树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-i05-semantic-offer-owner-review`；分支 `docs/T03-i05-semantic-offer-owner-review`；base `c3eb0694daad26527cc3a1eb0127ed5033f2be25`；实际candidate `ae28572c91b78933c35996f0d80e81c03b96edf0`。入口HEAD/分支相符、index空、唯一tracked dirty为受保护AGENTS。
- 全部15文件 current=固定candidate Git=manifest原bytes。14payload349852B +4553B manifest=354405B；manifest SHA `21a7b0a5f39d6673613a6f30f83797471382a70db3444b3775e2f5e698df8e0c`；base→candidate精确只有这15路径。旧D0 66、offer47/adoption12、产品/四writer/锁/tests/CI未被本candidate改动。
- 当前AGENTS全文读：15147B/SHA `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`。全文读D0 protocol/consumer/profile及根有限收件；四schema与field责任全JSON递归读取核1241 property/required/type/const/enum/ref，并核新方案完整source/header/receipt列表。不是另跑完整JSONSchema引擎，也不冒实际loader/业务验证。
- 全部新Markdown已全文读完。较长组合输出发生截断后，从held连续片段及原protocol有限前缀补齐；没有把未显示尾部当已读。大段重复lock/artifact/固定schema通过完整JSON解析、原Git逐byte/hash、无损重构和全字段关系核查，不声称重新逐行语义审计全部既有供应产品源码或8MiB业务资产。
- 未参加作者工作；本人只写这3件新独审文档，不改15件候选、旧66/AGENTS，不stage/commit，不借caller/native计量票。原方案的future pins保持null和未运行边界有效。

## F1 · P2：完整guard迁移缺7项共享source/resource冲突

位置：implementation-plan.md 55–59、68行；forward-protocol-delta.md 49–51行；verification-matrix.md D1-I03。

方案明确“旧默认/profile路径、43 guard保持已收意义”，并具体把联合依赖带来的guard变化归为pyproject/lock两项；新专用分支又须采用6891固定canonical/resources并有33 distinct source输入。独立从a4d实际wrapper的fixedInputs静态解析出完整43项，与D0新23 canonical+4resources+2assets作同path比较，20项共享中另有以下7项hash/bytes冲突：

| 相同checkout路径                                             | 旧a4d guard bytes / SHA256                                                  | 新6891输入 bytes / SHA256                                                   | 原维护者                      |
| ------------------------------------------------------------ | --------------------------------------------------------------------------- | --------------------------------------------------------------------------- | ----------------------------- |
| `packages/contracts/python/contract_v2.py`                   | 20174 / `0dc96a67cc47a03843a783cc47e649f13d5b5b80a43d520d0f6963b408d274fe`  | 34608 / `17aa68bc2271b45ffb70a023b9db9e441bb1b4e79fc9a42bb6932f60631be7b7`  | T01                           |
| `packages/contracts/v2/errors.json`                          | 14400 / `6986be7cb6742fe955f6ad55b5f1c8565ead3b8b27b80ddfbcdd593187e181f1`  | 16299 / `ad242d93ced7a0c8a463b708b7a1f3105e65f03c3980e0a0c6c4309f8c26544c`  | T01                           |
| `packages/contracts/v2/registry.json`                        | 13039 / `59bfb09bbb142f56ff07e759e0d964d5910fa861c6a16edcf5cfa5e47f920efb`  | 15962 / `1f2e298209e238433c02864a05c70b24482e4c1fd00e7309f63eac84a1f3706b`  | T01                           |
| `packages/contracts/v2/schema.json`                          | 122889 / `9215266523f539c81282bbc96ca88de52b79c99ef39f7696b3a49c58fa7a2b79` | 207256 / `e913138e6f3ac632268ae7f8c2461577022e8298d1c03e0668416a0d654eaabf` | T01                           |
| `packages/engine/src/ontolearn_engine/resources.py`          | 2927 / `2361c55da7983e46fbdd08e50fc3ec48b281d2c76d0021f82fd94ab50ca54274`   | 3065 / `177f57db2c3e768b9fc17d0c9e0665677e6aab55c16003ac7f304254c10d2238`   | original I05/T05 source owner |
| `packages/engine/src/ontolearn_engine/semantic.py`           | 52609 / `5a3a53fc79928a7aa7de280a8477541db4053ec9b2bec489bf28a2ad4e935549`  | 65749 / `60008130fe0db368ea87948c2c8f079b1161f2aa951693b69635558ed1f56a07`  | original I05/T05 source owner |
| `packages/engine/src/ontolearn_engine/semantic_execution.py` | 32917 / `cc701dba39cdeb7f2ae281dfd4a9580b879b9e85f34d3c87a09a3414e7c32731`  | 35220 / `3ac496383349e3ddefea1672c27c88bacaf99f4436c22e96e1592393bac102f3`  | original I05/T05 source owner |

这是固定文本可直接推出的冲突，不是运行所得故障。反例：即使后继把旧43中的pyproject/lock更新为新26包批准pins，采用新的 `resources.py` 3065B后，旧default wrapper仍要求2927B/2361…，会在旧fixedInputs循环抛`ENGINE_BUILD_INPUT_CHANGED`；其余六项同理。若保旧source满足旧guard，新专用33输入则不符合新批准6891 bytes，二者不能靠同一path两个版本同时满足。只把旧43保在旧分支而让default无法运行，也不能未经明确决策就算保留旧行为。

方案虽泛称“新旧T01资源不能互换”“建立新guard表”，还没有列完整43→新33/parent的逐项映射、这些source/resource冲突的具体owner采用、旧profile/default对应输入作用域或新版guard/旧flag行为处置，因此缺少用户要求的**精确最小实施方案**。这不是要求现在修改7个共享源码或四writer，更不授权删除guard/收集glob/把旧profile报告当新组合通过。

关闭条件：新方案给完整43项旧guard逐项身份及其在新semantic/parent/default各scope的保留、更新、隔离或不适用理由；明确已知2依赖+7源资源共9个冲突，保留全部旧来源责任，分别由T03/T01/I05等真实owner/root精确采用。为default/profile旧flag保留定义可检验的真实行为和相应输入/guard版本，若需分离历史构建说明明确入口/根/新批准路径，不能静默把旧功能变成永远拒绝。新增mapping4 source及新consumer/四writer也列完整guard账；所有未来pin未实际形成仍null。同步正文/机器清单/forwarddelta/验收矩阵，再由固定新candidate作必要独立delta；不运行build或产品来关闭本静态缺口。

## F2 · P3：运行验收矩阵丢失真实代码属性literal

位置：verification-matrix.md 54行R2，实际文字为`函数.**code**`，没有真实属性名`function.__code__`。D0 protocol/consumer明确要求实际函数的`__code__`对象，上一D0关闭的F3也正是literal问题。这里主要为Markdown排版错误，完整D0合同仍优先，未发现新schema弱化；但作为交给后继实现者的精确验收矩阵应修为反引号中的`function.__code__`或对应真实函数属性，并保same canonical object/exact CodeType/co_consts/domain完整要求。不能改成name反射或sourceSHA。

## 已独立核实的成立部分

1. 三份完整lock文本分别无损重构并逐byte等原Git：5f18包20999B、profile23包28440B、mapping21包23393B；每个package block原bytes/SHA单独核同。两固定lock并集26包、共有18包，没有版本冲突；143个artifact来源行从原TOML文本独立提取URL/SHA/size并与union表逐项全同，共有包artifact列表相同。exact block差异确为ontolearn-engine metadata、rdflib html optional、setuptools末尾空行；不能因此宣称resolver兼容/installed/license已验证。
2. 原D0四schema完整JSON、责任索引唯一全集1241=669+56+366+150，property required与type/const/enum/$ref全部核同；3个local refs逐字识别。新change-index14 schema literal及10责任const的old指针值都与固定原件相符；内嵌header版本/ID并未漏掉。新v3/profile4/header2/receipt3是proposal，实际新文件/pins不存在，不继承D0或指定Pass。
3. 新source/interface的22供源、23祖先、4resources、2assets、function bindings、全部collection/exclusion/argv、18header required及build/runtime/run required列表与D0原件完全相同。26锁包、23实际canonical、22source声明、8专用semantic distributions、33distinctsource分维度正确。第23旧2cf只能祖先，新D2 selfpin外批且null；bootstrap/pyshacl.validator独列，frozen actualSource/observedSource23=null，没有造源观察。
4. strict JSON、所有required/unknown/null/bool-int/重复键/前置exit2与未知exit1、实际partial/false/null/坏Python/ref/digest、observedPaths、header原raw→payload→run映射和immutable后出收据均保D0含义。SHA不冒签名，root信任入口/新mode/consumer签名/collector身份留后继明确；caller不从bundle locator自找批准，probe不读包外witness/许可/安装路径。D2/caller/T01/原tests/CI未被方案自动夺权。
5. 原12S1 SQLite HOLD、wholeH、B1/417完整源包parent scope、目标两OS/GUI/ABI/loader/drain/原57P0/真人/指定双审/CI/develop等门没有被方案关闭。未执行的全部资源/平台/性能如实待验，不把静态设计当runtime。

## 实时政策快照漂移（记录项，不作为产品失败）

81条输入原件身份核查中80条匹配；唯一当前文件漂移为仓库外desktop-operation-policy-20261022.md。作者snapshot3172B/SHA `7b54d589d39bfe71c0f67d61c00995bb4d60b5156a74a6ae25ac69a2f491f5eb`，本独审当前3160B/SHA `2032bd9e1cdbf398a0d505e092e1a08b80ff15df26b1d06c7d7e1c2e0a5a8ec1`。本人全文读当前政策：T06已释放前台，短时创建lease按execution-state，后台推理不独占整个应用；静态/native具体运行界限保留。

这是live操作政策在作者封存后的变化，不是15文件candidate损坏、不改变正式批准base5f，也不要求无变化产品重测/新Goal。不要重写旧manifest假装“81当前仍匹配”；owner/root后续过程/派发附最新政策身份即可。正式远端5f来自控制方实际ls-remote归属；本独审未联网复验。localdevelop1b6为旧I01祖先，不申请新base批准。

作者39个/tmp静态scratch越界写入偏差在author-checks/交付完整保留；本独审按其39个精确路径核当前全部不存在。不能据此追认原越界合法，但没有发现现存scratch、执行其内容或产品污染的证据；本人没有为审查新写scratch。

## 实际检查、未验边界与交付

实际仅普通文件/Git读取、JSON/hash/re/字面静态关系、本人3件文档格式检查。固定15身份/来源/锁/字段/guard冲突检查是本独审新执行，不借作者Pass。没有JSONSchema引擎、resolver/install、import/sourcecompile/pycompile、产品/reader/helper函数、fixture/模拟、build/native/archive decode/installed/license/binary/witness/identity/SDK、网络/GUI或指定外部模型任务；没有stage/commit/push/PR/merge。

F1/F2保持OPEN，先由原T03全文读本报告并封存，再修方案为新actual candidate后独立delta。当前结论只限D1精确方案未完整，既不否认已核静态事实，也不授权任何实现/依赖锁/运行。最终报告与checks的原bytes/SHA由independent-seal.json及外报seal身份固定；封存后停写。
