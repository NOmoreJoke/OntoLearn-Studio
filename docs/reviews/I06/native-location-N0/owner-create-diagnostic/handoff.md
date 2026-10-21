# 单 test 失败回执精化交接

2026-10-22。固定产品 ref：`2d0443c037919f8655214daf4af7f184e0613fd9`，parent `7d496da72d4f32bd23c7475f572496640570368b`。唯一产品文件location_core_test.cc为30037B，SHA256 `4cec7d67ba66fdf47d0ae26ba056372dc437e67ac076e768a548c334bd260319`。精确diff见single-test.patch，供方字段见provider-handoff.json；不生成或猜新T03 inputDigest/pins。

五个CLI调用分别传metadata、child、partial-child、revoke-concurrency、budget。helper只在原同一次create返回失败后、原cleanup/require之前向既有stderr加一行，字段仅固定case、现有status整数、owner_nonzero布尔。%.18s限制标签；常量+18B标签+11B有符号int+1B布尔及LF的静态上界为75B，小于160B。没有运行镜像输出测试，也未实际观察新C++输出。

默认nullptr保留原第六处Node bootstrap未传标签调用及其原有无新增回执行为，避免误标成CLI case。原owner_close/abort/require、通用owner-create失败行、所有断言与case顺序/资源上限/EXCL均未改。去掉这三个新增诊断行、参数及五个固定标签后，源码逐字还原7d；其余八源与28条Windows断言逐字不变。没有修改native返回分支、ACL/权限、errno、ABI、构建配置或锁。

## 实际检查

先用原锁建立本worktree独立node_modules/.venv：npm ci --offline --ignore-scripts及uv sync --frozen --offline均0。Node24.15.0/npm11.12.1、Python3.12.14/uv0.11.12为实际读取版本。锁及依赖声明未改，未启安装脚本或应用。

**完整npm run check仍失败**：唯一一次exit1，止于旧八源之一tests/unit/i06-native-location-owner.test.ts:189的prefer-const。该文件SHA256 `e0946f7daf1236045d0198d989cf718ea40227d63b76e5a1407eaa1b0d501b04`，与7d逐字一致；不越过单test窗口修改它，不把这个失败删去或伪称check通过。

聚合命令因&&未到达的五阶段随后分别执行：format/typecheck/build均0；TS unit为16文件、637通过/1跳过；engine:check为ruff检查通过、202文件格式通过、pytest1052通过。唯一native addon测试因显式artifact gate未设置而未运行，不能算native通过。执行时去除I06_NATIVE_LOCATION_TEST_ADDON、I02_HMR、ROOT_SOURCE_PATH，Python保持UV_OFFLINE=1，防止加载native、启HMR或借用其他源树。12个归档源核验0。各原始stdout/stderr、argv及实际退出值保留，汇总见checks-summary.json。

这些是允许的TS/Python单元及前端构建，不是九源C++预处理/编译、native/core/probe/CTest/try_run/addon/e2e/HMR或GUI验证；本轮未进行这些操作。首次配置路径/缺本地runtime的只读发现保留preparation-discovery.json，不冒充产品测试失败。

独立源码审查原文7012B，SHA256 `630a4a3abafa54287cbdac3741d0e519c293d41ca81716834d208dc08ec9cbbd`：固定2d0443c的有限静态范围通过，无新增P1/P2；实际check仍exit1，不能签完整检查绿或C++可编译/可运行。原报告保留不格式化。

## 保护与后续

61件既有过程原件及四份历史manifest、八源和受保护AGENTS/依赖锁均核同。原唯一宿主运行仍为tool1/core1、owner-create根因未知；原窗口已用完，本次没有重提、扫删fixture或更改旧失败事实。

本包只交新的单test源码。根接收后再决定T03新采用/必要构建及新pins；任何下一次CLI仍须另授精确窗口。当前二者均未授权，旧pair不能冒用来验证新诊断。完整check的旧lint门、N0运行/目标OS、父功能、指定双审/CI/PR/develop门均保持未关闭；未push/合并或改变Goal。
