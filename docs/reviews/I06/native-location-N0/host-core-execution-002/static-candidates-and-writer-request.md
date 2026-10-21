# 002：最小静态候选与下一 writer 申请

本文件仅响应总控对002新结果的静态定位要求；没有修改源码、探针、执行或重建。依据固定 I06 `fc6237e8cad1a4043d46a1c7198439f1da06ad67` 的既有采用源码，以及002原stderr：`case=metadata status=4 owner_nonzero=1`。现有raw不能确定单一底层根因，暂不申请改变返回值/权限策略的修复。

## 可以确定的收窄

`metadata` 是 location_core_test.cc:391 传入 make_owner 的 **case标签**，并不证明已进入 platform_metadata。make_owner:379–388 的失败条件是 status非OK或owner零；ABI:67 的4是 NL_UNSUPPORTED。

capability_core.cc:190–195 先把*out清零，ABI/platform早退UNSUPPORTED发生在owner分配前。只有:207–211在首次monotonic调用后写入非零owner，并注释失败也承担cleanup owner。因此002的owner_nonzero=1排除该早退（含不支持host的platform_id=0分支）。admission本身只有OK/BUSY/BUDGET/INTERNAL，且也在*out发布前，不能解释本次非零owner/4组合。

之后core:214–216只串行执行：started_ms哨兵检查 → duplicate_anchor →（前者OK才）metadata。:217–223 保留第一个非OK status返回；若这些均OK但active时钟失败，只会返回NL_STALE=2，不能单独解释本次4。close_all/原helper cleanup不把这个返回4变成成功；它们也不提供外部drain证书。

在已采用Darwin源码路径下，最小候选为以下 **四处终点**，不能从raw继续排序或任选其一：

| 候选                   | 具体源码                                 | 会产生4且保留非零owner的条件                                                                                                            |
| ---------------------- | ---------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| initial clock sentinel | core:208、214；platform_macos.cc:29–33   | clock_gettime失败，或秒值为负，或秒值超过现有毫秒转换上限，返回UINT64_MAX；owner随后仍发布，core取UNSUPPORTED，未调用duplicate/metadata |
| duplicate fcntl        | core:215；platform_macos.cc:35–42、17–20 | F_DUPFD_CLOEXEC失败，现有error_status把ENOSYS或ENOTSUP映为UNSUPPORTED                                                                   |
| root fstat             | core:216；platform_macos.cc:58–62、17–20 | duplicate成功，fstat失败且其errno为ENOSYS或ENOTSUP，映为UNSUPPORTED                                                                     |
| root ACL query null    | core:216；platform_macos.cc:70–71        | duplicate与前置fstat/类型/UID/mode/link检查通过，但acl_get_fd_np(...ACL_TYPE_EXTENDED)返回nullptr；当前不分errno统一UNSUPPORTED         |

目录类型/UID/mode/link不满足、acl_valid/acl_get_entry非空/错误条件为DENIED；acl_free失败为RETAINED；它们本身不能解释本次4。这里没有观察到任何一个具体errno，也没有依据把ACL null当空ACL、clock能力缺失或文件系统问题。001仍没有case/status细分证据，不追认它与002是同一分支。

## 具体最小 writer 申请（未获授权、未实施）

建议下一步仅给 I06 一个源码 writer：`packages/native-location/src/platform_macos.cc`，限定现有Darwin实现上述四处失败终点的有界诊断，不改变 ABI/core/test/Windows/限额或构建driver。目的只区分clock、anchor-duplicate、root-fstat、ACL-null，并记录失败调用当时已有的errno或clock范围理由；不新增一次OS查询、重试或fallback。

拟增量约束：

- 每个命中的现有失败返回点最多一条固定stage短行；stage只取clock/duplicate/fstat/acl-null，clock范围理由只取固定枚举。errno只在现有失败调用后立即捕获；不可在成功调用或范围错误上解释陈旧errno。每行上限96B，不打印路径、FD/PID、owner值、stat/ACL内容或环境。
- 保持原调用次数/顺序、原short-circuit条件、返回码及句柄/owner/ACL生命周期。日志前保存失败errno，日志不能覆盖error_status所用值；返回前恢复原errno。clock范围判断只拆开原既有条件以给固定理由，不能重新调用clock。
- 不把ACL nullptr视为空ACL，不放宽ACL/UID/mode/link检查，不把UNSUPPORTED改OK，不换API/目录/系统权限，不改变close/reap语义。若需新增stdio头，仅限同一源码文件。
- 静态点审仅核这次writer增量及更新供方指纹；随后由总控另给T03必要采用/构建窗口，再另授精确运行。不得自行第五构建、用现有002再试或增加一般trace/平台穷举门。

这是基于四个剩余候选的一步诊断申请，不是既定修复。若总控只希望先分三阶段，也可只授core中clock/duplicate/metadata阶段标记，但metadata仍留下fstat与ACL两个分支，不能据阶段名直接定因；为避免额外往返，上述单Mac文件四终点是本次推荐的最小可区分范围。
