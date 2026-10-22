# Mapping P2 两项全新完整审查预备包

本包只准备新树、原字节输入、独立依赖环境与完整审查提示，不创建应用任务、不占用CUA、不启动检查或打包。根已在I05原120秒full_run自然exit1后释放CPU并解除安装暂缓；本线不重未变pack/check，私有provenance真实build/CLI仍无执行票。GUI由T08使用，新包就绪后排队。目录或提示存在不等于实际外审已经发生。

产品候选固定为`da1795b20c3c0d47ae975fe3371e802092a4b429`；现有完整证据为`4ec492f07d261164283a939c65b5e835c30e561e`。批准base为`5f910b52c69d86a1076b2032e5d3c63e715947f3`，本次修复base另列`30319412daf8ae4745987babf7bbed93c53b6b42`。新包仅追加文档，不改变两产品或任何其他工程字节。两棵新detached树必须核验同一个完整固定ref；最终精确ref由后续独立派发索引绑定，不能拿产品SHA代替实际HEAD。

## 完整范围

工程范围为完整候选所有tracked工程、工具、tests、fixtures、配置、依赖锁，以及docs中的可执行证据工具（包括.py.raw/.input.py.txt）。原`ed9cef968b17a1edefc0977b509906fb9f81a336`共享包、mapping原866项输入、历史阶段矩阵及原始失败/验收继续有效；新包不是只审两产品delta。原866中缺失的11份T03历史文档已按固定blob原字节恢复。仅原始受限SDK/witness/descriptor/index身份payload及STOP现场保持原禁止，逐项标明未读/未验证，不能据此排除父门后给整体Pass。

需求范围为完整PRD文件、完整59条FR（其中57条P0，另2条P1），全部附录C–G与§10–12、M-01–M-06及M0 S1/S2/S3/C1/B1/U1。FR-300–304是映射局部定位，不是整个审查范围。完整requirements.csv与50条acceptance-baselines已保留原字节。完整tasks.json/plan等为控制资料快照，T03其中旧native树、旧HEAD和旧状态是历史记录，绝不是本次工作目录或执行授权；本次只认派发索引指定的新树与精确HEAD。

历史原报告按Z1–Z7及F01–F11共18个真实编号逐项复核。没有可确认的“原15问题”清单；该称呼是根已纠正的口误，不能据此造清单或验收门。18编号不等于18个缺陷：部分是正向观察或报告统计错误；旧P1/P2是证据事项标签，不是缺陷严重度。原报告、主控技术处置和新模型判断分别记录，不能将主控草案当新模型结论。

P2证据覆盖新实际包的固定17项（旧11项保持、追加6项），三类额外参数拒绝、source优化模式、三模块source/PYZ绑定、完整440项engine清单与74份原始双流/命令收据。原始包/进程发生在原P2树，不能写成新树重新构建或执行。17项共用一次source/一次package进程退出码，逐case独立exit仍null；socket仅三API在固定解析期间的累计计数，不是全OS网络证明。外部引用两个成功case的column2是固定B2坐标；四CSV case才是实际issue完整定位。

## 输入及证据分层

- `legacy-fixed-package/`是mapping及共享历史材料的原字节副本；其余原包入口仍可由同一Git仓库对原固定ref只读取得，不读取其他工作树当前WIP。
- `control-snapshots/`是当前共同规则、操作政策、权限及完整需求/计划的原字节快照；不改写冻结历史提示，不据其中旧路径切换现场。
- `p2-original-raw/`保存74份已执行原件的精确副本；`raw-relocations.json`只添加定位关系，未改原收据中的历史路径/时间/argv。
- 同树`mapping-followup-1-completed-20261023/`保存两个历史完整报告及技术处置草案；本轮双方任务/报告仍完全独立，不能读取对方本轮意见或运行状态。
- `history-agent/`提供真实18编号与完整需求覆盖索引，不替代原报告、PRD正文或源代码全文。其“未安装”状态仅指该独立文档子任务；整个新树环境实际安装另据owner setup收据。

新树AGENTS使用15147B / SHA `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`保护覆盖并保持unstaged。依赖环境、缓存、tmp/raw/report/metadata写面按各树隔离；独立安装是否成功以各树owner setup收据为准，不借原树node_modules/.venv或可变运行库。实际任务ID、模型/思考/权限、lease及终态均null，之后必须由原owner真实创建/读回，不伪填目标设置。

本次owner已完成两树各三条安装命令，六条均exit0；未运行产品、pack/check或GUI。`owner/setup/`保存命令双流、收据和环境原件；两实体node_modules/.venv的普通文件inode集合无交集（只做lstat元数据检查，基础Python链接另披露）。安装实际开始HEAD是4ec，随后只增加本包文档，不伪称在后生成完整ref上重新安装或验收。

没有新产品运行；旧真实检查结果只作为已固定历史证据。两项指定任务均需新建并完整终态、全文读回及逐项处置，旧303两任务及本地Codex独审均不能继承为新候选双Pass。push/PR/合并、GUI/两OS、父业务及生产门分别保留。
