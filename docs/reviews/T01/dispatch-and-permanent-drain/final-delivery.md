# Dispatch / permanent drain 正式封存

固定产品 `7dfa9c8008727d469935181fc20beebb5ba4419a` 的R2独立定点审查通过。正式封存只新增过程证据，不改产品、不重跑无变化全套，不更新旧r1/r2受审输入。

## 候选、报告与原始验证

base为 `5f910b52c69d86a1076b2032e5d3c63e715947f3`；52项采用commit为 `e79d9d4f2e2fbdfe29217be5e4cc03f8bcce82e1`，原来源423b。产品历史04ed、过程4f270、修复cd506、最终产品7dfa及封存前过程009e全部保留。完整产品/test相对base仍54，唯一有效writer仍三项，51采用项继续逐字等423b，AGENTS保持15852B/78df且不stage。

唯一独审报告现25535B/SHA256 `8614f0d463d2fd089ff993250605547881612706a67b0ed30bcdabb969306b5e`，其中原14062B前缀/SHA `eec339c0d75b6877be39aee23918e9ca2bbe1e5068b6af93335fa3ab8ab3060d` 不变。受审 `review-input-r2.json` 的13输入继续绑定原报告前缀；追加后的完整报告另由本封存manifest绑定，不能倒改13输入成当时不存在的追加版。

原实际完整check `d5fb00/session9376→ede6da exit0`：1175 Vitest、2969 pytest通过、44既有skip，含50专项/新增8例；独立sources `e928ed exit0` 核12归档源。原独审真实131失败 `e4ca5b`、`09c1fe` 均exit1保留；修后独立原反例 `57fdd6 exit0`、额外峰值/恢复和三种取消反例 `acb720 exit0` 共4例通过。primary两对真实复核 `0a0ab7`、`745038` 均exit0也以原始response_item纳入。

## 两个可离线核对的原件包

`original-evidence.zip` 保存376条原始response_item、188对完整call/output，保留原始UTF8字节/LF，不重序列化。边界为：

| 独立角色/阶段 | 完整对数 | 原source一基行 |
| --- | ---: | --- |
| 作者真实实施R1/R2 | 121 | 539–1607 |
| 独审R1 | 37 | 1478–1743 |
| 独审R2 | 13 | 2014–2111 |
| 独审额外交接 | 7 | 2126–2169 |
| primary0a0ab7 | 1 | 11795–11798 |
| primary745038 | 1 | 11826–11829 |
| 作者封存准备，另标非产品执行 | 8 | 1625–1688 |

独审中间I05工具1759–1996完全排除；作者继承的C2工具及旧计划审查不冒充本次实施。索引逐条列真实绝对source、零基byteOffset、一基line、source response/tool ordinal、时间、callId、原长度/SHA及ZIP内offset；原list-block custom output保持原样。三个source各只用对应片段，巨大session_meta/reasoning/user消息不进包。

该包共231个member：7份分段工具原流、100份实际日志/脚本/运行原件、124份从保全PID JSON中按原UTF8记录取出的marker/ps/trace字节。派生提取明确标为原JSON字段的精确记录字节，不假称已删除的临时路径仍存在。首失败、后续实际终态、完整已存在的合并stdout/stderr日志全部按原件保留；工具原先返回的截断也照原样保留，不重建未返回尾部或分流标签。

`source-documents.zip` 保存172份实际原文：精确控制文件和保护AGENTS、506e固定计划包、423b采用52、最终54、旧三writer快照、旧过程Git blob、原13受审输入及当前追加报告。每项注明实际文件、固定Git blob或原报告前缀；缺路径不虚构文件。原文包和原件包分别由 `source-manifest.json` 与 `original-evidence-index.json` 逐member绑定。

## PID证据边界与后置门禁

P3原395861B/ebc0 JSON准确表示29个marker PID/29次成功定向ps，只有28份完整fixture argv，PID37879仅进程名(node)，另28个marker文件。它保持原字节；后续5个PID不倒补旧缺失。最终R2新8例原件为5个marker PID/5份完整fixture argv、3个marker文件、6份预算trace；最大总额130、control1。marker均为实际读到的完整行前缀，不声称每次最后IO全部捕获。controlled fake和reserve取消case只计机制，不计真实OS关闭证据。

封存读回逐条核raw source区间、line/ordinal/时间/hash、call-output配对，以及172原文与固定来源；提交前后另核三writer、54完整集合、51只读、原报告前缀与index范围。封存读取/打包/格式/提交等发生在上述原流捕获边界之后，不能伪称已在旧ZIP内；实际终态另记final manifest及仓库外Gitreceipt。Gitreceipt置外以避免commit/manifest自引用。

本交付仍不提供真实生产issuer/terminal producer、未知jobId完整发现、Store/worker/native/VFS/cohort released、首IO/全生产旁路、目标OS真人、指定双外审、CI、PR或合并证明；原唯一owner及父验收门保持。未运行GUI/Electron/native/模型/付费/打包或push/PR/merge。
