# T10 私有服务的隔离 Linux 原生验证

此验证补足私有 `PreparedHtmlReportFile` 与真实 main-owned 文件选择器之间的保存/取消证据；不注册 IPC，不改 App/preload/Store/公共协议，不关闭 T10 父功能。产品源码固定 `a8a497a8b1b7d52fcc365f8b128972867b2bd433`，报告及文件服务的 hash 与前次内审一致。

## 可复现路径

只从固定提交归档 `package.json package-lock.json pyproject.toml uv.lock .node-version apps packages tests scripts`。`source.tar` SHA256 为 `8d62e0e1f776726a23014b5f48e87cece15d07b3182259f1143c4e53990fd994`；116 个文件逐 hash 核对，无 `.git`、`.env`、业务运行数据库、依赖目录或特殊 tar 条目。清单及原始构建日志在 `docs/reviews/T10/evidence/isolated-native/`。

把此归档作为 `source.tar`、本目录 `isolated/Dockerfile` 作为 Dockerfile、四个 runtime controls 及冻结 hash manifest 作为 `controls/` 放入私有构建上下文。Dockerfile 从固定官方 Node24 Debian12 镜像构建，安装 npm11.12.1、uv0.11.12、锁定依赖、Electron44.9.0、Python3.12 和 Xvfb/Openbox/xdotool/ImageMagick；不复用其他功能线的候选运行环境。构建阶段需要依赖下载，运行阶段网络为 `none`。

```sh
docker build --progress plain --label org.ontolearn.task=T10 \
  --label org.ontolearn.source=a8a497a8b1b7d52fcc365f8b128972867b2bd433 \
  -t ontolearn-t10-native:a8a497a-v1 \
  docs/reviews/T10/evidence/out/isolated-context
python3 docs/iterations/T10/isolated/run-container.py --attempt 3
```

每次 attempt 使用新名字及新输出目录，禁止覆盖。host driver 创建容器后绑定固定 ID，先读回非 root UID1110、默认 seccomp、明确增加 `SYS_ADMIN`、网络 none、无挂载和端口映射、私有 PID/IPC、2CPU/4GiB/1GiB shm/512 PID 限额，再从未启动容器复制四个 controls，逐 hash 对比受审源码和镜像 manifest。额外能力已公开，不称最小权限或 Docker 默认能力环境。最终镜像 ID 为 `sha256:475ba702e6d1425542aedfed5638cc780875c140b6bacdd50a46a44c84602e1f`。

runtime 先执行 61 项 T10 TS、60 项 Python 检查，再在容器自己的 D-Bus/Xvfb/Openbox 中直接启动 Electron；没有 Playwright Electron loader、dialog stub、`no-sandbox`、关闭 hang monitor 或 mock keychain。为载入测试专用 main hook，短暂启用容器内 loopback main inspector；在调用 picker 前关闭，无 renderer CDP/DevTools。测试 hook 仅在 main 中调用实际私有服务及实际 `dialog.showSaveDialog`；X 键盘输入和截图限制在本次 Electron PID 所属、标题及焦点均确认的 native 窗口。每个外部命令有硬超时，总流程有 deadline，清理限定本次进程组和容器。

## 实际结果和失败原件

- attempt1 在启动前因 Docker 回显 `CAP_SYS_ADMIN`、脚本预期 `SYS_ADMIN` 而失败；容器未启动。修复为仅接受这两种精确单项写法，没有放宽权限集合。
- attempt2 实际显示保存窗口并输入 Enter，但无选择回执，55 秒超时失败；没有 published/cancel 结果。原因未由该次日志证明，保留失败原件，不作为通过。
- attempt3 增加对话框截图和 750ms 就绪等待，以实际 Save 快捷键 `Alt+s` 保存、`Escape` 取消。driver/native 均 PASS、Electron/容器退出码0。两张截图可见实际 GTK 文件选择器和目标文件名；取消窗口还能看到前次保存的文件。
- 保存文件为 3,896 字节，SHA256 `ad367a3158a8adc989378239d68d992e9c281f0269561af7fd31027a1743cdcd`，权限0600；与服务回执相符，durability confirmed、cleanup complete。取消没有生成文件，实际 picker 函数未被替换。
- actual renderer：sandbox/contextIsolation 为 true、Node integration 为 false，`NoNewPrivs=1`、`Seccomp=2`、有效能力为0，DevTools 关闭；引擎实际 health 成功。

## 保留的验收范围

这是合成报告和私有服务的 Linux arm64 原生保存/取消证明。既有 headless Chrome 对同一报告实现的12组攻击文本检查仍作为独立的 HTML 安全显示证据，本次没有把 native 对话框验证等同于打开 HTML 后的行为。

仍须由批准依赖和 owner 正式接线完成可信业务投影、凭据及授权排除、完整 checkpoint、原子迁移、逐 attempt 学习证据、跨设备续编辑/查询/重跑冲突/撤销、G.6、跨平台/包内验收。通用 `npm run test:e2e` 未被本探针替代；指定双外审、push/PR/CI/正常合并/远端核验仍未完成。
