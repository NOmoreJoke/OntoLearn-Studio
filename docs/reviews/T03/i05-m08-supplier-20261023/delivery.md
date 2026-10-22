# M08 三路径供方交付

产品冻结：`4e752177f3e350d0be94ed063aca2e866dbf7970`，父提交 `2cf0c3328de464e15a3fa9cdbfdf6aa88d0b4a64`；approved base `5f910b52c69d86a1076b2032e5d3c63e715947f3`。分支 `fix/T03-i05-m08-supplier`。仅三个产品路径：engine pyproject、uv.lock、build-engine.mjs。现行 AGENTS 15147B/de15f6ce 保持受保护未暂存 overlay，不进交付提交。

直接声明 pyparsing 3.3.3 / pyshacl 0.30.1 / rdflib 7.6.0；build 加 pyshacl/owlrl/html5rdf code+data 收集与八包 metadata，原 rdflib、engine data、contracts、uv.lock provenance 保留。其余五闭包固定 owlrl 7.6.2 / packaging 26.3 / prettytable 3.18.0 / wcwidth 0.9.2 / html5rdf 1.2.1。原18项锁定版本未变，新增五包，总23项。

锁是实际 resolver 生成：首次把 constraints 放到 uv.toml 配置未生效，得到 wcwidth 0.9.3，该结果拒收；随后以八项 `uv lock --upgrade-package name==version` 明确版本重新解析，`uv lock --check`、`uv sync --frozen` 和逐8版本断言通过。最终28440B/SHA86dfe82d952e2c88edcfc5658f488f6e1f0d04b4ec3b1e6f5c5d3bc4f57e8b73恰与旧6891锁相同；不是复制旧锁，resolver日志/argv保留。本目录旧 `resolver-constraints.toml` 是首尝试输入证据，不是现行生效配置。系统 python3 最初缺 tomllib 的准备失败也保留，后续固定使用实际Python3.12。

## 实测与边界

| 验证                                 | 结果                                                                                                                                                                                                                      |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| npm ci / frozen uv sync / lock check | 0；八实际安装版本符合固定组合                                                                                                                                                                                             |
| fresh npm run check                  | 1；固定2cf的implementation.md与两原JSON格式阻断，未改字节                                                                                                                                                                 |
| typecheck / TS tests / build         | 0；15测试文件、630项TS测试通过                                                                                                                                                                                            |
| npm run engine:check                 | 1；189项ruff错误阻断，&&未进入format/pytest                                                                                                                                                                               |
| 单独原授权实际pytest                 | 1；1175收集、1167通过、8失败、204.47s；首失败全文在pytest-first-failure.log                                                                                                                                               |
| verify:sources                       | 0；12项归档源身份一致                                                                                                                                                                                                     |
| package:dir                          | 0；真实unsigned macOS arm64目录包，不含GUI/native运行证明                                                                                                                                                                 |
| actual-package-static-audit.json     | 八项metadata、11份真实许可证/notice（包括 metadata 声明的 AUTHORS.rst）与安装输入逐字节相同；八项PYZ代码清单、wcwidth abi3物理文件存在；两原JSON、contracts全体、uv.lock精确入包；Python3.12 cookie/sharedlib真实静态身份 |

pytest 的canonical/full-v1真实执行已在失败trace中观测；执行文件包含会真实调用两B1 selector的fixture，但默认点/F输出没有各selector独立退出结果，因此保持UNKNOWN，不由“未列入8失败”推成每项0。先前普通fullcheck总授权与full-v1子禁项粒度冲突，以及root后续允许已运行pytest自然收尾的更正，均记录在validation-receipt.json；未kill/重启/抬guard。合并双流原样保留，文件UTC不是精确monotonic。

8失败均为固定2cf的probe测试路径，本供方未改这些测试或实现；尚未对未改依赖的旧环境作对照，不据此宣称全部是既有已证实缺陷。按root唯一路由已交I05 owner静态triage；不改expected、guard、原input或oracle，不擅自补跑。

## 后续接口与集成

`provenance-entrypoint-plan.md` 仅为最小额外路径/私有格式/真实绑定方案，未实现；当前 entrypoint 没有 semantic selector dispatch，frozen guard 原样。包内metadata、license、code/native文件存在不是冻结导入/真实loader绑定证据。完整source/package CLI parity、外部artifact binding、新401a后集成候选与指定双审仍待后续实际工作。

产品供方commit可由I05唯一owner在root确认后集成到其最新401a候选，旧2cf probe SHA不得冒作最终pin。整体check与I05验收目前不能签通过。原始日志在本工作树build/m08-validation，精确argv/exit/bytes/SHA/filetime在validation-receipt；首pytest失败因必要可复查且体积小另存全文。独立审查结论单独保留，不代替指定双审。
