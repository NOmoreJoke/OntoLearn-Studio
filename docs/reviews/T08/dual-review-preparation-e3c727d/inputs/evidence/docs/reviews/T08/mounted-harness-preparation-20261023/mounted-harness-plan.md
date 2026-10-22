# T08 真实挂载最小harness方案

2026-10-23。先独审本方案，随后只在原owned fixtures与T08文档实施测试候选；产品当前固定7a33a920faf92fe0d19de3a0a1b0efad80b93d5b，过程9cdb3541ab9c56818bb8e4d73a8de80fe7c86663，base5f910b52c69d86a1076b2032e5d3c63e715947f3。原112纯TS、752/1052完整check、修前3失败与独审全保留，不继承为新测试候选的已运行证据。

## 机制、范围与owner

新增且仅写 `tests/fixtures/agent/sidebar-mounted-harness.tsx` 与 `tests/fixtures/agent/sidebar-mounted-probe.mjs`，以及本目录及T08 status。复用本树实际React19.3.1、ReactDOM createRoot、AgentSidebar.tsx/CSS；使用已安装Vite8构建隔离browser IIFE到自有runtime，Playwright1.64.1自动化真实DOM。AgentConversation/AgentSession/codec保留在Node runner侧，以Vite独立SSR bundle加载实际源码，使用Node原有Buffer，不向browser注入Buffer/polyfill。测试专用Playwright binding仅传合成动作和安全state快照，实际主进程纯编排在Node运行；此binding不进入产品App/preload或宣称公共契约已接线。无hook/DOM stub、无SSR替代点击，不改App/preload/公共contract/锁/package/Playwright配置，不引入新依赖。所有model/port callback输入为明确合成协议与fixture数据，验证实际纯模块编排和渲染，不声称真实provider/查询/业务job。

**Query供方事实**：当前7a33 renderer仅App、main和AgentSidebar三个TSX，没有QueryPage；T04 worktree确有QueryPage，但未取得该固定实现消费授权。第一步挂载实际AgentSidebar并覆盖query模块、原SPARQL草稿/证据显示；不复制T04 QueryPage。不把缺件扩大成等待整个T04完成。若根所指“现有Query组件”为T04 QueryPage，其实际同页联验还需T04给固定获批ref/精确只读source/props及T00实际composition/取消接口；此供方缺口单列，不用自造查询页填补。

## 浏览器与执行资源

锁定Playwright/package与browsers.json、当前expectedChromium缺失、Electron二进制实际SHA和自动下载触发见actual-browser-and-electron-facts.json。系统Chrome实际Info.plist为155.0.8059.85，拟优先其精确可执行路径 `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`，先静态核存在/大小/SHA，再由本次headless新进程观测实际browser.version；不把plist等同已运行兼容。launchPersistentContext只用本线新建user-data-dir；headless=true、不接既有profile/标签、不启Electron、不开固定server端口，browser使用pipe。页面用setContent+addScriptTag注入本地已构建IIFE和CSS；在页面加载前拒绝全部外部请求，背景网络关闭，测试数据全部合成。

若Chrome路径/真实运行兼容性失败，保真实失败，不自动切浏览器或装包。备用精确setup argv为 `node_modules/.bin/playwright install chromium`，仅设置本线 `PLAYWRIGHT_BROWSERS_PATH=<runtime>/browser-cache`；未执行，不改锁。该备用需根核实际必要性后才采用。任何真实Electron/UI/native/固定端口继续等根串行票，GUI当前C1，不能因下载过Electron就启动。

## 可执行probe约定

计划argv：`node tests/fixtures/agent/sidebar-mounted-probe.mjs --candidate <含两fixture的完整新40位SHA> --output <本线全新runtime子目录>`。runner拒绝缺SHA、源文件与Git字节不等、输出目录已存在或不在本线runtime下；将原26源与两新fixture作为28项运行前后身份，记录cwd/base/candidate、源码和依赖/hash、argv、真实Chrome版本/二进制SHA、开始结束/exit、每个case实际断言和原始console/pageerror。始终关闭自有browser context，不宽泛kill或删除失败profile/raw；异常也写metadata并exit1。当前先是方案，两个fixture尚未创建，不能称此命令已可执行。

## 原完整验收覆盖，不能只验Query

1. 七模块learn/ontology/mapping/query/quality/behavior/scenario与tutor/project模式：每页动作不超过四个；已给handler的local hint可点击、缺handler不可调用，完全本地禁模型发送/重试；full-assistance回调值原样可观测但不称学习记录已入库。
2. 全上下文项目、revision、snapshot、scopeRef、module、mode、选中顺序分别变更：旧记录警告、旧Diff及取消禁用；同实例A输入→B独立输入→切回A保留；属性插入顺序不造成新身份。通过真实textarea输入/点击submit验证，不只调用helper。
3. 同context双submit同步只一次、在途禁重入、输入在reject后保留且异常private文本不显示；A在途切B并编辑，A迟到reject/finally不改变B或覆盖后来A输入；切回未完成A保持锁。
4. Node侧实际纯AgentConversation到AgentSession的工具取消（真实browser事件经专用测试binding触发）：第一query草稿已完成可见，第二合成端口等待并监听真实AbortSignal；点击cancel后信号实际aborted、state取消、本地草稿仍可见，迟到结果不能变成功；这是实际纯模块取消传播，非I04 job取消/ACK/持久终态联验。
5. 草稿/证据真实渲染生命周期：实际同组件rerender追加收据、query SPARQL原文、001/0/false/null、trace、current/stale/historical/failed/cancelled；final错误后草稿仍可见，Diff callback拿到克隆与原base，旧revision不触发。恶意HTML作为文本，不产生script/img/外发。
6. 原所有codec/AgentScope/白名单/协议/预算/取消与固定输入单元仍由完整npm check全部保留，新harness不删或替换原测试。真实业务query、所有领域端口、I06实时隐私/授权、T01正式ChangeSet、T09真实离线与学习、原11.3/12.2/目标OS/真人仍按原gate完成，不能用本harness手工protocol或UI fixture顶替。

先独审方案修正具体缺陷；获本次必要新测试实现后固定新候选，跑静态/真实headless probe/原完整check，保所有失败，独审实际实现与证据，随后按原要求新完整同版指定双审。P1 parsergate、原P1/P2与两NotPass不关闭，不调用provider/读key/付费，不默认Q5。

方案独审首项纠正已采纳：codec的Buffer.byteLength是Node边界，不能直接随renderer打包。browser bundle仅UI；Node SSR bundle执行实际conversation/session/codec，经专用测试binding驱动取消与状态更新。没有Buffer或DOM/hook shim。
