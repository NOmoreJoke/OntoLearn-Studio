# D2 canonical interface 纯文档独立审查 R2

结论：**本轮固定 R2 的限定文档增量通过（Limited Pass），未发现 P1/P2；IR1-P2-01 的两个显式目录遗漏已在 R2 关闭。** 这不更改原 R1 Fail 历史，不代表全部值语法、原 codec、实际权威或产品接线通过；采用、source/runtime、issuer/capture、17L、full417、whole-H、SQLite HOLD、两 OS、真人、指定双审、CI/develop 等门仍为 false/pending。

## 对象、授权与独立性

工作 tree 为 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-d2-consumer-design`，分支 `docs/I05-d2-consumer-design`。旧 205 固定于 `6b94c152a8fca0f0e26d377b0e4d79ff4d64b8b5`，其中原 176 另核 `0841ffbe7a4599fbea96f4ff998808f3f4e00972`。R2 candidate 固定为 `92352c581d958300d566037e5df7a1cbde660f61`，过程固定为 `e2125ef17a901e70bd83b2e7d48373eba7bf6b92`；实际独立检查时 HEAD 等于该过程提交，但结论绑定上述固定对象，不要求后续 root 合法封存审查文档时 HEAD 停住。

先全文读取适用 AGENTS 和 root 两份精确接收件。事实依据限于 root allowlist 的 11 纯事实 @39a91de416eb2692aea079c637309f9d8770b08a、两纯类型文档 @d6ecbc887e1bf9acd5e98b18237d6740d2e61796 及本 tree 对应固定快照。全部 13 件逐一核 current、固定 Git 对象、快照、bytes/SHA。sourceRef/path/行号只作来源元数据，未沿它们读取产品、索引、方法、算法、资源或 LOCK_FILE。新输入快照内历史 `D2ReadAuthorization=pending` 是接收前原件文字；本轮权限只来自 root 后出的精确接收件，不改快照。

本轮九份作者设计已全文读完；长 JSON 分段读取，并补读被工具截断的区间，全部 JSON 另由新独立 stdlib checker 全量解析。固定八旧设计仅核身份并读取必要继承字段目录/纯事实；不复跑旧 codec 或旧摘要/切片算法。原 R1 只全文读取 root 指定的 report（11122B，SHA `35b1d913c4baf3bbe07d3a582ae16fd9ed76479d77841e865b89b0ec5efc5b11`）及 receipt（5188B，SHA `59e20cd2a31de65a0f4a220b20eafcf565cb2ca27295aef21900fc0e6b7da600`）；其余 12 附件只接触允许的身份元数据，未读正文或运行 checker。没有读取其他 retained 外审、peer 或 native 会话内容，没有使用记忆作为事实来源。

## 身份与清单

R2 manifest 为 5339B，SHA `f6bbc95cef3d0b588739b7a332d50cf15e63d3aa0dda3736477fdbdff502a18c`；process receipt 为 81542B，SHA `b9a3246e11eee57489f46d09e82ed41e84da6136b80a0991ab8423d16a5162bd`。21 payload 加 manifest 是 candidate 22 件；过程只再新增 receipt 1 件，共 23。两段 Git diff 精确等于这些新增路径，均限两个 `d2-canonical-interface-design-r2` 前缀，无旧件修改。

新独立 proof 对旧 205 逐件比对 current=6b94 Git=bytes/SHA，其中 176 另与 0841 Git 相等，canonical 原 29 独立计数；R2 前 22 current=candidate Git=bytes/SHA，过程第 23 current=process Git=bytes/SHA。开始所见 `AGENTS.md` 既有 M、原 R1 14 个审查文件 untracked 都没有由本审改动。本审只 exclusive-create `docs/reviews/I05/d2-canonical-interface-design-r2/independent-r2-*`；不 stage/commit/push，不写 index/HEAD，不将 root 后出合法审查文档视为固定候选污染。

## 17 类 / 86 本地声明的实质核验

来源纯目录与 R2 field map、17 蓝图三者逐类逐字段比较，覆盖 class/source pin、decorator/base 原语法、字段顺序、annotationSyntax、defaultSyntax、sourceLine、pureFactPointer 及蓝图 requiredFields，而不是仅比较 17/86 总数。

| 类型               | 本地字段数 | 类型                | 本地字段数 |
| ------------------ | ---------: | ------------------- | ---------: |
| SourceRecord       |          4 | TermInput           |          5 |
| InputLocation      |          4 | ProfileLimits       |         17 |
| Variable           |          1 | Triple              |          3 |
| Comparison         |          3 | RuleSpec            |          8 |
| Catalog            |          3 | BindingMatch        |          4 |
| ComparisonEvidence |          5 | HeadEvidence        |          2 |
| PreparedFiring     |         11 | PreparedFiringBatch |          5 |
| ProfileValue       |          4 | Number              |          3 |
| Calendar           |          4 | 合计                |         86 |

原 7 helper 目录 / 27 行与新 17 目录 / 86 行交集准确；原已有的 13 条非 null 注解逐值保持，另 14 条此前未知注解得到明确细化。新增 10 类型目录 / 59 行；P2 另增 2 目录 / 3 行。因此有效视图为 `52-7+17+2=64` 目录、`263-27+86+3=325` 行，无重复 ID；原其余 236 行来自精确固定旧文件引用，未以部分重抄改变原行。`replaceOnlyRowIds` 正好等于 27 交集。

所有 17 个蓝图逐处 `NEW-PROPOSED-NOT-ADOPTED`，原 wire discriminator 和 adoptedAdapterPin 全为 null，approvedSet 等价性全为 false。17 个本地声明不能证明 projection/probe/material 注册集合相同，source class/path 也不是 recordType 字面。Q01 仅字段/type/default/顺序目录子项收到，注册、tag、实际安全 adapter 和合法语义词表仍待原 owner/root。

默认文字与实际值没有混淆：JSON null 表示该声明无默认语法，`None`、`False`、`1`、`()`、`PROFILE`、数字与 `''` 都保持字符串语法，不求值、不补 actual、不进入旧 preimage，不当费用 cap。Number.denominator 的 `1` 不补丢失字段，也不证明非零/有理数规范；ProfileLimits 的 17 个默认不授预算；PreparedFiring.source/revision/definition_digest 虽可为 None，声明无默认的 null 也未误抄为字符串 None。str 不补 enum。

ProfileValue.value:object 与 domain->value 关系仍阻断，明确传播至 ComparisonEvidence.left/right、PreparedFiring.comparisons、PreparedFiringBatch.firings。native_result:dict、其他未细化 tuple/dict/object 仍 pending；未用通用 MapValue、反射、getattr、**dict**、repr/str 填洞。完整 adapter 未闭合时保原 byte/preimage/sidecar、layout-blocked；没有原专用 wire 时不制造 raw 或用 null 冒完整成功。

## IR1-P2-01 两触发的独立处置判断

**A：selectedFacts wrapper 已关闭。** `type-field-map.json:3355` 新增 `api:legacy-provenance/selectedFacts[*]` 的 `triple`、`sources` 目录；两行均 requiredWhenParentInstanceExists。`:3455` 明列外层 selectedFacts[i] 到 wrapper 的 parentField/childDirectory，再从 wrapper sources 到 selectedFacts[i].sources[j] 的三个既有 source 分支；三 target 目录实际存在于旧设计。全 i/j、原序、重复、尾项均有明确保留规则；unknown kind 仍全保并 layout-blocked，不把三个已知分支视为穷尽 enum。`:1058` 的新 nested blueprint 一致连接。它没有将非空 wrapper 的两个字段藏在通用 extra blocker 内。

独立声明例使用两个 wrapper（同 triple 重复）、六次 source 出现，覆盖 asserted/rdfs/rule、重复 asserted、第二 wrapper 与最后 rdfs，另以 inputs/basis 的尾项、false/null 作为保全标记。按明确的全 i/j 链接，每次完整原值都有落点；裁掉 wrapper 2 或 source 尾项、去重或只验首项都违背 R2 文字。这里只判断目录/保全义务，未声称这些人造值符合原业务语法，未运行 serializer。

**B：known optional mutation 已关闭。** `type-field-map.json:3384` 另加唯一 mutation 行，requiredWhenParentInstanceExists=false；独立核对原普通 13 键仍与授权 API facts orderedKeys 全等。`:3474` 明确 absent 不补 None/not-reached；present 保完整原值；present null 只保全且区别 absence，nullable/合法性未知，没有产品 accept/reject expected。未知内部仍 layout-blocked，坏副本/原 expectation/未 reissue 标记仅按实际返回保留，不猜内层键。其余未知外层 key 仍保 raw 并阻断完整性。

独立声明例分别保存 `{}`、`{mutation:null}` 与带 syntheticUnknownInner 的 present 对象，三个分支只作 optional 片段，明确不是缺了普通 13 键仍获产品合法性通过。该 delta 不把 mutation 变成第 14 个普通必有键，也不以 null 例签 nullable 合法性。

原 R1 949 结构检查为 0 失败仍不能排除已发现的语义遗漏，R1 Fail 保持原结论。R2 两个修订足以关闭原 P2 的指定触发；未观察到原件实际丢值，不把设计遗漏追认为已发生 runtime loss。

## 继承与未决边界

旧 14/15 字段继承、RootRef 五字段及 kind:str、ReadonlySequence.native_kind；production flat 与 probe nested/full-module recordType，hex/base64 与 material codec；旧 16 摘要、catalog/canonical_string/未求值 IMPLEMENTATION、8192 Python 字符及尾片、scope/profile JSON 选项均由未改动的固定八设计继承。R2 没有新增旧 recipe、新 tag、自环或重算原 source/definitions/payload/rows/catalog。这里只验 delta 与固定身份，不重演旧 codec、算法或摘要/切片证明。

identity-policy 仅原六键外部 pin 的角色/链接：receipt.runId 对应先登记 caller attemptId；child ID 只首受信 context。没有读 policy 正文、回填旧 null，另 30 字段保持 CR-R/CR-H。Q01 残余注册/tag、Q02 闭值/domain/native_result、Q03 原 codec、Q04 安全 adapter 采用、Q05 原 lexical/preimage、Q06 live verifier、Q07 registry/collector/layout、Q08 source/runtime/预算、Q09 安全异常均有最小纯合同请求，actual pin 为 null、sourceFollowing=false。来源、issuer/capture、17L、whole-H/SQLite HOLD、两 OS/真人/CI/develop 不因目录接收开启。

## 实际验证、失败与限制

新独立 `independent-r2-check.py` 先 AST parse/核 stdlib import 面，再以实际 `/Applications/Xcode.app/Contents/Developer/usr/bin/python3 -B` 运行，保 `PYTHONDONTWRITEBYTECODE=1`。真实 exit0，2419 个有限身份/字段/引用/门禁断言，0 失败；5 个保持数量的元数据反例及同 86 数量的尾字段丢失均可识别。没有运行作者 checker、原 103/383/949/1241/417、原 model、第三方 schema engine、产品/旧 codec、pytest/npm/build/package/install/network/DB/native/GUI/Goal，也无外部消息。

2419 是独立有限静态证据，不是完整性、原语法、runtime 或 adoption 的证明。实质结论来自上文对源声明、已知父子链接、可选 presence 与 pending 传播的逐项判断。650604B 原 stdout 保留全断言/86 字段证据/精确 Git argv 和身份，便于复核，未包含运行业务数据；不将原 Git blob 大内容另行出版。Git blob stdout 绑定 immutable ref:path+bytes/SHA，所有 Git stderr 独立保 base64。独立 checker 顶层 stdout/stderr 原文件分开，execution 含真实 exit、bytes/SHA 与 stderrBase64，原流不 format。

本审初期一次只读身份脚本将 receipt 路径误写为不存在的 `type-directory-r2-receipt.json`，真实 outer exit1，未写文件；实际名由同次先前 Git delta 明示为 `type-directory-r2-process-receipt.json`。后来正式独立 proof 对正确名成功核验，不抹去此前失败。早期直接工具输出并未逐条分流持久化，不能事后伪造 stdout/stderr；少数大显示截断已分段补读。详细边界见 `independent-r2-bootstrap-boundaries.json`，失败与截断保留于原工具转录。完整 205+23 字节保护将在封口收据中再核，不扩内容读取。
