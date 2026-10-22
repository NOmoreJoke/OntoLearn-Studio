# T08 上下文边界续修与必要验收

2026-10-23。继续原授权自有修复，不改旧93516/5b64审件，不重新解释旧M1P1/7P2/3P3为已关闭。原14项技术处置完整保留于[逐项裁定](../post-designated-review-20261023/finding-disposition.md)。上一候选330641的完整739TS/1052Python只属于它，不能计为本次新增字节的完整check。

## 采用与共享责任

- P1继续采用唯一I05 parser/真实T04服务门禁；本线不增加lexer或关键词拒绝。读取总控固定执行接口事实及T04当前状态，只用于确认接口缺口，没有导入或消费未批准实现。现T04 reader不是查询执行器；缺获批执行入口、来源/范围/版本/取消及拒绝原因映射时不安装query_execute。T00维护实际composition/唯一注册映射，不能安装原样执行端口补空。
- provider/thinking维持330641的宿主受测pin、响应/历史差异与固定codec合同；requested ceiling仍只代表请求输出上限，usage与Q5/费用不混用。本轮未改这些路径。
- I06仍唯一维护实际配置/隐私/字段外发/主体/预算授权；T01仍唯一正式写入、Diff/confirm/undo/restore；T09实际离线和学习记录、T03共享测试依赖/配置各留原owner。没有借这轮修复取得共享路径。

## 本轮真实新增缺陷及最小修复

1. **端口调用微任务缺口**：330641的AgentSession只在批入口/每笔结果回收后检查context，executeOne的Promise.then实际调用前无复验。批入口后切project仍会调用首端口；第一笔回收后微任务切snapshot仍调用第二端口；authority变不可读可在结果后抛原异常。三案修前原命令实际exit1，见before-fix.raw.txt和metadata；不是历史指定模型发现。现在每笔真正调用前同步读当前权威并比较，读取/解码异常固定STALE_CONTEXT；批前/结果后沿用同一安全读取，已有完成收据保留。该微任务检查不替代真实服务的独立scope/身份/事务门。
2. **侧栏跨上下文输入与迟到UI更新**：同一组件A输入切B时，旧useState仍可把A问题交B处理器；A的旧异步失败也会显示到B。现question/dispatching/localError以固定字段顺序的完整context tuple隔离，选中顺序保留；inFlight同步按相同key加锁，异步完成只合并启动key的最新状态，不覆盖后来编辑。切回仍有该上下文原输入。仅组件生命周期内UI内存，不是项目/学习/隐私权威，也不提供跨卸载持久保存。
3. **旧上下文取消入口**：旧A运行state配B回调时取消原未检查isCurrent。现按钮和handler均拒绝不匹配上下文；匹配的等待状态仍允许取消，不因busy封住取消。实际job/cancel ACK与真实终态仍归批准T00/I04服务，当前只校验组件入口。

## 已执行与待执行

最终本轮6个纯TypeScript T08文件共112项通过，eslint、完整TypeScript类型检查、五改动路径Prettier均exit0，见final-*.metadata.json/raw.txt，运行前后五路径SHA相同。此6文件不含会启动Python的fixed-input测试；对dispatch首批修复的102项日志按其当时WIP保留，不冒充最终112。UI状态转换单测和SSR禁用属性不等于挂载事件；没有hook/DOM stub。

完整npm run check、固定输入Python、build、Electron/e2e、实际DOM与真实服务联验仍未执行于本轮字节。总控最新安排为I05原check占共享runtime，新增共享运行须内部协调；观察其check自然结束不等于取得下一票。本线不自行启动GUI或共享check，也不重复向人类索取原授权。待内部runtime票执行原npm run check；因主进程改动，仍需按AGENTS补原test:e2e和相关实际入口验收。组件DOM可以用已安装同版依赖准备临时真实挂载夹具，不新增锁/共享配置；具体执行环境及GUI lease由总控安排。若确需新依赖仍由T03维护。

实际DOM必验（全部pending，不填success）：

- 原M P2-6四组：输入“保留001”双submit只handler一次；reject后原输入仍在且仅固定提示；无handler不调用；local禁retry而真实已给local hint可调用。
- A输入→B输入空且只传B文本→切回A保留原文；A在途→B编辑→A迟到失败，B无错误/锁污染，切回A见原失败且输入未丢。
- 同一context在途重复动作只有一次；切回仍在途的A保持锁。不同key不得交叉清锁。
- 旧A state配B context时取消不可调用；匹配A仍可取消。scope/version/snapshot/module/mode/选中顺序每项变更都隔离；对象属性插入顺序不造成误分组。

原指定两NotPass、原P1/P2、原Goal blocked保持；本轮独审仅审最小补丁，不替代新完整同候选指定双审。旧330641及其过程4e4ef5保留，新候选不能沿用它的完整check或外审状态。未push/PR/merge。

本轮最小实现候选已固定为 `7a33a920faf92fe0d19de3a0a1b0efad80b93d5b`；26份完整原范围源码/测试/fixture与本次五改动路径、实际验证绑定见[candidate-and-acceptance.json](candidate-and-acceptance.json)。这是待完整验收候选，不是指定Pass或发布候选。小份raw随本修复归档，保留首失败及真实退出码以便独审复查；runtime数据库/缓存不入库。

## 后续原完整check实际完成

总控明确I05/CSP普通check自然结束后，本线已在独立.venv/uv缓存/XDG缓存/pycache/tmp/pytest basetemp执行原`npm run check`，实际exit0：22文件752项TypeScript、1052项Python；lint/format/typecheck/build/ruff通过，26份固定源码运行前后hash相同，过程HEAD仍af24482c。完整raw/metadata见fullcheck-01；本节更新上文初始收据的pending，不修改旧失败或借用330641的绿。普通运行不是性能验收，没有host idle或性能量化结论。

准备挂载环境时，`require(electron)`触发包自身“Downloading Electron binary”，随后返回的本树node_modules二进制存在；未启动应用或窗口。这一步有环境下载副作用，不能称纯只读清点。Playwright指定Chromium实查不存在；esbuild直接导入不可用，现有Vite解析可用。实际挂载probe/harness尚未编写，拟定argv明确因该缺件不可运行；未安装浏览器或修改锁。现有`npm run test:e2e`仍需根串行GUI/资源，且共享App没有T08挂载，不能拿现有壳层e2e替代T08事件或实际Agent取消。

完整剩余原验收按实际owner、缺件和argv列在[真实验收清单](remaining-real-acceptance-plan.json)：真实DOM、真实job取消、唯一parsergate/安全说明、当前隐私及受测provider、正式ChangeSet与离线/学习记录、原11.3/12.2/目标平台及新同版指定双审。原P1/P2及两NotPass保持开放；没有API、密钥、付费或Q5默认。
