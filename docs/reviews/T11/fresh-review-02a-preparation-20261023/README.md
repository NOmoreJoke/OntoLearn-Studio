# T11 02a 两份完整指定审查输入准备

受审候选固定02a4738a220b2c6e881f7161ee658c61bf4328dc；原handoff-index仍在../f1-candidate-handoff-20261023/index.json，583B、SHA bbedf633614cff2f47f3fb8b96995cd31b48d5f07ddeab9b173b235cd4554b2e。本文是后续已授权的两输入准备，不重包或改动该交付。

两个全新detached根为T11-zcode-review-02a4738a与T11-minimax-review-02a4738a，各自956受控文件实测仅最新AGENTS政策差异（15147B/de15f6ce…）；107 requiredFiles逐一字节/hash均等02a。两root有独立node_modules/.venv目录与own runtime，npm offline ignore-scripts与UV_OFFLINE frozen均exit0，未重跑测试或产品。

common-review-scope.md正文完全相同；full-prompt仅角色封面有差异。角色分别目标GLM-5.3/最高/max/yolo及M3.1-Flash/xhigh/bypassPermissions，均是目标设置，尚无实际任务/模型/effort/权限收据。真实派发必须完整附件实际摄入及自身设置读回，不能把准备SHA或目标设置当实际执行证据。short-request.txt明确准备状态是冻结时快照，实际派发后执行全文，不要求人类再次批准继续。

本轮peer当前材料严格隔离：两root的input仅自己的full-prompt、共同正文、manifest与candidate-binding；不复制peer当前prompt/状态或owner review-roots。scope保留原完整工程/四历史报告/原18+M036-F1共19、其他观察、全部owner/root读面偏差及两禁令输入；这些显式旧材料可读，不等于当前peer可读。Git只已给精确SHA+相关路径；禁止--all/分支/worktree枚举来探查其他线。新增F1错误面/运行时门/真实失败及不吞警告回归不替代原领域标准与发布门。

source-snapshots.tar.gz保存两份956记录的原始source-setup JSON，逐成员hash在source-snapshots-index.json；大源身份清单压缩入库，两个root自己的metadata原件保留，不向任一root复制含两方的归档。owner目录下两个未跟踪*-source-setup.json是可恢复本地重复副本，不属于固定载荷；index明确排除。两份setup.json和四setup.log为operator原件，保原字节，排除格式化；源快照归档也是原字节，不冒充系统原生日志。

当前阶段prepared_inputs_frozen_not_dispatched：taskCreated=false/sessionId=null/actualSettingsReadBack=false/report不存在。GUI仍归T09，T11未CUA、未创建应用任务或发送提示。实际创建须根具体GUI窗口，随后读回精确自己SID/原turn；从允许输入定界与公开状态接收，不广读role/header/system/thinking/global日志，不补读旧被禁返回。旧036两审树、02a实现、原M NotPass、19最终关闭及过程例外均不由准备动作改变，无push/PR。
