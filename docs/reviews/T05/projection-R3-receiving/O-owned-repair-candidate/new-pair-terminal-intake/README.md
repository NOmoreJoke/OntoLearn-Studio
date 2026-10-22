# O15 指定新双审：正式终态与原稿收件

Z 原审查正式 completed，原稿已逐字保全并全文收读；M 原 turn 尚未收到正式终态与报告。本批仅收件，不修改冻结候选或续发审查，不签双审最终关单。

## Z 本方原审查

官方唯一日期事件源 `/Users/kyle/.zcode/cli/log/zcode-2026-10-23.jsonl` 双匹配 `session_b89ca579bc1862a94909bd1503bafbc6` 和 `turn_a4a74b36-8465-458a-a385-cdfd22c33d3c`，得到 `2026-10-22T18:41:38.748Z / turn.completed / completed`。原报告来源是本方新树 `launch-O15/report.md`，非 symlink，17338B、95行、SHA256 `65379ed2e765a9388438245dbb140d6d3ff5dd2d1b5b68d4ca54bd9402b72965`。复制前后来源两次字节相等，原样另存 `zcode-report-original.md.raw`；owner 已全文读取全部95行，未以终端截断代全文阅读。

Z 自签结论为完整 O 静态150项、五项全文缺口及共同历史输入 Pass。它自述逐行读五项旧缺口，对大JSON使用完整解析、全节点遍历与约束核对。owner收取和准确归属该声明，没有重新进行150项产品语义审查，也没有以hash或统计代全文覆盖。独立收件审查另行判断原生公开阅读记录能支持到何处。

Z 表中 F01–F11 是其本方实体闭合裁定，F12–F15 仍交root/T01；原15条全部外部流程继续open，须待指定双审汇合和总控处置。15行原文及行号逐项登记 `zcode-reported-opinions-register.json`，不改写原稿，不将本方裁定冒充流程关单。137 pending、26 allocation pending、whole=false和所有运行/打包/生产/父/发布门保持原状；本次不把它们变为完成。

## Z 两项获准正常验证原流

原报告明确命名的 `raw/oracle-selftest.stderr.raw` 已原样收取全文：8697B / `4bd3544eeef3f3888b6ca39c7dc72a19db914cd26e69f4ac7f0f28984873ed61`，57项均ok、末尾OK。`raw/oracle-check.stdout.raw` 为1001B / `030cabeee57f2adf1e3d03376c0f079e78a62e045c819b67f8241b356888bce5`，417 observations、320 datasets、280 specified、137 pending、whole=false，五件产物bytes/SHA与封存相同。argv/env/exit首先归原报告，并由独立收件沿本方原生工具调用配对核实；owner未重复运行oracle、产品检查或observe。

## owner首次末答投影错误及纠正

首次 `zcode-terminal-original-preservation.json` 只按SID/turn取最后stop，误把querySource=session_title的标题生成当审查末答，53B文件 `zcode-native-final-reply.txt` 同样是标题JSON。该首错误回执及文件保留，未静默覆盖；这不影响独立官方completed事件或报告身份，也不能归为模型审查错误。

正确过滤必须同时带SID、原turn、`querySource=main_turn`、finishReason=stop。唯一匹配record94/request `790d5046-cffc-4f9e-bff1-dbc431ededd0`，18:41:21.731Z开始、18:41:38.448Z结束，公开末答2149B / `18b886cbfca7d20733a57b80acb333d2b4b91f6edb77dfedd0e9228a52f7485f` 另存 `zcode-main-turn-final-reply.txt`。官方18:41:38.748Z随后完成。全部纠正字段在单独 correction JSON，今后不以同turn标题生成或末toolcall代正式审查末答。

## 输入与读取边界

Z完成后owner直接重核两树manifest声明的450保护件+10launch+1AGENTS覆盖层，全部匹配；两HEAD仍0f87f2c2，index空，tracked只授权AGENTS未暂存。未运行helper，不覆盖模型observe，不读取或hash未知自动metadata。该快照不宣称全filesystem集合冻结，也不冒充M终态后freeze。

GUI已在派发后释放给总控，本批没有再次CUA；没有读peer当前报告或给任一指定模型发送另一方意见，没有新模型请求/安装/收费/凭据操作，没有push/PR/merge/Goal。原生活动全流和thinking仍在官方原处，入库仅本方公开原稿/末答/明确命名正常命令流与最小事实投影。收件所需原件以 `.md.raw` 或 `.raw` 保字节，作者Markdown/JSON单独格式检查。

## Z 原报告未逐项披露的两次静态工具首错

独立收件定位了两次本方静态工具首错，owner只按精确native坐标保留公开最小投影，原稿不改：

- 一次Read路径漏掉“工作”目录，公开isError=true/file does not exist，随后正确路径Read isError=false；没有打开误路径下任何其他内容。
- 首轮大JSON统计对孤立代理字符做普通UTF8计长，产生被catch的UnicodeEncodeError，记录PARSE-FAILED；这不是产品解析失败。后以surrogatepass重跑成功，使用追加写保留首错和DONE-RERUN。精确scratch文件当前11473B/131行/SHA `cbc37d0e7a7ec3daf29e471231a0cce096f4f486cf010ad1bb38d91f61a1242a`，原样另存；它是含首错及后追加结果的现行混合文件，不能称第一版原件未变。

调用/结果精确坐标和公开错误见 `zcode-static-tool-first-errors-projection.json`。报告未明确逐项提这些本轮静态工具首错，是准确性补充；不可抹去原native记录，也不能把恢复成功当作首轮无错误。owner没有因此再次执行遍历、产品或oracle。

## 独立收件结论

现有独立agent已完成 `independent-zcode-terminal-intake-review.md`：9884B / `096b394c96a21b45d5d3567d9e58d6b14e0c19103607dbe339db64d8362011d1`，owner全文收读。它直接核官方原turncompleted、source=current副本=native Write公开content；五项旧缺口确有Read-call/result行覆盖，57项测试和--check均核紧随Python的EXIT=0而非复合shell末命令退出码。它未重做150实质审查，准确归属Z本方静态Pass；不代M或总控关单。两工具首错、混合scratch与main_turn/title纠错都已核明，原稿保全。

本目录是Z完成时的首批固定收件，M执行中状态只代表本批时点；后续M终态另加过程收件目录，不覆盖本批历史记录。
