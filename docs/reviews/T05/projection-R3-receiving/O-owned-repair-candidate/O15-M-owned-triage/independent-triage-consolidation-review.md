# O15 M五项triage汇总与保全独核

2026-10-23。**限定汇总/保全通过，未见实质遗漏或错配。** 已对照本目录README、five-medium-triage-register、契约/Job与IPC原稿、owner测试/CSP报告及其独审。只核文件与结论对应，不重开源码或产品triage。

五行精确对应原§8.1–8.5，均保留原[中]、reported-open-awaiting-controller-and-unique-owner-adjudication；B150 NotPass、全部15外部流程open、§3.4未读保持。摘要没有利用M报告的计数/来源误述替作者降级或改判。

- 8.1：条件边事实与原子success/alreadyTerminal、通知False规范依据并列；root/T01仍须裁决表示映射或提供可达失败序列。
- 8.2：无独立literal pin与已有动态资源SHA/包源一致性分开；独立gold批准权和变更门交root/T01，未把风险写成整套变异已绿。
- 8.3：类型关联/result组合覆盖缺口与已有activeProject/信任/更新谓词测试并列；供方具体类型和精确请求/结果/IPC组合行动已列。
- 8.4：辅助数量断言不等于违规，frame非恒真及邻近强断言均保留；30/12/17仍待逐项需求、上下文与可穿透反例。
- 8.5：文本政策单测盲点与真实CSP行为分开；nonce优先使单加unsafe-inline不足以推出放宽，供方须定义两模式政策及事件语义投影。

台账五项均未发现要求T05 W1–W3自有实现修正的新反例，实施增量记0；共享供方职责和具体行动非空。此处确认三专题与汇总口径一致，不代证所有潜在风险不存在，也不授权跨线写共有实现。

## 原字节与便读绑定

三raw均与binding登记bytes/SHA相等；相应便读副本bytes/SHA也匹配。独立去空白及Markdown表分隔线后逐字相等，仅据该限定规则确认便读绑定，原稿仍为字节权威。

| raw原稿                        | bytes | SHA256                                                             |
| ------------------------------ | ----: | ------------------------------------------------------------------ |
| contracts-and-job              | 19068 | `820d409ced38aa8b9f8059b4a1bb957eee6b5d45160605ae672abc9d998d93aa` |
| ipc-route                      | 18590 | `efff2491bd43075c722f5bea045bf9328c57c5bcfd72ab50b344bb318e311652` |
| independent-owner-test-and-csp | 12111 | `913062b2ec2aee137a073e2b5b290835ff345b3769f69e13ff04e4bf6741298b` |

独审raw的首9660B前缀hash亦等于登记ee2d11f0…9ab。其追加节明确限定接收owner nonce推论实质纠正后的7414B / `3d7ac1b8596df36ca3ae6cd8404b101d5562956e51260e9d39177f8cbbc009b1`。当前owner7414B / ad7fe07c…53cd仅两处locator后继；独立将417–444逆为417–443、csp.ts:3–26逆为3–28，精确还原上述3d7a绑定，无新增语义delta。

原错误摘句及纠错JSON保留，未冒称完整初稿仍在；首次定向格式check1、先存raw再生成便读副本的顺序也已登记。独审未将规范核对或已有测试代码升级为浏览器/产品实测。

本次仅静态文本/JSON/hash及声明归一化核验；没有源码/450/native/产品/oracle/GUI/网络重查，只新增本报告。结论不签产品、指定双审整体通过、意见关闭或父/发布门。
