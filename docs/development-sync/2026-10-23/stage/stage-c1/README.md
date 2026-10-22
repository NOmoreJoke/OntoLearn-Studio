# 阶段验收组合完整外审包

本目录准备两指定模型的同候选独立外审；**尚未派发，尚无指定双审通过**。仅复制固定交付、既有源码和现存证据，没有修改已经交给用户的browser/desktop包。

1. 先读 `candidate.json`、`payload-manifest.json` 和 `payload/scope.md`；执行 `python3 verify-freeze.py` 核对全部冻结文件。
2. 读取 `payload/guidance/AGENTS.current-de15.md` 与最新桌面操作政策。当前已撤回静默限制，可按总控资源协调使用桌面；历史README“优先后台”等只记录当时交付，不重新成为现行限制。
3. 由总控指定owner各创建一个全新完整任务：ZCode GLM-5.3 / 最高(max) / yolo；MiniMax M3.1-Flash / xhigh / bypassPermissions。提示分别为 `prompts/zcode.md`、`prompts/minimax.md`。两个任务读取同一payload，但不读取另一模型本轮报告。
4. 动态记录只写 `reports/zcode/` 或 `reports/minimax/`。该目录不属于冻结源码，创建任务和报告不改变候选身份。两任务的真实session/turn、模型/思考/权限读回、报告全文和终态须由实际owner另行记录。

`payload/artifacts/`含原验收壳、34固定组件、导出页面/manifest/verification、全部现存作者headless原件、原生构建metadata/脚本/日志及使用说明。`payload/independent-review/`保留内部审查报告、三P2及存在的独立原件。`payload/baseline-source/`为精确5f既有原生基线源码参照，完整Git树身份和导出列表另附；不是把基线通过转授给新增stage组合。

原生.app/ZIP约345MB/144MB不重复复制；`payload/external-artifacts.json`引用交付的实际绝对路径、ZIP hash与429文件/14符号链接清单。可运行 `python3 verify-freeze.py --external` 做只读外部产物核对。不要运行会写原目录的原build/probe脚本；必要执行只在模型专用scratch副本，见scope。

没有代码或验收变更，所以本次只做文件冻结/来源身份核对，没有重复运行原产品测试、浏览器、模型或原生GUI。最终验收入口仍是 `outputs/20261022_stage_acceptance/` 原交付。新发现须由作者在新候选修复，不能让审查模型在冻结树直接改实现。
