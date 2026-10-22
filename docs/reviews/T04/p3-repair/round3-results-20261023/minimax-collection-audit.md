# R3 MiniMax 正式收件独立增量核验

结论：本次 M 收件与意见处置的过程增量核验通过，未发现新增阻断。模型报告的有界 T04 S1 Pass 与总控的完整双审接收门分列；本结论不代替指定模型审查，也不自动接收双 Pass。F-R3-01 为模型保留的非阻断 P3，尚未修复、尚未关闭，交唯一 owner 判断，不改变冻结产品 5070004。

## 范围与方法

仅只读核验本目录 M 原报告、索引、17 成员归档、owner disposition、三组 helper 收据/raw、七个反例文件、归档中已知 11 个本人 probe 请求及必要结果、最小 terminal 标量，并对照两份本人 operator 原件。全文读取报告 380 行。未重审 42 项产品、已接收的创建包或完整原生输入链，未读取 Z 本轮意见、实际 native 源文件、后台或全局资料，未运行产品测试、GUI 或外部模型。只新增本审计文件。

## 原件、终态与收据

- 原报告 59,781 B、380 行，SHA-256 `fe23ab51aea1ded81ba87264377475b71d1676468c49e7dc3a75199e7dc1d612`。owner 展示原件、本人 review root 原件与归档 report 成员逐字一致。
- 归档 40,465 B，SHA-256 `34f57c27c4bc4628e539526768049b7ce19da5238ab3f1d33c227191a47da92a`。17 个成员集合、逐项字节数与 hash 均与索引相符；所列 raw、反例和持久结果亦与本人原路径相符。
- 最小 terminal 记录严格绑定 SID `mvs_4e9f4b2b7bdd47348293cdbb41f60109`、原 turn `659fd77a-9a0b-49c5-b39f-48aeb928d9f1`，`terminal_outcome=completed`、`updated_at_ms=1792701245588`，`currentFallbackUsed=false`。该记录与索引一致；数据库更新时间不另解释为独立完成事件时间。报告读取前后 hash 一致。
- 本轮两份 operator settings/acceptance 与已接收创建包中的本人对应原件逐字相同，未由 reviewer 改写。
- `mm-r3-full-check-01`、`mm-r3-ssr-01`、`mm-r3-component-01` 三组 helper metadata/raw 的 argv、cwd、起止和实际 exit 0 完整且相符。raw 分别支持 TS 719/Python 1167、SSR 14、组件 DOM 5 情景；组件持久结果为通过、requests 空、pageErrors 空。这里核的是原收据，不是独审重跑。

## 全部意见处置

D1–D4 的关闭结论及 owner 对应处置均保留：草稿原始 UTF-16 上限与固定 30 字符 trim、typed CSV 与字符串防护、最新 16 字段状态、visual 清理及保存身份/generation 边界。本次未重新执行这些产品验证。

F-R3-01 明确保留：reader 结果列名/实际 SPARQL 等长度口径与 Zod code point 口径可能在极端 astral 输入下不一致，造成偏严拒绝或定位误差。报告定为非阻断 P3，owner 未将其抹去、改称已修或在 507 内补丁。D1 的 draft 授权不外推为 reader 结果 contract 变更授权；后续由唯一 owner 决定 canonical 适配与验证。

正文 OBS1–6 均有对应处置，无遗漏：

1. 历史 10 项 closed 与旧 partial 保持原证据边界；新增 T09 provenance 不倒写旧结论。
2. 列名字符串的 min(1) 不等于列数组 min(1)，空数组/ASK 语义留父 canonical 适配器批准与边界验证。
3. 两处全局 CSS selector 的潜在集成影响保持为父 App 边界，无已证实碰撞或修复声明。
4. `staleReason.code` 静态类型较宽与运行批准校验的区别保留，类型收窄未冒称已修。
5. 旧 verification 的历史候选指针与 507 当前验证入口区分，原历史材料未改口。
6. 独审曾报告的 244 组内联探针缺完整脚本/raw/时间原件，仍不计为 owner 的持久运行证据，未补造或以重跑冒充。

owner 也准确纠正了报告开头“3 个观察”实际为 OBS1–6；“4 副本”是 3 个业务输入加 1 个 hash manifest；40 个命名 case 之外另有 120 次 trim 边界循环检查。报告中“唯一手段”仅可视为所选实现的说明，不能升级为排斥等价校验实现的政策。

## 自写反例的证据等级

归档的 Python probe 源码、40 个唯一命名持久结果和 T09 probe 源码/持久结果已核对。Python 结果无 error 项；T09 19 个 provenance 成员均匹配，四个 product copy 标志均为 true，mismatches 为空。持久答案支持 canonical/generated 均为完整 A01、Closed 后空集，以及数量相同但错误语义的 Closed/High 返回 A02。未重新执行 RDFLib 或这些 probe。

已知 11 个请求/必要结果归档为 21,866 B，SHA-256 `73b765a6067b9f024c41dfd47b7db23ce375ac21784cbe353b13761624cd748e`；严格本人 SID/turn、callId、必要结果字节数/hash 均相符。最终 TS/Python 摘要均为 cases 40、mismatches 空；TS 没有持久逐例实际规范化值，不能据此声称独立完成 40 条 TS/Python 规范化值深比。fixture 预期值检查、额外 case 接受性检查与循环次数也不混为同一种覆盖。

自写 probe 未具备三组 helper 那样的完整 UTC/实际 child exit 收据。pipeline 后的 `tail`/`head`/`echo $?` 以及外层工具 isError 不升级为 probe 的实际退出码。以下首败或诊断失败均有原件，不能称首轮全绿：

- 错 fixture 根路径导致 FileNotFound；随后两次读取含 `.repeat()` 的非法 JSON 均失败。
- `call_01a1654d77547629a93b4ff2` 的诊断使用 macOS 不支持的 `cat -A`，返回 illegal option，随后继续打印 JSON ERR；外层 isError=false 不等于该诊断全成功。
- 修 probe 的正则 replacement 曾报 `bad escape \u`，shell 继续运行产生成功摘要，不能用后续摘要抹去此前 Traceback。
- T09 首次 manifest 映射错误产生 product-copy mismatch，修正后持久结果才是四项匹配、mismatches 空。

这些均为已归档的本人 harness/诊断请求；没有据它们推定产品失败、审批拒绝、绕过审批或伪造，也没有把后续成功摘要升级为完整首败收据。

## 接收限制

本核验只检查上述已知 11 个必要请求/结果，不是全轮 native 请求合规审计。模型“未读 global/native/peer”等自述不能升级为独审确认的全轮合规、零曝光或零偶然显示。大 trace 的本地 hash 不能替代未归档且本次未读的全部内容。

原模型 bounded S1 Pass、owner 事实纠正及总控过程接收是不同层次。当前 F-R3-01 和相关父边界未关闭；真实 executor/App/IPC/Store、父验收、CI、两 OS 等既定限制保持。本次没有修改 507、测试或原报告，也没有自动开启下一轮任务或复测。
