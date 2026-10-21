# 单 TS 声明修复：独立 delta 审查

2026-10-22。新产品固定 `fc6237e8cad1a4043d46a1c7198439f1da06ad67`，基准 `2de79e886bb9fb3aa97cb66efc1d04a86961c552`。

结论：该有限 delta 静态通过，无新增阻断；本轮主线唯一完整 `npm run check` 实际退出0、12源核验退出0。旧完整 check 退出1的历史保留。本次仅关闭 lint 阻断，不证明 C++ 诊断可编译/已运行，更不解决此前通用 owner-create 失败的未知根因或签 N0 通过。

## 授权和精确差异

已全文读根 `iteration-control/2026-10-21-weekly-release/I06-native-diagnostic-lint-repair-delta.md`，1590B，SHA256 `3932ff24a18210b01755bf49fc32d274482baf637777659950aedd5a8869236c`。仅授既有 reentrant 测试两处声明修复，不授其它产品路径、构建或 native 再运行。

两 ref 的全 Git diff 只有 `tests/unit/i06-native-location-owner.test.ts`：删除提前 `let current: ReturnType<typeof owner>`，将原初始化赋值改为 `const current = owner(data.binding)`。独立文本还原检查确认除此两处外整个文件完全相等；无 lint disable、测试预期/断言、mock、owner 构造或调用前后顺序变化。

固定新 TS187–198行：先创建 data、保存 original，再安装 file 箭头回调；该声明只捕获 current 绑定，不执行回调。current 仍在原 owner 初始化位置（新194行）创建，之后195行 root、196行 file 才触发安装的回调。必要只读调用依据：测试 owner helper72–76行仅构造包装并检查结果；未改动 createNativeLocationOwner175行起捕获方法/schema、建立状态并返回方法闭包，没有在构造期间调用绑定的 file。因而不会在 const 初始化前读取 current，也没有把 owner 创建前移。当前源码条件下，const 替换保留原 reentrant revoke/busy→stale/accepting=false/close 的测试行为。

本轮未重审旧 N0/C++ 语义。仅独立核九件固定 Git blob 指纹与 source-static-check 逐项一致；其余八件与基准完全相同。关键交接身份为：

| 文件 | B | SHA256 |
| --- | ---: | --- |
| tests/unit/i06-native-location-owner.test.ts | 8424 | 4552db106b86a8a8a80b9fcb7b55292a1696f69b72a20bd97bdfaae2bdc104ce |
| packages/native-location/tests/location_core_test.cc | 30037 | 4cec7d67ba66fdf47d0ae26ba056372dc437e67ac076e768a548c334bd260319 |

全 ref 差异只有 TS，也证明新固定 ref 内原诊断/失败 tracked 原件没有变化。另抽读当前旧 npm-check.result/stdout/stderr、原 native execution-001 result/stderr 五件，与2de79固定 blob逐字相等；旧 check 仍exit1、原native失败标签未被重写。主线 preservation-check 所列40件旧manifest原件保留属其已保存核验，本轮不重复全套旧审计。

## 本次实际检查原件

本子任务没有运行任何产品检查。最终补读新 `checks-summary.json`，其一次完整check/退出0、205/637+1skip/1052和12源记录与原始流及结果一致。实际只读本轮 `npm-check.result.json`、`verify-sources.result.json` 和四条原始流、source-static-check、preservation-check、provider-handoff；所有读取命令显式 cwd 为 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-native-location-N0`。

主线记录：`/usr/local/bin/npm run check`，sourceRef=fc6237e，exit0，repeatCount=0，elapsedSeconds=55.713473166；顺序原 stdout 实际包含 lint、format、typecheck、vitest、Vite build、engine:check 全六段。TS为16文件/637通过/1跳过，Python1052通过，ruff check通过且本轮实际为 **205 files already formatted**。`npm run verify:sources` exit0，原stdout明确12个归档源。

记录移除 I06_NATIVE_LOCATION_TEST_ADDON/I02_HMR/ROOT_SOURCE_PATH，UV_OFFLINE=1；未改动的显式 addon 环境门在新TS213–214行，1skip不能当 native addon 通过。Vite构建不是 C++/addon 编译或应用启动，TS/Python通过也不证明 native 新诊断已观测。provider-handoff 明确新T03 digest/artifacts仍null、采用构建及再次运行均未授权。

| 本轮原件 | B | SHA256 |
| --- | ---: | --- |
| npm-check.stdout | 5074 | f64be29fc1dbfb442d52815863a6d94397e43f9a211cc8a86f3c8e0fc10456ee |
| npm-check.stderr | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| npm-check.result.json | 537 | 59419b890e568f2ba5872c0ca926a3b23e656122dcb721b556e82aba9fdc8834 |
| verify-sources.stdout | 111 | 1439dca3a0fd2dbc3702b336e9accceedc93893d0d65264c69da1aa175c45536 |
| verify-sources.result.json | 240 | 54d364cdfb19fa4b3759d883dce9e11998c9db68e1d7817f0d046d99332051d4 |
| source-static-check.json | 2369 | ddec00fb81bdc9e55d7d2c461bb1a88791ad38e0b72daeca6f61dab6d4f7f48b |

verify stderr也为0B/空文件SHA。读取实际结果与旧失败明确区分：新候选有自己的一次完整check退出0，不能回写旧候选check退出1为通过，更不能将此前core1/control1失败归因为这处lint。

本子任务一次纯静态日志marker脚本误沿用上轮ruff计数202而assert退出1（其前面的源/原件核对已完成）；随即只读原stdout84行确认本轮205，按真实值在本报告纠正。没有修改原日志、重跑检查或用该静态脚本失败冒充产品失败。

本轮仅新增此报告；无源码、旧文档、Goal修改或提交，无镜像实现测试、C++编译、native/addon/core/probe/GUI运行。下一步供方采用/构建及任何精确运行仍需根另授；独立delta审查不替指定模型或目标OS验证。
