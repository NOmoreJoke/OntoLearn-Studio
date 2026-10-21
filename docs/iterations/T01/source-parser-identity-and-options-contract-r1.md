# T01 parser身份与完整options补充合同 r1

全文读T03固定 `25de6bbfb77435b1cf49ec5b5292b20b885eeaa3` 的 `parser-producer-and-options-r3.md`，SHA `df94bdec2bdb66659941e36bc8ee853bc79b54765527bf4b08b342da93814a6c`。仅事实/设计输入，不消费S1实现或改未交resources；本页补充 [digest r1](source-table-digest-contract-r1.md) 与 [capture r2](source-table-digest-contract-r2.md)，状态见 [status](../../reviews/T01/status.md)。

## 1. 事实与机制范围

固定S1没有专门parser语义版本或真实parser三字段，realParserImplementation仍未提供。`i04-infrastructure-v1 / 0.1.0 / 旧锁SHA`只是既有基础设施声明，不是parser执行身份。T03 `t03-source-parser-v1`是待采用标签；源码SHA、三个库版本、旧包probe均不能补齐它。纯材料golden继续明标synthetic，不把本合同写成producer已接通。

## 2. 五个CSV词汇与XLSX精确边界

下一纯机制候选拟把CSV options.encoding接受集明确为固定S1五个精确词：`utf-8`、`utf-8-sig`、`gb18030`、`big5`、`utf-16`。这是依据真实接口补齐未发布设计，不改变tag/version1材料排列，也不是本轮实际decoder验收。每次调用仍显式必填编码，摘要器无隐式默认、不猜测/规范化别名、不转码；真实parser默认sig属于T03入口事实。相同Table而encoding不同，完整材料/hash必须不同，不能强改为sig；源bytes转换会改变sourceHash并重新确认。

其余词（含utf-16-le/be、UTF-8大小写、别名）拒绝。五词机制golden须全部精确比对完整材料字节/hash；真实五种解码/跨平台/worker接线仍须原owner实际验证，不能只由此关闭FR300。原准备patch只接受sig且未完成，不能直接作为新实现。

XLSX Table.sheet和options.sheet必须是同一非空合法Unicode字符串；非空是T03新答复中的parser事实，替代旧r1未证明非空的开放点，不使用trim把用户原名改掉。是否真实存在由可信producer实际枚举/调用验证，摘要器本身不证明。broker的256 UTF8/NUL私限不写成公共parser长度schema；纯材料总预算与原Unicode规则仍保持。CSV options.sheet=null、Table.sheet=CSV保持，XLSX encoding=null保持。

## 3. parser三身份与正式Job身份的衔接提案

保持唯一canonical implementation精确三字段，无第二schema。区分两个真实生产角色，不能在adapter里私选标签或用一个角色的身份冒充另一个：

- **Parser产物身份**：认证真实解析执行的profile及该实际产物engineVersion/完整锁。T03描述并固定parser语义；实际worker/构建owner提供可恢复资源、真实版本/完整锁与执行入口。T01只接受经root批准的精确producer映射并绑定实际调用/typed完整结果/source/options/tableDigest，不能从调用方参数自报或getter对象取得授权。
- **正式Job/领域result完整implementation**：仍来自该真实Job执行器获批的wholeimplementation，现有create_job/derived新消费/current与historical的三字段全等门原样保留。parser材料引用不是自动获得的derived result，不据“同一文件”或“同一版本标签”跳过完整比较。若未来把parser产物作为既有derived result来消费，必须满足原完整身份规则或先经明确新合同审批；本页不加例外。

正式input/context需要同时不可变绑定实际parser三身份及实际Job三身份各自的角色、原完整来源/选项/表摘要，不能把parser标签静默替换Job.implementation，也不能盲改全局I04资源以假装全部消费者同语义。两角色若真实由同一批准执行profile产生且三字段全等，可如实使用同值；不同则只能以明确typed源输入证据连接，不能冒称满足原derived结果三字段全等。该typed context字段尚未注册，本页不授权实施。

实际签发链拟为：T03提供固定parser语义声明→root协调实际资源/构建owner冻结profile到当前产物完整身份→真实受控worker报告且coordinator对照同产物可信期望值认证→T01把认证结果和内容链写入原context/plan/claim指纹。`resources.py`仍非T01路径，不直接改；原I05语义新候选也不因本页被采用。每项身份/映射/版本资源必须先由原owner实际提供并经root批准，没有这些事实就保持正式producer缺口。

本提案仅解释如何保留现有Job身份不变量及逐角色认证，未批准新方法/字段、capability分派表或producer标签。root若要求最小单一执行profile，需明确该profile真正覆盖的parser/正式任务语义及实际owner，而不能仅把两标签强行写等。纯table材料机制不依赖此生产决定，但真实parser接线必须先闭合。

## 4. 原claim/proof边界再次确认

接受T03对r4的明确分流：先认证当前项目读权限，已有claim按原完整context只读对账；不先总调readForCommit/proof/livelease/当前CAS。首次受理才验证真实proof、确认和最终dispatch guard。unknown原operation先取得barrier/fence明确结论，新确认才可新operation；不以同bytes/新代次绕过，accepted pin不受旧transport TTL/release撤销。均为合同，未跑该生命周期实现。
