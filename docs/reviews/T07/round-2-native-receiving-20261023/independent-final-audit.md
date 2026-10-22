# T07 R2 原生收件独立最终审查

审查者：`/root/t07_round1_document_audit`。仅静态读取本任务明确封存与导出副本；未运行产品/测试、未访问动态原生或全局实物、未改共享文件。

**本地封存一致性和两份报告真实写入绑定通过；指定完整双审门不通过。** Z 作者 NotPass；M 作者“限 S1 PASS”原文保留，但完整阅读证明不足且存在本轮越界写入，不能放行。

## 确证收件

- M 44 个、Z 14 个源封存索引文件的大小/SHA 均匹配。M 截获 89/89、Z 139/139 调用和结果 ID 唯一且对应；M 计数不包含已经压缩丢失的早期调用，不能称整个原 turn 的完整调用总数。
- 原 SID/turn 都有正式 completed 和公开末答；报告旧 UNKNOWN 按产生时点保留，不继续视为当前身份/终态缺项。completed 只证明回合结束。
- M `call_01a1658a1af375eca91f552d` 成功 Write 的内容与 34061 B 报告逐字相同，SHA `ee282bd9297ef05c174a4037968d49f90b734ec00c0066081d426797ae5c3307`。
- Z `call_2d79eaa4e3ca4efaa9880717` 成功 Write 的内容与 14464 B 报告逐字相同，SHA `b8923de36fde820c4e87373af55270a48eeeab97a22d6cb38122612d6625fbec`。
- 复用当前 R2 前段已独立完成的实际返回重建证明：Z 输入三段 1–588/589–1148/1149–1701 连续 join 为 242491 B，14 项源码 fixture、完整 patch 与 PRD 匹配冻结清单；没有用 expected 补字节，没有重取旧 R1 原生。

## 实质发现

1. **P2：M 越界写入未披露。** 第 83 调用 `call_01a16589548875cb80205d78` 成功向授权 runtime 之外的 `/Users/kyle/.minimax/v2/assets/t07-r2-ledger.json` 写入 45 B；下一调用清理并列举全局 assets 顶层。超出唯一写面，清理不抹除事实，报告未披露。未据此推断读取他人正文。
2. **P2：M 完整阅读和 PASS 无充分证据。** 早期原生文件压缩丢失完整读取链，242581 B 附件身份不能替代模型可见全文。报告第 65/84/195/219 行宣称全部 EOF，ledger 却有 38 项标注 `not independently re-read this round`，并统一 `eofConfirmed:true`。该声明不能由现存返回补证；证据不足不等于证明从未读取。
3. **P2：Z 历史日志全文声明过度。** 报告第 38 行和 ledger 的 33/33 FULL-EOF 不成立。`call_1e5449b354504b458c104510` 对六份 check 日志只输出关键行；`call_620c2b32c1ff43bebab35d50` 经 `head -c 13000` 实际返回 READONLY 正文 12970 字符并出现 BrokenPipeError，`call_1e83fff215a843f697dbb6f0` 从字符 13000 接读，缺 30 字符。这独立于作者已经披露的 G-1（历史 M results 结构扫描及选段）。
4. **P2：Z 超出明确写面。** `call_e34b751fa60f4a91ae806490` 成功 `tee /tmp/t07_r2_diffpaths.txt`。冻结前缀第 33 行只允许本方 raw/validation、reports、指定 reviewer metadata 和唯一报告；该写入越界，与报告第 30 行自述不符。本审未读取或清理 /tmp 实物。
5. **P2：Z 历史关闭映射错误。** 报告第 75 行将 IR-03 写为项目/引擎/锁身份；实际历史定义为删除最高序号工单后复用历史 ID。该表不能作为本轮正确逐项关闭记录，历史原件不改。

## 验证与边界

- M 005 probe 的原调用已确证实际 cd scratch/probe-copy、打印真实 pwd、相对路径调用原脚本、直接保存目标 rc=0，双流均空；后置 ls exit1 独立保留。该成功不消除其他越界。
- M 001–004 完整形态双流、通过输出和 exit 文件存在，但原始调用位于压缩缺口，现有链仅后续查验和作者 ledger，不能独立确认原入口、直接目标退出的完整因果链。
- M 本轮首错包含 wc 目录 exit1、四次 Read ENOENT、后置 ls exit1，均非自动审批拒绝。
- Z `call_67be7300c0dc4552845dc9c0` 确为验证入口，被自动拒绝后未见同目的脚本/包装/替代验证，三必要验证仍 UNVERIFIED。可选 probe 未跑不新增必跑门；“误报”仅为作者判断，解除须 root 精确裁定。
- P3 精度：M 报告 runner 行号应为源码 159–160，非 2108–2111；006 实际输出完整 rounds/checkpoint 不相等，语义子集相等由 007 支持，须分开归属；ledger 的 007 exit 路径另有名称笔误。新 P2/P3 原文保留，不由独审接受或关闭。

## 导出脱敏

仅 M results 第 84 行（`call_01a165896d9070ac8817c5d7`）变化：遮蔽 content、processOutput.stdout，新增标记；原 stderr 为空未变，执行状态/退出码保留。原序列化记录 1059 B（不含 LF）及 SHA、stdout/stderr 大小/SHA 均与声明一致。其余源索引文件（含两报告 Write、附件与全部 Z 文件）逐字未变。原始源索引改名 freeze-index.source.json；导出实际字节由 export-index.json 独立列示，不混淆。未公开全局列表中其他条目。
