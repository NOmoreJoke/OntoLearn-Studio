# I05 独立语义打包 profile 静态草案

2026-10-22。此件是交给原 T03 四 writer 维护者的可审 offer，**尚未由 T03 接收、尚未实施、构建或运行**。只写本文件和 `docs/reviews/I05/semantic-build-offer-draft/`。T03 当前 native D/N 修复保持原写锁、meter HOLD、原路径/候选/计量票；暂不请求其读取或新票。本草案不能借用该票。原57P0、C–G、PRD10–12、六迭代、SQLite损坏输入HOLD/whole-H/owner、指定同版双模型/CI/Windows及macOS/真人/develop与远端门不变。

## 1. 固定来源、采用状态与当前缺口

本树 `.worktrees/I05-semantic-build-offer-draft`，分支 `docs/I05-semantic-build-offer-draft`；base=`5f910b52c69d86a1076b2032e5d3c63e715947f3`。AGENTS为保护未暂存M，15852B／`78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`，不stage。

| 固定依据                                                                                                     | 用途/权属/接收边界                                                                                                                                                        |
| ------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 合同 `ee2b30a2dad35b2d395f9c735aff80371ab41110`                                                              | 主合同与命名reviews附件：22模块/128静态边、43guard30同13异、全输入/资源/许可/测量。合同已限定接收；首Fail与delta Pass保留，均非运行                                       |
| supplier `6891a5842302859a531cf82767c5a482417bc274`，过程 `f79a29f596b2444cba542a906c91727869014886`         | 22canonical模块不可变供应；原I05/T05维护权不转移，不扩整树/quality/worker/Store                                                                                           |
| T01 candidate `dd972b79adf4d378636a7d41a6b0e3e08c0d5ca1`，过程 `79d63cc1f403ee857a3af2a98f8870db9a6a910d`    | 四件6891公共资源已限私有只读采用；不是公共执行/依赖/打包/未来维护授权                                                                                                     |
| I05 R2 candidate `2cf0c3328de464e15a3fa9cdbfdf6aa88d0b4a64`，过程 `61f53dbe76262f5003065900a4e97d9a6130014b` | 新probe/资产/测试静态接口依据；root本轮已全文R1/R2和限定source-only收件，见inputs保全的`I05-source-package-source-only-root-closure.md.raw`。不等于运行/包/指定双外审通过 |
| 旧T03 offer `4fa5d62eb13269351384527b1f84761c08811e79`                                                       | 仅四writer/依赖/所有权历史设计证据；旧7quality/17canonical/83probe不代表新组合                                                                                            |

[source-manifest.json](../../reviews/I05/semantic-build-offer-draft/source-manifest.json)逐命名ref/path/blob/bytes/SHA，[input-identities.json](../../reviews/I05/semantic-build-offer-draft/input-identities.json)给采用角色。raw只供静态核对，不能作为业务输入或oracle。

实查两个独立前置：2cf frozen在`check_runtime_preconditions`明确抛`FROZEN_BUILD_PROVENANCE_UNAVAILABLE`；source树仍5f锁20999B／`d5d027da6628a2f4fc2e73730ce3a5e40d85aebba95188b0d4c3801ebdde949e`，pyproject351B／`626b8f7024e8460af3ca42076a953b2827c0d6468903065c71a7fbb819cbce20`，不是其常量要求的6891锁。source-only封存未偷改T03依赖，也不能直接声称checkout具备运行组合。初次静态collector错误假定两锁同一而AssertionError，已保全并改为双身份记录；未执行业务。

## 2. T03四writer逐路径后继请求

唯一维护者仍T03，当前四件零修改。只有T03当前写锁释放、原会话明确接收本草案固定candidate、root另定实施/资源窗之后才施工。依赖提交和包装提交分别冻结，不与I05业务修复混为一项。

| writer                           | 5f/2cf bytes与SHA                                                         | 6891比较bytes与SHA                                                        | 最小后继delta                                                                                                                                                                                                                                   |
| -------------------------------- | ------------------------------------------------------------------------- | ------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `packages/engine/pyproject.toml` | 351／`626b8f7024e8460af3ca42076a953b2827c0d6468903065c71a7fbb819cbce20`   | 398／`bcc8825b1f2902a66ae539e687df57e5b2554247f48a48a65215601a77958365`   | 保rdflib7.6.0，新增direct pyshacl0.30.1/pyparsing3.3.3；保engine0.1.0/Python范围/build-system。6891字节只提议，T03审实际patch                                                                                                                   |
| `uv.lock`                        | 20999／`d5d027da6628a2f4fc2e73730ce3a5e40d85aebba95188b0d4c3801ebdde949e` | 28440／`86dfe82d952e2c88edcfc5658f488f6e1f0d04b4ec3b1e6f5c5d3bc4f57e8b73` | 唯一完整锁；先审23包提议、extra/markers/完整各平台wheel/sdist，不复制旧环境/整C4或XLSX锁、不造第二锁。实际解析差异先报delta                                                                                                                     |
| `scripts/build-engine.mjs`       | 1234／`2a9036fd76ed32f8df52d7ffa7afee2213c00008986269cd2d1cf66f1857aa81`  | 13264／`5dab9850ba97e3c5e916ac45386a05f540c671f342f5ebf5c911ccc5e4772894` | 保parent原构建；加exact `--i05-source-package-parity` profile，target新probe/name=`ontolearn-semantic-parity`/onedir/optimize0/隔离输出。明列33源guard及额外元数据、外部archive/code/provenance生成；不搬旧inventory脚本，不接受任意target/path |
| `packages/engine/entrypoint.py`  | 787／`979b65e5efc3d19ad9851cc2a97255594591626fbed2efbecd8713723e9f2f60`   | 1232／`9abf0c22943cfae9f6f43893586626027bf9f4fc7318100465c0179aba69fe31`  | parent新flag只接受三exact argv并原样调canonical `main([flag,selector])`；单flag/unknown/extra/`flag=value`以2拒绝且不落default。原storage/worker/contract/resources/default与已批旧flag原义保留；独立profile不target此file                      |

[profile-descriptor.draft.json](../../reviews/I05/semantic-build-offer-draft/profile-descriptor.draft.json)为具体草案，`acceptedCompositionRef=null`、`executionAuthorization=false`。拟输出`build/i05-semantic-parity/{approved-composition-ref}/{platform-id}/`，dist/work/spec/cache/log独立子目录；root须另授唯一前缀/资源票，不能借T03 D/N票。

集成须真实可恢复composition commit：T03 dependency ref→I05消费delta ref→T03包装ref→root/owner批准组合；原supplier/T01/I05 asset refs及逐path实际diff分列，不取任意HEAD或跨树绿拼组合。33受控源及descriptor/工具元数据须构建前后clean且逐实字节核；AGENTS政策M不stage，不允许其他WIP混入。

## 3. 有限闭包、guard与布局

新profile23模块+4资源+2资产+4writer=33不同路径，再加批准profile descriptor、后继消费者、工具/安装/许可等实际元数据。第23probe的后继改动须新pin，不永久借2cf旧hash。

[guard-migration.json](../../reviews/I05/semantic-build-offer-draft/guard-migration.json)完整保43旧guard/旧值/6891值与逐项retain/omit，30同13异。parent原guard不删除或改为假通过；独立profile按有限表重建，不能仅换semantic hash或slice旧17。22supplier/128边为静态可达依据，不自证实际archive。quality保父包+7rule子模块，精确解除旧rule_revalidation exclude；definitions/planning仍排除且不得触发父懒导出。不collect整engine/quality，不引worker/Store/Job/旧probe/semantic_samples/storage_probe/`__main__`/protocol。

### 3.1 精确23 canonical模块

前22固定6891；第23固定2cf作为后继delta基线。完整path/ref/blob另见JSON。

| module / source path                                                                                                           |     B | SHA256                                                             |
| ------------------------------------------------------------------------------------------------------------------------------ | ----: | ------------------------------------------------------------------ |
| `ontolearn_engine` / `packages/engine/src/ontolearn_engine/__init__.py`                                                        |   101 | `4b8460a6ccc649f44188171c3d4c0c9e58e1204c711462d9ecf0aff12135684f` |
| `ontolearn_engine.quality` / `packages/engine/src/ontolearn_engine/quality/__init__.py`                                        |   548 | `9a5130c2fdbe376e5e4c15e68085f01724847ff13e9b2c195cf270e476806d9c` |
| `ontolearn_engine.quality.rule_calendar` / `packages/engine/src/ontolearn_engine/quality/rule_calendar.py`                     |  4047 | `6a2e43b029f7069e398f696ff19948d9e806f06fecd9a1e239b889a55e528aec` |
| `ontolearn_engine.quality.rule_comparator` / `packages/engine/src/ontolearn_engine/quality/rule_comparator.py`                 |  1750 | `9a495876a182d1cad4cac86bb4651c1627e4afc37e1bf9bb3d62be6bb0e95ff2` |
| `ontolearn_engine.quality.rule_firing` / `packages/engine/src/ontolearn_engine/quality/rule_firing.py`                         | 19149 | `5116aa3e96ae10e7f37eb7afddceef50879869d38af116f9c794437edf49243c` |
| `ontolearn_engine.quality.rule_numbers` / `packages/engine/src/ontolearn_engine/quality/rule_numbers.py`                       |  7372 | `6b080a55bd8f4af1a1120b55448e02a1a442c231a32ab575ce6e82de054164f9` |
| `ontolearn_engine.quality.rule_profile` / `packages/engine/src/ontolearn_engine/quality/rule_profile.py`                       | 11987 | `b40b73f65f474cda32ac42caeeb837ad6470a7daeeba9013d8f69e7f0c5a261c` |
| `ontolearn_engine.quality.rule_revalidation` / `packages/engine/src/ontolearn_engine/quality/rule_revalidation.py`             |  6288 | `9e9258cfefdef56f369dad6bb7838afd22478ea6714e4322b2d872d12616200e` |
| `ontolearn_engine.quality.rule_terms` / `packages/engine/src/ontolearn_engine/quality/rule_terms.py`                           |  6176 | `218c4790e9b35236e393407b5b4e0207890d46fe3ea48a9a69e26aa08ddba1d1` |
| `ontolearn_engine.resources` / `packages/engine/src/ontolearn_engine/resources.py`                                             |  3065 | `177f57db2c3e768b9fc17d0c9e0665677e6aab55c16003ac7f304254c10d2238` |
| `ontolearn_engine.semantic` / `packages/engine/src/ontolearn_engine/semantic.py`                                               | 65749 | `60008130fe0db368ea87948c2c8f079b1161f2aa951693b69635558ed1f56a07` |
| `ontolearn_engine.semantic_error_adapter` / `packages/engine/src/ontolearn_engine/semantic_error_adapter.py`                   | 15426 | `0572b4730ba1ac28192e84633633d7da222e6603ff7da811c84e1f368eb55014` |
| `ontolearn_engine.semantic_execution` / `packages/engine/src/ontolearn_engine/semantic_execution.py`                           | 35220 | `3ac496383349e3ddefea1672c27c88bacaf99f4436c22e96e1592393bac102f3` |
| `ontolearn_engine.semantic_offline` / `packages/engine/src/ontolearn_engine/semantic_offline.py`                               |  1351 | `4897d9c6a07756d5f8ed4908b4b7a28ca96c67b2670753b74f73e41bf4b67488` |
| `ontolearn_engine.semantic_profile_directsteps` / `packages/engine/src/ontolearn_engine/semantic_profile_directsteps.py`       | 46459 | `7927769077e363b23741f6dc78b7c0ec2ad00b7d3285f8403a190c0e00169b22` |
| `ontolearn_engine.semantic_profile_input` / `packages/engine/src/ontolearn_engine/semantic_profile_input.py`                   | 40378 | `f4d76b68e6bd5f27d4e1c0ee7b26435117b1dd762a4b2a16503d41afd1841f74` |
| `ontolearn_engine.semantic_profile_production` / `packages/engine/src/ontolearn_engine/semantic_profile_production.py`         | 19993 | `5c857470890bd810370ad877db930848ba08e80096c640037d39bea83c14a320` |
| `ontolearn_engine.semantic_profile_restore` / `packages/engine/src/ontolearn_engine/semantic_profile_restore.py`               | 70203 | `1607d2968d2ba76ad0711be446fea7965641fb845226d0e683ac35e5d0f57243` |
| `ontolearn_engine.semantic_profile_restore_budget` / `packages/engine/src/ontolearn_engine/semantic_profile_restore_budget.py` | 37889 | `ffde8fd243696ab4e8812e8994e6a8fc2b5832f411e5fdf1e4c7753fe19c93d0` |
| `ontolearn_engine.semantic_query` / `packages/engine/src/ontolearn_engine/semantic_query.py`                                   |  6448 | `fe8e600de7c0b300038ba0c952497cb8fbbf30f741f1e0d5e1bba78afef8670f` |
| `ontolearn_engine.semantic_scopes` / `packages/engine/src/ontolearn_engine/semantic_scopes.py`                                 | 13051 | `aa8f1231df09332e9f02d96e3c8e4ef4cb64d4b3fa28067babcd3431de820ebf` |
| `ontolearn_engine.semantic_turtle` / `packages/engine/src/ontolearn_engine/semantic_turtle.py`                                 | 33916 | `4180feb9d0c775669b65338e1cfb37a8d5bb7f3ce155b4804dd53a43efad5214` |
| `ontolearn_engine.semantic_source_package_probe` / `packages/engine/src/ontolearn_engine/semantic_source_package_probe.py`     | 93848 | `b3456f021afdbd53ec8677bf317a5ffdff636b55bae760eb8b7fec6e399e41b9` |

### 3.2 四资源与两资产

| source（ref）                                                                                           |       B | SHA256                                                             | `_MEIPASS`内位置                                                               |
| ------------------------------------------------------------------------------------------------------- | ------: | ------------------------------------------------------------------ | ------------------------------------------------------------------------------ |
| `packages/contracts/python/contract_v2.py`（6891a584）                                                  |   34608 | `17aa68bc2271b45ffb70a023b9db9e441bb1b4e79fc9a42bb6932f60631be7b7` | `contracts/python/contract_v2.py`                                              |
| `packages/contracts/v2/schema.json`（6891a584）                                                         |  207256 | `e913138e6f3ac632268ae7f8c2461577022e8298d1c03e0668416a0d654eaabf` | `contracts/v2/schema.json`                                                     |
| `packages/contracts/v2/registry.json`（6891a584）                                                       |   15962 | `1f2e298209e238433c02864a05c70b24482e4c1fd00e7309f63eac84a1f3706b` | `contracts/v2/registry.json`                                                   |
| `packages/contracts/v2/errors.json`（6891a584）                                                         |   16299 | `ad242d93ced7a0c8a463b708b7a1f3105e65f03c3980e0a0c6c4309f8c26544c` | `contracts/v2/errors.json`                                                     |
| `packages/engine/src/ontolearn_engine/probe_inputs/i05-source-package-parity-inputs.json`（2cf0c332）   | 8205267 | `47c66ffe18613eb8cc1af6365dcfc9d866821f22c48f96d9f44725f8f7c59eaa` | `provenance/i05/source-package-parity/i05-source-package-parity-inputs.json`   |
| `packages/engine/src/ontolearn_engine/probe_inputs/i05-source-package-parity-manifest.json`（2cf0c332） |   21202 | `0b91c1a9366d170b5614d94c20006054a5a959be235e0f46cb150cf32335193a` | `provenance/i05/source-package-parity/i05-source-package-parity-manifest.json` |

source两资产只从模块相邻`probe_inputs/`，四资源从checkout`packages/contracts/`、锁从root`uv.lock`。frozen两资产只`_MEIPASS/provenance/i05/source-package-parity/`、资源只`_MEIPASS/contracts/`、锁只`_MEIPASS/provenance/uv.lock`；无cwd/checkout/用户目录/系统Python/网络fallback。

`resources.CONTRACT`仍由原`spec_from_file_location("ontolearn_contract_v2",...)`执行唯一对象；原resources并未把该动态对象注册`sys.modules`。后继核实际resources.CONTRACT、SPEC/name/origin/loader与canonical消费者引用，不另exec/alias、不谎称已有sys.modules注册。允许semantic_identity和普通error目录/`validate("error",value)`；checker顶层只读schema/registry/errors，resources另读registry/lock。禁止直接间接resource_manifest/build_request/execute_request/derive_dependencies/permits_transition；后二者lazy读dependencies/states。不得glob v2或加fixtures/binding-regressions/frame-fixtures；需要新调用先T01/root路径delta。

实际PYZ放代码；onedir `_internal`放runtime/data/dist-info/license，布局草案：

```text
ontolearn-semantic-parity[.exe]
_internal/
  <actual Python runtime/native/PYZ related files>
  contracts/python/contract_v2.py
  contracts/v2/{schema,registry,errors}.json
  provenance/uv.lock
  provenance/i05/source-package-parity/{i05-source-package-parity-inputs,i05-source-package-parity-manifest}.json
  provenance/i05/source-package-parity-build.json  # archive核后外部后置
  <eight actual dist-info dirs with METADATA/RECORD/license files>
  licenses/{distribution}/{original-relative-license-path}
  licenses/runtime/{component}/{original-relative-license-path}
```

23canonical hidden-import逐项，prettytable/wcwidth/packaging另hidden-import；collect-all仅rdflib/pyshacl/owlrl/html5rdf，八dist逐copy-metadata。不collect-data/collect-all/collect-submodules ontolearn_engine，不整目录add contracts/v2。target bootstrap与canonical probe可能各在CArchive/PYZ有代码副本，archive见证分别列项；bootstrap仅最早main guard转canonical main，不在`__main__`发行类；唯一canonical模块对象才发行类型。

### 3.3 依赖与许可责任

[lock-distributions.json](../../reviews/I05/semantic-build-offer-draft/lock-distributions.json)静态保6891 pyproject、整23包、workspace/dev/tool顶层、所有wheel/sdist URL/size/hash与8runtime记录；不安装、不推定实际许可证。不能只留宿主wheel。

| distribution | 固定lock版本/边                                    | T03后继收集责任                                                        |
| ------------ | -------------------------------------------------- | ---------------------------------------------------------------------- |
| rdflib       | 7.6.0→pyparsing；html extra→html5rdf               | plugins/data/code/metadata/RECORD/实际许可                             |
| pyshacl      | 0.30.1→owlrl、packaging、prettytable、rdflib[html] | code/内置资源/metadata/许可；I05核真实Validator.run                    |
| pyparsing    | 3.3.3，direct                                      | code/metadata/许可，不因5f同版本继承                                   |
| owlrl        | 7.6.2→rdflib                                       | code/data/metadata/许可；收集不授full OWL-RL能力                       |
| prettytable  | 3.18.0→wcwidth                                     | 真实imports/metadata/许可                                              |
| wcwidth      | 0.9.2                                              | 实际pure/native平台artifact/marker/data/metadata/许可，宿主不代Windows |
| html5rdf     | 1.2.1，来自html extra                              | code/data/metadata/许可，不能漏extra                                   |
| packaging    | 26.3                                               | runtime code/metadata/许可，不以旧锁相同替实际身份                     |

T03逐dist核actual selected artifact→installed RECORD/files→最终目录/PYZ code/data/metadata/LICENSE/NOTICE/COPYING原字节；每file列hash/角色/最终映射或owner审过的非runtime遗漏原因。METADATA实际Requires-Dist/marker/extra完整。build-only不必全装runtime，但artifact/metadata/使用许可须证据化。锁提议PyInstaller6.22.3不等于已安装工具/bootloader；Python/stdlib/PyInstaller bootloader/动态库/平台runtime独立source artifact→bundle file→license/notice责任表。仅basename扫描或License字符串不足；runtime必需映射缺失记unknown，不能生成accepted build provenance。旧C4/S1库版本、包体/许可/峰值不继承，本草案无性能数。

## 4. 外部build provenance协议草案

[build-provenance.schema.json](../../reviews/I05/semantic-build-offer-draft/build-provenance.schema.json)及[final-build-receipt.schema.json](../../reviews/I05/semantic-build-offer-draft/final-build-receipt.schema.json)均仅JSON Schema2020-12**草案，无现行采用**，没有实际build实例或PYZ hash。schema结构加以下跨字段约束共同生效；schema不是builder/签名/owner接收/真实archive证据。

### 4.1 外部生产与自引用断开

1. root冻结真实composition commit，含批准T03 dependency/wrappers、I05消费delta、23模块/4资源/2资产/descriptor。descriptor是Git输入祖先，被外部provenance引用。probe/source身份由外部批准组合pin；probe不能嵌含自己hash的descriptor/provenance hash。2cf记祖先，后继源码另ref。
2. T03核33输入与工具元数据前后身份/clean、实际Python/环境/argv/installed映射后构建onedir，**此时不把最终provenance放进PYZ/CArchive**。必须实际有canonical probe PYZ项和bootstrap CArchive脚本；缺get_code或canonical项不以bootstrap代替。
3. T03外部固定逻辑读取新实际archive，保存完整TOC/member原bytes/hash，以构建解释器compile批准source bytes（不exec/import）得expected code，与实际archive解码code同域指纹比较。23模块/bootstrap/dynamic checker/四函数均映射；提取器/normalizer自身绑定T03包装ref/path/hash/工具版本。必需文件/许可/code有unknown不生成accepted状态。
4. archive见证完整后，生成普通文件`_internal/provenance/i05/source-package-parity-build.json`，不重建archive、不写自己hash。payloadFiles列`_MEIPASS`内其他所有文件并明确排除此件；可记已固定archive/executable hash，不写包含自己字节的目录hash。新消费读取cap提议16MiB+1；完整映射超限提交版本delta，不截断/悄增；逻辑cap非物理许可。
5. 包外collector生成final目录逐file manifest（含exe和全部_internal/provenance），包外receipt再绑定manifest、embedded provenance、archive witness、approved profile/composition。两外部文件均不进入被hash目录、不hash自身。过程commit只包含既有收据，不预填自身未来commit。签名/安装改字节须新receipt并保原件。

证据有向图：既有source commits→build输入→实际archive/code见证→后置provenance→全目录manifest→包外receipt→过程commit；不反指后项hash。caller先按批准receipt核最终目录与provenance，再启动获准进程。只靠包内自报不能证明可信build。

path域：source相对Git根；archives/member archivePath相对final bundle root；payloadFiles相对_MEIPASS（排唯一provenance）；runtime resource/data mappings相对_MEIPASS；final receipt directoryFiles相对final bundle root（含_internal前缀）；包外manifest/log相对批准证据前缀。拒绝绝对路径、`..`、反斜杠、重复名、symlink逃逸；原始日志cwd可另保，不能当开放locator。

### 4.2 与2cf实际loader/fingerprint逐字段对应

| 2cf当前源码事实                                                                                                                 | 草案绑定/后继比较                                                                                                                                                                                                                                                                                                            |
| ------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `_code_fingerprint`对exact CodeType递归co_consts内code，仅replace co_filename=`<i05-canonical-code>`                            | algorithm=`i05-code-object-marshal-filename-normalized/1`；保其他所有字段，包括字节码/flags/name/qualname/lineno/linetable/exception table/常量；不另做语义等价归一                                                                                                                                                          |
| marshal.dumps(normalized(code),4)→SHA256                                                                                        | marshal4；原member bytes hash与normalized code hash分别列；sourceSHA只在sourceCompilation.source.sha256，actualArchiveCode指纹必须实际解码，不能sourceSHA预填                                                                                                                                                                |
| 返回algorithm/sha256/pythonCacheTag/domain四字段                                                                                | schema精确四字段；domain保持`actual-loader-code; not source bytes or a build approval`。compile也复用此返回shape只为可比，由sourceCompilation外层声明实际域，不能拿domain字样自证                                                                                                                                            |
| source22项loader.get_code与compile(source,actualpath,"exec",dont_inherit=True,optimize=sys.flags.optimize)比较整fingerprint字典 | builder/运行optimize固定0，实际Python精确patch/build/cacheTag/magic/byteorder/flags核同；source compile/actual archive/actual loader三向对应；第23probe也纳入，不仅自报sourcehash                                                                                                                                            |
| canonical检查name/spec.name/sys.modules[name]同对象，source origin精确                                                          | frozen新增批准loader class/origin布局/code比；精确23名称集合/单一类发行对象，不能只比数量或同名                                                                                                                                                                                                                              |
| functionCode观测reason/query/validate_shacl_text/Validator.run真实__code__                                                      | 外部从批准compile模块co_consts索引路径取expected function code，对actual archive同路径和runtime实际functioncode；Validator.run绑定pyshacl.validator实际source/RECORD/artifact，非版本自报；sourceCompilation.source对此使用installed-distribution-source域，不伪造仓库Git ref。23canonical/bootstrap/checker仍须Git source域 |
| probeWriter读取canonical loader；contract目前仅name/spec/origin                                                                 | 后继probe自身source/loader/PYZ与bootstrap分别核；dynamic checker实际bytes/loadercode另核，始终只用resources.CONTRACT原对象，不另exec或改公共resources                                                                                                                                                                        |

同cacheTag不保证marshal引用/字符串intern/loader缓存、解释器build或PyInstaller转换稳定。跨loader/cache/版本稳定性**未测**；不能通过删字段“修绿”。后继有限code域验证先全23/四函数/checker在同批准解释器/optimization的sourcecompile、实际archive解码、fresh/cold/warm重复get_code逐项实测。若不一致保首错、提交I05/T03算法版本delta、重冻source/见证/consumer/schema并重审。缺CodeType/get_code、unknown或编译域不匹配均拒绝，不降sourceSHA。编译/解码留未来builder窗，本窗未做。

### 4.3 I05最小消费delta（本窗不实施）

I05 owner另窗只改`semantic_source_package_probe.py`及专用test/docs；不改22供应或公共resources/checker/registry。schema若进入runtime须另授精确路径/hash/guard，不因本docs schema存在而自动读取。

| 点位                                     | 后继修改/失败策略                                                                                                                                                                                                                                                                                                                                         |
| ---------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| check_runtime_preconditions frozen总拒绝 | 保resource/lock/dist/Python原前门；唯一bundle locator bounded16MiB+1→严格UTF8/JSON duplicate/nonfinite/BOM拒绝→schema exact/版本→approvedcomposition/23集合/4资源/2资产/lock/Python核对。外部caller先核批准receipt及provenance bytes/hash；caller缺批准receipt不得启动。probe不持批准receipt，不宣称自己验证外部批准，仅核自带provenance/actualcode一致性 |
| _runtime_modules                         | 实际import之后、图业务调用之前核23name/spec/loader/origin/code三向、四function与dynamicchecker；reject alias/unknown/错版。公共checker顶层import已读三JSON，不能声称尚未import任何业务；此门只保证图计算未开始                                                                                                                                            |
| probe pin/header                         | 外部descriptor记录后继probe ref/hash，不在probe嵌自己hash；header分declared supplier/source、actual archive/loader、provenance bytes/hash/composition与有限packageCodeBoundToSource（externalReceiptStatus=external-unverified）。匹配不等于sourcePackageEquivalent/oracle/原操作通过                                                                     |
| T03实际锁变化                            | 原LOCK_BYTES/SHA或dist pin需改变则I05显式delta并审；不能删identity检查迁就5f或假写6891来源                                                                                                                                                                                                                                                                |
| 拒绝测试接口                             | 后继补缺/错版/超cap/duplicate/逃逸、23名字错、sourceSHA伪作code、Python/optimization/cache、模块alias、尾资源/资产、provenance篡改、非法argv等真实边界；本窗不pytest/import/模拟frozen造通过                                                                                                                                                              |

**固定caller/consumer分工**：保三个exact argv，不新增任意路径/环境选择或receipt载体。caller在启动前从root批准的固定证据前缀读包外receipt、核其批准来源/目录/provenance/executable；无批准receipt或任一差异不启动。probe只从唯一bundle路径读provenance并核actualcode，header给provenance digest/composition及`externalReceiptStatus="external-unverified"`，不声称自己见过外部批准。caller将该header digest与已核receipt中embeddedProvenance digest绑定，联合得最终build来源结论。内部`packageCodeBoundToSource`最多`archive-loader-consistent-with-declared-source`，不自签approved。此设计没有receipt自证环，也不要求probe解析自己拿不到的外部文件；如将来必须probe内验证批准receipt，须另提固定可信载体和授权delta。当前2cf无此协议仍前置拒绝，不能当parity通过。

### 4.4 接收schema还必须核的语义约束

refs实际存在/组合ancestor与owner记录相符；33路径唯一且bytes/hash/Gitblob实核；23名字/来源精确集合、四资源/两资产路径精确、lock为T03批准；八dist名称/版本/selectedartifact/marker/extra与整锁及RECORD闭合；所有runtime必需文件与许可有bundle映射，遗漏只限owner审过非runtime/build-only；archive名唯一/TOC完整；23expected编译/实际提取/loader同指纹、bootstrap映射同源；四function索引与runtime对象准确；checker唯一对象；排除模块/额外v2/oracle在archive和目录确无；前后文件稳定；final receipt核完整目录且无循环。任何unknown不生成archive-code-source-bound。该状态只证明构建域，runtimeParity/externalOracle均not-run-by-builder。

## 5. 完整suite与独立oracle

[suite-inventory.json](../../reviews/I05/semantic-build-offer-draft/suite-inventory.json)逐417项保id/family/operation/dataset/parameters/sourceRefs/context/projection SHA与三个有序caseSet，仅读metadata。实际2cf资产320datasets/417observations；full-v1恰全部，两个B1 selector各仅一个对应scale的measurement。不能子集拼full，不能把此metadata当runtime输入或golden。

| full-v1 family           | observations |
| ------------------------ | -----------: |
| `profile-83`             |           83 |
| `consumer-C-query`       |            2 |
| `consumer-C-shape`       |            9 |
| `consumer-C-date`        |            4 |
| `consumer-C-integer`     |            2 |
| `utc-date`               |           76 |
| `turtle`                 |            1 |
| `rdfs`                   |            1 |
| `b1-measurement`         |            2 |
| `readonly-query`         |           25 |
| `turtle-lexical`         |           17 |
| `turtle-rejection`       |            9 |
| `rdfs-finite`            |            7 |
| `legacy-rule`            |            4 |
| `scope`                  |           10 |
| `original-query`         |            2 |
| `original-shape-repair`  |            3 |
| `transfer-shape-repair`  |            2 |
| `dag-fullview`           |           19 |
| `restore-negative`       |           14 |
| `shape-template`         |           19 |
| `integer-policy`         |           39 |
| `shacl-front`            |           31 |
| `utc-date-public-budget` |            2 |
| `utc-date-D1`            |            6 |
| `offline`                |           28 |

完整矩阵保Turtle/query/RDFS/legacy rule/scope、83数学与22扩展/C13各policy变体、真实prepare→producer→capture→restore→roots/fullview/DAG、restore尾child/source/definition/limits及DAGpremise/depth/伪leaf/head1023/15、shape/整数/date/公共预算/D1/严格offline。合法`definition.heads`保留，不能扁平key黑名单误删；computed heads/basis/closure/given-matches/expected/native_result/restore expectation/allocation不得入asset。词法/namespace/source pointer完整，不造缺失token span。

原83为82eligible/79full/交集78/四E.5片段；repair77旧数学仍not-executed，SHACL before/after可另观测但不继承R-risk或叫repair已提交。106操作/54checks/50product原false审计状态不改；五unresolved不是仅五未执行。G-list13无selected subject、G-list05缺late-V1载荷、ontology-model仅四增量、learning-report缺RDF项目等不补造。C为2query+11SHACL，不能缩83或83+date。

完整采集：获准caller stdin接`/dev/null`，probe不读；UTF8 JSONL header→每完整observation→唯一terminal；全API显式参数/来源指针/实际stage起止状态、完整graph/query variables/全rows/None/ASK、reason图/证据、SHACL六字段/conforms、typed全字段、payload/rows/source/definitions/catalog原bytes/base64/wire、同次capture/expectation/allocation及全restore/roots。失败时已返回真实阶段仍全保，失败restore不造view。unknown固定INTERNAL_ERROR/stage，完整stdout/stderr/exit/signal由外部caller保原bytes，首错不覆盖。已知拒绝/unsupported/missing-context/not-executed分别状态；hook只按真实reason/Validator.run code对象计call，已有hook先拒且finally恢复；B1 instrumentation=false不混hook耗时。

逻辑cap保持descriptor1MiB/input8MiB/合计9MiB、observation≤512（实际417）、item32MiB/stdout64MiB/terminal预留64KiB、120s monotonic逐stage前后。新provenance16MiB须消费delta另审。上述均不证明CPU/native/whole-H；opaque调用不可被deadline即时中断。完整item先预算再写，强停半行原bytes保留并判incomplete。exit0仅所选采集完整（可有已知拒绝/未执行），1为harness/unknown/逻辑预算/过界不完整，2为argv/asset/provenance前置非法，130仅协作stop边界；hardkill记真实signal/null。取消request、stopping与目标实际停止/readerjoin/引用释放分别记。

父agent本轮补充：T05原作者报告417全覆盖oracle已生成及28项自有stdlib测试；目前未正式独审/总控收件，本草案未读该新oracle原件，故只记录待交接，不据此写通过。oracle数学约束完整度与实际child allocation准入、12个date首码判定必须分开；后者仍pending，不可用历史78/4/1填expected或把逻辑cap冒实际准入。

T05独立oracle接口提议（须原T05另接收）：`oracleVersion/ref/path/bytes/SHA`固定；按assetSha+descriptorSha+selector+ordered observationId+stage/API/parameters+projectionSha定位完整预期，明确return/rejection/允许missing-context、全term/rows/报告/wire typed/source/definition/implementation/DAG/root/diagnostic。source实际输出不能固成唯一golden。旧C-goldens8163B／`c25e7afcc593a7be09fc8b2ca29af9cff28a7a1e030a13b98aa5e7d88d596440`保core/extension条件；旧T05 expected767826B／`87220503f9983146c974fe3e35025d520cad70e54fdd994aebfa86fb1ff7259f`只外部读，不因文件名inputs喂业务。新图无独立oracle逐ID pending，不删或只比source=package充正确。

未来同批准组合/asset/policy/环境/case序 source与包分开真实采集，外部纯比较器比全结构/有序rows/多重行/词法/失败诊断，BNode仅规定图同构。只预先命名runId/time/真实source-vs-frozen locator/编译域元数据可分域展示，不一般性删除“变化字段”；语义source IDs/lexical不归一。collectionComplete/fullSuiteCollectionComplete/sourcePackageEquivalent/externalOracleMatched/originalOperationPassed分判，probe不自签后三者。full417所有终态可见，not-executed/missing-context不变业务pass。

后继有限方法：先获批code域微验（全23/四函数/checker/重复loader），再完整source/独立包full及strict argv/provenance/resource/offline否例，再T05完整独立oracle，另source/包×1×/10××3fresh=12 B1 trial。每票具体process/前缀/物理准入/timeout/终止方案另授；首次失败留candidate/runID，修复新candidate/delta并适用复审，不自动重试。

## 6. B1、原S1、parent与正式门

| 门                                  | 同版实际证据/前置                                                                                                                                                 | 当前                                                  |
| ----------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| source完整suite                     | T03批准依赖/环境、I05消费delta、固定资产/oracle、caller/物理票；source bytes/loader code核同后真实417采集                                                         | 未运行                                                |
| 独立artifact完整suite               | 实际build/archive/provenance/license/runtime收据；同selector源/包全观测/否例/资源/外联拒绝，各自T05 oracle                                                        | 未构建/运行，不继承旧C4                               |
| 12 B1 fresh语义trial                | source/包×两scale×3fresh；每进程仅对应B1 selector，无先full/另scale/query/validator；First/Warm parse/ontology/graphBuild/query/RDFS-rules/shapes/SHACL与完整输出 | 未执行，不填S1 snapshot                               |
| parent `npm run package:dir`同suite | parent原旗标/默认入口/资源/完整guard及必要回归；实际包调同canonical probe/同asset；source-parent-oracle全比较                                                     | 开放，独立artifact不替代                              |
| 原12 S1 snapshot trials             | source/包×1×/10××3fresh；真实Store/SQLite snapshotLoad/rdflibBuild/fixedSelect与Warm；T01 fixed source/schema/owner/损坏输入保护及物理/H准入                      | HOLD，不调storage_probe，不以数组或0秒伪装            |
| 正式Job/Store/worker/selected/H     | 真实trusted tuple/allocator/source认证、持久化/恢复/取消/历史/公共selected正式链                                                                                  | 开放，组件admitted_job/restore无正式权威              |
| 57P0/C–G/PRD10–12及六迭代           | 原逐项完整输入/输出/失败与正式产品上下文；片段/unsupported/未执行不升级                                                                                           | 范围不缩                                              |
| 指定同版双审                        | ZCode GLM-5.3最高与MiniMax M3.1-Flash xhigh双方新完整只读实际终态及处置                                                                                           | 开放，内部agent静态审不代替                           |
| CI/Windows/macOS/真人/develop远端   | 同候选CI、两目标OS干净无系统Python/断网/签名安装、native/UI真人、正常合并/远端核验                                                                                | 开放，arm64开发机或Linux不代两OS；本窗无push/PR/merge |

B1固定四ontology方法：seed20261019、原18/180 asserted独立`urn:case:{i}:...` IDs；保原asserted给SHACL，每份equipment001 type替换CriticalPump，加CriticalPump→Pump→Equipment和alarm domain/range四条，graphBuild22/184。十ontology28/190只full另案，两个selector不能混。固定两行query末无LF，SHA=`7879b25f2833b8e485b53d3f6664220836ada716ec29ae7de82f907eae014ab5`；原fixture1×/10×SHA=`b0bcc466774f37d4f6a520900b8e7caa5f4fb7f827bbcf8c5ad0e9d12946ea0c`／`25393c99db270c57a75cd75c675876d148659fef7e7624e4197e90754b257ed2`，改型/合并图另摘要不冒原fixture；Q01的162B query另身份。

每trial保预定12ID/所有终态、完整argv/cwd/环境差异、输入/资源/锁/probe/executable前后hash、stdout/stderr/exit/signal/elapsed原bytes/hash、设备OS/CPU架构/内存/Python/库/build工具/分辨率、executable与全目录filecount/bytes/hash、每次First/Warm及统计方法。import/startup wall和workload阶段分列；FirstAfterS1已热，fresh仅进程新，OS cache uncontrolled，不称物理冷盘。原S1 timer=perf_counter_ns，allocation before/after/peak和进程生命周期high-water RSS按实际工具/平台单位，unavailable=null，不能0或phase独占RSS。具体工具/物理准入待票，不重开已拒RSS/heap/OS方法；原验收保留等owner合法方案，Q5无容量线，不量化未测提升。

## 7. 冻结与本窗验证边界

本草案先local commit冻结→新独立agent只读固定candidate，审全部写面/来源/所有权/自引用/代码域/开放门→全文报告逐项处置，保首Fail/unknown→修稿新candidate/delta复核→本地过程交付父agent。T03原会话后续接收后才可能实施，本草案/内部审/root收件都不代T03维护者接收。

本窗仅Git/文件/stdlib AST/JSON/TOML/hash及现有文档formatter。没有产品import、builder/spec/reader/helper/fixture模拟/pytest/probe、业务编译/archive解码、旧binary/witness/42772index/SDK/toolpayload、安装/网络/DB/native/GUI/计量；没有借T03票或改四writer/环境/22供应/2cf源码/公共契约。schema结构核对不是consumer实现、runtime稳定性或实际包通过。最后refs/manifest/hash与独审按实际过程收据，不在本文嵌自身hash/未来commit。
