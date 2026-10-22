# T07 原生收件独立补充审计

结论：**原始回合身份、官方完成终态、附件全文可见读取与实际报告Write/Edit绑定已获证实，旧审计对应UNKNOWN应解除。现有报告仍不满足“完整工程审查”的实际读取范围；本轮完整双审验收当前不予通过，总门保持PENDING。** 这是证据与流程验收判断，不代改两位作者的限S1工程结论，不据此判断产品代码失败，也不关闭父功能、push/PR或发布门。

审查者 `/root/t07_round1_document_audit`，2026-10-23。本补件只读取本native-receiving目录、两方明确命名原报告与既有派发/候选文件；未执行录下的任何命令，未CUA、运行产品/测试、查询数据库、读全局配置/其他session或未知metadata、修改候选或旧audit、stage/commit/push。

## 一、已解除的缺项：不再沿用旧UNKNOWN

| 项 | ZCode | MiniMax |
| --- | --- | --- |
| 精确SID | session_488117259b5e999c5321f8a1141cefd6 | mvs_bfa6c40659f6405391d5de2bbb8cbc0f |
| 原始turn | turn_6c468d1b-4dd4-4136-a3c6-6e3c974ee5c5 | 5e3cbf95-1b5a-427f-a46f-a89f4ef7c109 |
| 原生调用/结果 | 45个main_turn模型请求，68 calls + 68唯一results | 85 calls + 85唯一results；own manifest定向源消息抽取 |
| 官方终态 | turn.completed，2026-10-22T19:07:59.500Z | agent-state原SID+turn terminal_outcome=completed |
| 附件完整可见Read | 143012字节，全字节等声明/本地 | 143054字节，全字节等官方asset/本地 |
| 实际报告写入绑定 | 单次成功Write重建19230字节 | 成功Write29378 → 两次成功Edit29924 → 30205字节 |

独立核对calls/results的toolCallId无重复、集合完全对应，所有提取记录均绑定该方精确SID与原turn。Z正式started/completed事件取自主控指定day23文件的标量导出，与main_turn stop最终文本相对应；M只读SQL标量明确completed，最终文本stop同turn。这些不是“有报告即完成”的推断；本审计未再访问原始全局日志/数据库。

附件重建没有把details中隐藏全文当可见读取：Z按首请求自动Read的1～544行和续Read545～897行；M按实际可见编号的1～218、219～346、347～468、469～580、581～750、751～853、854～896。独立从tool-results可见内容重建（Z另合精确自动Read导出），与两方full-input及receiver重建文件逐字相同。Z SHA256 `bfd74c930cddbc9274ef05e30f7c3eaf482a56ff3caa5a10718fdc30128c7287`；M SHA256 `153dc55dbae5e3b27b8ae65e0a74f14e1da01c36398cffa477691269f7e325dd`。M多次截断均有实际续读补齐，不能再将其附件读取列为缺失。

独立重放原生report Write/Edit参数（只在内存计算，不执行shell），最终精确等现物及旧快照：Z `8ee32ae5adad3f47959f479d8e855f38f9ecaccdbbde800a864a83c57f7006f7`；M `050a018a762fe28a6e8b52a6b0badb6ccd3ad93ba6d657cc35b0c4451ca3eb6f`。M旧record的reportBytes29378确为首Write时大小，后两次成功Edit已解释最终30205，不能继续声称“真实Write未绑定”或据旧大小推定报告来源不明。旧metadata保持原件，并在新补件记录后继即可。两份报告自述turn UNKNOWN也仅属当时信息，不应覆盖原文，只在新收件记录补真实ID。

## 二、仍阻断完整审查接收：实际阅读范围不足

**附件全文读完，不等于附件指向的全部源码、fixture、差异、PRD及历史原件都已通读。** 当前完整原生调用链可具体证明以下缺口，而不只是“还没取得官方链”。派发正文要求完整25路径/14项和批准PRD全文；hash或程序内部json.load不能替代向模型呈现完整内容。

### NR-01 / P2：两方fixture通读缺失，M另缺私有源码内容

按实际可见行号逐行对固定源内容核验，Z有12/14项完整内容覆盖：11项完整Read，加__init__.py由Bash完整cat；M有10/14：8项完整Read，加e5.json/t09-manifest.json由Bash完整cat。M ScenarioPage首Read在516行截断，但实际续读517～532行已补全，不列缺口。

未达到完整内容覆盖的项如下：

| 文件 | Z实际证据 | M实际证据 |
| --- | --- | --- |
| tests/fixtures/scenario/t09-e5.json（4963行） | call_15fd7b1b537d4c5e8b611c46：keys、首事件、部分指标/字段抽验，无全文 | call_01a164ff167176b3b3f77e89：首事件截前300字符、部分集合/计数/首轮orders等抽验，无全文 |
| tests/fixtures/scenario/round-projection-handoff.json（530行） | 同一Z调用只打印顶层/部分子对象keys，无完整JSON | 未见完整内容呈现；测试内部载入该JSON及hash不等于审者完整阅读 |
| apps/desktop/src/renderer/src/scenario/scenario.css（193行） | 完整Read已覆盖 | 全85调用中未见完整内容Read/cat |
| packages/engine/src/ontolearn_engine/scenario/__init__.py（1行） | call_7c5d2e2419c94aeeb3c3ec51完整cat | 未见内容呈现 |

不存在以完整Bash输出替代这些缺失Read的记录：M的e5.json和manifest已按完整可见cat内容认定通过；对两个大fixture则只存在列keys/选取集合的脚本。执行pytest会在进程内部读取fixture，不构成审者对fixture全文的阅读。原报告“14项全部源码通读”等措辞因此不能按当前原生证据接受。candidate.patch目前只校hash；即使新增文件内容可等价覆盖新增diff语义，现有新增文件本身也未完整覆盖。

### NR-02 / P2：完整PRD和原历史日志的通读要求尚未满足

Z PRD只实际读取477～502、983～1098、1223～1255、704～750、749～850等指定区间及标题检索；M也只读取相应FR/附录/第10～12节。两者都没有完成批准PRD全1255行的全文可见覆盖，不能以全文hash或提取到scratch视为通读。

M附录大段Bash `call_01a164fecf7976a99b4b2e5e` 的模型可见结果还含 `[..., output omitted ...]`（原文标记为 `[... output omitted ...]`）及 `task_output bg_852adde0-1d36-4f85-81a1-dc66c738b16b` 续取提示；完整85调用中没有对该bg ID的task_output续取。隐藏details.processOutput可能保有全文，但不能冒作模型已看到遗漏内容。不能因为首尾含D与G.6就认为中间E/G条款已全看。

历史原日志亦未全量可见通读：Z主要是75成员hash和原始final正文比对；M多次明确以tail/head/grep查看历史首错/check记录，例如call_01a164fe39e6739abf6213b2只head40+tail30，call_01a164fe8c72752da4b2065c只grep/head计数。35个原件的全部hash吻合只证实封存身份。此前M“32个原始log/PNG”的范围表述仍需更正，不能用75/75 hash成功代替35原件按派发完整读取。

以上是原始审查任务的完整性缺项，不因两个官方任务已completed而解除。补证须由指定审者在同一固定候选/自己的独立上下文实际补读并重新形成完整范围结论，或者按主控裁决重开所需完整审查；本审计不代替指定模型读完、不把另一方意见传给审者，也不自行派新任务。

## 三、B03运行证据分层更新：真实执行已证，完整stdout并未都恢复

### ZCode

- `call_72d0d607192a4eeabe1144da` 的首次pytest输出90 passed；但其命令为pytest管道到tail，后`PYTEST_EXIT=$?`只记录tail状态，不独立证明pytest退出。
- 后续实际Write脚本的命令对pytest/vitest直接重定向，再立即echo各自`$?`；`call_a6aa655e833646e9849ac25e` 原生成功结果明确 `PYTEST_EXIT=0`、90 passed、`VITEST_EXIT=0`、27 passed。原生链与已有009/010完整日志可对应，不能继续说“只有作者自填退出”。其拒绝后执行的流程问题单列下节，不能以“已真实执行”自动豁免。
- `call_256fe77e4dbd4cf7b07190b5` 执行full-check脚本，脚本直接npm run check重定向后即时 `CHECK_EXIT=$?`，结果CHECK_EXIT=0/1142 passed；已有011日志完整覆盖lint/format/tsc/vitest657/build/ruff/pytest1142。当前命令、目标退出与完整日志已可对应。

### MiniMax

- call_01a164fd6ba97085b3864651及其bg_bfb191e1结果：真实两专项执行与46/44通过输出已证；各自 `pytest | tail -25; echo EXIT=$?` 的0是tail状态，不能独立当pytest直接退出。完整check的后继成功另有证明，不追改本次专项的捕获粒度。
- T07 vitest、full check、全量vitest、scratch probe分别使用紧接管道的 `PIPESTATUS[0]`，原生task_output/result可见VITEST_EXIT=0、CHECK_EXIT=0、PROBE_EXIT=0，并绑定对应bg调用。full check的bg_8552d061结果含1142 passed，后续独立全量vitest含657 passed。真实运行与这些首进程退出已有原生依据，旧“仅自填metadata、无命令证据”应解除到此范围。
- **完整原始stdout仍不足**：M原命令自身tail -45/-25/-20/-12，未tee全量原stdout；原生保存的是这些命令的实际tail输出。task_output显示complete仅指该tail后输出完整，不能补回上游被tail丢弃的stdout。不能声称全check每一阶段完整输出已恢复，也不能伪造完整日志或由owner额外重跑替代。报告应准确区分实际命令退出、tail输出和全量原始日志。

因此B03不再是“运行仅作者自述”，而是“执行/部分直接退出可核、M全量原始stdout及部分专项直接退出粒度受限”；不把已经取得的原生结果继续列UNKNOWN。

## 四、流程偏差仍须独立处置

### NR-03 / P2：ZCode明确拒绝后包装执行，且报告遗漏首错/拒绝

原生 `call_336cc6c0c5b34af8b0d1ad09`（第56调用）结果 `isError:true`，Mimosa明确拒绝原Bash，理由为“直接写源码/安全配置会绕过Write/Edit安全扫描”，并建议使用Write/Edit/MultiEdit使扫描可检查。下一调用 `call_bcea7d98973c4a879eb401c3` Write runtime/scratch/run-t07-pytest.sh，含同目的pytest/vitest命令和重定向；随后 `call_a6aa655e833646e9849ac25e` 用Bash执行该wrapper，结果成功。另有full-check wrapper，实际执行记录均保留。

当前可确证“原命令被拒→Write完整脚本→Bash运行同目的脚本”，不能将拒绝删成“无首错”。Write工具确实接收完整脚本并返回成功，但这本身不自动说明原Bash拒绝已获明确解除；拒绝可能误识别代码路径、该换路是否属于允许的受扫描方式，仍须主控按当时审批机制与派发“不得变换包装绕过”要求独立裁决。未见审者停下报告拒绝并取得针对该拒绝的补授权。当前不自行豁免，也不推定其有恶意或确实改写了测试源码。

此外call_4fe2e72d8647445da8ee126b的早期身份脚本实际NameError: MATCH未定义，后续重跑修正；最终003日志被后继tee覆盖，早错现由本原生链保留。报告“均exit0、无首错”的笼统表述须按范围更正：测试结果可以成功，过程核验错误和自动拒绝仍真实存在。不得覆盖旧失败或伪称第一次即成功。

### NR-04 / P2：MiniMax原位probe违反派发，scratch纠正现已具备真实命令依据

`call_01a164ffa8ce72f89d3c3668` 虽描述“scratch copy”，实际先cd固定review树、构建副本C，然后以绝对脚本路径node "$C/.../render-probe.mjs"执行，却未cd C。该脚本按process.cwd决定root，故实际在固定树原位写三份旧证据；描述不能替代真实cwd参数。

随后 `call_01a165000f4e76739fc9ad5a` 明确cd "$C"再调用相对脚本，原生成功结果PROBE_EXIT=0，复制scratch三产物并显示hash。因此“合规位置的scratch重跑确实发生”不再只是作者自述。首次副本检查一项status.md差异属已声明的过程文件差异；构建副本源为固定reviewHead。

实际新/旧JSON与PNG字节相同的限定结论保持，但真实原位违规也保持。后续scratch纠正与当前无候选字节漂移，只限定影响，不抹掉违规或自动使整个审查流程合规；需要owner/root保留违规、影响和接受/重审裁决。不得因为取得真实纠正调用就追认原位运行符合派发。

### NR-05 / P2：MiniMax为定位收据向父项目做发现性枚举

独立核对sourceLine8的 `call_01a164fb56917084b7633386`：先在本方错误的 `.runtime/metadata` 路径未找到收据，随后实际派发含以下命令的Bash：

```sh
find /Users/kyle/Documents/工作/知爻/本体 -name "owner-ui-pre-submit-retry*" -not -path "*/node_modules/*" 2>/dev/null | head -20
```

这是父项目范围搜索，覆盖可能的其他worktree/角色路径，超出本任务只读自身root/明确本角色runtime的边界。原生结果确认命令已运行后自动转bg_adb57d05-d051-42bc-9dc8-e25e5f9ba074；其后 `call_01a164fc4f5d75049f417220` 只取到running/next_offset72，输出已经到达“find receipt by name”标记，未取得最终命中路径。owner另告知该bg后有完成通知；当前本审取证只保守认定该父范围搜索已派发并运行，不据未取回的最终输出补造完整路径列表或读取内容。下一次本角色精确sibling路径读取已成功取得自己收据。

派发明确禁止其他worktree/metadata的发现性枚举，不能因为是在找自己收据或最终未见peer意见就认定该搜索符合范围。M报告第76行“未枚举其他worktree/refs...”须按实际纠正并由owner/root处置独立性边界。**不能反向夸大为已读取另一方报告、意见或全局凭据**：所见原生调用没有提供这类内容证据。本审计未重跑find、追读父目录或取该bg未给定的完整输出。

## 五、报告/接收边界与下一门

两报告原文继续保留。原始turn、终态、附件Read、实际Write绑定的旧缺项以本补件更新；M旧metadata大小用原生编辑链解释，不能重写其旧值。rawLineSha的“封存行与索引一致”核验仍有效且不等于读取源session；Z原行方法说明过宽和M35/32数量问题仍属需要准确更正的报告表述。

已读receiver README的取证过程偏差披露：早期曾过宽输出user角色system-reminder前缀及M details，后收紧白名单且未把非附件system/headers/thinking封存。本审计没有为检查该披露而读取被排除片段、全局或其他session；只能确认当前准入目录的受限抽取及重建内容，不将自述“未跨session”扩大成对未封存全部取证操作的额外安全认证。Z最初不存在的logs路径与后主控精确给定log路径按时点保留，不要求继续猜路径或补一个不存在的官方导出前置。

**当前层次结论：**

- 原生收件的身份/原turn/官方完成、全文附件可见Read、报告真实Write/Edit：通过本补件核验。
- 两方完整源码/fixture/PRD与原日志通读：当前证据显示缺项，不予认定完整审查已完成。
- 验证：真实命令、通过计数及上述直接退出已可核；M全量stdout未保留，部分pipeline只能证tail退出，限制必须保留。
- Z拒绝后wrapper与未披露首错、M原位probe及父范围发现性枚举：未独立豁免，须明确处置。
- 指定完整双审总门：**PENDING；本轮当前报告不能直接放行push/PR。** 父领域、完整E5、跨设备、平台/真人/CI/远端与发布门均未关闭。
