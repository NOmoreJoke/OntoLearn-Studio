# F1 最小修复方案独立静态设计审查

2026-10-23。结论：方案方向合理，可按本线最小范围实施；静态上未发现必须改根 package/tsconfig/锁/CI 的理由。通过条件是后继实际证明 Node CLI、TS 类型解析、Vite/Vitest 三条路径及完整 stderr；本意见不是实现通过、测试结果或指定模型 Pass。唯一新增本设计文件，未改源码或配置、未运行测试/复现命令。

## 已核对的解析依据

当前根 package engines 是 >=24 <25，TS 5.9.3、Vite 8.3.4、Vitest 5.0.5；tsconfig.unit.json include tests/unit/**/*.ts，继承 contracts 配置的 module=ESNext、moduleResolution=Bundler、strict/noEmit。两个专项直接导入唯一 verifier。共享交接第3行明确不得另建 package/lock 旁路唯一配置。

[Node 24 官方规则](https://nodejs.org/docs/latest-v24.x/api/typescript.html#determining-module-system)明确 .mts 固定为 ESM，.ts 才按 .js 的模块规则判定；Node 直接执行时不读取 tsconfig，且相对 import 必须带真实扩展名。因此 CLI 改 ./verify.mts 是正确路径；仅移动原实现、不留旧副本或第二 schema，保持原字节 hash，可避免类型探测重解析这一成因。

[TypeScript 官方扩展替换表](https://www.typescriptlang.org/docs/handbook/modules/reference.html#file-extension-substitution)明确 .mjs 可首先解析为 .mts；显式扩展的相对导入也支持该替换。因此测试写 ../../scripts/release/verify.mjs 与当前 Bundler 类型解析相容，不必为了 .mts import 修改 allowImportingTsExtensions。该规则证明的是类型解析，不能据此说 Node 能加载不存在的 verify.mjs；运行测试必须由现有 Vite/Vitest 实测映射，CLI继续直指真实 .mts。

## 需要保留的兼容限制

- Node 官方版本历史注明 v24.3.0 才停止 type stripping 的 ExperimentalWarning。当前获验工具 Node24.15 可以验证本方案，但根 engines 仍包含24.0–24.2，故不能宣称全部24.x严格 stderr 都无警告。先固定实际验证版本并明确CLI支持口径；若要收紧全仓 engine，交 root/唯一配置 owner 决定，不自行改共享文件或全局吞警告。
- .mts 不在 unit include 的初始 glob 中，但预期通过两个测试 import 传递加入类型检查；须留 tsc 对 tsconfig.unit.json 的 listFiles 实证，确认列入精确 .mts，且旧 .ts 不再被误用。不能仅凭 fullcheck 退出0就断言该文件受检。
- Vite/Vitest 对虚拟 .mjs→.mts 的解析、现有 fs mock/模块身份和固定探针必须实际验证。若失败，记录具体解析错误再协调，不制造 verify.mjs/verify.ts 兼容副本或旁路 package 来求绿。
- ESLint 现有全局 ignore 覆盖 release；全仓 lint 不能自动证明 .mts 已检查。沿用显式解除该路径 ignore，直接检查 .mts/CLI/两测试且确认没有 ignored/no-matching 告警。Prettier 同样须显式 ignore-path /dev/null。不扩大共享 ESLint 配置；本模块也没有 React hooks 规则适用需求。

## 必要回归矩阵

1. 参数数量不足/过多/缺项：usage 整段固定、stdout空、exit2；不要只测参数缺失一种分支。
2. manifest 与 freeze 分别无法读取、JSON格式错、16MiB超限：每路径独立验证整段 stderr 等于约定固定错误码和换行，stdout空、exit2；用例输入名含明显标识，确认不输出内容、绝对路径或 MODULE_TYPELESS_PACKAGE_JSON。恢复整段断言，不以 trim/末行筛选吞掉前置输出；若允许尾LF规范，断言应明确这个唯一规范。
3. 正常 synthetic：完整 stdout 可解析、consistent/模式语义保持、releaseAuthorized=false、exit1、stderr空。保留 evidence 生产 profile 和原固定源/身份/全部专项，不放宽错误接受条件。
4. 受控 --import preload 仅放本方临时目录，使用明确 .mjs 与 file URL（跨平台用 pathToFileURL）；仅主动 emitWarning 一个稳定测试 code/message，再走真实输入失败。要求 marker仍在stderr、固定错误码仍出现且exit2/stdout空；不要依赖 warning 与错误码先后或PID/完整路径字面。该注入场景故意产生额外诊断，不能拿它放宽第2项无注入基线的严格错误面，也不应修改全局 NODE_OPTIONS/NODE_NO_WARNINGS 或拦截所有warning。
5. listFiles、显式lint/format、显式四固定输入探针专项及原 fullcheck 按新实际数量/退出/skip留原件。此处只是后继验证要求，本审查没有执行或预填通过。

## 范围与冻结

唯一 schema 实现应原字节重命名 verify.ts→verify.mts，删除旧实体；CLI及两测试只更新导入路径，随后增加真实错误面回归。当前 README/acceptance/status 和新候选索引同步路径、Node验证版本及真实结果；历史036提示/报告/收据/manifest保持原字节，在新交接里明确rename映射，不能让原25路径覆盖表漏掉唯一实现。

该变更需要新候选、独立实现复核和原指定门。没有第二 package/schema、共享配置修改或新增资源授权。F1、旧18项、M NotPass及本轮input-only/owner越界事件均不由本设计意见关闭；过程事件不能抹去F1技术发现。

## 最终补充：JS bootstrap 与本地运行时门

同日复核 root 采纳的补充：合理，建议作为最终实现方案。CLI仅为明确 .mjs 的 JS bootstrap，先处理参数，再要求 Node major=24 且 minor>=3；不满足时固定 UNSUPPORTED_NODE_RUNTIME/exit2/空stdout，之后才在 try/catch 内 await import('./verify.mts')、解析和核验。这样不需改根 engines，也避免早期24.x在加载TS前产生实验警告；动态模块加载失败纳入原固定错误码，而非未捕获异常/路径。将此约束明确限定为独立工程CLI的解释器支持，不改变最终产品用户无需Node的边界或双OS产品矩阵。

实施时版本条件应 fail-closed（major===24 && minor>=3，解析失败也拒绝），参数错误与runtime错误的优先级按“参数先”明确保留；不要在门前静态导入 .mts 或其他会触发类型探测的模块。文档写 CLI >=24.3 <25、实际受验24.15；这个guard和无警告保证不外推任意古老Node解析器或调用者额外注入的运行时参数。

必要补例合理：受控子进程preload模拟版本，只证明guard分支，不声称旧Node实机通过；临时目录只复制CLI、不带verify.mts，实际动态导入失败必须固定整段stderr/exit2/空stdout，不输出ERR_MODULE_NOT_FOUND堆栈或路径；独立preload emitWarning仍须保留marker，不约束warning与错误码先后。保持无注入的正常/错误面严格断言。额外验证24.2/24.3边界与非24大版本、参数错误优先级，计数按实际新增回归记录。

最终设计静态无阻断问题，可以进入最小owned实现与后继实际验证；TS listFiles、Vite/Vitest映射和显式.mts lint等前述验证条件继续有效。本审查不运行这些检查、不预先关闭F1、历史意见或过程异常。
