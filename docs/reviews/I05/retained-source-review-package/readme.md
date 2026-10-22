# I05 完整保留源码首包（尚未派发指定外审）

主受审候选为批准base `5f910b52c69d86a1076b2032e5d3c63e715947f3` → source-only `2cf0c3328de464e15a3fa9cdbfdf6aa88d0b4a64`，最终交付过程 `61f53dbe76262f5003065900a4e97d9a6130014b`。该包为完整工程源码审查准备；没有产品运行、完整业务、指定双Pass、父I05或上线结论。

唯一备包树：/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-retained-source-review-package
分支：docs/I05-retained-source-review-package
唯一写面：docs/reviews/I05/retained-source-review-package/。原2cf、原supplier及其它树均只读。主AGENTS当前外部全文适用，历史archive里的AGENTS原字节保留，不倒改冻结输入；树副本由政策owner传播且不stage。

## 读包顺序

1. current-policy-addendum.md 与 guidance/AGENTS-current.md / developer-common-instructions-current.md / desktop-operation-policy-20261022.md / external-review-permissions-current.md。
2. input-manifest.json、author-validation.json、coverage-matrix.md＋json，逐成员检查 frozen-inputs.tar.gz；相同Git blob以tar hardlink去重，全部快照在独立namespace，不能编辑解包hardlink或把版本拼成一棵产品树。
3. 主快照 snapshots/main-source-only/ 是2cf全部Git树；snapshots/main-completion-process/ 是61f相对2cf六个过程delta。candidate.patch.json 是base→2cf完整binary/full-index差异的lossless base64，不排除测试、配置、docs、原始失败。
4. reference命名空间保存每个旧固定产品及final process整树，包含原测试、fixture、原验收、首Fail、原始证据；只是独立参考候选，不声称全部已采用进2cf。
5. 两个完整独立prompt分别是 zcode-glm53-input.md / minimax-m31flash-input.md；dispatch-requirements.json 只给计划设置和读回项目，真实任务数仍0，不能用文件名/关联标签充任务ID。

## 覆盖与保留版本

2cf只采用6891的22 immutable模块；未覆盖其整个工程：按B→6891 delta有11个其它shared/desktop源码版本不同、13源码路径缺失（其中11为T01 project族、另profile_probe与samples）；47旧测试缺失、1个task-runtime测试版本不同，27fixture缺失。24个缺失测试属于I05/quality；其余23缺失与改变测试属于T01。不存在的旧源码和测试不能由新70函数测试代替。

主包新增probe、generator、newtest和两资产是独立新审范围。C4的worker/protocol/bridge/native/e2e/harness/CI/lock与后继T01供方都有不同版本，完整snapshot和reference diff各自固定，不盲拼。C4五十三件许可原件也不在2cf；保留于C4参考namespace，不把旧许可存在解释为新bundle许可验证。

148路径×8phase的实际same/changed/missing与211unique blob独立SHA256在coverage JSON；完整快照另外覆盖该delta表统计之外的docs/许可/同base上下文。未跟踪calculation/lexical/restore-tests只保opaque路径/bytes/SHA，尚非冻结候选，待原owner决定采用或撤回，不执行或抄入产品。

## 完整工程可先审，未证运行必须准确判定

源码可读与验证可执行范围分离。允许只读固定源码、完整需求、原始历史证据及Git/hash/JSON/tar纯结构检查；本备包及拟派审任务没有产品import、pytest/npm/check/build/package、417实际运行、DB、native/GUI、安装、网络或HOLD项目执行许可。不得借“full access”扩大本轮运行边界。

主source-only R1两P2一P3的Fail与R2限定静态Pass保留。R2不是指定审查、不是runtime/产品Pass。C1真实双审最终ZCode条件Pass、MiniMax NotPass，native UUID未暴露，关联标签不是ID；C2/C3/C4的记录为0新任务，不能继承C1曾短暂Pass。历史C4已退出当前release候选，但原保留代码必须明确纳入参考审或另包，不能凭祖先/日期自动撤回。

未取得T03供应锁/writer组合、八distribution验证、runtime/package同selector、完整417独立oracle、loader/cache代码指纹、whole-H、S1 snapshotLoad/SQLite损坏输入HOLD、真实Job/Store/worker/selected、目标两OS/真人/CI/develop远端等。审者必须按原验收逐项标not executed/无法验证/NotPass；不得删除验收、改golden或将历史actual反推独立expected。必要运行未证使完整验收无法通过时，应明确NotPass或无法完成验证，不能自己放宽门禁出Pass。

## 后继审查单元

- A：本次2cf完整源码与61f过程首包。审查主工程全部diff、22supplier、probe/generator/newtests/资产、来源和缺证；直接使用固定原件。supplier日期版本的24个I05测试及其27fixture单列reference，静态审清它们与主candidate的关系，不复制进主产品冒采用。
- B：6891/f79完整supplier工程参考包。它保存生产/恢复/DAG/整数/date所有测试与供方上下文；共享T01版本须由T01原owner的精确候选接手审查，不作为2cf已采用依赖。可与A审查同时静态读取；整体产品验收待正式组合。
- C：523旧C4保留集成参考包，包含semantic_probe/samples、worker/protocol/bridge/native/harness/CI/许可。其作为当前release已撤回，不重开旧产品release；其中仍保留而未被A/B逐字节覆盖的工程范围须独立完整审清，不能冒最新runtime。
- D：0475、3ef/4be、6c1/2d5、8e8/fb99、shape3bd/43d、integer91e/ec85等旧变体，完整ref和逐文件改写关系已保留。旧实现被最终代码修订的部分按根closure作为历史问题追踪；未明确撤回的旧工具/源码/测试进入B/C或独立后继队列。仅不同字节不足以宣称撤回。
- E：未冻结WIP及fee/projection/D2纯方案是独立owner/独立窗口。本包没有读取fee/D2 WIP或将源码actual作为其规范来源；待其各自固定后另包，不在本包下冒指定Pass。

## 验证与冻结

author-build.py仅纯Git/stdlib打包器，author-command-log.json保存实际argv/cwd/exit/分离双流：stdout以lossless gzip artifact保存、stderr以base64保存。bootstrap只读盘点的早期工具输出没有回造split流。author-validation只核全部tar member bytes/SHA/ref和JSON/diff编码，不是产品测试。

input-manifest自项排除，后续candidate Git提交绑定其最终字节；独立agent文档/包结构复核和指定应用实际任务仍待root接手。没有创建Goal、模型任务、外部消息、push/PR/merge。

补充：初次Prettier受仓库ignore影响，exit0不能证明覆盖；原输出保留。后续text-correction-proof.json的显式 --ignore-path /dev/null 才是新作者文件格式检查。原author-build.py、author-finish-first.py作为首次失败作者器保留EOF，不清洗；完整base→packet whitespace仍保留其两项例外，另给精确排除两件后的检查，不称全量绿。
