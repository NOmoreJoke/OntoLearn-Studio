# metadata 合同实验静态承接准备独立窄审

结论：当前文档可接受，无阻断本轮静态准备的未解决问题。本结论仅覆盖新目录内的责任、输入收据、预算算式和后继门，不授予实验构建、静态产物检查或运行权限，也不代表 N0、ACL、EXCL 或任一产品测试通过。

## 审查对象与固定身份

基线过程引用为 `37fe056e5d1716a10237de20f79042db54aa0549`。本次全文读取四份准备文档、有限的八份输入副本及新增静态验证收据；未读取 I06 当前源码或半成品、旧供应池、SDK/index、旧构建大包。审查时当前文档身份如下：

| 文件 | 字节 | SHA-256 |
| --- | ---: | --- |
| build-plan.md | 11672 | 03f83b96791e866425e575c7c5b4deb4415b67f69f0d241423b1559faca3df2d |
| budget.json | 4231 | 81b25cbc4827f1655cd3063e2b3485c972301b71d9d25c6b13e9f30ad2ab151d |
| input-receipt.json | 3881 | 69725608fc08a8dc0c0c6c6220af33eb18130151cdf60b3e217891c25dc8834c |
| handoff.md | 1498 | 68695111c006c17c9cd27c2862d43432b0d0699975bead6ef779359546c244a4 |
| static-validation.json | 1149 | 0b1003c0ce0edd28299a9328a7bfcd55ede6ed68793d5caccd334e0956f66c5e |

八份输入副本共 43015B，逐件 bytes/SHA 与收据一致，路径无重复：

| inputs 内文件 | 字节 | SHA-256 |
| --- | ---: | --- |
| T03-metadata-contract-probe-build-static-preparation.md.raw | 3556 | 9a6f220ac95e926237d4122e127f067a3063a222d9cf0d7f9a4b749a6614beba |
| I06-full-positive-contract-root-closure.md.raw | 1821 | d3d3aa29ba371c81f1c3b39853526282d69f40ec84bcd45746e39ea03feb1c9c |
| I06-controller-full-positive-contract-direct-proof.json.raw | 3144 | 7e0db6854652b687ed21e1bfa914e189d0678cc0b66e99b3d9b5e11e2cdbd851 |
| I06-metadata-contract-probe-source-window.md.raw | 4746 | 7eca703961cfafedc130d4e864ae9394f3a52d136256973614a43b73f90ec3f6 |
| decision-experiment.md.raw | 15506 | 55f073f1352ef7e621455a2fb70dfe92c6287e10c591459abf916ee4d532c1e7 |
| experiment-static-bounds.json.raw | 1377 | 63623e918aca20d85cf5ffa03404d2cb662fc5e07666a15ddee58ab9cc9ff8c1 |
| sixth-read-account.json.raw | 2390 | 2996a3d7c056af486734f72f49d23bec9eeb70d2f25ad5c861bff29fad76e3b1 |
| sixth-fixed-toolchain-lock.json.raw | 10475 | 0ed8ddd79a31439086ef3fd5cabbb750ccaffc48024ea0e1a64ab2cb1f608d07 |

核验范围是这些指定副本及其收据；没有重新取回 live root 文件、Git origin blob 或物理工具来另证身份。两份实验文档的固定 `7ea3bfb06ff117f80f0aa770ab5f563b6b5c3b3e` 引用与所附 direct-proof 的 pin 对应。旧锁来自固定 `bfe137f371361f9fda446d5cbe6b3079c5433ee5`，仅作为本轮 metadata 输入。历史 proof 中“源码仍不存在”只描述其快照，不是本次对当前 I06 源码存在性的检查。

## 责任和后继门

本轮授权只覆盖静态承接准备。I06 仍是实验源码 writer；T03 不维护原源或替换判定标准。本轮没有创建、调用 runner，也没有创建新 build/run 目录。

计划保留了原实验关键边界：两个自有 fixture E/N、固定五个样本、普通模式与限定 FD，不以更强权限或环境替换换取通过；固定缓冲区与调用次数上限；完整请求掩码、打包布局、实际返回位、长度/偏移溢出检查、NOACL 与单 ACE 完整语义映射。它们目前是后继输入合同，尚未由冻结源码、编译结果或运行观测验证。输出上界和静态字段宽度也不能代替实际源或 runtime 证据。

后继仍需 root 收到冻结实验源、独立静态审查、精确 source/header/symbol/layout 映射，以及 runner/interpreter/tool/SDK 的固定身份；另行授予一次单源 compile/link 与有限静态归档窗口。runner 尚未实现，字节捕获、超时和 unknown drain 的落实仍是后继前门。当前命令模板保留占位符，不是可执行验收命令；已删除继承旧产品配置的 `-O2 -g -DNDEBUG`，不预先引入改变新源检查语义的宏。

任何缺件、未知绑定或触顶都停止并报告准确缺口，不自动追加工具/库、fallback、重试、放宽 cap 或转移记账类别。未来物理实体访问的记录也计入相应 metadata 分票，8192 实体票不是额外 metadata 票；所有 cap 同时适用，先触顶停止，不能保证各票均可用满。编译器内部访问、loader 和系统实际 I/O 不因应用票而成为已观测或硬限制。

计划未重启产品第七次构建、原全 pipeline、SQLite 拒线或其它冻结范围。后续原 I06 的 fixture 设置、API 调用、读取及 cleanup/native once 仍须独立运行授权。T03 不能将未来静态产物等同于该运行授权。

## 账算核验

旧账原样保留：build 声明 108738235432B，guard 137438953472B；旧 supply 9745727085B 单列；metadata 2055635/2250000，实体 513264/600000。首次 CMake completion 的 unknown、旧超额 255、历史已消费和预留票均未退回或归零。

当前静态准备分票核同：

- bytes：四份各 2097152B，合 8388608B；作者窄审与 root 窄审分开。
- metadata：owner 2000 + 作者 2000 + closure 1000 + root 2000 = 7000；实体新增 0。
- build：108738235432 + 8388608 = 108746624040B；余额 28692329432B。
- combined：118483962517 + 8388608 = 118492351125B。
- metadata：2055635 + 7000 = 2062635；余额 187365。guard 未扩大，旧票未释放。

未来方案明确为 `PROPOSED_ONLY_NOT_AUTHORIZED_NOT_CONSUMED_BY_THIS_STAGE`。候选分项相加：128 + 64 + 16 + 16 + 32 = 256MiB（268435456B）；1000 + 6000 + 500 + 1000 + 4000 + 4000 + 128 = 16628 metadata。实体 cap 8192 与这些分票联合适用。若以后另获批准并分配，算术余额分别为 build 28423893976B、metadata 170737、实体 78544；此处没有将候选票冒充当前执行许可或当前消费。

旧锁中 compiler descriptor 为 124676976B，单件小于 128MiB 身份票，只余 9540752B 给其它必需输入；这不能证明源、其它工具和 interpreter 合计仍可容纳，也不能证明当前物理 compiler 身份未变。最终精确前门必须求和并在不足时停止。

旧全扫反例算式核同：171088 + 42772 = 213860，比当前静态准备后余额 187365 **超出 26495**，还未计其它审查成本。曾发现 build-plan 将方向写成“少26495”；owner 已改为“已超出本轮准备后187365余额26495”，本次复核当前字节已修正。原数字和 JSON 缺口一直一致，本修正未改变 cap、历史消费或权限，也不代表实际执行了旧扫描。

`static-validation.json` 的 18 项有限断言、八份输入 43015B 身份及静态/未来权限区分与本次核对一致。该收据不是产品测试、compiler 或实验 API 验证。

## 阅读与交付边界

本次独审只使用指定小文档、副本及有限 JSON/文本运算；没有读取供应物 payload、实际工具或 SDK/header 内容，没有执行构建、verify-only、检查器、版本命令、测试或 API/native/GUI 实验。没有重新解析完整 42772 metadata 或旧 used 集合。

按跨调用重复读取也累计的保守口径，本次审查及报告收尾的应用读上界取 **384KiB**，逻辑对象/记录访问上界取 **1000**；均低于独立票 2MiB/2000。以上是本次有限文件操作的保守应用侧上界，未实测 OS/cache/磁盘 I/O，未借用 root 的独立票。报告本身是唯一新增文件，不修改产品、源、锁或他人材料，不提交。本结论不预签 owner 后续最终 index 字节闭包。
