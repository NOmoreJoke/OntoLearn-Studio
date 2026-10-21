# metadata 优化：精确账界与 Node 回执独立补充审查

2026-10-22。本补充仅处理新 1754B 授权、小账和事后执行重建回执；不重开实现、全量映射或首轮构建审查。

结论：当前静态窗口的逻辑记录账界已由精确授权解决；95f07d931eeffd3bdcd52cb21e9fa2d8a1db12bd 候选的原静态代码／映射结论保留。此结论不批准第二次 configure/build，不扩大到 40GiB，不把 Node 元数据用例写成构建或 native 通过。

## 本次固定依据

- `exact-metadata-record-delta.md.raw`：1754B，SHA-256 `130323fc6d12a2823e6bb9591f79b13807c5695bd724b8ad902bad02abf43363`；已全文读取。
- `read-and-parser-budget.json`：7176B，SHA-256 `c58868af0dfa7deb6f500c02b68abefa9d0174a34655af342697c59efab66228`；已全文读取，含未来两门的 prospective 字段。
- `final-node-metadata.execution-reconstruction.json`：2220B，SHA-256 `56ba18e57f1637a044c80105a8f0dee5dae145db479b99385e4dde2c3b1b59f4`；已全文读取。
- 原 `independent-review.md` 保持 10643B、SHA-256 `f016b32259cab6404f441a15c9a6816d0fe0fd553bc59a7b06903175a99baa84`，未改写。

## 账界核对

608116（owner）+128316（原独审）+85544（根独审按 source／sidecar 各计一次）=821976；加 fixture 1024 和收尾 4096，合 827096。新累计上限 1000000 下余 172904。小账各项与授权一致，历史 223168 计数不完整、400000 不足以及后续 750000 请求不足均保留，不能倒写为过去从未超界。

本授权只覆盖既定 42772 集合的有限 metadata 静态窗口。实体供应记录 200000、32GiB、其中 metadata 1GiB 预留、旧供应读取 9745727085B、单 manifest 16MiB／50000 均未变。逻辑记录访问与实体 pin、磁盘 I/O、RSS、性能测量分别记账；本次没有新增实体读取或 pin 验证。

未来两门预计实体验证 85544，source／sidecar 逻辑访问 171088；827096+171088=998184 的算数成立，但不能因小于 1000000 就执行：这 1000000 仅授当前静态窗口，未来须根另授精确范围。未来累计字节声明 37044475528B 超原 32GiB 2684737160B 的待决边界亦保留。第二次构建和 40GiB 尚未授权。

## 候选身份与 Node 证据边界

只读 Git 比较当前三 writer 相对上述 95 提交无差异；没有重新读取 SDK、cache 或供应实体。以下为该固定候选身份，未因账界／回执变化改变：

- CMake：19815B，`f2b5522b92c5dfc9724b95c35b876ce5015a4955385f614a6da20fb9bce57645`。
- lock：10474B，`bb74f5117e2efa6e5abf2d45bfaa0788a539dc502eb028f9819b4f8de6739a1d`。
- driver：30056B，`ca4ef93024762ae5dfd3dc95133f8ab28ae2e63048af0b3a658bfeb98f62045c`。

重建回执明确其非当时保存的结构化 child result，口径可接收。它记载 argv 为 `/usr/local/bin/node` 加该目录 `static-metadata-validation-v3.mjs` 的绝对路径，cwd 为本工作树；exit 0 依据原 Python 调用中的 `assert z.returncode == 0` 及原 exec chunk `405b1d` 的 exit 0 重建。本次没有重新取证原工具历史或执行脚本，不能把此重建当作新测结果。

实际保留 stdout 为 59B、SHA-256 `b364273f18bce6d3621e553b00008cb42b522233b24cc137dbc27f37ba99d999`，内容为 24 cases、pass、physicalSupplierReads=false 的 JSON 行；stderr 为 0B、空字节 SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`。本次核同其字节和摘要与重建回执相符；stdout 本身不单独证明退出码。缺少当时独立结构化 subprocess 回执及 child 起止时间仍是证据限制，null 时间没有补造。规范化换行／排版的调用转录也不应标为逐字原始记录。

本补充只读小型授权、JSON、原双流和 Git 差异，校验小文档摘要并写本文件；没有重跑 24 例、全量解析、driver、探针、configure、编译、测试或实体 hash。原报告的实现和映射结论不扩展为性能提升实测或新增运行授权。
