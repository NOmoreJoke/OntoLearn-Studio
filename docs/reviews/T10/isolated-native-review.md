# T10 隔离验证工具与实际原生证据独立内审

审查 agent `/root/t10_private_review`，只读审查 T10 独占工具、固定 source.tar、Docker 配置和实际产物；没有改源码、重复主线整仓检查或重跑 Electron。

## 发现与关闭

- 原设计仅记录 renderer 的隔离字段，可能错误放行。已改为硬断言 `NoNewPrivs=1`、`Seccomp=2`、零有效能力和 DevTools 关闭，实际运行通过。
- `xdotool windowactivate --sync` 等外部命令缺硬超时，可能使清理不能到达。已为每个命令加入5秒硬超时，并绑定总 deadline。
- 仅 Dockerfile `USER` 不足以证明运行隔离。新增 host driver，以精选 inspect 硬断言配置；create 后固定 container ID，避免名称复用误操作；每次有独立输出及终态，清理限定自身进程组和容器。
- 构建时修改 controls 可能错用旧快照。最终重建后，启动前从未启动容器复制四个 runtime controls，逐 hash 对比当前受审文件及镜像 manifest。
- native 窗口增加实际 PID、标题和焦点断言；截图限制在本次原生窗口。

审查方实际核验 Docker daemon seccomp 为 builtin、归档116文件的逐 hash 及非特殊条目、脚本语法、真实保存/取消截图和最终回执。额外 `SYS_ADMIN` 已公开；不称最小权限。短时 loopback main inspector 用于测试 hook，已在 picker 前关闭，不称无内部 listener。

## 实际读回

attempt1 在 start 前失败，attempt2 为 `T10_NATIVE_DEADLINE`，仍保留失败原件。attempt3 的 driver/native 均 PASS、容器终态退出码0；内含61TS/60Python通过；4个 runtime controls、3个编译源和host driver hash 一致。

审查方独立从固定源码生成预期，并与真实 native 保存文件逐字节核对：3,896字节、0600、SHA256 `ad367a3158a8adc989378239d68d992e9c281f0269561af7fd31027a1743cdcd`。取消目标不存在，实际 picker 函数未被改写。最终结论：当前私有验证范围未见新阻断问题。

这只确认隔离 Linux arm64 的私有服务原生保存/取消。没有打开本次报告进行浏览器行为检查，不代表正式 App/bridge、可信脱敏投影、迁移/G.6、跨平台、指定双外审或父功能完成。

原始构建日志的CR/行尾空白及测试日志尾空行按原字节保留，完整git diff --check因此报告原件空白；不为通过样式检查改写原件。非原件的代码和文档另行diff --check通过，原件完整性由manifest核对。
