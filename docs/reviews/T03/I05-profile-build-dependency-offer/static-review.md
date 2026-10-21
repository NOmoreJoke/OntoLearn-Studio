# I05 profile 依赖与包入口 offer 独立静态复核

2026-10-21（Asia/Shanghai）。**最终通过，限于文档准备提案；无实现施工或依赖采用批准。** 唯一 P3 导入闭包措辞意见已闭环，无未处置问题。原 T03 Goal 保持 blocked，既有产品/测试/锁/包字节未由本轮复核修改。

## 受审材料及规则

- 首读主稿 `docs/iterations/T03/I05-profile-build-dependency-offer.md` SHA-256：`9452003dc129b47da215dd43fc9824511022454852ed360310aec2bb2d5327d6`。
- 已全文读取修订后最终主稿：19386B / SHA-256 `5bcbc99714765bd65585ac02dce4c2878af9f4e827ebebf3353940d13d7c6788`。
- `inputs.json` SHA-256：`f117425c10f85a85513f68f2689b6665580768376cdd9c47a977acf638e350c3`。
- 已全文读取准备授权，2878B / `288350b2cf49586df962544d47fd76eb3b2f4b005cb1909828b42f7cc00b83da`；已全文读取 raw plan，30339B / `28295b0efd79c68ab5fe9ba1dd5c335b72a2be0e9d044698cdbc3a00a4bf32b9`。两份实际长度及SHA均独立核对一致。
- AGENTS 为 `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`；共同指令实际17891B / `e437121a08053544c2a09151ac5183baf15b5fa67a3a604891aaa9e77ba971b0`，旧16317B前缀仍为已全文读过的 `ff5f9fd0a4913cc6c2fa612ec565bdf40d67db4a6640e5293d4ca1e7d02cfaff`。新追加的四文件基础责任交接已读，不扩本次授权；完整第九节/无桌面/冻结/双审门保留。
- 只用 git/file、标准库 TOML/AST/JSON 和 hash 作静态读取，没有运行 dependency resolver、安装依赖、import 产品或读取未批准 T01 runtime，没有运行 parser、tests、构建、包、GUI或网络操作。仅新增本报告，不改 status 或其他材料。

## 固定四文件及依赖闭包

1. 对批准5f、C4 `523c478d5f39671c4ac7c1ea6997e51d3047d58e`、S1 XLSX `30319412daf8ae4745987babf7bbed93c53b6b42` 的四文件共12组 ref/path/长度/SHA逐条核对，全部匹配。
2. 批准5f锁18包；C4锁23包。C4只新增 html5rdf/owlrl/prettytable/pyshacl/wcwidth，既有记录只有 ontolearn-engine 和 rdflib 改变，其余16条及非package顶层字段一致。pyparsing 3.3.3在5f已锁，提升direct不是版本升级；packaging 26.3原已锁但现在进入pyshacl运行闭包。
3. pyshacl 0.30.1依赖owlrl、packaging、prettytable及rdflib[html]；owlrl 7.6.2→rdflib 7.6.0；prettytable 3.18.0→wcwidth 0.9.2；rdflib[html]→html5rdf 1.2.1，普通rdflib还依赖pyparsing 3.3.3。主稿未漏extra边。
4. inputs八项候选闭包的版本、registry、普通/optional依赖、完整锁记录canonical hash、是否已在5f及是否逐记录相等均匹配固定锁。全部artifact的URL/hash/size投影完整匹配，包括wcwidth的sdist和12个wheel，未只保宿主artifact。此检查不验证远端分发真实性或许可证文本；新resolver/实际锁/分发许可仍是正式授权后的待办。
5. S1 XLSX锁21包，只新增三个解析库且仅engine既有记录改变，其余17条及锁顶层字段不变。A面从5f新增两direct/五锁记录是最小候选；B面三XLSX库需另批，集合并集26项只是静态集合，不是兼容运行通过。主稿没有整用C4锁/venv或将B自动采用。

## 七模块与构建采用面

固定T05 `1e3e0ee1d9d5b70f1f59233d0a3c64f6d85fd2cb` 七文件的长度、SHA、canonical module、AST imports、全部public top-level classes/functions和所列常量均独立核对一致。5f/C4均没有该quality目录。

- 六个rule子模块的计算导入闭包只涉及所列同包rule模块和stdlib；`__init__.py`原字节有四个指向definitions/planning的旧懒导出。主稿已明确它们不属于采用面，不能借七文件声称根旧服务完整。
- 七个完整hidden-import名字、两个明确排除模块、禁止collect-all/collect-submodules扩整quality及实际TOC待验的建议合理。不能把静态建议配方或排除提示当真实打包成功；若实际计算路径调用被排除旧服务，须失败并返root，不能stub修绿。
- 固定rule_profile确实按canonical包名从sys.modules识别record class，CompiledPlan/ProfileValue有精确类型与本进程发行记录检查；原名、相对位置和单一模块实例要求有静态依据，源码相同不能证明别名实例兼容。
- 沿5f保留rdflib、contract、uv.lock及engine数据收集，在授权后最小增加真实闭包/metadata/输入资产和来源清单是合理四文件面。主稿没有暗用C4 inventory脚本或整个引擎业务包；明确recursive metadata/正常import分析不足以证明extra及包完整，实际缺失须新候选实测。
- 来源清单可由已获准四文件之一build-engine.mjs生成；仍待root批准实施、I05提供固定采用表/资源合同，不是现在可写产品。原.py hash与PYZ/pyc/引擎归档hash分别记录并关联，未要求二者相同，也未把清单自报当归档已验。

## 探针合同与隔离/门禁

受限 `--semantic-profile-probe` 分派只是一项待I05 main签名/CLI/私有JSON/输入资产/身份合同冻结后才实施的建议。源/包同一canonical probe与真实reason、完整实际输出、外部独立oracle、expected不进输入、未知接口明确待交付，均与raw plan相符；未创造第二matcher/probe/schema或借test Job伪接线。

不打开Store/Job、不注册能力、不写current/history、无任意路径/脚本/URL/通用JSON入口；额外参数、安全异常及域失败边界合理。具体输入/输出/展开预算与固定失败矩阵待owner冻结，CLI采集exit0不能充当oracle通过。

实施隔离建议保留原S1/C4冻结树，新独立树从root明确批准base开始；T03唯一写四文件、I05只按精确授权接收固定提交，冲突回原owner，不扩大未来维护权。要求一个实际同版集成快照而非跨树拼绿，保留check/source验证/新包/源包同输入/原受影响probe、平台/B1及完整原门，既未越权也未要求等整个M0后才能准备。

## P3：收窄“七模块AST只依赖…”的句子

位置：首读主稿§3末段（第68行）。该句容易被读为七文件所有AST依赖均闭合；父包事实上还有指向被排除的definitions/planning的懒引用，inputs也如实记录了它们。

建议改为：“六个rule_*模块的计算导入闭包只含所列同包模块与stdlib；父__init__另保留指向definitions/planning的四个旧懒导出，不在采用面且不得触发。”这是文案精确化；主稿前文已正确限制采用面，不构成需改代码或运行的缺陷。

### P3 关闭复核

最终主稿§3已明确仅六个rule_*模块的计算导入闭包闭合，父__init__另保留指向definitions/planning的四个旧懒导出，未采用且不得触发。与固定七文件AST和限定私有采用面一致，P3已闭环；保留首读SHA与原意见，不改写旧证据。此次收尾只全文读取主稿、核长度/SHA并更新本报告，没有运行产品、依赖、测试或打包。

## 证据边界

本次静态通过只解除offer材料事实/最小增量/私有采用面/待冻结包合同是否列清的准备问题。所有新依赖解析/安装/许可证、新probe真实实现/输入oracle、PyInstaller归档与模块身份、source/package结果、安全失败、目标平台、指定同版双方新审/CI/正常合并/远端及父范围仍按原门待实际批准和验证。未新建产品树、Goal或可导入实现，未提交/推送/切分支。
