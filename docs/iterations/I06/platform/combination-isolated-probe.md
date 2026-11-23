# I06 真实私有持久化与 Linux safeStorage 组合探针

此探针只消费主线明确 source-root 当前源码，逐文件捕获、转译并记录原 TS/实际 JS 的 SHA256；不提交主线拥有的私有模块，不改共享入口、依赖、CI 或公开契约。运行实际 Electron 44.9.0 主进程、`createElectronCredentialBoundary`、`PrivateCiphertextRepository`、`PersistentGatewayAudit`、`ModelGatewayCore` 及实际 transport；没有凭据/审计/HTTP mock。协议与数据仅为合成探针，不选定产品模型协议。

前提：使用本线已验证的不可变 Linux 基础镜像，image ID 必须为 `sha256:0497417676f686d3b35a17d6c08a2c28a4c7e81169e9f72c17a50d748ae33a44`；给此 ID 打独有本地 tag 后核对再 build。该基础镜像自身不作为本次构建证据：本次独立保存 build 日志、image/container inspect、实际容器内 JS/probe/runner/sources/package hash，和运行结果共同绑定。

```sh
node tests/i06-private-platform/build-probe.mjs --source-root /absolute/approved/I06-source-root
docker tag sha256:0497417676f686d3b35a17d6c08a2c28a4c7e81169e9f72c17a50d748ae33a44 i06-safe-storage-platform:base-0497417676f6
docker image inspect i06-safe-storage-platform:base-0497417676f6 --format '{{.Id}}'
docker build --network none -t i06-private-platform:20261021 -f tests/i06-private-platform/Dockerfile tests/i06-private-platform
docker create --name i06-private-platform-UNIQUE --network none --shm-size 256m i06-private-platform:20261021
docker start -a i06-private-platform-UNIQUE
node tests/i06-private-platform/collect-evidence.mjs i06-private-platform-UNIQUE i06-private-platform:20261021 tests/i06-private-platform/out/UNIQUE
```

每次保留唯一 container/output，build/start 的 stdout/stderr 另存日志。`build-probe.mjs` 保留当时 TS snapshot 并再次读取源文件拒绝采集过程中的变化。collector 要求容器已 exit 0、实际 image ID 一致、network none、容器产物与 host snapshot 逐文件相等，并核对所有六项结果和实际 Electron/zod 版本。Docker COPY 严格限定编译 JS、package 和 manifest，禁止把增长中的日志带入镜像；collector 同时拒绝额外 out 文件。

实际场景：安全 GNOME Keyring 下凭据只经 safeStorage 加密后由真实仓库原子落盘，实际本地动态 loopback receiver 收到一次授权 POST，真实审计持久化一条 metadata-only intent；第二 Electron 进程先监听原端点同一端口，再重开真实仓库/审计并构造网关，恢复凭据/原审计且观察到零重发。恢复观察窗为 100ms，当前恢复路径没有调度重发。坏密文反例保留有效私有记录 digest，仅替换 OS 密文，以确保拒绝来自真实解密边界；新 Keyring 无法恢复原密文。basic_text 和不可用后端下真实凭据目录零文件。实际检查目录 0700/文件 0600/owner，并验证权限放宽、用户符号链接、排除根重叠、异 owner 拒绝。

探针扫描实际私有文件与最终普通运行日志，断言不含合成 secret、业务正文、端点路径或 userData 路径标记。仅合成绑定/端口保存在探针控制目录，用于独立进程重开；没有复制产品凭据文件到提交证据。全部 Docker 构建和运行断网；只有容器 loopback receiver，未启动产品 HTTP 服务。Xvfb/Openbox/Keyring 位于独立容器，未连接主机桌面/Keychain/CUA；`--no-sandbox` 仅用于此无 renderer 的隔离 main 探针，不作为生产 sandbox 验收。

本次失败与最终证据见 [组合证据](../../../reviews/I06/platform/combination-linux-evidence.json)。首轮依赖查找失败及第三轮 collector 发现构建日志被带入的拒绝均保留，未记为平台通过。Linux/arm64 实际结果不外推 macOS/Windows、签名/升级/干净设备、平台提示行为或真实 Store/项目导出/main→bridge→UI 接线。POSIX 私有目录策略不宣称防御可完全控制同一 OS 账号/内核的攻击者。
