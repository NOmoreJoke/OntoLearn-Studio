# I06 B 真实资源供方方案：独立定点复核

2026-10-21，审查者 `/root/i06_design_review`。**修订方案静态审查通过：首审两项P2及owner表述小项均已关闭，未发现本次差异引入的新阻断。**这是docs设计合同结论，不授权B-M/B-R/B-L实施，也不替指定模型双方同候选审查或真实供方/平台验证。

## 实际输入与检查

工作树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-project-inventory-lifecycle`。实际逐行比较保留首稿与当前稿的完整unified diff，再定点读取§4.2、§5、§7及§9相关上下文。仅Git/文件读取、stdlib JSON/hash与文档差异；未import/执行产品、测试、build/install、真实metadata/FS运行、网络、GUI/native/Keychain/模型，不改Goal或产品。唯一写入为本新报告。

- 当前主方案44238B，SHA256 `b71667de836ee2bcf8f62107f170e808200a3b4f77c264ed06d7c21e9ceed605`。
- 保留首稿plan-before-independent-review.md实核41058B，SHA256 `d6bf752aa945711867c8362fa9e332474b03cf81e3922486c81a125bc9fd2d10`。
- 首审原文independent-review-r1.md实核7405B，SHA256 `1acdbd9d80b906aced55f35dae19a33b0f96d17e3c2b1d2f27e6cfd81001f25a`，原字节未变。
- review-input-followup.json实核360B，SHA256 `47d119aae006cbe9389b249376507dd7b435403a28e0b7d21df03ac453507f0b`，其当前方案bytes/hash断言匹配。
- 原inputs.json及source-metadata/source-lifecycle三件均重新实算，与首审绑定的bytes/hash完全相同。首审已实际核52项来源，本次未重复读取全部不变源码或重跑A/旧网关/平台。

## 逐项关闭

**P2-1 同址历史/当前身份无法映射A：关闭。**§4.2第8项（91行）及§7第4项（143行）准确指出locationKey唯一与完整观察不能省历史的组合限制，不再声称新incarnation id足以解决。冻结A上的B-M明确unknown、保留旧新身份/保护且不宣称观察完成。最小后续申请仅列inventory模块与其专属测试，限定同位置一个present当前项与有界absent-retired历史共存，保原id/identity、历史不可复活、计数及links闭合，拒两个present冲突；没有在本轮修改6a38或隐含采用扩展。§9（173行）增加实际临时文件替换、未知/历史保留/零生产准入与未来扩展正反例，足以关闭本轮可实施性表述缺口。

**P2-2 控制metadata自举/自身追加递归：关闭。**§5（101–109行）冻结了唯一固定控制树bootstrap/self-append例外。实际受信fresh来源仍须根/T01另冻结；先内存reserve已存在父对象及固定控制集合，再独占建立目录与immutable header，完整写入/同步/关闭/身份核验后才可追加。partial、冲突、close/sync/identity失败或来源不明均unknown，不放目标操作、不假fresh。已建立控制树内只有固定schema/序号/exclusive-create的intent/seal自身追加直接计槽/自保护，不递归生成上一层intent；不是任意文件、目录写权或通用callback。所有其他目标仍须完整可恢复intent+seal及所需耐久确认后执行。§9补bootstrap各步失败、自身不递归、bootstrap/未seal时外部目标IO为0，未把未来测试写成已通过。

**owner表述小项：关闭。**19行改为“不合成任何缺席owner”，与各实际供方子集及全局incomplete/unsupported边界一致，不引导填空角色凑complete。

## 通过范围与剩余前置

主方案的B-M/B-R/B-L是统一候选子阶段，源报告的子阶段名称不自动并集为写权。固定A、e2c、961产品/测试及原证据仍冻结。B-L选择本地真实唯一registry的启动前准入，A reservation只为后续独立申请；synthetic complete/publish、opaque对象和native Promise品牌不认证真实资源来源或OS释放。

B-M同址复用目前仍是已知功能限制；B-R真实fresh/bootstrap来源、稳定安装级位置、writer仲裁和发布耐久尚未交付，不能据本复核自签恢复完整。T01 canonical/dispatch/实际request与永久child/Store寿命、native跨进程fence/同build VFS/两目标OS、生产首IO与宿主/UI消费仍需精确授权和真实证据。本轮未将这些前置当实现完成，也不解除productionAdmission unsupported、父I06/FR或指定双审/CI/正常合并/远端/真人门。

本次仅定点静态复核修正文档；无产品或测试运行结论，无commit/push。首审原文与首稿保持原字节。
