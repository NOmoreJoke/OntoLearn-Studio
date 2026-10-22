# I05 pin-refresh-r1 最小身份消费独审

结论：Limited Pass，未发现新增P1/P2。此次消费绑定真实存在的source/process commits；22个canonical当前源字节与固定supplier及声明pins一致。probe变化严格限于2个refs、1条semantic pin和删除过期docstring句，未松动guard或改写原验收预期。本审查没有运行产品、Ruff或formatter。

## 固定身份实证

- SOURCE_REF：`23352bacb500088367f849e53980e97c937724b3`，Git对象类型实际为commit；该提交恰有5个产品路径：engine pyproject.toml、uv.lock、build-engine.mjs、semantic.py、probe test。
- PROCESS_REF：`513db0056f312342a6791e2d4c7842f3726581f2`，实际为commit且其直接父提交正是上述source。该提交恰有95个文档路径，严格等于94个manifest payload与manifest自身；没有借旧refs命名新源码。
- 固定process的source-freeze-manifest.json为21044B，SHA-256 `0f8b5548bb3788fddea51dd6d9cf01a32b436c4678d435822fbeff296e65f3d2`。独立核验其sourceSupplierCommit匹配23352、payloadCount=94，并逐件比较94成员 current bytes = fixed process Git blob = manifest长度/hash。manifest本身current=fixed，故95成员身份链成立。

上述成员检查是字节/hash完整性检查，没有重新审读95份文档全部内容。对manifest中gzip只核压缩文件本身字节身份，没有新增解压/round-trip验证或重构旧原始流。

## 22源与最小消费改动

当前probe102607B，SHA-256 `a6b6b133a188e1124e81e74a3d63cc3c6daf4e52aec69c0510d6a8f897a72ef3`，与pin-refresh.json声明吻合。对22个SUPPLIER_PINS成员逐一读取当前及固定23352 Git blob的字节，不读算法；全部满足current=fixed且长度/hash符合声明。pin-refresh.json的22行也逐项匹配独立计算结果。

相对固定23352原probe（102669B/`05f4ac85f883f40142782e9ee3943b8df9593ddf5a35e318ca35bbd6781a6dd4`），只有：

- SOURCE_REF和PROCESS_REF改为上述真实提交。
- semantic pin由65749B/`60008130fe0db368ea87948c2c8f079b1161f2aa951693b69635558ed1f56a07`改为66258B/`d6c5f5c38aec310de726f73568e1086bf4de95117cbdf664ae1384fcd6808392`，对应已独审v2实际源；另外21行完全相同。
- 删除过期句“This source-only candidate has not been executed or packaged.”；该删除不构成已完成packaged执行的声明，剩余future frozen方向不由此关闭。

精确恢复SOURCE_REF、PROCESS_REF、SUPPLIER_PINS三赋值并恢复该docstring句后，整个probe AST与固定23352完全相同。另独立比较pins新旧22行，确认只有semantic一行变化，避免整tuple归一化掩盖其他pin变化。

因此原八依赖版本声明、两JSON声明pins、417预期与selector、guard、identity校验、错误和采集流程均保持。该结论限源码AST和固定源字节；本轮没有重新执行依赖导入、读取两JSON资产实体或运行preflight，也没有重新审计供应商三路径的实现。

## 验证边界

本轮仅Git只读、文件/hash、stdlib AST/JSON检查；无产品、pytest、Ruff、formatter或GUI调用。实际CLI/frozen、S1物理测量、source/package parity与整体目标不在本轮关闭范围。

身份消费静态检查通过后，后续正常完整check及必要既有pytest仍由主agent按授权执行。所有历史诊断失败、red/green、格式失败和独审产物保持原样；此处只新增pin-refresh-r1后缀文件。
