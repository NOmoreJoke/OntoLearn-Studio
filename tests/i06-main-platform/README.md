# I06 正式主进程 Linux 隔离探针

只构建本 worktree 已正常合入、由根线完成检查并冻结的完整提交。`prepare-build.mjs` 要求 HEAD 精确相等，拒绝产品源码 dirty；protected AGENTS 与本线 harness/docs 单独记录。harness 可以继续修正，每次尝试都使用新输出目录，失败证据不覆盖。

本线唯一写入 `tests/i06-main-platform/**` 与 `docs/reviews/I06/main-platform/**`。不改共享入口、依赖锁、CI 或旧平台证据。主机仅执行准备/构建/采集脚本，实际 Electron 与 Python worker 都在容器内；无 host mounts、无 host GUI/Keychain，运行 network none。

根线提供固定 SHA 后，先在本线正常 fast-forward merge，再执行：

```sh
node tests/i06-main-platform/prepare-build.mjs <40位固定候选SHA> r1
docker build --pull=false --progress=plain -t i06-main-platform:<唯一尝试名> <prepare返回的context目录> > <独立build.log> 2>&1
docker image inspect i06-main-platform:<唯一尝试名>
docker create --name <独立容器名> --cap-add=SYS_ADMIN --network none --shm-size 256m i06-main-platform:<唯一尝试名>
docker start --attach <独立容器名> > <独立run.log> 2>&1
node tests/i06-main-platform/collect-evidence.mjs <容器名> <不可变image ID> <新的证据输出目录>
```

固定自有基础镜像 ID：`sha256:0497417676f686d3b35a17d6c08a2c28a4c7e81169e9f72c17a50d748ae33a44`。它仅提供基础 OS/显示/keyring 工具。项目依赖由新镜像独立执行 `npm ci`、`uv sync --frozen`，不借用 Mac `.venv`、其他线镜像/容器/数据库/输出。实际构建使用仓库正式 `npm run build`，启动其 `apps/desktop` main。

运行使用容器内 Xvfb/Openbox/dbus/GNOME libsecret、实际 Electron 44.9.0；采用容器内合成 CA 与 `NODE_EXTRA_CA_CERTS` 信任动态 loopback HTTPS 接收方，不禁用 TLS 验证。直接 spawn 正式 Electron main，仅以容器 loopback 动态 Node inspector/CDP 读取 runtime、退出和驱动 UI；不加载会强制 basic/mock-keychain/disable-hang-monitor 并包装 readiness 的 Playwright Electron loader。最终运行不带 `--no-sandbox`，记录实际 argv、main commandLine、renderer `/proc` 的 NoNewPrivs/seccomp filter。容器经明确授权增加唯一 `SYS_ADMIN` capability，保持默认 seccomp、非 privileged、USER i06、network none、无 mounts/host ports，并将镜像内 Chromium helper 设 root:root/4755。这是能力扩展的测试环境，不能称为默认 Docker；它增加容器内 namespace 管理等能力，不能外推宿主机或生产安全配置。旧 `--no-sandbox` 尝试只作有界凭据/驱动失败证据。

真实 Store fixture 通过本容器 Python 包和独立常驻 coordinator/worker 运行批准的 `test.read`。主进程只用已批准 I04 的 path+env 可信 fixture 和固定 `i06-finite-probe-v1` main policy。第二个同输入 worker 在 main 内运行；第一 public 字段必须在其完成前授权，之后 UI 选择第二结果并验证授权复用。`workMs` 按实际上限 10000，时序不足将失败并保留记录，不扩公共 API。

接收方只将完整 body 写入专用 `.body` 与 SHA 清单，headers 仅内存校验。合成 secret 不写入 fixture、摘要或日志；扫描 ordinary product/renderer/probe 日志、私有 gateway 文件，以及实际 SQLite 所有字段。源 rows 原本就在 Store，扫描明确允许这些源值，拒绝凭据、模型 response 和完整 outgoing payload 新写入项目 DB。当前没有导出入口时如实记录未能扫描实际导出产物。

`runtime-manifest.mjs` 分别记录 Git archive 源、独立 harness、正式构建输出、Electron/Python binary 与版本。collector 对实际容器 artifacts 做哈希回读，保留 image/container inspect 与失败结果。通过只说明该固定 Linux arm64 候选及 I04 合成结构化数据链；不外推 Mac/Windows、签名升级、真实 I05 业务 producer、真实服务协议 Q9，也不替代指定双模型审查。

独立原生恢复增量使用 `Dockerfile.native`，其 FROM 是本线 r11 成功镜像（prepare 对 tag 检查不可变 ID `sha256:f7fc7b481eb6270fc169a173970846ce998e1b59b4a42fffdb9b36295730dff1`），只新增 xdotool/scrot 与冻结的 observer/driver。它不重建或修改产品入口，不复用主运行的 profile、DB、keyring 或输出。

```sh
node tests/i06-main-platform/prepare-build.mjs 9fcba6634d5c16983c36ef671d4ec8e79694b6d6 native4
cp tests/i06-main-platform/Dockerfile.native <新context>/Dockerfile
docker build --pull=false --progress=plain -t i06-main-native:<唯一名> <新context> > <独立build.log> 2>&1
docker create --name <独立native容器名> --cap-add=SYS_ADMIN --network none --shm-size 256m i06-main-native:<唯一名>
docker start --attach <独立native容器名> > <独立run.log> 2>&1
node tests/i06-main-platform/native-collect.mjs <native容器名> <不可变image ID> <新证据目录> <r11正常链binding-evidence.json>
node tests/i06-main-platform/collect-storage.mjs <已退出的自有容器名> <已收集证据目录>
```

native driver 只短暂连接 main inspector 载入测试 observer，随后关闭客户端；observer 实际 `inspector.close()` 后记录 `url()===undefined`，故障前核验没有 renderer remote debugging port，全程不连 renderer CDP。通过实际 contextBridge 先建立已完成模型调用与实际 atomic Store 提交，再 `forcefullyCrashRenderer()`；不替换 dialog/recovery。外部 xdotool 只在该容器 DISPLAY 观测可见的准确窗口标题并按 `shift+Tab Return` 操作实际恢复提示。第二窗口只读核对整个 project、jobs/result/operation、selection、invocation/outcome 相等，接收端计数仍为 1。collector 额外核对与 r11 同一编译 app/binary，保存 prompt 截图和动作 receipt。该增量证明 crash 恢复，不声称覆盖无响应/hang 矩阵；容器 CJK 字体缺失，截图不作为中文可读性证据。

`collect-storage.mjs` 仅从已退出的本线容器额外回读合成 SQLite 与私有 gateway 文件，保存逐文件 hash，便于独立复核；这不修改原 runtime/scanner receipt。Chromium profile/cache 不纳入保留物。完整 raw 与失败版本保留在被仓库忽略的 `out/`，提交文档只引用固定归档及 hash。
