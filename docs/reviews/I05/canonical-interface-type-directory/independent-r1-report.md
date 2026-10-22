# 类型字段目录补件 R1 独立窄审

结论：**Limited Pass，限已审声明的纯字段目录出口**。未发现 P1/P2，也没有新的非阻断意见。本轮103项静态核对全部相符；不重跑原383项，不签新 codec、封闭 admission grammar、来源/运行权威或产品门。

## 固定范围

审查者 `/root/independent_canonical_interface_review_r1` 是非D2的独立审者。唯一工作树为 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-canonical-interface-inventory`，分支 `docs/I05-canonical-interface-inventory`。新候选为 `b3e1ba80a3ea7040af0c03ad9a34a5f4950af14b`，基线为 `39a91de416eb2692aea079c637309f9d8770b08a`，仅审两个 `canonical-interface-type-directory` 前缀中的9件新文件。

先全文读 controller 的 `I05-canonical-interface-inventory-D2-limited-reception-20261022.json`，确认既有接收只给D2十一份纯事实，明确排除两个声明索引、源码和检查器。故本补件解决的是获准事实正文中未展开的逐字段出口，不是扩大D2索引/源码读面。旧接收中12个顶层 API layout 的精确计数勘误继续有效，本轮没有重用旧独审“13”措辞或再认证旧检查。

## 身份与逐字段核证

- 新9件：实际 base→candidate membership 精确等于 manifest 的8 payload 加 manifest 本身。9件当前字节均等于新固定 Git；8 payload 的 bytes/SHA 全匹配。
- 旧48件：从固定39a91的两个原库存前缀取得精确48件目录，逐件核当前字节等于固定 Git；没有改动或格式化它们。
- 提取源：只读固定39a91的 `docs/reviews/I05/canonical-interface-inventory/additional-source-index.json`，80114B，SHA256 `14ee0d210df3b2626094ccc9898b852a8cdb63075db5295add52274c78ab0ea9`，与补件输入登记相符。没有读取产品源码、追imports、方法或算法。
- 17类选择及顺序与输入登记完全一致，没有重复className。各完整class行的 sourceRef/path/bytes/SHA、类起止行、装饰器和基类语法均吻合旧固定索引。
- 86个本地字段逐项核对 name、annotationSyntax、sourceLine、defaultSyntax 及顺序；各类fieldCount和总fieldCount均从实际数组复核。没有重复字段、漏掉默认表达式，或把“没有默认值”的JSON null混成默认值源码字符串 `None`。
- ProfileLimits有17本地字段；RuleSpec的8字段、PreparedFiring的11字段、ProfileValue的4字段及其value:object均完整。原字符串 `PROFILE`、`False`、`''`、`()` 和数字默认表达式都只作为源码语法保存，未求值。
- 作者登记的四份 formatter stdout/stderr 的实际字节与摘要相符。作者exit0是其登记；本轮没有重跑作者命令或旧检查器来补造证据。

结构核证共103项、全部通过。该数量由身份/字段/目录/边界检查构成，不是103个产品测试。逐项结果及60个真实Git子命令的argv/cwd/exit、stdout身份和分离stderr保在 `independent-r1-proof.json`。Git正文stdout用不可变ref/path/bytes/SHA完整定位，目录stdout原base64保留；所有子命令exit0，stderr0B。

## 语义与授权边界

全文阅读 type-directory 和 handoff 后，没有发现把 className/sourcePath 发行成wire discriminator的声明。`sourceLocatorNotWireDiscriminator=true` 与 `newNormativeCodec=false` 明确限制用途；17这个计数本身不被用于证明与某投影approved集合等价。目录只列本地声明字段，当前基类语法均为空；没有把字段目录伪装成已执行的完整dataclass或实例结果。

既有production的recordType加平铺字段、probe的完整模块名recordType加嵌套fields、material原codec保持区分。str注解没有被补成enum；ProfileValue.value:object、其他未细化tuple/dict和domain/value对应关系仍缺少封闭grammar。默认语法没有变成consumer fallback，也不证明费用cap获批、原返回已经完整或runtime类型合法。

handoff明确D2在独立审和总控精确固定接收前不得读取本补件；接收后也不能沿pin追索引/源码。本报告不直接授予D2访问权。native_result完整布局、完整byte codec、same-issue/live issuer/handle/verifier、外部来源权威仍pending，所有原wholeGate和实施/运行门未改变。本补件不加入retained两项指定审输入。

## 本次动作与限制

只使用固定Python3.12、stdlib JSON/字符串/哈希处理及Git字节读取，PYTHONDONTWRITEBYTECODE=1。未执行任何产品、测试、probe、已有检查器或运行模型；没有读取actual/expected/probe_inputs、retained任务输出、D2新WIP或其他费用/载体材料。没有新产品源/算法读取、默认表达式求值、网络/DB/native/安装/构建，也未stage/commit或修改旧9件、旧48件。

本轮内联静态核对的外层实际exit0见工具转录 `51d8e5`；外层独立双流没有事后补造，Git子流则在调用时真实分离捕获。后续仅格式化本人新md/json，原始流不格式化；实际格式化命令与分离流另存本轮receipt。已有字段身份无需新增源码、运行或算法来补证。

因此本补件可交总控按精确固定纯材料接收。它不关闭完整codec/admission、实际采集、来源/issuer、费用/17L、wholeH、417、S1/B1/SQLiteHOLD、父Job/Store/selected、平台/真人/指定双Pass/CI/develop等门。
