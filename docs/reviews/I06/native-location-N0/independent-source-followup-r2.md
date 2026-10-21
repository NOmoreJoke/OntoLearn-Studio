# I06 N0：源码定点独立复核 r2

2026-10-22。结论：**本审P2-N0-01/02/03和P3-N0-04均已在新源码关闭；接口独审P2-IF-01的相关修复亦静态成立。未发现新增产品阻断。** 最终只得到待构建源码候选，不能称N0编译、测试、目标OS或技术通过。另保留一处非阻断说明精度意见，见§4。

## 1. 固定版本、实际范围与来源保全

受审新ref为 `fa1a7e4155f3afee4a1b3409f9ab8804cc620186`；首审输入仍为 `4cffd2d43b42dd1c14ae5c5745f2c705b7a6c6c8`。工作树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-native-location-N0`。只读取两个固定Git ref的产品，不读作者可变WIP。

实际阅读新ref处置 `source-review-disposition-r2.md`、九件新hash清单 `source-text-check-r2.json`、全部四件实际代码diff及相关原函数上下文、主说明实际diff；对IF-01另读最终bootstrap/hook/失败路径。五件未变文件沿用本人首审全文阅读，并本次独立比对Git字节完全相同。九件实际bytes/SHA均与新清单吻合：

| 路径 | bytes | SHA256 | 对4cff |
| --- | ---: | --- | --- |
| `packages/native-location/include/location_abi.h` | 13296 | `fc3f7983d62b0ef4f5a3a056198c00a0b971d2ae722acc33bc6f61937ec8e172` | 字节未变 |
| `packages/native-location/src/capability_core.cc` | 17304 | `eae2d2dcf4ccf1f648dbec5fdd0424c0a2dac31a94a45d493e819948f2309319` | 已修 |
| `packages/native-location/src/platform_macos.cc` | 7675 | `28f9c736e59a24cb050b706628aca26283a513fa3c019fdf58dd14e7d3f8a5be` | 已修 |
| `packages/native-location/src/platform_windows.cc` | 12506 | `bcf474ca9d9e5ce4efdf06284dd71b9504c5e69027d3a53c96fa7df56bc2b4c4` | 已修 |
| `packages/native-location/src/node_binding.cc` | 13163 | `e10e59bdb200460310489bb4fc5b8c64ab79c1b8e2cfc9e7353a10a0c8667383` | 字节未变 |
| `apps/desktop/src/main/security/native-location-owner.ts` | 12496 | `e354b0830469647d70690f3e1d6e567c816f70cbbbe5c211dabba817fa7cc8d0` | 字节未变 |
| `packages/native-location/tests/location_core_test.cc` | 24169 | `ee2460d5f4d2e6076d97622c4504734dd9f9f88e1f341358141b1f3ffbc61aaa` | 已修 |
| `packages/native-location/tests/location_child_probe.cc` | 380 | `041e60f57b34ec1b04157e73e2161b332acc3bc8f804d7f7fcd6baf575d34b9c` | 字节未变 |
| `tests/unit/i06-native-location-owner.test.ts` | 8460 | `e0946f7daf1236045d0198d989cf718ea40227d63b76e5a1407eaa1b0d501b04` | 字节未变 |

新ref保存三份首审原文，本人实核：本审r1为16508B/SHA256 `585ea61f3f808af4b8221368ee12122f6b6f928b35c8639bd5e9fb29d5d49917`；平台r1为15779B/`10dbd240a5d2580947e2a801f97b86643a003024f80b45631963efc767cad7a2`；接口r1为10473B/`cfce3c180c3388ea693192fb6234853f87ae9a3e0e576c44b61defd219dc2cc3`。没有改写首审输入、原文或把新修正追贴到4cff。

本次唯一新增写入为本文。不提交，不改产品/测试/说明/AGENTS/其他报告。所有shell显式cwd为上述新树；只有Git/文本/JSON/hash静态检查，正常exit0。没有编译或syntaxcompile、产品import、测试、native动态加载、FS/child实验、依赖安装或借旧环境；没有GUI、模型/凭据/Goal操作。

## 2. 原发现关闭判断

### P2-N0-01 · 已关闭（源码不变量）

core:40–42新增仅gate下访问的不可逆unresolved_native_open。首个open返回NL_RETAINED时，264–271先记原unknown，再设全局fence并撤销全部已发布owner，最后保原reservation。新owner在198行即拒；其他新接纳均经75–82的active拒绝，不能第二次进入open继续占满两槽。未扩预算、未减原unknown槽，也没把超时当完成。

cleanup入口仍能使用剩余一槽：close/release/poll/snapshot不要求active。原有try-lock语义允许并发caller得到busy/budget并稍后重试，但不存在第二个永久新open把其容量耗尽的路径。若某次cleanup自己的同步syscall未返回，仍保原槽，不能承诺其结束时间；这不同于原先无需再dispatch也永久饿死所有cleanup的缺陷。

Win open_record新增returned_status并保存真实返回值，区分pending与failed-status伴异常输出；两者保守留未知，但注释及主说明不再声称后一种一定仍在执行。静态存储/未知恢复仍未实现，本复核不认证实际STATUS_PENDING曾发生或最终完成。

### P2-N0-02 · 已关闭（首次close与unknown分离）

core:90–98仅用value==-1判号码已退休。即使metadata/ACL未知，仍对确切持有且未尝试close的号码做一次平台close，然后无条件value=-1；unknown以OR保留原辅助未知或新增close未知。以后不会再碰该号码，owner亦不会仅因FD close成功而成为closed。

因此原root/parent/member/observe的NL_RETAINED分支可以继续有限FD cleanup，又不抹掉ACL或其他未知责任。其他对象/pipe/child仍各自收口。处置明确固定Apple实现的acl_free实际总返回0，原首审用例是源中显式错误分支的归属推导；不能据此编造真实OS free失败。

### P2-N0-03 · 已关闭（晚返后下一dispatch fence）

core:217对owner create最终active复核；262在parent metadata返回后、下一member open之前重核active；370在匹配循环晚返后、真正child adoption之前重核；378在adoption或前一pipe返回后、每下一pipe duplicate之前重核。383仍保最终active。

过期/撤销后不再启动这些下一步新操作，已有slot/bytes/child责任和partial receipt仍归原owner；没有因stale抹去wait_owned或已dup pipe。原OS操作允许实际晚返而不被假定完成，30秒TTL也没有升级成强制系统调用超时。确定边界的执行证据仍未取得。

### P3-N0-04 · 已关闭（FIFO用途）

Mac platform_duplicate_pipe末尾已仅S_ISFIFO；socket不再作为pipe成功接纳。原borrowed FD不被关；若已dup再发现非FIFO，副本仍记录在原child槽，由有限cleanup处理。没有新socket操作/网络用途或公共child入口。

### P2-IF-01 · 相关修复静态成立

两平台fixture均新增node_owner；bootstrap在取得owner后449行将其交给fixture保存，早于hook注册和bind。430–438的fixture hook不依赖bind是否已注册自己的owner hook，先对同一原owner实际close，非OK明确abort，才清fixture。原owner已confirmed closed时重复close是core既有幂等路径，未知号码不会重试。

hook注册失败在451–455行同样核close及fixture cleanup，非OK明确失败；make_owner对失败adoption返回的非零owner也不再忽略close结果。bind早退后责任因此留在已注册fallback hook，已绑定owner hook返回unknown时fallback不能只删名字而绿色离场。

最终catch仍有保守best-effort语句，但当前会抛C++异常的new fixture/make_owner均发生在外层owner赋值完成之前；make_owner内部已把非零失败owner关不明改为abort。后续hook/bind为不抛C++异常的C/声明noexcept路径。不能仅凭该catch推导本候选仍存在已知同样的owner丢失路径。此判断只限现函数，不授权将来新增会throw步骤继续忽略责任。

测试进程abort是明确失败，绝不是release receipt；普通native host的实际image pin仍独立待交，不由fallback hook自动完成。IF-01归接口作者首审，本处只确认同一修正路径，不冒称已运行其故障反例。

## 3. 新diff与剩余证据

未发现global fence、close状态或TTL重核引入新产品阻断：fence在gate下读写，revoke仍用原静态owner的atomic epoch；owner/cap不reuse、预算未增；cleanup不受active fence阻拦；partial adoption不回滚成无资源。signal.h显式加入Mac test，修正依赖间接声明的源码精度，仍不是实际SDK编译证明。

public ABI、Node/TS和两个未改测试字节确实未变，不因本次复核要求重复无变化检查。TS parseDiagnostics0仍仅语法，C++ assertions仍仅预期layout；完整类型检查、实际exports/链接、同registry/Node fixture加载和普通host image pin都未验证。三构建文件仍归T03且只有onlydocs，不能当已批准采用。

现代码未新增确定的pending/ACL未知/TTL晚返故障测试，也没有运行旧测试；本源码修复关闭来自控制流静态核对，不是红绿实测。后续获批运行窗应保真实OS与注入分支区别，覆盖首unresolved后原cleanup、首次close/不重试、精确TTL与partial child、bootstrap/hook失败。现并发revoke仍是非确定竞争表征。

N0继续metadata-only/held-object-only、production unsupported；publish没有实际OS动作，SQLite/Python/VFS、用户目录、生产bootstrap/B-R、T01接线或新public协议均未加入。普通祖先rename/alias/held对象边界及非任意恶意同UID范围保持。

## 4. 非阻断说明精度意见

主说明§5称“borrowed pipe metadata先核真实pipe…再受限dup”。对Windows成立：先在稳定borrowed对象GetNamedPipeInfo再duplicate。Mac:118仍先fcntl duplicate，122才fstat并做FIFO分类。建议一句分OS写准确，不应宣称Mac已完成duplicate前分类。

Mac dup/close适用于普通FD，此顺序不造成Windows socket/closesocket问题；非FIFO副本仍由owner追踪cleanup，所以不重开P3用途已收窄的关闭结论，也不是新增产品P2。该文字没有放宽产品权或补任何运行证据。

## 5. 最终结论

对完整新ref `fa1a7e4155f3afee4a1b3409f9ab8804cc620186`：三项P2、FIFO P3与IF-01相关源码修复静态关闭，无新增产品阻断；建议仅补上述说明精度。首审原字节继续保留，后续若变源码/测试/工具链，按新candidate再核对应实际变化。

这不是N0技术通过：尚未构建、编译、运行测试、加载addon或取得macOS15 arm64/Win11x64实证；T03实际构建/双目标、取消/真实close/child/alias/late及全部当前未执行反例仍待精确授权。N1同build SQLite/VFS、oldholder跨崩溃、fresh/历史/B-R耐久、T01消费/dispatch/scope/永久排空、公开首IO与父I06/57P0、指定双模型/CI/正常合并/远端门原样保留。
