# T05 独立内审与处理

独立 reviewer：`/root/t05_internal_review`。只读本功能路径与对应 PRD，未改文件、未开 GUI、不接触凭据/外发。首轮明确不通过，原意见保留；不替代指定外审。

| 严重度 | 原问题及实际反例 | 开发处理 | 复核状态 |
| --- | --- | --- | --- |
| P1 | 非法 xsd:integer literal 返回受限错误但 RDFLib 日志包含原值、堆栈/路径 | `quality/rdf_terms.py` 用 ContextVar 限定解析中的 RDFLib term 诊断过滤，不关闭其他线程/普通日志；新增 caplog/capsys 零输出及退出后日志仍工作的测试 | 原反例已由同一独立 reviewer 重现关闭 |
| P2 | 隐藏 maxCount 参数为空，切到 rule 仍阻断生成 | 抽取纯表单序列化 `draft.ts`，仅约束分支处理模板；增加切换反例断言 | 原反例已由同一独立 reviewer 重现关闭 |
| P2 | id 为孤立 surrogate，计划 UTF-8 哈希抛原始异常 | 所有本地 text 入口统一拒绝 surrogate，返回 INVALID_TEXT；覆盖 id/label 回归 | 原反例已由同一独立 reviewer 重现关闭 |

首轮 reviewer 实跑 Python 42、Vitest 3 通过，仍发现上述缺口，证明已有测试不等于需求覆盖。首次定向 ruff 有 4 处长行格式错误，经格式化修复；未执行者不记通过。

基线缺口：真实执行器、Store/IPC、失效重算、G.2 完整真实结果和桌面项目切换均未验；不关闭父模块验收。


## 复审新增问题与处理

独立 reviewer 发现同类 Unicode 可从 `dependencyVector` 的 rule/constraint/ontology 键绕入哈希，复审结论仍不通过。现对每个键在 family 前调用 text 并用固定诊断路径；新增 rule/constraint/ontology/facts 四个回归，Python 49 passed。未将首次复审结论改写成通过；等待完整末次独立复核。

复审额外实际探针：非法 literal 日志/stderr 为零；其他线程、独立 Context 保留日志，异常后 ContextVar 恢复。均由 reviewer 只读执行，不是产品真实执行器证据。

## 末次独立结论

同一 reviewer 对最新完整代码/测试重新只读复核，明确“通过，仅限 T05 私有准备范围；未发现新的实质问题”。原四项反例均重现关闭，独立复跑 Python 49/49、Vitest 5/5。reviewer 报告 13 文件组合 SHA256 `a78309a15ead8e66c231b0484fc0a0658287a86bbc6059968904975b0f4a2b60`。

结论不覆盖真实执行、持久化/IPC、完整 G.2、桌面验收、全仓 check 或指定双模型。新增差异报告核对是只读证据补充，未改变受审实现/测试。


最终补齐常见 datatype IRI 后，独立 reviewer 再次全文复核通过；53 Python/5 Vitest，13 文件组合 SHA256 `079d7c74aa463f800f669de156d2291f16daaba22253ecc5dcdf15e2bc0140b2`。本地完整 check 同版本实际 635 TS/1105 Python通过，非reviewer代为声称。
