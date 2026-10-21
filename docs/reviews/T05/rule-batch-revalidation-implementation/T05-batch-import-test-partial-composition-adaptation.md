# T05新纯模块树：一条采用测试的精确适配

2026-10-21，补充5884B纯实施授权；只允许适配 `packages/engine/tests/test_quality_profile_imports.py` 的第一个fresh-process测试，不增加任何产品/依赖路径。

根已全文读原测试、548B package root及实际 `adopted-import-baseline.stdout.txt/exit.txt`：新5f+21采用集、尚无新API时，真实1failed/1passed、exit1。首测试要求导入未获准采用的definitions/planning并核lazy identity，与本阶段明示缺失模块不可调用矛盾。原fixture manifest测试通过。原dbb测试与既有完整T05树原件不改，首失败和21采用时hash/原文在新review目录保留；不覆盖原失败。

在新partial树，仅将首测试改为精确验证当前获准组合：保fresh子进程、真正quality/rule_firing导入、rdflib/rdf_terms未导入、logging/int-max/decimal全局政策不变、原完整__all__声明及unknown AttributeError；把未批准旧模块的成功导入/identity段替换为**无分支/无skip的明确缺失断言**。以真实import定位核definitions/planning均不存在，实际调用这四个旧lazy名字须ImportError安全失败且不缓存成可调用对象，不能注入替身或把别的异常当通过。按新语义同步首测试名称/固定stdout。第二个fixture manifest测试及其完整五项hash断言原样保留。

不允许复制definitions/planning/rdf_terms、改548B root/七模块/loader/依赖、conditional skip/xfail或遇模块存在就跳过。若实际异常不是预期ImportError，保原件给确切行为，不借此改产品。完整旧T05 lazy identity兼容性仍留原完整候选验收，不能用partial缺失测试声称其通过；后续真正引入旧模块需恢复/另核完整identity验收。

正常check与独审覆盖这一个适配；最终范围诚实列20精确采用+1采用测试适配+3新路径，原21清单作为历史输入来源保持不改。交付将此测试新旧bytes/hash/diff和本补充授权单列。其他20采用项与旧两个树保持，API/预算、正式消费/恢复/selected/父功能及双审/CI/合并门不变，不重测无变化旧树。
