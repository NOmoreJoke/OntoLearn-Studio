# I05 source/package pure-input generation

仅完成纯输入准备与结构验证；未运行产品、测试、CLI、打包程序、语义库或业务算法，不能将本报告视为业务运行通过。

固定供应 `6891a5842302859a531cf82767c5a482417bc274`；合同 `ee2b30a2dad35b2d395f9c735aff80371ab41110`；B1 原输入方法 `523c478d5f39671c4ac7c1ea6997e51d3047d58e`。生成器仅依赖 Python 标准库，从固定 Git 字节读取原件，或做显式 AST literal／JSON 白名单提取和命名输入变换。

输入资产 8205267 bytes / SHA-256 `47c66ffe18613eb8cc1af6365dcfc9d866821f22c48f96d9f44725f8f7c59eaa`；manifest 21202 bytes / SHA-256 `0b91c1a9366d170b5614d94c20006054a5a959be235e0f46cb150cf32335193a`。共 417 observations、320 去重 datasets、22 固定原件。硬上限 512／8MiB／1MiB 均在写出前检查；未按 cap 删除用例。

原83、106 operations、54 learning checks、50 product cases、5 unresolved 均保留。82 个 eligible、79 个 full，交集 78；transfer:repair 的 profile 调用保留 not-executed，并另用真实 SHACL 纯输入表达修复前后。四 E5 输入保留 fragment，不能升级为完整原项目／原操作通过。原106/54均维持未执行状态，原操作全文与独立 expected 只在审计原件中。

C 的13个原 caseId全部引用；C date/illtyped 以显式 policy 组合扩展，不能误称17个原case。运行时 datasets 不装入 golden、expected、实际结果、推理闭包、已算 matches、basis、native carrier 或恢复前提；原规则定义 heads 属于合法输入并保留。

dataset digest 与资产采用 `json.dumps(ensure_ascii=True,sort_keys=True,separators=(',',':'),allow_nan=False).encode('ascii')`，资产另加一个 LF；不配对 surrogate 保留为 decoded 输入值而不回显。raw 原件 bytes/SHA 另外固定，不能将新 JSON digest 冒作原 SHA。

## 入口与来源

parse→turtle；query→query；legacy-reason→legacy；scope→scope；profile→profile；fullview→records/profile/turtle；dag→records/turtle；restore-negative→records；shape/shacl-text→shape；offline→query/turtle/shape；b1-measurement→b1。每 observation 绑定 exact dataset digest、固定 sourceRefs 和上下文状态，详细参数和全部有序 selector 在两份 JSON 中。

规则 structured terms 使用 kind/lexical_form/datatype_iri/language_raw/source 五字段；SourceRecord 为 reference/digest/revision/text 或 null。原83 source 为原 path/ref/sha256/pointer，未重新计算 definition 摘要、匹配或业务值。rootsTargets 为三项 N3 key，restore mutation 只描述如何在真实 producer/restore 边界扰动，不携带任何 payload/rows 摘要或预设输出。

scope 含 asserted/fresh/project 与七个选择失败/分区模式，须由真实 prepare→project 再交 query/SHACL 消费。fullview/DAG 含四 finite 分支、depth2、同轮首 witness、原始 alias、双 head occurrence 和 text 拒绝。restore 变体覆盖末项 source/definition/limits/child、unknown key、depth/forward premise、统一 leaf rename、1023/15 occurrence。纯 JSON 不模拟 native foreign／私有故障对象。

SHACL 含 C 全量、原 V01 与 transfer repair 前后、有限模板和 shape 前门；整数 B 的 strict/WIDE、UTC bound/value 双侧正负、混合两侧、缺 target/value、legacy 隔离、D1 三顺序×两路径、原 public exact/overcap 和 graph/text 前门。私有少一票、native 库兼容故障与 hook 费用正确性不能由输入资产执行，须由已授权产品测试或独立审查另验。

B1 两 selector 各只含一个 b1-measurement 输入，固定 seed=20261019、scale1/10、18×scale fresh asserted input 与原四 ontology text，明确 equipment type 替换输入；不导入 Store fixture/helper。十 ontology suite 是另一个语义用例。full-v1 中两个 B1 observation 允许 instrumented/nonfresh，不能冒作独立 fresh 测量证据；只有专用 selector 供后续无 hook fresh 进程。

offline 覆盖八类 SERVICE/FROM、格式拒绝、imports 三角色×两 scheme、九类非支持 SHACL 与真实 implicit JSON-LD 边界；example.invalid/file 字符串均为拒绝输入，生成过程无网络或文件业务读取。

## 结构与可复现检查

允许命令（cwd 为当前精确 worktree）：`python3 scripts/generate-i05-source-package-inputs.py`；`python3 scripts/generate-i05-source-package-inputs.py --check`。后者只从相同固定 Git/原件重建并逐字节比对，不覆盖；未知参数拒绝。生成器内验证 exact root/kind/observation 字段、operation-kind 对应、源 bytes/SHA、dataset digest、原context数量及未执行标志、C13集合和全部 cap。

首轮准备命令 exit1：原 query 路径误带 queries/，在读取固定 Git 原件前即失败，未写出 runtime assets；已改为固定原件真实 product-baselines/unclosed-high.rq 后重建。另两次只读定位命令确认 supplier 不包含旧 semantic_probe；implicit JSON-LD 方法改引用固定 C4 原件，未运行旧 probe。原失败工具输出保留，不当作业务失败或通过。

实际准备记录：修正路径后 generate exit0；补充六个 query 前门与八个 bad-IRI policy 组合后 generate exit0、--check exit0；另以标准库 ast.parse 完整检查生成器语法 exit0。最后固化说明后再次 generate/--check 仅核可复现字节。所有步骤 cwd 均为 I05-source-package-probe，未设置业务 env、未导入业务模块。stdout 是有限 metadata JSON，stderr 成功时为空；首次失败的 traceback 已保留在本会话原输出。

准备结果与原件清单见 inputs-source-manifest.json；本报告列出的 source-path/JSON pointer 属于输入出处，不能补齐 unresolved 原上下文。后续主线必须执行真实 canonical dispatcher、完整报告与双端对比，并保持 B1 fresh 条件与原失败边界。

## R1-03 delta：报告 EOF

R1 正式 Fail 原件保留于 review-r1.md／cf15439；固定旧候选 0e42a0fe349054a92817cb4d463bccdc15f6c042 的首 EOF 失败为 `input-generation-report.md:497: new blank line at EOF.`，base→candidate diff check 原 exit2 不改写。

本 delta 只将 generator 报告输出尾部规范为恰一个 LF（移除 join 后遗留的空白行），并重建本报告及 inputs-source-manifest 的 generator bytes/SHA。所有输入、dataset、观测、selector、两件 runtime JSON 字节均保持原值；未删用例，未改产品或测试，未执行产品／库／测试，未 stage／commit。

本 delta 实际执行 generator generate 和 --check，均 exit0；另外以纯标准库比较两件 runtime JSON 的 before/after bytes 与原冻结 SHA、核报告末尾恰一个 LF。R1-01/02 由对应 writer 处理，不能用此 EOF 修复声称整体审查通过。

## family counts

- `b1-measurement`: 2
- `consumer-C-date`: 4
- `consumer-C-integer`: 2
- `consumer-C-query`: 2
- `consumer-C-shape`: 9
- `dag-fullview`: 19
- `integer-policy`: 39
- `legacy-rule`: 4
- `offline`: 28
- `original-query`: 2
- `original-shape-repair`: 3
- `profile-83`: 83
- `rdfs`: 1
- `rdfs-finite`: 7
- `readonly-query`: 25
- `restore-negative`: 14
- `scope`: 10
- `shacl-front`: 31
- `shape-template`: 19
- `transfer-shape-repair`: 2
- `turtle`: 1
- `turtle-lexical`: 17
- `turtle-rejection`: 9
- `utc-date`: 76
- `utc-date-D1`: 6
- `utc-date-public-budget`: 2

## 完整 selector 表

### full-v1

1. `profile-83/baseline:G-base`
2. `profile-83/baseline:G-behavior`
3. `profile-83/baseline:G-map-empty`
4. `profile-83/baseline:E.5`
5. `profile-83/A-01:steps:1`
6. `profile-83/B-01:steps:0`
7. `profile-83/B-02:steps:0`
8. `profile-83/B-03:setup:0`
9. `profile-83/B-03:steps:0`
10. `profile-83/B-04:steps:0`
11. `profile-83/B-04:steps:1`
12. `profile-83/B-05:steps:0`
13. `profile-83/B-06:steps:0`
14. `profile-83/B-07:steps:0`
15. `profile-83/B-09:steps:0`
16. `profile-83/B-10:steps:0`
17. `profile-83/B-11:steps:0`
18. `profile-83/M-01:steps:0`
19. `profile-83/M-02:steps:0`
20. `profile-83/M-02:steps:1`
21. `profile-83/M-03:steps:0`
22. `profile-83/M-03:steps:1`
23. `profile-83/M-03:steps:2`
24. `profile-83/M-04:steps:0`
25. `profile-83/M-04:steps:1`
26. `profile-83/M-06:steps:0`
27. `profile-83/M-06:steps:2`
28. `profile-83/O-01:setup:0`
29. `profile-83/O-01:steps:0`
30. `profile-83/Q-01:steps:0`
31. `profile-83/Q-02:setup:0`
32. `profile-83/Q-02:steps:0`
33. `profile-83/R-01:steps:0`
34. `profile-83/R-02:steps:0`
35. `profile-83/R-02:steps:1`
36. `profile-83/R-02:steps:2`
37. `profile-83/R-02:steps:3`
38. `profile-83/R-03:steps:0`
39. `profile-83/R-03:steps:1`
40. `profile-83/R-03:steps:2`
41. `profile-83/R-03:steps:3`
42. `profile-83/R-04:steps:0`
43. `profile-83/R-04:steps:1`
44. `profile-83/R-04:steps:2`
45. `profile-83/R-05:steps:0`
46. `profile-83/R-05:steps:1`
47. `profile-83/R-05:steps:2:order:0`
48. `profile-83/R-06:steps:0`
49. `profile-83/R-06:steps:1`
50. `profile-83/R-06:steps:2:order:0`
51. `profile-83/R-06:steps:2:order:1`
52. `profile-83/V-01:steps:0`
53. `profile-83/V-01:steps:1`
54. `profile-83/V-01:steps:2`
55. `profile-83/V-01:steps:3`
56. `profile-83/extension:CMP-EQ-TRUE`
57. `profile-83/extension:CMP-EQ-FALSE`
58. `profile-83/extension:CMP-NE-TRUE`
59. `profile-83/extension:CMP-NE-FALSE`
60. `profile-83/extension:CMP-LT-TRUE`
61. `profile-83/extension:CMP-LT-FALSE`
62. `profile-83/extension:CMP-LE-TRUE`
63. `profile-83/extension:CMP-LE-FALSE`
64. `profile-83/extension:CMP-GT-TRUE`
65. `profile-83/extension:CMP-GT-FALSE`
66. `profile-83/extension:CMP-GE-TRUE`
67. `profile-83/extension:CMP-GE-FALSE`
68. `profile-83/extension:JOIN-NO-CROSS-ALARM`
69. `profile-83/extension:MULTI-OUTPUT-ONE-FIRING`
70. `profile-83/extension:DISABLED-RULE-NO-OUTPUT`
71. `profile-83/extension:MISSING-PROPERTY-IS-NOT-A-NEGATION`
72. `profile-83/extension:CMP-EQ-ABOVE-FALSE`
73. `profile-83/extension:CMP-NE-ABOVE-TRUE`
74. `profile-83/extension:CMP-LT-ABOVE-FALSE`
75. `profile-83/extension:CMP-LE-BELOW-TRUE`
76. `profile-83/extension:CMP-GT-BELOW-FALSE`
77. `profile-83/extension:CMP-GE-ABOVE-TRUE`
78. `profile-83/transfer:repair`
79. `profile-83/transfer:classification`
80. `profile-83/E.5:event-fragment:round:1`
81. `profile-83/E.5:event-fragment:round:2`
82. `profile-83/E.5:event-fragment:round:3`
83. `profile-83/E.5:event-fragment:round:4`
84. `C-query-numeric-promotion`
85. `C-query-type-error`
86. `C-datatype-exact`
87. `C-langString`
88. `C-count-term-identity`
89. `C-in-term-identity`
90. `C-inclusive-numeric`
91. `C-inclusive-nni`
92. `C-inclusive-dateTime-equal`
93. `C-inclusive-dateTime-before`
94. `C-inclusive-type-error`
95. `C-inclusive-date-entry/strict/legacy`
96. `C-inclusive-date-entry/strict/utc-date-range-v1`
97. `C-inclusive-date-entry/integer-illtyped-report-v1/legacy`
98. `C-inclusive-date-entry/integer-illtyped-report-v1/utc-date-range-v1`
99. `C-illtyped-entry/strict`
100. `C-illtyped-entry/integer-illtyped-report-v1`
101. `utc-date/C-before`
102. `utc-date/C-offset`
103. `turtle/G-base-fixture`
104. `rdfs/ten-ontology-suite`
105. `b1-semantic/1x`
106. `b1-semantic/10x`
107. `query/ask`
108. `query/words-in-string`
109. `query/optional-unbound`
110. `query/count`
111. `query/order-tie`
112. `query/filter`
113. `query/string-distinct`
114. `query/string-count`
115. `query/insert-update`
116. `query/delete-update`
117. `query/construct`
118. `query/describe`
119. `query/invalid`
120. `query/load-update`
121. `query/rand`
122. `query/now`
123. `query/uuid`
124. `query/struuid`
125. `query/bnode`
126. `query/string-expression-0`
127. `query/string-expression-1`
128. `query/string-expression-2`
129. `query/string-expression-3`
130. `query/string-expression-4`
131. `query/string-expression-5`
132. `turtle/numeric-lexical-0`
133. `turtle/numeric-lexical-1`
134. `turtle/numeric-lexical-2`
135. `turtle/numeric-lexical-3`
136. `turtle/numeric-lexical-4`
137. `turtle/numeric-lexical-5`
138. `turtle/numeric-lexical-6`
139. `turtle/numeric-lexical-7`
140. `turtle/numeric-lexical-8`
141. `turtle/numeric-lexical-9`
142. `turtle/string-identity-0`
143. `turtle/string-identity-1`
144. `turtle/string-identity-2`
145. `turtle/string-identity-3`
146. `turtle/string-identity-4`
147. `turtle/lang-case`
148. `turtle/integer-distinct`
149. `turtle/front-0`
150. `turtle/front-1`
151. `turtle/front-2`
152. `turtle/front-3`
153. `turtle/front-4`
154. `turtle/front-5`
155. `turtle/front-6`
156. `turtle/front-7`
157. `turtle/front-8`
158. `rdfs/type`
159. `rdfs/domain-depth2`
160. `rdfs/range`
161. `rdfs/subclass`
162. `rdfs/cycle`
163. `rdfs/domain-first-witness`
164. `rdfs/range-first-witness`
165. `legacy/no-rule-feedback`
166. `legacy/multiple-matches`
167. `legacy/repeated-variable`
168. `legacy/unbound-head`
169. `scope/asserted`
170. `scope/fresh`
171. `scope/project`
172. `scope/missing-source`
173. `scope/wrong-source`
174. `scope/missing-result`
175. `scope/nonexact-include`
176. `scope/unselected-rules`
177. `scope/unselected-result`
178. `scope/facts-axioms`
179. `original-Q01`
180. `original-Q02`
181. `original-V01-before`
182. `original-V01-missing`
183. `original-V01-repaired`
184. `transfer-repair-before`
185. `transfer-repair-after`
186. `dag/type`
187. `dag/domain-depth2`
188. `dag/range`
189. `dag/subclass`
190. `dag/first-witness`
191. `dag/cross-rule-witness`
192. `dag/range-literal`
193. `fullview/raw-aliases`
194. `dag/raw-aliases`
195. `fullview/two-head-occurrences`
196. `dag/two-head-occurrences`
197. `restore/fullview/payload-unknown-key`
198. `restore/fullview/tail-source-tamper`
199. `restore/fullview/tail-definition-tamper`
200. `restore/fullview/tail-limits-tamper`
201. `restore/fullview/tail-child-tamper`
202. `restore/explanation/payload-unknown-key`
203. `restore/explanation/tail-source-tamper`
204. `restore/explanation/tail-definition-tamper`
205. `restore/explanation/tail-limits-tamper`
206. `restore/explanation/tail-child-tamper`
207. `restore/explanation/dag-depth-plus-one`
208. `restore/explanation/dag-last-premise-forward`
209. `restore/explanation/leaf-rename-all`
210. `restore/explanation/head-occurrence-1023-15`
211. `fullview/turtle-entry`
212. `dag/turtle-entry`
213. `fullview/profile-0`
214. `fullview/profile-55`
215. `fullview/profile-73`
216. `fullview/profile-74`
217. `fullview/profile-75`
218. `fullview/profile-76`
219. `shape/front-0`
220. `shape/front-1`
221. `shape/front-2`
222. `shape/front-3`
223. `shape/front-4`
224. `shape/front-5`
225. `shape/front-6`
226. `shape/front-7`
227. `shape/front-8`
228. `shape/front-9`
229. `shape/duplicate-target`
230. `shape/duplicate-path`
231. `shape/arbitrary-constraint`
232. `shape/template-datatype`
233. `shape/template-maximum`
234. `shape/template-allowed`
235. `shape/template-minimum`
236. `shape/template-upper`
237. `integer/lexical-0/strict`
238. `integer/lexical-0/integer-illtyped-report-v1`
239. `integer/lexical-1/strict`
240. `integer/lexical-1/integer-illtyped-report-v1`
241. `integer/lexical-2/strict`
242. `integer/lexical-2/integer-illtyped-report-v1`
243. `integer/lexical-3/strict`
244. `integer/lexical-3/integer-illtyped-report-v1`
245. `integer/lexical-4/strict`
246. `integer/lexical-4/integer-illtyped-report-v1`
247. `integer/lexical-5/strict`
248. `integer/lexical-5/integer-illtyped-report-v1`
249. `integer/no-target`
250. `integer/no-constraint`
251. `integer/max-count`
252. `integer/other-datatype-0`
253. `integer/other-datatype-1`
254. `integer/other-datatype-2`
255. `integer/other-datatype-3`
256. `integer/other-datatype-4`
257. `integer/other-datatype-5`
258. `integer/other-datatype-6`
259. `integer/other-datatype-7`
260. `integer/other-datatype-8`
261. `integer/bound-front-0`
262. `integer/bound-front-1`
263. `integer/bound-front-2`
264. `integer/bound-front-3`
265. `integer/bound-front-4`
266. `integer/bound-front-5`
267. `integer/bound-front-6`
268. `integer/bad-iri-subject/strict`
269. `integer/bad-iri-subject/integer-illtyped-report-v1`
270. `integer/bad-iri-predicate/strict`
271. `integer/bad-iri-predicate/integer-illtyped-report-v1`
272. `integer/bad-iri-datatype/strict`
273. `integer/bad-iri-datatype/integer-illtyped-report-v1`
274. `integer/bad-iri-shape-path/strict`
275. `integer/bad-iri-shape-path/integer-illtyped-report-v1`
276. `shacl-policy/data-0`
277. `shacl-policy/data-1`
278. `shacl-policy/data-2`
279. `shacl-policy/data-3`
280. `shacl-policy/data-4`
281. `shacl-policy/data-5`
282. `shacl-policy/range-0`
283. `shacl-policy/range-1`
284. `shacl-policy/range-2`
285. `shacl-policy/range-3`
286. `shacl-policy/range-4`
287. `shacl-policy/missing-both`
288. `shacl-policy/missing-range`
289. `shacl-policy/missing-data`
290. `utc-date/minInclusive/1999-12-31Z`
291. `utc-date/minInclusive/2000-01-01Z`
292. `utc-date/minInclusive/2000-01-02Z`
293. `utc-date/maxInclusive/1999-12-31Z`
294. `utc-date/maxInclusive/2000-01-01Z`
295. `utc-date/maxInclusive/2000-01-02Z`
296. `utc-date/calendar/0001-01-01Z`
297. `utc-date/calendar/9999-12-31Z`
298. `utc-date/calendar/2000-02-29Z`
299. `utc-date/lexical-0/bound`
300. `utc-date/lexical-0/value`
301. `utc-date/lexical-1/bound`
302. `utc-date/lexical-1/value`
303. `utc-date/lexical-2/bound`
304. `utc-date/lexical-2/value`
305. `utc-date/lexical-3/bound`
306. `utc-date/lexical-3/value`
307. `utc-date/lexical-4/bound`
308. `utc-date/lexical-4/value`
309. `utc-date/lexical-5/bound`
310. `utc-date/lexical-5/value`
311. `utc-date/lexical-6/bound`
312. `utc-date/lexical-6/value`
313. `utc-date/lexical-7/bound`
314. `utc-date/lexical-7/value`
315. `utc-date/lexical-8/bound`
316. `utc-date/lexical-8/value`
317. `utc-date/lexical-9/bound`
318. `utc-date/lexical-9/value`
319. `utc-date/lexical-10/bound`
320. `utc-date/lexical-10/value`
321. `utc-date/lexical-11/bound`
322. `utc-date/lexical-11/value`
323. `utc-date/lexical-12/bound`
324. `utc-date/lexical-12/value`
325. `utc-date/lexical-13/bound`
326. `utc-date/lexical-13/value`
327. `utc-date/lexical-14/bound`
328. `utc-date/lexical-14/value`
329. `utc-date/lexical-15/bound`
330. `utc-date/lexical-15/value`
331. `utc-date/lexical-16/bound`
332. `utc-date/lexical-16/value`
333. `utc-date/incompatible-0/bound`
334. `utc-date/incompatible-0/value`
335. `utc-date/incompatible-1/bound`
336. `utc-date/incompatible-1/value`
337. `utc-date/incompatible-2/bound`
338. `utc-date/incompatible-2/value`
339. `utc-date/incompatible-3/bound`
340. `utc-date/incompatible-3/value`
341. `utc-date/incompatible-4/bound`
342. `utc-date/incompatible-4/value`
343. `utc-date/mixed-bounds-no-target`
344. `utc-date/reversed`
345. `utc-date/reversed-no-focus`
346. `utc-date/no-target`
347. `utc-date/no-value`
348. `utc-date/minCount`
349. `utc-date/unrelated`
350. `utc-date/shared`
351. `utc-date/multiple-values`
352. `utc-date/shared-unrelated`
353. `utc-date/integer/strict/legacy`
354. `utc-date/integer/strict/utc-date-range-v1`
355. `utc-date/integer/integer-illtyped-report-v1/legacy`
356. `utc-date/integer-no-target/legacy`
357. `utc-date/integer/integer-illtyped-report-v1/utc-date-range-v1`
358. `utc-date/integer-no-target/utc-date-range-v1`
359. `utc-date/minExclusive`
360. `utc-date/maxExclusive`
361. `shape/date-legacy-entry`
362. `utc-date/legacy-text-isolation`
363. `utc-date/none-data`
364. `utc-date/none-shapes`
365. `utc-date/invalid-turtle-data`
366. `utc-date/invalid-turtle-shapes`
367. `utc-date/surrogate-data`
368. `utc-date/surrogate-shapes`
369. `utc-date/text-limit-data`
370. `utc-date/text-limit-shapes`
371. `utc-date/blank`
372. `utc-date/unknown-datatype`
373. `utc-date/nonfinite`
374. `utc-date/imports`
375. `utc-date/relative`
376. `utc-date/bad-iri`
377. `utc-date/path-arity`
378. `utc-date/fact-axioms`
379. `utc-date/bound-before-facts`
380. `utc-date/facts-before-value`
381. `utc-date/public-budget-43460`
382. `utc-date/public-budget-43461`
383. `utc-date/D1-p0/forward`
384. `utc-date/D1-p0/reverse`
385. `utc-date/D1-p0/rotate`
386. `utc-date/D1-p99/forward`
387. `utc-date/D1-p99/reverse`
388. `utc-date/D1-p99/rotate`
389. `utc-date/graph-limit-before-preflight`
390. `offline/service`
391. `offline/service-silent`
392. `offline/service-variable`
393. `offline/service-nested`
394. `offline/from`
395. `offline/from-named`
396. `offline/base-from`
397. `offline/file-from`
398. `offline/jsonld-context`
399. `offline/jsonld-import`
400. `offline/xml-entity`
401. `offline/n3-formula`
402. `offline/imports-data-https`
403. `offline/imports-data-file`
404. `offline/imports-ontology-https`
405. `offline/imports-ontology-file`
406. `offline/imports-shapes-https`
407. `offline/imports-shapes-file`
408. `offline/shacl-sparql`
409. `offline/shacl-js`
410. `offline/shacl-js-library`
411. `offline/shacl-rule`
412. `offline/shacl-target`
413. `offline/shacl-validator`
414. `offline/shacl-function`
415. `offline/shacl-logical`
416. `offline/shacl-inverse`
417. `offline/implicit-jsonld`

### b1-semantic-1x-v1

1. `b1-semantic/1x`

### b1-semantic-10x-v1

1. `b1-semantic/10x`
