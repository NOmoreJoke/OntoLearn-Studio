# T10 独立内审与处置

只读审查 agent：`/root/t10_private_review`。实际创建后审查本线完整私有实现、单测/fixture、说明及 `render-probe.mjs`。没有修改文件、启动 GUI、读取凭据或重复全仓检查。此内审不替代指定双模型新任务。

## 发现和修复

1. P2：原检查仅覆盖 ZIP 中央目录，可隐藏不在目录中的 Agent 会话本地成员或任意前缀。改为本地 header 从偏移零连续覆盖到中央目录，严格对照路径、大小、CRC、flags 和压缩方法。进一步检查 raw-deflate 的终止、剩余输入、真实长度与 CRC，拒绝压缩尾随数据及声明大小截断的额外输出。补隐藏成员/前缀/header 冲突/加密/流式 descriptor/deflate 尾部/截断输出反例。
2. P2：原数组 spread 执行 getter 并可能原样抛出敏感异常。改用数据描述符，拒绝自定义原型和缺少自有索引的数组，入口异常统一固定错误。补自有 getter、继承 getter及稀疏数组反例，确认未执行 getter。

复核 agent 实际定向运行上述 ZIP 4 项测试及预算/访问器测试，全部通过，明确两项及延伸问题已关闭、私有候选未发现新阻断。其结论只适用于私有准备范围。完整包选择项分离、报告栏目/纯文本编码与逐 attempt 分类已检查，正式迁移、真实学习与 G.6 仍未验收。

## 最终读回的实现哈希

| 文件 | SHA256 |
| --- | --- |
| transfer/inspection.py | `c64ea0f0cb766545080fe1e9346c97370eca3ee8eaedb98fdfd0e7f2d141e6e8` |
| renderer/src/transfer/report.ts | `e6076bb91d407c6474a65e69cba756d39133070250fca23a3ba420cc76bd079d` |
| docs/iterations/T10/render-probe.mjs | `dcccc5b9bf080310141c8a28e0341eed05044e6f4bfea0421180aebd79cc8807` |

原初审文件哈希：inspection `cb4c4e3e08337c8a2bfc5c788e2de44d5d14617e837f8dfb48d3b097d21ac940`；report `dcde9ec326df19b9148b0872a132712b13a6c371c13b6474c6cff6140bfd2262`。审查时基线 HEAD 为 `5f910b52c69d86a1076b2032e5d3c63e715947f3`，实现尚未提交；本线随后形成恢复提交，不能把基线 HEAD 当受审实现 SHA。
