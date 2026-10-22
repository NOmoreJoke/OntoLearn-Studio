# T04-S1 完整 diff 文本的当前复现参数补充

2026-10-22。给 ZCode、MiniMax 两方同一份操作补充；随各自已冻结完整新正文提供，不替代或修改原正文、manifest、产品与验收。总控派发预检已确认准备条件满足；本项为非阻断 P3，不新增产品门禁或代码重审。

## 当前可精确复现的命令

在本方实际 detached review 工作树读取固定 Git 对象：

```sh
git diff --abbrev=7 5f910b52c69d86a1076b2032e5d3c63e715947f3 554ec89844ae5e8efcc4ac0d4f7e21d955a4b6a6
```

同样显式加上 `--binary` 也得到相同文本：

```sh
git diff --binary --abbrev=7 5f910b52c69d86a1076b2032e5d3c63e715947f3 554ec89844ae5e8efcc4ac0d4f7e21d955a4b6a6
```

本次在开发树及两个实际 review 树分别真实运行以上两命令，均 exit 0，输出 **170428 字节**，SHA-256 **`777ef6d58b8697530024ad4c47110443b613b9ba7de37d8420fae97e44b6c651`**，复现原声明。

本次另实测显式 `--abbrev=8` 和当前不带 `--abbrev` 的 `git diff --binary <同一 base> <同一 product>`，均 exit 0，输出 **170494 字节**，SHA-256 **`9a96fcead3817efb9ebdc33d7277d11cb6186fc6013e80171484d56fb7705c9c`**。本次默认输出与显式 8 位相同；不要假定未来 Git 的隐含默认永远不变，也不要改 Git 配置来凑文本摘要。

这些是**当前实际复现参数**。旧输入记录的历史 argv 没有 `--abbrev`，继续原样保留；本补充不声称当时显式使用了 `--abbrev=7`，不倒写历史命令或覆盖旧哈希。

## 源码身份与解释边界

差异只在 diff 的 `index` 对象名缩写文本，不能据此误报源码漂移、文件遗漏或验收变化。实际完整 33 路径集合、固定 product 的全部 blob 字节数/SHA-256 仍与原 manifest 相同；本次已在三树分别读回核实，源/tests/fixtures/SSR 未改。完整 blob 清单及本次逐命令完整 argv/cwd/起止/真实退出/输出大小/hash 在同目录 `actual-reproduction.json`，原 source manifest 与映射保持不变。

审查仍应核本方实际工作树/base/product、原完整范围和 33 项原件；本补充不授权跳过源身份核验，也不能用文本缩写解释真正 blob 不同。必要普通验证、源码只读、独占产物及禁限研究仍按原当前执行补充，不因本 P3 扩大或收缩。

总控根预检原件：`iteration-control/2026-10-21-weekly-release/.private/T04-controller-dispatch-preflight-audit-20261022.md`，5621 字节，SHA `0517537529f1211fcbd7f26ea0c830f2f25f8b861e5672251f5bd2431feb129d`。这是准备静态预检，不是两指定任务或通过。当前本线两指定任务仍为 0，未取得新 GUI 窗口，不启动外审、不占用 T05 的窗口、不参与账号 reset。
