# SHACL 非法整数独立文本入口

仅本组件窗口有限通过。continuation `a15f1478e398fb3b58fd60b1421a9cad04fdb430`，固定产品 `91e98074a334931648e9b7c8f58a3b5e8f93a642`；日期政策、正式execution/Store/Job/selected接线及父功能验收不在本次结论内。Q6沿用已采纳结论。

## 行为与范围

`validate_shacl_text(data_text, shapes_text, *, data_policy, range_policy)` 两个policy均须显式提供。data_policy只接受strict、integer-illtyped-report-v1；range_policy只接受legacy。未知策略固定SCOPE_SELECTION_TYPE_INVALID。返回entryVersion=i05-shacl-text-1、两项实际policy和真实report；旧SEMANTICS_VERSION=i05-finite-6及旧报告结构不变，无cache/公共参数接线。

唯一宽点为数据object、精确xsd:integer、ill_typed is True，保原lexical/datatype/三元组，shape仍严格。真实target和constraint决定结果，无目标或无约束可conforms=true。旧parse/query/reason/check保持strict，日期bound保持INVALID_SHAPE且Validator0。没有全局转换表、DAWG/parser/logger/constraint-map修改、吞错继续或补造violation。

相对continuation恰一改semantic.py、一新增专用测试；145受控、143只读。旧1238过程只冻结Git mode/type/blob身份，不重审旧257MB内容。最新操作AGENTS及common全文读取并归档在inputs，旧Git AGENTS保持原字节；操作规则更新不改变产品决定。

## 实际验证

最终03正常完整check exit0：1125项TS、5060项Python通过，44项既有跳过；新增70实例，原77 DAG和26 shape在同一次完整运行。新入口78份观察=14次真实Validator调用+64次前门拒绝，真实结果4个true/10个false；原26 shape=9次调用+17次拒绝，覆盖重叠不相加为新用例数。actual-report-audit逐原始RDF report核完整六字段和conforms，未伪造BNode ID或缺省value。本轮未开启D费用大快照采集，不外推费用或性能结论。

另04 verify:sources核12来源exit0；05产品diff检查exit0。06完整暂存空白检查exit2，仅原始patch/首失败trace的空白字符；三原件及06检查自身stdout原字节保留，四件精确raw例外见raw-whitespace-exceptions.json。07检查其余全部暂存文本exit0，无产品或活动代码例外。所有验证记录完整argv/cwd/env/开始结束/exit/timeout和145项来源前后身份，新树独立node_modules/.venv及临时目录。无GUI/native/e2e/HMR/外部模型/付费/push/PR/merge。独立审查仅新入口与本轮证据，报告见independent-review/final-91e9807。

## 首失败与修复

首候选be61c928的01完整check实际1 failed/5051 passed/44 skipped/1 warning：非法IRI在_terms的n3排序先抛原始库Exception。首候选、双流、首轮70份观察及首审不通过报告原件保留，没有改预期求绿。

91e9807仅在新文本入口启用排序前的实际URIRef/literal datatype IRI检查，按原IRI字面边界固定拒绝；旧API调用顺序不变。保原失败测试并新增subject/predicate/datatype/shape-path×两策略共8向量，再以新候选完整check验证。坏decimal的既有RDFLib序列化warning保留，未通过全局logger/warning设置消除。

最终来源、过程成员和原件hash见final-manifest.json、validation.json；manifest自hash由交付回执外部绑定。正式执行链仍有严格facts/scopes/selected门，本组件通过不等于正式链支持非法整数。
