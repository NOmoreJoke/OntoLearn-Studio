# 主进程来源选择与字节复验

实现：`apps/desktop/src/main/mapping/source-selection.ts`。依据 FR-300 的 CSV/XLSX、显式编码与单工作表要求，以及 FR-303/304 的旧预览拒绝要求。本文件描述私有模块及接线前置条件；实际状态与证据见 [status](../../../reviews/T03/source-selection/status.md)。

## 权威与接口

`SourceSelectionBroker` 只由可信主进程持有。构造时注入 `TrustedPicker(signal)`；只有该回调返回的绝对路径可进入读取。renderer 不能传路径、回调、任意方法或 `SourceProof`，也不能取得原始字节。选择摘要仅含不透明 selectionId、项目/lifecycle/generation、格式、编码、sheet、大小和 SHA-256，不含路径、文件名或单元格内容。

| 方法                                     | 私有语义                                                                             |
| ---------------------------------------- | ------------------------------------------------------------------------------------ |
| `openProject(projectId)`                 | 新建按对象身份核验的 scope，撤销旧 scope、选择与证明                                 |
| `pick(scope, encoding)`                  | 撤销旧选择，可信 host 选择后真实有界读文件并计算摘要；用户取消返回 null              |
| `configure(scope, selectionId, options)` | 校验精确选项，入口即撤销旧证明并更新代次；重读原字节，后发配置生效，成功后换新选择ID |
| `readForInspection(scope, selectionId)`  | 选表前复验并读取main-only bytes/summary供真实解析器枚举工作表，不生成proof           |
| `readForPreview(scope, selectionId)`     | 重新读取与验指纹后返回 main-only 字节副本及弱引用表登记的证明                        |
| `readForCommit(scope, proof)`            | 核验同一实际证明对象、scope/generation 和当前来源指纹，返回新字节副本；不写数据      |
| `cancel / closeProject / dispose`        | 撤销选择与证明并发出 abort；关闭/销毁使旧 scope 不可再用                             |

XLSX 选择后 sheet 为 null；先通过 `readForInspection` 读取主进程检查字节交给真实 `xlsx_sheets`，再显式配置所选sheet，之后才能读取预览。检查入口不能用于提交，也不能向renderer返回字节。工作表是否存在、文件是否为合法工作簿、缓存公式/外链处理由真实解析器负责。CSV 只接收枚举编码，原始字节在此不解码、不猜测。伪造同值 scope/proof 或跨 broker 重用均拒绝。

## 读取、并发与失效

读取使用只读非阻塞打开，fstat 拒绝非常规文件；FIFO 无写入者也不等待。单文件最多 8 MiB，可注入更低测试/host 上限，不可调高。分配上限加一字节并在读取时复核，防止初始 stat 后增长；读取前后核对 size/mtimeNs/ctimeNs 与实际字节数。选中后每次预览、配置和提交前读取均重算 SHA-256，不只比较 stat。

每个 broker 最多两个实际未终态的 host/FS 操作。已 abort 但未真正结束的操作继续占用槽位，不能用反复取消绕开限制；繁忙返回固定内部 busy 标签。该限制不是全应用资源配额，host 仍需唯一生命周期 owner 与全局调度。可信 picker 若忽略 abort 且永不终态，该 broker 可能一直繁忙；不能将逻辑取消写成已关闭原生对话框。

状态先失效、后触发同步 abort 监听器；异步成功、错误与重入后都核对 scope/generation。旧失败不能撤销新选择。源文件改变、变大、删除或读取异常会撤销当前证明；恢复原始内容也不能复活旧证明。调用方修改已返回字节副本不会改变磁盘或后续复验结果。

配置期间原来源仅供后发配置请求定位，不能新建预览，旧证明也已失效；后发有效配置撤销前次配置。配置失败（含操作槽已满）撤销来源并要求重新选择，不恢复旧选项。接线方应处理固定 busy/stale 标签，不把迟到失败覆盖到新配置界面。

错误统一为固定 `SourceFailure` 消息及受限内部 kind，不携 raw cause、系统异常、路径或内容。kind 尚不是公共错误 schema，由 canonical owner 统一映射。模块无 Electron import、IPC、网络、解析器或 Store 写入。

## T01 / I06 后续接线条件

1. I06 在受保护业务 IPC 的 sender/mainFrame/可信文档校验之后调用 broker。可信原生文件选择回调由 main 持有并实现可用的取消/生命周期策略；不得经 renderer 传回路径或 proof。真实原生对话框与新模块实际主进程 e2e 在隔离环境验收。
2. T01 canonical 格式与 I06 main bridge 确定唯一来源字节传输方式。8 MiB 原始文件不直接塞入旧有界 JSON 帧，本子任务不新建第二种公共协议、不复制 public contracts，也不采用未批准实现。
3. 将 broker 的确切字节交给真实解析器；解析后核对 source SHA、sheet/encoding、表摘要及规范映射定义。固定 S1 解析/映射实现应按获批候选集成，不因本子树存在而视为已采用。
4. broker proof 只证明来源选择与复验，不能代替用户确认、项目 revision、预览/映射摘要、授权或 Job token。T01/I06 必须将其与当前预览、项目与映射版本绑定；源变更、重选、配置改变、项目关闭和取消要同时撤销 UI 预览及正式任务授权。
5. `readForCommit` 返回的是本次已复验快照；随后磁盘仍可变化。正式 Job 必须仅处理该确切快照，不能再按路径重开文件；提交前仍执行真实 Store 版本/冲突校验并经唯一 `Store.commit`。本模块既不做提交，也不把文件选择取消解释为 Job 成功或正式 Job 取消终态。

需联验：真实 CSV/XLSX→预览→确认→Job→Store、源变/编码/sheet/项目修订与旧预览、正式 Job 取消/异常恢复、页面状态及原生选择生命周期。仅运行旧 App e2e 不能证明新模块正式接线。
