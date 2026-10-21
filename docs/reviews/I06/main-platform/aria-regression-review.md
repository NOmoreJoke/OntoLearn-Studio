# I06 e2c ARIA 修复与原 e2e 回归回执

固定新产品提交 `e2c269ad78a78e1a042cadc93b1c81a874707153` 已重新正式构建 source app 与真正 unpacked package，完成原仓库 e2e、live 语义最小检查和六项 CI fresh-fixture 用例。结论为：**首次10门中9过、source native一项失败；仅该原用例在独立新容器/新fixture定向复验通过，首次失败保留，原因未定。** 不能写成一次10门全绿。

根修复仅将 App.tsx 模型不可用提示的 `role=status` 改为 `aria-live=polite`，文本/条件保持，源文件 SHA `d66e74cd77b4ef1e5b0e97f3ddefe10481dccd8466bbc40c1f403eaee1b22716`。本线正常 merge 后只新增专属 harness/docs，没有修改旧 e2e、CI、源码、锁或放宽断言。

## 实际结果

| 检查 | source | packaged |
| --- | --- | --- |
| 原 `npm run test:e2e` | 3 passed / 3 默认 fixture skips，exit0 | 3 passed / 3 默认 fixture skips，exit0 |
| 模型不可用提示 initial/reload | aria-live=polite、无 status role、全局 status=1；无项目/local/控件禁用，pass | 相同，且实际 isPackaged=true，pass |
| 原 native renderer fresh fixture | 首次 fail；独立原命令复验1pass/0skip | 首次1pass/0skip |
| 原 reload fresh fixture，rounds12 | 1pass/0skip | 1pass/0skip |
| 原 coordinator exit fresh fixture | 1pass/0skip | 1pass/0skip |

默认全量的3项 skips 严格保留，并由各自独立新 fixture 的真实定向调用覆盖，没有把 skip 算通过。每份定向 report 均核实际执行而非 skip，逐项使用原 CI 的 `scripts/prepare-i04-fixture.py` / `--background-rounds 12` / 原 grep。没有重跑S1/S2故障矩阵或998/1052全库。

source native首次 raw 已完成 crash→第二窗口，inspectorClosed=true、hangMonitorEnabled=true，第二窗口可见/有焦点/X11焦点标题正确；events只有crashed，原断言未观测到 hang 原生提示。原 TS 每phase 是 **`Date.now()+30000`，30秒**；report总耗时约13.315秒，不能据此猜原因。此前工作消息误述10秒已纠正，代码/原始时限未改。

唯一复验使用完全同一 Docker inspect image identity `sha256:948721a324bcfa8a219271f5b886830bf8c41ab6d4d0f209c55d1dc8581c0e9a`、同 candidate/881源码记录/运行文件/原测试，只新建容器与fixture。原 verified raw 记录 `crashed` 与 `unresponsive`、3窗口、两次真实可见 GTK恢复提示、实际按键、关闭inspector和焦点实证，1passed/0skip/exit0。复验的 inline runner 与 Docker Config.Cmd 逐字相同并单独hash；不以新脚本倒贴旧运行。首次失败是否环境时序或其他原因未确立，不宣称已消除不稳定性。

## 构建与证据

从本线自有固定 dependency/package image 派生，核验新旧 package-lock/uv.lock逐字相同，复制明确 e2c Gitarchive 后再运行仓库正式 `npm run package:dir`；没有拿旧9fc包代替新构建。build阶段为自有同锁UVcache预热，运行UV_OFFLINE/network none。实际source/pack/e2e均在独立Linux容器Xvfb/Openbox/GNOME会话，USER i06、唯一SYS_ADMIN、默认seccomp、非privileged、无host mount/port或主机GUI。该capability扩展环境不能称默认Docker。

外部collector检查10份exit/report、失败保留与唯一retry、source/candidate/binary/运行hash、两run同一image identity；回读实际新包243文件并逐hash/大小核对，直接解析ASAR内5个out文件与本次source app build输出hash相同。这里的identity是Docker inspect Id/container.Image/RepoDigest，未单独存取OCI config blob或证明签名。

原 `collect-evidence` 是 S3 probe采集器，在本回归没有自定义result/receiver/leak-scan，generic `binding.result=failed` 的非适用门不冒称通过；本回归以专用逐门 `aria-regression-receipt.json` 判定，containerexit0也不替代测试exit。独立只读审查已核同候选、命令、raw、243包文件/ASAR5输出及失败+retry边界，无本收口新增阻断。

aria1准备失败原件另留：source full本已3pass3skip，新增最小helper漏传strict `{}`、后续fixture UVcache为空导致offline editable build缺hatchling，后续用例未运行；aria2仅修自有helper/cache，并用新动态identity package-manifest修正旧硬编码candidate label。没有改产品或原断言。

复现核心命令：

```sh
node tests/i06-main-platform/aria-regression-prepare.mjs e2c269ad78a78e1a042cadc93b1c81a874707153 aria2
docker build --pull=false --progress=plain -t i06-main-regression:e2c269ad-a2 tests/i06-main-platform/out/e2c269ad78a7-aria2/context
docker create --name i06-main-regression-e2c269ad-a2 --cap-add=SYS_ADMIN --network none --shm-size 256m i06-main-regression:e2c269ad-a2
docker start --attach i06-main-regression-e2c269ad-a2
node tests/i06-main-platform/aria-regression-collect.mjs tests/i06-main-platform/out/e2c269ad78a7-aria2/evidence tests/i06-main-platform/out/e2c269ad78a7-native-retry1/evidence
```

完整实际命令、唯一retry的Config.Cmd、build/source/runtime/harness/per-file hash、raw/trace/verified/fixture均在 `tests/i06-main-platform/out/i06-main-e2c-aria2-native-retry1-raw.tar.gz`：SHA `f13d9a6f0cb06b39703a91bfd76e85266c87583c0123f5c31a92ee8ccb1afa34`，154,270,058B/598entries，index SHA `f29eecfe97648e650f5c896095f4a9695d64d101b873212e4408b5cb86356205`。完整新包纳入，不借旧包字节作新证明；仅去重相同candidate tar/context source，独立原目录继续保留，archive不进Git。

定向ESLint/Prettier、22 JS语法、6 Python AST、6 shell语法通过；文档显式绕过默认reviews ignore做格式检查。本范围不把原C1 dialog stub当真实prompt；真正I04 native有外部真实prompt观测。也不把本次I04回归重命名为e2c凭据/模型领域完整平台验证：旧9fc normal22/native4/pkg2仍只绑定9fc。真实I05业务、未来最终候选组合、跨OS/签名升级/Q9及指定双模型审查另保留。
