# I06 独立 Linux safeStorage 探针

入口 `tests/i06-platform/probe.cjs` 在正常 Electron 主进程执行项目实际的 `createElectronCredentialBoundary`，不创建 BrowserWindow，不设 `ELECTRON_RUN_AS_NODE`。Linux Xvfb、Openbox、D-Bus、GNOME Keyring 全在本线专属 Docker 容器；不连接主机显示、Keychain、Docker socket、其他线数据或运行容器。镜像由固定 digest 的 Node 24 bookworm 构建，单独安装锁定 Electron 44.9.0 与项目同版 zod 4.6.7；不改共享依赖清单、锁或 CI。

重现命令（从本线 worktree 运行）：

```sh
npm ci --ignore-scripts
node tests/i06-platform/build-probe.mjs
docker build -t i06-safe-storage-platform:20261021 -f tests/i06-platform/Dockerfile tests/i06-platform
docker create --name i06-safe-storage-platform-20261021 --network none --shm-size 256m i06-safe-storage-platform:20261021
docker start -a i06-safe-storage-platform-20261021
docker cp i06-safe-storage-platform-20261021:/probe-data/results tests/i06-platform/out/results
```

探针仅使用合成 secret/password。专属 fixture repository 在进程内接收密文；探针把该合成密文临时保存供第二 Electron 进程及新 Keyring 恢复反例使用，这不是产品凭据仓库。结果目录不带 fixture 密文/正文，原始运行日志保留于忽略的 `out/`，失败日志不覆盖。

实测范围：ready 前 `unknown` 与不可用、factory 拒绝；实际 `gnome_libsecret` 加解密、第二进程恢复、损坏密文拒绝；新 Keyring 无法解开旧密文；显式 `basic_text` 与无 D-Bus 后端的拒绝及零仓库写入。单元 double 单独验证 factory 的主进程/ready/缺少 Electron 版本、加密异常与安全错误边界。未能自然产生的实际 OS 加密失败不能由 double 宣称平台通过。

factory 不接受调用者提供 encryptor、不启用明文模式，也不配置安全后端。真实 safeStorage 可阻塞等待 OS 交互；future 主进程 owner 只在已批准使用时段/隔离环境初始化。Linux 证据仅属于结果中明确记录的 OS、架构、Electron 和后端；macOS、Windows、签名/升级/干净设备仍需各自实测。项目/导出排除、真实私有凭据仓库与 Store/窗口联验由本线后续接线证明，不能从此 fixture 推断。

官方 API 依据：[Electron safeStorage](https://www.electronjs.org/docs/latest/api/safe-storage)。文档用于了解 API 与风险，实际锁定版本行为以本探针输出为准。
