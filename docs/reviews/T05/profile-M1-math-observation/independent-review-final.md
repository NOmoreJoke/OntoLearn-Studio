# 最终证据独立审查

审查者：`/root/m1_observation_independent_review`。本报告由实施负责人按审查者最终回报归档；审查者未参与实现、未写文件、未运行产品，仅作静态和实际原件只读检查，不替代指定双模型审查。

**独立审查通过：本次受限组件窗口无剩余阻断项。原P2已关闭；不代表父M1完整验收完成。**

固定候选 `051ae4cb9b5e58560c8e45cdc56fd98522777b5c`：test 24239B/SHA `250a760bd1c0f2710a9585a67650c3d0b743f376c1ecdd308fdf0d3d8aaf6047`；fixture 490953B/SHA `9f198fcefa50ca30a87acfa3cef021360100a9dea3fb5ed829c5f62fc02b0d9f`。149项只读输入保持批准字节，受控151，相对5f实际delta142；未发现候选后产品/测试变化。

## 实际证据审查

1. 逐1331项核对固定输入/ID与独立golden，包括486域槽、648 numeric实例、38 Number、15 Calendar及其余family。完整Number/Calendar、raw/source/domain/language、main与独立probe对应、7/15/11 fullview、原L及C/R费用边界均核对通过；没有重新实现数学parser或运行产品。
2. 两项入口分层严格符合正式决定：error/28为production/ABSOLUTE_IRI_REQUIRED及完整诊断、公开DTO；error/31为material/MATERIAL_INVALID、production未进入。两者main零比较器调用、无结果，且明确`pureReasonExecutedByThisEntry=false`；原pure expected未改，不能据此宣称两个pure reason已执行验证。error/31独立operand探针另计，不冒充main。
3. 独立重聚合计数一致：3821操作中3329成功恢复、491 production拒绝、1 material拒绝；production/restore比较器调用7116/6658，到达操作3787/3329，main到达1297/839，material调用0。这些不能相加为唯一案例数。
4. 直接读取最终ZIP全部17976成员，逐项核byte/SHA/CRC，并核完整observation与索引对应。最终ZIP 120953467B/SHA `65d81a465c2551fee9dbdb6c6be42383efb326439c8bbc86a955d5362af707ef`。
5. 最终专项1332 passed；正常check exit0，前端1125 passed、Python6219 passed/44既有skip；sources核12通过。命令argv/cwd/exit及双流SHA一致，新测试没有skip/xfail。
6. 三版ZIP实际存在于声明绝对路径，尺寸/SHA均核同，既未tracked也未形成Git blob；最终ZIP成员为本次直接独立全量验证，另两版全成员验证依已有原命令日志核验。

索引：`final-full-actual-index.json` 12339129B/SHA `16163785117af8282e1d4f09ab055d8391a116dc2936d1f83f013f8f49133ac8`；`final-full-archive-members.json` 4013729B/SHA `08a03ed021c69480668e06c86b979f8255ebcf2885ba29be7d16efba2a688344`。

正式T01 Job、Store/worker/selected、directstep、query/SHACL、E5/repair及父级发布门仍未由此窗口验证；逻辑retention/live不证明物理释放、H租约或性能容量。
