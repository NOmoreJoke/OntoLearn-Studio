# T05 批次复核提案修订一：独立静态审查

结论：**最终固定 e5f 修订稿在其写明的可信原 child 输入、限额及当前发行前提下可接受，未发现算法或费用界阻断，可交总控继续决定精确实施阶段。** 三池成功蕴含和整次求和的文档缺口已修正。原 d7df 稿非阻断 N1 已通过唯一句澄清及实际 delta 核验关闭，详见末节。I05 实际 capture、可信分配账本、有界恢复 R 及 T01 正式跨 child 载体仍是未交付依赖，不能把本结论写成 API 已实施、已批准消费或 selected 已闭环。

## 固定对象与实际审查范围

- 工作树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T05-quality-reasoning`。
- 实际 HEAD：`ede46ad0ad78323f805561e9eeeba20067b27253`。
- 全文审查原修订提案：`docs/iterations/T05/rule-batch-revalidation-proposal.md`，32567 B，SHA-256 `d7df87c723bdc340b0b039fc0e79b742e3b162a4393b386fb8283b574d55125d`。最终稿为32769 B，SHA-256 `e5fefefd78f62b4b5c989acd02aba6dc227042a3517fe3d90dc23bc0e3bae750`；全文旧稿加唯一句 delta 覆盖最终实际文本，未重审无变化数学。
- 全文审查 inputs：10201 B，SHA-256 `97127cb4b958d5c99af85424ac0de3113032ebcaca0bc3f5bd2073c67d75fd3d`；receipt：2533 B，SHA-256 `c1789edf5ddf52f70f17e28d79af75acfa2bac44f1c3b491804bf1f0a57b1a3f`；manifest：1567 B，SHA-256 `d4fa7dedc61002b72788e6c76a1ffc4dc55129005b42e401326c192f2798aa40`。
- 已全文读取 I05 `profile-selected-carrier-facts.md` 的固定 5316 B／`d7f128c22719561e75a737a7093a01d19132265f805f429eb9811cf7b74dcd47`，及总控静态报告 17078 B／`a44ed73f2668a7684b55adc4cf94b861bb1e4fd243660069207588b03da66385`，实际源与本目录 raw 归档逐字相同。本线未追读 I05 动态产品源码，故关于其现状是 owner 事实材料，不是本审查的运行验证。
- 原 c1a 提案归档已与 `git show c1a616bbc8fc699ad11cd73cbf663c3692515e5f:<path>` 逐字核验，24357 B／`578032f78cd8571496c5709f18c7f5c02292db89cf316a52e3d2f49c61234bea`。先前静态审查已读固定旧 firing/profile/terms/comparator 源码及 numbers 相关计费部分；本次承接旧结论，只核真实 child 修订和边界，不重复机制执行。
- 实际静态校验 manifest 所列六对象、两份事实源归档及原 c1a 归档。旧 20 个源/测试/夹具路径逐项读取字节，与固定 `1e3e0ee1d9d5b70f1f59233d0a3c64f6d85fd2cb` 和 c1a 的 Git 内容及 inputs 中长度/SHA 全部相同。这是归属与完整性检查，不是测试通过。

问题严重度：本固定修订未发现 P0/P1/P2 算法或费用界缺陷。非阻断 N1 是明确相等比较连接边的表述补充，不新增比较、费用或算法；本报告末节记录其新稿点验。以下为通过依据及实际采用条件，不能省略成无条件批准。

## 1. 新签名、限额来源及复制

新签名要求 keyword-only 的 exact `ProfileLimits` 与 exact bool `disabled`，saved 明确为批次或 None，返回 `batch-consistent`／`definition-only` 两种不同事实。新预算 `/2` 与旧未实现默认三池提案 `/1` 分开，旧 PROFILE、mechanism-budget/1、Budget 和 ProfileLimits 不改。

逐字段 exact int（拒 bool）、非负及不超过旧默认的验证，与固定 ProfileLimits 的收紧政策一致；用固定字段表复制后再建三个 Budget，可避免调用期间外部修改原 limits 对象改变配额。该字段表长度固定，属于入口控制单位，不引入随规则/数据增长的扫描。limits 的形状验证不能证明它就是原分配；文档对此没有混同：批准 allocator／原不可变上下文提供原值，I05 校保存值一致，跨 child 另由 T01 核 producer 和输入绑定。

“每 child 都传默认 ProfileLimits”仍能通过单次数值验证，但可能违反整次 Σ 限额；文档已明确由 I05 总入口拒绝该调用方式，不声称纯函数能从参数认证分配来源。这是必要边界，不是遗漏的机械鉴权能力。实际实现测试必须分别断言 T05 数值形状拒绝与 I05 来源/账本拒绝，不能让纯函数测试冒充可信 allocator 已接线。

## 2. 原 child 三池与成功蕴含

修订不再以默认三池复演紧配额 child；三个池各以相同原 L_i 独立构造，不借用、重置或动态放大。对合法原成功批次：

1. replay_i 按同一 definitions/Catalog/原有序完整 matches 调旧 compile 和 evaluate。原 bindings 顺序、false matches、when/proof/source 保留，因此旧 `_resolve` 线性查找、全部比较、重复匹配检查及排序/编码的操作与收费相同；原成功即满足同一 L_i。
2. saved-encoding_i 逐字段、逐出现编码与原最终输出同内容的保存值，是原成功执行的完整输出编码片段。别名和共享 source 未获免计，因此没有把独立新对象误当成本更低的特殊情况。
3. saved-issuance_i 对每个保存 true comparison 的 left/right 调原 check_value，是原 compare_values 中相同调用的子集。它包含每出现的输入编码和哈希 work；没有把 parse 重新发行混进子集。当前重新发行、强引用及同模块身份仍是输入前提。

原更紧 term/source/integer/结构和累计限制同样随 L_i 进入三个池；保存编码与原合法输出相同，发行校验与原相同 operand 校验对应，故这类限额不会因为只使用更紧 L_i 就破坏片段/子集证明。恶意内容可以在自己的有界池 resource/internal 失败；本证明不承诺损坏输入成功。

入口浅层 guard、一次付费 typed 编码、唯一组/比较 guard＋发行遍历的旧消歧保留。沒有另一个递归预扫或第二轮逐组 shape 检查。limits 固定字段复制是新增常数工作，已明确归入口1；两次 payload 和 digest/profile 比较仍预扣。若实现增加恢复、排序、复制、哈希或额外遍历，应重算，不能凭此静态稿免检。

## 3. K_i 与整次求和

固定 C=32 是保守比较数上界，实际 guard 用 L_i.comparisons；F_i、O_i 来自原分配。两次 payload 比较、一次 digest、一次 profile，加唯一组/比较循环及入口，得到：

```text
K_i = 1 + F_i + F_i*C + 4*O_i + 2*H + 2*P + 4
work_i <= 3*W_i + K_i
input_i <= 2*I_i
output_i <= 2*O_i
```

Σ 式逐 child 相加成立；将 K_i 展开可得：

```text
sum(K_i) <= N*(2*H+2*P+5) + (1+C)*sum(F_i) + 4*sum(O_i)
```

修订正确保留 N 份入口/digest/profile 常数，没有用单 K 代替整次，也没有把每 child 默认 W 累乘后叫整次3W。N≤100 及 ΣW_i/I_i/O_i≤整次旧上界必须由实际 allocator/账本提供；ΣF_i≤F 未证时不得使用整次 F 简写。文档对这一缺项给出的较松 N×默认上界仍是有限数学界，不是对现 allocator 已验证的陈述。

失败 child、disabled、空定义及重试均登记，已耗额度不退回发新池，能避免通过重试或拆更多 child 无界领取预算。单次函数无法独立约束调用次数，因此这仍是 I05 入口的真实实施义务。计量单位仍只是机制 debit／编码字节，不是时间、峰值内存或整个 child 的系统资源证明。

## 4. disabled、空定义和空批次

修订正确区分以下路径：

- disabled：必须 original_matches=()、saved=None，仅在原分配 replay 池 compile；不 evaluate，不虚构成功批次，返回 definition-only。
- 空定义且原生产无 batch：definitions=()、matches=()，compile-only；原生产确实存在空 batch 时完整重放并核该 batch。
- enabled 非空定义但无匹配或全部 false：原来确有空成功 batch，仍 compile＋evaluate＋完整批次核验；saved=None 失败，不能偷换为 definition-only。

compile-only 在原 compile 已于同一 L_i 成功时，是原成功片段；如果原 disabled 路径从未 compile，则“生产没有报错”不能推出新 compile 成功。文档已明确补这项真实证据，失败安全报告，未伪造成功蕴含。compile-only 消耗最多一个原池并落在统一三池上界内，不把另外两个闲置池借出。

绑定 disabled 状态和“生产有无 batch”仍需真实上下文；纯函数无法由调用方声称的 bool 认证。修订已明确，不能把返回 definition-only 作为执行事实或用户启停授权。

## 5. 已知载体缺口与外部 R

修订不再把 I05 已回答的事实留作泛问：当前 controlled 真实包含原有序 true/false matches，但没有进入返回载体；JSON 无 exact records 恢复器；强引用只维持当前进程身份。它记录 temporary carrier 已另获授权，但尚无本线可核验的固定交付，未将授权写成完成。

新的临时 capture 必须保实际传入 evaluate 的同一 tuple、原 definitions/Catalog/limits/disabled，不从 true groups 重建，也不重跑图。延长生命周期、完整 JSON 投影、复制/编码和限额取得成本须在图/载体侧预扣，不能用“只是引用”免去新增表示成本。

R_work≤原 W、R_input≤原 I 仍明确是待证明申请。唯一 term parse 的来源不能覆盖缓存键/source 全字段编码、比较/哈希、重复出现扫描、保存 domain/value/language 全对照、JSON/精确整数解码及载体/hash。修订要求独立整次 R 界及 success→restore→recheck 实测，不能重复领取每 child 默认 R，不能用重算值静默修复坏字段；alias 缓存也不免除 T05 每 occurrence 编码/发行费用。这些外部成本未混入3ΣW_i。

T01 仍需实际成功 producer、不可变项目/快照/定义/source 绑定、implementation 三字段、作用域与访问权限、跨 child 保存窗口/撤回/GC。历史/unknown 不会因数学一致性升级 current。同进程原对象复核不是保存字节恢复，更不是跨 child selected 验收。本稿没有错误承诺这些门已闭合。

## 6. 路径、候选及验收边界

仍只提议 rule_revalidation.py、专属 test 和 fixture 三条新增产品路径；旧20实核不变。另一隔离 IRI 修复不在本轮消费/审查基线，修订已要求未来如需采用先拿独立批准固定 ref 并重核成本/清单，未以本次旧20等值证据冒充新基线。

新测试计划已补紧原限额、全局账本/N=100/重试、disabled/空定义/空批次及恢复各池失败的边界。它们现在是计划，不是实际通过；原静态 source40000 见证也未被升级为旧执行成功。本次没有运行该见证、机制、parser、产品测试、构建、probe、GUI、e2e/native/HMR 或外部模型。

可交总控决定后续精确私有 API 阶段；真正代码候选须另获路径/依赖/隔离授权，完成新同候选独审和实际必要测试。I05 selected 消费要等其 capture/可信分配/恢复及 T01 相关依赖交付，不能因静态方案可行提前关闭。原 Goal、Q6、指定双审、包/平台、CI及正常合并和完整父验收门均保持。

## 7. N1 唯一句澄清及最终固定点验

原 d7df 稿的步骤4仅写“两次 payload 与一次 digest 比较”，比较连接边可从前后文推断，但不够直接。非阻断 N1 建议明确三条等式，防止实现者误重复同一边。这是精确表述补充，不是原费用界或算法反例。

已实际读取 d7df 原件与最终 e5f 稿的完整 diff，唯一正文改动在步骤4，明确预先付费并依次核 `fresh.payload == canonical_saved`、`canonical_saved == saved.payload`、`fresh.digest == saved.digest`，任一不等安全 internal；profile 保留步骤1的付费检查。正好两次 payload、一次 digest，未增加比较、扫描、排序、hash 或池操作，原 K_i 和求和不变。N1 关闭。

最终实际核验的 metadata：

| 对象                              |  字节 | SHA-256                                                            |
| --------------------------------- | ----: | ------------------------------------------------------------------ |
| proposal-revision-1-inputs.json   | 11625 | `822c01071d53514bafa9543529c1a02a78061030fba523ef9f088a807bf2946d` |
| proposal-revision-1-receipt.json  |  3182 | `41eb1f4170944d88165680d4ef841d366576287b2c85261cdb45ecac8813a761` |
| proposal-revision-1-manifest.json |  2521 | `60fc86590bf0a33171e1d600b7c416c6db9ab6b6b2c11440ab41ac3eaf598c92` |

最终 manifest 六项与实际文件长度/SHA 全部相同。`proposal-revision-1-before-N1-proposal.raw.md` 仍为原 d7df 字节，before-N1 的 inputs/receipt/manifest 三份 raw 仍分别等于上述首次审查的原哈希。原 c1a/初版与先前审查证据没有覆写。

本审查仅新增并完善本报告；未改提案、产品/测试/夹具、旧证据、公共/Store/worker/UI、依赖或其他 worktree，未暂存、提交、推送或切分支。
