# T02 指定双审完整积压台账（2026-10-22）

本次全量盘点固定本线流程 HEAD `dd7babf29b5fbab6238a6596724536afa11137ea`，批准 base `5f910b52c69d86a1076b2032e5d3c63e715947f3`，当前保留产品 `49321221733ea927484647352e05e7d833cebc86`。owner 为原 T02 聊天 `01a15bcd-f40b-7c91-81fa-7c481d2030d5`，实施树 `.worktrees/T02-ontology` / `feature/weekly-t02-ontology`。三条实现提交之外，后续提交均为过程或方案文件；已实际核对完整 Git 历史，未把纯方案写成产品。

## 当前指定审查的真实身份

| 方 | 实际 task/session | 模型／思考／权限 | 独立工作树 | 正式报告 | 当前结论 |
| --- | --- | --- | --- | --- | --- |
| ZCode | `session_8fdff47bb96963af157c498504a58c72` | GLM-5.3／最高／完全访问 | `.worktrees/T02-zcode-review-4932122` | 该树 `docs/reviews/T02/round-1/zcode-glm53.md` | 已实际开始，尚未终态／通过 |
| MiniMax | `mvs_06002009bb614b3bb56905f07eb5b240` | M3.1-Flash／xhigh／始终授权 | `.worktrees/T02-minimax-review-4932122` | 该树 `docs/reviews/T02/round-1/minimax-m31flash.md` | 已实际开始，尚未终态／通过 |

两树 detached HEAD 均 `ce1c3df41a233a07de4ef8fad54d5f201b222a23`；对应上列同一 base/product，当前 AGENTS `de15f6ce…c8c4` 未暂存。完整 58 项原始 delta 已按冻结 input-manifest 逐项核对 SHA：19 产品/测试/fixture、5 harness、24过程证据、10后续纯方案上下文。不可将 S1 缩成 UI 或提示准备。

原提示全文分别 28991B／29048B，各原样包含一次；实际提交全文31959B（ZCode SHA `2342bf340a2bff63e5362e18c194f7ecd30868cc6d71689a675b6059a7675f2f`）和32029B（MiniMax SHA `5c4317d0700a87b18aa8d9f018e91dac98a68de9a4a6b828711756de143f6a3d`）。ZCode实际接收长附件逐字节相等；MiniMax发送前展开正文并由AX确认精确包含全文。详见 [创建回执](round-1/launch-20261022/creation-receipt.json)、[全文和设置证据](round-1/launch-20261022/foreground-release.md)。原 T06 sessions/stdio 保持，前台已释放；监控与处置仍归原 T02。

## 全部阶段与历史候选

所有表行的批准 base 均为上述5f；“无指定任务”表示没有实测指定 ZCode/MiniMax 报告，不能以内部 Codex 报告替代。

| 阶段／固定内容 | 技术与原验收范围 | 内部证据及原结论 | 指定双审与覆盖/替代关系 | 当前可独立动作／就绪缺口 |
| --- | --- | --- | --- | --- |
| C1 `438c6ade34795cb3b0111f0bca463d4fd091b393` | 14 产品/测试/fixture、5 harness、5流程；私有不可变编辑计划、隔离React编辑页、有限输入/异常/身份保留 | `independent-review-c1.md` **不通过**，P2单行定义编辑丢换行；`verification.json` 原始633 TS/1075 Python、23本线Python/3TS、10合成回调headless检查及首失败均保留 | 当时无指定任务/模型设置/报告。后继C2修复；无正式撤回记录，保留积压和原Fail；当前全量S1审查包含其变更及历史闭环，不能倒填C1 Pass | 历史有缺陷候选，不另造旧版通过；若总控要求独立追补历史版，须精确冻结该版、完整新双审与原问题，不继承C3结论 |
| C2 `5ef86a1da88d86f2de7b55a7e3be38b1e0f986b4` | 17 产品/测试/fixture、5 harness、8流程；多行textarea、原owl/rdfs类声明、T09 G-base完整RDF固定输入；正式接线/导入往返仍未验 | `independent-review-c2.md` **通过**（内部）；`verification-c2.json` 633 TS/1078 Python、26本线Python/3TS、11合成回调headless；过程固定 `ca7f25366cb9e11533004938b86d5b80a75fe4b4` | 当时无指定任务/报告。C3新增source projection后成为当前，旧内部通过只覆盖C2，未失真改写；当前两新任务审完整C3并包含C2闭环 | 历史保留，无模型Pass可沿用或“作废”。是否额外追补历史版由总控明确；不可将当前审查当旧版已审 |
| C3／T02-S1 `49321221733ea927484647352e05e7d833cebc86` | 19 产品/测试/fixture、5 harness；在C2上加不可变Store快照RDF来源绑定与13真实临时SQLite专项；事实ID、owner/source_row/managed_value、tombstone、重叠支持、payload hash/引用保全；只读，不生成writer/确认/提交 | `independent-review-c3.md` **通过**（内部）；`verification-c3.json` 633 TS/1091 Python、39本线Python；13新增专项通过；UI字节未变沿C2的11项证据；P3 delivery入口指C2已仅过程修正；过程 `d597b3c00980652042163d250c875d660d4d371e` | 本页两真实任务正在完整同版审查；暂无终态报告/所有意见处置，不计通过。没有拿旧内部Pass替代指定审查 | 原owner继续后台监控，读取双方完整终态和报告/原始流；所有P级均处置。若受审代码/测试/依赖/验收/基线改动，则新候选、必要验证、两方全新同版完整复审 |
| S1原证据封存／恢复 `c30927000bdf7fafd5f396c08b39ae3ce9829f6d` → `51bec0d835246c4d0cc21f9a0e14fad5b30437c0` | 纯证据工程：47 payload+内嵌manifest共48成员，原始流／固定索引／可恢复性，非新增运行能力 | `evidence-archive/independent-review.md` 内部通过，`git-readback.json` 从Git实际恢复核验；C1原截图已被覆盖仅留旧hash，缺口明确 | 无独立指定task/报告；已纳入两当前完整S1任务的原证据链，仍等待真实意见，不倒填“外审通过” | 无需无变化重跑产品；保留原压缩包/首失败/缺失截图边界，审查实际意见后处置 |
| S1范围登记 `cab0d8e870d5a5b92a06a278ba05fd81b278b94b` → `f6a30406696179bddd5bdc7b9bef00a8f33f8717` | 纯过程：子阶段与父功能缺口、接口/所有权/审查排程，非正式接线 | `stage-registration-review.md` 内部通过；本人授权发送回执、root登记及后续独立范围/证据核验留档 | 无独立指定task/报告；当前S1任务必须保留登记边界，不把登记当父功能验收或指定模型Pass | 按实际报告更新status，root维护共享登记；本线不改root state |
| typed ChangeSet接入方案 初版 `64bbfe27a2191e65e8e81ab34862b9867e46a034` → 修订 `4406103ac309b21ddabb5f99b3efd11265acb64f`；交付过程 `d597b3c00980652042163d250c875d660d4d371e` | **纯方案，未实施**：sourceBinding贯穿原previewHash/planRef/receipt与确认/Job/commit原事务复验、成本执行前预扣；34固定源+5控制输入 | `typed-changeset-integration-plan/independent-review-initial.md` **不通过**2P2，final **通过**仅方案层；`disposition.md`保原Fail；主方案44243B/SHA `6b88b1f7a8e9b7b08719f6b48dda16905a3eb800a7b8baef21f4b7a26b06983c` | 无独立指定task/报告；当前S1任务只以“后续方案上下文”读取，不等于方案本身独立外审Pass，更不等于已实现 | 待T01固定供方/采用和root精确树/路径/版本/实施授权；可只读核对具体供方差异并形成请求，不能写adapter、共享schema或提前消费未批准实现 |
| 双审准备 `93c1125c56c3910a83835761cda852271d5964bd` → `ce1c3df41a233a07de4ef8fad54d5f201b222a23` | 纯过程：完整原提示、58delta/hash、原始日志索引、政策历史、准备manifest（14payload+manifest=15） | `round-1/preparation-review.md` 内部通过；完整准备包与manifest留存，原提示不改写 | 不存在独立外审准备Pass；当前实际两task才是S1审查，准备通过不能替代产品审查 | 原件保持；实际接收证据/当前映射另存launch目录 |
| 执行补充 `1278083da15e3df404992c21fb603be6922f8ec8` → 当前政策 `ec586947b87b024892fc034f2e4bd246ec08cf47` → 过程 `dd7babf29b5fbab6238a6596724536afa11137ea` | 纯操作层：自主必要验证、独立环境/输出映射、撤回旧静默限制，非产品变更 | `background-addendum-review-initial.md` **不通过**P2旧AGENTS/P3计数；final内部**通过**，原Fail及旧提示保留 | 无独立指定task/报告；实际桌面launch覆加当前窗口与真实路径，不用旧租约描述阻断；当前S1任务适用本轮最新操作政策 | 仅记录具体创建证据；无需因纯政策变化重测不变产品；新树AGENTS已实核de15 |
| T02父功能 FR-200–204／正式集成（未形成独立新实现候选） | FR200全文领域/非RDF元数据、可信当前源/引用；FR201–204导入/视图/手工与模型草稿等完整链；唯一Store.commit／真人确认／原子性/receipt/undo；I05有限Turtle/SHACL与完整往返、I06 App/bridge生命周期、T08真实草稿、目标平台/真人/release | 当前仅S1局部实现，typed方案不能抵交付；原全部父验收仍保留，无父功能完整运行证据 | 无可审完整父候选，无父指定任务/报告/Pass；不能借S1两任务关闭父功能 | T01明确可采用的固定版本及全量source/reference/metadata、S2 proof和成本合同；root唯一责任/路径授权；获准后独立树实施、验证、双新审。生产/CI/PR/正常develop合并/远端门均待 |

## 覆盖与失效的准确边界

实现后继关系为438→5ef→493；未发现历史C1/C2的正式撤回文件。历史内部报告原结论保留，未存在的指定Pass无从作废。当前S1新审覆盖全部保留实现与历史问题，不自动把任意历史阶段改为已通过；历史追补排程及方案是否另开指定审查仍需总控登记。凡当前审查发现问题，由原T02修复；原Fail与首失败保留，禁止改旧记录或通过缩验收关闭意见。

本页为事实登记，不替代 `status.md` 的唯一进展来源，不修改根清单或控制状态，不将任务受理当审查通过。原Goal保留blocked，未重建/关闭；实际获得本次指定审查创建窗口已单独记录，父集成依赖未因此完成。

## 首轮终态与后继C4/C5（原表为创建快照，保留不改）

原493两指定任务均已真实终态并各给有界S1 Pass：ZCode19506B/SHAaf43f9ab…d0e4f，MiniMax36714B/SHA51e3b498…579f6，ID/turn/原报告/原始流见round-1/received-20261022。按正文准确登记1P2+10P3共11项（MiniMax摘要错称4P3，实际5P3）；本方Pass不等于所有意见关闭或父门通过。

| 后继阶段 | 固定产品／过程 | 实际证据／结论 | 指定双审及后继动作 |
| --- | --- | --- | --- |
| C4类型与UI修复 | 35aa93fc007e92632d83747f7fe345295db340c8；过程3d603b2 | 634TS/1133Py、81本线Py、21headless，原始流及首失败全保；独立完整复核**不通过**，发现JSON surrogate编码逃逸P2 | 无指定task/Pass；已由C5修，原Fail保留不改；未以C5倒填历史通过或假定总控已正式撤回该历史项 |
| C5当前私有服务候选 | e5ad54e5762157cafe532c2a0c07c22e8dd737cb；证据过程516ba27 | 原P2 UTF-8拒绝、31负例/合法Unicode正例；634TS/1164Py、112本线Py exit0；独立C5复核通过，UI六输入hash未变沿21项；20产品/测试/fixture+5harness | 待双方全新同版完整R2审，不沿493 Pass；完整120delta/130输入与11项处置已独立复核，准备完成不算实际任务 |

全部旧C1/C2/C3、证据恢复、纯方案/范围登记与父功能行继续保留。Z语言小写子集及完整前置parser延期未变成已实现；原验收/公共共享/锁/CI未改。原owner同一聊天，当前集成源移至`.worktrees/T02-s1-review-fixes`、branch feature/t02-s1-review-fixes；旧树/原报告保持。R2新任务实际ID/逐方设置/报告/处置在实际创建及终态后另登记。

## C5 R2实际创建追加（原准备表不改）

同产品e5ad、同review HEAD7c52，两实际独立树已真实创建：ZCode session_70e23e92b6da020a8bf5e58fe51cc04e（GLM5.3/最高/完全访问）；MiniMax mvs_1cdba3c3802647838bc5f5091a866e22（M3.1-Flash/xhigh/始终授权）。完整原文受理与逐方证据见 `round-2/actual-launch-20261022/`；M少一个末LF的表示差异如实保留，Z首次请求synthetic附件重建字节相同，不以标题/附件存在冒Pass。GUI已明确释放；当前两方终态/全文报告/逐项处置均待，不沿493结论。新接口矩阵和创建记录只在owner过程源，不写两冻结审查树，不缩父验收。


### C5 R2双方正式终态追加（当前进展）

同候选e5ad、同审查HEAD7c52的两方现均真实stop且完整报告已收件：ZCode20343B/SHA c3f5efd5858a568b2ed4843eac8a0210ed0ea66832bc6b37ebfae278c90bd8a2；MiniMax40420B/SHA449cf074c463105e286d0d42fe5ce1506632dc57bda6f5af667db3a221d4a181。均明确有界S1 Pass，各自实际634TS/1164Py、ontology112、合成callback headless21 exit0。全部原始流／首失败／完整报告及终态原回复在round-2/received-20261022各方目录；Z 21成员、M 26成员归档逐成员读回匹配。owner仅静态读取，不重跑产品。

仍有M 3项P3（内部digest边界／当前交付指针／深链代价）和Z 1项P3（localGraph非graph页签也重算），均接收待后继，未修、未宣称全部关闭；M的T01范围外观察只经总控路由。完整处置与原报告覆盖描述纠偏见round-2/received-20261022/dual-review-disposition.md。R1延期／部分接受及全部父验收保留。候选和两审查树仍冻结，不改实现／测试／配置／锁／验收、不占GUI；后继产品改变须新候选及现行重审。原Goal仍blocked，正式接线／CI／合并／远端门未完成。
