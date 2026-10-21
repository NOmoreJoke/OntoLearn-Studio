# I06 命名接口文档对齐检查

2026-10-21；文档子任务 worktree `I06-interface-alignment` / 分支 `feature/I06-interface-alignment`，固定代码 base `9fcba6634d5c16983c36ef671d4ec8e79694b6d6`；批准依赖仍为 develop `5f910b52c69d86a1076b2032e5d3c63e715947f3`。本记录是独立文档线的实际校验回执，不是指定第三方审查或平台通过报告。完整状态由 [status](status.md) 维护。

唯一提交范围为 `docs/iterations/I06/{narrow-interface-draft.md,narrow-interface-examples.json,main-integration-handoff.md,stored-result-plan.md}` 与本检查。未写 root checkout、实现、契约或总控文件，未采用 I05 未批准候选。已读取最新 AGENTS、scope/state 和完整 Goal（含第九节），protected AGENTS SHA-256 为 `db1fb184809932a27c5bfd8c91b72837d719cdbdc07d7a83860e5cba38529786`，保持 dirty 且不暂存。

## 已对齐内容

- 12 个真实 main 专名方法及严格 params/result/reply，`configureModel` 双 null 新建/双 UUID 更新，`storeModelCredential` expected configurationVersion 与新版本响应，privacy 字段名。
- 10 个固定 GATEWAY_* 错误及独立取消结果，合法失效 context 的 AUTHORIZATION_REQUIRED；endpoint 变更清旧 key，未新录入时 CREDENTIAL_UNAVAILABLE，重新录入后旧 grant 仍撤销。
- 有限 16 字段、字段描述/类型/nullable/requires 闭包、whole/fields 实际 row/UTF-8 byte count；main owner/context/ledger、UI 只读结果 cache、单 profile 锁、初始化失败隔离/5 秒退出等待、fatal UTF-8 响应。
- 固定 main 合成 policy + 批准 test.read echo worker，static dependsOn 非生产溯源；正常生产 models=[]/runtime-only，可信 launch fixture 才启用有限策略。I05 新业务模型须在新执行语义实际批准合并后另绑定。
- 保留显式历史已允许、无自动 live-current lease 前置、读→send 观察窗口，以及无 M1 全列 provenance/恰好两 API/I05 编号前置的原需求边界。

## 实际检查

独立 `npm ci --ignore-scripts --no-audit --no-fund` 完成，没有启动 Electron/native/GUI/Keychain/CUA，没有真实 key/model/业务外发。仅执行本次文档所需检查，不重复整库、Python、sources 或平台测试。

`npx vitest run --config out/interface-alignment/vitest.config.mts` 对每例真实调用固定源码的 `validateModelParams`、`validateModelResult`、`validateModelReply`、`matchesModelResult`；两项非法 SafeError 另实际核对 safeError 固定降级。错误 reply 无成功 data，因此 result/matches 为 false；合法参数的运行权限错误在 schema 层仍为 true，不能记作结构拒绝。源代码无需服务实例或网络。

首轮 43 项中 6 项失败：旧合成 result metadata 的 dependencyVector 为空，现有语义校验要求 `facts:asserted`。保留失败 log 和 receipt，修正案例为合成 `facts:asserted:1`，未改契约/实现。修正及最终格式后运行均为 **43/43**：41 个独立案例、原 ID 保全检查、source-bound receipt 检查。保留原 35 例 ID 及顺序、5 个场景 ID 及顺序；追加 6 例覆盖双 null 混用、凭据缺 expected version、17 字段、重复字段和 requires 闭包正反例。

最终四个文档 prettier check 与 `git diff --check` 通过；完整命令与校验脚本位于本 worktree 忽略目录 `out/interface-alignment/`。最终 validator receipt SHA-256：`d045e624123ccaa8889a73116589011758e40a785170bf403cb5a72f777c81d7`。该 JSON 绑定案例与 5 个实际 contracts 源文件 SHA，列出每例四项实际/预期布尔值。最终执行 log SHA-256：`d655269aab4cf12b7cf11d3c4f9d518f59c22bf03a6b8cff158524ed8e8c942f`。

| `11666cfc` 初次对齐文档原件 | SHA-256 |
| --- | --- |
| narrow-interface-draft.md | ba209a47ebf8911ec69fe9db6e838bf6faebf6d044e1b7cc362fc19aea50530e |
| narrow-interface-examples.json | 36f5a933894f72daa4f12fa4ceb3648d630c67ed7bdcc641808a2a2ff8fac61d |
| main-integration-handoff.md | a3c24d347a79251bb134502dea4c6a190cf4c9d0ecb3f83103d44594dc8c9b0e |
| stored-result-plan.md | 4db4e48b62803b6c2fcb6544d9c5e6277b6b771a552a626efa604cc7ba23d247 |

## 证据边界

本次没有执行 main 服务、preload/UI、真实 receiver 或平台。根线已有 998 TS/1052 Python/check/source12 是其固定实现验证回执，不是本子任务复跑；新 main/preload/UI/safeStorage/Linux 平台线尚无本次通过证据。原私有字段证据按原 hash 引用：完整 body 有执行断言，独立 probe 未归档成功 HTTP body，不声称独立重扫正文。后续正式链仅将合成 receiver 完整正文及 hash 放忽略测试证据，排除 headers/真实凭据/业务数据，产品日志不记 payload。

五个 integration scenarios 保留为验收/边界描述；案例 validator 通过不表示场景执行。无当前导出入口即无实际导出测试，不发明 mock。完整 S3、其他平台、同一冻结候选指定 GLM-5.3/最高与 MiniMax M3.1-Flash/xhigh 全新全范围双方独立通过、PR/实际 CI/远端合并不由本文记为完成。未 push。

## 文案复核追加：ADR、验收映射与终态顺序

本次后续仅更正文档事实，运行源码仍固定 `9fcba6634d5c16983c36ef671d4ec8e79694b6d6`。新增唯一可写范围为 ADR-0004-model-gateway.md、acceptance.md，以及独立审查指出的 narrow-interface-draft.md 一句终态淘汰顺序；本记录追加证据，不写状态或实现。

ADR/验收映射原“未公开注册”“无设置页/未来录入”“待 owner 交接”等口径改为开发分支已实现 12 方法/main/preload/UI、实际平台待新完整证据；保留早期来源与原验收，不把 I05 编号或 Q9 真实协议选择扩为无关合成链前置。内部 core configVersion 与公开持久 configurationVersion 分别生成 UUID：前者绑定 grant/core preview/audit，后者绑定 UI/录入 CAS/service 预览版本；不把二者称为同一值。

独立审查发现 model-service 的 Map 在调用启动时插入，完成后 set 同 key 不改变插入序；prune 过滤终态再 slice。因此 draft 的“终态按 main 完成序淘汰”更正为“按调用登记（启动）顺序在终态集合中淘汰”。未改实现或验收。

`11666cfc` 原 raw `out/interface-alignment-raw-20261021.tar.gz`（SHA-256 `458ddca166bb568532944741a37216996c92e9c82925ddeca1d940564534cd01`）及其 21 份源码/文档快照、validator receipt/首轮失败/最终成功日志保持原件，绑定初次对齐文案，**不代表本次新版文案快照**。原 validator receipt 仅绑定未变案例与 contracts 源；41 例 JSON SHA-256 仍为 `36f5a933894f72daa4f12fa4ceb3648d630c67ed7bdcc641808a2a2ff8fac61d`，不重跑未变案例，不覆盖旧 receipt。

| 本次文案 | 新 SHA-256 |
| --- | --- |
| ADR-0004-model-gateway.md | 612763d70362da65dff57d8e9615379640748dd960f73724bd11ca527955f3f8 |
| acceptance.md | 981daada9d349fe6bdf7a345ba198118e7374122970b7bd501b36e72cc8b448f |
| narrow-interface-draft.md | 619a97612bcd2d8305278c6d4299fd1cc89da035c399815c07f4a23a77e03484 |

本次只执行 4 份修改文档 prettier check、git diff --check 和静态事实/范围检查；未改样例/契约/实现、未重跑 validator/整库/平台。新文案快照另存 `out/interface-alignment-followup/`，不能借初次归档替代。独立只读复核由根线已有 review agent 执行，其结论另行记录；本记录不预设通过。
