# raw stdout 存储保全独立补充审查

2026-10-22。结论：新增第四条精确 `-text` 规则及对应 raw stdout 的当前暂存字节可接收；base64 双流可恢复回执声明的原字节。全量 whitespace 仍为 exit 2，只有排除明确 36 项原始证据后的 scope 回执为 exit 0。本审不签全量 whitespace 通过，也不签新的构建或全量 manifest。

## 指定原件与属性

本目录 `.gitattributes` 当前 working/index 完全相同：169B，SHA-256 `3c261faf49e57b04eb6654e259ba0810eef679d83b8ba1f7ad223590cc493e2d`。相对此前三条精确 fixture 规则，仅追加 `whitespace-preserved-full.stdout -text`；无通配规则。该 raw 输出的 cached text 属性为 unset。

`whitespace-preserved-full.stdout` working/index 逐字节一致，均 6174B、SHA-256 `1ed1bbf5524863aced6fe9a955c5252aa5e68d73a888170d8e3f658863b09435`，含六个 CRLF。三份原 CRLF fixture 的 working/index 仍各 271B／`0d0adbc839c29591f7041a3b80154ca87652486bbf7698b50c06a6e6b11bea48`、两个 CRLF，未被此次修复改变。

`raw-stream-normalization-stage-failure.json` 为 939B／`5226745f3854b881d7c2ded59be9066490f2bcf78fbdde1eb1cdbf5bb9d20763`。它明确保留未提交候选的 316 项核对中这一项 mismatch：原 working 6174B，旧 index 6168B／`29843c6ca816497e6e873e9277d0293328571448dc0d207763356e46c8af52b6`，并指向旧 manifest `335a0b0c77abff6618051b5bea5217aeadc945e6c028091e36d520490269e193`。本次不重新检查 316 项或覆盖旧快照；新的最终 manifest 应另存。

## base64 双流及例外回执

已完整读取 `whitespace-final-scope-validation.json`：10435B／`2a51efd7693dbe932024067a2ebe4bbe5c89add446a9bdb22dc31b8a2ba77cc0`。本次仅读取和解码保存的双流，不重新执行 Git whitespace 检查。

- stdout base64 文件为 10437B／`5f5233a698ee73dcf711207963d1b58884d83230836dfeaba6bf35bd7e8b2d46`；仅去编码文本的 CR/LF 后严格解码并核 canonical base64，得到 7826B／`786b8c59677f45d66f7d96e7fd49544723ec792ded4e2b409e453599e5531a62`，与回执相同。
- stderr base64 为 0B；解码亦 0B，SHA-256 均 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`。

回执含 36 个不重复的精确原件路径，ordinary scope argv 的全部 exclude 路径与这 36 项逐项同序相等，未见泛化排除。解码 stdout 中 44 个路径／行号诊断对应的唯一 36 路径，集合恰等于例外表；没有表外诊断。例外是保存原字节的错误输出、故意异常行尾 fixture 及包含其原行的 raw checker stdout，不应 trim。回执的 full exit 2 与 ordinary filtered scope exit 0 分别保留；后者不能改写前者。

## 范围与保留

只读 Git diff 显示三 writer 相对 95f07d931eeffd3bdcd52cb21e9fa2d8a1db12bd 无差异。此前 10643B 原报告、3973B 账界补充及 3121B CRLF 补充均核原摘要不变；本文件是另外新增的补充。

本次仅核小型属性、raw／base64 字节、JSON 回执及 Git index 身份，未读取供应实体或大 metadata，未重跑用例、mapping、driver、探针、configure、编译或测试。最终全量 manifest／提交身份由后续新原件单独固定；本审没有增加任何第二次运行授权。
