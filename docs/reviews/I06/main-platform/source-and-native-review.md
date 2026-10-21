# I06 正式接线 Linux source app 与原生恢复回执

固定产品提交 `9fcba6634d5c16983c36ef671d4ec8e79694b6d6` 的 source app 实际 Linux 验证通过：r11 同一次运行 22 项场景、3 次合成 HTTPS POST；独立 native4 真实 crash→恢复提示→第二窗口只读恢复通过，接收次数保持 1。两次 collector 均核对实际运行源码、构建产物、harness、binary 与 host 冻结身份。native4 与 r11 的编译 app 和 binary 完全相同。包内 executable 尚待独立增量，不能以这份 source app 证据代替。

本报告及 `source-and-native-receipt.json` 是本范围验证回执，不是整个 S3 或指定双模型审查通过报告。独立只读审查已核验 r11 两轮 actual source page/catalog/selected/preview/grant、完整 body 与未选字段零外发；另核验 native4 frozen/executed脚本、哈希、真实 prompt/actions、前后项目/ledger/outcome/Store 相等。审查未执行应用或修改文件。

## 实际范围

r11 证明默认 local、无项目禁用、实际 gnome_libsecret 加密与设置恢复、凭据无读回、真实 worker 结果字段选择/预览/授权/HTTPS、同输入第二结果复用授权且其他列零外发、纯文本响应、reload 只读不重发、第二相同 profile 进程退出、定向取消、local/config/endpoint 变更撤销旧授权、凭据版本 CAS、password 切换清空、新配置表单跨轮询保留。另在 actual audit 不安全时阻断 POST，而相同真实 atomic worker 仍完成 Store 提交；模型初始化失败也不阻断本地 Store/窗口。实际 basic/unavailable backend 均零凭据文件，actual worker protocol 拒绝 main-only 方法。完整 case 名称和结果在 JSON 回执，未拼接旧失败 run 计数。

A03 的 actual body 是 3 份相同 693B 的 public-only JSON 投影；原 source page 含未选私列及派生列，Dedicated raw 保存两轮不同 result/job/catalog/selection 与同一 grant 的真实身份。源 row UUID/原 ordinal/私列/派生值均未进入 receiver body。这是固定 main-owned 有限模型与批准 test producer 的 M0 证明，不是 I05 真实业务溯源或通用 CSV 能力。

native4 故障前 inspector 已实际关闭且 `url()===undefined`，全程无 renderer CDP；正常产品恢复函数与 dialog 未替换。外部 xdotool 在容器 DISPLAY 读取可见标题 `OntoLearn Studio 窗口恢复`（id6291458），实际按 `shift+Tab Return` 后得到第二窗口。整个 project DTO、job/result/stateVersion、operation marker、context/selections/invocations/completed outcome 前后严格相等，只读恢复不重发。未测 unresponsive/hang 矩阵；容器 CJK 字体缺失，截图的方框不能作为中文可读性证据。

## 环境与复现

自有新依赖镜像执行锁定 `npm ci`、`uv sync --frozen`、正式 `npm run build`，运行 Electron44.9.0/Node24.22.0/Linux arm64/Xvfb/Openbox/dbus/GNOME libsecret。所有数据、CA、keyring 和凭据均合成，runtime network none，无 host mount/port、非 privileged、USER i06(1106)。明确授权唯一增加 SYS_ADMIN capability，保留默认 seccomp，Chromium helper root:root4755；actual noSandboxSwitch=false，renderer NoNewPrivs1/Seccomp2/filter2>main1。这个环境具有额外 capability，不是默认 Docker，也不代表 Mac/Windows 或生产 OS sandbox 证明。

实际命令（均在本线 worktree 执行；完整 build/run/inspect 与实际 argv 在 raw）：

```sh
node tests/i06-main-platform/prepare-build.mjs 9fcba6634d5c16983c36ef671d4ec8e79694b6d6 r11
docker build --pull=false --progress=plain -t i06-main-platform:9fcba663-r11 tests/i06-main-platform/out/9fcba6634d5c-r11/context
docker create --name i06-main-platform-9fcba663-r11 --cap-add=SYS_ADMIN --network none --shm-size 256m i06-main-platform:9fcba663-r11
docker start --attach i06-main-platform-9fcba663-r11
node tests/i06-main-platform/collect-evidence.mjs i06-main-platform-9fcba663-r11 i06-main-platform:9fcba663-r11 tests/i06-main-platform/out/9fcba6634d5c-r11/evidence
node tests/i06-main-platform/prepare-build.mjs 9fcba6634d5c16983c36ef671d4ec8e79694b6d6 native4
cp tests/i06-main-platform/Dockerfile.native tests/i06-main-platform/out/9fcba6634d5c-native4/context/Dockerfile
docker build --pull=false --progress=plain -t i06-main-native:9fcba663-n4 tests/i06-main-platform/out/9fcba6634d5c-native4/context
docker create --name i06-main-native-9fcba663-n4 --cap-add=SYS_ADMIN --network none --shm-size 256m i06-main-native:9fcba663-n4
docker start --attach i06-main-native-9fcba663-n4
node tests/i06-main-platform/native-collect.mjs i06-main-native-9fcba663-n4 i06-main-native:9fcba663-n4 tests/i06-main-platform/out/9fcba6634d5c-native4/native-evidence tests/i06-main-platform/out/9fcba6634d5c-r11/evidence/binding-evidence.json
```

普通日志、私有 gateway 文件与所有实际项目 SQLite 字段和 raw pages/WAL 扫描通过；Store 允许原有合成 source rows，拒绝 key/model response/完整 outgoing body 新写入。Headers 仅内存校验不归档，key 不入 argv/普通日志。额外从已退出本线容器只读回收 SQLite 与私有 gateway 原件并逐文件哈希，供复核；没有改写原扫描 receipt。无项目 export 入口，实际导出产物未验。

## 失败原件与边界

r1 archive 准备失败、r2 build manifest 权限失败、r3仅build、r4 Playwright loader 强制 basic（未录入、0POST）、r5 direct native backend但UI初始重挂时序失败、r6 no-sandbox下checkbox驱动失败/0POST、r7仅capability preflight、r8 task刷新驱动失败/0POST、r9 alert locator歧义、r10旧current拒绝码预期错误均保留，均不记最终通过。r4 actual loader/version/hash 可复核，basic强制来自测试 loader，不是产品缺陷。r5/r6只作有界事实，不能算最终native/sandbox。

native1准备阶段错误（本地digest解析及空格式管道）未启动应用；native2目录重复创建被静态审查拦截未运行；native3实际首个只读 restoreTasks 受初始view generation fence拒绝，0POST且未注入故障；native4只对该初始固定拒绝做有界重试并记录，恢复时严格相等，未降低产品判断。未覆盖失败或倒贴新 hash。

完整 raw 归档位于本线 `tests/i06-main-platform/out/i06-main-platform-9fc-r11-native4-raw.tar.gz`，SHA-256 `9dac44b0cd0a588c902b85b35079f691a52ef13a0e51dce5c9b9e5f9dd99f0fe`，953文件/13,744,955B，逐文件 index SHA `d2602b4f18ca9eb67ebf727e0b8a0ee580d4a0a421705717ebf000f3312b070e`。保留每次 build/run/inspect、frozen harness/identity、成功和失败原件及一份相同 candidate tar；仅去重 context/source 与候选 tar，排除依赖 cache。原独立运行目录仍保留；archive 未放进 Git。

定向 ESLint/Prettier、5 Python文件 Ruff check/format、11 JS语法、5 Python AST、2 shell语法和 diff 检查通过；没有重复全库998/1052。`docs/reviews` 默认被格式工具忽略，因此文档以 stdin 明确检查。最终交付 harness 与实际 frozen 版本分别记录；仅格式/采集/README补充不会倒称为已执行 runtime。后续打包、I05批准后必要联验、指定双审与真实服务Q9分别保留。
