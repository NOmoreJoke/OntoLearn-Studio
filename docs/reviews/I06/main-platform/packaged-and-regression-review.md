# I06 9fc 包内专项通过；原 e2e 回归失败

固定 `9fcba6634d5c16983c36ef671d4ec8e79694b6d6` 的真正 Linux arm64 unpacked executable 专项 pkg2 通过。官方 `npm run package:dir` 构建 PyInstaller engine 与 electron-builder 包，actual `app.isPackaged=true`、`appPath=resources/app.asar`；243份包文件全部从实际容器回读并逐字节 hash/大小核对。独立只读审查核验了 source map、实际 exe/asar/engine、当前 main 的 engine 父链、完整 body、finite 三拒绝和真实 crash 恢复，无本专项剩余阻断。

**同候选原仓库 e2e 回归失败，不记总验收通过。** Source 和 packaged 各运行原 `npm run test:e2e`，均 1 passed / 3 skipped / 2 failed（exit1）。C1 与 desktop smoke 的全局 `getByRole('status')` 同时匹配原 health-result 和新增模型不可用段落，strict mode violation；精确位置是 `desktop.spec.ts:19` 与 `csp-lifecycle.spec.ts` 的 normal()，新增段落在 App.tsx:542。C1 在 normal-ui 阶段先失败，后续 CSP/恢复未执行。根负责单独修复，原 trace/错误上下文保存，不修改旧测试或绕过断言。

## 包内实际链

pkg2 用独立 profile/SQLite/keyring/loopback synthetic HTTPS receiver，无 host mounts/ports，network none、USER i06、唯一 SYS_ADMIN、Docker默认seccomp，非 privileged。正常包不带 no-sandbox，helper root:root4755，实际 gnome_libsecret；main inspector 故障前关闭且全程无 renderer CDP。mainPID243 的包内 enginePID295→PPid243→71 连续祖先链写入 raw，只采纳当前 main 后代，不能把上一 finite profile 遗留进程当本调用 worker。包内 actual atomic Store commit 与随后只读结果通过真实窄 contextBridge。

窗口中明确选择历史整份结果、预览、确认授权后，接收端仅收到一次2327B POST；其 rows 与 actual sourcePage 完全相同，source metadata/producer/selection 同实际 DTO。该整份授权**有意包含合成私列**，不作为 source A03 public-only 字段证明。响应通过实际 bridge 返回且无 key 回显；普通日志、私有 gateway、两个 SQLite 全字段与 raw pages 扫描通过，额外停止后存储只读回收及 hash 单列。不存在实际项目 export 入口，未宣称已扫描导出产物。

真实 crash→可见 GTK 标题→xdotool 按键→第二窗口恢复，前后整个 project、job/result/operation marker、context/selections/invocations/completed outcome 严格相等，receiver保持1。恢复函数和 dialog 没有被替换；只证明该增量 crash，不计 hang 矩阵。容器缺 CJK 字体，标题由 X11 Unicode 字符串核验，截图不证明中文可读性。

独立 finite-policy profile 实际 `isPackaged=true`，source-only finite fixture 不能启用模型服务。经真实 bridge 发送有效格式 configure/store/start 三请求，均返回固定 `GATEWAY_MODEL_UNAVAILABLE`；凭据目录实际为空，**父级活跃 HTTPS receiver 跨全过程测得 delta0**，不是硬编码或未启动接收端。正常 whole-result profile 与它分离。

## 构建与原件

本线 own native4 不可变 image `sha256:495979a381da8be793248a520d8ed4f75e87ea02dd69adae5cfb57ada57bc61c` 独立派生 official package base2 `sha256:b7bba605ea11528cbfcadf6ab3e8e341243fa19d9cf384f84427b3d899b07dc0`；只有构建依赖允许网络。pkg2 与 r11 的 candidate/851源码 hash map 直接 deepEqual；实际包文件与 binary 的 hash 在 JSON 回执及原始 package manifest 中。

```sh
docker build --pull=false --progress=plain -f tests/i06-main-platform/Dockerfile.package-base -t i06-main-packaged:9fcba663-base2 tests/i06-main-platform
node tests/i06-main-platform/package-prepare.mjs 9fcba6634d5c16983c36ef671d4ec8e79694b6d6 pkg2
docker build --pull=false --progress=plain -t i06-main-packaged:9fcba663-p2 tests/i06-main-platform/out/9fcba6634d5c-pkg2/context
docker create --name i06-main-packaged-9fcba663-p2 --cap-add=SYS_ADMIN --network none --shm-size 256m i06-main-packaged:9fcba663-p2
docker start --attach i06-main-packaged-9fcba663-p2
node tests/i06-main-platform/package-collect.mjs i06-main-packaged-9fcba663-p2 i06-main-packaged:9fcba663-p2 tests/i06-main-platform/out/9fcba6634d5c-pkg2/evidence tests/i06-main-platform/out/9fcba6634d5c-r11/evidence/binding-evidence.json
```

base1 是本线误断言 exe 名称造成 build RUN失败，official packaging日志保留；批准CI的实际 exe 名为 `@ontolearndesktop`。pkg1 实际链虽完成，旧 collector 未显式比较 source map、engine 未记父链、finite 计数未接实际 receiver，这些证据缺口不倒改，以新 pkg2 完整重验收口。regression1 单独使用原始仓库 e2e，默认CI全量步骤不提供 trusted fixture，所以每种模式3项按原门skip；未在已知首步回归未修复时扩跑后续 fresh-fixture CI步骤。PW Electron loader 的 basic/mock/hang 覆盖仅属于该旧回归环境，不作 safeStorage/native 证明。

原件 `tests/i06-main-platform/out/i06-main-packaged-9fc-pkg2-regression1-raw.tar.gz`：SHA `006f0bb374c659077c6433df3bdaeede900bb90bddd7fe7d4bc2d1dd6f26f7fd`，142,457,921B/591 entries；index SHA `2cefe86501f88d79b8ca5c986be4e544bf04449e637f2ef490c8276c4d624332`。完整243份 actual package 文件纳入；仅将相同 pkg1 package 副本去重为 pkg2，并沿用旧9dac归档内相同 candidate tar。包含所有 build/run/inspect/frozen harness/identity、两轮实际数据和失败 e2e trace，不含headers或明文key。完整独立运行目录仍保留，archive不进Git。

定向 ESLint/Prettier、6 Python文件 Ruff、JS/Python/shell语法检查通过，文档按默认ignore之外显式格式检查；没有重跑998/1052全库。最终提交与实际 frozen harness 的 hash 分开，后续候选修复不会冒称9fc的旧证据已覆盖新源码。本报告不外推其他OS、签名升级、真实I05业务、Q9或S3最终批准。
