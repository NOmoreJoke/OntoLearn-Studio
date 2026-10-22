# R4 版本与实际退出保全

从6bb1c1e5a4250468f894033e42864d480ccdb815开始，当前保护AGENTS15147B/SHAde15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4全文读核；R3报告全文读，新3.3MB纯adversarial全文JSON解析，分别检查全部9case原输入、异常/全池/事件/receipt/alias摘要。未执行旧reviewer或collector，不读产品、投影、D2、备包算法或v1隔离正文。

1. 新建charge-reference-v4，旧v3逐字节保留。所有新脚本先AST/import和写面静态核，再执行；初次静态8件通过，后续改动的reference/driver、binder/audit分别有pre-execution-static-02/03/04记录。未复制/运行无改动numeric测试或小Ledger。
2. 一次只读rg猜了不存在的profile-contract.md/schema.json路径，实际exit2；之后先rg --files定位正确既有纯输入。保此查询事实，不包装为模型通过，亦未扩大输入。
3. focused-entry-01两个命令exit0：5个focused方法和21完整程序生成。baseline-01生成也exit0，但实际29项metadata拒绝，旧driver只断生成/金额而未断固定positive状态。随后实际baseline-state-first-failure断言exit1，完整source和失败baseline raw保在r4-first-failure。缺陷是我把原definitions.source定位locator误作typed四字段SourceRecord；这个测试覆盖缺口与错误拒绝不能被此前exit0掩盖。
4. 修正raw definitions locator与typed rules SourceRecord形状，locator不当许可/SourceRecord；fixed114 driver增加不允许非RESOURCE的意外语义拒绝。没有改输入。改动源静态审后，focused-entry-02两命令exit0；baseline-02完整2449项成功；all114-01完整生成exit0；final-determinism-01实际135程序两seed相同exit0。前版本的有限成功记录保持。
5. bind-and-audit-01 binder exit0/114金额非null；独立audit exit1，错误字面把variable-class计划INPUT估成1121B。保audit raw和stderr；独立第二编码按R头5+definitions560+Catalog96+limits439=1100B、101nodes、static72得1273work，修手算/audit断言，不改reference/收费。再静态审后independent-audit-02实际exit0。
6. 当时head阶段source1df4e7d9d34f2f182d37d8b445332e33c57dbc444aeb272cf3cdf2a17b0f17e8；每ID E00独立差表验证其它钱包金额、cap、whole-H峰不变，原现行/数学字段保留。source occurrence发生点明确record-term.source及definition.source，definition常量TermInput.source仍属M0，不扩大C0收费。

最终格式仅新md/json、显式--ignore-path /dev/null；原/raw/所有Fail流不动。清单self-exclusion仅新manifest自身和后续author-process-receipt，旧清单全部保留。candidate提交前执行实际git diff --cached --check，提交后验证current=固定Git=SHA、index空和仅AGENTS M。固定refs/完整退出见process receipt；未执行产品/pytest/npm/build/native/DB/GUI/network/install/version/model/push或原collector。

7. 根按integration59+64原文确认when/head都要求固定已声明类TermInput；不作用普通输入RDF图，也不改legacy。此前提出疑问及135程序成功只保当时head范围，source/audit/delta已raw保留。新增when固定类型门1work、完整classes每occurrence扫描及reference1work；93个固定114 producer当次when检查与6个R16重复检查全计，未读产品/修改输入。全纯输入observations扫描另有111项when（是输入全集口径），无Variable冲突；最终所选114的已执行编译口径为93+6，不混计数。

8. focused-entry-03两个命令exit0：6方法/27完整程序；baseline-03 2455项成功、all114-02生成exit0；final-determinism-02实际141程序两seed一致exit0。补when后的独立差表审计final-delta-audit-04 exit1：我只认<IRI>，漏了固定raw predicate/subject的bare完整IRI，导致M0差表错误。保raw和stderr，修独立raw字段解读，不改reference。final-delta-audit-05又exit1：我遗漏fullview恢复R16-child的实际重复compile，因此漏了那里的同一when门收费；保raw后明确仅已开户R16列同样增量，negative held-byte门未开户不能收费。再次静态审后final-delta-audit-06实际exit0。两次都是审计范围缺项，不能用之前exit0冒全差表已证。

9. 最终reference bc47b16bf528b973aeebcc0be4a103bf00acbf0f351485f5370510817bf1467c。114分析236545/执行236484，原cap均不变；唯一E.5 round4资源首拒13732，input255390+12342>262144，已有work404868/scan43159。每ID独立算E00+producer和真实R16的when门后逐域交叉，未依actual调价。独立audit默认只读，只有作者明确--write-delta时生成本轮delta；交审使用默认只读调用。
