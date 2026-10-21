# 本新组合独立审查

本记录由T05根据独立agent `/root/shape_combination_independent_review` 的实际回复整理。审查者未参与本次采用或过程实现，全程只读，不写文件、不跑产品/测试、不访问网络/GUI。下列为本次组合与原件独审，不代替指定模型双审。

最终结论：限定通过候选 `b3f72d10e3c6ab5eb8eb24247dcd096aea90a0d5`，无新增P1/P2或证据阻断。

- parent精确4b8，唯一产品差异是获准semantic.py两集合复制；145项逐一核source Git/current/candidate/固定manifest bytes和SHA。
- 旧201项逐一仍等4b8及原指纹；原28706B测试、fixture和黄金不改。原测试全文审阅，输入/golden分离、完整两图/报告断言与pending/direct边界有效。
- 最终ZIP 1309655B / SHA `55759b2f143035e6064d00f4d7fd01b51955524fceb1c84963ae6251abc166b4`，全部87成员逐byte/SHA/CRC核同，且与本次原目录/命令原件一致；15观察与index对应，testSourceSHA精确绑定不变2ce39测试。
- 完整stdout全文读回：lint/format/types/build/ruff通过；前端1125 passed/22 files；Python4903 passed/44既有skipped，145.07s；check exit0。12sources exit0。
- 原四红均真实Validator.run=1。前三conforms=true；dateTime-before为完整MinInclusive违规。全部9份report.nt逐实际blank-node核conforms及focus/path/value/sourceShape/component/severity，与原API六字段和只读golden对应；两query完整projection相符。
- 两规则图完整7/15/11 native/restored projection、原rows bytes与digests、完整child batch和originalMatches严格相同；2matches/3heads/2RDF保持。false→error完整诊断及无成功结果/payload保持；实际C/R/L不被替代。

可仅关闭此组合原四格的已证差异。总15观察=13规范相符+2pending，pytest16项还含完整性与pending结构观察。两pending仍原reason/Validator0且无report，三direct未执行。父M1、正式Job/Store/worker/selected、83/E5/repair、指定同版双外审、CI、目标OS真人和发布门不由本审关闭。
