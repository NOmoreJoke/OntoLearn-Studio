# I05 source/package probe 源码交付

已完成本次 source-only 实施窗：真实 canonical 调用编排、新 probe、确定性纯输入资产和70个测试函数源码。R1 的两项 P2、一项 P3 已修复，独立 R2 **限定通过源码静态 delta**。没有导入或执行产品／probe／tests，不是运行、业务或合并就绪结论。

## 固定版本

| 对象 | Git ref |
| --- | --- |
| 唯一树／分支 | .worktrees/I05-source-package-probe／feature/I05-source-package-probe |
| base | 5f910b52c69d86a1076b2032e5d3c63e715947f3 |
| 22供应原件／过程 | 6891a5842302859a531cf82767c5a482417bc274／f79a29f596b2444cba542a906c91727869014886 |
| 22模块采用 | 01434e3f0f693de1cc3b560d04fdecd700d424a3 |
| 四资源采用 | 44f88a5cf45563a47ecf8df32cff35b7baaa95fa |
| 第一候选／R1 Fail收件 | 0e42a0fe349054a92817cb4d463bccdc15f6c042／cf15439a72207e622d2f8baa8d476a363107f5c6 |
| 最终受审源码候选 | 2cf0c3328de464e15a3fa9cdbfdf6aa88d0b4a64 |

T01四资源owner受审 dd972b79adf4d378636a7d41a6b0e3e08c0d5ca1、过程79d63cc1f403ee857a3af2a98f8870db9a6a910d。只采用不可变供应，未改其维护权。原AGENTS保持15852 B／78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759，唯一受保护修改，不暂存。

## 清单与证据

- 新候选77件payload共13091580 B，见 candidate-r2-manifest.json；排自身与后继过程件。旧72件供应／候选集合包含未变的101B根__init__，不等于Git delta。全交付文件的bytes/SHA另见 final-manifest.json，明确排自身以免循环。
- probe 93848 B／b3456f021afdbd53ec8677bf317a5ffdff636b55bae760eb8b7fec6e399e41b9；tests 73466 B／8055c398ca4d03bb99bdec06f599db1c342b2bc6a49a0a247e2ffc54c8652da5。
- inputs 8205267 B／47c66ffe18613eb8cc1af6365dcfc9d866821f22c48f96d9f44725f8f7c59eaa；descriptor21202 B／0b91c1a9366d170b5614d94c20006054a5a959be235e0f46cb150cf32335193a。417 observations、320 datasets；原83/106/54/50、C13和上下文边界保留，R1修复没有改变两资产字节。
- R1报告10425 B／de645efa00f9b127698ccbcd3b2ea1da3a58a9deab042f3d37af16da9c01e60f；R2报告7617 B／e86fc531c227813d765bc8949aa7a57c5403c1ca71c57e21e1a9100632c04fd8，R2 proof26195 B／a4aa9808614efa36ceecea84ae2a02af1f8fce5f608e353e9515e87db8c52436。root已全文读回两轮报告；旧Fail不覆写。
- review-chronology.json记录实际R1结束→全文读→收件提交→修复顺序，逐条原session ordinal/hash；r1-resolution.md逐项对应修复。首生成器路径错误、首EOF失败、静态辅助检查错误与修正均保留，没有冒充产品失败或运行成功。

实际完成的是标准库AST／JSON／bytes/SHA、固定Git逐字节来源对照、417投影摘要与集合审计、纯生成器generate/--check字节复现，以及明确范围的Git whitespace检查。static-verification-r2.json列新固定ref的base／工作区／stage检查；独审额外核其最终字节，不采用初始空redirect自检冒充最终身份。最终收件只显式stage任务资料，提交禁用hooks及签名交互，避免借hook运行本窗未授权的产品命令。

## 后继前置与仍未执行项

当前锁仍是5f的20999 B／d5d027da6628a2f4fc2e73730ce3a5e40d85aebba95188b0d4c3801ebdde949e；要求的供应锁28440 B／86dfe82d952e2c88edcfc5658f488f6e1f0d04b4ec3b1e6f5c5d3bc4f57e8b73尚未采用，八distribution也未安装或核实。T03四writer和环境不改；没有build-provenance schema则frozen明确前置拒绝。

后续需按总控窗口分别取得T03组合／锁／环境／构建来源、T05独立oracle与source/package同selector实际运行；检查真实hook、完整JSONL和新增故障回归、实际全量输出cap、loader/cache代码指纹稳定性。原S1 Store HOLD、12个snapshot试验、另12个B1 fresh试验、whole-H、许可、父包、完整check/package、指定同版双模型、CI、目标OS、真人及develop／远端门继续保留。

本窗未运行pytest、npm check、打包、native、DB、GUI或外部模型，未push／PR／merge，也未创建替代Goal或会话。原Goal保持未完成；源码阶段交付不关闭后继工作。
