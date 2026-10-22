# R4 固定候选交接

revisionBase=6bb1c1e5a4250468f894033e42864d480ccdb815。candidate/process实际提交后在r4-author-process-receipt.json与最终交接列出，本文不预填未来hash。旧R1–R3源、输入、manifest、Fail、首失败、隔离事故和数学/golden都保原件；新写面仅两授权fee docs前缀，AGENTS15147B/de15保持M且不stage。

请先核R3正式Fail与[r4-disposition](../../../reviews/I05/independent-fee-spec/r4-disposition.md)，从整数ID/另一外层无效JSON直接调用完整入口验证pointer、N=0无dummy、真实metadata费用/H01/receipt/清理，再核when/head的disabled/零match非法类变量与合法binding正例。不能用小error程序替代完整入口。原更早resource、alias与严格执行器继续作为必要回归，旧未变numeric/小Ledger不重复运行。

工作目录为本fee树，Python固定`/Users/kyle/.local/share/uv/python/cpython-3.12-macos-aarch64-none/bin/python3.12 -B`。v4所有脚本先静态AST/import核后执行；命令原流在review新r4记录中。attempt证据不可覆盖，如复核请另名保存。

| v4实际命令                                                                          | 结果                                                                                             |
| ----------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| verify_r4.py focused-entry-03 test_complete_failures_r4.py produce_complete_r4.py   | 6个方法（含参数化metadata/类正反/原六例/alias）exit0；27完整程序生成exit0                        |
| run_reference.py --attempt baseline-03 --baseline-only                              | baseline2455分析=执行项，exit0                                                                   |
| run_reference.py --attempt all114-02                                                | 114分析236545/执行236484，exit0                                                                  |
| check_determinism_r4.py 02                                                          | 114+6+21=141两seed的双hash/金额/已付/首错/receipt一致，exit0                                     |
| verify_r4.py bind-and-audit-01 bind_per_id.py audit_execution_r4.py                 | binder exit0；audit首Fail exit1原件保留                                                          |
| verify_r4.py final-readonly-audit audit_execution_r4.py                             | 默认只读审计，exit0；交审不传--write-delta                                                       |
| audit_execution_r4.py --write-delta（作者显式生成新差表；final-delta-audit-06记录） | baseline+27完整双tape/IFR3/第二encoder/字面；114逐ID E00/when/R16金额差表/cap/峰/字段保全，exit0 |

baseline C0work3279051/scan2275390/hash823438，ENTRY/G为176580/185814，M0141824（when类门262），H01152824/receipt792B和whole-H峰149697/6819815不变。新增正常价格为E00以及when类门（含实际R16重编译），114每项都有独立公式及pointer，不按actual调价。113项原cap内、E.5 round4首拒13732仍是input255390+12342>262144，不返回成功前缀。

首失败包括rg不存在文件exit2、原locator误拒导致状态assert exit1、独立计划长度1121→1100的audit exit1、后续独立审计遗漏bare-IRI语法与R16重编译各exit1；源/raw/实际流均保，旧exit0只保持其原范围。格式显式--ignore-path /dev/null，最终清单排自身和process receipt避免循环；旧件opaque current=revisionBase Git保护，新候选逐成员current=Git=SHA，commit前实际cached check。

现行source/native/wire/fingerprint/plan codec、同次真实17L/capture/issuer/usage、owner H/调用许可继续pending；不以提案完整数学账代填。未执行产品/pytest/npm/build/native/DB/GUI/network/install/version/model/push、旧collector或无改动numeric/小Ledger；T05候选未改。发现是否关闭由独立delta审查决定。
