# T03 Table 接口数据 r2 独立只读复核

2026-10-21（Asia/Shanghai）。**通过；未发现需要修正的材料问题或越权交付。** 结论只覆盖固定接口事实、六组小输入及其数据投影，不是 parser 重跑、canonical tableDigest、公共协议或运行装配批准。原 Goal 保持 blocked。

## 固定输入与规则

- 主稿 `table-interface-r2.md` SHA-256：`1cc78023aae09ca2d2975d21e0cd2d71542325fe9c1e9c057ddd409b95f29605`。
- 数据 `table-interface-r2/complete-projections.json` SHA-256：`dd249c93dd23bbfa5dd47293f578251a375bb144da5b25f3e8683f878829106d`。
- T01 固定 `ff98761ad14bbcea39331f2305e4e7c56bc6ef2e` 的 `source-contract-t03-response-r2.md` 已只读核对，全文 SHA 为 `dfd39ff7ddb9fb861b392cf0268bd3b23e09caa0cc42248976ce9b067af8fccf`。
- 已核对 AGENTS `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`；共同指令当前为 `ff5f9fd0a4913cc6c2fa612ec565bdf40d67db4a6640e5293d4ca1e7d02cfaff`。新追加的 worker 唯一 owner 交接说明已读取：责任交接不等于 source wire/限额/运行批准，原第九节与无桌面规则继续适用。

## 核对结果

1. **来源可追溯。** 对 JSON 中三条 sourceProvenance，直接读取 git `30319412daf8ae4745987babf7bbed93c53b6b42` 的文件内容核对：source.py、既有测试和 equipment.csv 的长度与 SHA 全部一致。未 import 本线产品或 T01 候选实现。
2. **真实字段准确。** 固定 Table 的字段只有 source_hash/sheet/fields/rows，Row 为 number/cells，Cell 为 text/kind；fields 确为有序字符串 tuple，而非字段对象。kind 注解是 str，六个有限产生分支是当前 parser 事实，不是已有公共枚举或 dataclass runtime schema。
3. **kind/text 边界准确。** string/empty/boolean/datetime/date/number 与固定 `_cell` 及 CSV 路径一致，数值和布尔的 text 均是字符串。六分支数据明确是 `_cell` 直接分支示例，没有夸大为六种真实工作簿类型矩阵。日期/时间文本及数字不被摘要端再次格式化的说明合理。
4. **六组 raw 与全部投影一致。** equipment、multiline-bom、sparse、formula-empty、header-only、empty-value 的文件长度和 SHA 均匹配 receipt，且等于各自 table.source_hash。逐行逐 cell 核对 table 与 orderedValuesDataOnly，六组均完整一致。直接查看 CSV 原文及 XLSX 内 sheet1.xml，样例来源与已有测试 helper/对应 sheet XML 相符；未重新生成 ZIP，也未调用产品 parser。
5. **空缺、稀疏及重复语义准确。** CSV 显式空字段为 string/空文本，空记录及缺列按固定宽度规则拒绝；XLSX 缺 cell/内部缺 row 按表头宽度补 empty，确认存在的公式空缓存为 string/空文本。没有 presence 字段可区分缺 cell 与 None。精确重复表头拒绝，数据/业务键重复留给后续 Mapping 检查；文档没有混淆两者。
6. **行号与空表准确。** 多行 CSV 保留记录起始物理行号 2/4；稀疏 XLSX 保留 2/3/4。合法仅表头返回零行；空 CSV 则 EMPTY_SOURCE。成功输出行号/数量范围及“限制记录起点不等于检查跨行终点”的边界说明与代码一致。
7. **五个拒绝对象准确。** 对五组 inline inputUtf8 独立核对 SHA；EMPTY_SOURCE、重复字段、短行、空记录、空表头字段的 code/sheet/row/column/field 与固定源码分支相符。没有把拒绝伪装成成功空 Table。
8. **数据不冒充新协议。** format/encoding 等 caller options 与 Table 分离，orderedValuesIsCanonicalWire 明确为 false；没有声称已有 tag/version/tableDigest/sourceRef/授权、完整 worker 或公共错误。T01 仍需冻结 canonical Unicode/JSON/整数规范和跨语言 fixture，六项既有装配缺口及原验收保持待办，没有无端扩大或关闭范围。

## 证据边界

本轮只做文件/JSON/原始 OOXML 静态数据检查、git 来源和 SHA 核对；没有运行 pytest、全 check、打包、GUI 或产品 parser，没有 import 产品/T01代码，没有执行本次交付记录的六分支调用。数据提取执行环境及版本由交付 receipt 记录，本报告没有将其升级为独立重跑证据。

未修改主稿、raw 数据、实现、测试、依赖、共享文件或 Goal；仅新增本报告。不输出可导入实现或第二公共 schema。worker 维护责任已交 T01，但运行/schema、真实来源传输/配额/pin/TTL、typed 结果与端到端验收未因此获批。
