# C2 正文探针前资源门修订

本次仅修两处原 writer。旧产品256b、过程5b118、129专项、原19044B独审及215对工具原件保留；旧候选仍暂停供方采用。本文不是新独审结论。

## 前门与真实 SQL

旧 `_cost` 把 length、CAST、instr 放进 metadata，先扫描正文再按 u/n 收费；原 aggregate guard 和 WHERE 定位也有同类先后缺口。首真实低预算反例 `bac5e4 exit1` 保存原39943B/d655模块、完整输出和11043B/729fe1fc原流水。

本版在同一 owner 连接和本次 BEGIN 内先核 SQLite3.50.4 的完整 sourceID，再读实际 page_size；不匹配返回有限 unsupported-profile，不改锁、发行环境或平台支持承诺。原启动完成前提不变。

每行分组直接列参数的 typeof/octet_length，最高实际物理列先访问；每种真实 metadata SQL 首次实际 EXPLAIN 核 OP_Column P5=128/192、无索引/排序替代，INTEGER PRIMARY KEY 仅 Rowid 的无 Column 路径亦允许。UTF16 TEXT 必须有偶数字节数。u 是原数据库编码字节，不先 CAST、转码或扫描字符。native metadata 前已支付 statement、物理 record header98307、20页 point seek 和局部页复制票；局部正文可能复制，不声称绝对零拷贝。

实际完整源码为官方 SQLite amalgamation9282866B/SHA e3f5d6901e7492af4a1fc8c4d745cae84c264942524c3fbfc02b82a5ca8818c8。OP_Column97359–97416/97505–97548：完整物理 header 可先分配，不能从逻辑32列/u小推出 header 小；仅 overflow 分支根据 typeof/bytelength flag 跳过正文。编译器115504–115522只对直接列参数设置该 flag；bytelengthFunc130532–130567 对 TEXT 使用原编码 bytes/bytes16，对 INTEGER 的十进制字节按 db encoding乘1/2。精确行费的 INTEGER 长度据此计算。

取得 u 后，先按 UTF8原160*(u+1) 或 UTF16 `16*(u/2+1)^2` 最坏字符上界持有 probe 票，之后才运行 length/NUL，再结算原 n 费用。失败/取消时保留已持有额度，不把已发生工作抹去；成功结算后的原 typed 行 canonical 费用、完整字段名/标点/NULL/TEXT转义及独立实际完整行核同保持。probe 的瞬时峰值另记 probePeak，预算±1以真正峰值验收。MAX_QUERY_COUNT65536、probe/read各512MiB、原 ReadLimits 与 evidence/selector/return上限不提高。

## 行遍历、缓存和清理

没有原 COUNT/aggregate 扫描正文。schema/object count 和各表原 raw-byte aggregate 改从实际 native metadata 得到，原 ProjectHostReader._preflight 条件仍实际执行。schema 全行先界后计价、物化、建同 snapshot 名称索引；table_xinfo输出≤33后拒>32或 hidden/generated列。其字符串受已收费的完整 schema 原文约束。

无 WHERE 的单 cursor 以 LIMIT(validation_rows+1) 枚举 rowid；每次 fetchone 前支付下一次40页推进，execute首 step另付，严格递增拒重复/倒序。CPython3.12.12 cursor.c1112–1115先构造本行、stmt_step下一行，再返回本行；所以未返回行、异常、DONE都不能凭已交付行数免账。枚举自有 cursor 在正常、资源拒绝、取消时关闭；未知 caller事务不动，仍只 ROLLBACK 本次事务。关闭/ROLLBACK失败保首因与有限 cleanup_failed，不声称释放。

SQLite同版 moveToRoot77066–77140只允许空 leaf终止及page1虚根；moveToChild76966–76999拒nCell<1、类型不符及深度20；moveToLeftmost77152–77164下降有深度界；btreeNext77816–77895单次最多向上20/向下20。这里不借 page_count 给坏 DAG 的遍历总次数作界，也不调用 BtreeCount。

后续 WHERE/ORDER BY 由已完整枚举的 rowid VALUES集合 CROSS JOIN真实表、rowid等值 point seek执行；固定 JOIN也分别按真实两来源 rowid定位。避免按逻辑行数预扣后执行坏DAG上的无界零输出 WHERE扫描。实际 EXPLAIN 核真实表 SeekRowid、无 Rewind/Next/Count/OpenAutoindex；先用最高列 typeof 的 CASE，再执行原筛选和原字段投影，维持原 sqlite.Row。LIMIT只用于有限数值 rowid枚举/既有原查询，不截断完整必要 history。

同 snapshot缓存 native bound、schema索引、定位结果及已验证完整 sqlite.Row；重复 cache lookup/output仍先收费，重复 SQL/读取不因 seen免账。唯一(table,rowid)证据费仍只计一次。SQL编译/参数、实际值比较/排序/物化和临时结果另预留有限工作；缓存不跨事务，不新增可变权威、UDF、第二连接或业务权限。

## 新反例与边界

新增12例覆盖低 probe 前无 length/CAST/instr、真实 EXPLAIN、header票±1、预读时取消及同时 rollback故障、未知 sourceID、generated/33列拒绝、64/65行预读边界、真实空 child和重复缓存收费。

真实临时库 overflow canary：dbstat指定job_blobs首 overflow页88，checkpoint/shrink后只破坏其 next页指针；native u仍正确读1048576，低 probe返回resource-limit，未进入正文扫描；同库直接 length对照实际 SQLITE_CORRUPT。另一真实临时库仅将 SQLite指定的非根 leaf nCell清零，rowid枚举即 storage-failure，未进正文。这是专属临时损坏反例，不是合法业务写入或通用 Btree parser。修改前页字节在finally恢复。

原129正向/反向断言保持，费用 oracle扩充实际控制票、临时 hold结算、额外 scan和cache工作；SQLite execute/fetchone/fetchall/fetchmany/iterator注错仍走真实 driver。先前首修保守工作票曾使正常材料拒绝，focused-04 read536163937、control445624033的原账保留；随后去除重复 schema/full-row读取并建付费索引，未升 cap、删阳性或放宽业务 validator。

## 保全及未验

每个后续 run使用独立 `--basetemp`，原日志为完整 stdout/stderr合流，不补造分流标签。首反例及关键 focused-04等流水已逐字封存。必须明确的遗漏：中间 focused-01的11份 unsupported-profile失败流水在统一捕获前已被默认pytest轮转，只有原完整日志/工具exit，没有流水原件；索引逐项列 missing，不重建、不声称全账完整。原C2历史归档没有被改动。

新正常check、sources、固定54和每件身份见本修订 checks/manifest；独立 reviewer须审本新候选，不能延用旧19044报告的通过。本修订不授供方采用、组合56、profile2、formal resolution/current scope/原dispatch物理绑定；生产供方、既有启动/preview、指定双外审、目标OS/真人、CI及父门保持。未运行GUI/native/模型/网络/付费/打包/push/PR/merge。

## 2c425候选后续实际阻断

上述新141项正常check成功仍遗漏两条真实路径，2c425不得Pass或恢复供方：作者549a43 exit1证明新增同名rowid TEXT使数字枚举先返回1MiB正文（probe0）；独审f3969e exit0证明最终_cost SELECT*的rowid谓词藏在CASE里，真实300行Rewind/Next以263503票发生超过300KiB局部copy。两反例完整原件另封r1-counterexamples，不倒改原check/source/57pairs归档。根已明确授权同两writer修后另固定候选及正常check/source与独审复核；本次原成功不覆盖后续字节。
