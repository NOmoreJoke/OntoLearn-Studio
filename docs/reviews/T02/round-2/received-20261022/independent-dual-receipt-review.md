# C5 R2 双指定收件独立静态复核

结论：**通过本次收件归档与 owner 表述边界的静态复核，无必须纠正事项。** 本结论不是重新审查 C5 产品，也不替代指定模型结论、意见处置或父验收。

固定过程 `ae084b3f43f72925dc0069c4f153976587446008`，产品 `e5ad54e5762157cafe532c2a0c07c22e8dd737cb`，原 base `5f910b52c69d86a1076b2032e5d3c63e715947f3`。本次读取该过程的 ZCode 七件收件、dual-review-disposition、status/backlog 追加及已归档的 MiniMax 收件；不访问 live 会话或应用存储。

## 归档与来源核验

- ZCode 原报告 20343B／SHA `c3f5efd5858a568b2ed4843eac8a0210ed0ea66832bc6b37ebfae278c90bd8a2`，终态文本 2334B／SHA `8e43ef4a963a35dc1e7e3e4136ed8b52c55179a0777d896b915592f98ddc6cee`，均与 receipt、固定 Git 和 owner 当前原件匹配。未改原报告。
- raw tar 为 703715B／SHA `ad53709d4e7f5dfdc719c13abedba5fc76b1dfc768c0ea32735bf28de596ed06`；21 个成员的名称集合、大小和逐项 SHA 全部匹配 manifest。仅在内存解包读取，未执行成员。
- `runs.json` 实际是 **8 条 executed＋1 条 auxiliary**，不是九条均有日志/hash的运行记录。八条 executed 的日志大小/SHA全部匹配；退出记录为五次0、三次1。auxiliary 仅记录 exit0，无对应日志/hash。另有 `input-verify-final.log` 原件，由 report-final 引用，未列入 executed；初次与最终输入核验日志字节相同。input-verify 原始 stdout 本身没有 EXIT 行，其0取自 runs 元数据，不冒称每份 raw 都自带退出标记。
- 归档完整 check 明确记录634 TS／1164 Python及 EXIT=0，专项112及 UI completedCheckCount=21亦有成功原始流；本独审未重跑。
- before 清单26项，在 owner 树当前逐项重算大小/SHA均相同。8 fixture＋4引擎源＋3renderer＋4 Python测试＋1 TS测试＋5harness＝25受审路径；AGENTS是第26政策文件。原报告“9 fixture”为原文计数错误，owner纠偏准确。
- after JSON仅保存head、零漂移汇总和说明，没有26项独立after哈希。owner没有将其包装成完整逐项after证据；当前26项核对不能重建审查运行期间每一时刻的状态。
- e5ad到本固定过程的 apps/packages/tests、package.json、package-lock.json、pyproject.toml、uv.lock差异为空；固定提交 git diff --check exit0。本次不重新核验所有130输入。

## 探针与报告精度

最终 Unicode raw 精确为 **33记录＝32 OK＋1 INTERNAL-NOTE**。仅静态读取归档脚本AST和原始流，确认七类路径分别使用DB80／DBFF／DC00三个码位，另有Put/Copy、对象字面量、拒绝后不变、合法Unicode和诊断检查。不是全surrogate码位穷举，也不是33条均为拒绝负例。该脚本直接Triple探针仅构造object字面量；三术语源审读及既有套件是另一证据层。owner已正确限定原报告的概括。

前三次harness失败及退出1均保留：字符串字面量换行、fixture参数冲突、错误domain目标；第四次EXIT=0。原报告“实际执行命令全部0”只能按最终成功运行理解，不能抹掉前三次失败，owner已明确纠偏。未将这些脚本问题算为产品失败。

MiniMax原件及owner纠偏继续保持：19注入点中8点全2048码位、11点仅两个端点，合计16406；不采用原报告“20点全部穷举”的描述，也不自行改其有界Pass。未重跑或执行该脚本、临时C4或任何产品代码。

## 双审处置与未验边界

两原报告各自给有界S1 Pass。owner准确并列登记四项尚未实施修复的P3：内部snapshot_digest边界、陈旧交付指针、深链祖先Set成本、localGraph无条件重算；保留两审者对snapshot_digest的定级差异。T01 Store surrogate为范围外观察，未转成T02修复授权或当前T01新候选结论。语言小写子集和完整前置parser等延期也未被写成已实现。

terminal receipt的session/turn/stop等来源是owner对精确官方会话的读回记录。本独审只核归档一致性，**未独立认证现场、官方后台存储或所有工具执行过程**，不据原报告“无审批行为”认证权限配置。没有访问其他官方会话、live模型意见、运行产物目录或GUI。

四P3未自动关闭；源绑定／metadata／S2 proof／CostSession、真实确认与原子提交／receipt／undo、I05交换、正式App/bridge、T08、跨模块、平台／真人／CI／正常合并／远端及发布仍待。父Goal blocked、旧Fail与新Pass各固定版本归属保持。当前两方有界Pass不能外推上述门，也不授权直接push/PR/merge。

本次仅写本独立报告，未改其他文件、未提交，未运行产品、探针、测试、SQL/DB、native或GUI。
