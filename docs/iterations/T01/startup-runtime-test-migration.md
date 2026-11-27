# 启动阶段旧恢复测试迁移申请（尚未应用）

唯一申请路径：`tests/unit/task-runtime.test.ts`。原基底 `79d6bc4998ef49f8401636166b7e9fa7193c6b21`，Git blob `8bc5fe2141d409f1157d7153efd13a342f71fae1`，26406B / SHA256 `2f8f8c1fd34cc449b2cca6ff2a05dcbed43b47560f97fcc039810233f2dfee50`。当前原文件与该对象相同，未写入；不以已有17产品/7测试授权外推这条旧测试写权。

`npm run check > /tmp/t01-startup-fullcheck-first.log 2>&1` 的实际 session96369 / chunk8cd807 exit1：lint、格式、类型通过后，20个TS文件中19个通过，1024 tests passed /3 failed，未执行后续build/Python全仓。三个失败均在旧测试404行读取 `internal.session.pending`，因为真实Session已改为ES运行时私有。完整原日志3636B / SHA256 `097c07f47415d392e6bc085db16158a33dbc065f4ad2c30112110b5f921a1cbd`；不把1024称为全仓通过。

[最小未应用补丁](startup-runtime-test-migration.patch) 为6223B / SHA256 `cba8eaf5ee10753e1ed0e9c0df3256d9452ff08934ff185226a1d6e7825e5baa`。只迁移测试的故障入口和观测，不修改生产API：

- 测试模块包装现有真实OS spawn，持有该测试实际创建的child；原健康、Job、worker、SQLite与stdout均实际运行。
- 对实际stdin写出和stdout返回使用原JsonlReader做只读观察，记录请求/响应id集合；原零pending断言保留，增加framing未失败断言。没有以TaskService调用数量代替真实内部heartbeat等wire请求。
- 从测试自己捕获的child执行原SIGKILL并等待close，保留原PID/session换代断言；不读取或暴露Supervisor的Session/WeakMap。
- 失败重启仍通过真实Python `raise SystemExit(73)`，仅把原可变command对象切换改为测试spawn拦截点切换。保留三次失败后offline、无自动额外启动、手动读恢复、确切4/5次真实spawn等断言。
- 原rounds/atomic receipt、成功Job不降级、operation对账、无写入重放、唯一Job/claim、view绑定、全部超时和8个测试均保留；不加skip、不改期限或预期成功状态。

补丁已用虚拟CompilerHost在原路径替换内存source做全unit类型检查，0 diagnostics，实际chunk e780b8 exit0；原文件未写、未运行本补丁测试。最初普通函数赋值不兼容write overload的类型诊断保留，改为测试内Proxy原样转发重载后通过，不冒称首稿通过。待root当前owner精确一次窗口批准后，才应用、实际运行8项回归并独立核对断言等价；其他包内验证可继续。

## 独立只读意见及r2（仍未应用）

独立审查确认原8测试/期限/主要断言均保留，但只按响应id移除Set不能等价于内部Map：错method/session响应可能误清，半帧也可能尚未登记。采纳后另存startup-runtime-test-migration-r2.patch，原6223B/cba8…e5baa补丁不改。r2改为保存完整实际request并复用原matchesResponse才清对应项，增加读写两方向bufferedBytes总和为零断言；保留零pending、framing、所有既有故障/Job/receipt断言。精确口径是“所有完整合法匹配wire请求已获响应且无半帧”，不冒称直接读取ES内部Map。

r2虚拟CompilerHost全unit类型检查0diagnostics（实际chunk549b68 exit0），原文件仍2f8f…ee50；没有应用或运行。root应对r2最终字节登记精确窗口；r1只作历史审查输入，不作为待应用新候选。
