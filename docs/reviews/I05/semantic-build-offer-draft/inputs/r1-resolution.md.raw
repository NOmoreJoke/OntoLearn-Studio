# R1 处置：新候选待独立 delta

原候选 0e42a0fe349054a92817cb4d463bccdc15f6c042 的 R1 结论为 Fail，已在 cf15439a72207e622d2f8baa8d476a363107f5c6 保全。root 全文读回后才开始修改；实际时间顺序和本会话原 JSONL 记录 ordinal／hash 见 review-chronology.json。R1 报告的 current=Git=manifest 仅适用于审查结束时的旧72件，不用于此后 WIP。

| 项目 | 实际修复 | 验证边界 |
| --- | --- | --- |
| R1-01 P2 | CollectionBoundary 共用 preflight 前起点；_checked_call 显式检查各真实调用前后，覆盖 parse/query/legacy/profile/scope/material/compute/restore/roots/offline/B1阶段。原 canonical 函数及参数未替换。已返回值先存真实引用，再检查过界，后续调用不再启动。 | 仅 AST／控制流及测试源码。新增真实首parse后121、两次累计70→121、preflight已耗121、协作取消的测试，未执行。opaque 调用本身仍不可中断。 |
| R1-02 P2 | 当前 stage/API 与阶段开始／结束／returned 元信息进入 observation。异常时只读序列化已完成真实阶段；生产 bytes/wire/allocation/capture与本次 expectation分阶段保留；未成功返回的 restore不产生 view。unknown 安全 INTERNAL_ERROR，边界停止另分类与退出码。scope 已完成阶段同样保留。 | 仅静态。测试写真实 First 后 Warm/SHACL fault、真实 producer 后 restore fault，不 fake 成功结果；当前没有运行通过。超出原 item/report cap 仍失败而非截尾。 |
| R1-03 P3 | generator 将报告尾部固定为恰一个LF，重建报告和来源清单；两份业务输入资产 byte-for-byte 不变。static-verify 改为分别审 base→固定ref、base→tracked工作区、stage、unstaged与各新文档文件，不再拿无ref工作区diff的0覆盖新候选。 | generator和--check确已执行exit0；两assets SHA不变。固定ref diff结果在新提交后另存，旧static-verification.json原结果与R1 Fail不覆盖。 |

测试原作者已补齐并封存70个 test 函数；本窗没有 import/执行这些测试或任何产品。输入仍417 observations／320 datasets，原83/106/54/50/C13不删不改。供应22件及四资源、lock和构建writers不改变。

首候选 manifest 的72 payload包含一件与base未变的供应根 __init__.py（101B）；manifest自身不计入payload。因此 payload集合与实际Git delta文件数不应直接相等。新清单也按明确供应／候选资料范围核身份，Git变更集合另核。

不因本处置自行宣称独立通过；必须冻结新本地 candidate 后由独立 agent 只读 delta，保原 Fail并逐项核关闭。运行、T03锁／环境／构建来源、source/package等价、外部oracle、原S1和正式门均继续后置。
