# T08 指定双审创建收据静态复核（2026-10-23）

结论：本次创建与受理收据归档核验通过，未发现字节、身份或状态表述的阻断问题。本结论只确认指定材料之间的一致性，不是产品通过、指定审查结论或官方终态确认。

## 实际检查范围

只读检查主树 `gui-dispatch-receipt-20261023.json`、`dispatch-native-receipts-20261023/seal.json`、seal 列出的全部 6 份归档 JSON，以及 `docs/reviews/T08/status.md` 新增第 167–173 行。逐份读取两棵独立树对应的同名 `review-runtime/metadata` 原件，核对字节、长度与 SHA-256，并比较汇总收据内嵌 JSON 与原件的解析结果。另只执行两树 `git rev-parse HEAD` 和 `git symbolic-ref -q HEAD`，核实当前 HEAD 与 detached 状态。

除获准的 owner/受理 metadata 外，未读取任何模型本轮报告、发现、raw、其他任务状态或会话数据库；未访问 UI、global 配置、源码或测试；未执行产品、安装、测试、API 或探针。仅新增本报告，未修改任一审查树。

## 字节与归档核验

以下全部 6 项的归档字节与对应树 metadata 原件完全相同，长度和 SHA-256 均匹配 seal：

| 归档文件（均位于 `dispatch-native-receipts-20261023/`） | 字节 | SHA-256 |
| --- | ---: | --- |
| `zcode-owner-ui-pre-submit-20261023.json` | 820 | `031a8c175f5837ad934cc2207d1c94e4d10f80ff2add088041d8b4a952f909cb` |
| `zcode-owner-ui-submit-receipt-20261023.json` | 1146 | `a5a933817f9bf4f1f7cd8703ad3e56a3b34f74323eb5d5170a196f8ae918813d` |
| `zcode-zcode-glm53-acceptance-20261023.json` | 3491 | `4f142e2c114c3fd4343a6a2382ab211386b5138246ed5568e7e1de0b03e3d8d3` |
| `minimax-owner-ui-pre-submit-20261023.json` | 890 | `eb1706c3da98e1e3afdb3a06503b6cc3b4dade656320ead1f5f99836153a0c2f` |
| `minimax-owner-ui-submit-receipt-20261023.json` | 1351 | `0454ef3a4da1cd9b96e647dc81611dc820b3b3034c6c3bd165f0b3c779de7500` |
| `minimax-minimax-m31flash-acceptance-20261023.json` | 4702 | `29762a68a36907de94622fe41d989440e6b0c323d368b60c3ff39550328b197a` |

汇总收据的两项 `receiptSha256` 匹配原件，内嵌 `receipt` 与各自 owner 提交收据解析后相等。提交前后 cwd、reviewHead、model、effort、permissionLabel、附件大小/hash 未发生身份替换；提交后模型、思考等级及权限字段与提交字段一致。

本次读取的控制材料身份：

| 材料 | 字节 | SHA-256 |
| --- | ---: | --- |
| `gui-dispatch-receipt-20261023.json` | 3658 | `6fd7b2790eb7cd1d3f820b43e20560a0383437fec813428daa4295733efbd7f1` |
| `dispatch-native-receipts-20261023/seal.json` | 3276 | `9fdb1217237ec0a934f0ad8a95cbfb1fadd8ba8b106e8512f90afb2ae928a913` |
| `docs/reviews/T08/status.md`（整文件身份，仅核新增末段） | 29307 | `8bde357728e0999d79535c063bfa698f991beedf522945dca3524d232a6202f9` |

## 任务身份与状态

两树实际 HEAD 均为 `5b64bfea538b638310cd3ce79e595c3b482e003d`，且均 detached，与 owner 和受理记录一致：

| 身份 | ZCode | MiniMax |
| --- | --- | --- |
| 树名 | `T08-zcode-review-93516fa` | `T08-minimax-review-93516fa` |
| 模型 | `GLM-5.3` | `M3.1-Flash` |
| 思考等级 | owner 为“最高”，受理为“最高 (max)” | `xhigh` |
| 权限 | owner“完全访问”，受理对应 `yolo` | owner“始终授权”，受理对应 `bypassPermissions` |
| SID | `session_cd996c3a9b47f03713b41eaae59a83b0` | `mvs_68301ad5197d46ed91bf9aee7ec39f19` |
| 附件大小 | 59804 字节 | 59859 字节 |
| 附件 SHA-256 | `8951b0e305e9326dbb41ff8a2f16c4de5f1c35dc0163d19601b2daa08683029d` | `65104b0ce095ed1c163d16645cc408c8798bf3bb7fd8fc5132494c82f8eea65f` |

两 SID 在 owner 提交、汇总收据和各自受理记录中相同；提交前 SID 未知与提交后官方菜单复制所得 SID 的先后关系明确。受理记录中的 base/product 仍为 `5f910b52c69d86a1076b2032e5d3c63e715947f3` / `93516fa8455cf4b195cbfb699aa7a6652d428b6f`。本轮仅核收据所载身份，未重读附件、Git 源码或重做此前完整范围核验。

所有材料均未把创建或受理算作 Pass：owner 收据为 `not issued` / `working; not terminal`，两份受理记录均未出 verdict，seal 明确 `officialTerminal: NOT OBSERVED`、报告在封存时不可用、root 独立核验待完成；turn ID 仍为 UNKNOWN。status 第 173 行同样明确“无指定终态或完整报告；创建及受理不计 Pass”，保留 product93516fa、原 Goal blocked 及其他原验收门。历史“未创建”段落未被重写，新增末段明确更新其时间状态。

## 证据限制

本轮没有亲自重放 UI 或查询实时会话状态。官方菜单 SID、任务设置、GUI 释放和附件接收来自 owner 的封存观察记录；模型完整读取与自身环境核验来自各自受理记录。MiniMax 受理记录明确说明其无法独立读取实际 effort/任务权限，依赖 owner 读回；ZCode 也保留 owner 来源。这些记录相互一致，但不等同本复核独立取得官方设置或终态。

seal 明确保留官方完整 turn 正文尚不能经核验的官方 Read 能力重建、turn ID 未知及完整报告未取得等限制。本轮不补造这些证据，也不判断任务目前是否仍在运行。后续指定审查结果、发现处置和正式验收须沿原门禁独立核验。
