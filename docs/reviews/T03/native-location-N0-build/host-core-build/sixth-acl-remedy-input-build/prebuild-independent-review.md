# 第六新输入：ACL两源采用与构建前独立审查

2026-10-22。结论：未发现阻断当前候选执行授权内唯一第六次新输入构建的问题。真实授权／两源采用／锁产品链、provider九pin、完整12及锁八叶差异均核同。仅接受固定源受限采用与构建前静态检查；不能由公开源码、fixture源码或本报告推定installed libSystem、ACL状态、003根因或实际运行已验证。三份Darwin fixture此刻只编译，不设置ACL、不读取见证。

## 授权、源闭包与ref链

已全文读取 `authorization.md.raw`：4056B／SHA-256 `e4d560d58808eea8b83498384ea3285eb074e6765d3f9d873baf42e19c33f57a`，工作字节与真实提交 `ad93c6a744bf243633ed3f265816454630c32923` blob完全相同，父级8528ccb3d68de4f31ee1e10bd984084e0f7f418c，提交只新增本授权原件。

已全文读取过程中的 `I06-source-root-closure.md.raw`：1494B／`14979837ba1a6943aafb76a6a2967796a9b896c5b569a66245419c407bf36cdc`，与授权receipt固定值相符；它是过程副本，不属于auth commit，本审未作错误的authblob要求。根已收件8750B源码审查等材料，本审不重读长审或旧五轮大包，不把受限源收件变成API/ACL运行许可。

真实链为ad93c6 → `2ce18bb20aace0f4434a97d691afdf08f4413b89`（仅platform_macos.cc和location_core_test.cc）→ `3e6e5ddd14ae08241f2f26f8b30e0a765ce70077`（仅toolchain-lock.json）。没有wholecommit采用供方或扩改T03构建算法。

`provider-source-after-and-static.json.raw`：6514B／`afceaf726ce8105d274e1b26b928e07d6bdfe21e0ffedae5692c16e076eb2667`，逐字节等9509d02790f9a79905371c5183be16cab99f5114中指定acl-null-003-remedy-source/source-after-and-static.json blob。按实际schema将nineSourcePins[].path与after合成九pin，逐项等当前锁source.files及完整12前九项；没有误用旧allNine schema或before值。

独立逐Git blob比较1217e0f63a9c62b72e01046ef5fbc5c53434251a与fc9853f3521faced3a3b88ab8254310c9748a6a6：仅Mac与core_test变化，其余七源逐字节相同。当前工作九源均等1217，两个采用blob也精确等1217：

- Mac12579B／`d944a4901b6d3f516f18ab436aed9ec56a78eb1bbd12d1949ebf6a6e171825ce`。
- core_test37928B／`2517eb970ef39f37dd99ca9945909331df937d4dd43ce53b74eb722bf47a7053`。

## 受限源码差异

已全文读取采用patch：16325B、360行，实际SHA-256 `21cad57babde64a45d0947c314cbbc1660d635112ec7003746a069e3456b6160`。用上述两份新旧Git原字节按固定labels重建unified diff，结果逐字节等该patch，未夹带第三源或本地WIP。

Mac差异限于metadata新helper/资源收尾及原platform_metadata路径：fresh filesec、同held-FD fstatx及owner/group/mode完整性检查、UUID envelope/presence、ACL获取/有效空规则及失败/释放处理。原非metadata区域保持。输出metadata在收尾成功后发布；任何ACE拒绝、未知与释放失败不当成功。这里仅确认所采用内容与已授源增量一致，不重复旧算法审查，也不独立证明公开Libc推论等于本机installed实现或API运行结果。

core_test新增membership include、Darwin限定资源/owner/witness/setup helper及darwin_acl_cases调用。源码分别描述自然空ACL状态（按实际presence报告absence）、有效单ACE拒绝、仅duplicate前门invalid-FD；明确setup／witness须成功，源码本身不能证明本机覆盖absence与present-empty两种状态，更不能把invalid-FD当metadata覆盖。新增Darwin调用放在原case序列前，原case主体保留；本窗口仅将其作为编译输入，绝不执行ACL设置、见证读取或生成的proof输出。

provider内正常637TS／1052Python／native addon skip等是I06既有源证据，不是T03新执行，也不编译C++。既有静态输出上界或资源推论不代替runtime成本、内部资源硬界及installed libSystem身份。003实际acl-null/errno2仅定位旧空返回，根因及旧drain未知继续保留。

## 完整12与锁八叶

`approved-input-manifest.json`：2545B／`a731bb8a9fb05da24e535f238fc532f8ccd748196cef93112f165200c069b0c8`。12路径唯一；本审逐项只读计算当前工作文件bytes／SHA，全部吻合。auth/adoption/product/source/process各ref与真实对象相符。

当前锁10475B／`0ed8ddd79a31439086ef3fd5cabbb750ccaffc48024ea0e1a64ab2cb1f608d07`，工作字节等3e6e5d产品blob。相对8528旧锁，拒重复键JSON解析和递归全对象比较，实际恰八叶：source.ref改1217；source.files[2]的Mac bytes/SHA；source.files[6]的core_test bytes/SHA；source.approval.reference、Darwin toolchain approval.reference、Darwin/core execution.reference三项均改真实ad93c6。approved与其余权限、七源pin、API3/contract/staticassembly、供应descriptor、environment、selector、flags和限额不变；Node/Win/addon/fixture-addon未扩大。

锁与原indent2+LF序列化逐字一致；10474→10475的唯一长度增加来自Mac bytes 8670→12579多一位，其它固定长度ref/sha及五位test bytes不增加长度，没有额外format变化。

CMake19815B／`f2b5522b92c5dfc9724b95c35b876ce5015a4955385f614a6da20fb9bce57645`、driver30056B／`ca4ef93024762ae5dfd3dc95133f8ab28ae2e63048af0b3a658bfeb98f62045c`冻结。本审不维护或重审其算法；原13命令、parallel2、每命令600000ms、shell:false和固定供应/DEVELOPER_DIR保持。

## 已存静态结果与费用票

已读锁JSON/Prettier回执及完整原流：exit0、stdout66B为格式通过、stderr0B；本审另独立解析锁。未变driver语法证据复用，不重跑整套check。`static-validation.json`：309B／`87aac2f97418f624bf870821620a92b39e84572ae0d225fcc9a6b9ac82d44a2d`。owner的AGENTS/common同字节复用及新hash由receipt保存，本审只核该小receipt，不冒称新读长规则。

`read-and-record-plan.json`：1541B／`d0fbca49d781ca279cfc6c07f84359521936d7c43478f8f217d35110534de8ce`。独立核算90848349888+17755667816+134217728=108738235432B，低于128GiB=137438953472B，余28700718040B。旧供应9745727085B独账保留，combined声明118483962517B／guard147184680557B。两源净增3909+7891=11800B及小锁/源静态读取在新128MiB预付内；估算不是OS/compiler/loader实际I/O或性能。

实体427720+85544=513264，低于600000。metadata1784519+171088+2000+15000+15000+10000+15000+42772+256=2055635，低于2250000，余194365。root独审与作者票独立，所有旧消费、预留、超255/关闭界及unknown不重置或释放。

条件批准index票只在真实used出现新增全局依赖时启用：最多一次resource/SDK批准记录流42772访问，combined文本<=64MiB且已含128MiB预付，仅保新增<=256 selected身份；本prebuild没有扫描。无新增则不做pass、票仍不释放；超界、新tool pin或未知路径必须先报具体差额，不能自动扩guard、换供应或第七编译。不能在当前阶段预称membership等真实dep无增量。

本审只读完整12小文件、九源新旧18个Git blob、两个采用blob及有限auth/provider/lock/patch/receipt。本次主批应用读569889B，连初始patch/小文档等累计保守小于1MiB，低于4MiB；宽逻辑访问保守上界768，低于1000并计入pre2000，包含360行采用patch及有限对象/小记录核对。没有读SDK、供应metadata全池或8750长审，没有编译/native/API/ACL实验或工具探针。

## 执行边界

owner固定新HEAD及完整12后，可按真实新授权直接一次原driver CLI；只configure/try_compile编译链接并构建core与child，禁try_run、CTest和任意产物执行。失败保原件收件，不修I06源消错、不自动第七次，不新增API/ACL运行许可。成功也仅built-unverified/NOT_RUN，实际新增依赖、静态产物与预算需后验独审。

本审只新建此报告，无产品/源/他人文件修改，无GUI/native/e2e/HMR、模型/凭据/付费或桌面动作。不扫描未知fixture/PID或重启已拒绝SQLite线；目标OS/EXCL全路径/wholeH/父N0及指定双外审、CI、真人、远端等门保持开放。
