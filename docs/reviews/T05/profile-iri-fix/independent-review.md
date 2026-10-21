# IRI 最小修复独立实现审查

结论：**通过本次两路径最小修复的独立实现审查，无剩余实质问题。** 只关闭固定机制对合法Unicode空白IRI的过度拒绝；不将其说成完整IRI parser、真实图匹配执行器、包内采用或T05/I05父产品完成。指定同候选外审/集成/CI/正常合并等门保留。

## 固定范围与规则

工作树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T05-profile-iri-fix`，分支 `feature/weekly-t05-profile-iri-fix`；base `1e3e0ee1d9d5b70f1f59233d0a3c64f6d85fd2cb`，受审/current HEAD `dbb6b36e9259aa79a1fd908b5cfede3064f0c074`。实际Git diff恰两路径：rule_terms.py和新test_quality_profile_iri_boundary.py；当前两文件与固定Git blob一致。旧20路径中其余19项逐个对base/ref/当前树原字节相等；21项实际hash见 independent-input-binding.json。本审未改实现/测试/依赖/配置，未提交、推送、切分支或触旧batch/oracle树。

实际全文读当前AGENTS15852B/SHA `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`（有意未暂存）、authorization.raw.md4286B/SHA `60e0b72f6e15ad9a853f26bc30b187d61771a3d467614eb571ae31dbb506d097`、common17891B/SHA `e437121a08053544c2a09151ac5183baf15b5fa67a3a604891aaa9e77ba971b0`。授权中的新树/两文件/原Goal/旧树不改/无桌面/费用边界适用；未操作审查应用或凭据。

## 规范与代码判断

实际只读官方 [RFC3987 §2.2](https://www.rfc-editor.org/rfc/rfc3987.html#section-2.2) 的 iunreserved/ucschar、path/query/fragment组成；ucschar从U+00A0起的若干区间包含本次涉及的18个Unicode空白。[RDF1.1 Concepts §3.2](https://www.w3.org/TR/rdf11-concepts/#section-IRIs)要求绝对IRI、允许fragment，并按精确字符串比较，比较时不得额外规范化。该最小门不应以Python全Unicode isspace直接替代这些语法规则。

rule_terms.py:90–100仅把原空白条件限为ord(c)<0xA0且isspace；原scheme/显式禁字符检查、UTF8和work预扣、term字节门、输入类型/location/安全错误、签发/身份路径及其他literal/numeric/calendar逻辑未变。新增ord是已预扣逐字符扫描内的常量操作。没有新增parser、Unicode normalization、percent转换、大小写折叠、DNS/网络读取或第二图matcher。

Python3.12.12/Unicode15.0.0的标准库独立枚举实际确认：新放行的isspace集合恰18个（U00A0、U1680、U2000–200A、U2028/2029、U202F、U205F、U3000），全部处于RFC3987 ucschar；U0085及原ASCII空白仍在低码点拒绝门。这一枚举未import产品，仅核修复涉及的码点集合，不是完整IRI符合性证明。

完整IRI组件/语法仍由已验证上游入口提供precondition；旧最小门对其他不完整语法的覆盖没有被本审扩大成全RFC验证。Q6/profile1既定IRI政策未改变；实际未来采用须新ref/hash，不沿用旧1e3包或旧通过。

## 回归质量与实际验证

新增203行测试已全文读。覆盖18合法空白在路径/query/fragment位置的公开parse_value/term_key原值；普通Unicode/emoji/fragment；NFC/NFD、scheme/host大小写、percent编码与字面字符、percent十六进制大小写及fragment差异均保持精确身份。compile_rules/evaluate_bound_batch使用真实本机制入口，在catalog/常量/给定binding/when/输出中保留Unicode原值，并实际核比较判定、全部head、facts与proof leaves；这是给定binding机制，不证明图搜索或producer权限。

负控覆盖原ASCII空白、U0085及全部原显式禁字符；公开parse维持INVALID_RULE与真实location，受信binding损坏在evaluate转Internal且不回显原IRI；scheme/相对fragment/surrogate拒绝不变。work/input/term限额及多字节9/10边界实际回归；外来TermInput替身不能执行callback。

本审实际命令：

`uv run --frozen --no-sync pytest packages/engine/tests/test_quality_profile_iri_boundary.py -q`

真实subprocess exit **0**，**131 passed in 0.28s**；stdout180B、stderr0。原argv/cwd/ref/returncode/bytes与hash在 independent-tests.receipt.json，原输出在 independent-tests.stdout.txt/stderr.txt；未装依赖、未复跑全check。

另实际命令：

`uv run --frozen --no-sync python docs/reviews/T05/profile-iri-fix/independent-ucschar-audit.py.raw`

真实exit **0**；stdout902B、stderr0。脚本、原输出和receipt保留，包含所用Python/Unicode版本与完整空白集合。未对测试IRI执行DNS解析或网络请求；公开规范读取与产品运行分开。

## 旧红/首失败与本审边界

读取owner保留的old-red-inputs.json：旧terms5909B/SHA `8f58a68b896a62443ab3681c29802905d5ff1e010a944d32eb07f988319cc19a`；初始新测试7622B/SHA `8f64e9117a982605da9e17575cc635a4949c0ca53ce26e3f0ef03f5cd5a1e198`。old-red日志终态74failed/57passed且exit文件1；owner修后原日志131passed/exit0，受影响回归1539passed/exit0。本审读回这些来源，没有重跑旧红或把owner终态改写成本审执行。初始测试与当前7621B不同（lint删空行），当前实际131运行绑定的是固定dbb最终测试，未冒充字节相同。

全npmcheck/sourceverify由作者执行并封存；本审不重复、不预判其最终结果。必要包内/D2及I05采用、真实图入口/来源/producer/持久化/selected/平台与原完整FR/父Goal等均不在此次通过内。没有GUI/Electron/e2e/native/HMR、外部模型/新增付费或旧树修改。

## 受审文件hash

- rule_terms.py6176B：`218c4790e9b35236e393407b5b4e0207890d46fe3ea48a9a69e26aa08ddba1d1`。
- test_quality_profile_iri_boundary.py7621B：`4ed40d6b6247200886f0ed774a5e6c9cfb1cd8ccbeff05f26ffcdd1e5edcde88`。

发现：无需要修复的P0–P3问题。上述有限范围通过，不等于后续正式采用或完整产品验收。
