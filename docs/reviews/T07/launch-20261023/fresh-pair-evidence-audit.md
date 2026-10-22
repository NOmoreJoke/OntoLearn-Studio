# T07 fresh pair 报告与证据边界独立核验

结论：**两位作者均给出“限S1通过”，但当前不能认定指定双审流程门通过；保持PENDING，不能据此push/PR。** 已确证候选与封存材料的本地字节身份；官方全文Read/调用退出/正式终态仍缺，MiniMax明确执行偏差尚不能自行豁免。本审计不推翻或代签作者工程结论，也不把其P3登记变成父验收通过。

审查者 `/root/t07_round1_document_audit`；2026-10-23。只后台读取精确命名的两报告、各自角色raw/validation、明确命名的input/verification/operator元数据、派发正文及owner快照/处置文档。只写本报告；无CUA、产品/测试执行、候选修改、外部模型调用、全局会话/配置/未知元数据访问、stage/commit/push或向审者互传意见。

## 受审对象与确证

| 项目 | ZCode | MiniMax Code |
| --- | --- | --- |
| 精确native SID（operator官方菜单收据） | session_488117259b5e999c5321f8a1141cefd6 | mvs_bfa6c40659f6405391d5de2bbb8cbc0f |
| 任务UI设置收据 | GLM-5.3 / 最高 / 完全访问 | M3.1-Flash / xhigh / 始终授权 |
| 作者结论 | 限S1通过；4项P3/观察 | 限S1通过；3项P3 |
| 报告实物大小 | 19230字节 | 30205字节 |
| 报告SHA256 | 8ee32ae5adad3f47959f479d8e855f38f9ecaccdbbde800a864a83c57f7006f7 | 050a018a762fe28a6e8b52a6b0badb6ccd3ad93ba6d657cc35b0c4451ca3eb6f |
| 本地完整输入大小/SHA256 | 143012字节 / bfd74c930cddbc9274ef05e30f7c3eaf482a56ff3caa5a10718fdc30128c7287 | 143054字节 / 153dc55dbae5e3b27b8ae65e0a74f14e1da01c36398cffa477691269f7e325dd |
| 官方turn / terminal / 原生完整Read | 尚未核实 | 尚未核实 |

两树实际HEAD均为reviewHead `24f3703ecf4fce75e0d0375f7291ed928f083c41`，产品/测试为 `f9a1157c2fff06c8bef17fa1ec44d8eb1ebacad3`，base为 `5f910b52c69d86a1076b2032e5d3c63e715947f3`。独立逐项哈希确认两树14项实现/测试/fixture均等f9；当前Git状态均只有受保护AGENTS、派发输入目录与本方报告。两份full-input字节/SHA与operator已受理收据相符，且分别以原冻结prompt的精确字节为后缀。

operator收据是本任务workspace、UI设置、官方菜单SID与附件受理的记录，不是工具自身的完整原生Read/终态导出。Z提交前acceptance里SID UNKNOWN是历史快照，最终报告引用accepted收据真实SID，不应回写旧记录或把两者误判为不同任务。

已独立验证owner `fresh-pair-snapshot/snapshot-index.json` 的25项副本，逐项对实际命名source字节、大小及SHA相同：2报告、7元数据、10份Z日志、6份M探针产物。index SHA256 `5fa77c96fa4dd0ceaa43e031b56f38e5bef44954f1eed8aa40c22064e76e1d1e`。另核 `fresh-pair-local-evidence.tar.gz` 1620647字节、SHA256 `ce2e54279a87b26d4a2dbbbf5297c4c68ae9051bc952f06277d5030568632485`，26个成员（25原件+index）逐字等快照。未仅信索引，未解包覆盖原树。

## 阻断项与缺项

### B-01：真实官方回合、完整读取与终态门仍未满足

双方accepted收据均明确 `fullNativeReadChainVerified:false`、`officialTurnId:null`、`terminal:null`；owner retry index与snapshot同样保持pending。报告里的“本报告即最终输出”或“本会话已全文读取”是作者声明，不能自行证明正式terminal、完整原生Read/tool链或完整回合所属。Z报告第16行以本报告自指最终输出，第129行仍turn UNKNOWN；M第36～44行如实保留task/turn UNKNOWN。平台若无另行task ID，可诚实保留该项而使用已确证SID；不能为了补齐字段猜测ID。

本地full-input与operator hash相同只证实文件身份与受理收据相符；Z acceptance将“单一文件哈希”解释为官方附件逐字一致，仍不能独立证明服务端原生已全文读取。需由owner沿支持的官方定向只读/导出路线，对两个精确SID核回合、全文输入/Read及真实terminal，并绑定到当前报告hash；本审计不另建/resume任务、不读全局配置、不用私有HTTP补真。当前不能把报告存在、作者结论或进程状态回填正式通过。

### B-02 / P2流程偏差：MiniMax违反明确的固定树只读运行边界

M报告第223～230行及 `minimax-review-record-20261023.json` 第93～96行自述首次以固定review checkout为cwd执行render-probe，原位重写ui-probe.json与两PNG。派发full-input第340～376行明确禁止原位执行，并要求在独占scratch固定Git副本调用、保留副本清单与新原始输出；这是具体限制，不能被普通测试权限或桌面政策撤回覆盖。

独立核验当前checkout三件、inplace-run三件与scratch-run三件均与封存字节相同：JSON `6e5edcec50ee0bffcb0e63c3f2e39023ab5379297cbe1cb64688f204f8361ba8`，wide `32ede79bc9dc5330e9a6d7082223f41baf808ce0d812d8808a0492146461216e`，narrow `1ee10753e7b467eea745ae14f4ea907d168d43f01a40aae80a7ef9e0e03ca3ec`。因此当前无产品/证据字节漂移的限定判断成立；但这些相同产物本身不能证明调用位置、先后、scratch来源清单或退出0，原位越界也不会因后来相同结果而消失。

保持原报告、两组产物及旧封存不覆盖；把原位运行登记为违规执行，不计作合规复验。所谓scratch纠正只有取回对应原始调用/退出与副本身份记录后才能按其实际范围采信。该偏差须owner/root独立处置并记录是否接受后续恢复条件，不能由报告作者或本审计自行豁免；也不在未发生产品/base字节变化时擅自断言必须重开双方整轮。

### B-03 / P2证据缺口：MiniMax命令运行与退出证据尚未提供

M报告第105～114行和review-record.verificationRun自填46/44/27/657/1142及exit0；本次明确指定的raw/validation目前恰有inplace-run、scratch-run两组三件产物，没有这些pytest/vitest/check的原始stdout/stderr、起止时间或退出回执。六件UI产物不能证明check执行或退出码。不能据此断定命令未运行或伪造，但当前只能记为“作者声明，未独立取得执行证据”。

Z的raw/validation/009、010、011分别确有90 Py、27 TS及check全链657 TS/1142 Py通过输出。011全文覆盖lint、format、三份tsc、vitest、构建、ruff与pytest，根目录/计数与报告相符。其SHA256依次为 `49ec9fd2768c741cf3fb9f8b3fa657e16cb99402e634a03c80b2908d16203b6a`、`cf403e478bfcefe484781430e13c49686aae9661dc15e30f323c2f8cfcaf1ec6`、`dffe6730bbd65d9898668fbef900fb2591c0ee32c2ed6d9109b787dd9a53cb65`。这些确证“已保存通过输出”，但日志不含官方invocation/exit事件；summary所写exit0仍须官方链对应，不能由本审计把stdout反推为官方退出证明。不要通过owner额外重跑替代原审查运行记录。

## 需要修正或澄清的报告表述

1. **M最终报告绑定不一致。** review-record第91行reportBytes=29378，而实物30205；该元数据没有当前报告SHA。Z verification-summary的19230字节/SHA则与实物相符。owner快照已准确封存M的30205字节，故实物可追溯；旧元数据仍须标为旧/未同步记录，不覆盖原件，不能单独充当最终报告绑定证据。
2. **M历史原件数量矛盾。** 报告第97行称“全部32个log/PNG”，archive-manifest与归档实际为35个。报告另称75/75 hash全匹配，不能以这个hash总数自动证明35原件已完整读过；须由作者或官方Read记录澄清32是笔误还是读取范围缺项。Z第36行将“25路径全部内容”与candidate.patch“哈希层”、t09-e5“结构/关键字段抽验+全量hash”并列，也不足以仅凭报告证实派发要求的完整源码/fixture/PRD全文阅读，需在原生读取链核对，不能把hash等同通读。
3. **9条rawLineSha256的准确含义。** 本审计只读各自封存JSONL，以 `splitlines(keepends=True)` 保留原行换行，直接逐行SHA与sources索引比对，双方9/9均匹配，payload.id亦逐项对应；没有读取sources指向的原sourceSession。故M第67/76行在“封存原行与索引一致”的限定含义下可成立，不据此指控其必然越界或读取原会话。这不证明当前重新打开了源session，也不证明本轮官方Read。
4. **Z原行核验失败不能归为必然不可核。** raw006保留早期字段取错/0-of-9与DIFF结果；raw007仅核消息正文 `strip` 后等价9/9，不能替代原行字节比对。Z第41/94行“本角色无法复算”过宽：不能跟随源session，但封存原行本身允许且确实可复算。无需改历史失败日志或读取源session，追加准确更正即可；这是证据方法说明，不是新产品缺陷。

## 工程意见、范围与处置文档

已完整阅读两份当前报告。两方均覆盖完整S1私有候选的25路径/14项、历史IR-01～05及原验收，明确保留真实T05/T06、T01/I04生命周期/取消/原子进度/终态/对账、公共契约/bridge/App、真实删除/恢复/快照续跑、完整E5四类领域结果、T10跨设备、FR-700～705父验收、双OS/真人/CI/远端/发布门。没有将合成端口或资源投影改称父功能完成；作者各自P3分级是其判断，本审计未重新代做产品算法审查或代签严重度。

只读审阅 `fresh-pair-findings-disposition.md`：7项P3/观察均有登记；保留冻结、不在当前候选临时落实新契约/实现、按相应owner在接线前固定责任，以及对原位违规/缺原生证据不自行豁免的表述准确，未发现扩大授权。该文件为owner处置登记，不是官方模型终态或完整父验收。涉及本报告列出的数量/最终报告绑定/Read范围澄清仍须补正；任一实际实现/测试/契约/配置/依赖/验收/base变化，按原规则新候选与双方全新完整审查。

## 核验过程与边界

本次只运行文件/Git/JSON/tar/SHA比对。核26成员归档时首个本审计脚本重复拼接fresh-pair-snapshot目录，FileNotFoundError后改用实际归档相对launch目录解析，26/26字节匹配；这是审计脚本路径错误，未改归档。尝试读取owner提及的read-route-status.md时文件尚不存在，未据不存在推断官方路线结论，也未等待或扫描替代路径。官方链取证后应另补真实记录，不改写本时点快照。

**当前可确认：本地候选身份与封存准确，作者各自声明限S1通过；当前不可确认：两任务的官方完整Read/调用退出/正式terminal以及M运行证据和执行偏差处置已完结。指定双审门、push/PR与后续父验收继续未放行。**
