# MiniMax 新507报告收件与逐意见处置

2026-10-23。原SID `mvs_be9afd3ec94f4d05935086be63c127b7`、原turn `9faa1d9d-6d75-4958-beeb-9c0cc82051d7`；strict四scalar观察为completed，updated_at_ms=1792693627829。原报告38855B/418行/SHA `7a63268ae5ef0c1ea078180406dfeaa59f820f13b5bbedf73afd9564ccb2d765` 已分五段全文读取并原字节归档；31成员归档包含十组命令收据/raw、反例、首败说明与覆盖后的设置收据。原报告不改。

模型对完整同507有界S1给出Pass、无P1/P2，四P3关闭，历史10closed+1partial在新provenance下可独立复验；该模型判断与过程合规验收分开，后者交总控。下面逐项处置覆盖原§10 N-1至N-7，不遗漏第七项过程事件，也不沿用结尾“6项”压缩计数。

| 原编号 | 核实与处置 |
| --- | --- |
| N-1 环境配方P3 | 首次完整check确有exit1，lint/格式/类型通过后Vitest缺rolldown native binding；锁内`@rolldown/binding-darwin-arm64@1.2.14`补装后完整check exit0，TS719/Python1167、SSR14/DOM5。保留两次完整raw与pack/install各自完整收据。不改固定507验收或安装历史，当前环境补充以本表和原argv为准：以该树`.venv/bin/python`调用日志helper，系统python3.9不支持datetime.UTC；绑定缺失时仅补装该树锁内平台包，不删改锁。报告将原因归于npm optional-dependency bug属于其推断；本方仅确认实际失败及补装后通过，未独立证明唯一根因。后续owner维护安装说明时纳入，此轮不为流程建议重开产品候选。 |
| N-2 历史证据定位P3 | `evidence/final-verification.json`及`verification-summary.json`保留早期candidate原件，不能作507终态。507真实owner终态在`p3-repair/verification.json`；本轮指定双审终态在本目录索引。已在status新增当前入口及历史定位说明；不改原件。 |
| N-3 CSS作用域P3 | 两全局选择器当前无已知同名冲突；保留父App样式接线处置，未修、未关闭。 |
| N-4 staleReason静态类型P3 | 运行时仍由批准validateV2强制枚举；静态code:string的收敛建议保留给对应owner，未修、未关闭。 |
| N-5 零列/ASK语义观察 | reader列名字串min(1)不等于columns数组非空；固定507未改此接口。父元数据契约仍待定，不作本轮新增缺陷或已有保证。 |
| N-6 model保存身份观察 | 已保存X载入model后仍更新X是现有显式规则；D4授权要求不改definitionId/generation。固定507成功model仅清visual+update，新建/saved推进generation。与Z报告事实纠正一致；保留父接线语义决定，不擅改产品。 |
| N-7 覆盖操作者收据事件 | reviewer确已以自己的readback覆盖ignored runtime同名文件；当前两份reviewer文件原样归档。操作者原3349B收据SHA `8c9cb6f0e629ab94f642bbf031e53ba5f979c781adeb3cad2722dee135eaeec0`早已在本目录minimax-owner-task-settings.json及创建21成员归档中保存，二者逐字一致，故本owner可恢复原事实，报告“无法恢复”仅限审者当时可见材料。保留事前原件为权威创建回执、覆盖后原件为事件证据；不覆盖回review runtime或改模型报告。该事件已报总控。 |

## 额外过程边界与事实修正

原§1引用用户级`~/.minimax/config.yaml`，原§10 N-7称检查`v2/sessions`排除本session外记录。它们是审者报告披露的读取/搜索，不能据此宣称全程只读自身批准最小面；已原样报总控单列判断。本owner没有为复现这些披露而读取全局配置、枚举其他session或输出凭据，也没有将默认配置当逐任务设置证明。实际创建UI/逐任务native证明与完整输入证明另有已归档原件。现有完整输入中的配置映射属于政策引用，不能自动扩大本任务后端取证授权。**后续最小原turn独审已证实：确有读取permissionMode配置的请求、对本轮Z review runtime的列举请求及跨session递归搜索请求；写入/后续edit覆盖收据也有实际请求证据。独审仅读请求参数与必要状态，没有读取config或peer结果，故不判定具体秘密/意见已泄露，也不声称零泄露。过程不通过，不能接收完整双Pass；处置/补审决定待总控。详细callId、必要路径与状态见minimax-process-audit.md和minimax-native-request-audit.json。**

报告§4的分类数量不准确：完整manifest实际42，按独立文件清单分类为runtime7、测试5、fixture8、probe2、其他docs20；其“3测试/7fixture/13文档”不能替代真实清单。原报告原样保留，42文件实际逐字核对仍42/42。审查后真实Git status还含本方`?? docs/reviews/T04/round-2/`（新模型报告）；非产品改动，不复述为只有AGENTS。

初次TS反例探针ERR_MODULE_NOT_FOUND仅有报告叙述，当前runtime未见独立该次raw/完整收据；不能把“首失败全部保留”升级为每次尝试都同等级完备。Python3.9首败保留重建说明（含argv/起点/exit1、无单独结束时间）；compare首败KeyError及完整check首败则有原raw及起止/exit收据。成功探针20fixture/60边缘/孤立代理项的逐例结果与十组收据均可核。

大型DOM trace1806380B继续保存在本方ignored runtime，索引登记hash；小结果JSON归档。该独立真实组件DOM不扩大为App/IPC/CSP/执行器/持久化、两OS或父验收。未push/PR/CI/合并/发布；无新产品改动，不重复产品测试。
