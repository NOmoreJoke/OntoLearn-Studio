# T01 完整解析表摘要合同 r1（待独立审查）

设计输入仅为T03固定 `0b74b0a21e2336e1332042f612938b83a464be60` 的 `table-interface-r2.md`（SHA `1cc78023aae09ca2d2975d21e0cd2d71542325fe9c1e9c057ddd409b95f29605`）和完整 `complete-projections.json`（13123B，SHA `dd249c93dd23bbfa5dd47293f578251a375bb144da5b25f3e8683f878829106d`）。消费接口数据，不导入或批准S1实现。实现将在唯一canonical由T01统一提供，两端同一golden，不让调用方另造摘要算法。当前状态见 [status](../../reviews/T01/status.md)。

## 输入、身份与完整性

受信调用者必须提供 table、解析options、完整三字段parser implementation、独立预期sourceHash与显式有限 maxEncodedBytes。后两项是owner输入，不从table或对端自报导出。table.source_hash须与独立预期完全相等；身份标签进入hash只绑定声明，生产者授权/真实性仍由真实owner独立认证。

Table只接受精确四字段source_hash/sheet/fields/rows。fields为1..256个精确唯一非空白字符串，每项1..32768 Unicode码点、无NUL。rows为0..50000条，精确number/cells；number为2..50001严格递增，保留实际源行间隔；cells宽度精确等于fields，各格精确text/kind。text 0..32768码点、无NUL；kind仅解析事实 string/empty/boolean/datetime/date/number。empty文本必须空，boolean必须true/false小写文本；date/number等保持原字符串，不做重解析、trim、NFC、casefold或数据去重。该kind集合是内部解析投影，不借本设计注册公共新enum。

options精确format/encoding/sheet：本次受限CSV profile选择csv/utf-8-sig/null且table.sheet为CSV，所有cell.kind必须string；这只是本次设计选择，不声称S1只支持这一编码，其他编码须owner冻结明确词汇后另扩。XLSX为xlsx/null/真实选中sheet，必须等于table.sheet。sheet为合法Unicode字符串、不可为null，无已证明单项长度界，不擅填Excel31、32768、非空或控制字符新限制，由总编码预算约束。真实存在性由受信T03选择/producer认证，不以纯摘要器证明。缺列/短行不得补齐；header-only rows=[]合法。XLSX None/missing格均empty且无presence位；formula缓存空串是string空串，二者必须产生不同材料。

字段空白判定固定Python3.12 str.isspace字符集：U+0009..000D、001C..0020、0085、00A0、1680、2000..200A、2028..2029、202F、205F、3000。只判断全空白，不改任何原字节；不用JS trim/正则\s（FEFF区别）。拒孤立surrogate；TS按码点计数并允许合法UTF16 pair，Python拒任何D800..DFFF字符。

number使用JSON值语义：两端只允许有限safe integer、非bool、范围如上；Python的2.0与JS解析后的2相同并规范化为十进制整数2。不声称值层助手能区分原JSON的2、2.0、2e0；原始帧词法限制若需要，由原strict transport另行负责，不能伪造跨端一致证据。数组拒hole/undefined/null及额外/缺项，对象拒额外/缺字段。

## 唯一摘要材料

按顺序构造完整数组，字段/行/格均保留顺序，不排序、不采样、不只hash预览行：

```text
["ontolearn.source-table",1,source_hash,
 [format,encoding,sheet],
 [executionSemanticsVersion,engineVersion,dependencyLockHash],
 table.sheet,fields,[[number,[[text,kind],...]],...]]
```

以UTF8、无BOM、无空白/尾换行编码。JSON转义固定quote/backslash及短转义\b\f\n\r\t，其余控制字符用小写\u00xx（fields/text中的NUL此前已拒；sheet若含NUL按\u0000编码），不转义斜杠；U+2028/U+2029、非BMP直接UTF8，不ASCII/HTML转义。SHA256使用完整材料字节。格式/编码/工作表/三字段任一变化即独立摘要；mapping及domain base不属于解析表摘要，在上层计划另行绑定。

## 预算与验证次序

maxEncodedBytes为受信owner必填有限safe integer正数，不设隐式容量、不将262144帧限当完整表总限。先检查精确形状/字段数/行数/宽度，再逐标量校验并计入escaped UTF8、标点和整数文本，加入前比较剩余额度防溢出；超过预算立即拒绝，不能先全量Zod clone/map/JSON.stringify/encode后再检查。两阶段同步无await，验证与编码间无外部可变输入窗口。代码实现应逐量产出/更新hash或使用预算后严格上界内分块，不能无界复制整表。调用者自身解析表扩张/进程内存界与transport配额另外计量，不把逻辑编码预算说RSS或目标机性能证明。

## 必需测试与待审点

T03六份完整golden均使用明确合成parser身份，保存完整材料、字节数和SHA：equipment、multiline BOM实际行2/4、sparse XLSX含真实空行/空格、formula string空串、header-only空rows、CSV空值string。五份解析拒绝证据不制造table/digest；六项direct cell分支单独标机制测试，不冒充六份真实workbook。

还需独立机制golden：U+2028/2029、非BMP、FEFF非空白、0085/001C全空白拒绝、组合字符保真、empty与string空串不同、全部表尾/单格/选项/三身份/源SHA变化、exact预算与±1、超长/无界/重复/缺项/乱序/孤立surrogate、JSON integral float两端一致。摘要一致不证明parser实际被调用或source获得写授权；正式接线另测真实producer、权限、封存、预览确认和Store。

## 实施前精确合同门处置

已再读T03固定接口§2：Table.sheet为str且不是可空选项字段。CSV options.sheet=null与Table.sheet=CSV分开；XLSX options.sheet为同一个真实选中字符串。摘要器只验证类型/等值/合法Unicode/总预算，不另填未证明的sheet长度或真实性规则。

implementation精确复用原唯一canonical `$defs.implementation`：只含executionSemanticsVersion、engineVersion、dependencyLockHash且全必需；前两者各为ASCII `[A-Za-z0-9_.-]{1,128}`，最后为小写hex64，不接受额外字段。由受信producer传入，与当前运行时3字段完整绑定；T03投影未提供真实值，不能从源码SHA、Python/openpyxl版本或fixture合成生产身份。对应原定义属于本轮business3变更未动的旧定义，后续实现不复制第二身份schema。

本补充关闭两个已有设计空项，并明确CSV编码为受限profile选择；待独立定点复核后实施。当前未新增IPC/错误码、未启用parser/source业务入口。
