# T03 → T01：固定 S1 Table 类型与有序投影 r2

本交付只有接口数据与说明，不是可导入实现、公共schema或已存在的tableDigest。原Goal保持blocked；不采用T01候选代码，不授权装配。已读取T01固定 `ff98761ad14bbcea39331f2305e4e7c56bc6ef2e` 的 `source-contract-t03-response-r2.md`，原件SHA `dfd39ff7ddb9fb861b392cf0268bd3b23e09caa0cc42248976ce9b067af8fccf`。

## 固定来源与实取范围

本线S1固定提交 `30319412daf8ae4745987babf7bbed93c53b6b42` 的以下字节已与现存文件逐字核对：

| 路径                                                     | SHA256                                                             |
| -------------------------------------------------------- | ------------------------------------------------------------------ |
| `packages/engine/src/ontolearn_engine/mapping/source.py` | `93bf09e10723c8522f1e9fbb8e170ffece596143c5e00ddcf7be950d15e1ddc8` |
| `packages/engine/tests/test_mapping_source.py`           | `c66e1fda26ee73dc87324402c2194def0bf6b7eea6b38b18fc90b669dfa0eed7` |
| `tests/fixtures/mapping/equipment.csv`                   | `cf85db51de82f9f42266bd83bcba72795cb4f6dd12ffb7553c3f0e575bea02b8` |

使用本线既有Python3.12环境执行一次有限接口数据提取：上述真实parser解析6个小输入，记录5个定位拒绝；另直接读取并调用固定 `_cell` 的6个类型分支。没有运行pytest/全check/包/原生GUI或改动S1源、测试、验收。XLSX输入复用上述既有测试的workbook helper及对应sheet XML；完整生成的合成输入字节和SHA一并保存，非只给hash。六个kind分支示例是 `_cell` 的实际返回，不冒称六种工作簿类型都经真实XLSX解析验证。

完整数据见 [complete-projections.json](table-interface-r2/complete-projections.json)：每个成功实例都有完整 `table` 与 `orderedValuesDataOnly`、独立caller options及源文件SHA。数组示例的顺序为 `[source_hash, sheet, fields, [[row.number, [[cell.text, cell.kind], ...]], ...]]`；它只是完整值的交接排列，不冻结tag/version、wire schema或canonical JSON转义规则。

## 真实类型及全部parser kind取值

以下范围限两个既有parser入口**成功返回**的Table，不涵盖外部手工构造的dataclass。dataclass是frozen，但注解本身没有runtime schema校验；`Cell.kind`实际注解仍为 `str`，不是Literal/已注册公共enum。

| 字段                | Python真实类型与值域                                                                       | 顺序/语义                                                                                                   |
| ------------------- | ------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------- |
| `Table.source_hash` | `str`；原完整输入bytes的SHA256，小写64位hex                                                | 包含原BOM/换行/ZIP元数据等，不是解析表摘要                                                                  |
| `Table.sheet`       | `str`；CSV固定 `CSV`，XLSX为调用者显式选择且实际存在的工作表名                             | 不提供公共长度schema或sheet枚举；不是可空选项字段                                                           |
| `Table.fields`      | `tuple[str, ...]`；1–256个字段名，各自最多32768个Python字符，非空白、无NUL且逐字符串不重复 | 首记录的cell.text，保留原顺序和空白/Unicode/大小写；不是字段对象数组，不带类型                              |
| `Table.rows`        | `tuple[Row, ...]`；0–50000个实际输出行                                                     | 保持来源顺序；只表头合法时为空tuple，不补伪数据行                                                           |
| `Row.number`        | `int`；成功输出行的来源行号为2–50001，非bool/float                                         | CSV为记录开始的1-based物理行号，跨行引号后会跳号；XLSX为1-based工作表行号，内部缺行也保留。不是数据数组索引 |
| `Row.cells`         | `tuple[Cell, ...]`，每行长度恰等于fields长度                                               | 位置i对应fields[i]，列号i+1；不按名称重排，不省略empty cell                                                 |
| `Cell.text`         | `str`；0–32768个Python字符，无NUL                                                          | 观察/缓存值的文本；无JSON null、bool或number，数值类型也已经是字符串。长度是字符数，不是UTF-8字节预算       |
| `Cell.kind`         | `str`；现有parser分支只产生下表6个精确小写值                                               | 观察类型，不是用户转换规则或最终RDF datatype                                                                |

| kind全部取值 | 现有产生分支                                                              | text规则                                                                                                                 |
| ------------ | ------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `string`     | 全部CSV cell；XLSX普通字符串或其他值的str回退；确认存在的公式空字符串缓存 | 原解码文本/`str(value)`；如 `001`、空字符串。CSV的 `true`/日期/数字文本不会自动变kind                                    |
| `empty`      | XLSX保存值为None，包括缺失/稀疏cell与内部缺行补位                         | 恰为 `""`                                                                                                                |
| `boolean`    | XLSX值为Python bool（检查先于int）                                        | 恰为 `true` 或 `false`，均为字符串                                                                                       |
| `datetime`   | XLSX值为Python datetime（检查先于date）                                   | `value.isoformat()` 原结果，不能擅自统一时区/精度                                                                        |
| `date`       | XLSX值为Python date但非datetime                                           | `value.isoformat()` 原结果                                                                                               |
| `number`     | XLSX值为int或有限float，不含bool                                          | Python `str(value)` 原结果；digest端按字符串处理，不再次解析、格式化或按Excel显示格式补零。非有限float拒绝为INVALID_CELL |

当前不产生 `null`、`integer`、`float`、`time`、`formula` 等额外kind；Python其他类型若进入 `_cell` 回退仍为string。例如仅时间对象不取得独立time kind。完整六分支实际返回及其证据范围在JSON的 `finiteParserKindBranches`；datetime/date分支不扩大为所有日期样式/工作簿格式已通过。

## 缺失、空、稀疏及重复字段

- 完全空CSV返回EMPTY_SOURCE；没有首记录不能构造Table。只有合法表头则返回rows=[]，不等同EMPTY_SOURCE；本次保存两种真实结果。
- CSV字段原样解析；显式空字段仍为Cell(text="", kind="string")。缺少分隔列或额外列触发ROW_WIDTH，不填null/补列/截断。真正空记录不跳过：csv.reader产出零列，非空表头下ROW_WIDTH；没有把它静默洗成合法空值行。
- XLSX首行确定宽度，内部/尾部稀疏cell补Cell("", "empty")；内部整行缺失也保留行号与全部empty cell。后续行长于首行触发ROW_WIDTH。文件末尾无实际范围的无限空行不会被生成。
- 缺失单元格与保存值None在Table中合并为empty，**没有presence标志，无法从Table再区分两者**。公式缓存缺失触发FORMULA_CACHE_MISSING，无Table；明确的空字符串缓存则为string/""，区别于empty。Table不保存公式表达式或Excel样式。
- 首记录任何字段名为纯空白/空字符串、含NUL，或完整字符串精确重复，都拒绝而非自动命名/去重。`id`、`ID`、`id`及Unicode不同规范序列不被自动合并；不trim/NFC/casefold后再去重。字段顺序不排序。若表头含空的稀疏cell，该字段同样非法。
- 重复的是**数据值/整行/业务主键**时parser不做实体去重；在完整rows保留，后续Mapping preview按所选键检查空键/重复键。该语义与重复字段名拒绝分开。
- CSV跨行text保留字段内换行，number记记录起始行。默认utf-8-sig可去除输入首BOM，编码是调用选项；Table没有encoding字段。50001的限制检查CSV记录开始行/XLSX遍历行，不表示已验证任意CSV跨行记录的终止物理行也不越界。

## 完整小实例

下面是既有equipment.csv真实解析的全部Table字段、全部行和全部cell，没有describe样本截断：

```json
{
  "source_hash": "cf85db51de82f9f42266bd83bcba72795cb4f6dd12ffb7553c3f0e575bea02b8",
  "sheet": "CSV",
  "fields": ["equipment_id", "equipment_name"],
  "rows": [
    {
      "number": 2,
      "cells": [
        {
          "text": "001",
          "kind": "string"
        },
        {
          "text": "泵站A",
          "kind": "string"
        }
      ]
    },
    {
      "number": 3,
      "cells": [
        {
          "text": "002",
          "kind": "string"
        },
        {
          "text": "泵站B",
          "kind": "string"
        }
      ]
    }
  ]
}
```

同一数据JSON另保存CSV BOM/跨行（数据行号2/4）、合法仅表头、显式空值、真实稀疏XLSX（行号2/3/4）及公式空缓存的完整投影，以及5个无Table的实际拒绝对象。XLSX raw由既有helper本次生成后原字节固定；ZIP生成时间可使重新生成的raw SHA不同，应使用交付的精确文件而非猜测再生成的hash。

## 明确不存在的字段与r2保留边界

Table只有 `source_hash/sheet/fields/rows`，Row只有 `number/cells`，Cell只有 `text/kind`。当前没有tableDigest、tag/version、format、encoding、sourceRef/phase、selectionId/generation、长度、project/domain base、确认/operation、presence、源XML类型/样式或原公式。caller options只是本次数据receipt的分离元数据，**不是S1 Table已有schema字段**。Preview的snapshot/source/definition_hash也不是新增表摘要。canonical owner须据本完整值形状与明确options冻结UTF-8 JSON/tag/version/孤立surrogate与整数规范及TS/Python逐字fixture，不能从describe、输出事实或raw文件hash冒充完整表摘要。

接受T01 r2将不足两段frame直接拒绝固定64KiB profile、inspection/configure独立phase、只读执行先于最终写确认、权威受理/revoke排序的设计选择；source_content只证明完整内容/同库缓存，不是活授权/公共wire/pin。worker未来owner现已为T01，但剩余source profile/配额/TTL/pin、typed worker结果、具体公共形状/错误、真实parser适配及六项原门禁未因本数据交付通过。此处不输出可导入实现，不消费T01候选，不发明tableDigest已存在。
