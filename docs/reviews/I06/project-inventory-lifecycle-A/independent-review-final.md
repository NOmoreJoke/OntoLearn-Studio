# I06 A 独立实现审查最终回执

2026-10-21，审查者 `/root/i06_design_review`。**通过本轮 A 纯机制实现的独立审查：四项 P2 已关闭，未发现新增阻断。**此结论不替代指定模型同候选双方审查，也不授予生产 IO、宿主接线或发布许可。

## 实际范围与输入

工作树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-project-inventory-lifecycle`，分支 `feature/I06-project-inventory-lifecycle`，实际起点/HEAD `5f910b52c69d86a1076b2032e5d3c63e715947f3`。先全文读实际授权7045B/20c9c0c6006746a54e286d391e49fac728810889a8165e13838d82667779708f、根独审12219B/556c6b838cf8e0c6a209a5a3633286128a1687bb208d25ce91191e56bd56647e、共同指南17891B/e437121a08053544c2a09151ac5183baf15b5fa67a3a604891aaa9e77ba971b0和新树AGENTS15852B/78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759。

已沿首审全文读取两模块及两测试，对各次实质差异、最终修正和新增反例逐段回读，并全文读最终A说明7045B/SHA256 `0f840cc162d3f64d84069eea2c17953803f350a4899cb803a8863e18afffedfd`。

最终实际四文件身份：

| 文件 | 字节 | SHA256 |
| --- | ---: | --- |
| apps/desktop/src/main/security/private-resource-inventory.ts | 23598 | 0f6a2125d5dea53b5e5badde99401086284d4fd776b0cefadad324e408c786e5 |
| apps/desktop/src/main/security/project-cohort-lifecycle.ts | 23585 | bcbb73449395757b0cb6260b1299366e1a25de5bcc16c161f145a1f7674fcdb9 |
| tests/unit/i06-private-resource-inventory.test.ts | 22330 | 7d82c1012bbe7fc35c5faf6eaf167b82d93a357e0b1060db6256ba809a118f49 |
| tests/unit/i06-project-cohort-lifecycle.test.ts | 25548 | f90dd23b6f30e4e641197db6cb93a0fae4786948e489d4985b38f37ec0bf2fea |

## 四项问题关闭依据

1. **导出owner集合可变：关闭。** `inventoryOwnerRoles`已运行时Object.freeze，内部有限必需owner集合不再能被splice删成两项。新增反例实际尝试改导出集合，随后仅登记profile/private-root仍不能complete或签快照。
2. **重新观察使释放完成写丢：关闭。** merge保留稳定RecordState及birth owner，只替换不可变resource；等待中的release闭包仍落原记录，不把旧完成归到新owner实例。新增track→整轮retired观察→resolve反例核released-retained；旧profile迟到完成隔离用例保留。
3. **旧Promise可冒充另一DB释放：关闭。** 工厂私有WeakSet在成功登记后记录原Promise终生单次归属，不在settle/profile/close时移除。并发、已fulfilled跨资源和跨profile新owner复用均有直接拒绝反例；批量IDs仍可在原一次登记中使用。实际未settled槽不因超时或逻辑取消提前释放。
4. **已结束寿命仍可发布/继续接纳：关闭。** child/store-connection聚合寿命在candidate或active终态时，使该组quiesce、失效候选transition并禁止同组新操作；已draining时正常close仍按实际完成进入release。新增candidate/active × child/store-connection四反例覆盖正常完成，原逻辑亦对拒绝终态执行相同quiesce分支。

最终代码注释与A说明明确：这里的寿命严格是整个cohort对engine/Store的永久拥有关系，由未来B/T01用永久stopAndDrain聚合全部实际子进程/连接终态；不是可重启transport session或普通RPC Promise。普通noteViewRecovery/同Supervisor短session瞬断仍按原T01恢复政策，不由本模块清grant或强制整组重建。A不认证session-ready；未来供方不得把短session Promise冒充永久聚合寿命。这个定义足以消除本轮纯机制接口的歧义，真实供方是否兑现仍待后续接线证明。

## 实际验证与原件口径

本审查者运行两次有界内存探针，均为新树自身TypeScript工具链转译纯模块并data-URL import，argv为 `node --input-type=module`，cwd为上述新树，均exit0；完整脚本、工具合并输出、时长/退出及stdout/stderr未分离限制已分别保全：

- raw/independent-inventory-first.txt：6061B/SHA256 `b3f68869d6ccde028f4759729d1076bc04a47e4c14f46b99e9ac924eecfda1d2`。
- raw/independent-second.txt：7683B/SHA256 `43fd9e23844ecc91d7a43ba6e2ad6454348d49b23b754b910be66a4fb0580fa1`。

已实际读回owner保存的定向receipt及stdout：首两反例2fail/32pass，Promise复用2fail/34pass，寿命终态4fail/30pass后34pass，组合70pass/0skip/exit0。没有由本审重复运行已有专项或完整check。首两反例红测的source快照实际是23162B/18439a02ee2db51bcb8b21bc14f674cefbed1d49e7f870c0450c3845dd98c27e（已含另一项clock异常补正），不能误称为最初独立审读23089B/c885a2e4…的精确源码；before-promise1018与cohort-before-a9bf快照已独立实算匹配。初始失败和中间检查结果均保留，不挪贴成最终候选结果。

本回执形成时，root最终full-check-final仍在运行，本审没有读到其终态，因而不声称最终完整check通过；sources-final12项通过是owner当前报告，另由owner封存最终命令/退出/输入绑定。这里的明确通过是独立实现审查结论，不代替尚在运行的工程验证。

## 未验边界

实际owner来源、完整真实FS inventory、持久retired恢复、原生句柄/跨进程fence、SQLite/VFS/ABI/锁、T01 Store/worker/宿主、公开桥/UI、两目标OS、真实凭据和父I06/FR-002均未由A实现或本审验证。所有结果仍mechanismOnly且productionAdmission unsupported，不能把合成metadata complete、opaque票据或Promise品牌兑换为生产能力。

本审没有运行GUI/native/e2e/HMR/Keychain/模型/付费/服务，没有读用户内容或凭据，没有修改四产品/测试、共享文件、配置、依赖、Goal或AGENTS；仅写root逐次明确授权的三个独立报告/探针证据文件，无commit/push。
