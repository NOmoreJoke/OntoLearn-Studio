# future70组合依赖补充：另列两份测试绑定文档

2026-10-21。仅补充组合依赖，固定原方案提交 `851e6241233d8b7a8f944944207260436b524e9f`；不改该提交的22件文档、主方案、预算合同、测试或产品。本补充不授施工，根对R/witness/exec的独立审查继续。

静态全文读取固定0475的 `packages/engine/tests/test_semantic_profile_imports.py`：第18–19行实际读取 `I05-profile-P1-fixed-inputs.json.raw`，第20–22行实际读取同目录 `T05-profile-iri-approved-seven-inputs.json.raw`。两文件在5f均不存在，原future70清单没有列入它们。继承该测试时只继承70项会缺这两份绑定输入；不能把“未来docs另批”当作已覆盖，也不能改测试或跳过其读取。

未来精确组合申请修正为：**原70项完全保留 + 下列2份支持文档 = 72项**。不是72项产品代码；这2项仅为既有测试读取的原字节绑定输入。未来新施工证据docs若另获批准，仍须单独计入最终完整diff，不能宣称72已覆盖所有未来证据。新manifest保留原70项列表与来源，另列两项支持docs；原future-adoption-scope.json不改写。

| future相对路径 | 固定来源ref | bytes | SHA256 |
| --- | --- | ---: | --- |
| `docs/reviews/I05/profile-integration/I05-profile-P1-fixed-inputs.json.raw` | `0475d0ec6c486a63c7e8f62f11f35181da6b2576` | 13431 | `b90106230f1d3e0f251a3daa1693260fea30555d02d4d6dbc85ceda71f11f40b` |
| `docs/reviews/I05/profile-integration/T05-profile-iri-approved-seven-inputs.json.raw` | `0475d0ec6c486a63c7e8f62f11f35181da6b2576` | 2435 | `a90d1ebbd7856f3f95668fc9eec9f5eac484798cd710190132b8439f45a65672` |

这两份JSON是历史测试绑定的固定输入，保留原字段和历史ref，不将它们内部记录的历史semantic字节误认成应回退的当前产品。实际未来采用仍按原70清单的0475/16c来源。仅在root另授独立树施工后逐path原字节继承这两件；不复制整个review目录，不创建新的支持文档格式，不修改原测试或增加测试豁免。

本轮仅新增本补充与 `combination-dependency-manifest.json`；原851e的22件和产品固定118件逐字核对不变，AGENTS原dirty字节保护且不提交。manifest固定原70清单的ref/bytes/SHA、完整72项组合、两项Git blob、调用处以及本补充hash；manifest自身由追加的本地docs process提交固定，避免自引用。

验证仅为Git/文件/JSON/hash静态读回：两文件当前字节等0475，5f不存在，原70无重复、加入后恰72；没有import产品、运行原测试、重做预算、安装/build/package或创建代码树。T01/selected/正式消费及父出口边界均沿原方案，不由本补充关闭。
