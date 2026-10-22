# T03 历史双审补齐包：独立准备审查

结论：**NEEDS_CHANGE（F1 / P2：跨工作树共享输入缺少可执行定位）**。19 件固定材料的身份、四组完整树清单及历史逐路径比较相符，没有发现字节覆盖错标或伪造指定 Pass；但六份面向另外三个工作树的提示没有给出实际共享包的绝对入口和固定身份，不能直接作为自足派发输入。修复文档定位后可有限接收三个现有工程组的发审准备；native 仍须先修内部 Fail、固定新候选并完成既定独立 delta。本审查不是源码/产品验收，也不是指定模型审查。

## 固定身份与实际检查

- 工作树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-mapping`；分支 `feature/weekly-t03-mapping`。
- base process：`3c396070c74fbf09cf319b0230c6f96ed2858482`；真实 candidate/入口 HEAD：`ed9cef968b17a1edefc0977b509906fb9f81a336`；产品仍为 `30319412daf8ae4745987babf7bbed93c53b6b42`。
- candidate-manifest：4301 B，SHA-256 `60c52bd13dac43bb9685b5233db817118dda10341357794d9f27500f07301e6c`；18 payload 共3369151 B，连清单共19件3373452 B。
- 逐件核 current = candidate Git bytes = manifest bytes/SHA，清单自身也等固定 Git；base→candidate 路径集合恰为19件新包。旧 round-1 七件与产品没有在此 commit 改变。入口 index 空、唯一 tracked 修改是受保护 AGENTS。
- AGENTS 全文读取：15147 B，SHA-256 `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`。全文读当前 common、desktop policy、external-review-permissions；当前 policy 已改为创建/设置/读回短 lease，不把后台推理时间当整个应用独占，也不向用户重问桌面时段。

本审查独立读取全部新 Markdown：README、覆盖摘要、完整历史矩阵及8份提示。一次输出保存至 held buffer，再连续分段补齐全文，没有把截断部分当已读。所有 JSON 完整解析；大量重复的 Git 清单/矩阵通过完整集合与每行对象核验，不冒称读了对应源代码内容。

| 实际固定组       | full tree条目 | base→product路径 | process后来追加的证据工具 | 独立检查                                                 |
| ---------------- | ------------: | ---------------: | ------------------------: | -------------------------------------------------------- |
| mapping-S1       |           866 |               75 |                         0 | 全集、mode/type/OID/bytes一致；全部非docs产品与process同 |
| source-selection |           823 |               15 |                         0 | 同上；当前8c与历史f2c分开                                |
| profile-D2       |           941 |              116 |                         9 | 同上；9份py.raw工具逐项存在且纳入完整process范围         |
| native-current   |          2602 |             1814 |                         0 | 同上；仅固定cf9元数据，不读当前修复WIP或native载荷       |

四组总5232条，全部与固定 `git ls-tree -r -l -z` 元数据逐项相同；全部 base delta 的状态与路径集合也与真实 Git 相同。29个历史阶段的全部1222条 engineering 比较独立重算，stage/target object、same/changed/deleted、allEngineeringBytesExactlyCovered、全 delta 计数、非相同证据路径全集均相符。六个跨组共同非docs路径冲突表也完整重算一致；没有用祖先关系或相同数量替代字节比较。

## F1 / P2：跨工作树提示缺共享包绝对位置及固定身份

位置：`source-selection-{zcode,minimax}-prompt.md` 第5、9行；`profile-D2-{zcode,minimax}-prompt.md` 第5、9行；`native-current-{zcode,minimax}-prompt.md` 第5、9行。其余mapping两提示也可一并给明确入口。

这些提示只告诉模型在各自 source/profile/native 工作树审查，却要求先读取“本包 `*-fixed-inputs.json`”、`historical-stage-inventory.md` 和 `coverage-matrix.json`。实际整个包只存在于 mapping 树：

`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-mapping/docs/reviews/T03/designated-review-backlog-20261022/`

本次只用文件存在性核查：另三个目标工作树的同名 `docs/reviews/T03/designated-review-backlog-20261022/` 输入不存在；提示正文也没有上述共享包绝对根、该包的 ed9 固定 ref 或其 manifest 身份。JSON 的 worktree 字段指各自工程，不能反推出另一个 mapping 树中这个新包的位置。实际通过 CUA 将单份提示正文送入所选工作树任务时，模型无法按给定位置取到覆盖矩阵/历史处置和完整清单；可能只看旧本树证据或自行搜索到变动版本，失去本次“完整范围、精确固定输入”的可审查依据。这是输入定位缺口，不是要求拼装或改动任何工程。

建议前向新增具体派发定位/提示修订：每份提示明列只读共享包绝对根、固定包 ref `ed9cef968b17a1edefc0977b509906fb9f81a336`、candidate-manifest准确路径/4301 B/SHA，以及本组完整输入与历史矩阵的绝对路径或同 ref Git 地址；说明工程仍按各自 product/process读取，跨树只读包不改变工程版本、不复制或合并共享源码。若owner采用附件传递，则真实派发收据逐件列附件内容身份，不能只说“附上本包”。当前19原件及本Fail报告保留，再审新增的精确 delta。

关闭验收：独立从每份提示正文，使用它实际指定的目标工作树，能够无猜测定位**同一固定包**和本组清单/历史矩阵；其字节或固定 Git 对象核同；没有改工程/旧冻结提示，也没有新建或复用错误真实任务。新定位本身不触发产品复测。native 提示当前禁止派发的状态仍须保留。

## 已符合的准备关系

1. 四个当前分支保持不同真实工程版本，S1 XLSX21、profile semantic23与D1纯方案26区分；跨组共同文件差异明确，不把多版本锁/入口/guard拼成虚假的一个运行候选。旧版本changed明确不覆盖，不继承旧Pass。
2. 历史清单完整保留六构建、各阶段source/product/process、Q/N/P冻结、meter失败/撤回方案、forward限定关闭及caller新Fail。纯offer/adoption/D0/D1方案另列，没有冒成实施或指定Pass。历史快照与README前向ae285/cf9说明分开。
3. 全部8份提示已全文读，模型要求及完整范围对称；按预期模型/报告名作文本替换后，每组两提示内容一致，没有把一方缩为delta或泄露本轮意见。ZCode GLM-5.3/最高/yolo、MiniMax M3.1-Flash/xhigh/bypassPermissions都是未来必须实际读回要求；所有实际task/settings/report均null，lease=NOT_GRANTED，sameCandidateDualPass=false。
4. 提示保完整源码、工具源码（含.py.raw/.input.py.txt）、tests、fixtures、配置锁、原全部验收和失败/缺证。完整FR300–304、附录C–G及§10–12/57P0与父门仍在，源码/运行/打包/目标平台/父业务分别判断。没有因父runtime缺证永久排除其他三组静态审查，也没有授指定模型代跑旧HOLD/被拒工作/native未签票或caller/runner/reader/模拟。
5. 小型根收件全文核对：S1归档恢复E1已闭；D2限当前宿主unsigned技术证据，源/包83各78/4/1且probe/oracle exit1；第6构建built-unverified/NOT_RUN；forward静态绑定已限定接收但未来806000/164MiB/737280仍未fund。包中没有继续把“待root读E1”当阻点，没有将这些收件改成父功能或运行Pass。本次未重读这些原包、索引、witness或二进制。

## 未执行与交付边界

本次只普通文件、Git对象元数据、JSON/hash与新报告格式检查；未读取源码/SDK/工具安装/二进制/descriptor/witness/index/归档payload内容，未运行caller、任何准备函数/runner/reader/helper/模拟/fixture/compiler/product/test，未用CUA或网络，未新建外部模型任务、stage/commit/push/PR/merge。验证脚本只是本次文档/元数据核对，未调用受审实现。

本报告不认证新包里所有历史验收事实或每份旧报告再次全文审计；相应声明来自明确列出的原状态/根收件。本次已新证实的是交付字节、完整树/差异集合、历史覆盖计算和提示文本。所有实际源工程/原验收及模型终态仍须真实指定任务各自完成。native source-bound修复/F1–F4、执行票、四角色身份/批准、ABI/loader/drain、目标两OS/CI/真人/父功能/develop与57P0门均不由本报告关闭。

只新增本报告、independent-checks.json、independent-seal.json三件；本人不改19候选或历史证据，不stage/commit。完成本人格式检查、全文读回与seal后停写。最终字节/SHA由seal和父agent实际接收确定。
