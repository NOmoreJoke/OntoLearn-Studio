# 作者验证与冻结范围

base 为 `5f910b52c69d86a1076b2032e5d3c63e715947f3`，分支为 `docs/I05-observation-projection-spec`。唯一作者只写两个本窗 docs 前缀；保护 `AGENTS.md` 为 15852B / SHA256 `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`，不 stage。精确 candidate ref 只在实际 commit 后由 process receipt 记录，不预填未来 ref。

`source-ledger.json` 记录全部固定输入/纯合同/获准限定行全文字节 hash。限制源只输出指定行；完整字节仅求 hash。额外获准 AST 引用保存为 `.json.raw`，逐 fragment 与固定 6891 字节/行/fragment SHA 核验，不 format 原件；`literal-excerpts.json` 是作者生成的限定行容器，其字符串内容保原行。

`preparation-errors.json` 保留作者两个实际 exit1 的 JSON 探索 KeyError、原 traceback 尾部和 tool chunk ID；第一项完整 stdout 在工具中被截断，故没有伪造完整原始流文件。第二项工具结果有实际 exit_code=1，不按惯例推测。它们发生于纯输入检查，不是产品错误；随后以字典键和逐项状态读取修正，不重写首次记录。外控窗口另记 root 编码/缺文件错误，责任与产品证据分开。

静态/纯模型证据只支持规范模型和所提交文件的一致性。`verification.json` 保存实际命令 argv、exit、输出文件 hash、有限身份核对结果。自测 20 个方法，包含手写 normal 边界、所有37项、尾项/额外字段/误拒/错误替代、typed/null/重复与全图 BNode 反例。不是 pytest、产品调用、真实库、source/package 或生产验证。

以下没有执行：产品、原业务 tests/probe/generator/helper、构建/业务 compile/archive 解码、第三方库/依赖安装/版本或能力探针、native/DB/GUI/网络/模型、发布/CI/两OS/真人/指定外审。没有来源权威、预算或运行身份可以由本 schema 关闭。当前 37 exact 目标是提案；旧实际分类与新增 API/serializer 均 pending，wholeOracleComplete=false。

`manifest.json` 列本候选两个前缀内的有限文件、bytes/SHA，明确排除自身以避免 self-hash 循环；process receipt 在候选实际 commit 后另加，亦不倒填候选 manifest。精确 base→candidate delta 只能含本两前缀。提交后读取固定 commit 对每个文件做 current=Git=SHA 核对，再交 root 指派 fresh reviewer。作者不自任最终审者，不在冻结审查期间改候选。
