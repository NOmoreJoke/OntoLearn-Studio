# T01 纯来源表材料阶段收口

本阶段实现并验证两端完整表的 canonical 编码与摘要助手，独立审查 P2-M1 已修复并关闭。只支持受控、独占 data-only 输入树上的内部机制；没有启用真实 parser、来源授权、source wire、worker 或业务3-ready。

## 授权、范围与冻结输入

总控阶段授权 `T01-table-material-phase-authorization.md` SHA256 为 `562be71b7b122f17ab3747c1bf149a30574b6aba44330a7a8c1750d95f071a02`。产品基底为 `b35cb4e21d375386775e5fc0431a8089a47195da`；期间的过程提交不扩大产品范围。本阶段只修改三个产品路径、新增两份专属测试：

| 路径 | 最终 SHA256 |
| --- | --- |
| packages/contracts/src/v2.ts | d61d00f0f0fbba3cb658f628d1e1d128cac232a1c0e183bb9e38e112cc424ef6 |
| packages/contracts/python/contract_v2.py | e50be513b51a817029c3a212e7d3a8ac02cb1b7164b7ab08987fc6af339ae20c |
| packages/contracts/v2/fixtures.json | 752284cb502e34ff6c97f223c20610c96a4eda7366bfb3aa7ab2858bf583cd5d |
| tests/unit/t01-source-table-material.test.ts | 4a650f1d23661eabbff5488f69e633bb8c05ee14628584cc194c0f4330e58902 |
| packages/engine/tests/test_project_source_table_material.py | 96f0dc32e2ff847f4cd3880f548faa65b1aa4dd57be4e488f8c41a173d9ef3cf |

TS 既有 helper 前区域与基底逐字相同；Python 既有区域只增加 hashlib import；fixtures 旧顶层值均不变，仅追加 sourceTable。以上机器比较及独立检查见 [独立报告](source-table-material-independent-review.md)。没有修改 schema、registry、errors、默认协议、ready、producer、Job 或桥接。

## 实际行为

TS 的 `sourceTableMaterial` / `sourceTableDigest` 与 Python 的 `source_table_material` / `source_table_digest` 要求显式 options、三字段 implementation、独立 expected source hash 及正 safe integer 值的 encoded byte 总预算。无隐含编码、sheet 或实现身份默认。CSV 限精确五种编码，XLSX 限非空 sheet；原始字段、行序、物理行号间隔、六类 cell 的原始 text/kind、完整尾行及三个实现身份全部进入规范材料。

两端先捕获受控原始值并核精确结构、字段/行/文本限制及 escaped UTF8 费用，再生成私有编码块；预算不足不返回部分材料或摘要。普通 accessor、Python 子类和宿主转换在读取回调前拒绝。TS 反射可能触发恶意 Proxy trap，因此内部 data-only 前置、受控 decoder/producer 与实际进程隔离仍不可省略；本助手不承诺任意宿主对象沙箱。

共享 corpus 为62个完整机制用例（29个合法）、14种原生 JSON 预算 token、完整大材料与字段256/行50000/非BMP32768三个边界 oracle、29个精确空白码点。golden 由独立标准库参考脚本生成，使用 synthetic 身份；六份 T03 完整表只是固定接口投影，不代表执行过真实 CSV/XLSX parser。295207B 大材料明确大于单帧262144B，不据此开放运输。

## 验证与独立处置

实际专项最初80 TS/84 Python，扩边界后112/116。首次 typecheck 的两处新增测试类型错误、首次 check 的 control-regex lint、随后文档格式失败均已修正，原失败日志保留。第一轮完整 check 938 TS/2612 Python/44原不适用 skip，实际 session45516 exit0，属于后续 P2 修复前候选。

独立审查发现 P2-M1：原 Python 仅接受 int 预算，TS 接受 JSON `10000.0` / `1e4` 的相同整数值。已改为先精确 builtin int/float、非 bool、范围/有限门，再判 integral 并规范化；巨大整数、NaN/Inf、分数、宿主子类仍拒绝。两端共享14种 token，另补 Python 宿主回调反例。修前身份、实际失败和原独立探针的外层退出对象未展示边界均保留在独立报告。

修后最终专项 **126 TS /132 Python**；最终 `npm run check` **实际 session67934 exit0，952 TS /2628 Python /44原不适用 skip**，lint、格式、类型、构建及 ruff 均通过。独立定点16项 passed，以及14 token 两端完整结果对象、4个额外巨大/非有限数拒绝均实际通过；独立没有冒称重跑完整矩阵。独立报告最终 SHA256 为 `3b80fb8167c1f4ca940221529fe70430625fdbed1cf360ca9b18d82c41b1d684`，无第二项实质阻断。

## 原始证据与未完成范围

[新原始证据包](evidence/source-table-material-raw-evidence.tar.gz) 为39000B，SHA256 `e558203ff2ac79fe8948549054ab80fc1d04353d7c53238a608f6fdb1b13ec2c`；[索引](evidence/source-table-material-raw-evidence.json) 保存原 session 前缀、行/offset/hash、11对主线和7对独立工具 call/output、12份完整日志、修后五文件身份。归档后逐成员回读字节/长度/hash，与索引一致；旧阶段包不改。第一次全仓通过和最终通过分开保存，不沿用旧938/2612证明新候选。

尚无真实 parser implementation 三字段、受信 producer/source 权限、实际五编码解码、source 运输/预算账本/GC/pin、学习与完整恢复、运行时3握手或最终桌面验收证据。内部审查不替代指定双审。当前只准备本地恢复提交，未 push、PR、CI、合并或发布；父功能与现有 Goal 仍未完成。
