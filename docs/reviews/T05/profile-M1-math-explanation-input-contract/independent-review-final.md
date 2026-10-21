# M1 独立审查最终局部复核

Reviewer：`/root/m1_independent_review`。在初审完整数学/来源/fixture审查后，只复核P1/P2对应修订及字节，未重复无关数学检查。

**P1与3项P2均已关闭，无剩余文档阻断项。** 初审意见及首稿保留在independent-review-initial.md、review-first-C-inputs.json和两份review-before-P2原件；author-method保逐项处置。

- 11个SHACL输入保持真实支持的targetClass NodeShape→PropertyShape结构。
- 两个label结论与golden均改canonical `"ok"`，三个head分别绑定准确conclusions pointer。
- 独立数学input corpus已分离，各family内ID唯一，未含expected、Number/Calendar、数学结果或reason字段；逐项核对operand与对应golden一致。
- date inclusive补齐core-only违规和明确采用date扩展后等值conforms两种条件预期；没有冒充当前actual或新增政策采用。
- assembler只从独立作者常量生成输入，未读golden文件或产品输出。

独立复核实际字节（与review-P2-candidate.json七项逐字节核同）：

| 文件                            | 字节   | SHA-256                                                          |
| ------------------------------- | ------ | ---------------------------------------------------------------- |
| math-operand-inputs.json        | 490953 | 9f198fcefa50ca30a87acfa3cef021360100a9dea3fb5ed829c5f62fc02b0d9f |
| supplemental-graph-inputs.json  | 5962   | dc57792093204d85c2e54471c271965c40b7ccd7e5cd6f4614173e1497c332f6 |
| consumer-C-inputs.json          | 8505   | eeab821ccd71d55eed425a08b34d07648e623c0aa34eb2eabf66b839bbb426f6 |
| consumer-C-goldens.json         | 8163   | c25e7afcc593a7be09fc8b2ca29af9cff28a7a1e030a13b98aa5e7d88d596440 |
| explanation-goldens.json        | 11584  | 68bc6848ad05b7cca01f37368a15b9e961a78a6a877b841f08cafa2a2fba36d9 |
| term-error-goldens.json         | 11426  | 9737eb1a0113ac22d38e03cb058f2cce0a22319797456a2d6f8886487f598986 |
| assemble-independent-goldens.py | 16526  | 6084cb736a2d9a71743349196641e3716da56d24bfbc0b07fbd66498c88f39e6 |

初审已核31 fixed raw/ref/SHA、26 future windows、486域槽、648numeric、38Number、15Calendar、5混型关系及差、五graph/Catalog/四finite witness规则、原census及16实际源事件映射。未发现数学golden错误、来源冒充成功或需改七quality机制的问题。

本次仅静态文件、JSON、算式与hash复核，未导入/运行产品、parser、比较器、reasoner、Validator或测试，未写文件。实际binder、producer、restore、selected及Validator运行仍待根获准窗口；本结论不关闭原Goal/83项/父验收。

复核临时脚本首次因当前python3不支持`zip(strict=True)`退出1，改为先核等长再zip后退出0。无文件写，不是产品失败。初审算式SyntaxError和作者首失败也均在author-method保留。
