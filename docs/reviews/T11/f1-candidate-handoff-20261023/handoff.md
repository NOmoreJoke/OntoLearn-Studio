# T11 F-1 新候选完整交接

冻结受审候选：`02a4738a220b2c6e881f7161ee658c61bf4328dc`，父提交 `550d47ad064f4d3899c844e8f791841498851ec5`。本目录是提交后的绑定收据，后继仅流程提交不替换该冻结候选。代码/测试/当前验收均已进入新候选，原036两审树及原报告未改。

唯一核验实现从 `verify.ts` 原字节重命名为 `verify.mts`（38220B，SHA `c3e670e66594af4a7ff4be3d0802f559117ded12d9dceab4a985f576ba930b9b`）。CLI先纯JS校验参数与Node24.3以上24.x门，再在try内动态导入真实.mts；加载失败/JSON或freeze错误/超限返回整段固定错误，不输出路径；manifest schema不合法仍按原合同JSON/exit1，不混改失败语义。测试用.mjs specifier由TS/Vite映射唯一.mts，实际listFiles已证明纳入，CLI不使用不存在的.mjs。没有第二package/schema、根engines/锁/tsconfig/CI修改，也不屏蔽warning。Node依据见[官方24文档](https://nodejs.org/docs/latest-v24.x/api/typescript.html#determining-module-system)。

实际验证：Node v24.15.0，初轮专项122/122；最后3个合同例加入后的125项纳入显式flag完整755个TS测试（零skip），1052个Python测试、构建、ruff、格式、类型检查通过，完整真实child exit0。6个受验路径before/after与新候选一致。模拟版本门测试不冒称早期Node实机；独立warning仍被输出且真实错误exit2。完整raw与真实exit/输入hash元数据共13成员保字节入档；每条索引复验通过。独立agent核实际delta和最终运行原件，未重复测试；其结论不替指定双审。

文件入口：相邻 `f1-fix-20261023/index.json`（1959B、SHA `c7d3a34e7cb4cc3b336f092aa4dd6cd742a42f9571751f54dbf125560f5b4dfa`）；verification 11463B SHA `1ae0844a00d6674a8fa05329d4223e31b724474a84e2fa7f4f5fbe3fab22f949`。精确路径/hash见binding.json。

新完整审查scope为107文件，`review-scope.json` 23213B SHA `b52e1bf8e45fe25c285c57db34bd552a0b9109e94ec429a5fd43b94a8bf0d6ad`，107条全部与新候选Git blob逐一复核。涵盖原56（唯一rename映射）、原25产品/8流程/前23修复、五脚本/两测试/两fixture、PRD、四份历史完整报告（7d28两份与036两份）、原18逐项意见及所有新观察、036完整创建23载荷与550收件15载荷、F1设计/实际delta/验证/raw，以及全部已登记操作偏差。不能只审F1或复用036 Pass。

新任务尚未创建，GUI持续RELEASED。后继按根协调资源创建两个全新完整同版指定任务：GLM-5.3/最高与M3.1-Flash/xhigh，实际读回各自模型/effort/权限、当前AGENTS字节hash及独立环境；完整prompt/attachment真实读取、原turn正式终态和全文意见接收。两方只读自己本轮材料，另一方本轮材料禁读；列入scope的036及7d28材料明确是历史。

新审边界应明确：任何临时仓也禁止commit；即使参数错或预期平台门拒绝，也禁止运行真实collector/native。允许原已授权普通suite/CLI/临时SQLite/worker；不能因child/SQLite关键词泛停或skip。原生读回仅精确自身SID/原turn、确切自身输入/公开工具/正式状态，禁止广读user role导出注入上下文、header/system/thinking/全局日志和配置。未知旧越界结果继续UNKNOWN，不检索、不转存，不事后补授权。

旧18项owner关闭数0，新增M036-F1本地已实现验证但待新指定门关闭；历史M NotPass、Z信息级O1与M中级F1差别都保留。此前owner/根审计读面偏差与两审提交输入偏差不因技术修复消失。真实平台/签名/同包/模型API/真人/Q5、完整P0/CI/PR/合并/远端/发布门不由本交接关闭；无push或PR。

550d47安全包精确目录及原两报告名已列binding.json的historicalSafePackage550，根可直接取读，不需全局发现。本轮运行目录runtime未纳入Git；raw和元数据已固定13成员归档，不声明其余临时产物全部归档或全流程零暴露。
