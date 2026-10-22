# T05 date 首错预期的既有声明来源收件

本记录只绑定既有回归要求，不制定新日期政策或证明固定库对任意词法的分类。已采纳有限UTC date政策和Q6不变。

总控实际读取固定6891a5842302859a531cf82767c5a482417bc274的 packages/engine/tests/test_semantic_shacl_date_policy.py 参数和断言 L275–313、reject helper L183–187，核整文件26924B/SHA bd8e332a1b55ebdf183f1effdd37126a61233931edaa8d2239e0a20d9179b765；并全文读固定f79a29f596b2444cba542a906c91727869014886的 docs/reviews/I05/shacl-date-policy-implementation/independent-review-6891a58.md，9809B/SHA15f35bcf7401d4f353036ae58d5c1aff574bd37c4d5e7fb90813c81e5dfaca2a。

该旧独审记载日期预期首候选到末候选未变。原I05另只读核首候选1e91ad6对应AST一致且首跑在提交后；总控没有重做该时间线核验，不冒作直接观察。

| 固定输入ID中的N | raw lexical               | 已声明bound首错                      | 已声明value首错                    |
| --------------- | ------------------------- | ------------------------------------ | ---------------------------------- |
| 7               | 2000-1-01Z                | INVALID_LITERAL_LEXICAL@parse-shapes | INVALID_LITERAL_LEXICAL@parse-data |
| 8               | ２０００-01-01Z           | INVALID_LITERAL_LEXICAL@parse-shapes | INVALID_LITERAL_LEXICAL@parse-data |
| 9               | 前有一个空格的2000-01-01Z | INVALID_LITERAL_LEXICAL@parse-shapes | INVALID_LITERAL_LEXICAL@parse-data |
| 10              | 20000101Z                 | INVALID_LITERAL_LEXICAL@parse-shapes | INVALID_LITERAL_LEXICAL@parse-data |
| 15              | 2000-01-01z               | INVALID_SHAPE@date-bound             | RDF_TERM_INVALID@date-value        |
| 16              | 2000-01-01T12:00:00Z      | INVALID_SHAPE@date-bound             | RDF_TERM_INVALID@date-value        |

ID为 utc-date/lexical-N/{bound,value}，共12项，旧reject断言另要求ValidatorCalls=[]、result=None。总控允许T05将其作为 pre-registered legacy regression assertion 来源绑定，不能把旧check实际输出或新版probe输出当预期来源。T05已回报绑定完成；最终候选及独审仍待收件。

65e31d设计对illtyped优先仍是条件合同，没有另外逐项枚举固定库分类的独立纯规范。更强库分类证据仍pending，须与上述已声明回归预期分开；不因允许复用旧断言而改写为已证。预算准入及actual child allocation缺口独立保留。
