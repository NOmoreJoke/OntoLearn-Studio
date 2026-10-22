# F1/N1 精确 delta 冻结

产品提交 `e37cc2b161b53a6250a4085104ee955c423fb149`，parent `d4686b1769b5925190a9e7afcc23b92d5db04d4d`，tree `71b99b1ca0408a604c36742d0e3f3b90a5ec2ff1`。仅四产品路径；AGENTS 保持未暂存，过程文件未混入提交。

F1 已统一新合同全部适用路径/证据域、当前 c706 与已采用 a633 和历史组件分域、静态与条件 unit 授权边界、16 类负例；N1 原流 path 引用无条件保留。六个新关系 unit 与 Node 机器映射/三阶段 hash-IO 负例已写入，但没有运行。

机器映射在新合同 JSON pointer `/buildScratch`，阈值 `/buildScratch/sampling/thresholdBytes` 为 8589934592，采样模板 `/buildScratch/sampling/rootTemplate` 覆盖整个 own runRoot 单一递归账面域。I05 外部 caller 负责采样/监控和缺 guard 拒绝；T03 builder 不强制该阈值，不实现 OS 硬 quota，不授 build/OS 执行；permit digest 不绕过 BUILD_SCRATCH_GUARD_REQUIRED。

实际通过的只有 AST/JSON/文本关系/hash保护向量、Ruff、Node 语法和产品 whitespace 静态检查。首审8成员与原始失败完整保留。没有运行产品、unit、stub 或 build helper；四源停写，等待非作者实际 delta 审及主控另行 unit START。
