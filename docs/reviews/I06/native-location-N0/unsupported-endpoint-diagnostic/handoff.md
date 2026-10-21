# 四个 unsupported 终点：源码诊断交接

产品候选 `fc9853f3521faced3a3b88ab8254310c9748a6a6`，父提交 `70704ed7b5226c86c5cb06e7e9dbd6689f62b403`。唯一源码差异为 `packages/native-location/src/platform_macos.cc`：7675B/28f9c736e59a24cb050b706628aca26283a513fa3c019fdf58dd14e7d3f8a5be → **8670B/e1fbbcd9c9b73916bd9a030da8bc237dd46230fdd8d0366f0e2424168d4cd71a**。

本次只加现有Darwin失败终点的stderr诊断，没有选择或修复根因。新原件窗口、唯一Mac patch及source-before/source-static-check保存在本目录；九源前后逐件匹配固定Git，除Mac外其余八源完全相同。

- clock仍只调用原clock_gettime一次，再按原顺序检查负秒和原转换上界；调用失败打印立即捕获errno，负秒/范围只打印固定reason，三处仍返回原UINT64_MAX。成功路径原计算不变。
- duplicate-anchor fcntl和metadata fstat错误先立即捕获errno、先算原error_status，仅NL_UNSUPPORTED打印固定stage；其它原状态不扩日志，原返回码不变。
- ACL query nullptr立即捕获errno，保留原UNSUPPORTED；不把null当空ACL，不改变后续ACL/UID/mode/link/no-follow判断。
- 两私有helper仅打印固定stage/reason或失败errno快照，并在返回前恢复原errno；不输出路径、FD/PID、owner值、stat/ACL内容或环境。不新增原生查询/重试/fallback，不改owner/句柄/ACL/close/reap生命周期。

stage只clock/duplicate/fstat/acl-null，每命中一个既有失败终点最多一行。以Darwin int32十进制最长11字节（含负号）静态计算，含LF的上界：clock45、duplicate49、fstat45、acl-null48；clock固定reason negative-sec47、range40。最大 **49B ≤ 96B**。这是格式静态上界，未执行新C++，不是实测诊断输出。

四个授权block及必要include/helper反向移除后与原Mac源码逐字相等；原OS查询调用数保持。原安全门及非Darwin分支保持，未改core/ABI/test/Windows/构建driver或限额。独立静态delta审查见 `independent-source-review.md`，不重复旧控制算法、002结果或四轮构建历史。

本候选唯一一次完整check实际退出0：lint/format/types、TS16文件/637通过/1项native addon跳过、frontend编译、Ruff（219文件格式匹配）及Python1052通过；12源核验也退出0。原双流/result保存在本目录，摘要见 `checks-summary.json`。本轮仅一次必要完整check；npm check包含frontend Electron Vite编译及TS/Python测试，**不编译C++**，native addon环境门仍跳过，不证明此Mac诊断可编译或已运行。

新供方九源完整pin及新Mac8670B指纹见 `provider-handoff.json`；C++诊断测试保持30037B/4cec7d67ba66fdf47d0ae26ba056372dc437e67ac076e768a548c334bd260319，TS单测保持8424B/4552db106b86a8a8a80b9fcb7b55292a1696f69b72a20bd97bdfaae2bdc104ce。现有T03 d98/d51、digest a0e724…cac77 的旧pair不含此Mac改动；新digest/artifacts为空，不能复用002或用旧pair验证新诊断。

`preservation-check.json` 记录父候选至新产品仅Mac差异、当前tracked仅AGENTS原WIP；旧001/002十件runtime、17件002归档、旧准备和四轮构建原件均未改。没有扫描/清理未知fixture或杀旧PID。本目录有限manifest排除自身，过程提交号由提交后的回复给出。

新endpoint诊断尚未观测，002仅知metadata case的owner-create返回4且owner非零，仍不能唯一定位clock/duplicate/fstat/ACL-null。metadata只是case标签。根收件新九源后，另授T03精确采用/第五输入构建，之后再另授运行；当前无C++构建、第三次CLI、原生探针、GUI、权限/目录更改、push/PR或Goal变更。根因、native drain、EXCL、目标OS及父N0/功能门保持未关闭。
