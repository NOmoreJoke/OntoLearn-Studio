# 四个 unsupported 终点：独立静态 delta 审查

2026-10-22。固定产品 `fc9853f3521faced3a3b88ab8254310c9748a6a6`，基准 `70704ed7b5226c86c5cb06e7e9dbd6689f62b403`。

结论：本次授权单 Mac 文件诊断 delta 静态通过，无新增 P1/P2。主线本候选唯一完整check实际退出0，12来源核验退出0。此结论不证明C++可编译或新诊断已运行，不定位002的具体unsupported根因，不签N0/目标OS/EXCL/drain通过或授权下一构建/运行。

## 授权及范围

已全文读实际根原件并与本目录副本逐字核对：

| 文档 | B | SHA256 |
| --- | ---: | --- |
| I06-unsupported-endpoint-diagnostic-source-window.md | 2837 | 716809fb66e69b94cd57a9c732657394c265bafdfc8b413a2e3b8620a9f995e8 |
| I06-execution002-failure-root-closure.md | 1256 | 5e219ad98dfed42d24f8c585cec09772fe7f1da84629017a94cc3f3e87a3aeba |

唯一产品writer为platform_macos.cc。实际完整Git差异也仅该一件：7675B/SHA28f9c736e59a24cb050b706628aca26283a513fa3c019fdf58dd14e7d3f8a5be → 8670B/SHA `e1fbbcd9c9b73916bd9a030da8bc237dd46230fdd8d0366f0e2424168d4cd71a`。已核九件固定Git指纹与source-static-check逐项相等；其余八源逐件与基准相同。基准到产品只有这一源码差异，旧tracked原件未被该产品ref改动；本轮未重复历史大闭包或旧002审查。

所有命令显式cwd为 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-native-location-N0`。独立检查仅Git/stdlib读取、JSON/hash、授权文本反向还原和行宽算术，exit0；没有编译、产品导入/测试、native/addon、FS/进程/API探针、GUI或Goal/提交操作。

## 具体源码判定

- 新41–54行：仍只有一次原clock_gettime调用，按调用非零→负秒→转换范围的原短路次序检查。三个失败分支仍返回UINT64_MAX，范围仍为 `(UINT64_MAX-999)/1000`，成功路径的sec/nsec计算原样。不新增nsec校验、时钟查询或成功路径日志。
- clock系统调用失败后立即捕获errno并传固定stage；负秒与范围仅传固定reason `negative-sec` / `range`，不把成功查询后残留errno打印成失败原因。reason helper保存进入时errno，fprintf后恢复；不改变原错误哨兵。
- 新59–65行：fcntl失败立即保存error，再以这个error先算原error_status；仅status==NL_UNSUPPORTED打印 `duplicate`，仍返回已算status。BUDGET/DENIED不扩日志。原输出handle初始化、FD校验、复制调用和成功归属未变。
- 新88–93行：fstat同样立即捕获error、先算原status，仅原映射UNSUPPORTED打印 `fstat`。类型/UID/mode/link等其余安全判断未变。
- 新101–107行：ACL query返回null立即捕获errno，预先保存原NL_UNSUPPORTED，再打印 `acl-null` 并原状态返回；没有将null解释为空ACL/成功，没有增加ACL查询或改变后续valid/entry/free逻辑。
- 私有helper在匿名namespace中，只由上述固定字面量调用；error helper写后令errno回到所捕获的error，reason helper写后恢复saved_errno。status在日志前已计算，fprintf不能改变error_status的输入。新日志不输出路径、FD/PID、owner真实值、stat/ACL内容或环境。

独立以明确授权块做反向移除：去cstdio include/两个helper，将clock拆分和duplicate/fstat/ACL-null四分支回到旧文本，整个文件逐字等于基准。因而其它API调用、返回、安全检查与句柄/owner/ACL/close/reap生命周期未改变；新增的stdio失败诊断I/O本身不是新增原生查询/重试/fallback，也不声称零调度或I/O成本。

固定stage只clock/duplicate/fstat/acl-null，reason只上述两字面量；每次命中既有失败返回点最多新增一行。按固定ASCII文字及Darwin signed int32十进制最长11字节算含LF上界：

| 诊断 | 最大B |
| --- | ---: |
| clock errno | 45 |
| duplicate errno | 49 |
| fstat errno | 45 |
| acl-null errno | 48 |
| clock negative-sec | 47 |
| clock range | 40 |

最大49B，小于96B。此为格式宽度算术，不是镜像输出测试、真实fprintf运行或总日志量实测。errno值只是错误时立即读取的快照；ACL-null即使记录某值也不自动证明具体底层原因。

## 实际check原件与边界

已读本轮result、全部四条原始流、checks-summary/provider-handoff/preservation及冻结handoff。实际主线只跑一次 `/usr/local/bin/npm run check`：sourceRef为fc9853f，invocationsForCandidate=1，exit0，elapsedSeconds=54.637296833。原stdout完整包含lint/format/typecheck、TS16文件/637通过/1跳过、Electron Vite构建、ruff check/219文件格式与Python1052通过。`npm run verify:sources`实际exit0，stdout明确12个归档源；不是本子任务重跑或以摘要代替原流。

result记录移除I06_NATIVE_LOCATION_TEST_ADDON/I02_HMR/ROOT_SOURCE_PATH，UV_OFFLINE=1。1skip是native addon环境门未设；Vite构建/TS/Python单测不编译此C++，不证明新四终点日志实际输出或任何目标平台行为。检查耗时仅主线记录，不作性能提升或硬时限结论。

| 本轮原件 | B | SHA256 |
| --- | ---: | --- |
| npm-check.stdout | 5074 | 7134ea3fe228b8db6d2e93191182f9d1767388e3eaa4f302368c0817d07b9fd0 |
| npm-check.stderr | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| npm-check.result.json | 509 | afe1316b5ae048610aad94acdbe8ee647d079fefb4b073dc09fe88ed212ff595 |
| verify-sources.stdout | 111 | 1439dca3a0fd2dbc3702b336e9accceedc93893d0d65264c69da1aa175c45536 |
| source-static-check.json | 3354 | eafa4cb08a1d6bc2802ede56ea0ab05affe2ec0a2a71427d677a08ee514d24ab |
| checks-summary.json | 862 | 82c181fbe3fe4a3ba2dcd5bfad2db27fd21e24d9235975f4ade00a0fe2168251 |

verify stderr也为0B。summary和provider正确保留nativeCppCompiled=false/newEndpointDiagnosticActuallyObserved=false、新T03 digest/artifacts为空、未授权新构建或第三次CLI。

最终handoff3772B/SHA `567fba6bd70578af963634dc963a3bc3be2b5dc39799fdf6b35b356a08272406` 准确反映有限改动与上述真实检查：旧d98/d51/a0e724pair不含本Mac新源，不能用它验证新诊断。C++test仍30037B/4cec7d67ba66fdf47d0ae26ba056372dc437e67ac076e768a548c334bd260319，TS仍8424B/4552db106b86a8a8a80b9fcb7b55292a1696f69b72a20bd97bdfaae2bdc104ce。002只知metadata **case** 的owner-create返回4且owner非零，四终点尚未唯一定位；不能反向认定platform_metadata已进入。

preservation使用固定ref单路径diff及当前tracked diff，并明确AGENTS既有protected SHA78df…a759未改；本轮不据其重复旧原件大审计或改写任何旧失败。仅写本报告，最终bytes/SHA交出后停止修改。后续T03采用/构建或精确运行均须另授；此独审不替指定同版双外审、CI或父验收门。
