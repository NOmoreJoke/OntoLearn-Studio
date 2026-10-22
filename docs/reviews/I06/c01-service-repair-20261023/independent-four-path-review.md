# C01 四路径修复独立静态审查

结论：本轮实际四路径 delta 与 START 票一致，未发现新增阻断 P1/P2。MF02 的精确预览回收、ZN2 的 429/503 有界重试测试、ZN3 的服务层 displayName-only 回归，在静态实现/测试设计层满足本票要求。**本报告没有运行测试，不是运行通过、指定双 Pass、原 MF02 已完整验收或父 I06 通过。** 后续原票的精确专项与普通 check 门保持。

## 输入与实际范围

- 树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-C01-service-repair-20261023`；分支 `fix/i06-c01-preview-cleanup`；实际 HEAD/base `1f3b053d8a69d1f7ddb1e29c143f648d910fe689`，产品祖先 e2c；不借 H06/H07 或其他后继拼接源码。
- 全文读取授权票 `iteration-control/2026-10-21-weekly-release/.private/I06-C01-four-path-service-repair-and-ordinary-ticket-20261023.json`：6465B，SHA-256 `73b70587ff0a1301ab9ecba6ccf56ccd3fc96c4b452650175d2c6ed5b49d2612`。
- 全文读取实际新树 AGENTS：15147B，SHA-256 `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`。本次精确静态票覆盖通用运行流程；没有运行格式、lint、typecheck、测试、产品、GUI、native、FS/OS 探针或网络。
- 读三条既有文件实际 `git diff`、完整新增测试，以及 application/core 的 discard/confirm/preview/selection 生命周期和现有 service/receiver fixture 的必要上下文。作者已停止后开始实际 delta 审查；不是仅审 scratch 草案。
- 只写本独立报告，没有修改作者文件、四外源码、锁、配置、AGENTS、旧证据或 Goal；没有提交或暂存。

## 冻结四路径

| 实际路径 | bytes | SHA-256 |
|---|---:|---|
| apps/desktop/src/main/model-gateway/model-service.ts | 22303 | be3cb0c91ead9a84d34b14429e5284789c205dd234d61eba3513c89a1f075098 |
| tests/unit/i06-mf02-preview-cleanup.test.ts | 8731 | 3477be7b5b0a516353293e4c0546e5bd896022fc1469db49e55e34547badcfce |
| tests/unit/i06-gateway.test.ts | 23642 | 09fc00d0166935760cdc857c16df5a5937513dadbc72e5364d6d83bb7ba6242b |
| tests/unit/i06-stored-result.test.ts | 51350 | 2a2b2afc9c1644e30812790bf1452b8336712f919fa5d58c00445d7002ab376e |

## MF02：分配后失败只回收新 ID

`model-service.ts:408–446` 将 `application.preview` 返回后的检查/登记/构造响应放进 try/catch。成功 required 路径仍登记本次 ID；reusable 路径仍只丢弃本次临时 preview，返回原 grant；没有无条件 finally 清理、全局 clear、串行队列调整或新公共接口。

catch 删除 `context.previews` 中的 **`preview.previewId`**，并通过先前捕获的 **同一原 `context.application`** 调用 `discardPreview(preview.previewId)`，然后 `throw error` 保留原错误。它不向新的 `this.context` 清理，不删除其他预览，不撤销其他 grant，不读取凭据或调用模型。`application.preview` 自身拒绝且尚未返回分配 ID 时，不误清其他对象。

原 `GatewayApplication.discardPreview:299–303` 只解析可信 opaque ID、删自己的 Set，再调用 core 精确删除；没有要求 application 仍 open。core `discardAuthorizationPreview:118–120` 只删该 Map ID，不 await。因此即使原 context 已关闭，重复删除已清掉的主进程生成 ID 仍是幂等操作；本生产链没有把 cleanup 抛出的异常替换原异常的已知触发。没有新增跨 await 的 ID/owner 重新选择。

新增测试的关键点均真实存在，以下是**断言覆盖设计**，不是本轮运行观察：

1. `i06-mf02-preview-cleanup.test.ts:100–128` 用两个明确 source Promise，先等 replacement 已进入第二个 load，再在同一 stack 按 FIFO resolve refresh/replacement。观察原 core `previewAuthorization` 的真返回和原 `releaseSelection` 的调用，断言事件顺序为 `preview-created → release-selection`；没有给 service/application.preview 插入新 await 或替换真实预览/清理方法。
2. 两个 test 都使用真 `ModelGatewayService → GatewayApplication → ModelGatewayCore`。repository/source/credentials 是显式 doubles；没有假称真实 Store/OS safeStorage/接收端证据。source metadata 为空是故意的生命周期 typed direct-call fixture；失败通过 `owner.handle` 验固定 safe error，正常直接 typed preview/confirm 避免把该空 metadata 误当合法公共结果证明。
3. `:145–163` 要求原 `GATEWAY_SCOPE_EXCEEDED`、三个 preview store 各为0、本次旧 ID 再 confirm 得 `GATEWAY_AUTHORIZATION_REQUIRED`，且 core.invoke/credentials.read/audit.append 都未调用。
4. `:166–187` 在**同一 setup/同一 owner**循环128次；每轮都要求新 preview 实际创建、相同原错误、service Map/application Set/core Map 各0、旧 ID 拒绝、三类外发相关调用各0。不是每轮重建 owner 绕过容量耗尽。
5. `:191–208` 在128次失败后创建正常 required preview，逐表断言 **1/1/1**；真实 explicit confirm 返回 grant 后逐表 **0/0/0**，仍无 invoke/credential read/audit。能识别误用 unconditional finally 删除成功预览，以及只清一个 hidden store 的修复。

额外 context/config 变更失败没有为本票追加新的全矩阵：代码的本地 catch 作用域已覆盖 `same(context)`、configuration/selection 复核、key/登记/响应构造的异常；本票要求的具体旧 selection 竞态已有明确反例。后续运行仍应保存首败，不用静态结论代替 red/green 或实际错误码结果。

## ZN2：两种上游状态，各最多两次同载荷

`i06-gateway.test.ts:624–648` 将原只503的“单次允许重试”测试变为 `it.each([429,503])`。每个状态沿原真 loopback fixture 回应固定上游错误正文；断言最终完整 `{ok:false,code:'MODEL_UNAVAILABLE'}`、`received.map(url,body)` **精确等于两条**相同 `/synthetic` 与固定 JSON 字节、两个 attempt-intent、最后一项 attempt-failed，并要求暴露 audit 不含上游正文。

这符合原实现审计语义：gateway:334–384 的第一可重试HTTP响应继续循环，两个 intent 后终态统一 catch 产生一次 final attempt-failed；本票没有要求或实现每个 retry response 都另写失败记录。测试没有改变 retry 代码、endpoint guard、credential 或 audit 生产行为，也没有把上游错误正文放进断言输出之外的公开结果。

## ZN3：安全身份与展示名分别验证

- 原 core 测试 `i06-gateway.test.ts:292–302` 改名为“unchanged normalized security config preserves authorization”，准确描述只验证规范化 endpoint 不变。没有继续声称它覆盖 core API 根本不含的 displayName。
- 新 service 测试 `i06-stored-result.test.ts:379–425` 沿既有真实 Store/worker/source/HTTPS fixture 取字段、选字段、设置隐私、明确 preview 并 confirm。然后只更改 displayName，仍传原 configurationId/version、相同 endpoint/model。
- `renamed` 精确等于 `{...s.configuration, displayName:new}`，而 `s.configuration` 由原 configure 和 storeCredential 返回合并，含公开 configurationId、configurationVersion、endpoint、model、credentialState='configured'；不是只比较“版本未变”或只断言数量。
- 后续 preview 必须返回同一 `confirmation.grantId` 的 reusable；start 明确使用该**原 grant**，terminal 必须 completed，真 receiver 必须只有1个请求。因此若展示名更新无意清 grant/绑定或丢 configured 状态，该测试设计会失败。
- 这是公共具名 service.handle 链的受控 fixture 回归，不是 renderer/真实业务provider/OS凭据平台测试；既有 safeStorage 显式 double、临时自签HTTPS边界保持不变，本轮没有执行它。

## 四外保护与边界

实际核 `source-before-edits.json`：355410B，SHA-256 `e0f63074a53b54dde30ecd07af90bfb503ec2d6c449fec2028297ef6fee09bfc`，947个 tracked before 项。逐项重算当前工作树 bytes SHA，仅三个授权既有文件变化，缺失0；唯一 untracked 产品/测试文件是授权新增 `tests/unit/i06-mf02-preview-cleanup.test.ts`。AGENTS 与 before overlay 同 SHA，`git diff --cached --name-only` 为空。相对Git HEAD，AGENTS 是既有 overlay；没有将它计为新产品变更或暂存。

因此本轮未改 Python、contracts、main-index/task-service/engine、JobStore、依赖/锁、GUI/App、共享四路径或其他冻结产品。没有借四路径票解除 MF01/ZN1 的独立 owner 缺口；没有对旧严重性、H06/H07结论、平台/导出/真实provider未验边界重标。

本报告可作为本票“非作者实际四路径 delta 审查、无新增阻断P1/P2”的静态门输入。作者下一步运行权限仍只来自根票及其实际准备/源冻结条件，本审查不额外授 runtime、native、GUI 或重新发审。此报告冻结后停止写入。
