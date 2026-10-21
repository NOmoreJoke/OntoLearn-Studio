# directSteps 最终候选预算 delta 独审

结论：固定 `cb2662c2ea4014d3de06194442f462c17eabe23b` 的本窗口预算范围通过。首候选的 BUD-01、BUD-02、BUD-03 已由实际修复与独立反例复核关闭；未发现新增预算阻断。该结论不替代来源/schema 独审、正常全量 check、指定外审或父模块正式接线验收。

## 固定输入与证据绑定

本树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-profile-directsteps`；base `5f910b52c69d86a1076b2032e5d3c63e715947f3`；adoption `78e9cf7f26dc039e99ec6725d7de8a396d1298d2`。初审固定18908e4、产品修复固定ff90092、最终产品cb2662c分别逐Git读差异，不将前一版初审改写成通过。

`candidate-cb2662.json` 与根的 `candidate-cb2662c.json` 指向同一最终产品141项；逐current=Git=bytes/SHA，133只读=adoption。ff90092→cb2662c只有新增测试的173行，七个产品源码逐字相同。测试原35520字节是最终42828字节的精确前缀；最终测试SHA为 `7bd1b63fbdcaf70d0a78efa4432c1b6091f91d96758988a86b5764b5c5d4b708`。

首审30件原始材料由 `initial-members.json` 冻结，最终静态探针逐件重新核字节和SHA，全未改动。初审静态清单命令只有工具历史的记录限制仍原样保留。新增delta运行使用完整clean env、自有.venv、独占basetemp、完整argv/cwd/HEAD/固定产品/起止/exit/timeout、141来源前后、双流与费用事件；不把初版overlay环境冒作clean env。

## BUD-01：先解除回调引用再归还候选票，关闭

ff90092 的 `_finite_closure` 现在在 end_candidates 前将 additions、item、inputs、triple、basis、append、addition_key 全设None；原排序键、生成顺序、L debit/union 与首次插入位置不变。追加的exact私有capture门同时阻止外来callback进入。

`delta-ff90092-01-probe` 重用原depth2真实producer，仅替换observer对缺失回调的读取方式，仍委托真实end_candidates。三个真实轮次count=1/2/2，均观察到 append=None、addition_key=None、原list已不再由default持有，然后真实方法才减4×count票，根随后归还8×count。局部候选/排序别名均已解除；模块step/seed独立票继续保留。没有将账面归票说成CPython/RSS回收证明。

## BUD-02：严格 Reader 全流逻辑扫描先票，关闭

新的R入口在 `ledger.begin` 与任何Reader之前，为D新增一次不可退款 `scan_copy = 3343 * J`，J为实际payload+rows+input+source四份字节总和，scan_copy同时进入D work。旧R cap、TermCache、版本、默认key表和原收费顺序不变；原普通流4-pass `(J+2048)` 块继续存在，未用原R支付新增D票。

独立核算：schema2固定n=114、全部固定名长度和L=1060、最大名长度m=25。四份流内所有已解码key字符长度和≤J。key数q≤J/3：完整前缀每个key至少有两引号及冒号；唯一截断/unknown尾key即使尚未验证冒号，对象开括号补足该一个字节，因此不能把未读value算作已有字节，但全流q界仍成立。第一pass失败时第二pass不运行，按双pass仍是保守上界。

fixed-key扫描双pass≤`2*n*J + 2*(L+n)*q`；每object最多32key的prior检查双pass≤`64*J + 64*(m+1)*q`。代入q≤J/3，合计≤`1629⅓*J`，小于3343J；schema1表更小。新增四个key的长度已纳入L核算，尽管源码factor使用旧表长度和，该factor仍有充分余量。源码余256J dispatch项和保留的普通流块覆盖字节扫描/decoder控制的其它固定委托，不依赖第二钱包。该证明沿原显式逻辑字符串比较上界，不声称实际CPython每次会扫描全部双串。

同一真实反例的10个/1000个warnings对象仍完成实际Reader后在A2拒绝，无成功结果。1000例J46928：D scan_copy实际160014768，原R schema3155868（以及copy77558、wire140784、hash46974）均在新先票范围；完整原始事件保存。新增10000例J298998在追加D预票时即 DIRECT_STEPS_LIMIT/work；R charge observer为空，说明拒绝发生在原R/Reader之前。该较大例只能记有限先拒，不冒称执行到A2或扩大容量。

固定cap仍为work/scan_copy各581671040、objects270635588、scalar50331776。新保守收费会缩小可接收解释物料的范围，合同明确允许有限早拒；本审不承诺原8MiB上限内每个有效输入都能解释，也未测量性能提升。

## BUD-03：实际carrier字节接线，关闭

生产在原唯一 `_ProfileProjection.value(result)` 后，把已经产生的safe_result.directSteps交给 `_direct_json_size`；恢复对严格Reader已读的同一raw.directSteps计数。它只遍历既有str/list/dict/bool/None，不构造第二投影树或第二wire；原integerHex仍是已经投影的str/dict，未增加数值codec。

每帧先32W/16O，字符串先8len+1W与6len+2C，再逐字符数UTF8宽度、quote/backslash/控制字符转义、标点和键冒号；帧临时解除后归还对象票。计数后调用原note_carrier检查B≤8MiB并保存真实B。恢复已通过原严格Unicode门，生产已通过原projector UTF8门，计数器不替代这些门。

真实depth2 producer receipt、restore receipt均为779，与原唯一wire载体片段独立canonical字节长度779相等。另独立9类projected value计数探针含None、双bool、quote/backslash、全部短控制转义、低控制字符、é/中文/emoji、integerHex wrapper与嵌套dict/list，各与独立canonical长度相等；完整fee events保留，不将这些helper向量冒作产品图覆盖。

## 必要运行与新增委托

- `delta-ff90092-01-probe`：候选引用、真实B及三种Reader反例，exit0，141前后同。
- `delta-ff90092-02-budget-tests`：24 passed/41 deselected，0.73秒；producer/restore/roots四域exact/差1、bootstrap、lower-only、尾故障。该run HEAD及前后test均35520B原SHA，未跨后续test变更，不是混合源。
- `delta-cb2662-03-added-regressions`：12 passed/65 deselected，0.17秒；最终新test的foreign字段/bytes subclass/metaclass/domain、统一伪leaf ID、伪firing/head索引、foreign capture反例均实际运行。
- `delta-cb2662-04-static-and-size`：逐141最终current/Git，133readonly、七源=ff、原test精确前缀、初审30件保全、9种计数字节和Reader算式，exit0；前后141同。

上述24与12不是新增完整36项验收，初版24也不重复累加。根的77专项/正常check/12源验证属于根的运行，本报告不冒本审执行或提前替其终态下结论。

原模块51方法/40循环的完整核对见首审 `method-coverage.md`，模块在本delta未改。新增 `_direct_json_size`/projected 的逐字符计数与先票已如上核；新增 `_explanation_key` 在原formatter前按chars预付128+64chars W、32chars+128 C/S与64O，原leaf hash在构造join/UTF8/sha之前另付32chars+128、32O。实际typed firing/head与saved evidence比对仍经原R `_same`，新D全流保守票在其前保留；按真实record/head调用formatter，每项预扣，不从expected构造结果。

新增leaf hash和head对应检查没有修改七quality机制或R opaque块。并持由原R opaque票继续承担其原子机制，D负责本窗口的新增索引、carrier、普通全J流、别名与formatter；不把512MiB原opaque块虚称塞进D50MiB，也不以原R付款免去新增D工作。成功Dreceipt保守保留输出/诊断票，失败累计work/scan不退，根wrapper先清内部结果后终态，未见新增native/PV在公开错误trace留存的反例。

## 限制与交接

本审只写新 `independent-budget/` 前缀，没有源码/测试/旧过程/依赖/锁/AGENTS/Goal修改、stage/commit、GUI/native/HMR、网络/模型/付费或外部消息。完整clean env仅记录本次实际传递的有限字段，不读取或输出凭据。

通过仅针对固定候选的预算增量与已列正常/失败组件路径，不证明最大图容量、耗时/RSS、全闭包全局首witness完备、真实来源认证、Store/Job/worker、正式selected、T/S/H租约、跨workerΣ、目标OS/真人或上线验收。根仍需实际读回来源审报告、完整check终态与此报告。完成本报告与成员写锁后停止写入；后续源码变化须按新固定ref评估必要复核。
