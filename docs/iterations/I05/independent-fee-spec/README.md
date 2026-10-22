# 独立收费规范 R2 候选入口

本版回应 R1 的 F1–F3：完整114项新提案收费程序、2282-prefix baseline、独立手算/字节复核、control与累计cleanup/BLOCK修复。**现行invoice/真实issuer/usage仍pending**；新提案金额不证明产品已遵守。

先读[完整R2规范](specification-r2.md)，再读[逐ID表](per-id-r2.md)、[完整手算与首拒](hand-examples-r2.md)、[具体实施delta](handoff-r2.md)。机器入口是[完整114程序配方/分池金额](charge-reference-v2/all114-fee-programs-r2.json)与[114分栏表](per-id-r2.json)；[baseline全prefix](charge-reference-v2/baseline-prefix-r2.json)及合成输入原字节支持完整示范。reference.py只用stdlib做独立数学/编码/收费，不导入产品或导出业务expected。

原specification.md/operation-schedule.md/per-id.json/md/hand-examples.md及artifact-manifest.json是**R1原候选/历史**，保留其不完整与Fail，不能当R2当前金额。R1独立报告/命令/proof、旧作者not-independent原件、首失败与两个窄授权原字节均在review前缀；不得读/复用旧作者草稿。R2清单另用artifact-manifest-r2.json，明确self-exclusion和历史保全范围。

本候选未运行产品、pytest/npm、网络/GUI/DB、真实预算或平台门，也未修改T05受审候选。数学/静态/formatter验证与真实运行/发行证据分开；详细实际命令与exit见review中的R2命令记录。真实审查由root另派fresh reviewer。
