# 原始证据空白保留

第一次完整 staged `git diff --check` 实际 exit 2，报告的文件仅 `old-red.stdout.txt` 和 `product-two-paths.patch`：前者为 pytest 原始终端分隔/错误位置尾空白，后者为 Git 原生 patch 的空行上下文。授权要求保留真实旧红/补丁原件，因此不格式化两者。诊断原输出 `staged-diff-check.stdout.txt` 也原样保留，其中嵌套复现这些尾空白。

最后 scoped 检查仅排除此三份确切 raw 文件，其余新增文档/JSON/收据均纳入；产品两路径单独 diff-check exit 0。不得将 scoped 通过表述为完整 raw diff-check 通过。收据及 raw 输出保留首次失败与原因，没有修改或隐藏。
