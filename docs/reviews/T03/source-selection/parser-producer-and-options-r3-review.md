# T03 parser producer/options r3 独立设计与事实复核

2026-10-21（Asia/Shanghai）。**通过，限于固定来源事实与待采用设计答复。** 未发现源码身份、编码、数字或权限范围的实质错误；下面两项 r4 措辞建议已按最终材料关闭，无未处置问题，不把当前答复当运行批准。

## 固定材料与操作范围

- 首读主稿 `parser-producer-and-options-r3.md` SHA-256：`298f61459ce934f823c193abf2dbbb9817e84ed370882e971c6bc355463b1241`。
- 首读 facts JSON SHA-256：`1a2eeee69452d62c12885019b4ce5c3bce2d4703708557d132a9f87f531d20b3`。最终修订 SHA 见下文。
- T01 固定 `b35cb4e21d375386775e5fc0431a8089a47195da` 两份设计全文已核：table digest r1 `568cb308ec5db6b7b537b4a385958a475c200268d750cedd73bdb1e28ce65b79`；lifecycle r4 `17f34e57c503ddca2da18c1cb62eb22dab3b6fd250db5a600ce2a4c30930cb9e`。
- 固定事实对照为 S1 `30319412daf8ae4745987babf7bbed93c53b6b42` 与 broker `8c904b57b7c5aac7b2b19273e679e7e36304dd1c`；只读取 git 对象、文档及既有封存记录。
- 已核对 AGENTS `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`、共同指令 `ff5f9fd0a4913cc6c2fa612ec565bdf40d67db4a6640e5293d4ca1e7d02cfaff`，沿用已全文读取的规则及完整第九节/无桌面要求。
- 未 import 或运行产品/T01候选代码，未执行 parser、pytest、全check、构建、GUI或网络操作，未恢复 Goal。仅新增本报告。

## 逐项结论

1. **parser 身份未提供的判断准确。** 固定 mapping source/init 没有专用 parser semantics/version/implementation 声明或三字段输出；私有 probe 没有建立已注册的 parser 执行身份。固定 registry 的 mapping.commit 仍为 design-only。源码SHA、包版本或三个库版本不能认证真实 parser producer。
2. **已有基础设施声明没有被抹除或混用。** 固定 resources 确实有 `i04-infrastructure-v1`、`0.1.0` 和从完整 checkout/frozen uv.lock 字节计算的锁哈希；固定303锁为 `9f5b6d2b93d994a3e4f8a46ce5cccae99d4e024ea7531ab62dd8e85d6aa1152e`。主稿和facts把它明确标成通用基础设施声明，而 realParserImplementation 为 null，没有冒称本轮运行身份。
3. **提案边界正确。** `t03-source-parser-v1` 明确未采用/未实现，复用唯一三字段 schema。固定 canonical 的前两字段是 ASCII `[A-Za-z0-9_.-]{1,128}`、锁为小写hex64。实际引擎版本/完整锁及受信执行认证仍待 owner 落实；未要求抢写 resources 或复制第二 schema。
4. **CSV 选项准确且不缩水。** parser 与 broker 的精确五词及 utf-8-sig 默认一致。严格 decoder 不自动猜编码或替换坏字节；utf-8 与 utf-8-sig 的 BOM 行为不能静默互换。受限 digest r1 只有默认编码不代表旧能力消失，主稿明确要求正式接线保留其余显式编码及各自验收，没有虚称本轮重验全部编码。
5. **sheet 边界准确。** CSV options.sheet=null 与 Table.sheet=CSV 分离。XLSX parser 检查非空字符串及实际存在，不执行 strip/NFC，也没有在该参数检查处加公共长度限制；broker 的非空、NUL拒绝和256 UTF-8字节上限是额外私有选择规则。inspection 的 null 不提供预览 proof。文稿/facts没有把这些层次拼成已冻结公共 schema。
6. **r4 与 broker 无必然冲突。** receiving 精确重复、sealed 全 append 拒绝、清理终态不复活都属于传输状态，与独立检查字节入口不同。已有 claim 可在当前授权下按原完整请求对账，不能把序列化 AdmissionProof 反造为 WeakMap SourceProof；首次新写仍需真实 proof、dispatch guard、权威受理/revoke排序和 Store 原子门。未把本地取消、旧lease或旧append当成已提交撤销。
7. **来源索引全匹配。** facts 中八条固定303源记录的长度和SHA及两份T01固定文档SHA均逐条核对一致；已读 probe/pyproject/包内记录的三库版本为3.1.5/2.0.0/0.7.1，未冒充完整锁或正式worker接线。未重复提取0b74 Table数据。

## P3：主稿 r4 段建议显式保留两条原有分流条件

位置：首读主稿第55–56行。facts 的 r4ProofAlignment 已明确已有claim先于live lease/proof/CAS检查；主稿可同步写明已有claim只读对账不重验当前域base/CAS或新人类确认，避免恢复后的真实已受理结果被今天的域变更拒绝。

“未admit lease失效后必须新预览/新proof/新人确认”应加原请求结论前提：若原请求仍可能迟到，保持原身份unknown并取得r4的barrier/fence/事务结论；只有证明原请求未受理且不能再迟到受理，才可按新确认开始新operation。不能只据本地lease失效或not-found换operation绕过unknown。

这两条来自固定r4 §3.2–4，不新增协议或更改broker。主稿其余文字及facts并未否认这些条件，因此本项是精确化建议，不是运行缺陷结论。

### 最终材料与关闭复核

已只读回核主稿 r4 两条修订及 facts 对应字段：主稿最终 SHA-256 为 `df94bdec2bdb66659941e36bc8ee853bc79b54765527bf4b08b342da93814a6c`，facts 最终 SHA-256 为 `832a2fc6b4758293afa03976ae218d8787db9012a8e47483ef9b7cf963f5f1ee`。

已有 claim 现在明确只在当前项目读权限和原完整请求/context 下对账，不重验旧 proof/live lease、当前域 base/CAS或新人确认；原 operation unknown 时保留原身份并取得 barrier/fence 结论，只有已证明未受理且不会迟到受理才可通过新真实确认产生新 operation。两项建议关闭；没有产品或权限变化，无需运行测试。

## 通过范围

本报告只确认当前身份事实与设计答复是否忠实于固定材料；不批准 parser producer 提案、canonical digest 实现、wire/profile/配额/GC、typed worker、真实CSV/XLSX→确认→Store接线或平台/双审/CI/发布。原Goal保持blocked，原六缺口及所有父验收不变。
