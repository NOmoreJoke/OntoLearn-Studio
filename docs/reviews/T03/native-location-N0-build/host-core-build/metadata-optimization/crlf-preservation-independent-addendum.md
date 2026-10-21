# CRLF 过程原件保全独立补充审查

2026-10-22。结论：指定三份 CRLF 负例的当前工作区与 Git index 已逐字节核同原 271B 身份；新增局部 `.gitattributes` 仅对这三个精确相对路径设置 `-text`，可接收为原件身份保全修复。本结论限定当前暂存候选，不宣称已经形成新的提交或最终全量 manifest。

## 独立读取与结果

本次只读 `.gitattributes`、三份 tiny fixture 的工作字节／index blob／d0403efcb3a01c00d6d05edabb7a56587d0040d5 blob，以及小型首失败与 whitespace 记录；使用 Git 只读差异和属性查询，没有运行用例或产品脚本。

相对上述 d040 提交，指定四路径恰为新增 `.gitattributes` 加三份 fixture 修改。属性文件工作区与 index 均为 130B，SHA-256 `bb9e955857b7dcb19702b17d87328b9be676b9a4b803c1dd003c532d8dc51431`，完整规则为：

```gitattributes
fixtures/crlf.records.jsonl -text
validation-v2/fixtures/crlf.records.jsonl -text
validation-v3/fixtures/crlf.records.jsonl -text
```

没有通配符或根／全局配置指令；`git check-attr --cached text` 对三路径均返回 unset。本审不重查全局配置。

这三份文件分别是本目录的 `fixtures/crlf.records.jsonl`、`validation-v2/fixtures/crlf.records.jsonl`、`validation-v3/fixtures/crlf.records.jsonl`。每份当前 working/index 均 271B、SHA-256 `0d0adbc839c29591f7041a3b80154ca87652486bbf7698b50c06a6e6b11bea48`，working 与 index 完全相等，且均含两个 CRLF。三份旧提交 blob 均为 269B、SHA-256 `530b2e73f5a22f6aecfb3114e751e7d34b36f7285cf902fa74b4e21fbe5f7a25`；与首失败记录的行尾归一化差异一致。

`git-normalization-first-failure.json` 为 1753B、SHA-256 `662c90b3ab4a716f065359fb120afc281d12329f6074927c27a30d29f13469d0`，明确保存 305 项检查中三项 mismatch、旧 Git blob 身份及工作原件仍在。本次独立核这三项，没有重新读取其余 302 项，不能据此写成新一轮 305 项全量独审。历史失败及旧 manifest 应继续保留，后续完整 manifest 另存。

## 现有验证边界保持

三 writer 相对 95f07d931eeffd3bdcd52cb21e9fa2d8a1db12bd 的只读 Git diff 无路径。原 `independent-review.md` 仍为 10643B／`f016b32259cab6404f441a15c9a6816d0fe0fd553bc59a7b06903175a99baa84`；此前账界补充仍为 3973B／`a3f85301b6cb973416e66a5f89df4c4b6f5eb3948c584d57d9edf6a88d3dcd66`，均未修改。

已读取 `whitespace-first-check.json` 的原 `git diff 95… d040… --check` 回执：exit 2，未签全量 whitespace 通过。其 stdout 4507B／`4fae3b0ce67b74e4bbe09caeb83e7e0e0fd3607b7b10a1e25b0ce8a1c3114a31` 保存尾空行诊断，stderr 为 0B。错误诊断输出及故意多空行负例属于需按原字节保留的证据，本修复不以 trim 改造这些原件，也未重跑 whitespace 检查。

没有重新解析映射、读取大 metadata／供应实体、hash SDK／cache，或运行 Node 用例、driver、探针、configure、编译、测试。本补充仅确认过程原件在当前 index 中恢复，未增加第二次构建或其他运行权限。
