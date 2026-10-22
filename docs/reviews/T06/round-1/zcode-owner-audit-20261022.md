# ZCode S1 裁决与过程核验

2026-10-22。指定模型裁决为独立 S1 通过，原报告19238B/SHA bf381a82cf16bad608d8c15ca1a8e928a504d4689ecf0537a0249eee80a58638按原字节归档为zcode-glm53.md；原文及最终答复不改写。真实turn.completed、持久main_turn stop最终消息、12项受审源前后匹配已核验。MiniMax也已真正终态，但有两项P2、结论为有条件通过，不构成双无阻断Pass或推送许可。

## 报告意见处置

| 意见 | 本线核对与处置 | 当前状态 |
| --- | --- | --- |
| P3 指纹文档应点名排除sequence | 实现与既有测试已按事件内容身份排除sequence，interface.md现有“输入序号不参与内容身份”与此相符；接受明确字段名的文档建议，在下一必要产品候选统一补充，不改正在受审12文件 | 接受建议，未改冻结来源，尚未实施 |
| P3 适配动作属性值原样JSON标量边界 | 当前固定九例适配未承诺完整RDF codec；接受在t09-adaptation.md明确动作属性值原样JSON标量、由T05正式codec后续统一的建议 | 接受建议，未改冻结来源，尚未实施 |
| 信息：rdf:type保持集合基数 | 与既有兼容审计边界一致；保留集合语义，不新增代码改动 | 已核对，无需修复 |

上述处置不把未实施建议写成完成。若实际修改受审文档/接口、实现、测试、依赖、验收或base，仍按原规则生成新候选、必要验证及双方全新同版完整审查。

## 原始过程计数纠正

报告及最终消息称“两次Mimosa拦截”。官方本session脱敏modelIO完整44条记录的原文提取显示58个唯一tool call IDs：54个有工具执行日志，另外4个在PreToolUse前被拒。实际为一Bash加三Write，不能用报告摘要替换raw事实：

- Bash `call_67914d26ddab4f49bfafb495`：拟将固定作者脚本复制到/tmp并运行，钩子以“Bash直接写源码会绕过Write/Edit扫描”拒绝。输入命令与拒绝结果已保留。
- Write `call_910c19fab36745cdba47bf98`：拟写/tmp/T06-zcode-glm53-negative-probes.py，被报SQL注入第91/110行，未执行。
- Write `call_7feca54864624a23b076b5bf`：同一/tmp目标的调整版本，被报第91/109行，未执行。
- Write `call_895e85ce6771468ba1b1e6d2`：同一/tmp目标的再调整版本，被报第91/108行，未执行。

本线已读回四个完整拒绝原因，保留各输入为.txt证据，不执行。被报位置是脚本自身execute(req,facts)包装调用；该包装只调用prepare_events/plan_behaviors，导入copy/sys/本树behavior，当前静态可见内容没有SQL连接或SQL查询。这是owner静态观察，不改平台拒绝结果，也不把后续stdin执行自动追认为过程合规。后续stdin/作者脚本复现及其工具原始call/output正在一并归档；本线没有重试或换路重新执行被拒操作。过程偏差与完整raw覆盖须交总控核验，尚不关闭过程门。

## 原件与覆盖

官方完整modelIO原件仅私有保存在outputs/20261022_t06_external_review/zcode-model-io-extraction，不把headers/系统提示/思考内容输出或放Git。只解析本session，不读SQLite、凭据或其他session，不创建runtime/恢复turn。最终消息来自第43行main_turn，finishReason stop，非末行session_title。其精确偏移/hash见zcode-completion-receipt-20261022.json。

三/tmp验证产物已原字节保存：九例probe77789B/SHA d18e5059394b11f6f783d4247c8e4f074a102a58d5ef3d48c3272fc248339c9e；完整diff493640B/SHA e1b08e5c89b72f4d8a0a7e1ca57feadd91ced235301d1096fdfd07d8e5d507dc；作者复跑JSON218068B/SHA43efd27fbbc201b69e42b6808e739524f24acc0afae22aa4f35566d763db7af2。作者JSON的规范化语义相等与原字节不同分开记录，不误称逐字相等。

完整工具包现为 evidence/zcode-original-tool-evidence-20261022.tar.gz，918318B/SHA32c7b83753b572d085ce0703208e2f82f587c05d695cbd3509cb16234cb330c4。父线已逐一读回439个regular成员，与来源字节全等并核对manifest；包含58工具调用所有值版本/出现位置、拒绝与后继stdin、实际npm全输出与最终消息，排除63MB modelIO的headers/system/思考。两stdin实际为首跑20PASS/2FAIL/exit1，修正后5PASS；不得把首败抹成全通过。122专项命令自带tail，只有管道后完整记录，不存在可补造的管道前完整stdout；运行时argv未捕获。具体来源/偏移/hash和archive理由见对应readback JSON。

## 原作者补正与owner输入差错

原作者在同一session后续正确query `01a162fb-827f-7fb2-811c-ebea3c4e4037` 已于2026-10-22T09:46:56.411Z真正completed。独立补正原件 `zcode-glm53-process-addendum-20261022.md` 为9494B/SHA b9c8277021b704dfab265a55f3cb84824b9f34a4e69c3be40fd7a66fd1528f1d，已全文读取、按原字节归档；明确四拒绝的类型/未执行、实际被标记行、首败/修正链、原26应为27条结果，原始报告和原最终答复保持。作者维持原S1结论，不能据其自我判断替代总控对过程的审核。完整补正终态/新最终答复及17个新工具记录由独立收证核对。

owner在准备补正输入时误用多行typeText，导致部分内容提交为新turn。只取消该误提交query `01a162f9-ae29-7e17-b5d6-c7fcf0a59b6a`（09:38:12.678开始、09:38:52.007 cancelled，processing_input），原审查turn0和其他任务未停止；随后清理草稿，以format:text粘贴完整7313B/SHA c27fa8bcbc4f45e15df700bfa86b6df07027585cb31e0af9680f566e9b6b92a4正文，提交前和原生消息复制后逐字匹配，才产生上述正确query。此操作差错已向总控即时披露，原工具20 calls/40行及精确源行/偏移/hash保存在私有outputs/owner-cua-correction-raw，不以纠正后的受理掩盖先前错误。后续不再使用多行typeText提交审查。

独立补正收证已完成（ui-zcode-dispatch-verification/minimal-manifest.json）。新最终答复2339B/SHA a241a9652815cb6894ff1a89d6a3449e0958e7ef10a9e4a3c88242a3448be689来自第55行，17请求为12Read/4Bash/1Write；其中含一次新补正文档prettier检查，故final“未重跑任何命令”字面过宽，准确边界是未重跑原产品验证或被拒探针。误提交取消轮另有一次工作区元数据Bash请求，无最终答复，不声称零工具。两项已独立核对并向总控披露，原报告/补正/最终答复不改写，过程门待总控处置。
