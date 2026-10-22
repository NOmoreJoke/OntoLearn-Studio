# 固定实验输入与 runner 准备独立窄审

结论：最终候选可作为 **PREPARATION_ONLY / NOT_BUILT / NOT_RUN** 接收；原候选的输入绑定及异常首因问题已静态关闭。**未来 metadata admission 仍 BLOCKED**：完整累计计数方法及相应分票尚未被 root 接受，本报告不授予 helper、compiler、检查器或实验执行权限，不签产物、ABI、动态闭包或 N0 通过。无需为本次准备接收而追加运行验证。

## 对象与证据 pin

只审新 runner 的控制、固定输入收据、call-plan、身份元信息、预算及有限依赖方法。供方源仅作不可变副本身份核验，不重审其算法或 I06 当前工作区。

| 对象 | bytes | SHA-256 |
| --- | ---: | --- |
| run-once.py | 29217 | 8ee38b02aefb6208b56a0621b420b84dd9d3e9b783be3523147e0d4972dd29ca |
| call-plan.json | 8824 | 64868da91b8117ca599c2d4f9362f8eaee1f78b50795758aa161e2220ef5cc25 |
| approved-identity-pins.json | 62664 | 415d45da0f9fe5de03cead96e3bc529d33d13613126c0d75ed7c7ed6ec35adf3 |
| identity-descriptor-sum.json | 59366 | b0c2fd15678081c101f659cd01d111218a06b6acea3901c9dca4dfe5c502465d |
| input-receipt.json | 7711 | c84a0e27d4b88c67260045a3f254464086f758b4c4bf3a3783d8ffbacde4605a |
| control-method.md | 6494 | edf78c7f7483a84e8b1c336fc72f9f0f37717243d75c5d8f2a742c668fe0a250 |
| dependency-method.md | 4724 | be740fa4076087a866bf122a8b70fd90a013c9d0dff693a111bc5d0a5bdad42b |
| budget-and-usage.json | 4005 | 5af2d01c236a779b87b2732f72913707dbe324f4cb8313528751aa8f19cb8bab |

初轮17份输入副本共79645B均以 opaque bytes 对其收据核同；未复审源逻辑。新增第18项为全文读取的2314B作者超票补窗，SHA `9a4e1f6312ae96d96ac82aa9e423913c45933c27bddaba00abc3b70a5a3541a2`，最终收据条目相符。准备窗口5207B及身份重分窗1646B均全文读取；重分窗 SHA `a1b4801af60abe186bf1111a4b4774e9054804b322d7fb3e48b6e1c845d8c7af`。

源固定为 `2b724f0188c233de5c8ef107d39fe0c4cb50311f` 的20278B副本，SHA `6b6ff0969396c243c425dca507d0ea05732a0edb0123a264ab834cd2531690dd`；供方过程引用为 `119a8bef651a81ae80a6ef8bacdc64d4129e5373`。本审未重新取得 live root/Git origin 或实际工具 payload 来另证这些来源，不预签后续完整 index/工作树闭包。

## 原候选问题与处置

初轮23475B runner（SHA `d196f975c75c097035b7977b605edb3d8708fb28cba56e1cdbfef51f3fff06a8`）存在以下控制问题，均已先反馈 owner：

1. identity 前门依赖未被 authority 绑定的 descriptor 元信息，而未直接核 authenticated pin row 的 device/inode/mtime。最终代码同时校 descriptor SHA 与 authority、descriptor 与 authenticated row、实际元信息与 authenticated row，保留 realpath/size/别名冲突门；不再由漂移 descriptor 为旧 payload hash 提供新元信息。
2. source-evidence 在依赖绑定时仅限读取大小，未固定其身份。最终代码在解析前要求精确3621B及 SHA `5afb7c58d5154e7bd6083a5c7e7c273e15f4e6176e5f65c24758fa54a5ccb176`。SDK root 元信息也在前后核验；它仅证明 root 元信息，不证明 header 内容或 compiler open。
3. write/fsync 与 close 的连续失败可能覆盖首因；terminal 持久化失败及外层静默 catch 可丢失原 command 上下文。最终 `write_once_bytes`/`bounded_read` 分列首因与 cleanup，`CaptureFailure` 携带 command record，terminal/build-failure 写失败保留其上下文并尝试一次有界 stderr 回退。回退本身失败、短写或上下文过大不会被称为完整证据。该结论来自文本/控制流阅读，没有故障注入实验。

复核28769B修订后，又指出未来512次前门和4980次依赖的证明遗漏多次显式遍历。最终29217B候选和文档已撤回这些充足性结论，保留后继阻断，见下节。

## 最终控制流边界

固定 root authorization 路径，要求明确 scope、source ref/hash、runner/plan/identity manifest/descriptor hash、144/48身份重分、prepared-hash metadata-only reuse、依赖模式及累计计数接受。固定隔离解释器 `-I -S -B`，helper不接收参数；身份/环境不构成 hostile-host bootstrap attestation。

固定 stage 单次 `execution-attempt.json` 以 O_EXCL 留痕，不因 auth 空白变化而获得第二次尝试。只有独占目录实际创建成功才持有 output；重复/旧 output 不被写入新 failure。dirfd逐组件 nofollow，FD退役后不重试其编号。输入源独占物化；一条固定单源 compile/link argv、并行1，随后五项静态白名单；没有调用实验产物、旧 driver、cmake/xcrun、版本或能力探针的路径。

planned/dispatch-attempted/returned PID/terminal 分开。Popen返回后先接管 pipe，再写 dispatched；未返回 PID 的中断不凭空猜 PID。超时、取消或失败只控制本次自有 Popen leader：terminate一次/等待1s，再按需要kill一次/等待1s；不扫或杀旧PID、组或后代。leader退出、EOF、timer、cleanup完成均不等于后代 drain。文件操作及Popen的阻塞不是该合作式计时器可证明的硬墙界。

总日志16MiB中预留65536B给一次紧急stderr，子进程双流合计cap为16711680B。实际read按remaining限额，不读超票lookahead，不事后截断后签完整；恰触顶也按incomplete停止。0600独占原流和语义文件名相互区分；短写、close或持久化错误停止，不自动重试。突然死亡、存储故障仍可能只留下较早intent，文档没有宣称完整durable保证。

准备身份清单的117逻辑路径、115物理对象及109模块候选，在初轮有限元信息核对中与descriptor相符；按物理key求和137864612B与owner收据一致。该数是owner已执行的一次payload hash记录，本审没有再次读工具payload，也不独立证明当时工具实际加载闭包。未来只复用已获root接受的hash并前后核metadata，禁止占同票再hash约138MB；sys.modules候选访问另有512门，transitive dylib/actual open仍pending。

## 预算、超票历史与未来阻断

显式重分保持总256MiB：144MiB身份 +48MiB证据 +作者16MiB +root另16MiB +preflight/closure32MiB。原128MiB不足3667162B的事实保留。最终身份算式为137864612 +20278 +65536 +2097152 = **140047578B**，在144MiB内余10947366B；最后2MiB为control保守保留，不是新增总池或重复hash许可。

原候选16628 metadata/8192实体池只分配一次；build累计109015059496/137438953472B，combined118760786581/147184680557B，实体521456/600000保持。原所有旧票、unknown、255超额和失败不退。

**独审自身超票必须保留**：初轮辅助表达式对117行的5字段逐次 `next` 查找，位置合6903，五次为34515候选row访问；仅此项已超原4000票至少30515。不能改记为唯一117行、0次或实体/OS I/O，也不能称当时合规。root已采用宽口径，原4000不退，另显式历史保守40000及定点复核2000，两项不可相借；40000不是实测精确访问数。新增42000只加一次，metadata2079263→2121263/2250000，余额128737；本补窗不增执行权限或byte/entity guard。

未来512前门估计及4980依赖证明已经撤回，2000/5000 repartition 状态为 `WITHDRAWN_INSUFFICIENT_PIPELINE_PROOF_NOT_APPLIED`。显式identity遍历117+117+117+117+115已达583，尚未包括其余阶段；依赖token产出3072、再次normalization3072、oldmap880、SDK-evidence候选7、normalized binding1024合8055，也尚非完整上界。最终 authority 前门要求 root 接受完整计数方法并绑定planSHA，累计preflight票覆盖准备1000与未来bound，依赖票覆盖未来bound。1467/8055只是拒绝旧不足配置的门槛，不是完整充分性证明。没有 root 完整计数收件和匹配票，**不得执行**；原6000也不能自动当作足够。当前准备接收不关闭这一后继阻断。

## 有限依赖方法与未验证项

helper仅实现 capture/reuse/defer：未来一次读取固定3156859B旧used witness并校SHA；只复用准确已知SDK/resource路径、固定源及已收四SDK pin；未知最多64条保留pending。当前本审及准备阶段没有读取该旧used表、完整索引或header payload。depfile上限2MiB、raw3072/unique1024是联合停止条件，不意味着相关metadata遍历免费。实际更小的编译依赖不能在编译前假定。

有界locator只是proposal，当前无索引读取代码；没有immutable-membership/provenance接受，不能把path/size/mtime或一次bisection命中当完整SHA成员证明。缺件先报root，不全扫、不猜offset、不自动调用新工具或重新编译。未来允许closure pending的有限结果也须root明确接受。ld准备hash、普通libSystem名字、源API声明或链接成功均不代实际selected linker/stub/archive/member/ABI/runtime证据。

## 审查读取与交付范围

未运行helper（含dry-run）、compiler、cmake、xcrun、检查器、测试、API/native/GUI或模拟故障；未重hash工具payload、SDK/cache，未重开供方算法或旧供应史。初轮仅AST解析helper文本，未import/调用它；补票后只文本/小JSON定点复核，不重做原全列表查找。

补票后新2000票的显式有限复核访问保守上界取 **1950逻辑对象/记录**，不借原4000、历史40000或root另票；包含重复小文件/源码文本复核与报告收尾。全本审两阶段应用文件读取保守上界 **2MiB**，在作者16MiB票内；这不是OS/cache/磁盘I/O实测。旧超票另按上文保留，不以新上界覆盖历史。报告是唯一新增文件；未改源、产品、锁、他人证据或提交。owner后续handoff、静态收据、manifest和index封存未被本报告预签。
