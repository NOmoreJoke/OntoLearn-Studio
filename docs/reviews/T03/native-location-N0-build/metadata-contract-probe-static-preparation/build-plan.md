# 单用途 metadata 合同实验：T03 静态承接方案

2026-10-22。状态 STATIC_PREPARATION_ONLY / NOT_BUILT / NOT_RUN。本阶段是文档方案；没有实验源码、源码采用或新产物。需求只取根静态窗口及其指定三份根记录、固定7ea3的两份实验文档；复用第六轮固定锁描述和累计账。本阶段不读取I06当前实验源码/半成品，不核其存在状态，不创建record/run/build目录。

## 选择与责任

建议在未来精确窗口中，用已核Darwin工具链对一个冻结实验源执行一次直接clang++编译兼链接；不经过旧core CMake/driver、不重建core/addon/产品包，不链接产品owner注册表。这是一份待root批准的单用途编译方案，不是第七产品构建许可。旧pair及12项产品输入继续冻结，不能充当新实验产物。

未来唯一构建/过程writer为T03。建议唯一新执行脚本路径 `docs/reviews/T03/native-location-N0-build/metadata-contract-probe-build/run-once.py`，只容纳冻结plan的一条固定命令、输出捕获和身份记录，不接受用户路径/任意命令/API参数；本轮不创建脚本。脚本和解释器的固定bytes/SHA、日志上限执行方式、timeout后未知/drain处理必须先由root在未来窗口明确接受。I06唯一编写实验源；T03不修其源码、不修改实验判据。root转交冻结源及独审后，T03才能消费。若源不符合独立单源/依赖要求，回报具体缺口，不就地适配。

源内容拟在未来窗口从root指定Git blob精确物化到独占输出的input子目录，仅为编译输入副本；保留供方原path/ref/bytes/SHA和副本相等记录，不改packages下旧源。是否准许这一物化动作须写入未来窗口。本轮没有执行git show读取实验源。

## 已收描述与待补输入

第六固定input bfe137f371361f9fda446d5cbe6b3079c5433ee5的锁10475B/SHA256 0ed8ddd79a31439086ef3fd5cabbb750ccaffc48024ea0e1a64ab2cb1f608d07作为复用身份，见inputs/sixth-fixed-toolchain-lock.json.raw；本轮只读该Git metadata，没有打开compiler/SDK实体。

- 已核cxx描述：`/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/clang++`，realpath为同目录clang；124676976B/SHA256 ee029330bf58ab6e481385f4237cc54602eaa8b81526242e5c5ab5b76e8c5a7e。未来只按同一physical内容核一次，不因c/cxx别名重复算免费读取或无条件执行。漂移即停，不换工具。
- 既有SDK描述根 `/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk`，Darwin arm64、C++17、minOS15.0沿第六已收静态证据。SDK描述/版本是固定构建输入，不等于目标OS或installed实现证明。
- 新源码ref、过程ref、唯一源bytes/SHA、精确main/entrypoint、实际include集合及本地include闭包：全部 PENDING_ROOT_TRANSFER。当前不猜头文件/extern符号清单，也不预填H/A/offset等布局数字。
- 请求mask/4字节packing、REPORT_FULLSIZE/PACK_INVAL、4096B buffer、signed offset/溢出/对齐/完整长度、NOACL先判、H/H+A精确长度、实际属性位和标量一致性：以固定7ea3合同为需求，源码及目标SDK映射证据待root交回；尚未核实现。
- 必须收到正式目标定义到源码字段/语义的精确证据：ALLOW→PERMIT，目录/文件权限及owner qualifier、零额外flags；编译期断言清单/来源/目标布局待补。数值偶合、运行时sizeof或link成功不关闭此门。
- 实际工具front-end/backend、链接器/运行库输入的已批描述与本次是否需要新增pin，及wrapper/interpreter身份：待精确窗口逐项核定。锁中的system library名字不是实际选中tbd/archive/member闭包。不得以现有libSystem名字预签新API导入。
- frozen source须提供需要静态核对的符号与禁止项清单，以及已有官方SDK精确片段/记录的pin和定位；最终expected symbols只能在源码固定后建立，不能从本提案猜出。

## 命令模板与输出隔离（未调用）

未来单次构建拟为如下模板。尖括号字段均未绑定，当前不能执行；最终argv、cwd、env、所有输入pin、脚本pin和输出独占检查须在root精确窗口重新冻结。

```text
<fixed-clang++> -std=c++17 -arch arm64 -isysroot <fixed-SDK-root>
  -mmacosx-version-min=15.0 -MD -MF <exclusive>/probe.d
  <exclusive>/input/location_metadata_contract_probe.cc
  -o <exclusive>/artifacts/location_metadata_contract_probe
```

模板不添加NDEBUG或其它改变新源检查语义的宏；若冻结源码另有要求，由root后继精确窗口决定。仅一个源、一次compiler调用（该调用内部compile/link）；不调用cmake/xcrun/gnumake，不加产品源/owner注册表、动态fallback、临时能力探针、版本命令或额外configure。最终flags与冻结源/SDK要求不合即回报，不自动加宏或库重试。shell不拼接未知输入，保存精确argv。编译内部进程/系统库不是“只有一个PID/一次API”的证明。

未来隔离根拟为 `build/native-location/metadata-contract-probe/darwin-arm64/<approved-input-digest>/`，digest涵盖新源、build plan/script、工具/SDK描述、flags和授权ref。其下input/artifacts/tmp/编译双流/depfile/static-evidence完全独占，要求不存在后才创建；本轮不探查或创建。不同于旧六轮core树，不覆盖旧pair，也不预建I06 record/run目录。

拟环境为精确allowlist：PATH=/usr/bin:/bin、DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer、LANG/LC_ALL=C、TMPDIR=该次独占tmp。不得继承CPATH/CPLUS_INCLUDE_PATH/LIBRARY_PATH/DYLD变量或复用用户HOME作为任务变量。环境和compiler临时文件行为需未来plan实录；并非完整编译资源沙箱。

一次调用拟timeout600000ms、parallel1、stdout/stderr合计不超过16MiB；捕获方式/超限和超时后的处理必须先固定，不能靠事后截断签完整。任何失败/超时/输出不足均冻结原件、保留首因和未知，不重试、不自行kill/cleanup旧PID、不修供方源。timer、leader回收或稳定日志不证明drain；内部heap/OS I/O/进程资源硬界仍未知。

## 依赖与静态验证的有限门

复用第六已核的880-path证据和既有批准index/source descriptors，只把其作为已有身份链，不在本静态阶段解析3MiB used表、扫旧205件或重读42k索引/SDK。未来在源码固定后才建立本次实际头/符号需求；源码include推断不是实际depfile。

建议未来实际depfile限raw tokens≤3072、唯一路径≤1024；按旧已审核Make转义规则解析，保存原depfile和归一化差异。只复用能精确对应的旧witness，不按路径前缀放行。新增记录≤64、定位文本≤512KiB：root须转交已批准记录pin和准确offset/原行；T03只做有界定点核对和获准身份操作，不重新扫完整index、不用substring全文件查询。缺定位、未知header/tool、无法对应的依赖均停止，保具体unmatched，不临时扩大查询或重建。

未来应用SDK/resource身份或pin操作另设8192实体保守票，实际已知完成另记；该实体票不是额外metadata票，所有应用记录访问仍计入16628的相应preflight/depsAndBinding等分项；所有cap同时适用，任何一项先触顶即停止，不能保证每张票都能用满。不把编译器内部header打开次数当已观测，也不称此票可限制compiler内部访问。定点原行/目录元信息不证明compiler真实open。新源≤128KiB及上述限额都是待root批准的停止上限；超限需报告缺口，不是擅自压缩源或裁剪记录。

成功后拟保存一次真实compiler命令的planned/dispatched/result/原始双流、工具及源前后pin、产物bytes/SHA、原depfile与绑定、精确链接driver argv及其观察边界。仅在明确的静态许可内对新产物file/otool/nm核格式/arch/minOS/loader/import/rpath/符号，工具沿既有pin并先核；拟五条file、otool -L/-l、nm -m/-u，禁止执行新产物。stdout/stderr路径用数字+语义标签保证casefold唯一，保留0B及原字节。

真实dep和符号结果必须由独立窄审核本轮差异，root再核新产物/有限manifest。若源带静态断言，实际compiler接受仅证明此固定SDK/ABI下断言成立；并不证明runtime解析、ACL/API、installed libSystem、实际选中linker输入闭包或目标双OS兼容。

## 累计成本与候选上限

数字以budget.json为可重算账，不量化OS I/O。第六保留build声明108738235432B、guard137438953472B，余28700718040B；old supply9745727085B独账；combined118483962517/147184680557。实体保守513264/600000，已知完成470492（首CMake unknown不当零）；metadata2055635/2250000，余194365。旧六轮、003/004失败、255超额、未知drain及所有未消费但保留票都不抹去或退款。

本轮新增静态准备预付8MiB、7000 metadata（owner2000/作者独审2000/close1000/root另2000）；实体增量0，从原未分配余额分配，guards不变。分配后build声明108746624040B/余28692329432B；combined118492351125B；metadata2062635/余187365。8MiB各票owner2MiB/作者2MiB/close2MiB/root另2MiB，不借旧128MiB票。

未来单用途构建仅提出、尚未扣作执行或获许可：应用读取预留256MiB（源/工具身份128MiB，证据/产物64MiB，作者审16MiB/root另16MiB，preflight/收尾32MiB）；metadata16628、SDK/resource实体8192，分项见budget。当前余额在纯算术上容纳这些候选票；若以后另授并分配，build余28423893976B、metadata余170737、实体余78544。固定compiler124676976B小于身份票128MiB，但其它必需工具/源一并求和仍须前门核；超过任何分项都报准确缺口，不挪票或默加cap。这些是应用侧声明上限，不是compiler/kernel真实I/O/heap/CPU/loader硬界；拟命令未执行也不是未来0成本证明。

不能复制旧全pipeline并附条件全index查询：仅两前门source/sidecar171088+全index42772=213860 metadata，已超出本轮准备后187365余额26495，且还没算任何新build审查。该反例只说明不能把旧重扫办法免费带入本实验；不是本轮执行记录。若root要求全量前门或新增权威取证，必须另列缺口重审，不通过改分类解决。

## 后继门与停止点

1. root接收I06冻结实验源、静态独审、source/process refs及headers/symbols/layout映射证据；在此之前T03不消费半成品。
2. root转固定输入，明确是否接受独立精确命令/输入副本/唯一过程writer；补齐所有pending和成本前门，给本实验单次精确构建/静态检查窗口与预算。旧许可不继承。
3. T03仅按该新窗口真实构建一次、封存原件及有限差异、独审，交root核新产物。失败停止，无自动后继。
4. root收新产物后，由原I06另授精确一次CLI及setup/read/cleanup范围。T03没有runtime/API测试或修改实验判据的权限。

未来实验仍是两个自有fixture/五样本、固定4096B buffer、fstat≤7/fgetattrlist≤5、最多一次owner UUID获取及受检收尾；输出设计≤1018B、cap4096B/行≤96B。全部三empty及两单ACE和收尾全合格才eligible；缺位/占位要放弃当前路线，不能用UNSUPPORTED/改FD/换环境求绿。上述仅复述冻结合同，并非源码已实现或实际调用已发生。

本静态方案不改变T01 HOLD、旧失败、SQLite/heap/OS资源拒绝线、原双OS/EXCL/父N0、同版指定外审/CI/真人/远端门；无GUI/DB/付费/push/PR/merge/Goal变更。
