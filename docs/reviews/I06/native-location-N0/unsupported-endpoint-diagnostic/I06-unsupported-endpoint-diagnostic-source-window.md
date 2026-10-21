# I06 四个现有 unsupported 终点诊断源窗口

2026-10-22。原I06聊天/Goal/树/分支从70704ed7b5226c86c5cb06e7e9dbd6689f62b403接续；002失败已受限收件，参见I06-execution002-failure-root-closure.md。四候选静态申请和真实Mac源码已读，仅批准原owner的下述诊断，不选择或修复某个假定根因。

唯一源码writer为packages/native-location/src/platform_macos.cc，原7675B/SHA256 `28f9c736e59a24cb050b706628aca26283a513fa3c019fdf58dd14e7d3f8a5be`（fc6237固定来源）。仅Darwin既有四处失败终点：monotonic clock哨兵、duplicate-anchor的fcntl错误映射UNSUPPORTED、metadata的fstat错误映射UNSUPPORTED、ACL query nullptr。允许同文件必要stdio include/私有小helper；不改core/ABI/test/Windows、构建三writer、其它源码或限额。

每命中一个现有失败返回点最多一行固定stage诊断，stage只clock/duplicate/fstat/acl-null，每行含换行总上限96B。clock调用失败只记录立即捕获的errno快照；负sec/转换范围失败只记录固定reason，不解释陈旧errno。fcntl/fstat仅原error_status结果为NL_UNSUPPORTED时记录立即捕获的错误快照，其他原状态不扩日志。ACL null记录失败返回时立即捕获的errno快照，不预判它证明空ACL或具体原因。禁路径、FD/PID、owner实际值、stat/ACL内容和环境。

保持原OS查询次数、顺序、short-circuit、返回码及全部句柄/owner/ACL生命周期；不新增查询、重试/fallback/trace或调整目录。日志前捕获errno及原status，日志不能改变error_status输入，返回前恢复该原errno。clock只拆原条件以标注固定reason，保持一次原clock调用及相同哨兵/数值边界；不增加成功路径时钟或校验。不将ACL null视为空ACL、不把unsupported改OK、不放宽UID/mode/link/ACL/no-follow，不改close/reap。

新过程仅docs/reviews/I06/native-location-N0/unsupported-endpoint-diagnostic/；旧17件002归档、001、四轮构建及所有原件冻结。固定新产品后一次必要npm run check和12来源核验，明确这套检查不编译C++且native addon仍可能跳过。九源前后指纹/唯一Mac差分、四诊断行长度与errno/返回不变的独立agent静态审查、真实命令双流和新供方九pin交接同时保留。不要复制全历史或重新跑API探针。失败保原件，不改旧测试预期。

完成新源码与本轮必要验证候选交root，T03另授唯一Mac采用/第五新输入构建后才能编译验证；本窗口不授构建/产物运行/第三次CLI。不得复用002、额外FS/进程探针、系统穷举、扫描/tmp、清理未知fixture/旧PID。无GUI/e2e/HMR/凭据/外部模型/付费/push/PR/merge/Goal变更。只推进本次有证据的最小诊断，所有根因/平台/EXCL/父门保持。
