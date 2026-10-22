# 窗口需求对应与接收界面

唯一授权是 `inputs/I05-source-package-parity-contract-preparation.md.raw`；本件只索引合同，不新增范围或状态。

| 原窗口要求                                       | 可直接审查的交付                                                          | 实施前仍须取得的具体输入                                                         |
| ------------------------------------------------ | ------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| 1 最新组合、原83/C及原操作上下文、最小采用闭包   | contract §1–2、§5；case-catalog、static-import-closure、source-provenance | T01四件资源逐路径只读采用；I05新assets逐字段新字节；原缺上下文按账本不造输入     |
| 2 完整支持／拒绝、真实入口、纯输入与完整独立预期 | contract §3、§6；全83/C13与106/54/50metadata；coverage调查                | 新族精确纯输入清单及T05完整独立oracle；未执行/unsupported/missing各留状态        |
| 3 单一私有probe具体接口／数据／cap／退出／取消   | contract §4；新模块、flag、两assets唯一定位                               | I05精确新增路径实现票；实际完整输出投影schema／tally；物理进程与hook另审，不绕H  |
| 4 T03唯一四writer全guard／import／资源／license  | contract §5；43guard每项delta、22module每条import                         | T03当前native候选锁释放后新offer、真正组合ref／实际dist/archive/license映射      |
| 5 同版源包与S1两档／证据域                       | contract §6–7；包装调查固定原seed/count/hash/measurement                  | source/package/parent实际运行与S1 Store准入/工具/原件；OS/CI/真人/双指定模型另门 |
| 6 最小下一票／owner／base／freeze                | contract §8                                                               | root接收本合同后分别派路径级票；不自动取得runtime/四writer或外部模型权限         |

本次三名参与者分工：root唯一合同/索引writer；directsteps_independent_tests仅coverage报告与metadata清单；directsteps_budget_review仅包装资源调查。restore_schema_code_review独立审查新合同，只写自己的新review。独立调查不是指定双模型审查；每个原报告保持实际版本与sha，可恢复首版。

原来源 `.raw` 保留原字节：它们是小的命名政策/收件/需求文档，非运行包、输入生成器或probe实现。原T03 offer及架构需求复制为raw是为保留不在本docs Git内的验收来源；不批量格式化档案。最终manifest将逐件记录bytes/SHA，避免以口头复述代替证据。
