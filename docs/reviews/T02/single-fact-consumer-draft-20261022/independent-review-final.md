# 单事实 typed 消费草案：独立修订复核

2026-10-22。固定修订 `bb23457bc55fb68816f25b884f4b1a981e53e920`：**通过，仅draft方案层**。初审唯一P2已在文档语义层关闭，实际差异未引入新的实质问题。此结论不授供方采用、实施或产品运行，不替代后续真实同版候选的指定双审或完整父验收。

## 实际差异与关闭依据

本次直接读取e976→bb234完整prefix差异及新增disposition；相对前轮只修消费语义、追加PRD输入、保全初Fail及记录处置。supplier-requests逐字保持e976版，分页问题沿前轮已读回的两行修订结论，不重审其余正文。

| 原问题 | 本次实际修订 | 结论 |
| --- | --- | --- |
| P2：domain/range被误作事实值保存门 | consumer-matrix第24行只要求既有dataProperty与新canonical literal，原domain/range声明完整保留，不作实例类型/值合法性判据；第29行新增PRD688/970语义护栏，明确不新增prop.range与object datatype比较；F11删除“声明range不容新O”，限获准模型/decoder实际词项编码、支持datatype、ill_typed和语言检查 | 文档层关闭 |
| 重复页与受控重试歧义 | e976已把拒绝对象限定为确认材料重复拼段；受控同页重取依真实供方合同并计同CostSession。bb234不改变该修订 | 维持关闭 |

护栏明确保留声明自身支持域、类引用等既有结构检查，没有把删除错误range匹配门扩大为绕过C5校验；不能仅因range=xsd:string而新O为canonical integer literal就拒绝，其余真实守卫仍适用。该例只说明防误拒语义，不是正向supplier fixture、成功返回或整链Pass。真实SHACL验证仍需独立获批合同，没有在此预定新的保存阻断。

这与前轮已静态核过的C5 model事实一致：range声明支持域和词项datatype/ill_typed、property/literal形态有检查，事实新值没有与prop.range相等的额外门。本轮未重新读取或执行产品。

## 新PRD输入与历史保全

仅核本次追加的PRD输入：固定 `5f910b52c69d86a1076b2032e5d3c63e715947f3` 的 `docs/prd/PRD-本体学习与落地Agent工作台.md` 为93584B、1255行、SHA256 `7586b2c4784b8c691d510e2be16310ed551e110af6df96b7c6aeb86152f60fbb`，当前字节等于固定Git并匹配readback。语义只读取header第1–8行及684–691、967–973行，确认V0.6、domain/range为RDFS推理且不是数据校验错误；未声称重新全文审读PRD。

初审原件在固定bb234及当前文件均为8796B／SHA256 `db585c8947c759466842a91468f2340f22480ba07e79278f6635ebb16622d573`，与本审前次写出字节相同。db77初Fail、e976仍有P2的历史判断未倒填。disposition本次仍写“待固定修订独立复核”，没有提前伪称通过；本报告给出实际终态。

## 范围与未验边界

其余范围沿db77完整初审：C1–C8、完整metadata/全部支持/原factID、普通Preview非来源认证、旧Store2形状不能减字段凑来源、新S1/S2、首读前可信CostSession及失败/分页/历史/新undo预算、22未来case、10供方槽、owner路径、D/M/P/F层级、四P3分流和冻结Goal边界不变。

本次仅静态Git/text/stdlib hash与JSON，未重跑8/9输入全核、34/130/825审计或产品验证；未import、测试、探针、SQL/DB/JobStore/native/GUI/模型，无新fixture/API/schema/writer。仅新增本报告，未改原主文、初审、源码或根控制文件，未提交。真实新供方与逐路径采用、adapter/原事务机制、App/真人、父FR及CI/合并/发布仍须各自批准与运行证据，不能沿用本次方案Pass。
