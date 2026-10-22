# I05 profile 新隔离候选：T03 四文件最小依赖与包入口 offer

**可供总控决定的文档提案，尚不实施。** 本轮仅新增本文件及 `docs/reviews/T03/I05-profile-build-dependency-offer/`。不修改四文件、冻结候选或其他树，不安装/解析依赖，不 import 产品、不跑产品/test/package/GUI，不创建新产品树/Goal。原T03 Goal保持blocked，原父范围和指定双审/CI/正常merge门不变。

授权：总控 `T03-I05-profile-build-offer-preparation.md`，2878B / SHA `288350b2cf49586df962544d47fd76eb3b2f4b005cb1909828b42f7cc00b83da`。I05方案只读根快照 `.private/next-business-plans-received/I05-profile-new-candidate-plan-28295b0e.md.raw`，30339B / SHA `28295b0efd79c68ab5fe9ba1dd5c335b72a2be0e9d044698cdbc3a00a4bf32b9`，仍待独审及施工许可。全部固定ref、四文件12组blob/长度/SHA、lock记录/分发artifact哈希及七模块AST在 [inputs.json](../../reviews/T03/I05-profile-build-dependency-offer/inputs.json)，它们是静态来源证据，不是批准消费。

## 1. 固定输入与最小依赖决策

- 唯一施工来源基线：批准 `5f910b52c69d86a1076b2032e5d3c63e715947f3`。
- C4只作依赖/旧构建比较：`523c478d5f39671c4ac7c1ea6997e51d3047d58e`；不采用其整体lock/venv/worker/runtime/旧包/旧probe或inventory脚本。
- T03已有XLSX四文件候选：`30319412daf8ae4745987babf7bbed93c53b6b42`，原树固定保持；它不是本次I05从5f开始的自动批准依赖。
- T05七文件候选：`1e3e0ee1d9d5b70f1f59233d0a3c64f6d85fd2cb`，本次只读AST/固定字节；未来消费须root批准，唯一未来维护者仍T05，不由I05/T03 fork。

### 候选依赖闭包（按C4固定lock核实，非本轮安装结果）

| distribution | 精确候选版本 | 真实依赖边/现有关系                                                    |
| ------------ | ------------ | ---------------------------------------------------------------------- |
| pyshacl      | 0.30.1       | 新direct；依赖owlrl、packaging、prettytable、rdflib[html]              |
| pyparsing    | 3.3.3        | 升为engine显式direct；5f已通过RDFLib锁到同版本，非版本升级             |
| rdflib       | 7.6.0        | 保留5f direct/pin；依赖pyparsing；新增被激活的html extra               |
| owlrl        | 7.6.2        | 新传递记录；依赖rdflib                                                 |
| prettytable  | 3.18.0       | 新传递记录；依赖wcwidth                                                |
| wcwidth      | 0.9.2        | 新传递记录，含平台分发artifact；不可只留一个宿主wheel                  |
| html5rdf     | 1.2.1        | 新传递记录，来自rdflib[html]，不能因普通dependencies列表中未列出而漏掉 |
| packaging    | 26.3         | 5f已锁同版本；pyshacl使其成为运行闭包依赖，不另升级                    |

5f lock为18包/SHA `d5d027da6628a2f4fc2e73730ce3a5e40d85aebba95188b0d4c3801ebdde949e`。C4为23包/SHA `86dfe82d952e2c88edcfc5658f488f6e1f0d04b4ec3b1e6f5c5d3bc4f57e8b73`：仅新增pyshacl/owlrl/prettytable/wcwidth/html5rdf，已有记录只改变engine声明和rdflib激活html的记录；其余16个旧记录及lock非package顶层字段静态相同。这里不把C4整锁当批准结果，也不预言新解析的lock SHA。

**推荐本次I05单独从5f施工采用A面：** pyproject保留 `rdflib==7.6.0`，只新增direct `pyshacl==0.30.1`、`pyparsing==3.3.3`；唯一uv.lock固定上表完整闭包，保留原workspace/dev/平台记录及发行hash，禁止无关升级/删marker/仅保宿主artifact。正式授权后由T03在隔离树生成并审核实际lock patch，不下载/直接覆盖C4锁。若解析不能满足固定候选版本，先报具体冲突及最小约束方案，不擅改根workspace、加第二锁或接受漂移。

**与XLSX的B组合面另列，不暗中采用：** T03 303仅加openpyxl3.1.5/et-xmlfile2.0.0/defusedxml0.7.1三个新包、其依赖与engine声明；lock21包/SHA `9f5b6d2b93d994a3e4f8a46ce5cccae99d4e024ea7531ab62dd8e85d6aa1152e`，其他17个旧记录不变。版本与A无已见静态冲突，若root后续明确批准组合则保留这三项声明/收集/受限mapping-probe并合并A的两direct/五新记录，预期包集合为26项；仍须实际解析/锁审查及联验，不能据集合并集声称兼容通过。当前I05纯后端不需要为了借用XLSX而引入mapping源码；A不删除或回写原S1的B候选。

## 2. 精确四文件 delta 与 writer

四文件唯一未来维护者仍T03，本次均零修改；下列是待root阶段授权的最小修改面。

| 文件                             | A面最小delta                                                                                                                                      | 必保留/禁止                                                                                                                                                                           |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `packages/engine/pyproject.toml` | 在5f engine依赖加上节两个exact direct；不改包名/0.1.0/构建系统/Python范围                                                                         | 不把七quality模块当新pip包；不拷C4项目其余声明。B组合若获批保留原3解析库                                                                                                              |
| `uv.lock`                        | 更新engine依赖/metadata；锁5个新记录及rdflib[html]边、实际registry/完整分发hash/依赖markers；保留已有版本和dev/tool链                             | 唯一锁仍根uv.lock，`uv sync --frozen`使用新实际锁；不复制C4整文件/venv，不造overlay或第二lock，不以现有hash冒充未来产物                                                               |
| `scripts/build-engine.mjs`       | 保留5f构建流程；加入下节pyshacl闭包资源/metadata与七quality明确canonical模块收集；只为I05实际固定输入添加已批准asset映射及build生成的只读来源清单 | 保留rdflib、contract python/v2、provenance/uv.lock及原engine数据、原输出/缓存隔离。C4的scripts/i05-build-inventory.py与build/i05-inventory不在本新方案采用面，不能直接拷入            |
| `packages/engine/entrypoint.py`  | 建议新增唯一受限分派 `--semantic-profile-probe` → I05的 `ontolearn_engine.semantic_profile_probe.main`，符号/CLI须I05冻结后才能实现               | 不另写probe/matcher/expected；不接C4 `semantic_probe`/旧 `--semantic-probe`，不改storage/contract/protocol/worker和默认5f路由。B组合仅在获批且模块确存时保留mapping-probe，不加空入口 |

不改protocol/resources/worker/旧测试/CI/其他owner文件来补依赖。I05从5f适配resources、八语义文件及新probe，T05七文件采用与oracle交付都由root另按原方案定界；本offer不替代其批准。

## 3. PyInstaller明确采用面与排除面

### 运行库候选收集

沿5f已有rdflib收集与rdflib/pyparsing metadata，建议补 `--collect-all pyshacl`、`owlrl`、`html5rdf` 和 `--recursive-copy-metadata pyshacl`。对静态导入的prettytable/wcwidth/packaging记录完整闭包，验证实际代码/所需数据和对应dist-info/许可证都存在；不能假设recursive metadata已覆盖extra或正常import分析就证明包完整。若实际打包遗漏，按具体missing module/data/metadata给最小收集delta，再形成新候选，不预先整收引擎所有业务模块。B面三库原收集只在获批组合时沿用。

这是候选收集配方，**没有执行PyInstaller或证明其动态hook结果**；上表八distribution及实际代码/资源/metadata身份最终均需新源环境和新包原件验证。不得使用C4已打包结果替新候选背书。

### 七quality文件：原相对位置、同一canonical名字

固定前缀 `packages/engine/src/ontolearn_engine/quality/`：

| 文件/canonical模块尾名                                      | I05明确使用/递归需要                                                                                                                                                                  |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `__init__.py` / `ontolearn_engine.quality`                  | 仅原包父节点；548B/SHA9a5130…806d9c，保留原字节，不调用四个旧懒导出                                                                                                                   |
| `rule_profile.py`                                           | PROFILE、BUDGET_VERSION、PINS；TermInput/SourceRecord/InputLocation；ProfileLimits/Budget/ProfileFailure                                                                              |
| `rule_firing.py`                                            | RuleSpec/Triple/Variable/Comparison/Catalog/BindingMatch；compile_rules/evaluate_bound_batch/check_firing_group；ComparisonEvidence/HeadEvidence/PreparedFiring（返回批由同模块签发） |
| `rule_terms.py`                                             | parse_value/term_key；ProfileValue由实际进程机制发行，不从JSON重造                                                                                                                    |
| `rule_numbers.py`、`rule_calendar.py`、`rule_comparator.py` | 既有相对import闭包；不另写比较/日期/数值执行器                                                                                                                                        |

建议对父包及六个确切子模块逐项 `--hidden-import ontolearn_engine.quality[.rule_*]`（实际参数是inputs清单的7个完整字符串，不使用通配符），并在构建前核七份实际源文件与固定ref的原字节SHA，记录包内七模块归档身份及独立冻结产物hash。**不使用 `--collect-all ontolearn_engine.quality` 或 `--collect-submodules` 扩整包。** 对根懒导出指向的 `ontolearn_engine.quality.definitions`、`.planning` 明确排除收集并核TOC/归档不含其字节；如果构建分析提示缺这些旧服务，应确认为本次刻意排除面，不用stub或复制未批源码“修绿”。实际依赖若真调用旧服务则失败并回root申请完整采用面，不能隐藏必需导入错误。

六个rule_*模块的计算导入闭包仅含所列同包模块与stdlib；父__init__另保留指向definitions/planning的四个旧懒导出，未采用且不得触发。PROFILE为 `OntoLearn-rule-comparison-profile/1`，BUDGET_VERSION为 `mechanism-budget/1`，PINS是四份标准文档标识（不是pip版本）。I05必须从明确子模块导入，不 `from quality import *`、不触发DefinitionError/ValidatedDefinition/validate_definition/build_plan四个根懒导出、不访问私有seal/发行表。

来源清单建议由本四文件中的build-engine.mjs在构建前直接按固定采用表/输入asset/完整uv.lock生成（例如build私有目录→包内provenance只读JSON，精确字段/相对路径待I05接受），不采用C4 inventory脚本，也不另建产品probe。它记录的是实际构建输入，不能把清单自报的源码SHA当成包内已验身份。冻结PYZ/pyc通常不是原.py字节：源码SHA、实际归档/引擎hash、包内规范模块/类身份和同版构建收据分开保存并关联，禁止要求pyc与.py逐字同SHA或伪报inspect得到原源码。实际归档清单/代码指纹方法由I05与T03在包合同中冻结；缺证据即待验。

源/包只允许同一canonical模块实例：不重命名包、不把同字节另装成别名类；`rule_profile`的sys.modules识别和CompiledPlan/ProfileValue进程本地发行关系不能由“源码hash一样”替代。实际包内新probe应报告可验证的模块名/发行依赖/资源身份并走真实reason；不得伪造模块对象来满足检查。

## 4. I05唯一新probe：建议合同及待冻结字段

本次只提分派与限制，不创建 `semantic_profile_probe.py`，也不在T03目录写另一个计算probe/执行器。**I05须先交固定probe源码和入口签名/数据合同；当前main函数、选项、JSON字段均非已存在接口。**

- 建议源命令 `python -m ontolearn_engine.semantic_profile_probe` 与包命令 `ontolearn-engine --semantic-profile-probe` 最终调用同一个I05 canonical main/同一 `reason`。后者仅接受该单flag；额外路径、脚本、URL、任意JSON/表达式/其他flags固定拒绝，退出2/受限固定stderr，不落入默认服务。若I05确需固定case选择器，先冻结有限枚举再调整本offer，不能临时开放通用输入。
- 固定输入来自root批准的T05唯一oracle输入/已有17文件与扩展的具体版本；只把明确的**输入数据投影**放进受控manifest。来源必须包含case ID、相对asset映射、原bytes SHA/长度、profile/模式与完整定义/事实/ontology/source条件。不得把oracle expected塞入输入或probe计算分支，不从actual生成expected。原17是文件数，不偷换为17例。
- 不接受外部任意文件；源与包使用同一固定输入manifest原字节和同一明确定位器，包内路径相对已收集immutable资源。不能在包内失败后回退到checkout、用户目录或网络。输入总量、逐文件/展开/输出预算沿I05待冻结profile明确；超过预算真实拒绝，不截断事实/证据或漏后项继续“成功”。
- 输出实际完整rdfs/custom/warnings/basis/成功firingGroups、来源leaf/sidecar/定义/输入摘要及实际三字段implementation、机制PROFILE/BUDGET和每case真实有限失败/安全位置；不得只给数量/版本或复用C4 expected。exact私有JSON shape、稳定顺序、规范化、终态/退出码及是否含逻辑模块/资源hash由I05冻结；T03不先造第二DTO。CLI exit0至多证明固定probe采集完成，不能替外部完整oracle对照通过。
- 已知域失败保留实际有限reason/location/classification，fixture/case编号和未知source位置须准确；意外异常仅固定脱敏stderr/非零退出，不能泄露原异常、堆栈、绝对路径、term原值或凭据。错误形状与分类仍由I05该producer冻结，不把普通SHACL违反伪装成执行崩溃。
- 不打开Store、不创建/模拟Job、不改registry/公共capability、不写current/history；只跑被批准的真实图计算入口，不加第二matcher/comparator。资源只读和本次探针产出由外部shell证据采集，不能让产品probe自己改expected或宣布父验收通过。

**I05/T05/root尚需给的固定字节：** 新probe ref/path/SHA与main/CLI/输出契约；新semantic/resources精确采用表及实际executionSemanticsVersion/engineVersion/lock绑定；七quality采用许可及固定ref；唯一输入manifest/全部asset和单独oracle版本/hash、具体cases与完整结果/失败预期；asset locator和预算/安全失败合同。没有这些，不做入口stub/包成功推断；尤其不捏造新probe哈希、i05-finite-7已执行身份或synthetic producer认证。

## 5. 不争写冻结候选的实施与交付顺序（待授权）

1. 本轮只把offer和静态证据提交当前T03文档树；原T03-mapping 303及source-selection 8c产品/测试、C4都不改，不写I05拟树。root可先决定依赖A面/明确B组合、收集范围、probe合同和精确下一阶段；不要求整个领域runtime都合并后才准备。
2. 真实实施另由root指定T03独立worktree/feature从当时实际批准5f或明确新批准base开始，独立node_modules/.venv/build/日志；建议独立名T03-profile-build仅是提案，当前不创建。T03唯一写这四文件；I05只写其获批语义/新probe，T05维护其七模块。跨树不共享可变venv、输出或lock编辑。
3. T03形成只含四文件及本线必要证据的固定提交/ref/文件hash，保留实际resolver/lock/发行hash/许可证和构建日志。root确认同版I05/quality/input依赖后，I05仅按精确集成授权接收这个固定提交，不手工改T03构建逻辑、不整拷C4锁或将接收扩大为未来维护权。遇冲突先回T03唯一owner；AGENTS不stage，禁止宽泛结束进程/覆盖他线WIP。
4. 集成验证在一个实际批准的候选快照完成：root须明确谁的树持有I05新10文件、固定quality7、T03四文件和唯一inputs；不能拿三个树的分别绿拼成一个包绿。I05如尚无产品树/准入许可，维持依赖待验，不用临时import C4环境绕过。

## 6. 正式实施后必须采集的同源证据（本轮均未跑）

- 核干净独立环境、完整实际lock、精确库分发/许可证/metadata、七quality hash及规范模块身份；源码实际reason接受固定inputs，保存完整实际结果和全部失败。输入字节先封存，外部使用同一批准oracle逐集合/顺序/类型/来源/全head与basis对照，不混进probe内部。
- 对实际四文件/语义/收集影响运行原必要 `npm run check`、`npm run verify:sources`、新 `npm run package:dir`；首跑失败、实际命令/退出码/环境保留。无变化旧候选不重跑。check范围若含外部未批依赖不跳过换绿，按缺口报告；本机仍不启动Electron/native/e2e/HMR。
- 从**新实际包内引擎**运行同一新probe/同一输入manifest，核原bytes hash、完整实际JSON及有限失败/额外参数拒绝；包内原有storage/contract/resources probe按实际受影响范围回归，不把旧C4或T03旧包的结果贴到新包。若B组合获准，还须保留并核其真实mapping probe与三解析库。
- 采集源与包实际engine/模块/合约/uv.lock/输入资源/依赖metadata/许可hash和不可变清单，分别记录原源码与冻结归档hash并关联实际构建输入，不能把二者当同一种字节；核quality只7模块、无definitions/planning、无别名重复类，实际implementation与新resources/完整锁一致。不能只打印期望标签或仅比数量；source/包差异（例如规范化后的定位器）须准确披露，输出规范由I05先冻结。
- Windows/macOS目标平台/干净设备/B1和受影响恢复仍各自实测，CLI包通过不代native/UI/Store/取消联验；完整P3/P4及旧legacy能力、错误定位、历史分区、跨消费者支持范围、指定同版双新审/双方通过后push/PR/CI/正常merge/远端核验保持原门。

本offer只解除“所需依赖/四文件最小改动/私有采用面和包合同尚未列清”的准备缺口，未使任何库、输入、算法或身份成为实际批准依赖。独立静态复核和交付收据在reviews指定目录，未知接口待I05冻结，不用无变化运行制造进度。
