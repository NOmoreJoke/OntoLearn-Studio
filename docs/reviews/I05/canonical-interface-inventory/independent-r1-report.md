# I05 固定接口库存 R1 独立静态审查

结论：**Limited Pass，限现有接口事实库存**。未发现 P1/P2；有一处不影响字段完整性的 P3 行号笔误。该结论不接收新 codec，不证明 full417、运行、同次调用来源、发行者、费用或权限成立。D2 能否采用哪些纯文档，仍由总控精确接收；源文件访问权没有随本报告转给 D2。

## 身份、固定范围与完整性

审查者是 `/root/independent_canonical_interface_review_r1`，与库存作者独立。本轮只读候选 `4beccef733396d525b9db56be544dbdb551581ad` 的两个 `canonical-interface-inventory` 文档前缀，共23件。工作树为 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-canonical-interface-inventory`，分支 `docs/I05-canonical-interface-inventory`；候选基线为 `1b6df7a220fc9a67d7046133a340085f03f0a96c`。接口事实的唯一产品源是 `2cf0c3328de464e15a3fa9cdbfdf6aa88d0b4a64`，不采用文档工作树的产品源码。

我先全文读取三个 controller 静读绑定，再独立核 candidate-manifest 的22个 payload 加 manifest 本身：base→candidate 的实际23件集合精确相等，当前字节与固定 Git 全相等；22个 manifest bytes/SHA 均相符。没有修改候选原23件，没有暂存、提交、切分支、GUI或创建 Goal。

源码窗口为八个初始文件272650B、11个追加接口文件258542B，共19个固定 Git blob、531192B；19件 bytes/SHA 全与 binding 相符。另核三份 controller 片段：semantic_identity 646B、IMPLEMENTATION 187B、RootRef 字段 JSON 904B，SHA 均相符。**没有读取或解码 resources.py 的整份 Git blob**；没有求值 IMPLEMENTATION 的锁读取表达式或追到 LOCK_FILE。

追加 helper 只读取/提取获准的类型、构造字段、签名、返回 class 与 serializer 键；没有研究 ledger 算术、费用/费率、恢复或物理预算算法。AST 全模块解析仅用于定位声明；没有 import、exec、runpy 或执行产品函数。未读取 actual、expected、probe_inputs，未运行测试/probe/model、第三方 schema 引擎、安装、构建、网络、DB或 native，也未接触两项外部 retained 审查的应用任务、prompt、输出，以及 fee/carrier WIP。

## 独立核对及结果

| 核对面        | 实际证据与结果                                                                                                       |
| ------------- | -------------------------------------------------------------------------------------------------------------------- |
| 固定身份      | 23件候选 membership/current=Git；22 payload manifest；19源码及3片段身份相符                                          |
| 返回目录      | `additional-return-layouts.json` 全15个 record 的本地字段与固定 AST 声明相符；继承顺序逐项相符                       |
| 首窗口类注解  | api-layouts 全9个类字段目录与固定 AST 相符；未把注解解释成运行验证                                                   |
| API字典       | 全13个 API layout 的有序键与对应返回/构造字典相符；provenance 按 `**source` 的四键静态展开为13键                     |
| 定义索引      | source-index 的241个定义的位置、签名、返回注解或类字段均相符                                                         |
| 追加声明索引  | 37个实际 named declarations 全相符；缺失名仅 OfflineAccessDenied，有限定位保留为 unknown，不外推其他文件/alias不存在 |
| 摘要/原 codec | 人工核16条 recipe 及对应源码表达式；scope JSON、profile JSON、原 bytes、N3与新的 relation/display digest 边界明确    |
| 未闭项        | current-disposition 的 M02/M03/M04/M05 wholeGateClosed 均为 false；不把收到声明等同于接收完整实现或规范              |

第一 checker 有118项结构核对，第二 checker 有265项声明核对，**383项均通过**。这不是383个产品测试，也不代表所有语义路径已运行。第二 checker 尝试提取名为 `allowed` 的类白名单表达式，得到空目录，因为真实变量名为 `approved`；这项提取没有被当作通过检查或计入白名单证明。随后以固定源码 `_ProfileProjection.value` 519–590 定向静读独立确认17类列表及包装形状；原空提取与后续真实读取都保留，不改写已有过程。

## 关键事实的独立判断

### M02：旧 metadata 与返回字段

`semantic_scopes._source` 73–85 的四键确为 executionSemanticsVersion/assertedInputSha256/ontologyInputSha256/selectedRulesSha256。ValidationScope 的四字段和 provenance 完整13键均吻合。derived 分支保 `dict(source)`，reasoning_result 保入参引用；asserted 分支必须 rules 为 `()`，故 selectedRuleIds 和 warnings 为空。selectedFacts 的 asserted/rdfs/rule 三形态与正文相符，没有把新数学表达的 ruleId 或 asserted basis 倒填到旧字段。

legacy reason 五键、evidence 四键、rdfsEvidence 两键相符。所读函数没有发行专用 metadata byte wire，因此 current-disposition 将新导出 codec 的接收保持 pending 是正确的。数据字段的 frozen/dataclass 注解不被用来认证 Graph/dict 内容、来源或权限。

### M03：摘要 preimage 与 codec 分离

scope `_digest` 使用紧凑、排序、ensure_ascii=False 的 UTF-8 JSON，没有显式 allow_nan=False、domain prefix、LF或归一化。graph/source/view 保 N3 triple 排序；rules 保 canonical Rule 的 id/when/then 结构和规则 id 排序。第三方 n3 词法没有在本轮运行验证。

semantic_execution 的普通 `_json` 及 profile `_profile_json_bytes` 显式 allow_nan=False；它们不能回填为 scope `_digest` 的选项。profile 的 text input 保原 UTF-8 bytes，structured input 保原 records 的 ProfileProjection；source/definitions 各用原投影字节摘要。payload 七键和 wire 四键吻合。rows 依据解码后的字符串以 MAX_CELL=8192 个 Python 字符切片，保末片，然后独立 JSON 编码和 SHA；不是 UTF-8 字节切片。

material 的 `_project/_encode/_definitions` 与 profile projection 是不同入口；文档没有把其兼容性说成已运行通过。production 原 catalog_json 在391行确为 `_profile_json_bytes(_ProfileProjection().value(capture.actual_catalog))`。其中 `_ProfileProjection` 的 record 包装是 `recordType` 加展开的字段键；probe `_typed_value` 则是完整模块类名的 recordType 加嵌套 fields。二者须分别保留，不能把 probe 的 fields 容器插入 production catalog codec。正文第33行“fields/recordType包装”宜按“原字段及 recordType 形状”理解；本报告明确上述精确区别，不新增第三种包装。

IMPLEMENTATION 片段只证明三键赋值及两个字面版本；dependencyLockHash 是未执行的源码表达式。semantic_identity 在 exact bool 条件下覆盖 executionSemanticsVersion 为 finite6/7/8。这里没有实际锁哈希、路径、当前 runtime 或 issuer 证明。

### M04：来源、同次调用与权限

scope 模块首段、project docstring 与 `_selected_output` 均明确划定：哈希比较与内部一致性不认证 producer、历史 selected、授权或 storage binding。prepare→project 的直接传值及 probe 保存字段是静态调用事实，不是已批准的 same-issue/live-handle verifier，更不是运行 call count。parser `_issue_context` 只是获准 API 的返回指针，本轮未追读其内部；库存没有把它提升为 legacy 认证器。

在这个有限窗口内未提供已批准 verifier，保持 pending 合理；报告和候选都没有据此断言未读文件中绝无实现。没有因字段齐全或 content equality 签发新 authority。

### M05：类型、继承与错误出口

ProfileComputation 本地14字段，ProfileExplanationComputation 继承后保15字段，version 覆盖不重排原位置，direct_receipt 增在尾部。native_result、wire、material、各原 bytes 和 sidecar 均保留。ReadonlySequence 的 native_kind 和 items 没有丢弃；RootRef 的五字段、后四可空和 `kind:str` 均相符，没有补造 enum。

SourceRecord、TermInput、InputLocation、ProfileLimits、firing记录、Number、Calendar、ProfileValue 的指定声明均核对。ProfileValue.value:object、native_result:dict、未细化 tuple/object 等仍不是已接收的封闭 grammar。此缺口被 current-disposition 保留，不能由17类白名单或实际输出反推新的 expected/schema。

query ASK/SELECT、SHACL返回六项 violation字段、profile私有诊断和public四键error均吻合。SHACL未返回原 Validator report Graph；公共 adapter 的有限出口不等同于新 carrier 全 exact-class safe adapter 已采用。已读 helper 的错误声明和正文的 unknown 表述相符，未裁掉未知字段以换取表面完整。

## 发现与处置要求

**IR1-N01 [P3，非阻断] DirectStepsReceipt 的正文源码范围少一行。**

位置：`docs/iterations/I05/canonical-interface-inventory/helper-interface-facts.md:23` 写 `directsteps.py70–80`；固定2cf的类实际为70–81，retention_owner 在81。`additional-return-layouts.json` 已正确保存 endLine81 和全部11字段，正文也列出 retention_owner，因此不是字段遗漏或 codec 数据损失。最小修正是在后出勘误/修订中将正文范围改为70–81，不倒改本轮冻结候选。本 P3 不阻断有限接口事实接收。

没有发现需阻断的 P1/P2。未闭的 grammar/verifier/运行门是候选已明确声明的后继缺证，不能把它们消账；同样也不将其泛化为产品实测失败。

## 当前与历史的读取方式

`interface-facts.md:7` 明示首八文件中的“未获准/尚未定位”是历史窗口；`helper-interface-facts.md:39` 与 current-disposition 汇总随后收到的11 helper及窄片段。missing-definitions 是初始请求快照，不能拿其 textRead=false 否定后续实际到件。两份 source-inputs 与 final-fragment-inputs 的绑定身份可独立复核，后收到的 RootRef/IMPLEMENTATION 已在 current-disposition 列 textRead=true，但 wholeGateClosed 仍为 false。这一安排保留历史来源，也没有虚称旧请求表为最新状态。

## 执行记录与限制

使用固定 Python3.12，PYTHONDONTWRITEBYTECODE=1。两个独立 checker 的真实 argv/cwd/exit 与分离 stdout/stderr 分别在 independent-r1-execution.json 和 independent-r1-index-execution.json；均 exit0，stderr0B。其 Git读取子命令逐项保 exit、stdout长度/SHA与固定 ref/path，以及原 stderr；原源码 stdout 保全在不可变 Git blob，没有复制全源码给 D2。交互式定向文本读取留在实际工具转录中；没有事后补造其早期双流或时间。

检查源码的首批118项、次批265项均静态通过。后续 formatter、最终候选只读复核的实际流由独立 seal receipt 记录；原始流和执行过的 checker 不重写。没有执行产品和性能测量，没有 CI/生产/两OS/真人证据，也不引用他方指定审结论。

最终可接收范围仍为**固定源码接口事实库存**。新规范/完整codec/实际采集、same-issue/issuer、费用/17L、wholeH、417、S1/B1、SQLiteHOLD、真实父Job/Store/selected、平台/真人/CI/develop等均未由本次关闭。需要总控接收精确纯文档后再给D2使用窗口，且后继实现与实际运行应另依原门授权。
