# T05 固定纯输入的独立 oracle 实现窗

2026-10-22。继续原 T05 会话 `01a15bce-021c-74e0-a7ac-a899380b424a` 与原 Goal，不创建替代会话／Goal。原 date 树525c917及其它已收件材料全部冻结。总控已从实际核验的远端develop `5f910b52c69d86a1076b2032e5d3c63e715947f3` 创建新树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T05-source-package-oracle`，分支 `feature/T05-source-package-oracle`。开始仅受保护AGENTS M，15852 B／SHA78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759，先实际读，不stage。设置与状态见 `T05-controller-source-package-oracle-setup-proof.json`。

## 真正可并行的依赖

I05首候选 `0e42a0fe349054a92817cb4d463bccdc15f6c042` 的两件纯输入已固定，内部独立审查完成了输入白名单／来源／全部投影及集合检查，未发现expected污染；总控也已核全部72payload固定Git清单、实际417 observations／320 datasets、大小及三个case-set。I05 harness仍在R1失败后的修复，**本窗不接收probe或宣称其通过**。oracle的业务expected只依赖固定纯输入和已批准语义，不依赖harness deadline／partial-output修复，因此可现在并行实施。

只读以下固定Git原字节，不从当前I05 WIP读取：

| 0e42下路径                                                                                |   bytes | SHA256                                                           |
| ----------------------------------------------------------------------------------------- | ------: | ---------------------------------------------------------------- |
| packages/engine/src/ontolearn_engine/probe_inputs/i05-source-package-parity-inputs.json   | 8205267 | 47c66ffe18613eb8cc1af6365dcfc9d866821f22c48f96d9f44725f8f7c59eaa |
| packages/engine/src/ontolearn_engine/probe_inputs/i05-source-package-parity-manifest.json |   21202 | 0b91c1a9366d170b5614d94c20006054a5a959be235e0f46cb150cf32335193a |

先读固定合同 `ee2b30a2dad35b2d395f9c735aff80371ab41110:docs/iterations/I05/source-package-parity/contract.md`，重点完整观测矩阵、§4/6/7。原规范、Q6比较政策与有限UTC-date政策已由用户采用，不重新设默认或重问。使用你原来已收件冻结的独立expected／合法golden原件，先核实际ref/bytes/SHA并列来源；例如独立接受数据中的triples/graphs/rdfsWitnesses/matches是external expected，不因旧文件名叫inputs就放进引擎。不能以I05新probe/tests/generator源码或其任何运行输出作为oracle权威；本窗不要读取这些新实现。必要接口／类型仅引用批准合同与既有规范，不复制业务实现算法充golden。

后续I05若修改两输入字节／ID／投影／语义，必须显式输入delta、更新oracle并复审受影响范围，不静默混合版本。仅harness改变且两输入相同不构成oracle业务数据变化；未来实际JSONL适配仍另审。

## 唯一交付：外部oracle数据与可复现构建

按全部417 observation ID和三个case-set给完整独立expected／可审约束与来源。原83中82 eligible／79 full／交集78，repair77原profile不执行，但before/after SHACL仍独立验证；四E5仅片段数学，不能升级原操作通过。原106操作、54检查、50用例的上下文／false执行权威与未实现生命周期保留，不把metadata覆盖当执行。

每项给明确normal／known-rejection／not-executed语义及完整业务内容的比较政策。Turtle／图／query全部bindings及类型／RDFS／规则rows与when/comparison/head、basis/source／scope实际分支／SHACL完整字段、整数与UTC-date／生产及restore／roots／offline和逻辑预算边界全部覆盖，不只列数量或退出码。有限UTC-date不改Q6，其他timezone／mixed／exclusive范围按已采政策。所有动态值和不可预填的fresh bytes/expectation/allocation、runtime身份需明确可审的关联／完整性约束和来源门，不能拿source SHA预填包code证明。九扰动按原expectation验证实际接收bytes的A1拒绝，不夸成深层DAG或末child原子性覆盖。

逐字段给固定expected或完整、有限、可审predicate；集合顺序、空白节点／动态身份归一化须有依据，不得借归一化删业务字段或忽略全部尾项。harness unknown／incomplete／未执行必须保持独立状态，不能因collection exit0就oracle通过。没有独立依据的项目明确pending并指出缺口，继续可独立项；只要仍有必要oracle缺口，不宣布全oracle完成，不缩减417。

为将来source/package比较保留全部差异域，不读取或运行I05来生成expected，不从source观察再固化golden。此阶段实现独立语义expected和字段/关联规则，不冻结未批准的JSONL适配、build provenance或collector接口，也不写最终source/package等价比较脚本。

## 精确文件责任与可运行边界

只维护：

- `tests/fixtures/quality/i05-source-package-oracle/`：外部oracle expected／schema／逐ID覆盖与来源manifest。不得将其收进engine输入或包内业务资源。
- `scripts/build-i05-source-package-oracle.py`：仅stdlib，从本窗固定输入／已审独立规范与expected构建／核对外部oracle；无产品、rdflib、pyshacl、旧probe或任意业务模块import/call。可用Decimal、纯数据和有限独立规范推导／声明式expected，不抄I05算法。
- `scripts/test-i05-source-package-oracle.py`：本外部oracle的独立stdlib单测／完整性校验。可执行自己新oracle代码和纯数据测试，验证真实规范expected与错误拒绝；不调用产品、实际probe、native或伪装成源/包采集。测试不能只有条数、不能仅镜像generator。
- `docs/iterations/T05/source-package-oracle/` 与 `docs/reviews/T05/source-package-oracle/`：设计／字段政策／来源／输入raw副本／静态和本oracle自身验证／独审／逐项处理／有限交付清单。

不写 `scripts/verify-i05-source-package-parity.py`（未来外部比较器另窗）、I05新probe／资产／tests、公共contracts、语义／quality产品、T03四writer／lock／环境／打包／CI／Job/Store/selected、任何旧树。不共享可变venv/node_modules、不安装第三方依赖；现有明确获准formatter仅作文档工具，原.raw和历史报告不批量格式化。T03专用计量票完全不供此线使用。

允许普通Git/文件/stdlib AST/JSON/hash、纯外部oracle生成及自身stdlib测试、文档格式检查。这些实际检查只证明oracle模块，不替代产品pytest／npm check／package或源/包运行。禁止产品imports/pytest/probe/DB/native/GUI/网络/业务child或读取未来观察目录；不复用已被拒的heap/OS/SQLite分析。本窗不授权任何模型外发或付费。

## 冻结、独立审查与交付

先固定输入及责任，完成真实oracle，不停在计划。复杂工作可用独立agent并行负责互不冲突的子任务；遵守独立worktree、精确文件责任与整合规则，不在同checkout共同写。候选先实际本地提交，给base/head、真实验证、准确状态，再交新独立agent审完整417覆盖、expected独立来源、所有字段／异常／缺口及生成可复现性。审查只写新报告；不得并发修改受审路径。发现问题按原候选保留→修复新提交→独立delta，全文读并逐项处置；不覆盖失败。

交付完整manifest/Git/hash、实际命令及结果、独审／处理、oracle仍pending项目与准确后继步骤。输入delta或新JSONL适配后仍须相应复审，指定外部双模型门不替代。原Goal/父T05／formalJob/selected/83E5repair/wholeH、SQLite损坏输入HOLD、S1/parentB1、目标OS/CI/真人/远端develop门保留，无push/PR/merge或当前桌面操作。
