# T01 cd880 → 固定 507 消费 shape 独立静态核验

2026-10-23；结论：**通过。未发现阻断、事实扩大或需修改的非阻断问题。** 三项最小接口请求均有固定源码支持；本结论不构成 consumer 实施票、后端整包验收或 presentation 政策批准。

## 范围

全文核验 `docs/iterations/T04/t01-cd880-query-consumer-shape-20261023.md`、对应 `shape-evidence-20261023.json`，以及 status 本次最新 supplier bullet。复用本独审刚完成的固定 `cd880936e406d392b4e57da67d5b03b23b33ef27` 三份 Python 必要接口证据与固定 `5070004ec8e3219bea33960bd88f57f1976e9cf8` 消费口证据；另只读 cd880 的 contracts index:179–267、preload:1–35、desktop-ipc:46–84、task-service:771–804。未重新核对 20 项向量或七文件包，没有读取 raw/private/native、其他树、后台或 live 需求稿。

JSON 中 publicInputsFullyRead/sourceEvidence 记录的是 owner 读源与身份工作；本次不将这些字段升级为独审重做全部公开输入、全文件或整包审查。固定 ref/parent 与本次任务一致，界面消费仍以 507 为准。

## 三项请求核验

1. **缺命名创建入口，而不是缺后端受理。** cd880 `contracts/src/index.ts:221–267`、preload:15–35、desktop-ipc:46–84 的有限命名方法/通道没有 create；task-service:771–804 有真实 metadata/page 读取与 main 组装 binding。后端 coordinator:380–428 已通过现有 job.create 接受 query.execute 并返回真实 job。要求唯一 bridge owner 固定业务命名方法、主 authority、真实 accepted job/错误，未要求重写 executor、公开通用 invoke 或 renderer put_blob，准确且必要。
2. **已提交定义与可编辑 draft 的身份/版本须接上。** 固定 507 execute 回调仅 draft+selection、返回 Promise<void>，无 definitionId/load-base 或 jobId 返回；后端执行 snapshot 中 `{text,references?}` 的指定 query 定义（semantic_execution:154–159；job_store:1435–1439、1496–1510）。页面编辑 B 不能静默执行旧 A。要求权威读取、ID/载入版本、保存/CAS及执行版本绑定有实据；未私设自动保存、按名称猜 ID、draftDigest=parametersHash 或未保存草稿执行路径。
3. **证据叶分页与查询展示投影确有差别。** semantic_execution:299–328 的首行是五项 cells，后续 JSON-pointer 叶/分片是四项；固定 507 acceptPage 要统一 columns 行宽。公共页不是 SELECT 结果表，也不是已批准 ASK 页面形状。要求唯一 owner 冻结权威执行文本、SELECT/ASK、空/零列、绑定及有界续页的读取/投影接口成立；没有让 T04 删除证据首行、收齐所有页重建 payload 后自行发行 presentation 政策。

## 后端已有事实与精确认证

对照正确承认真实 jobId、终态/resultRef 和完整 payload 已有，不继续登记为缺 executor：

- `job_store.py:979–1008` 校验 job.create 参数，取项目归属 snapshot 与项目 blob；`663–673` 对 blob 重算摘要。`prepare_query_request:1420–1445` 要参数精确为 inputSelection=current/historical，仅 asserted、空 derivedResultIds、null preparedPlanRef/confirmationRef；current 还需 snapshot 等于该项目当前值。
- `1068–1102` 由 Store 发行 uuid4 jobId、queued/stateVersion=1、resultRef=null。`1594–1619` 同事务发布 rows、完整 payload 与两摘要，然后 succeeded/resultRef；`1256–1269` 推进状态版本和终态时间。operation 重复受理保留原 context 身份，不以新稿替换旧受理。
- `semantic_result:1621–1663` 内部直接返回 `(metadata,payload)`，复核成功 job、resultRef、输入身份与 payload/rows 摘要，不重跑查询。公共 metadata 是 17 个顶层字段，没有 columns/executedSparql/ASK；payload 则保留 queryText、query 的 SELECT variables/rows 或 ASK boolean、输入/范围/定义/选择及 provenance。
- coordinator:475–480 没有直接公开 semantic_result 路由。文档同时明确现有 result.page 递归投影完整 payload，可逐页包含 `/queryText`、`/query/type`、variables/rows、`/query/value` 的编码叶，因此没有误写“RPC 完全取不到 queryText/ASK”。直接结构化完整读取与可公开逐页读到编码内容两件事被正确区分。

本次是必要接口静态核验，不以源码分支存在或供方交付声明替代实际运行/收件；也不重复证明 worker 中 executor 调用次数。

## 授权与未闭边界

status 新 bullet准确限定“根最终收件进行中”和当前无 consumer 写票/运行票。T01 asserted 后端的具体进展未被抹去，历史真实 executor 未被否定；public presentation/App/draft save 仍未由该后端票扩大授权。

F-R3-01 长度度量/错误分类、ASK=false 与空 SELECT/零列、typed RDF 以及 selected/profile 等完整要求均保留待唯一契约/真实接口确认，不设默认答案。后续验证随成熟接口及实际改动确定，没有要求无变化重测 S1 或重做终态。

## 本次文档身份

| 文档                                                  | 字节数 | SHA-256                                                            |
| ----------------------------------------------------- | -----: | ------------------------------------------------------------------ |
| t01-cd880-query-consumer-shape-20261023.md            |   9747 | `3f4d644a64e9ce9e837bb56e72287724d7b20b9cafa80af1cd657ebe639c328f` |
| t01-cd880-query-consumer-shape-evidence-20261023.json |   4762 | `7f9a8ab2261a4090697d718a35d49ee5f07c79ffb4e46bb062aeb42b6999cddd` |
| status.md（全文件身份；只审本次最新 supplier bullet） |  14298 | `77ca3f63e3b5d351ca2c79dd3640c05de4ffe2283f282a3a4133b0b84304d3de` |

只新增本审计；未改原件、consumer 或共享源码，未运行产品测试、GUI、后台或外审。本次通过是接口对照文档通过，不是正式端到端接线、父验收、发布或 Goal 完成。
