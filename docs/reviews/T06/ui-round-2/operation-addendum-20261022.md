# T06 UI R2 派发操作附录（仅澄清路径与实时调度）

本附录优先解释下方原完整正文中的两个旧操作快照；原正文、原四件准备清单、产品97074205d677a8cc272426b1bcabe7140b5be085、流程8ed1fc562efd6416e9b571c4e62bc9e587db4b75、10个来源、旧报告和全部审查范围均不改。没有产品重测、模型任务创建或桌面操作。本附录与原正文同时完整供给，不能只发本附录替代完整审查。

## 已固定原四件及其含义

原文“本输入同目录 dispatch-preflight.json”是旧轮入口措辞。本轮不寻找该旧文件、不扫描旧兄弟树或全局目录：实际可用的本方预检和原完整输入是下表本人行的 out/environment-prep/preflight.json 与 own-frozen-input.md。原主四件已逐字节固定在Git25a65e3cd274a28569d47bde96e95ef4f71f1d25；它们保留为原准备快照，新增派发正文是本附录加原完整正文。

| 原主文件绝对路径 | bytes | SHA-256 |
| --- | ---: | --- |
| `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-behavior/docs/reviews/T06/ui-round-2/zcode-full-input-9707420.md` | 52775 | `6fb5a2f0a866862f587bbf6dd69474baf01aab1564107f2b32c37f0239624214` |
| `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-behavior/docs/reviews/T06/ui-round-2/minimax-full-input-9707420.md` | 52815 | `cf7788554007e3a3b380541e2de82e511e5ead4ef20aa195898e45b2d6055aaf` |
| `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-behavior/docs/reviews/T06/ui-round-2/frozen-inputs.json` | 1448 | `85b47ddb28b7f27956690e04d4e5cdafeae0068a32af3c53ac929cd61449c09b` |
| `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-behavior/docs/reviews/T06/ui-round-2/prepared-environments.json` | 28950 | `2f68ff2707522ea0bfc6722aa009a98366b2d1e4f68ffc185ecdf6079adc6dab` |

## 本方实际入口和六包精确路径

只使用与实际任务模型相符的一节。另一节仅用于说明同义映射，不授权读取另一模型输入、会话或意见。无需寻找原S1/旧UI兄弟树或账号全局目录。只读恢复原件，不执行旧preview/归档脚本；产品、完整验证与实际报告要求仍按原正文。

### zcode 本方

唯一工作树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-ui-zcode-review-9707420`，detached HEAD8ed1fc562efd6416e9b571c4e62bc9e587db4b75。

- 本方原预检：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-ui-zcode-review-9707420/out/environment-prep/preflight.json`
- 本方原完整输入副本：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-ui-zcode-review-9707420/out/environment-prep/own-frozen-input.md`（52775B，SHA `6fb5a2f0a866862f587bbf6dd69474baf01aab1564107f2b32c37f0239624214`）
- 本方本次完整派发输入副本：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-ui-zcode-review-9707420/out/environment-prep/own-dispatch-input.md`
- 本方唯一报告：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-ui-zcode-review-9707420/docs/reviews/T06/ui-round-2/zcode-glm53.md`

| 归档绝对路径 | bytes | SHA-256 |
| --- | ---: | --- |
| `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-ui-zcode-review-9707420/out/review-common-history/ui-original-artifacts-20261021.tar.gz` | 2232198 | `a51bfec8089f9a7db1578ebbfcc3570e1591beda51b956f2d8bf165a0cfab433` |
| `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-ui-zcode-review-9707420/out/review-common-history/ui-session-tool-records-20261021.tar.gz` | 6698 | `06d2e8636bbef29c6bb131bb3605c4f15e679d784137a2bffec5e58d472f5a3b` |
| `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-ui-zcode-review-9707420/out/review-common-history/evidence/ui-zcode-original-tool-evidence-20261022.tar.gz` | 3566845 | `3fabc7472130653d15d50900f36a7015d2a6cac3e286a10c321d12f1a03c5b80` |
| `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-ui-zcode-review-9707420/out/review-common-history/evidence/ui-minimax-original-tool-evidence-20261022.tar.gz` | 1494644 | `84d476e30e855aa4c0cce03164314e2512302103c521682052d84dedc806bfc5` |
| `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-ui-zcode-review-9707420/out/review-common-history/evidence/ui-9707420-owner-validation-20261022.tar.gz` | 944371 | `2d914d0d8844a1657d20252d6451c35e678bf5f925c6a7bcb4a7b4255b380f9c` |
| `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-ui-zcode-review-9707420/out/review-common-history/evidence/ui-9707420-independent-validation-20261022.tar.gz` | 1092987 | `1d98e29f857eec27a132d963443fdffef8fe3073383ae4cb5aabeced6f2a83c8` |

### minimax 本方

唯一工作树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-ui-minimax-review-9707420`，detached HEAD8ed1fc562efd6416e9b571c4e62bc9e587db4b75。

- 本方原预检：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-ui-minimax-review-9707420/out/environment-prep/preflight.json`
- 本方原完整输入副本：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-ui-minimax-review-9707420/out/environment-prep/own-frozen-input.md`（52815B，SHA `cf7788554007e3a3b380541e2de82e511e5ead4ef20aa195898e45b2d6055aaf`）
- 本方本次完整派发输入副本：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-ui-minimax-review-9707420/out/environment-prep/own-dispatch-input.md`
- 本方唯一报告：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-ui-minimax-review-9707420/docs/reviews/T06/ui-round-2/minimax-m31flash.md`

| 归档绝对路径 | bytes | SHA-256 |
| --- | ---: | --- |
| `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-ui-minimax-review-9707420/out/review-common-history/ui-original-artifacts-20261021.tar.gz` | 2232198 | `a51bfec8089f9a7db1578ebbfcc3570e1591beda51b956f2d8bf165a0cfab433` |
| `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-ui-minimax-review-9707420/out/review-common-history/ui-session-tool-records-20261021.tar.gz` | 6698 | `06d2e8636bbef29c6bb131bb3605c4f15e679d784137a2bffec5e58d472f5a3b` |
| `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-ui-minimax-review-9707420/out/review-common-history/evidence/ui-zcode-original-tool-evidence-20261022.tar.gz` | 3566845 | `3fabc7472130653d15d50900f36a7015d2a6cac3e286a10c321d12f1a03c5b80` |
| `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-ui-minimax-review-9707420/out/review-common-history/evidence/ui-minimax-original-tool-evidence-20261022.tar.gz` | 1494644 | `84d476e30e855aa4c0cce03164314e2512302103c521682052d84dedc806bfc5` |
| `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-ui-minimax-review-9707420/out/review-common-history/evidence/ui-9707420-owner-validation-20261022.tar.gz` | 944371 | `2d914d0d8844a1657d20252d6451c35e678bf5f925c6a7bcb4a7b4255b380f9c` |
| `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-ui-minimax-review-9707420/out/review-common-history/evidence/ui-9707420-independent-validation-20261022.tar.gz` | 1092987 | `1d98e29f857eec27a132d963443fdffef8fe3073383ae4cb5aabeced6f2a83c8` |

上述前两包位于各自 out/review-common-history 根，另四包位于其 evidence 子目录；原正文旧 evidence/ 相对写法只按这里的精确路径解释。现有安全恢复副本及1305 regular成员的来源核验仍依原准备回执；没有搬动、覆盖或重新执行它们。

## 账号恢复与桌面窗口分别记账

总控传达的最近官方UI观察已恢复至93%/92%；恢复原因unknown，未消费reset，也没有新增支付、升级或切换模型。本线不再因旧文案把整个Z账号视作总hold。此为总控转达的官方观察，不冒称本附录作者刚刚查询、执行恢复或保证未来额度。真正派发仍由owner读回当前任务GLM-5.3/max/yolo或M3.1-Flash/xhigh/始终授权，以及实际完整受理/身份/终态。

本附录制作时GUI唯一owner为T09，T06仅等待根明确本线lease；这是桌面资源队列，不能合并为“账号仍待恢复”。根授本线窗口前不操作审查应用、不盲重发、不新建Z或重复消费reset；获本线窗口后依当时实际账号可用状态创建正常完整新任务。这里不授lease、不新增平台逐次确认豁免，原额度恢复机制、无付费/不读搬凭据与全部门禁保留。正文其他历史队列按其原时点解读，实际调度以根最新明确交接为准。

根已接受S1/UI R2的完整静态准备，静态接受不是模型Pass或产品/容量验收。UI本次只补两个P3操作定位；S1原五件不补提交或修改。容量P2/Q5仍待两指定任务各自独立实质裁决。双方完整新任务都列队，未沿用旧Pass，禁止将同轮M意见透给Z。
