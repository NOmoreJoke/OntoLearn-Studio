# T05 M1：真实数学观察与独立断言实施窗口

2026-10-22。继续原T05聊天，不重建原Goal、不改其状态。固定9333的M1合同与根16096B/e5a39b独审已全文核读；I05固定6c产品/2d5过程已完成内部生产capture/fullview收件，见 `I05-production-fullview-root-closure.md`。现在可先完成不依赖T01正式Job的真实数学观察，完整M1联验仍保留。

## 精确树、输入和写权

原T05 `.worktrees/T05-quality-reasoning` 及原f9af/16c/9333全部保护。由原T05负责人创建独立 `.worktrees/T05-profile-M1-math`、branch `feature/weekly-t05-profile-m1-math`，基于已核准develop5f910b52c69d86a1076b2032e5d3c63e715947f3；路径或branch已存在先核实际归属，不重置别人的树。

从 `T05-M1-math-observation-fixed-inputs.json` 的149条sourceTree/sourceRef精确Git字节采用并先固定adoption。清单61054B/SHA256 `fe4c08efea5dcfdc9262d67741255e83816c0fedda2a30c9d4106b8498e7a163`：139为I05获准6c完整产品/test（含130继承及九writer），10为T05固定9333数学合同/输入/独立golden/来源说明；不是wholecommit，也不采用T01 C2/dispatch/S1、I05未授carrier或其它WIP。149只读，不改I05九writer、T05七机制/16c、restore_budget、旧tests、公共协议、Store/worker、资源/锁/build/CI。

只准两项新路径：

- `tests/fixtures/quality/profile-M1-math-inputs.json`：从已核9333的math-operand-inputs.json复制独立纯输入，最初字节须相同，原1331 operands/ID不删改。expected分类/比较/值不放入此fixture。
- `packages/engine/tests/test_profile_M1_math_explanation.py`：真实I05 producer及strict fullview的数学观察与外部独立断言。可按真实API组织有界helpers，但不新增产品module/第二套计算器/Job假通道。

完整受控151=149只读+2新路径，实际base差异另据Git列出，不能混用计数。新过程仅 `docs/iterations/T05/profile-M1-math-observation.md` 与 `docs/reviews/T05/profile-M1-math-observation/`；最新AGENTS15852/78df和common17891/e437全文只读携带，目标AGENTS保base1056/1b3原字节，不把规则复制误当实现改变。先核绝对树、base/branch/status、责任和采用指纹，再回执实际启动。

## 真计算和独立expected的边界

只从纯输入fixture构造真实TermInput/RuleSpec/来源并调用获准 `execute_admitted_profile_job` / `restore_profile_result`。该API名不代表正式Job权限，本阶段无T01受理、Store或ownedworker。golden四文件只用于结果断言，不能参与RuleSpec、输入图、allocation、limits、producer payload或restorer输入构造；不运行原golden生成脚本，不从Number/Calendar实际值反过来生成expected。

覆盖M1合同对应的九域/六operator分类、六数值域混比648实例、38 IEEE边界与15 Calendar，保完整逐ID actual/expected/error观察及原1331操作数来源。实际计数按各独立集合分别报，不能累加为唯一案例数。用真实source、原L与实际producer/capture/restore保存物料，比较Number有理分子分母/负零/格式、Calendar全部分量/offset、None/空串/language_raw及完整值，不只看通过数量或digest。外层7/内15/child11保真可在本已支持schema实测；directstep不存在要准确列缺口，不能从leaf union/expected自行补写。

不改query/SHACL入口、date支持政策、directstep载体或实现版本，也不把rule comparator用于query/SHACL。consumer13格、supplemental graph与正式selected/跨worker/Store/E5/repair仍是后续窗口；本阶段不伪称完整M1。当前实际生产结果与独立golden不符即保存可复现反例，交root路由唯一owner，不调整golden、删输入、放宽断言或加skip/xfail取绿。原规则false后错误整批失败的语义保留，不以expected推断未执行的错误。

## 验证与交付

使用本树独立frozen依赖与日志/缓存，可安装现有锁的离线缓存，不升级依赖、不借原树可变环境。允许运行无窗口Python真实计算/pytest及AGENTS对应正常check/sources；不启动Electron/e2e/native/模型/凭据或占桌面。控制每批真实对象/子进程寿命，保实际原L/新C/R费用及retention含义，不把逻辑live0当物理释放。新测试无需制造假Job或自签origin来满足此阶段。

复杂交付由未参与实现的独立agent检查测试输入与golden物理分离、真实producer/restore路径、完整逐ID数学值与错误、费用和未覆盖边界。新两路径固定提交、完整151清单、所有首失败/双流/真实argv/cwd/exit、独立报告、实际原件归档和最终process映射后回交。若发现I05具体问题，本树149保持只读，返回准确source ref/path/反例给root；原I05负责修复，新候选验证/审查后再精确更新采用。

不push/PR/merge，不以本阶段替换指定GLM-5.3最高与M3.1-Flash xhigh同版双方新审、CI/远端、目标OS/真人或父57P0。此授权是实际新增fixture/test与真实组件验证，可直接执行，不只再写一轮方案；除真实越界或缺失输入外不重复询问用户。
