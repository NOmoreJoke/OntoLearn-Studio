# directSteps 首候选预算独审

固定 `18908e4abca900a07a15a5d157d4022f2a11349a` 暂不通过。已确认一个提前归还候选持有票的问题；整流费用预扣未覆盖原严格 Reader 的既有逻辑扫描口径，需补明确上界或逐动作费用；非空 carrier 的 B 观测未接线。普通专项通过不关闭这些问题。

只读树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-profile-directsteps`；adoption `78e9cf7f26dc039e99ec6725d7de8a396d1298d2`；base `5f910b52c69d86a1076b2032e5d3c63e715947f3`。完整读本窗口输入目录的最新 AGENTS、共用指导、源码窗口、合同及预算、申请；读总控 layered-closure correction，并读 PRD FR-501—505 的一阶段/直接依据边界。未查网络、未扩大 SHACL 政策、未操作 Goal/GUI/服务/模型或修改任何源码测试。

`01-static-manifest.json` 逐141 current=固定Git=bytes/SHA；133只读=adoption，原139 adopted=各sourceRef；相对adoption恰六旧writer与两新件。模块51方法、40循环/推导式已全文读并建立行号清单。静态清单标准库命令的输出在工具历史，清单本身有完整成员hash；不声称这次静态命令有独立双流。两次实际产品运行则有完整 supervisor 元数据、独占basetemp、双流、exit/timeout、141来源前后及成员hash。

## BUD-01：候选仍被默认参数持有时归还临时票（P1）

固定 `semantic.py:466–470` 在 `additions = item = inputs = triple = basis = None` 后调用 end_candidates 并归还根的8×count objects。局部函数 append 的 `_additions=additions` 默认参数仍强持原 list，且每条 candidate 仍存原排序键。下一轮新建空 additions 后才重新定义 append，最终轮直到函数返回才放掉旧 callback。

`01-live-and-reader/stdout.txt` 的第一条实际 probe 用完整 domain→type depth2 图执行真实 producer，仅 wrap 原 end_candidates 并委托它，没有供应结果或费用。三个轮次 count=1/2/2；每次 caller 的 additions 均已 None，而 append.**defaults**[0] 仍为同一个含1/2/2条候选的 list。真实方法已经分别把 live objects 减4/8/8；外层随后继续减8×count。完整实际 ledger.events 一并保留，未从模型重建。

最小修复是在归还该批票前真正解除 append 的默认参数所持引用、排序回调及全部候选别名；不能只把 additions 设 None。保原 sort key、首插入规则与 L 顺序。新的固定候选须按同一 observer 确认默认参数不再持原 list。

## BUD-02：整流扫描票缺严格 Reader 的明确上界（P1）

`semantic_profile_production.py:110–117` 的通用块按每 pass `32J work +16J scan_copy`，接收端 `semantic_profile_restore.py:1434–1437` 使用四 pass，即 scan_copy=64×(J+2048)。这覆盖输入字节、普通树/缓冲的量级，但没有计入严格 Reader 固定白名单逐键比较的明确倍数；Reader 对每个候选 fixed key 按双串长度+1收费，且有两次扫描。

实际 probe 从同一次成功 producer 输出深拷贝 wire，把 warnings 改为1000个 `{day:null}`（都是 Reader 认识的 key），重绑真实 canonical payload/rows 和对应 caller-held digest，再调用完整真实 restore。Reader 完成后 A2 以 RESTORE_INPUT_INVALID 拒绝，未发布结果。J=46928；原 R 的实际 schema 费用3155868，D 的全部 scan_copy 仅3134464，甚至不含 R copy77558、wire140784、hash46974。较小10个对象向量也保留：J19203、schema1068948、D scan1360064。费用来自实际 RestoreLedger.charge observer，未供应任何扣费。

这是**现有显式逻辑费用口径的覆盖反例**，不是 CPU 指令或物理内存测量；R schema 本身采用保守双串长度上界，不声称每次 CPython 比较都实际扫描全部双串。现源码没有另一份严格证明可说明较小 D 常数仍覆盖同一新增模式的全量 Reader 工作，因此不能以经验32/16倍数签完整费用闭包。建议在调用 Reader 前按固定key表、两pass、重复key检查与实际新J给有限保守票，或提供可核验的逐动作预算；固定D cap不变，允许更早有限失败。原R金额和逻辑不改，不能用它替D付款。

## BUD-03：carrier B 观测未接实际路径（P2）

同一成功 producer 的非空 directSteps canonical片段为779 bytes，而 DirectStepsReceipt.carrier_bytes 为0。全产品 source 仅定义 note_carrier，没有任何调用；restore 同样不能得实际B。总 payload+rows≤M 会间接约束其中carrier≤M，因此本反例不是已发生越B上限；缺口是新receipt没有接真实载体字节观测，模块作者表中所述B检查不在实际链。不得把0当“未产生载体字节”。建议原唯一投影/编码链计入该子段的实际长度，或明示独立保守上界语义并接线，不能生成第二份 wire 来凑指标。

## 其它已核事实与尚待复核

独立 `02-budget-tests` 实际24 passed/41 deselected，exit0，0.71秒，141项前后相同。覆盖实际 producer/restore/roots 各四域 required exact 与 required−1，两个bootstrap不足128、128控制门、四尾故障、lower-only非法override和固定caps；实际fee事件逐case保存。未重复根的完整 npm check，也不把这些边界通过解释为上述所有权缺口已关闭。

固定新模块的预算实现已实质读取：双域128预门后才建 counters/events；每reserve同时预付当前与两条cleanup事件，scan_copy同时入work；二叉trie每byte八边、K累计含重复encode/get/put与长度头；identity不按Number归一；candidate含后轮duplicates；DP按实际union输入/输出与全N mask收费；capture carrier另持scalar；完成/失败不退累计费；receipt/最终events保守留票。root整流预界不构造第二投影，初步逐类型界覆盖canonical普通字符串转义、integerHex/bytes wrapper和固定record字段；它在原字段类型门前的foreign协议问题已由来源审另有实证，不在本报告重复运行。

原R opaque child block仍独立付款，未见修改旧cap/TermCache/version的行为；D普通流不能据此漏记Reader/投影/复制。未实测最大图容量、RSS、性能、T/S/H或跨workerΣ，也不把逻辑live计数当GC证明。本报告绑定首候选，不改写后续delta结论；待owner修复并冻结新ref后做必要复核，所有上述首证据保持原样。
