# 单产物捕获模板：独立增量窄审

结论：**本轮必要增量无新增P1/P2阻断，可作为静态模板收件；继续NOT_CALL_READY / PENDING_ARTIFACT。** 不构成最终可调arguments、控制器或实验执行许可、产物收件、实验eligible或产品N0通过。本审没有运行候选，连None guard也未运行。

## 范围与固定输入

工作树/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-native-location-N0。已全文读根I06-metadata-probe-capture-template-preparation.md；实际根文件与本目录保存件逐字相同：3793B/SHA256 65c097df32dc13c2979bcb630329f3d033732e3b6a71387f233ef9a794b81e67。该精确窗口只授新模板准备/增量静态独审，不授读取T03半成品、未来artifact/执行目录或运行。

独审读取六件本轮候选及固定e85ae88815e45aa336850b594910a524a073cc00中diagnostic-fourth-call/exact-tool-call.preparation.json的必要文本/AST。该Git blob19614B/8f9788b64b721ad60a8a1c5bf4a72287dd2519d6fcdedc82f5b681e1a8adb739，旧cmd17176B/100ebd1ae0a8f43608146565b95d145503e014b87beaccb53182fbc5115d8781，均实算相符。没有重新评价旧17KB算法、供应链或旧运行结果。

最终候选pins：

| 文件                             | bytes | SHA256                                                           |
| -------------------------------- | ----: | ---------------------------------------------------------------- |
| arguments-template.json          | 19383 | 59218b39a1a079ec41e23fe78d94b48af3e4fef012e363e988a27d78d89be871 |
| delta-static-check.json          |  8418 | 726486a87a65d7fc564e62a88f0a35462adb24a8672617852d80711ba86b983f |
| control-delta.patch              |  4123 | 08f3aa5377dd52cba89519bfb92f6eaec58e126b0e75f56716ec92db40314900 |
| capture-semantics-and-handoff.md |  7038 | 7dfae48616fb1e0795527e057299754a525c95d1d487ac884d9a4fe4c1502e6d |
| preservation-check.json          |  2795 | b021baa03da3d74c61924b6f705ad550d1a1341421f33f48221af0bf71983a18 |

最终patch是n=0零上下文版本；独立difflib从固定旧/新cmd重建与其逐字相同。首读7171B/7cb2d47b9017119e7f75757d2e5ec711414ef43cb6f6fe3078372946c9e83241含上下文空行，作者为归档格式改成零上下文；没有改变cmd/AST适配，不将此过程格式修正误记产品变更。

## 独立静态证明

工具41bdfa完成以下只读检查并exit0：固定Git基准bytes/SHA；非cmd四参数相等；按19个原cmd行的before/after逐一比对并精确重建新cmd；两stdin仅ast.parse；独立白名单AST适配后整个模块结构精确相等。适配内容仅授权/pin/guard、单pin迭代、单argv、新命名空间、sourceRef/programKind、FSIZE/STREAM4096及实验退出标签；不存在额外流程变更。

另按八函数AST比较：event、cancelled、new_record、child_setup、wait_until、stop_owned_group、stream_pass结构不变；pin_pass仅for迭代由两个pin变(EXPERIMENT_PIN,)后全函数结构相等。注释差异由精确文本重建覆盖，不依赖AST忽略注释来掩盖其它文本变化。

新cmd实算16552B/SHA256 ca69fa685b20b5a7313899a42f0b431ee0df1ac3e186b93da52fb25b6f0cc423；按固定heredoc界提取stdin含末LF16352B/b739519e5549072e257271c122eabf4a7b41842d828606c6c6b827859d143e3e。无eval/exec/compile、模块import或子进程调用候选；ast.literal_eval只读AUTHORIZATION/EXPERIMENT_PIN字面量。工具e8f4dd对最终零上下文patch和根窗口保存件核对exit0。所有shell显式cwd为本I06树。

本审只写/格式化本报告，未执行controller、实验/API/fixture、编译/npm、扫描/创建execution或record、读取T03或未来产物、修改源码/模板/其它候选、Goal或提交。preservation列出的旧九源/源码保护按记录引用，本轮不重复大审计或无变化source检查。

## 待补、单产物及真实来源

wrapper只有argumentsTemplate，没有arguments；status明确NOT_CALL_READY_PENDING_ARTIFACT_STATIC_TEMPLATE_ONLY。path/bytes/sha256/digest/T03InputRef/T03ProcessRef/recordIdentity均PENDING_ARTIFACT；payload内AUTHORIZATION和EXPERIMENT_PIN为None。guard位于其它import、目录访问及Popen之前，从静态结构可见未填值不会进入捕获流程；不能以“guard应退出”作为当前执行它的许可。

旧CORE_PIN和PROBE_PIN已从payload去除；pin_pass只消费一个待定实验pin；intent argv与唯一Popen argv均只[EXPERIMENT_PIN["path"]]，executable同pin，符合实验argc==1。没有旧child-probe argv、额外产物或任意参数，不借旧pair填新身份。

明确已收来源是2b724f0188c233de5c8ef107d39fe0c4cb50311f实验源、119a8bef651a81ae80a6ef8bacdc64d4129e5373过程、20278B/6b6ff0969396c243c425dca507d0ea05732a0edb0123a264ab834cd2531690dd；result.sourceRef改为真实实验ref并新增programKind。尚无artifact身份，当前不能证明任何产物由该源构建或前后pin稳定。旧raw的b592来源及旧core结果保持原件，不覆盖新实验。

BASE只指向metadata-contract-probe-run-preparation；RUN后缀、mkdir、目录open都为未来execution-001，没有复用旧host-core-run-preparation/001–004。准备时不检查/创建该未来目录，目录独占和存在即停仅是后继保留的算法条件，不是当前实际目录状态证明。

## 资源及控制边界

必要资源适配为child RLIMIT_FSIZE从1MiB降4096B、STREAM_LIMIT同为4096B；parent的三控制记录每件64KiB/合256KiB仍未改。child限制不误施加为parent控制记录4KiB限制。单pin pre/post每pass读取上限保留2MiB，两pass上界4MiB；不是预认产物大小，也没有真实读取未来产物。

NOFILE64、CPU12、CORE0、六项清环境、私有-I/-S入口、单Popen、新session/close_fds、显式stdin与0600独立双流保持。信号默认/空mask、取消、exact waitpid/ECHILD未知、15/1/2秒逻辑控制、仅未reap本组收口、finally/一次cleanup路径都没有新算法改变。本增量核对不再次证明旧控制器正确或把Popen握手、系统调用、内部资源当硬时限。

保留core.stdout/core.stderr和corePid/Returncode/WaitStatus是捕获键兼容，不把该leader解释成旧core/child-probe。新标签EXPERIMENT_EXIT0_REQUIRES_CAPTURE_REVIEW明确只为子exit0待内容复核；非零标签不抹去原coreReturncode。实验2/3仍保存在真实子返回字段，控制器通常工具exit1不能倒推实验1；控制失败74、信号/取消/wait未知也需分别解读。

## eligible的证据门及最终限制

controller没有新增stdout parser，exit0不自动签eligible；本轮文档明确把完整内容复核放在后继独立收件：真实单产物前后pin一致、工具/子终态对应、无取消/超时/未知、三记录与双流完整/有界/稳定；case0–4各三行有序且唯一、无多余/畸形文本，固定枚举/布尔/Int32/UInt32，E为NOACL/count哨兵或empty/count0，N为form3/count1，必要成功判定全1/api2/err0，最后eligible footer。stdio失败或任何缺行/重复/失败footer不能签eligible，不追加查询/重跑补齐。

即便未来符合全部条件，也只是目标profile值得后续ACL适配，不是产品owner/root/acquire/生命周期或N0通过。nativeDrainCertified=false、fixtureResidual未知继续保留；leader已收或snapshot stable不证明自然EOF、全部后代drain/fixture清空。

本轮无新增阻断或需局部修订事项。保持NOT_CALL_READY；root真实收件T03单用途产物后，仍须精确窗口填pin/digest/refs/record，固定最终arguments并独审，最后另授一次CLI/setup/read/cleanup。本报告不批准任何一步，也不关闭003/004失败、目标双OS、完整功能、同版指定外审/CI/真人/远端、T01 HOLD或已拒SQLite/heap/OS线。冻结交出后停止改写。
