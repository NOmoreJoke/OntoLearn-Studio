# F1 实际实现独立静态复核

2026-10-23。审查起点550d47ad064f4d3899c844e8f791841498851ec5，对比当前owner工作树（含后补空参数及两schema合同例的125版测试）。结论：当前owned实现静态无新阻断问题；F1仍待新候选完整验证及指定门，不由本内审签Pass或关闭。

仅阅读Git/文件差异、设计及获准的新普通工程日志/元数据；未运行重复测试、Node CLI复现、native/GUI/DB，未读取旧越界native返回、当前模型runtime或报告。AGENTS为既有政策差异，不属于本修复，不应暂存。

## 实现判断

- 唯一实现原字节重命名verify.ts→verify.mts：旧Git与新实体SHA均为c3e670e66594af4a7ff4be3d0802f559117ded12d9dceab4a985f576ba930b9b。没有第二schema或兼容副本；当前.mts受release全局ignore影响，最终必须精确force stage并在新索引登记rename，不将工作树可读误作已入冻结提交。
- verify-release.mjs:2–12保留参数优先，major!=24、非整数minor或minor<3时固定UNSUPPORTED_NODE_RUNTIME/exit2。第14–26行才在try内动态导入真实.mts、读取/解析/核验；导入失败和读取/parse异常只输出固定码，未打印error/stack/path。输出一致性结果及synthetic exit1语义未变，releaseAuthorized仍false。
- .mts明确ESM后不再依赖根type探测；源码没有全局warning开关或拦截，独立emitWarning测试也不以末行/先后筛掉诊断。调用者额外注入的preload警告与无注入基线固定错误面区分清楚，不以披露警告代替修复。
- 两专项改为.mjs specifier；已存listFiles原件列出唯一scripts/release/verify.mts，无旧verify.ts；首轮专项实际122全pass与类型检查为解析可行性提供证据。此为核对owner原件，不是本审者亲跑。
- Git差异未见根package、锁、tsconfig、ESLint/CI或共享配置变化。README明确CLI仅>=24.3<25、模拟版本不代表旧Node实机；这是工程核验CLI约束，不改变最终产品无需Node或双OS矩阵。原036/历史报告及收据未改，过程异常和原门保留。

## 新测试与合同

当前tests/unit/t11-release.test.ts:1173–1336覆盖无/少/多/空参数、manifest/freeze缺失与无效JSON、各自16MiB超限、正常synthetic、未来时间、真实缺实现模块、四个不支持版本模拟和独立warning。无注入错误均整段stderr精确一行及LF、空stdout/exit2；正常synthetic和时间拒绝结果stderr空；模块缺失用只复制CLI的临时目录触发真实动态导入失败，不用stub。

后补两schema例正确保护原失败合同：manifest JSON可解析但schema非法仍stdout完整MANIFEST_SCHEMA结果/exit1/stderr空；freeze schema非法由parse抛出，固定stderr/exit2/空stdout。README第17行已从统称schema错误改为明确freeze schema错误，并单列manifest合同；未借F1修复改掉既有错误语义。

warning例以受控.mjs preload及pathToFileURL传入，只断言marker/message、固定错误码和exit2，不依赖警告顺序或PID；参数/版本/模块/输入失败均未被吞成成功。四版本例复制CLI却不带.mts，所以能区分“门前拒绝”和“错误进入加载”。精确24.3接受、坏参数加不支持版本的优先级目前由源码可静态判定，未在本复核中记作额外实测；不据此要求机械新增重复测试。

## 已读证据与未完成项

已读runtime/01-first-explicit-unit.json及raw/01-first-explicit-unit.log：122passed，2files，Vitest13.28s；metadata记录exit0、墙钟13.608s，两者口径不混写。02-typecheck-list-files、03-explicit-lint、04-explicit-format的metadata为exit0；listFiles内容确有唯一.mts，lint显式包含.mts且解除release ignore、日志空，format明确ignore-path /dev/null并通过。

以上原件只对应首轮122及当时文本，不能冒称后补125版最终全仓通过。01 metadata未显式保存flag环境，不能说它已经记录T11_FIXED_BASELINE_PROBE=1；owner报告显式启用及122全pass与无skip相符，新fullcheck/verification应记录该环境和真实新计数、失败/重跑原件。后继125完整检查尚由owner执行，本内审未重跑或预填结果。

当前CLI SHA256：c83e455f63032ac81d2a6c2e4f7b420528d0f72007a603da468acc2f17df0e4e；本次读取125版专项源码SHA256：fb69c5b01d4cd0c98ff19ed4591ef756a59e612e7e5b407fe871a35f678b2c5e。这只是工作树观察身份，不替代提交后冻结SHA和最终索引。

后继需精确提交rename及owned变更、核新候选字节和实际验证，再按原要求进行全新完整指定审查。旧18项、新F1、M NotPass和越界过程处置均不由本报告关闭；不批准push/CI/合并/发布或任何新资源。

## 最终 fullcheck 原件核对

同日仅只读 runtime/06-first-full-check.json、raw/06-first-full-check.log，及05-final-explicit-lint的metadata/raw，未运行任何新命令或测试。06明确记录Node v24.15.0、T11_FIXED_BASELINE_PROBE=1、本方cwd/TMPDIR、自然退出0；六个受验路径before/after hash相同，并逐项核对当前实体仍匹配。fullcheck原始日志SHA256为edc8d5af5df40beb584cc1d693e1d515017b57d4c8b4e4956cb3daa55cce9d9a。

raw实际记录17个TS文件全部通过、755 passed且无skip；构建及ruff/ruff format通过；pytest1052 passed，53.90s。metadata总墙钟80.922623708s与各阶段计时分开，不作性能结论。末版125专项用例包含于该755全仓运行，没有另跑一轮125专项；01的122仍只作首轮结果，不冒称末版独立专项通过。

05显式lint在后补三例后exit0且日志空，明确覆盖.mts、CLI及两测试，六路径前后hash保持。04显式格式结果是三例增加前的历史检查，不能冒称其已覆盖后补文本；06的全仓format已实际通过且覆盖更新后的tests。README的后继手动Prettier unchanged由owner另述，本核对不将其伪装成04原件或声称全仓默认格式检查涵盖被ignore的release路径。

本次解决此前“后补125完整检查尚待”的证据状态；确认的是owner实际运行原件与受验字节的一致性，不是本审者亲跑或指定模型Pass。唯一.mts/CLI字节与本轮静态审查观察一致。新冻结提交、完整指定门、旧18项/F1最终关闭及过程异常处置继续保留，未获发布授权。
