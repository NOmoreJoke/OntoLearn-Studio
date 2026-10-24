# T01 business3 校验层候选验证

唯一canonical新增严格3分支与跨端完整共享fixtures，生产默认2及原Coordinator拒3守卫保留。实际采用、完整帧与未来ready/启动诊断边界见 [adoption](../../iterations/T01/business3-validator-adoption.md)。本阶段未改main/engine、coordinator、worker或protocol/resources；不能把纯校验层当真实3会话或应用功能验收。

本线专项首跑196 TS / 195 Python通过；完整 `npm run check` 实际exit0：826 TS / 2496 Python通过、44原不适用skip，lint/格式/typecheck/build/ruff通过。两端完整共享84 schema、15 hello、43 response、11 route和41绑定反例；测试包装差1已记录，不混用旧630/2301。没有GUI/e2e/native/包内或生产验证。

独立只读复核未发现新增实质阻断：Python39、TS39响应变异及TS5事件绑定，共83额外checks通过、输入不变；旧全部defs及旧resource顶层值机器比较一致。首个TS esbuild未安装装载失败在执行产品前发生，后用已有TS5.9.3内存编译完成，未安装依赖。具体固定10路径hash和两份设计分阶段hash见 [independent](business3-validator-independent-review.md)。此内审不替代指定双模型同版审查。

证据采用Git内小型压缩原件：`evidence/business3-raw-evidence.tar.gz` 29617B，SHA256 `4f012bb90358ee3f5d963f9ee4706d8666828033c971d513b95c1eed8c6a3594`。包含主线6对、独立3对实际工具call/output及3份完整logs，逐成员字节/长度/hash回读；JSON索引记录原session captured prefix/行/offset/hash。主线实际session33228专项及54464全check启动和终态poll均在其中，不以call/output成对代替异步完成证明。少量并行只读返回保留原完整行，未仅截exit0。原封存脚本首尝试捕获自身未完成call，被完整性断言拒绝，未登记为有效证据；排除封存自身后才生成本hash。旧应用CAS/source各证据包未改。

本阶段另完成设计：source r4明确active receiving精确重试、sealed/终态拒append、accepted durable pin不受迟到transport动作撤销，及unknown/barrier/满额/重建计账；表摘要r1独立修订核清sheet/implementation两门并标受限CSV编码选择，真实parser身份仍缺。T05 r2仅接受我方context/DTO/身份与未来诊断包装，不裁Q6、不注册新路由、不采用C3；第二agent只读复核无越权或错误分类。设计不作为实现测试通过。

后续先冻结完整表摘要并在已授权canonical实施可验证纯助手；业务3运行时启用须先完整安全启动诊断/Store3+Job-ready/同buildhash及真实子进程互操作方案。学习账本、完整restore、source wire/parser/producer授权与transfer/import仍未实现；最终指定双审、PR/CI/合并及父验收继续保留。准备本地恢复提交，不push。
