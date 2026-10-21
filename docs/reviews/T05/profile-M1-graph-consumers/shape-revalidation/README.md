# T05 shape 单路径采用与原图组合复验

本次组合候选 `b3f72d10e3c6ab5eb8eb24247dcd096aea90a0d5` 的完整 `npm run check` 实际 exit0：前端1125 passed/22 files，Python4903 passed/44既有skipped（145.07s），lint/format/types/build/ruff通过；12归档源核验 exit0。

原两规则图和全部13C均实际尝试，15观察为 **13项规范相符、2项pending**。另1项纯输入完整性测试也通过。原四红仅在此固定组合的已证差异关闭；pytest通过数包含pending入口观察与完整性测试，不能宣称13个C规范格全部通过。三张direct图仍未执行。

## 精确采用与冻结

原树及分支保持不变，起点 `4b8bc6bedcd1d1726259b322c6f6f77b529d16ea`。采用前HEAD/clean、145项旧身份和旧201项过程闭包均实核。唯一替换 `packages/engine/src/ontolearn_engine/semantic.py`，从I05固定Git `3bd19e347051627242197f15fce712c9c9dd6b8f` 逐byte复制：原53978B / `5d7413e6ed09f3b62958c6840db499722f2ef7cf0ede1a22415bdce64572f68e`，新54174B / `24f3c57f7995a7f4b901599e6f7837eb328355459f151e811dce01f6b38a173d`。仅_shapes两集合变化（11新增/2删除），未整commit采用；semantic维护责任仍属原I05。

原test仍28706B / `3ee46c9c633cdb611cf75a6fae3148b6abad8828ebf55327138549ad7cb8811c`，fixture仍5962B / `dc57792093204d85c2e54471c271965c40b7ccd7e5cd6f4614173e1497c332f6`；所有golden不变。采用后145项全部只读，没有新产品路径、I05新增测试、directSteps或观察器修改。新过程仅在本目录；旧201过程及旧主文仍逐byte等4b8，旧9相符/4红/2pending与exit1历史不覆盖。

## 四格实际闭合证据

| 原红ID                      | 新实际Validator.run | 完整真实报告                                           |
| --------------------------- | ------------------- | ------------------------------------------------------ |
| C-langString                | 1                   | conforms=true，零违规                                  |
| C-inclusive-nni             | 1                   | conforms=true，零违规                                  |
| C-inclusive-dateTime-equal  | 1                   | conforms=true，零违规                                  |
| C-inclusive-dateTime-before | 1                   | conforms=false，1条MinInclusiveConstraintComponent违规 |

原测试独立golden未放宽，四项均真实从入口到原Validator返回；RDF报告和原API的conforms、focus/path/value/sourceShape/component/severity逐字段匹配。四份report.nt与report-text原件新增入包，实际bnode保留，不制造固定ID或可选value。本次共9份真实SHACL报告、2次query完整projection。见 `four-case-closure.json` 的完整actual/expected和原件索引。

C-inclusive-date-entry仍check-shapes/INVALID_SHAPE，C-illtyped-entry仍parse-data/INVALID_LITERAL_LEXICAL，均Validator.run=0、无正常报告。原条件预期与政策缺口独立保留，两个入口观察通过不等于规范报告验收。

两规则图沿原prepare→production→restore真实路径，完整外7/native15/child11、when/bindings顺序、typed values/source、3head occurrence→2RDF、真实C/R/L与物料均保全；false→error保实际顺序、完整诊断、无成功payload/restore结果。输入/golden分离，query/SHACL没有另加reason或伪造C/R费用。费用事件条数不当预算用量；retention逻辑与物理释放、H租约、容量/性能仍分开。

## 封存与交付边界

`shape-normal-originals.zip` 为1309655B / SHA `55759b2f143035e6064d00f4d7fd01b51955524fceb1c84963ae6251abc166b4`，87成员/15观察。结束后立即新包封存，包含完整原command双流、argv/cwd/env/exit和所有actual；逐member bytes/SHA/CRC核同。相对旧79成员新增四格各两份真实报告，共8成员。为满足本窗口全部原件留存要求，此约1.3MB压缩包随过程入库。

新环境沿本树独立venv/node_modules/cache，输出 `build/graph-actual/shape-normal`，basetemp `build/graph-basetemp/shape-normal`，未复用旧run。`controlled145.json`、`preflight.json`、`frozen-old201.json`、`audit-result.json`、`command-ledger.json`绑定来源和新候选；源前后原字节及最小patch留本目录。独立审查结论另记 `independent-review.md`。`delivery-manifest.json`仅排除自身精确路径，覆盖本次所有过程文件；最终过程commit在总控交接消息另给，避免自引用。

本次不关闭父M1、两项pending、三direct、正式Job/Store/worker/selected、83/E5/repair或指定同版双外审/CI/目标OS真人/develop门。无GUI/Electron运行/e2e/native/HMR、凭据、外部模型或付费，无push/PR/merge；Goal未改。
