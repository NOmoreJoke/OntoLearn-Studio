# T01 四文件未来维护明确接收回执（尚未生效）

已全文读总控 `I05-I06-T01-foundation-four-file-handoff.md` SHA `bad9716a9f3669a40ddf1ddcd98b33bb3f1ca5898b5c3fd5ed8b72b06be82965`，private中jsonl、presentation、I06 startup三组各offer/binding或response/独立报告共9份原件；逐份实算长度/hash与root固定索引相同。root identity原件SHA `4781fee5b34a0b89d1c3d5fa01e1d7ed7fea74411c5c9cfcb2c6a2c51ad04845`已实际读回。完整机器回执见同目录JSON，记录当前观察时间/双方HEAD与逐路径状态，不用旧观察冒充现在。

**逐文件明确接受未来唯一维护责任，当前四项都尚未生效，也没有startup实施授权：**

| 路径                                               | 供方→未来唯一owner | 批准5f/接收当前SHA256（逐字相同）                                | 字节/当前path状态          | 明确接收                        |
| -------------------------------------------------- | ------------------ | ---------------------------------------------------------------- | -------------------------- | ------------------------------- |
| apps/desktop/src/main/jsonl.ts                     | I05→T01            | 12c0437f66b73b0aa88617b551394f6771529d2e5f307a5ab2765feb1fc05357 | 4774；staged/unstaged均空  | 接受这一独立offer，非默示扩张   |
| apps/desktop/src/renderer/src/task-presentation.ts | I05→T01            | 5ddcd33a9e00e367597d20d8d2449062df577a1f3cdb53dfae2318a173858751 | 8446；staged/unstaged均空  | 独立明确接受，不由jsonl答复涵盖 |
| apps/desktop/src/main/task-service.ts              | I06→T01            | 8d513fe5a25a4dc82839cdc6200ae1972b7743620175bc7e309834a712655122 | 32727；staged/unstaged均空 | 接受，仅从批准5f同一blob起步    |
| apps/desktop/src/main/index.ts                     | I06→T01            | 7df36c6d51a63de4ba6a302cb5063affffeb2dd6a1d9598bec29da8b09ea6bc9 | 6769；staged/unstaged均空  | 接受，仅从批准5f同一blob起步    |

四个接收文件实际bytes均等于本树批准5f Git对象和private批准raw原件，非只比较hash。I05两供方当前HEAD已为db0da44而非root早先6e6，现场各path仍clean、bytes与批准相同；仅更新观察，不解释为C4已批准。I06两个供方当前660da44各path clean，但分别33131B/SHA7ed65b…a68、12088B/SHAd88c1d…60b，与e2c同且不同于批准5f。仅读原件身份/哈希核验，不复制、解释采用或执行未批准gateway逻辑；T01接收起点绝不替换成这些供方字节。

接受供方停止所有checkout未来逻辑编辑的承诺，以及旧固定字节的只读构建/验证/全范围审查保留权。若旧审查/集成需要写任一文件：供方先给root精确路径、理由、起点、窗口、验收；T01停该path并保存HEAD/当前SHA/WIP diff/测试状态，双方明确唯一接手者与实际身份，root书面登记生效后才可编辑。返还、回收及再交接同门，不能从历史owner推定；执行输入变化仍新候选/必要验证及指定双新审，不承接旧Pass。

本回执与当前pure-table五路径WIP隔离：v2.ts/contract_v2.py/fixtures及两专属测试的冻结SHA、126TS/132Py、修后全check实际952TS/2628Py/44skip/exit0已记JSON；四拟接收文件零diff，不对该材料机制添启动实现。I06仍持preload/index、env、App、style四路径与私有模块；协议/resources/语义/旧tests/依赖/构建/CI及模型网关不随转移。未来新错误只按批准trusted opt-in3/local-startup-safe，不并入普通error2/3、不伪造never-ready事件、不增generic IPC或renderer profile开关。

**尚待独立核验、root全文读回与关键身份确认、执行状态/common明确生效登记及原owner通知。**三项未齐前继续遵守现owner；即使未来维护生效，startup/newcode/ready实际实施仍须root单独授权。本次仅接收过程，没有修改四文件、runtime/Goal/总控状态或运行GUI，无新增产品验证。
