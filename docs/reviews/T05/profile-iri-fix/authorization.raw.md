# T05：固定机制对合法 Unicode IRI 的误拒修复

2026-10-21，总控批准原T05会话 `01a15bce-021c-74e0-a7ac-a899380b424a` 处理一个具体机制缺陷。不是采用更窄的永久支持范围，不改已采用Q6政策，不重问规范版本；I05当前准确unsupported仅是未采用修复前的临时未完成状态，不能据此关闭原完整支持验收。

## 事实与规范

根已静态读取固定 `1e3e0ee1d9d5b70f1f59233d0a3c64f6d85fd2cb` 的 `quality/rule_terms.py:87–95`：`iri_minimum`在有界UTF-8/工作计费之后以 `c.isspace()`拒绝所有Unicode空白。I05两实现agent独立静态报告，该门会拒绝RFC3987允许的U+00A0等字符。尚未实际执行反例，必须先保旧红再修。

根实际查阅主规范：[RFC3987 §2.2](https://www.rfc-editor.org/rfc/rfc3987.html#section-2.2) 的 `iunreserved/ucschar` 包含U+00A0起的范围；[RDF1.1 §3.2](https://www.w3.org/TR/rdf11-concepts/#section-IRIs)使用RFC3987 IRI语法且允许fragment。因此不能把所有Python Unicode whitespace都当不合法IRI。仍由I05实际RDF入口负责完整语法/结构验证；此处修复最小机制门过度拒绝，不另造完整IRI parser或放宽ASCII空白/已有禁字符门，不网络/DNS访问、不额外规范化/转义/修复输入。

## 精确树和文件

核空后新建 `.worktrees/T05-profile-iri-fix`、`feature/weekly-t05-profile-iri-fix`，从固定已根收口的私有机制快照 `1e3e0ee1d9d5b70f1f59233d0a3c64f6d85fd2cb` 派生；记录实际HEAD/分支/基线。它不是新的批准远端集成基线，最终集成仍按实际develop/同版门处理。未知既有树不覆盖；原T05树f9/c1a文档与原1e3/20原件、oracle候选及所有历史保持，原Goal不重建/不假称恢复或完成。带入最新AGENTS78df/common e437操作政策，不stage保护文件。

仅两条产品/测试路径可写：

1. `packages/engine/src/ontolearn_engine/quality/rule_terms.py`：只修 `iri_minimum` 的Unicode误拒，保精确类型/位置、已计预算、字节/长度门、scheme与既有禁字符/错误类别、term身份/发行与其余数值/日期/字符串逻辑。
2. 新增 `packages/engine/tests/test_quality_profile_iri_boundary.py`：实际边界回归。

另可新增 `docs/iterations/T05/profile-iri-fix.md` 与 `docs/reviews/T05/profile-iri-fix/` 的必要旧红/修后/首失败、独审、Git/资源/输入绑定。不得改其他原20文件、夹具expected、依赖/锁/公共schema/Store/worker/desktop/build/CI或批量复核实现；实际必要额外改动先给反例和最小路径，不借本授权扩大。

## 实际交付与验收

先在原固定机制运行明确合法IRI（例如HTTP path中U+00A0，另含合法Unicode和fragment）并保存现误拒，准确区分静态见证与真实运行。新测试覆盖该合法Unicode子集、普通Unicode/ASCII/fragment、相同字符串term identity及不归一化、ASCII空格/tab/换行和现禁字符仍拒；不以仅测试某个flag证明真实函数已修。经实际公开 `parse_value/term_key` 及编译/执行路径核同一IRI原值保留，错误、预算边界与安全参数不回显原文。

修后跑受影响专项/原机制回归、正常完整 `npm run check`、必要source验证及独立实现审查，保首失败和实际命令/退出终态/完整输入输出；冻结只两路径产品diff的本地候选，交修改与不变七模块的bytes/hash、真实patch及归档。需要打包验证的实际影响仍留I05同组合候选D2；本源码修复不冒称包内已生效，source可用/新包/目标平台分开。无变化旧项目不因接收记录而重测。

原PROFILE/1和mechanism-budget/1的语言政策不变，这是既定语义的bug修复；新实现按真实ref/hash区分，不沿用1e3旧通过或旧包。root核验新候选后另精确授权I05采用该terms原字节，I05不私改七模块或临时monkeypatch。批量复核提案可以继续独立评审其输入前置，未获实现权，不将本修复混入未知batch API。

禁止本机GUI/Electron/e2e/native/HMR/审查应用、提前push/PR/merge。完整T05/I05支持面、图入口/来源/producer/持久与selected预算、指定双模型同版新审/CI/正常合并/远端及完整父Goal继续保留。
