# Profile IRI 最小边界修复

修复 `iri_minimum` 将合法 Unicode 空白字符误判为非法 IRI 的问题。实现固定在 `dbb6b36e9259aa79a1fd908b5cfede3064f0c074`，基线为私有机制提交 `1e3e0ee1d9d5b70f1f59233d0a3c64f6d85fd2cb`。本文件只记录该候选，跨线采用须由总控另行批准确切字节。

## 依据与改动

[RFC 3987 §2.2](https://www.rfc-editor.org/rfc/rfc3987.html#section-2.2) 的 `ucschar` 范围包含 U+00A0 及本次列举的 Unicode 空白字符，可出现在路径、查询和片段中。[RDF 1.1 Concepts §3.2](https://www.w3.org/TR/rdf11-concepts/#section-IRIs) 允许绝对 IRI 含片段，IRI 相等按字符串身份判断，不在比较时继续归一化。作者本次已直接读取两份规范原文；最初工具连接失败及后续成功核对分别记录于证据目录。

只将原有 `c.isspace()` 拒绝条件收窄为 `ord(c) < 0xA0 and c.isspace()`。原先拒绝的 ASCII 空白、U+0085 与 `< > " { } | ^`、反引号和反斜杠继续拒绝；其余既有最低检查不扩展成完整语法解析。UTF-8 大小、工作/输入预算、精确类型、位置、签发身份及固定错误逻辑沿用原实现。不改写、转义或归一化输入，不触发网络和 DNS。

产品差异仅两个路径：`packages/engine/src/ontolearn_engine/quality/rule_terms.py` 的 `iri_minimum` 和新增 `packages/engine/tests/test_quality_profile_iri_boundary.py`。其余六个模块、旧测试和 fixture 均保持基线字节；旧 20 路径中仅 `rule_terms.py` 改变。七模块前后哈希、两路径补丁及实际源文件归档见 [候选清单](../../reviews/T05/profile-iri-fix/candidate-input-manifest.json)。

## 验证证据

- 先用未修改的 `1e3e0ee` 模块执行新增测试：实际 exit 1，74 failed / 57 passed；原始输入、测试字节、完整输出和退出码已保存。
- 最小修复后新增测试：实际 exit 0，131 passed。随后测试只调整 import 空行以通过 ruff，语义未变；两次实现提交与第一次 lint 失败完整保留。
- 固定最终实现的新增测试及原七组机制回归：实际 exit 0，1,539 passed。
- 正常 `npm run check`、`npm run verify:sources`、同版独立审查的实际结果及命令退出码记录于 [最终收据](../../reviews/T05/profile-iri-fix/final-receipt.json)。收据未生成前，不据此文预报结果。

新增用例覆盖所有 Python 3.12 空白中落入本次 RFC `ucschar` 范围的 18 个码点在路径/查询/片段的公开 `parse_value` / `term_key`；中文、合法补充平面字符、空/非空片段；NFC/组合形式、scheme/host 大小写、百分号形式和不同片段的身份差异；原禁字符、相对项、错误 scheme、代理码点；预算、UTF-8 字节上限、精确类型与安全错误。编译和实际给定 binding 求值同时验证 catalog、常量、绑定、比较、输出三元组的原文字节身份；没有使用测试替身替代这些入口。

## 边界与采用

profile 仍为 `OntoLearn-rule-comparison-profile/1`，budget 仍为 `mechanism-budget/1`；实现身份与哈希已更新。完整 IRI 解析和图匹配仍由 I05 承担；本次通过的是私有给定 binding 机制。I05 的新 `rule_terms.py` 字节采用、D2 源包组合验证、T01 producer/保存/GC 前置仍按各自门禁执行。

原 `T05-quality-reasoning` 冻结实现、oracle、batch 提案与 IRI 新树分离；batch 修订只在旧树开展文档工作。没有实现 batch API，没有推送、PR、合并、GUI/native 打包或原 blocked Goal 的状态操作。原 T05 完成度仍以对应状态源和总控验收为准。
