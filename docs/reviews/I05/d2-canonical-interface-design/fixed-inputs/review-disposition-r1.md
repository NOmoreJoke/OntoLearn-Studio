# 接口库存 R1 处置与勘误

固定事实候选为 `4beccef733396d525b9db56be544dbdb551581ad`，独立完整报告为 reviews 同目录 `independent-r1-report.md`。结论仅为现有接口事实库存 Limited Pass，无 P1/P2；383项是静态结构/声明核对，未运行产品。原23件候选保持固定字节，本件只给后出勘误与精确阅读说明。

- IR1-N01 [P3] 已在本后出勘误处置：`helper-interface-facts.md:23` 的 DirectStepsReceipt 源码范围应读作 `directsteps.py70–81`，不是70–80。原结构化 `additional-return-layouts.json` 已保存 endLine81和全部11字段，包括 retention_owner；没有改旧候选或删字段。
- catalog codec 阅读精确化：production catalog_json沿 `_ProfileProjection`，record对象为 `recordType` 加原字段在同一层展开；probe `_typed_value` 为完整模块名 `recordType` 加嵌套 `fields`。helper正文“fields/recordType包装”泛指原字段和标签，不能据此给 production 插入嵌套fields容器。二者分别保全，不归并成新schema。
- 第二独立checker尝试名为allowed的白名单表达式得到空目录，没有计作通过；独审随后按固定源码真实approved17类定向核对，原空提取过程保留。383项全过不覆盖该空提取。

读取顺序：先 current-disposition.json 与本件，再两份事实正文和结构化目录；missing-definitions.json 是首八文件窗口的历史请求，后收到的11helper和3窄片段以当前处置为准。IMPLEMENTATION只核源码表达式，未求值锁路径/hash；RootRef.kind只注解str，不补enum。未封闭object/tuple/dict、完整导出codec接收、实际same-issue/live verifier/外部权威继续pending。

D2采用必须等总控对最终固定纯材料精确接收；源码访问不随文档pin转授。本文不修改retained外审输入、不签实际采集、费用/issuer/17L/wholeH/417/S1/B1/SQLiteHOLD/真实父Job/Store/selected/平台/真人/指定双Pass/CI/develop。工作树base1b6仅是本库存历史材料起点，正式集成base未在此选定，产品事实源始终fixed2cf。
