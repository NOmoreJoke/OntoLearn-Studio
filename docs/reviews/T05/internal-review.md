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

## 获批 T09 输入适配审查

独立 reviewer 再次检查完整本线与新增固定输入：实际用 `git show 873c8c0…` 核对 manifest/17文件/PRD源原字节一致，未消费未批准服务或Store helper；既有实现与 `dcc5ec8` 无差异。同一告警join、字符串001、R-05/06稳定未执行计划保持；50案例均runtime-pending，无actual字段，expected未当作运行结果/存储。独立复跑75 Python通过，明确通过仅限准备与输入适配范围。

32受审文件组合SHA256：`ce69de6c0a52c117807e67033a0e5e6e3ac2f132e9ff7441b6cf472af5e4cbba`。未修改文件、未开GUI，不能替代指定外审和真实执行验收。

## FR-505 代表输入与语义提案复核

独立reviewer全文只读复核，明确通过仅限私有准备和代表输入提案，未发现新实质问题。实际111/111定向通过；12个比较正反例手算一致；两个不同告警未误拼为一条High/Open；多输出共用R-risk-multi/A01四条输入依据；ontology/catalog/reset一致。原13核心文件未变，无第二执行器、Store写入或expected到actual路径。

35受审文件组合SHA256：`06f3d269007858672a0793f7c6ae4180e8ed62d985579ea08dbd076155b021bf`。此结论不证明真实推理、正式集成/公共协议、指定外审或发布通过。

## 具体保存参数与真实 Store 复核

同一reviewer对完整最新本线只读复核通过，仅限私有准备与隔离真实Store探针，无新实质问题。实际导入源与批准5f逐字节一致，格式2/SHA4abf1082...cf6842；临时SQLite、启停修订/历史/旧base、事务内三阶段故障及重开、提交后marker/同operation幂等均成立。未消费未批T01/格式3，未新增生产入口或存推理expected；引用派生/正式接线仍待验。独立118/118；原13核心文件未变。

38受审文件组合SHA256：`ed0a7bf930f0af73ee89489bfcdbadae6ae4a38ddf064a55f0571ee092b928a8`。异常注入不是实际进程崩溃/IPC丢包；不替代指定外审或正式集成证据。
