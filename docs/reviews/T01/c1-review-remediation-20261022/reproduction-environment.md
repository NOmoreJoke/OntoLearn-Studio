# C1 后续候选复跑环境

本说明处理 M P2-03/P2-04 的复跑前置。原报告、首失败和导出包保持原样；以下是后续候选的实际环境，不把旧失败改成通过。

## 使用真实 Git worktree

本轮工作树为 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-c1-remediation-20261022`，分支 `fix/T01-c1-remediation-20261022`，起点为受审 HEAD `c0b61fd245c1b3bd2a84e488f00a742a1942fd8c`；批准 base 仍是 `5f910b52c69d86a1076b2032e5d3c63e715947f3`。旧产品 `423b7e4c799f188cf2ce6e8e7121893ce85624cd` 及其两份外审工作树不修改。

完整 pytest 包含调用 `git show` 读取固定旧 reader 的兼容用例。运行前须确认当前目录确为 Git worktree，并能读取 `a816c2d0`、`5f910b5` 的原始源码与静态资源。`git archive` 导出目录不含 `.git`，不能直接当作这些用例的自足执行环境。发审时给每方独立 detached worktree 或包含所需提交的完整 Git bundle/clone；不通过 skip、过滤测试或改旧 reader 来源来绕过。

## 各树独立安装依赖

在上述工作树根目录执行：

```sh
npm ci
uv sync --frozen
```

测试中的 `.venv/bin/python` 必须存在，且 editable 安装指向该树的 `packages/engine/src`。不得把他树 `.venv` 的符号链接当作本树独立环境；`node_modules`、Python 环境、构建输出、cache、pytest basetemp 与临时运行库分别隔离。

本轮环境脚本、真实 argv/cwd/起止时间、独立 exit 与双流保存在工作区外 `outputs/20261022_review_backlog/T01-C1-remediation-20261022/`。其中 `raw/environment-npm/`、`raw/environment-uv/` 记录实际安装均 exit 0；这只证明依赖安装，不是产品测试通过。

## 结果记账

`npm run check` 以整条命令的退出码为准。独立 pytest 通过不能覆盖先前 check 的 exit 1；分步骤绿不能拼成一条未成功结束的合成命令。初次反例失败与后次通过分别保留，缺失的历史脚本版本或原始 exit 不回填。M 报告关于 a33 完整 check 的矛盾和首次反例披露缺口，见本轮意见处置矩阵及原报告。

真实 e2e、原生恢复和 GUI 使用由总控协调独占资源，另行记录实际命令、可见行为与覆盖边界；不能用构建、health 测试或单元测试替代。CI 在双方对最终同版候选明确通过后，经正常 push/PR 触发，以实际远端结果记账。
