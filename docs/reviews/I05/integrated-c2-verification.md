# I05 / B1 C2：修复、验收与来源

本次产品与测试受测提交为 `26eb632f0e1210b03ac3aef4cfd71fdc4a0c5222`，实际集成基线仍为 I04 PR5 `5f910b52c69d86a1076b2032e5d3c63e715947f3`。C1 双任务实际结束后才改动，原报告、错误结论、反例、所有终态和旧包证据保留。本文与证据封口不改变这份产品输入；正式候选 head 另由 candidate-2.json 固定。最新状态与剩余门禁只见 [status.md](status.md)。

## 实际修复

局部 Turtle parser/sink 对显式类型与裸数值使用输入词法，原规则仍按 RDF term 匹配。SHACL `sh:in` 的两方向真实误判均有完整正反预期；不同 term 的同数值不因本次修复被当成同一 term。statement 发射事件守卫补拒绝孤立数字/集合语句，保留合法重复三元组及带内部属性的空白节点；不是只比较 Graph 大小。

SPARQL 仅复制锁定 grammar 后改 numeric 构造与签号最长匹配。相邻 `-01` 是数值 token，`- 01` 是 Unary 运算；保留 Var parseAction、普通 FILTER/COUNT/DESC 和显式 typed literal。锁定 RDFLib 7.6.0 / pyparsing 3.3.3；结构不符合 gate 时走安全 INTERNAL，不伪装用户语法错误。没有修改全局 Literal 配置/parseAction/语法拓扑。正常库 parse cache 的更新不在“全局不变”的断言内。

普通 GRAPH 明确映射既有 `UNSUPPORTED_CONSTRUCT / sparqlForm`，嵌套 SERVICE 回归仍拒绝外联。语义与实施身份一起升为 finite-4；pyparsing 新增直接依赖声明，版本未升级。共享 suite 含10种数值身份的 SHACL、规则、BGP/VALUES、BIND/STR，以及4种非法 Turtle。完整逐项 C1 处理、延期原因和未做产品决定见 [意见处置](c1-disposition.md)。

## 本次已执行验收

| 实际检查                          | 本次结果与边界                                                                                                                                                                                                                      |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Mac 无窗口 `npm run check`        | 同一命令 lint/format/type/vitest/build/Ruff/pytest 通过：672 TS、1764 Python，Python81.14秒。                                                                                                                                       |
| `npm run verify:sources`          | 12份归档源通过；受保护 AGENTS 单独比对、不暂存。                                                                                                                                                                                    |
| Mac / Linux `npm run package:dir` | 两份新未签名目录包通过；Mac 不启动 Electron。                                                                                                                                                                                       |
| 两平台 `verify-i05-runtime.py`    | 完整共享 suite 源/包相等；每平台7项实际包内 stdio（原实际三能力路径＋新增6词法链），完整 Job/result/原始 payload/current-history 与 native 许可来源核验通过。                                                                       |
| 两平台 `verify-i04-package.py`    | 各17项真实 C4 包内回归通过；公共 canonical326/routing11/responses30/cursors9/joblist7/trusted41/rawframes51。                                                                                                                       |
| Linux 源码词法/执行               | 247项通过17.99秒，不将其当 Linux 全仓 check。                                                                                                                                                                                       |
| Mac / Linux 完整 `verify-i05.py`  | 两平台各自产生12条原 S1 口径与12条 fresh-process 记录，完整结果/摘要源包一致；每运行时28拒绝项；受控合成接收端正校准1次、拒绝0命中、入口 socket/DNS/urllib 尝试0，强制库 JSON-LD 路径在 urllib 层拒绝。新测量不继承旧 elapsed/RSS。 |
| Linux 新源码真实桥接/native       | 2项通过24.8秒；完整页/来源、真实请求拒绝、reload/显式取消，以及真实 crash/hang 对话与持久结果。                                                                                                                                     |
| Linux 新打包真实桥接/native       | 2项通过24.3秒，同样实际条件，未用源码窗口代替包。                                                                                                                                                                                   |

Mac 引擎 SHA `16a70c7ac72c95834f9d9b9e548734e1102968a21e9da0361692c5893a14611f`，引擎目录37,640,421 bytes，app561,710,329 bytes；Linux 引擎 SHA `32fb61edc773557a17c25362d72b65f64428a8f4fa489ac1e6a1ca9da061b222`，引擎目录43,876,255 bytes，app独立目录总计363,175,466 bytes。锁 SHA `86dfe82d952e2c88edcfc5658f488f6e1f0d04b4ec3b1e6f5c5d3bc4f57e8b73`。Mac400 / Linux409份实际引擎文件清单、资源、导入、动态链接及全锁依赖/native许可原件保留。

Linux 原始测量清单的 `appDirectoryBytes=0` 和 limits 文案“macOS”来自脚本旧的 Mac-only app 路径查找/硬编码说明。原件保持不变；平台、机器、真实引擎 SHA 来自其 Linux 实际探针，独立递归字节和说明在 `package-platform-correction.json`。0不是 Linux app 实数，也不据这些字段得出容量/生产结论。原生来源只匹配实际 Mac PBS3.12.12 与 Linux aarch64 CPython3.12.15/BUILD20261013，不宣称其他目标平台已核验。

## 隔离与完整原生结果

本线专用容器 `ontolearn-i05-isolated-20261021-v2` 无 host mount，独立源码、HOME/npm/uv缓存、依赖、fixture与输出；产品命令均 `docker exec -u node`。容器 CAP_SYS_ADMIN 只用于实际 Chromium sandbox，源/包 chrome-sandbox root:root4755；不使用 no-sandbox、隐藏窗口、禁用 hang monitor 或替身提示。

源码和包各在独立 Xvfb/Openbox 上生成3个可见窗口，第二窗口有外部 xdotool/XGetInputFocus 正面焦点。原生证据均 `events=[crashed,unresponsive]`、inspectorClosed=true、hangMonitorEnabled=true、noSandboxSwitch=false，两个实际 GTK 对话标题均为“OntoLearn Studio 窗口恢复”。每个窗口的完整 result metadata/rows、项目snapshot/revision、job/operation身份保持，真实慢 COUNT worker未自动重放/取消，最后显式取消得到 cancelled/null resultRef。fixture27事实与9模式×10的忙工作量、原时限没有变化；测量仍按S1的18/180，不混用原生负载。

独立最终证据核对发现默认list reporter没有落盘内存body型driver-log附件。原2×2通过和这一原件缺口均保留，随后只补源/包native各1项（20.1秒/20.2秒），相同源码/包/config/验收，命令额外启用list,json reporter。完整JSON报告及解码driver body逐字保全，本次stderr/stdout低于harness末65536字符上限；它们属于新一次运行，不能追称恢复了上一次内存日志。详见 `native-retention-supplement.json`。

26源码实际导出1159路径；203份全部执行输入在新构建/运行之后主机与容器逐字相同。完整导出压缩 SHA `0e39dba8d0cf3b266de30cfb8a1008a323625f55310fa04b85becefe061bd6ae`。文档随后封口不声称容器旧文档与最终过程材料整树相同。原checkout64保护源零变化；最新授权AGENTS78df保持dirty，操作指南变动独立登记。

## 独立审查与失败保全

两独立测试线保留 C1 红结果：183词法68失败/115通过；12真实运行链10失败/2通过。第三独立 agent 首份审查实际发现 P1 IB-1，初始 NotPass 报告 SHA `b27b6850802b15eae1de8369e4d7ae26e467c791af501808ce789021c704ff5f`。修复后独立固定26导出/环境运行488相关回归18.54秒、自建冷/热134矩阵、10条真实 Store/worker/source stdio签号查询全载荷认证链通过；补审 SHA `8d27233752d68827eb125229c7b20a78676f0ecb2fda7eeb1094b871b646392b`，在C2变更范围内Pass/IB-1关闭。该 agent 未运行主线全仓检查、包/native或外部双审；读回证据不冒充独立实跑。

保留原绑定错误环境失败、两种错误 flatten 原型、Var 丢动作导致 FILTER/COUNT/DESC 回归，以及最终修复；也保留 pre-orphan/pre-signed 的先前检查/包身份和测量，均标 superseded。所有旧报告/错误结论不覆写为通过。源代码原探针以 `.py.raw` 保留，避免被格式器改写；`originalExecutedPath` 映射继续可追溯。

原始日志、完整测量/原始结果、native全载荷、独立反例和历史报告版本以 [C2 可恢复证据清单](evidence/integrated-c2/manifest.json) 对应的无损归档保全，逐成员 bytes/SHA 与归档 SHA 另列。因当前尚无本轮 CI artifact，保留完整反例和运行载荷用于离线重审；不提交二进制app、依赖缓存、SQLite/DB/WAL、密钥或真实业务数据。解压后逐成员可恢复原字节；忽略目录里的数据库仅是本地合成fixture，未进入归档。

最终独立原件审计已全文读回并保全为 [独立证据审计原文](evidence/integrated-c2/c2-final-evidence-audit.md.raw)，SHA `7c8b1f5f6bc0692177c62c32e2d338e44d0f4d2b642b8e4778441435d1f1718c`。258归档成员、嵌套1159源码、203执行输入、64保护源、新JSON driver body均由该agent实际重读核对；不冒称其进入Docker或重跑产品。其v1关于最终post时间先后的一句误述及原报告c948…完整保留，最终版精确更正post晚于两补采集。

## 已知范围和待决项

锁定 Turtle 对部分前导分号语法仍宽松，孤立语句修复不是完整Turtle一致性认证；RAND与SERVICE等混合不支持组合可能先返回unsupported，仍执行前拒绝/零外联，不承诺所有组合的错误优先级。上述是独立审查披露的既有边界，后续不可据词法修复宣称完整标准兼容。

Q6十二项仍逐行等待负责人采用/修订/淘汰，FR-505比较与同条多结论未实现；后续T05提案不计作本版能力。Z-4/5/6/7与L-3延期依据见处置；未删历史/资源来掩盖增长，也未修改已移交的T01/T03/I06文件。Mac/Windows本版native、签名/干净设备、首发平台、生产或容量阈值均未由本次结果证明。最终同候选指定双新审、真实CI、正常合并与远端核验仍是原Goal门禁。
