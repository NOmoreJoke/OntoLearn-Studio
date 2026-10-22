# T03 standalone profile 源码与单文件 unit 最终移交

本次完成四产品路径实现、两轮非作者实际代码静审与一次获准单文件 unit。最终产品提交 `e37cc2b161b53a6250a4085104ee955c423fb149`；实际单测 **217 passed in 3.59s，退出码 0**。没有运行真实 standalone A、PyInstaller、source/frozen B 或 native；本包不代表实际产物或 root 批准。

## 固定身份与采用入口

- 源基线 `c706f8f581785053278f26e48d21d7bebadf09f6`；已采用 M08 `a633ef391344cce60807638ecd942d4e2183c7b4`。
- 产品仅两提交：`d4686b1769b5925190a9e7afcc23b92d5db04d4d`（首次实现）、`e37cc2b161b53a6250a4085104ee955c423fb149`（F1/N1 与 root scratch 合同修补）。
- 四源真实 bytes/SHA 见 [final-source-unit-handoff.json](final-source-unit-handoff.json) 的 `products`。最终新 contract 为 55577 B / `a93a5dc5b0b002482db8e99e072aab6d27d3a0cf58f59bfd9b0a7643305ead0d`，与 reader 常量一致。
- 供选择采用的完整四源 patch：[final-product-c706-to-e37.patch](final-product-c706-to-e37.patch)，由固定 `c706..e37` Git 对象生成；真实身份列于 handoff。未改 I05 consumer 或其他产品。
- 本目录唯一总清单为 [master-manifest.json](master-manifest.json)，路径基底固定为**本 process 目录**。它自排除，列全部其他实际 process 文件及固定四源/保护向量。子阶段 manifest 是原始历史证据，不替代本总清单。

## 审查、失败与修复链

首审 [review-d4686b.md](independent-code-review/review-d4686b.md) 发现 F1 blocking P2（新合同仍混 parent 路径、身份与授权叙述），另有 N1 P3（hash IO 故障仍宜保无条件原流路径）。首报及八成员 manifest 全部原样保留。

F1/N1 精确修补统一 source/frozen/contract/target/PYZ-CArchive/launcher 域、c706/a633 与历史组件分域、当前静态与条件 unit 授权边界、16 类必需负例；receipt 无条件保留 stdoutPath/stderrPath/receiptPath。六个新增关系 unit 及 Node 实际 stub argv/env/path、三阶段 hash-IO 负例防止回退。完整 delta/原流/静态与首败见 [delta-f1-n1](delta-f1-n1/delta-freeze.json) 与 [unit-author/delta-f1-n1](unit-author/delta-f1-n1/unit-delta-freeze.md)。

复审 [review-e37cc2b-delta.md](independent-code-review/review-e37cc2b-delta.md) 将 F1/N1 **CLOSED_STATIC**，0 新 blocking P1/P2；controller 之后另发精确 unit START。历史报告里的 NOT_RELEASED/runtimeExecuted=false 是当时状态，没有追改成后来通过。原 reader/unit lint 首败、delta E501、setup 兼容比较首次 AssertionError 和原 stdout/stderr 均保留。setup 首错只有当时 tool 输出的说明与比较 JSON，不伪称有未保存的重定向原 stderr。

主控 intake 曾将子 manifest 路径误以 delta 子目录为基底，形成 ENOENT；改为本 process 根后核46成员+4产品通过。独立说明见 [controller-intake-path-base-first-error-note.json](controller-intake-path-base-first-error-note.json)，不改首审/原 manifest，也不把它记为产品或 unit 失败。

最终过程封存首次普通 git add 受 *.log ignore 影响，只入90/172文件；精确集合断言已报错，但该 shell 未 fail-fast 而先创建不完整本地过程提交。随后仅对本process force-add原流并更正该未外发提交；首次身份、ignored差集与修正说明见 [process-freeze-first-stage-error-note.json](process-freeze-first-stage-error-note.json)。产品与unit结果不受影响，原件不改。

## 隔离环境与实际 unit

候选旧 Python 环境因 root pyproject 不同未采用；随后获准 `uv sync --frozen` 创建本树 own .venv，own UV cache/TMP，只读既有 CPython3.12.12 基础解释器。package.json/package-lock 匹配后复制独立 Node 实体，无共享 mutable node_modules/site-packages、无 npm/Electron 启动。兼容比较、首错说明、setup/copy 完整收据与原两流均纳入总清单。

唯一运行 argv：`/Users/kyle/.local/bin/uv run --frozen pytest packages/engine/tests/test_semantic_build_provenance.py -q --maxfail=1`。运行目录为本树，固定源 HEAD=e37；显式最小实际环境、own venv/cache/TMP、UV_NO_SYNC=1/OFFLINE=1/DOWNLOADS=never/DONTWRITEBYTECODE=1/NOUSERSITE=1 全列 [receipt.json](unit-run-e37-first/receipt.json)。没有 dump 父环境。

实际 PID83488；UTC 2026-10-22T23:10:43.914439 至 23:10:49.612665，wall5.698秒（限600秒）；status0，无 timeout/overflow/IO 错误，原 stdout340 B、stderr0 B，range/hash/ref 完整。四源 before/after 等于 e37 固定 Git 字节。新 Node wrapper 在这一次 unit 内断言31项受控 run/io/uuid stub；成功 TAP 未另存为独立原流，不捏造额外 Node 执行或原件。没有再次运行单测。

## 合同机械映射与证据界限

新合同 JSON pointer **`/buildScratch`** 是机械 mapping；单独快照 [final-build-scratch-map.json](final-build-scratch-map.json) 与身份/pointer [reference](final-build-scratch-map-reference.json) 可直接给 I05 使用。runRoot 模板 `build/i05-semantic-parity/<fresh-uuid>`，work/spec/dist/generated/licenses/provenance/binding/三 child raw/receipt/control 及两 cache/TMP 全属于 own runRoot。

`/buildScratch/sampling/thresholdBytes`=**8589934592** 是 I05 外部 caller 对整个 runRoot 单一递归域的账面阈值，不重复加子域；I05 拥有实际前后采样、监控和超限拒绝。builderEnforced/OS硬限制/runtimeGuarantee 均 false。`/buildScratch/executionGuard/guardRequired`=true，缺 guard 为 BUILD_SCRATCH_GUARD_REQUIRED，permit digest 不能绕过。这里没有实际 UUID、采样结果、OS quota 或 build 执行授权。

25 analysis imports、24 engine PYZ 模块+独立 anchor、35 source guards、5 buildInputs、22 suppliers、4 resources、2 inputs、8 distributions 是合同/静态/受控 unit 范围，不是实际 A 的闭包或运行证明。旧 parent entrypoint/合同/锁文件与32非产品 guards保持固定；AGENTS15147/de15 覆盖仍未暂存，不进入任何本次提交。

## 后继门

I05 consumer/选择采用与独审、完整 saved loader JSON join、scratch 实际 guard、standalone A、root 完整 actual artifact/binding 批准、fresh source/frozen full-v1 B 各一次，以及 native/parent平台/GUI/业务/发布仍另门未验。最终仅纯 process 本地提交；其 commit/tree 在外部移交消息给出，以免摘要循环。封存后 STOP，无 push/PR/merge 或后继运行。
