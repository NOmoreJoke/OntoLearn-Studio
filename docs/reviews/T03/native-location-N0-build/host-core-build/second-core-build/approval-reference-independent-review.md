# 第二次 core 窗口：approval reference 独立定点审查

2026-10-22。结论：当前窄锁候选可接收。实际差异只有授权指定的两个 reference，真实归档 ref 与 5010B 授权原件匹配；完整 12 项当前工作字节均与新清单吻合。权限未因引用更新扩大到其他 target／component。此静态审查不表示第二次构建已经运行或成功。

## 授权与候选身份

已全文读取 `authorization.md.raw`，实际 5010B、SHA-256 `9845bfc836ea0763713f79895b66b5b7a3a8f7a103369837cd48ae932e55f3c9`。其工作字节与真实提交 `228815f1f4f2bad005f21faffd8676c8713431c8` 中 blob 逐字节相同。该提交父级为 `5d7a143f2c100c5ca4ed6b36f7fa8fc2df611a34`，提交只新增这一授权原件；未用未来或不存在的 ref 作引用。

相对 5d7a 的旧锁，严格 JSON 解析并对对象全比较后，仅下列两字段改为 `228815f1f4f2bad005f21faffd8676c8713431c8`：

- `toolchains.darwin-arm64.approval.reference`，原为 `d6ed4e4bb9401ff310337937acd3196b9392e2fa`。
- `execution.darwin-arm64.core.reference`，原为 `c66f6e8ce7fee7f77ed7ed259d0771ef8c8ff278`。

两个 approved 保持 true。source、API3、test assembly 的 ac37 批准及 b1c source ref、6a contract ref保持原值；Windows toolchain、Node、Windows addon，以及 Darwin addon／fixture-addon、Windows 各 execution 仍 false。全部其它字段、pins、environment、两份 source／records descriptor 和范围未变。JSON 未见重复键。

新锁实际 10474B／`9be20b219a9420b49475e91a43dabb815551ad2e17815b03cd0dd376b49f15b2`。CMake 19815B／`f2b5522b92c5dfc9724b95c35b876ce5015a4955385f614a6da20fb9bce57645`，driver 30056B／`ca4ef93024762ae5dfd3dc95133f8ab28ae2e63048af0b3a658bfeb98f62045c`，均保持原固定实现；没有重审实现或运行语法／验证程序。

## 完整 12 与费用计划

`approved-input-manifest.json` 实际 2956B／`b8ed14c319d083d74093a872a5622788d9550ce61c306d02a3a18c7b173af72e`，含 12 个唯一产品／测试路径。本次逐项只读计算工作字节 bytes／SHA，12 项全部相同；前九项与锁的 source.files 逐项相等。清单的授权 ref、原件 bytes／SHA、旧产品与过程 ref、onlyAllowedDelta、单次尝试及 artifactExecutionAuthorized=false 均与实际候选和授权匹配。

`read-and-record-plan.json` 实际 1226B／`c5e149ed66fa28fdf7785cbc21e6b688da772a4e5b1bef032ac97cd1d65e1696`，与全文授权的费用口径吻合：

- 构建阶段 40GiB = 42949672960B；声明累计 37044475528B，余 5905197432B。原供应阶段 9745727085B 独立保留，两阶段声明合计 46790202613B、组合 guard 52695400045B。
- 实体记录保守 85544+85544=171088，低于 200000；未把首轮 CMake 未知完成数当零。
- metadata 逻辑访问 827096+171088=998184，授权本次累计上限 1100000，余 101816。当前小审查／收尾仍须计入；没有重置历史账，也没有将声明预算写成实测 I/O。

这次 40GiB／1100000 的扩界来自新授权原文；先前未授第二次运行的历史结论照保。`approval-reference-delta.patch` 为 862B／`dd550998ca0cb44573a736793c0fcd0512b604d9537cc9a84ea696822631bef6`；本审以 Git 实际差异及 JSON 全对象比较为准。

## 执行边界与未验证范围

新授权明确只准一次 `node scripts/build-native-location.mjs --target darwin-arm64 --component core --build`，须由固定新 HEAD 产生新目录；原 13 命令、每 command 600000ms、parallel2、shell:false、绝对 pin、固定 DEVELOPER_DIR 及 R5 首因／独立双流保留要求不变。允许 compiler identification／try_compile 编译链接，仅构建 location_core_test 与 location_child_probe；不增加 try_run、CTest、生成产物／child／native／addon／Electron／GUI 执行，也不自动第三次重试。成功仅可报告 built-unverified／NOT_RUN。

本次只读授权、小 JSON、Git 对象／差异及 12 项小产品文件的身份字节；未读取工具／SDK／cache 供应实体、大 inventory 或 42772 映射，未运行 driver、verify-only、Node 用例、configure、编译或测试。授权、完整输入及窄差异的定点审查已成立；owner 可按原授权固定新 HEAD 后执行唯一一次窗口，无需以本审名义追加常规审批停等。实际 outcome 仍须另审，不能把本报告当构建结果。
