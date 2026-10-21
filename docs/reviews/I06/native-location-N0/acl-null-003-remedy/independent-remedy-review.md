# ACL-null 003：独立最小修复方案审查

2026-10-22。结论：最终方案在本次只读设计范围通过，可提交根申请精确源码/测试窗口；未发现未关闭P1/P2。发现的P3验收可观测性文字已修正并关闭。**没有实现、API执行或真实正反验收结果**；本结论不证明本机libSystem等同公开源码、不保证缺省ACL推论跨实现成立，也不关闭003具体根因、内部资源硬上界、native drain或N0/目标OS/父门。

## 范围、身份与实际动作

已全文读根准备指令和003收件文，分别与本目录authorization-window/execution003-root-closure副本字节相等。其身份为2680B/SHA256 `afd7bfa6c451771f1809d88121b79c9cdcf323d20a5e4903c05b23743d819911`，1535B/SHA256 `8b67de4a92aaa44b609582fd909388606d2732a566bf79e9276fde0a673da60c`。003固定b0342c44c08441049edc7d246d201bd44ea35719和fc9853产品继续冻结，本轮不重审003或旧五轮。

实际全文读proposal、初版validation、handoff、三份固定Libc源码快照及必要SDK摘录；最终定点读P1修正及ACL getter资源措辞收窄，并重核最终文档hash。对三public快照、四SDK摘录及其实际SDK原文件、两根指令副本做静态bytes/hash核对，均与source-pins一致。仅点读固定ABI的nl_metadata确认公开可观测字段，没有重审旧产品逻辑。

| 最终输入 | B | SHA256 |
| --- | ---: | --- |
| proposal.md | 11272 | 67d287c13864fea4b56690958c62cb13b0d022d0e325750fd1ad0295da64968c |
| validation-scope.md | 8269 | 23366e91543e95cfaf37eb752027a51a9c71b758755f87b0605159c45eb1a45d |
| handoff.md | 2210 | aa2c0cf490115a633e5d0da0d65d2ac480ac6b9d77466e7adf41351813ee6195 |
| source-pins.json | 7609 | 8e171deb7d93836a624c9aae4a3e2c72b94c6dc9c4453549373a02d745c35382 |
| preservation-check.json | 735 | fc6f3291b1c20d5f2f5623ba5e62ccbf51c63299993edcdbe6da0d5ef1964902 |

所有shell命令显式cwd为 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-native-location-N0`；仅Git/stdlib/文档静态读取和hash，退出0。另只读一次Apple官方归档acl_get手册；没有产品import、ACL/API/FS/进程探针、测试、编译/native、GUI、Goal/提交或SQLite被拒线重启。除本独审不写其它文件。

## 关键反例与absence链

[Apple归档acl_get手册](https://developer.apple.com/library/archive/documentation/System/Conceptual/ManPages_iPhoneOS/man3/acl_get.3.html)将NULL列为失败并要求释放返回的ACL工作副本；工作副本不是持续访问授权。文档没有给NULL+errno2成功白名单。实际只读该页的返回与副本说明，不用错误名推003根因。

固定官方Libc commit为71bbe350ab79eef58113991d817ccc6165061a64：

- [acl_file.c](https://github.com/apple-oss-distributions/Libc/blob/71bbe350ab79eef58113991d817ccc6165061a64/posix1e/acl_file.c) 的wrapper合并init/statx/get属性层返回，不能用最后NULL识别是哪层。
- [filesec.c](https://github.com/apple-oss-distributions/Libc/blob/71bbe350ab79eef58113991d817ccc6165061a64/gen/filesec.c) 中fresh对象valid=0，query返回码与valid分开；valid是位值（如ACL位），不能写valid==1。ACL缺省getter的错误不是明确absence单独证明。
- [statx_np.c](https://github.com/apple-oss-distributions/Libc/blob/71bbe350ab79eef58113991d817ccc6165061a64/sys/statx_np.c) 同时存在完整envelope/NOACL和短envelope两类ACL未设结果；后者还清UUID/GRPUUID。扩容失败可在error仍0时退出，fresh fsec可能根本未填，因此仅fstatx0+ACL valid0不够。

最终方案逐项排除了这些具体反例：每调用fresh fsec/初始化输出；fstatx必须等于0；OWNER/GROUP/MODE各get成功且与同次sb一致；UUID/GRPUUID query成功且valid非零；之后ACL query成功的valid0才成为候选absence。短envelope见证缺省及成功返回但未填充均拒绝，不靠残留errno。不使用私有RAW/ALLOCSIZE，不加字符串路径/reopen/follow或ACL写入生产路径。

这是**固定公开实现下的保守推论**，不是归档手册普遍承诺或已证实本机行为。SDK声明/源码hash不能证明已装libSystem的实现、运行分支或同次stat/security的持续授权；同held FD约束对象，metadata仍只是快照。方案明确见证不足保持UNSUPPORTED，不以正例失败为理由删门。未来实际平台表现和采用此实现级假设的范围仍须根另行评估，不能由本设计自动扩大支持集合。

## 状态、所有权及资源

present分支先get独立副本，失败/NULL/SDK移除哨兵均拒绝；哨兵不交acl_valid/free，未知所有权不猜测free。合法owned副本继续有效性与首ACE检查，任意ALLOW/DENY ACE拒绝；有效且明确空才候选成功。无效/读取失败不能当空。

业务status/错误快照先保存；已知副本acl_free一次，真实失败或无法确认释放RETAINED优先，不重试或返回OK。fresh filesec每条路径free一次，其free为void，不能虚构可检查的成功返回码或证明后代drain。最后才发布原metadata flags。新的ENOMEM/BUDGET、权限/DENIED和其它UNSUPPORTED分类都明确是待授权行为变化，非纯日志且都不能放行。

应用侧固定对象/有限调用点与库内部有界性分开。最终proposal已将query/标量getter的字段读取与ACL getter的转换/分配入口分开，未展开入口的申请次数/字节不获证明；此措辞收窄准确，不改变算法或授权范围。公开statx仍有for/realloc，ACL_MAX_ENTRIES128不能证明实际申请字节、次数、OS链或wall硬上界；本机也未证明使用该代码。方案/交接明确保留此未知，未以旧wrapper已有该链或正例成功冒充硬资源证明。若后续根要求这些硬界限，本方案自身不能完成，须停在该缺口，不擅加资源框架或重启拒绝线。

## 真实验收范围与P3处置

拟两writer精确为Mac的platform_metadata/必要cleanup，以及core_test内Darwin fixture小helper/用例；ABI/core/Windows/Node/TS/driver/限额及旧原件不扩。下一窗口才可批准新fixture同FD setup、一次独立fstatx见证和单ACE负例。membership声明只支持拟owner UUID转换接口存在，不是已执行成功或系统资源上界证据。

P1须同时证明setup有效、属性ready/envelope/ACL presence以及owner/root/close/cleanup实际结果；present-empty只在自然表征出现时单列，否则明确未测。N1必须先证实恰一条有效ALLOW ACE设置成功和present/首entry，再要求DENIED；setup失败无效，不能算安全拒绝通过。原安全门不改期望。无效FD若只碰duplicate前门，不能冒充新property失败覆盖。

allocator/query/get/短envelope/真实acl_free失败不保证能自然制造；计划只保静态反例/未测边界，故障seam须另授，不用伪指针、双free或全局低内存来造假证据。P1/N1成功也不能关闭任意故障、库内部资源界限或持续ACL lease。

**P3已关闭**：原P1表要求root metadata观察uid/mode，但固定ABI82–90的nl_metadata没有这些字段。最终validation18行已改为公开root只比kind、identity（按既有编码）、link_count及acl_checked/held_object_only；uid/gid/mode一致性仅来自同FD fixture witness与生产内部门，不新增ABI/seam。该修正使验收可执行且不暗扩writer/协议。

完整check/12源核验、T03新输入编译及真实CLI仍按方案分开另授；本轮没有执行它们，旧第五pair不能证明未来修复。handoff准确区分设计/未实现、公开source/installed未知、内部循环未知及真实测试范围，无新增问题。preservation的旧原件保持为主线固定diff记录，本轮未重复历史大审计。

本独审通过仅供下一步精确授权评审，不是源码批准、成功修复或完整功能验收；最终bytes/SHA交出后停止修改报告及其它文件。
