# T01 应用 CAS 内部评审记录

## 实际范围与候选

本轮基于本地 b9027b16d0fe031f50367eeb97f737d946aa62a8，在独占路径实现 [应用 CAS 合同](../../iterations/T01/application-cas-contract.md)。不修改 schema/DDL、依赖、worker/protocol、既有测试、CI 或 I06 保留六文件。AGENTS 保持未暂存；指定外审前不 push。

Job 旧 claim 演进补齐四处即时 DDL hook，新增16项 RuntimeError/KeyboardInterrupt/OSError/进程退出验证，实际 16 passed/218 deselected，独立同样16通过。StageA 原26探针措辞更正另保留原件，不将当时pytest通过误写成附加探针拒绝。

## 内部审查与意见

主内审 `/root/store_interface_audit` 对冻结源码新 CAS＋旧 Job 独立 273 passed，发现1项P2：prepare_application 的共享表 envelope 可误用于普通 create_job，成功接受后重开失败。修前全仓 630 TS / 2212 Python / 44 不适用 skip 退出0，因该意见仅保留为被替代候选证据。

修复：新增普通域计划严格类型/完整 canonical 形状、plan hash、含真实输入快照和 Diff hash 的准备 ref、确认 project/base/hash/ref/actor UUID/write 验证，分配 Job claim 前拒绝跨类型；原 Job 接受的重试/重开采用同验证。create_job 无 caller actor 参数，不把存储的 trusted-prepare actor 说成新增调用者认证。新增双向凭据互换反例，拒绝后整库不变、无 Job/claim、可重开。

修后本线新应用＋旧Job 275 passed。主内审独立双向2 passed/108 deselected、正常预览/接受/旧重试3 passed；额外真实探针确认原复现拒绝、Job2/3 正常提交/重试/重开，P2明确关闭。ruff/格式/diff通过。

第二位 `/root/recovery_design_review` 对确认、旧CAS重试、NULL-job、无关editor更新、三个hash/单次sequence、checkpoint真实链/恢复目标和未开放动作独立20项定点通过，未发现新阻断；另实际探针证实无claim raw NULL-job零写入拒绝和旧CAS精确重试不写入。未重复全仓/故障矩阵。

## 运行验证与边界

应用专项先105、再108通过；新增稳定throughSequence分页。84个实际应用/combined故障用例覆盖8个应用阶段和额外5个域阶段的四类故障，比较完整库或提交后真实重开证据；两读连接读取同generation后由唯一writer受理请求验证CAS冲突，不声称两writer。含 metadata、草稿NULL/墓碑/同内容generation、恢复完整确认/旧CAS、真实NULLjob、域失效、三个不同hash、精确重试、跨kind/project与旧marker收养拒绝、伪计划越权字段和不支持动作无影响。

最新完整全仓修后 `npm run check` 实际退出0：630 TS、2214 Python、44上述不适用skip；lint/格式/typecheck/构建/ruff均通过。完整运行64.33秒仅为本次实测时长，不作为性能承诺。无本机GUI、Electron/e2e/native/HMR、指定模型外审、打包运行或生产证据。独立 agent 是内部审查，不代替 ZCode GLM-5.3/最高及 MiniMax M3.1-Flash/xhigh。


## 原始证据与冻结

本轮六份原始日志及三份任务工具原字节选段封存于 `evidence/application-cas-raw-evidence.tar.gz`，SHA256 `1f35a12250819bb74b8eda325e753815e2fdad38337c51ff23d1425924fe0fe9`，145804字节。`application-cas-raw-evidence.json` 记录每成员大小/hash、源session捕获prefix及逐行offset/hash；全部成员重新读取逐字节核验。保留修前通过、WIP/误用探针、修后终态与独立16/273/20/2/3实际工具输出，不冒称收录所有debug或整个会话。无用户消息、session_meta或其他聊天原件。入库理由是总控要求原始可追溯内审/验证证据；没有CI artifact可代存。

源码hash由清单固定：storage `cfba3b3a…3395d`、applications `888bac46…8d90f`、format3 `20f01692…ee0b1`、job_store `b55e5d1a…25380`；新应用测试 `7031b239…136b3`、Job3测试 `cb2c5a98…39a04`。全仓检查后仅补本文/状态/跨owner设计答复与证据清单，未变产品/测试；文档另做Prettier/diff检查，不重复无变化全仓。

跨owner设计答复 owner-interface-responses-r1.md 全文SHA `0f3ab7e539b9b69c6a602f4eabd089936a37afd9d842fa836748793031df6768`；第二位独立设计复核未发现阻断/越权/提前承诺，只接受作为待协同设计，不批准接口实现。
