# 有限 UTC SHACL date 组件交付

产品固定为 `6891a5842302859a531cf82767c5a482417bc274`，设计起点为 `65e31d331b315c245e1f921c3558bb7886adbd27`。工作树为 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-shacl-date-policy`，分支 `feature/weekly-i05-shacl-date-policy`。本次组件实施及无窗口检查完成，供总控按固定引用收件；父功能、正式接线和发布门仍按各自证据关闭。

`validate_shacl_text` 继续要求显式 `data_policy`、`range_policy`。选择 `utc-date-range-v1` 返回 `i05-shacl-text-2`；legacy 保持 `i05-shacl-text-1`。仅扩 minInclusive/maxInclusive 的精确 xsd:date：ASCII `YYYY-MM-DDZ`、0001–9999 真实公历，inclusive 相等通过，超界由真实 Validator 产生完整报告。无时区、任何 offset（含 +00:00）、坏词法、date 参与的不兼容比较都在固定前门拒绝，不转换或改写值。当前 exclusive 继续拒绝，旧整数宽点、strict/legacy、全局语义及规则 comparator 保持。

新增双侧 bound/value 检查、实际 NodeShape→property→target/path 全值检查，以及 `i05-utc-date-preflight/1` 的固定 1000000 工作单位。遍历和排序稳定，收集、保留、排序、缓存与重复关联先付。该单位仅界新增显式 preflight，不是 CPU、native 对象、whole-worker 或物理 H 上界。

## 产品范围和政策前提同步

145 既有来源中，semantic.py 是实现 writer；原整数测试仅按总控 [单参数返还](inputs/I05-date-policy-existing-test-single-parameter-amendment.md.raw) 将第 300 行旧“未知 v1”参数变成仍未知的 v2，原断言和所有其他字节不动，改后 SHA 为 `61a3e92c298fa37483d203a8ad59dcafc9ec0ff61cf6d30b043267b7ca048c98`。其余 143 个来源只读，另加唯一 date 测试，总计 146。相对设计起点产品恰三路径；原 C 输入/goldens、旧设计、历史 pending、依赖/lock、公共错误表及正式 execution/Store/Job/selected 未改。

前后身份见 `candidates/02-source-inventory.json` 和 `02-postcheck-source-inventory.json`，最小完整产品差异为 `02-minimal-product.patch.raw`。实际三路径及有限新过程成员由 `manifest.json` 固定；不重打包旧过程大包。最新规则只复制至本过程 inputs，旧 checkout 和根规则保持。

## 实际验证

- 最终正常 `npm run check`：`runs/check-02`，exit0；1125 TS、5166 Python 通过，保留原有 44 skip 和 1 个坏 decimal 序列化 warning。该次包含原 77 DAG、26 shape、70 整数入口及 106 新 date 测试，无额外旧专项重跑。
- `npm run verify:sources`：`runs/sources-01`，exit0，核 12 归档源；这些源在两个候选间未变，没有重复执行。146 候选源实核 current=Git=运行前=运行后，143 只读等原固定来源。
- 117 个 date 观察：34 次真实 Validator（22 true / 12 false）、83 次前门拒绝（全部 0 调用、无部分报告）。原 RDF、输入、完整六字段/conforms 和压缩逐 debit 记录均保留，另由只读 stdlib 检查重建所有六字段并核账。原整数观察 78 份/14 次真实调用，shape 观察 26 份/9 次调用。
- 公开恰界输入 43460 focus、两组 6/8 个互异日期值，独立账单为 `70+23*43460+150+200=1000000`；实际 true/空报告、Validator1、余额0。同输入私有少一票注入与默认公开多 focus 超界各有独立身份，均在下一操作前拒绝、Validator0。私有注入不等于公开可调 cap。
- D1 EARLY 与 LATE 各三种同 RDF 次序，实际解析图摘要、费用、阶段和首错误同组一致：EARLY 已付 366042 后 `RDF_TERM_INVALID`；LATE 已付 1000000 后下一票 `GRAPH_INPUT_LIMIT`，均无 Validator 调用。原始正常检查双流、环境/退出和全部观察见 `validation.json` 及各 run 原件。

首候选 `1e91ad6fd4216aee6537ec2a6b5a4585bde5e97f` 的 `check-01` exit1 原件和首审全部保留：Python 5162 pass / 3 fail / 44 skip。三个失败均为新测试问题：预算两个拒绝向量证据 ID 冲突、相对 IRI 原解析阶段误认、既有 SELECT 二维行接口误认。后续只改新 date 测试，保留防覆盖断言并补独立 IRI 前门覆盖，未改日期产品源码、政策域或旧 golden。首失败不得记为通过。最终独立审查已逐项关闭三项阻断，有限通过本窗组件范围。独审首报告与最终 delta 分别为 `independent-review-1e91ad6.md`、`independent-review-6891a58.md`；最终报告须连同首报告阅读，不替代指定双方外审。

准备记录脚本曾用系统旧 Python 导致 `datetime.UTC` 缺失，未启动 npm/uv；随后以既有 Python3.12 建立独立环境，原准备说明保留。另有执行前格式/静态准备纠正，均不冒充产品运行。固定环境为 Python3.12.12、RDFLib7.6.0、pySHACL0.30.1、Node24.15.0、npm11.12.1，venv 和 node_modules 均为本树独立环境。

未运行 GUI/Electron/e2e/native/HMR、外部模型或凭据、付费、push/PR/merge；未创建或修改 Goal。T05 消费、正式执行链、指定双外审、CI/平台/真人及合并仍待后续窗口。SQLite 损坏输入保护与 HOLD、此前被拒 SQLite/heap 分析停止、whole-worker/H 缺口及未授 object envelope 均保持。

Git产品差异检查通过。全暂存原始证据检查保留exit2：三个Git原始patch、首失败stdout及该检查本身的原始诊断含原始空白，精确五路径见 `raw-whitespace-exceptions.json`；不格式化这些原件。其余新增过程按精确排除清单检查，不能将全暂存检查称为全绿。独审报告、前置计划和其读取的validation原件保留原字节；只对owner交回摘要/manifest做格式检查。
