# 私有 provenance 四路径实施候选

四路径实现已完成，当前定向验证为96 passed；实际整合源、真实构建、frozen runtime和source/package语义对照尚未执行。完整独立实现审查进行中，本记录不授予root approval。

授权产品路径仅 scripts/build-engine.mjs、packages/engine/entrypoint.py、新semantic_build_provenance.py及新test_semantic_build_provenance.py。依赖/锁和I05 probe未改，AGENTS15147B覆盖保持unstaged。模块agent原提交5d033df在本树cherry-pick为56c234e2；其86项单元与本主控补充10项合计96项pytest，其中一项内含10项Node子测试。

Node builder为每次构建分配独占UUID目录，先生成只读provenance/contract/anchor，经固定PyInstaller argv收集八distribution及metadata/data，审计真实输出再产生外部绑定。发布复制至桌面固定stage，归档旧stage并在rename失败时恢复；每次immutable artifact/binding保留。Python入口语义分支保留原flag/selector并传递返回退出码；旧五种分派保持。模块只提供programmatic API，无新增任意路径CLI。

运行时reader不导入目标模块。I05先preflight，再安装observer，再显式导入22supplier与wcwidth._wcwidth_c，最后调用loaded/native verifier。opaque evidence不可直接放JSON，两个verifier返回独立JSON-safe值；精确字段见module-implementation-agent/implementation-and-consumer-api.md。模块loader/code资源绑定、source/native字节、semantic parity和root approval是不同证据域，后两项保持unknown。

## 已执行与修正

- 最终目标pytest：96 passed in1.73s（18轮）；Ruff check、format --check、Node语法、ESLint、Prettier及diff --check通过。没有真实全仓prepare/PyInstaller、native导入、full-v1/B1、GUI或全量engine pytest。
- 首次builder审查F1：独立publish helper接收非规范绝对root时祖先循环不能结束，现先要求string且root==resolve(root)。首次04回归测试缺少实际祖先目录，旧版本亦可提前拒绝而通过；05补齐真实engine祖先后10项通过。原报告、04/05双流均保留，未声称实际运行旧源码观察timeout。
- 临时04/05测试源码后来被格式化/移植；现在从本聊天自己原始工具输出恢复04 exact8330B/4077d437，再仅加mkdir得到05 exact8372B/92f4ea。副本明确标recovered、新建时间，不冒充原始备份。当前正式嵌入测试保留真实祖先与2s child timeout。
- 新永久测试首次style失败保留。12轮10 failed/86 passed来自嵌入JS子进程URL与runpy改写argv0的测试夹具误判；修正目标模块URI、按runpy实际脚本绝对argv0断言，17轮95 passed/1 failed只因Node默认reporter为spec而测试期待TAP。显式--test-reporter=tap后18轮96通过；没有改产品预期或放宽状态/flag/selector/退出码。
- 主控证据receipt首次选择命令时误按字符串cwd/command读取，得到0条；保留first-incomplete原件，再按实际URI cwd和argv list读取本聊天11条受限执行记录。未改写首次失败或回填不存在的执行时间。

## 待后续整合

最终I05完整修复源及消费probe必须由root正式交接，再整合四产品并冻结source commit。当前历史2cf、单supplier23352或本实施候选不能代替最终整合源。root须在实际完整artifact和外部binding固定后，给定expected SHA并授权独立运行窗口；已有外部executor先验证完整目录再spawn，保留实际argv/exit/双流。reader不能自授root approval；本阶段不执行这些受限步骤。
