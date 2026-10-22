# ACL remedy 两源：独立静态源码审查

2026-10-22。固定产品 `1217e0f63a9c62b72e01046ef5fbc5c53434251a`，直接基准 `3cc158e0a62b154d110a6fc80e3ddf171cea0098`。

结论：授权两源的静态审查通过，无需本阶段修正的P1/P2；实际主线一次正常check和12源核验退出0。此结论不证明C++可编译、ACL/fixture真实行为或003已修复；未取得absence正例、单ACE负例、故障释放或目标OS证据。真实运行及构建仍另授，不替指定模型外审、CI或N0/父验收。

## 规则、范围与身份

已全文读取本树AGENTS、根developer-common-instructions和本次source window，适用精确窗口覆盖旧通用流程：

| 文件 | B | SHA256 |
| --- | ---: | --- |
| AGENTS.md | 15852 | 78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759 |
| developer-common-instructions.md | 17891 | e437121a08053544c2a09151ac5183baf15b5fa67a3a604891aaa9e77ba971b0 |
| I06-acl-null-003-remedy-source-window.md | 4307 | bf352c3ed25b74f91897cdee8bcdefaa51a810586127e591915d5e46bd412bef |

只审两件current diff及必要已批准ACL方案/来源。固定ref与基准差异恰两路径；九源current/Git/after指纹独立逐项相等，七其它源与基准逐字相同。两实际writer为：

| 源码 | before B/SHA256 | after B/SHA256 |
| --- | --- | --- |
| platform_macos.cc | 8670 / e1fbbcd9c9b73916bd9a030da8bc237dd46230fdd8d0366f0e2424168d4cd71a | 12579 / d944a4901b6d3f516f18ab436aed9ec56a78eb1bbd12d1949ebf6a6e171825ce |
| location_core_test.cc | 30037 / 4cec7d67ba66fdf47d0ae26ba056372dc437e67ac076e768a548c334bd260319 | 37928 / 2517eb970ef39f37dd99ca9945909331df937d4dd43ce53b74eb722bf47a7053 |

只运行Git/stdlib静态读取、字节/hash/文本还原算术，命令显式cwd为 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-native-location-N0`，退出0。无产品import/npm检查、C++编译、native/ACL/FS/进程探测、GUI/e2e/HMR、Goal/提交或SQLite被拒线；未重审旧001/002/003或五轮build。当前工具完全访问不扩大只读职责；只写本报告，不发送其它chat。

## 生产metadata判定

Mac新增helper32–68及platform_metadata123行起与批准方案对应：

- 每次初始化fresh filesec、stat/属性输出置零，fstatx非0立即非成功。fresh-but-unfilled即便fstatx错误地给0，OWNER/GROUP/MODE getter仍须各成功且与同次sb相同；缺省/失败走非成功，不复用旧valid。
- UUID/GRPUUID query分别检查返回，presence只比较是否零；短envelope缺见证被拒绝，valid为非1位值也不误判。ACL presence成功后仅在完整前置链成立才允许absent；get失败NULL/ENOENT单独从不进入OK。
- 原type、UID/geteuid、mode、nlink及kind检查保留。不存在路径重开/fallback、ACL写入生产路径或私有RAW属性；identity/link来自同次sb，metadata flags仅在finish成功后发布。
- present ACL getter失败先捕获错误；未知非空输出标unknown_acl，最终RETAINED，不猜测free。成功的NULL/移除哨兵为UNSUPPORTED，哨兵不交ACL函数。只有真实owned副本进入valid/FIRST检查。
- filesec/query/get等新基础设施失败采用批准的ENOMEM→BUDGET、权限→DENIED、其它→UNSUPPORTED。acl_valid失败及首entry不满足原-1/EINVAL空规则仍DENIED，符合保留旧valid-and-empty政策，未将inspect错误或任意ACE变成功；不是将所有ACL检查errno重分类为基础设施错误。
- finish在每条返回路径执行一次：已知独立副本owns标记先退役，acl_free仅一次；释放非0或未知ownership覆盖RETAINED优先。filesec_free调用一次、void不造结果，最后恢复所保存的主错误快照。语义不一致路径用0而非陈旧errno冒充OS错误。finish后才写metadata；没有析构再free。

所读固定Libc中的fresh/未填充、短envelope和valid bit反例均有明确拒绝路径。但公开源码不是installed libSystem身份证明；absence链仍是批准的实现级推论，不证明通用合同或持续ACL/namespace lease。statx内部for/realloc与ACL转换入口的heap/次数/wall硬界未被此次代码证明，文件中同held-object快照注释及交接继续保留此边界。

## Darwin fixture与清理

新增Darwin局部资源guard、empty/one-ace/invalid-fd三case；仅CLI main调用，Node bootstrap不调用这些新case。逆去membership include、新Darwin helper块和main三行后，整个test逐字还原基准；28条Windows static_assert、原fixture/五case/全部原断言顺序原样保留。Mac还原metadata并去新helper后，文件其余部分亦逐字相同。

empty独立同FD witness一次；它要求三标量安全且一致、UUID/GRPUUID见证和无entry，随后校验公开ABI/kind/小端identity/link/flags并显式关闭。输出区分acl_present与absent_observed；只有absent_observed=1才是P1 absence覆盖，若目标自然present-empty仅算P2，不能凭owner成功声称两正例均通过。

one-ace用一次mbr_uid_to_uuid(geteuid)构造当前owner qualifier，设置一条ALLOW/ACL_LIST_DIRECTORY及零flags，检查每项setup/valid/set_fd/free。随后独立witness必须present、首entry及明确无NEXT，避免将setup失败当DENIED成功。被测非零owner在状态断言前close一次；必须DENIED。没有输出UUID、FD或实际owner。

对acl_create_entry失败guard的必要静态依据，另只读同固定官方commit的 [acl_entry.c](https://github.com/apple-oss-distributions/Libc/blob/71bbe350ab79eef58113991d817ccc6165061a64/posix1e/acl_entry.c#L50-L86)：所读实现失败在修改前返回，不替换acl_p。当前guard从acl_init成功就持有owns_acl；require异常展开时一次free，真实失败使析构abort，不能记成功。这是该公开源的静态依据，不是本机函数失败实测或installed身份。

资源guard的closed/cleanup_ok使显式关闭失败不会重试；析构保失败并abort，阻止继续fixture清理冒签。失败的非零owner同样关闭，异常展开也有guard；没有先断言状态而丢掉失败owner。invalid-fd仅更改自身input副本为-1，保实际anchor清理；明确只覆盖duplicate前门，不冒充fstatx/property内部错误。

固定新增输出上界含外层fixture-failure前缀最大71B，低于96B；独立宽度算术已核，非实际fprintf运行。应用侧对象/调用点有限不代内部硬界；新增fixture须由后续精确运行窗口纳入setup/read及资源预算，当前没有运行许可。

## 主线实际检查：读回而非本子任务执行

已读check/verify command和result、四条原raw，并逐项核实际字节/hash；productRef均1217e0f，cwd均本树。命令移除I06_NATIVE_LOCATION_TEST_ADDON/I02_HMR/ROOT_SOURCE_PATH，UV_OFFLINE=1。

主线唯一 `/usr/local/bin/npm run check` returncode0，elapsed55.944573375；原stdout完整六段包含lint、format、types、TS16文件/637通过/1跳过、三段Vite build、ruff check/236文件format及Python1052通过。`npm run verify:sources` returncode0，明确12个归档源。该一次完整检查没有C++编译，1skip的真实native addon没有执行；不能据TS/Python通过声称新C++/fixture已验证。

| 本轮证据 | B | SHA256 |
| --- | ---: | --- |
| check.stdout.log | 5074 | db63b5a8114f6a8fd18cefdabb66efdb9e71ffe4675976a09006e9f97a058bb2 |
| check.stderr.log | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| check-result.json | 575 | 937bb9fb55d31a03292ac5d741bf222a7698941cbeafbe3ffb8ba70c9132f590 |
| verify-sources.stdout.log | 111 | 1439dca3a0fd2dbc3702b336e9accceedc93893d0d65264c69da1aa175c45536 |
| source-after-and-static.json | 6514 | afceaf726ce8105d274e1b26b928e07d6bdfe21e0ffedae5692c16e076eb2667 |

verify stderr也0B。validation-scope4847B/f215ae14c7075c1b753b330f3081e6a6614bd4d90d0b5f099a0c493e37e9d85e和最终provider-handoff4133B/8ebfc8c9f2468bde815d10dd061a29682507957c978e2c12869e7116df5238c6准确区分源码调用点、未覆盖故障和后继授权。query/get失败、fresh未填、短envelope、valid非1、allocator/free失败、异常ownership目前只静态检查，不冒充真实覆盖；void filesec_free无伪造返回测试。

最终交接明确旧第五pair不含本remedy，新native digest/artifacts尚未生成，T03采用/编译及新pair CLI各须另授；旧失败不倒填根因或追认修复。不关闭drain、EXCL全路径、目标双OS、父N0、指定外审/CI及T01 H/SQLite HOLD。原件保持仅按本次固定Git父链/保护指纹记录，不重复大审计。

本轮仅新增本报告，最终bytes/SHA交出后停止修改。静态通过与正常仓库check通过分别成立；C++编译/链接、fixture/API行为和完整产品验收仍未验证。
