# I06 N0：单 test 失败回执精化

2026-10-22。总控已全文读固定7d496da72d4f32bd23c7475f572496640570368b的失败交接/静态分支表、作者6292B结果独审及根5369B失败审查；另核最终13行政件current/Git/hash。接收本次有限失败与封存，不签N0运行通过。core1/control1、33B通用owner-create标签、无取消/超时、后代/fixture未知事实保持；原一次运行窗已用完。

现在直接批准原I06在原树/分支继续本功能的**单 test 失败回执精化**。起点7d496da72d4f32bd23c7475f572496640570368b，唯产品writer为 `packages/native-location/tests/location_core_test.cc`，旧29706B/SHA256 `f1684029430f28918fd4caa062eb8d250f97d5d34aa3ab65c517e44954525037`；其余八原源、28断言、ABI/生产实现、CMake/driver/locks及全部旧准备和运行原件保持原字节。不得以该标签先改某个native失败分支、ACL/权限/时间/预算或限额。

## 最小改动

五处现有make_owner调用各传一个固定case标签：metadata、child、partial-child、revoke-concurrency、budget。helper在同一次原nl_fixture_owner_create已返回、且原status非OK或owner为零时，向现有stderr额外写一条有限回执，只有固定case、现成nl_status整数和owner是否非零。可用函数参数传静态字面量；不增加全局动态状态、创建/调用次数或运行时查询。失败行最多160B，不输出owner原值/地址、路径、FD、业务数据或猜测errno。

回执放在原失败cleanup/require之前，随后原owner_close/abort/require和main返回语义保持；原通用owner-create失败行也保留。成功路径不新增输出。不得改任何断言、预期、cleanup、case顺序、资源上限、EXCL逻辑或目标路径；不新增系统诊断/探针/API或产品runner。只补可归因证据，不将测试失败放行。

## 本窗口验证及交付

允许源码静态检查、文档格式与AGENTS必要无窗口 `npm run check`、12归档源核验；不得执行native/core/probe/CTest/try_run/addon/GUI/e2e/HMR，不自行编译这九源（仍由T03唯一构建owner负责）。不为这个有限输出改动另造镜像实现测试；独立agent实际读精确diff，核只有五个固定标签和一条失败回执、控制流/断言/八源/旧原件未变及真实检查结果即可。

新过程只写 `docs/reviews/I06/native-location-N0/owner-create-diagnostic/`，固定新产品与纯过程ref、单test bytes/SHA、唯一产品diff和精确供方回执，原失败/双流/历史不覆盖。不要纯收件递归追加清单；复用已固定原件引用，新增过程独立有限manifest。

根接收新源码后，另给T03必要新采用/构建和新pins；之后才另授精确一次CLI。当前不授权第四次构建、任何第二次运行、扩大资源、换入口、扫描或删除/tmp、修改系统设置或Goal。平台拒绝即停，不重试/重措辞。目标OS、父N0、指定双模型/CI/PR/develop门保持。
