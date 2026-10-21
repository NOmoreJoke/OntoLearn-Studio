# I05 / B1 C4：RDF 字符串身份修复与验收

产品源 `1a79731091e671c497824c94e12dae34a4e8609b`，完整回归头 `40c18ea1b9ce4fef9a5235718fd7e622e2d06cc4`；本次 fetch 后实际 develop 仍为 `5f910b52c69d86a1076b2032e5d3c63e715947f3`。当前完成度和门禁只维护于 [status.md](status.md)。原 C3 冻结、12 个真实错误结果、两平台旧包和全部不利记录均保留。

## 修复和责任

根授权 [原件](c4-string-repair-authorization/I05-string-term-repair-authorization.md.raw) SHA `88f9116c…`，只允许七个语义源路径及直接回归。`semantic_turtle.canonical_string` 是唯一字符串转换：无语言且 datatype 为 XSD.string 时，以同 lexical 的 plain 内部形式表示同一个 RDF term；保持 normalize=False，numeric/date/lang 不变。私有 Graph 副本、Rule when/head、shape/list、查询常量及运行时字符串构造、selected 的规则/源 hash 共用该身份。原 Graph、Rule、raw 定义和既存结果不被改写。

查询只包装每次私有 Expr 的原 bound callback 返回值，保留 Expr.eval 的错误传播和 ctx 清理；遍历 VALUES 的普通 dict，先复制 OPTIONAL 使用的全局 TrueFilter。原语法/能力 guard 和数字词法 grammar 保留，局部适配不变量失败仍为内部错误。严格 `_term` 先验证原始 N3 等于原文，再转成共享身份，合法 typed string 不被误拒，注入门不放宽。语义与 implementation 同步为 `i05-finite-6`。

实际产品差异恰为授权七源＋三份直接测试；原 204 执行输入中不属本次修复的195份保持原字节。worker 已唯一归 T01，Store/coordinator/canonical、锁/依赖/build/CI、桌面路径未改。没有引入 T05 比较政策、多 head、D3/D4 或 Q6 默认答案。

## 实际验证

| 验证 | 本版实测 |
| --- | --- |
| Mac 无窗口完整 check | 672 TS、1847 Python（80.09秒），lint/格式/类型/build/Ruff 全部通过。 |
| 来源和固定输入 | sources12；205执行输入主机/容器一致且全验收后未变；原 checkout64保护源不变，AGENTS78df保持dirty/不stage。 |
| 独立新回归 | 原63项在固定3289为40失败/23通过；新增隔离10项旧版2失败/8通过；固定838导出的73项全通过。838→1a仅格式变化。主完整1847含全部73项。 |
| 两平台实际新目录包 | Mac/Linux构建 exit0；每个平台完整新 suite 源包一致，各7项真实stdio＋17项C4协议回归通过。 |
| 包内实际代码 | 分别读取实际 CArchive/PYZ，七模块 code object 与固定1a源码编译结果逐项相等；同时实际执行新增 stringIdentity suite 和下述stdio，不用打印版本替代语义验证。 |
| 完整 B1 | 每平台12原口径＋12 fresh-process记录；完整结果源包相等。每运行时28拒绝，接收端正校准1、拒绝命中0，入口 socket/DNS/urllib尝试0，库级 JSON-LD backstop拒绝。 |
| Linux 受影响源码 | 最终360项通过9.32秒；不是Linux全仓check。 |
| Linux 新源码/打包 native | 各2项通过，Playwright报告耗时24.98/25.08秒；首次即完整list,json报告。真实crash/unresponsive、外部可见窗口/焦点和GTK提示、慢任务显式cancel均通过。 |

原生只在无host mount的独立 `ontolearn-i05-isolated-20261021-v2`，产品命令以node运行、独立Xvfb/Openbox，真实Chromium sandbox配置；没有Mac Electron/e2e/native/HMR、隐藏窗口、关闭hang monitor或stub提示。三个窗口时点完整结果相同，Node实际重算 JSON.stringify SHA 与各原记录一致；完整driver body已从报告base64解码保留。负载和时限仍为原验收值，未改成较小fixture。

Mac引擎 SHA `fd4b5ab3ca97334c81a4363bb1c9141bf1db9ebbeaf1f555e456b47510e4841f`，引擎37,648,261 bytes/400文件，app561,718,169 bytes。Linux引擎 SHA `184c8542aaf8c189f980ad35984db5734b769f3a386895619cc8f5563e4cbdcc`，引擎43,884,087 bytes/409文件，app实际363,183,298 bytes。原Linux测量脚本的Mac-only路径仍输出appBytes0，保留原值，旁附独立目录求和校正，不将0当作Linux实数。锁86dfe82d…未变；原生许可仅匹配实际Mac PBS3.12.12及Linux aarch64 CPython3.12.15/BUILD20261013。OS缓存未控制，不量化性能提升或宣布容量通过。

## 真实包内旧红新绿

独立 agent 提供可移植真实 stdio driver，固定36份产品/契约/Session输入，直接运行常规coordinator/isolated worker。原v1新增首轮及带guard的source-02保留；主线分别在新Mac包、Linux源码/包运行，每次19任务全绿，完整语义比较SHA `74ab416c…` 相同。source-01脚本在运行后、guard修改前实际备份，缺开跑时SHA；不把后来e054字节归给首轮。固定source-02的现场launch绑定e054，主线三次也实际用e054。

为让旧版也实际执行两条emit，v2将第四规则前件从typed改为plain，输出仍typed；另建不可变合成seed，未拿v1绿替代v2。v2同时在独立源码、新Mac包、新Linux源码/包各实际完成19任务，全部7结论/8trace和完整SHACL报告正确，完整语义比较SHA `eb51f12c63c9ea6abac3cd745aeab887ab9b0f3310071da0fe0c2c2901f8cb2b` 一致，覆盖六构造、STRDT空串/引号/反斜线/换行、VALUES/sameTerm/DISTINCT/COUNT、selected和断言负控。

同一v2 seed在原封保留的Mac/Linux C3包各完成19任务，先保全全部实际metadata/public rows/原存储行/认证payload和hash，再评估oracle。两者均真实exit1：5结论/5trace、max1错误违规、min2错误通过，共17个case不符。这个红来自字符串语义，不是硬编码finite6先拒旧版；expected implementation取旧真实认证结果的完整三字段，实际job/metadata/payload另逐项校验。17不符是同一身份缺陷的多个表现，不是17个独立发现。旧summary中硬编码7/8是oracle规模，实际计数明确在observedReasoning为5/5。

主线独立解码上述十组完整结果，每组19份payload与公开rows逐leaf相等并重算payload/rows hash；新每组2802聚合行，旧每组2288行（均含header，不是测试数）。比较副本只排除临时result标识和validationBinding包装；原完整载荷、binding、resource内容及hash均另存并实核，不能以去身份副本替代原结果。

## 独立实现与历史门

[独立报告](evidence/integrated-c4/internal-review.md.raw) SHA `d053c56b49f635ce6fbe3e1a6c44f0bc55c4816b5a2da3b68684336d0fd61a97`，在固定1a本次修复范围Pass，I05-C3-STRING-1关闭，未发现新增阻断。其亲测522项/33.31秒，新worker18＋stdio18＋historical selected2共38任务、旧finite5任务12；50份完整结果共5329行重组通过。另有34个精确pure case、12次并发、cold/warm grammar/TrueFilter隔离、8类lexical及numeric/lang负控。该agent没有运行主线包、全check、B1或native，证据归属分开。

真实旧finite5结果在新Store仍按原producer身份读取，原payload、rows、hash和metadata不变；新任务选择旧结果的current和historical路径均IDENTITY_CONFLICT。对新所选结果分别改变consumer三个implementation字段，也各自拒绝；真正新finite6 current/historical selected成功。selected纯投影另用失败回调确认没有调用reason重算。

## 失败、恢复与未验边界

共享suite首跑使用范围外targetNode被原guard拒绝，改为既有targetClass后通过；首次全check只因strict decoder格式失败，修正后1837通过，追加隔离测试后最终1847通过，全部原日志保留。

Linux第一次受影响测试359通过/1失败：源码文件已6，但mtime0和同文件大小令旧resources字节码被复用，实际源码进程导入5。清src缓存后第二次仍有1项失败；在源码semantic已6而断言失败的条件下，pytest重写缓存是归因，未伪称已保存其旧code object。清本线tests缓存后360全绿。首包从未在该轮接受runtime验收，不能据此称首包运行5：事后直接读取首包七模块均与1a相等，且其engine hash实际等于最终Linuxengine。曾用“错误包”概括的说法已向用户和总控更正。首目录包仍独立保留，最终验收明确绑定最终release与实际上述运行。

独立原型v1漏检并修改了其临时进程的TrueFilter，首件和fresh负证据保留；v2额外复制单例。独立实现审查的首pure oracle错误（全unbound BIND原旧版同为[]）及读取计算型parser.name造成的观察器干扰，均保留脚本、失败、旧版对照和修正后raw，未为探针改产品。上述旧行为限度不算完整SPARQL标准符合性。

205是跟踪执行输入；ignored验收driver、输入spec与输出另由1254成员清单及archive hash完整固定，并非未绑定的可变补充。完整raw及脚本见 [证据清单](evidence/integrated-c4/manifest.json)。大raw入库用于本线尚无实际CI artifact时完整可复核，排除SQLite/WAL/SHM/locks、环境/缓存、app二进制和可恢复的源码transport；完整输入spec、原始失败、结果和恢复recipe保留，不承诺从raw压缩包恢复原SQLite文件/签名app。205执行输入、64原保护源、全部源码transport成员与实际包绑定另列，旧C1/C2/C3原件未覆盖。

当前是固定库有限范围修复；私有Expr适配依赖锁定RDFLib7.6.0及明确guard，没有全RDF/SPARQL/SHACL、完整BCP47、未来aggregate或D3/D4比较政策承诺。所有旧C1意见处置/Q6十二项及其他产品待决、签名/干净设备、Mac/Windows本版native和生产证据保持原边界。指定同版双审、真实CI/正常合并/远端核验依原门禁执行。
