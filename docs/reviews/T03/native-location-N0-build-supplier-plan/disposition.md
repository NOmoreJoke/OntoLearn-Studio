# N0 构建供方方案审查处置

本轮只处置静态方案，不把输入请求或文档审查通过当作产品实现／构建／平台通过。首候选为27663B／`08a7361228c8604781f50bda5db2d6a1e5e9a1808c0bd1c2d6b5df4bf7cd70a5`，原snapshot保留；修订候选为28008B／`50cddad30ed8c7302cb0c007ccab8fa2bd71967389897d44ad3bfeee03277124`。

| 来源／意见                                                   | 处理与状态                                                                                                                                                                        |
| ------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 独审P3：§6实际有三条 `--build`，不能说“后两种”才校验输入     | 改为“各 `--build` 分支”，core／Mac addon／Windows addon都按本分支必需输入核验；无产品改动                                                                                         |
| 主作者补充：Windows Node-API import宏不可只凭 `.node` 后缀   | 新增addon目标显式 `BUILDING_NODE_EXTENSION` 与最终确认的NAPI_VERSION；依据已读node_api.h的条件声明，不让核心／测试承担Node宏                                                      |
| 主作者补充：复用core编入MODULE的PIC不能靠反向属性推定        | 新增OBJECT／STATIC core自身也显式PIC；不新增shared-core库或产品helper                                                                                                             |
| 独立初查：Node-API稳定保证有限，实际ABI／API集未冻结         | 保API8为具名候选、核心C ABI和真实符号／布局／内存释放契约pending；交根精确九路径请求，未捏造I06自有函数名                                                                         |
| 独立初查：Windows Electron专属node.lib／delay-load hook／CRT | 方案列真实现有node-gyp12.2.0 hook＋MIT原件、HOST_BINARY／DELAYLOAD和直接链接要求；实际Electron importlib／MSVC／SDK仍待供，不写已满足                                             |
| 独立初查：Node24加载不能替Electron44.9，runAsNode有fuse门    | 将Node与Electron分层；Electron未知runtime/API明确未推断，必须静态核具体binary fuse且另获headless窗口；不自动运行Electron                                                          |
| 独立初查：Mac15与宿主27、deployment与真实运行要分开          | 固定显式arm64／SDK／min15参数提案，STD_REQUIRED及链接政策；SDK可选15和宿主工具版本均不写目标15通过                                                                                |
| 独立初查：NT用户态内部API不能靠未核importlib假定             | 要求I06列实际winternl签名／系统模块／动态查找和unsupported策略；不预写不存在或错误的kernel链接闭包                                                                                |
| 实际外部输入缺口                                             | CMake未在PATH和七常见候选路径发现；Node许可／headers来源接受及Windows工具chain未齐。按子窗口选择必需输入，不以N1 SQLite／Python或Windows缺件阻止N0 core源码准备，也不称现在可构建 |

独立审查者已对三个主稿改动精确复核，最终报告11110B／SHA `fd8cc1e608811dbe9f7d7e21bce3285bac2888d771e790f36134c34fd254782e`；负责人已全文读取，R1／P3关闭、两项自查增强确认，无剩余P1／P2。结论仅接受受限静态方案，不记构建或运行通过。原报告由审查者独立写入，不回写制造全绿；source／metadata／raw snapshot不因处置改写。
