# D2 固定输入与包组合合同独立静态内审

2026-10-21。**通过；本精确文档合同范围无未关闭阻断。** 合同已具体到固定来源、只读接收集合、唯一入口、完整输出比较域、真实失败、构建与实物证据方法及下一授权条件。本结论是文档静态审查，不是实施许可、源码采用、实际包通过、I05 全算法审计或指定双外审。

## 范围、权限与最终身份

审查树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-profile-build`，HEAD `59a5abbee1dc10298511769428420bf0b53399ae`，分支 `feature/T03-profile-build`，批准基线 `5f910b52c69d86a1076b2032e5d3c63e715947f3`。已全文读取本次准备授权 3959 B / `ceb03cbf23fdde33ec71406b09be909457075a2969b08868200a91f745bf9ed1`、AGENTS `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`、common 17891 B / `e437121a08053544c2a09151ac5183baf15b5fa67a3a604891aaa9e77ba971b0`，遵守完整第九节和无桌面约束。

后续根受限收口原文 1902 B / `32d13ceac16d0db45222ac129c5a22f2c132004d5a17169e5386115fcaaa747d` 也已全文核读：固定 0475 可作技术来源，仍未授权复制、入口/build 施工或运行。主稿和 inputs 的更新与此边界一致。

| 最终受审文件 | bytes | SHA-256 |
| --- | ---: | --- |
| `docs/iterations/T03/profile-D2-fixed-input-package-contract.md` | 30281 | `ae53dfb1695a61331467e81661e82decb4e94e82929512c25259645244bb67b7` |
| 本目录 `inputs.json` | 59283 | `1186ab9af09a1fd81f116371a808ac7002c873bad087157495e41cf807957f4a` |
| 本目录 `historical-observation.json` | 13921 | `b5d16326656893cda4d4de6fdfde13ebe8fe9a4fa80110a170a8e8d07439933f` |

审查仅使用 git show、文本/AST、JSON/ZIP 和哈希读取；未 import 产品、parser、T01 或 PyInstaller，未执行 probe/tests/安装/构建/包/GUI/网络，未复制源码。唯一写入本报告；仅格式化本报告，不改主稿、产品、配置或历史文档，不提交/推送/切分支，不恢复 blocked Goal。

## 固定来源与精确集合

逐项按清单 ref/path 读取 Git，97 个带 ref 的文件记录全部 bytes/SHA 相同，所附 AST imports 与实际 AST 一致。另核根收口及三份本机 PyInstaller 工具源文本 bytes/SHA。关键来源固定 `0475d0ec6c486a63c7e8f62f11f35181da6b2576`：

- probe 13391 B / `2b2dabd91745b4b4c2a3fad39b6386e4edd985189336bf029d9b07a638fc7bf6`；合同 6295 B / `471ce2922e301322b33791d953fd86e05864db180921cdbcf607e2d2b80fb7d3`。
- 执行资产 1839011 B / `6c6ffc3a1a57d1817583c0a71d24e2847cc5d2d673848878c6e6e72dfe6c39de`；candidate-inputs 32937 B / `aa22b70ce65f27c16361b04f32c74a9e2d8de105d1611d70d6e5338f2e4e7b86`。
- 七 quality 文件与固定 dbb、0475 对应路径逐字相同。六 rule 模块的计算闭包闭合；父 `__init__.py` 的旧 lazy exports 被明确排除，不误称整个父包无外部依赖。禁止 definitions/planning/rule_revalidation，不将 T05 新 API 自动纳入。

十 I05 源的真实 imports 落在拟收集合、七模块及批准基线；semantic_samples 是明确额外收集的 legacy 回归依赖，并未包装成另一入口。主稿保留动态 resources 的 contract Python 文件、八 JSON 及完整锁，真实运行资产只新增一份。资产与原 projection manifest 的 JSON 值相等、bytes/SHA 不同；递归静态检查只见 `expectedIncluded:false`，未见 expected 数据键。

22 条运行差异集合无重复，确为 10 I05 + 7 quality + 1 资产 + 2 D1 + 2 D2。24 条 source-only 验证提案确为 15 tests、7 fixture/oracle、2 binding docs，测试的实际文件读取与这些明确依赖及继承的 I03 文档相符。19 origin refs 被单列为追溯，不作为自动接收或打包项；外部 checker 不作为 pytest/产品模块安装。

实际 D1 两文件仍逐字 fd87（pyproject `bcc8825b…8365`、uv.lock `86dfe82d…e8b73`）；D2 两文件仍逐字 5f。九 contract 和十四基线引擎源/data 在 0475 与 5f 相同。可沿现树组合的判断有实际依据，但须另获根精确起点、接收及两文件施工授权，不 whole-commit 接收，不消费其他树环境或未批 T01 runtime。

## 唯一入口、预算与历史事实

固定 probe 的 main、locator、常量、identity 与异常路径已全文核对。合同规定包仅单 flag 调 canonical `main([])`，保真实返回值；多 token、前后混用及 equals 变体均先拒绝，不落入旧默认服务。拒绝 stderr 明确为 ARGUMENTS 文本加一个 LF 共 32 B、FAILED 文本加一个 LF 共 21 B，stdout 空；不接收任意文件、JSON、脚本或 URL。

单次 8 MiB payload+rows、输入 2 MiB、集合 64 MiB、83 条及内部 120 秒边界检查分域准确。合同另要求真实进程外部硬 120 秒、超时保原字节/归属进程组，不把边界检查说成 CPU/内存抢占或取消能力。未要求增预算、删源/尾行/false match/head 或补规则取 exit0。

独立读取固定 runtime ZIP，核五个历史成员的 bytes/SHA 与原 manifest；30/31 execution 逐值相同，30 stderr 空、exit1、未超时，31 checker exit1。83 case 的顺序、唯一性与资产一致，历史摘录的 status/error/diagnostic/reason、identity 均与实际 30 JSON 相同：78 success、4 resource failure、1 not-executed。

对 78 成功项仅用 JSON/hash 静态复核，payload 与 rows 的 canonical digest、rows 全文拼接回 payload、单次总字节和 cell 长度均一致，无缺尾项。31 comparison 的成功项映射汇集为 49 个图，未把 coverage 的候选可映射 51 图当成功覆盖。24/40 matches、16 heads/R04 叶的范围与固定根收口一致，本轮不另审整个 oracle 或算法。

四 E.5 failure 保留精确 public error 与 diagnostic（前二 semanticInput/RULE_INPUT_BUDGET/R-risk，后二 semanticWork/WORK_LIMIT/null）；transfer:repair 的 fullOriginalInputContext=true、eligible=false、定义为空均来自真实资产，不能将元数据或空规则变成执行通过。源/包重现这些结果时应保持 exit1；一致失败不等于业务通过。

## 等价域与外部 oracle

业务 JSON 仅允许两个 frozen 布尔与七个 sourceSha256→null 路径差异，先核预期值再剔除，未删除整个 identity。其余新旧字段、数组顺序/重复、精确类型、完整 payload/rows/摘要、来源、true/false matches、head/basis/error/diagnostic 全深比较；missing/null、bool/int、数值字符串均不合并。八库、九 contract hash、完整 lock hash及实际 implementation 三字段被保留为约束；默认 i04 与 profile finite7 未混为公共注册身份。

外部四依赖有固定 ref/container/member/hash：独立读取 original-evidence.zip 的 compare_oracle.py、input-manifest-v2.json、project_inputs.py，三成员 bytes/SHA 均吻合，另核实际 oracle 文件。checker 实际静态依赖为 stdlib，并只调用 projection 的 definition 映射；合同明确不调用 project()/Inputs、不重生成输入，故不要求自动接收十九原件。checker expected 留在产品外；同源/包分别执行的完整 argv、short-no-revision、各独立输出/coverage/真实 exit1 已具体写明。源码/包等价与外部数学对照分别记录，未相互替代。

## 两文件构建及实物证明方案

施工仍仅 build-engine.mjs/entrypoint.py，D1、业务十源、七机制和资产原字节只读。构建输入 provenance 可在已授权 build JS 内由 fs/crypto 与固定元数据读取产生；它只作输入承诺，不自报最终 engine/PYZ 身份，不引入 C4 脚本、另一业务 probe/matcher 或 Store/Job 写入。

十+七 explicit canonical imports、三库 collect-all、八库 metadata/data/license 及真实 TOC/资源核验足够具体；保 rdflib 基线收集，禁止 collect-all quality，未把 venv 有文件说成包中有文件。实际许可相对映射及不足时返 owner/root 的处理明确。

已静态核本地固定 PyInstaller CLI/reader 源：`-l -r`、CArchiveReader/open_embedded_archive、PYZ raw 提取等方法存在。合同补充在 reader 转 dict 前统计原始 PKG/PYZ TOC 重复，避免映射覆盖遮蔽重复。按实际 Python/优化编译但不执行、仅递归规范化 co_filename、保其余代码元数据与常量的指纹连接具有可实施性；源码 .py、marshal/PYZ、engine 原 hash 分域，未知额外变换须停下精确审查。规范名唯一、全归档指纹、实际使用路径约束与完整输出共同提供身份依据，没有声称模块名字本身证明一切动态 alias。

最终应用 resources 内实际 engine、onedir 树、资产/锁/contract/metadata/license 与输入/TOC/外部收据绑定的链条明确。旧 contract/resources/storage CLI 同组合源包回归也被保留；storage 耗时/RSS/页数与数学/查询字段分开，不要求环境度量跨运行相等或虚报提升。

## 意见处置与最终边界

P3（已关闭）：初稿 §1.2 把 canonical `__init__.py` 写成 Markdown 加粗 `init`，会丢失实际文件名下划线；现已改代码格式，完整路径清单一直正确。审查期间又核对拒绝错误的换行/字节表达，最终已显式写一个 LF、32 B/21 B，消除文案转义歧义。无剩余修改要求。

最终结论为此三文件合同静态通过，可交根评估下一精确授权。没有采用源码、实施两文件、运行产品/依赖矩阵或生成新包；后续真实组合正常 check/source12、外部 hard timeout、完整源包及 oracle、归档与最终应用内实物、缺失/负例副本授权仍须实际完成。两目标平台/干净设备/窗口/B1、指定同版 ZCode/MiniMax 双新审、CI/正常合并/远端及完整父验收门均保留；本轮不替代根 I05 最终审计，不恢复 Goal。
