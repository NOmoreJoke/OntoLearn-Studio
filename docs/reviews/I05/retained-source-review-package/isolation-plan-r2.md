# R2 隔离计划与真实状态

两普通 wrapper 已由总控实际创建并将唯一 setup 写权交给本备包作者：

- /Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-retained-review-zcode
- /Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-retained-review-minimax

登记原件为 iteration-control/2026-10-21-weekly-release/additional-review-roots-20261022.json；仅核本两根，创建不代表输入就绪。physical-copy-spec-r2.json 是精确复制白名单。先冻结 R2 candidate，再复制最终字节，setup receipt 绑定实际 candidate 与逐件 SHA/inode。当前实际任务数0；不启动应用/模型/GUI。是否 copy-ready 仅以实际 setup receipt 为准。

每根只收到本人一个当前 prompt、本人 contract、共同不可变数据；不复制主 readme/dispatch/isolation 中的 peer 路径，也不复制旧 R1 两个 prompt。共同历史 C1 双报告是必需固定输入。每根独立 reports/scratch/review-status/application-metadata，空目录基线据真实检查登记；应用生成 metadata 的增长尚未发生，只允许以后按当前任务精确确认路径，禁全局发现。

常规物理复制不使用跨根硬链接；归档以流式安全 materialize 校验所有相对路径、类型、manifest、后向根内 hardlink、完整 SHA/Git blob，移除执行位且各 namespace 分离；不盲 tar 解包，不执行产品。核完整根内 pathset/所有 inode：输入0444与目录0555、输出0700，输入/输出无共享 inode，两根无共享 inode，根外无符号链接。异常立即停，保真实首失败；不删除证据。

意外串读立即停止审查和继续读取，最小真实事件留本人报告，root 判独立性。本人 prompt 不泄露 peer 根路径，不允许 Git worktree inventory、兄弟目录或全局任务扫描。full access 只为逐任务设置，不能扩大 scope。静态源码完整审查可先做，原运行门、HOLD/native/审批限制继续保留。
