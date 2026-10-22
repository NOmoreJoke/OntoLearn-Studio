# T08 e3：28源、有限DOM与原完整check根收件

结论：可限定接收候选 `e3c727dd90e22e7add5f0db94cefb57901af61f0` 的两份新增fixture、实际mounted-03及本候选原完整npm check证据。没有发现阻断本次有限收件的新问题；不是指定双模型Pass或父项完成，原NotPass/NotPass、P1/P2严重度与原Goal blocked不变。

固定过程 `0932268ddaaac29511bd57d26737ad48de1e8495`，base `5f910b52c69d86a1076b2032e5d3c63e715947f3`。入口8993B／`94468fff19850b8e3756f7ad2a3db9b62c0bfa4b1249d05a50fe98ca18ef1378`。新archive-manifest列28普通文件；旧manifest列25文件；与索引合并54个唯一显式成员共156034B，全部安全相对路径、current长度/SHA/固定process Git一致。新manifest自身5821B／`45ecdbecd1fcdad4fe25eb8800905634401532c838da136cb29ef9baa6290af8`，另核current=Git；这是目录归档清单，没有虚构ZIP。

28源current = e3产品Git = process Git；原26源还逐字节等于7a33。产品源码增量只有harness3625B／`470b34fd9b4e2e23d21545b4e1f1da71f4ead027e7f894e3090b4ae7ad7fab9c`与runner22805B／`304d54217a8949da24081a591ecc5ec67ec5bd5c7e0e0ba160e9a6b355c9e7d1`；另有过程文档变化。run03和最终check的28源before/after均等此清单；授权prefix当前Git无改动。未重审原26算法。

全文读handoff、方案、两轮方案/实现独审、取消oracle纠正、DOM/check证据独审及三次mounted raw/metadata/result、symlink负例、新完整check原流。独审文件是owner导出的独立agent最终回复，不冒充指定模型或本审直接核过其原生全流。初版方案未独立导出字节/hash仍UNKNOWN；首NotPass保留。

失败链完整：修前3项实际失败exit1（21 skipped）原raw保留；方案首NotPass指出codec Buffer不能并入browser IIFE；实现首NotPass指出busy掩盖Diff、依赖pin不足、父symlink逃逸。mounted-01五组通过/第六组2≠1失败、exit1；取消oracle改为完整deepEqual两条收据，静态核原未改conversation测试369–398确有完成收据+CANCELLED合同，未降低产品语义。mounted-02虽六组exit0，不能计最终完整覆盖；最终e3补非busy正对照、七轴stale负向dispatch、9依赖pin及mkdir前realpath。mounted-03六组exit0，三个result归档逐字等runtime原件，三次28源前后均等各自固定候选。

全文读111行harness与600行runner：browser实际ReactDOM createRoot/flushSync、原Sidebar/CSS，真实textarea/requestSubmit/click；Node Vite SSR执行原conversation/session/codec并保原生Buffer，没有DOM/hook/Buffer shim。专用binding传合成动作和安全state，model响应/端口仍是合成fixture。覆盖14模块模式组合、七上下文轴、A/B及迟到更新、草稿证据/克隆/文本安全与纯模块AbortSignal取消。它不等于T04 QueryPage、公共composition或I04持久job/ACK/终态。

run03记录Node v24.15.0 `/usr/local/bin/node`；Chrome真实版本155.0.8059.85，显式exe367696B／`6e156f2271cef44afce9db36a5b920e94518857b94a4160f082696f8c3bd1c9d`。Playwright/core/test1.64.1、React/DOM19.3.1、Vite8.3.4、React插件6.1.2；9依赖before/after/current一致，2固定输入before/after/候选Git一致。Node二进制SHA未记录，本审不从当前文件反推历史字节。三own profile目录独立存在且非symlink，仅stat，不读内容；launch源采用headless/offline/route abort、不用既有用户profile或固定server端口。pageErrors/页面requests为空只支持页面观察，不是OS全局网络审计。

symlink负例真实exit1，错误为output parent symlink escape；源码在mkdir/browser/build前拒绝。当前仅核该own parent为指向/tmp的symlink及精确新目标不存在，未执行probe。三PNG均61914B／`122d96ead3bd5c088a3cfb4f264981cdbaf285c4f1ac146b6a76eae2a9208b41`，只hash，未视觉审查。

本e3原完整check：2026-10-22T21:04:10.682662至21:05:40.552903Z，实际exit0；raw5050B／`05e1fcbbd222cb7e199e9cddf9c07eaf9f1870bc15f50acfda89f9457d48b045`，metadata8950B／`d7499824f12cd76d46b89e0e06c1c1434a041ef299f48da77e845e6099cce44f`。完整流含lint、format、contracts/unit/desktop类型、22文件752TS、build、ruff及1052Python通过；执行前后HEAD均e3。没有借旧7a33绿。harness不在unit tsconfig范围，DOM证据来自单独run03；handoff其他定向静态命令未在本审重跑。原raw/metadata支持退出和计数，本审未另做PID轨迹或双流拆分。

Electron require自动下载副作用如实披露；原stdout无单独raw，按原对话来源说明承接，不称只读清点/应用启动。原I05/T04唯一parser/executor、T00接线、I06隐私/provider、T01正式ChangeSet、T09实际离线/学习以及原11.3/12.2、平台/真人/CI/远端/新完整指定双审仍待。没有API/key/spend或Q5默认。本审仅stdlib/hash/stat/JSON/text和只读Git，不运行产品/作者工具/import/tests/GUI/browser/native/DB，不改owner/source/state。精确54成员、28源和全部关键引用见同名JSON。
