# 静态核验记录

2026-10-22。cwd 为本次新 docs worktree；只运行普通Git与stdlib资料审查脚本。未借用任何旧树的环境、node_modules或T03计量预算。

## 已实际执行

1. 全文读取本次窗口、root限定closure、固定合同§5.1–5.4、对应static-import-closure与packaging-resource-investigation。全文读取固定checker901行、resources97行及相关offline模块；三JSON完整stdlib解析。输入17件595764 B及其原bytes/SHA均已保存。
2. `python3 -X utf8 docs/reviews/T01/i05-semantic-resource-offer/static_audit.py`：实际exit0。仅对Git原文做AST、JSON唯一键／ref／catalog／基线差异及hash比较；产物 `static-audit.json` 88434 B，SHA256 `ca6d87574368b12139f4846d9f79a317cd2695244df45ffc4b92a68a05e7d375`。22模块、128 literal边、607 ref目标和26普通error分支核同。不调用supplier模块或函数。
3. `python3 -X utf8 docs/reviews/T01/i05-semantic-resource-offer/top_level_audit.py`：实际exit0。23件（22模块加checker）的lexical顶层调用表，包含条件分支／class body／decorator／default，跳过函数和lambda body；不解析第三方import的副作用、不声称完整运行导入或whole-H证明。产物 `top-level-static.json` 29376 B，SHA256 `4a31479b89016b196963aeae443703df1cd1aa710f97e798f02b2363f31930cc`。
4. 查可用formatter：本树 `node_modules/.bin/prettier`不存在，PATH中无prettier。未执行npx安装、未连接共享可变依赖或借旧树环境；因此没有Prettier通过结论。窗口允许使用可用固定formatter，但本地没有这个条件。将另做stdlib UTF8/JSON/末换行/尾空白及Git whitespace静态核验，实际结果由候选清单和交付记录报告。

## 未执行与未证明

未import checker/引擎或执行其任何函数；未运行产品、tests、probe、DB/SQL、native、业务子进程、构建、包内/路径/单实例/性能测试、GUI或指定外部模型。静态脚本使用git子进程读取固定文本，不能误写为完全没有任何子进程。JSON数据比较不是JSON Schema validator运行，也不能替代T03实际bundle/lock/distribution/license或source-package联验。

原候选4064b21形成时，主线尚无检查失败记录；后续root格式检查、R1不通过及主线修复阶段的失败均在下节与原日志保留。此前SQLite/heap/OS拒绝线仍停止，本次未尝试，不以格式修正覆盖这些边界。

## R1之后：root精确授权现有formatter与格式修复

总控对原4064b21的只读检查实际exit1，三件为主offer、dispositions.json、static-audit.json；独审R1最终因此不通过，原9884 B报告SHA `687227d50bfd9a386ec3db8fcc4559c839c0b08222193e6665dfb927d48a107c`已全文读回，未改写。早先“本地没有可获准formatter”的记载保留为原时点事实。随后总控明确授权现有 `/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio/node_modules/.bin/prettier`，实读package为3.9.10，bin/prettier.cjs为2628 B／`6e922134a3c76fd4de202959bb6aef50bde0c994148075003a15569b7197906e`；本次只将它当文档格式工具，不作业务依赖，不安装或修改工具。

主线等R1完成后才修改候选。`format/01-before` 原命令exit1、`02-write` exit0，但仓库.prettierignore忽略docs/reviews，故它们实际只检查／写主文，没有把JSON遗漏包装成通过。随后显式 `--ignore-path /dev/null` 加三件绝对路径：`04-explicit-check`实际exit1，余下两JSON告警；`05-explicit-write`实际exit0，三文件逐项均进入工具。所有实际argv/cwd/exit及纯stdout/stderr原bytes/hash均在format目录，原日志未覆盖。

首次等价性检查的外层inline Python实际exit1：比较式错误地要求Markdown表格分隔行的连字符数量不变，而Prettier会扩展该分隔行。没有因此判定或宣称正文不同。原失败另存03记录；修正检查只排除纯表格分隔行，再核全部非空白字符及所有inline-code原文相等，并直接读实际Git diff。两件JSON独立核解析后deep equality。这里的脚本判断失败不是产品、自动审批或资源门失败。

原三件及原manifest/verification保存于history/4064b21-format-inputs，仍可由原Git恢复。格式后主文10465 B／`d62791067bdcc73e8aa5755336ceda02611c61df7fdc3063df6437f77215cd0a`，dispositions1691 B／`caa0baf7d3668fd58222a87dfcedf514655fab448c787157ed7aa3ffaa25ef21`，static-audit88332 B／`b082f3ee65521a69611f800b3a6b4bd86755a9416d44f28d5fcf53f2007db87f`。此前§2的88434 B/hash是原脚本实际输出，原数据未重跑；重现顺序为原静态脚本后显式formatter，不能把纯格式差当新产品核验。format/semantic-equivalence.json绑定前后身份与比较域。

未对.raw或历史独审做批量格式化。新清单与当前新增文档将显式检查后冻结；后继独立delta复审应核纯格式、清单和原采用决定不变，再给新结论，不能覆盖R1不通过。
