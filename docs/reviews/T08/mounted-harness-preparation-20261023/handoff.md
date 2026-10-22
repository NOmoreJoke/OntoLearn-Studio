# T08 真实挂载与新验收候选交接

新验收候选 `e3c727dd90e22e7add5f0db94cefb57901af61f0`；cwd `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T08-agent-model`，branch `feature/weekly-t08-agent-model`，base `5f910b52c69d86a1076b2032e5d3c63e715947f3`。原26源码／测试／fixture逐字节同7a33a920faf92fe0d19de3a0a1b0efad80b93d5b，只新增两份自有挂载fixture。原7a33完整752/1052证据固定在9cdb3541ab9c56818bb8e4d73a8de80fe7c86663；本次e3另跑完整check，不沿用旧绿。

## 真实执行与原件

现有Chrome155.0.8059.85、锁定Playwright1.64.1，显式exe SHA、全新own profile、headless/offline/route abort、无Vite server或固定端口，不接既有用户profile。没有启动Electron/UI/native。browser使用真实ReactDOM/Sidebar/CSS；Node SSR bundle执行原Conversation/Session/codec、使用原生Buffer，经专用测试binding传合成动作与safe state，没有接入产品公共桥。

- mounted-01（44f1346）实际exit1：前5组pass，取消oracle错误地期待1条；已按既有完整收据契约纠正，旧失败保留。
- mounted-02（3896）实际6组pass/exit0，但独审随后指出busy掩盖Diff对照，因此不计最终完整覆盖。8d9/e3补正反对照、依赖和路径门。
- mounted-03（e3）实际6组pass/exit0：含14模块／模式组合、七上下文轴、原M P2-6事件、A/B输入与迟到更新、草稿／证据渲染、克隆预览、文本安全、纯模块工具取消与late result。28源码、2固定输入、9依赖前后相同；pageErrors和页面requests为空，不是OS全局网络审计。
- symlink负例实际exit1且符合拒绝预期，外部目标未创建；没有把预期失败写成运行exit0。
- e3原完整check实际exit0：752TS/1052Python，lint/format/types/build/ruff通过，28源码前后相同；独立证据核验通过。harness严格tsc、node语法和定向eslint也已实际通过；单元tsconfig不覆盖该TSX fixture，不混写证明。

入口：[精确索引](controller-handoff-index.json)、[最终收据](final-candidate-receipt.json)、三次mounted的raw/metadata/result、fullcheck-final原raw/metadata。result JSON是runtime原字节副本；小份raw保留首失败与真实exit，随本次归档。profile、bundle、PNG与Python数据库／缓存保留在own runtime，不stage、不删除或ignore求绿；PNG哈希见local-screenshot-artifacts.json。owner已查看草稿／SPARQL文本可见，不宣称全App视觉验收。

方案独审1因Node/browser边界NotPass，纠正复核2通过；实现独审1三项测试／runner边界NotPass，e3增量复核2通过；DOM和新完整check证据分别独立核验。旧意见全部保留，没有替换指定模型。

## 命令与真实缺供方

已执行的完整argv见mounted-03.metadata.json：`node tests/fixtures/agent/sidebar-mounted-probe.mjs --candidate e3c727dd90e22e7add5f0db94cefb57901af61f0 --output <本树runtime>/mounted-03`。重跑须用全新output，不覆盖该目录。runner核固定Git28源／输入、真实路径归属、锁／依赖／Chrome身份，失败同样留原件。备用锁定Chromium为revision1248／156.0.8078.4，仅在现有Chrome不适用后采用；本轮未安装Chromium或自动换浏览器。

- P1：仍缺获批I05/T04唯一parser/executor、拒绝原因及T00实际composition；产品query_execute未安装，不造lexer或原样执行兜底。
- Query组件／真实取消：当前e3没有T04 QueryPage，仍缺固定获批只读消费ref、精确路径／props以及T00/I04真实命名job、取消、ACK与终态。本次DOM和纯模块AbortSignal不等于业务查询／持久job验收。
- 原其余真实验收：I06当前设置／隐私／最终字节授权／受测provider，T01真实Diff／独立confirm／原子／undo／restore，T09真实离线／学习记录，原11.3/12.2、平台／真人／CI／远端和新完整同候选指定双审仍待实际路径。无API、key或spend，Q5未默认。

原两NotPass、P1/P2与原完整目标／Goal blocked保持，不由owner关闭。旧93516/5b64审件、共享App/preload／契约／锁／CI／root状态均未改，受保护AGENTS未stage。下一指定双审携带全部原完整输入／PRD／失败／争议及新28源，不做delta-only。
