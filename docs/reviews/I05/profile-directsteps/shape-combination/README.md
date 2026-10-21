# directSteps 与已收件 shape 入口的精确组合

本窗口从 `fb99fbdc6d2630efe0c1107b93401667a808466d` 延续，产品固定 `43d56317f0bfbdfeec05efc583b306615ae54a30`。相对该起点恰一改三新增：只把原已收件3bd的 `_shapes` 两个集合差异施加到现有DAG源码，逐3bd Git采用两份consumer-C原件和7211B原shape测试。没有整文件覆盖 semantic.py。

组合 semantic.py 为56037B，SHA256 `c45fda962a3aa272490d683abbec96175e21ca32de94afb1d2de006b02a3c56e`。机器核验唯一变化顶层AST节点为 `_shapes`，其完整AST等于3bd原函数，其余节点与fb99原样。`exact-shape.patch.raw` 保留精确文本差异；144受控中143项只读按源Git/bytes/SHA核同。原1095过程与旧主文逐项冻结在 `frozen-process-1095.json`，本窗口仅在此新目录追加过程。

正常检查一次同时运行原77项DAG与复制的26项shape测试；真实Validator调用次数、完整报告和D事件分别写在该次run的shape-reports/direct-fees，完整144来源前后、clean子进程环境、真实argv/cwd/HEAD、双流及成员SHA独占保存。12归档源另行验证。实际01完整检查exit0：1125项TypeScript、4990项Python通过，44项原有skip保留；144来源前后相同，77项DAG与26项shape同次执行。03实际12归档源核验exit0，04 continuation→product的产品diff检查exit0。独立delta已有限通过，根已全文读回6263B报告（SHA256 `dd042cc97677d0f13891244ba1efc92301af8945b847c1eacc30cae9623d5ff4`）：精确补丁/三原件/144来源及1095旧过程核同，并消费唯一check与26份真实报告，没有重复测试。实际9次Validator执行、17次前门拒绝；D观察为66文件178累计快照，不能相加当独立收费次数。

第一次十二源启动器因runner尚未创建退出2，npm未执行；该工具调用没有独立原始双流和准确时间快照，缺口记在early-verify-launch.json，不重建原件。随后03独占执行12源核验通过，不能将成功改称首跑。

本组合只采用原langString与inclusive nni/dateTime入口修复；date、illtyped、其它writer、D费用和合同均保持原政策。原测试及黄金逐字复制；测试模块预载黄金供断言，expected在实际调用后选取，没有进入产品输入或生成报告。两个消费者pending、正式来源/Job/Store/selected/HΣ、父I05/M1及外部验收门仍保留。本窗口没有GUI/native/e2e/HMR、模型/付费、push/merge或Goal变化，不自动采用到T01/T05。
