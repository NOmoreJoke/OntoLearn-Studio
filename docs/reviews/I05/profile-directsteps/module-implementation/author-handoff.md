# 新纯模块作者交付记录

本记录是作者实现说明和纯 helper 运行证据，不是独立预算审查结论，也不是实际 producer 图运行证据。

冻结来源为本树 adoption `78e9cf7f26dc039e99ec6725d7de8a396d1298d2`，原 base `5f910b52c69d86a1076b2032e5d3c63e715947f3`；139 成员来自固定清单中的 `6c1eec41091a997f898cb448bfc7d4000c154307`。本树未修改这 139 个成员；`clean-final-adopted-139-members.json` 逐个保存当前 bytes/SHA 和 matches=true。

唯一新产品文件 `packages/engine/src/ontolearn_engine/semantic_profile_directsteps.py`：46459 bytes，SHA256 `7927769077e363b23741f6dc78b7c0ec2ad00b7d3285f8403a190c0e00169b22`。新增职责包括固定四域 ledger、binary byte trie、TripleKey/RDF identity 编码、私有 capture、固定 carrier 局部 DAG 校验、纯 roots 定位。仅导入标准库 dataclasses 和原 TermInput；没有 reasoner、restore、Graph、ProfileValue、Job、网络或模型调用。

固定常量：version `i05-direct-rdfs-steps/1`；budget `i05-direct-steps-budget/1`；候选上限 250000，步骤上限 100000−seedCount，K 和 B 各 8388608；work/scan_copy 各 581671040，objects 270635588，scalar 50331776。override 只允许四域 exact tuple、非负 exact int，逐域取 min，不扩默认 cap。

## 方法与费用来源

完整 51 个方法的起止行见 `clean-final-source-method-inventory.json`；40 个循环/推导式的原文与所在方法见 `clean-final-source-loop-inventory.json`。以下说明实际收费位置和所有权，使用 W=work、D=scan_copy、O=objects、S=scalar。

| 方法/组 | 实际费用与边界 |
| --- | --- |
| DirectStepsFailure.__init__ / _require | 固定 reason/classification/stage/domain；不嵌入输入、路径或异常文本。 |
| Ledger.__init__ | 固定至多四个 override 的精确类型/重复检查；没有输入规模新容器。实际动态 counters/events 在 begin 两域控制门后建立。 |
| begin | O/S 都先满足 128；不足时 used/live/peaks/caps 仍 None；固定 begin 事件在控制块中。 |
| usage / events | 返回已经存在的字典/有限事件列表引用，不产生未经付费副本。 |
| _running / _active | exact ledger 和 single-use 状态门；receipt 后普通 charge 拒绝。 |
| _apply / debit / charge / reserve | 每次事件自身 16W/16O/128S；scan_copy 数量同时进入 W 和 D。reserve 额外预付两个 cleanup 事件，总计 48W/48O/384S 再加实际票；先比较全部四域再更新/append。 |
| release / discard | 引用实际删除后消费既有 cleanup credit；事件维持累计 W/D 和四域相邻 before/after 链。只能释放已发数据票，不释放固定控制/事件元数据。失败/完成态仍能用预付 credit 清理。 |
| enter | 先 1W 和自身事件再切换有限 stage。 |
| consume_key | 每次 encode/lookup/put 实际 key bytes 累计到 K，先 count+1 W；重复访问仍计入 K。 |
| note_carrier | 检查实际 B≤8MiB，1W 后记录 max。完整新 J projection/rows/stream/hash 的先票由主树调用方负责；本模块不生成第二份 wire 来测长。 |
| receipt | 先 eventCount+64 W、8*(eventCount+8) D、eventCount+96 O、1024S，再冻结 tuple；used/live/peaks/caps 和 events 都只复制已付容量。 |
| completed / transferred / failed | 固定状态转换；不回退累计费，不把 failed/completed 变回 running。直接底层 debit/reserve 失败由 owning 入口标 failed；capture/validator 的失败路径自行标记。 |
| _triple / _sequence / _integer / _object | 精确 native 类型、固定键表和有限长度；_object 对所有 incoming key 先 exact str 门，再做固定字段读取，避免外来 hash/equality 回调。每个扫描收 W，字段比较保守 D。 |
| _parts / encode_triple_key | 3×uint64BE 长度头，原 UTF8，无分隔歧义。先2*upper+32 D、8O、3*upper+128 S；逐字检查 surrogate 和实际 UTF8 宽度，再 K 票，才创建 bytearray/UTF8/bytes。清掉临时后保留返回 bytes 票。 |
| _term_identity / encode_identity_key | IRI kind=1；literal kind=2、lexical/effective datatype 各长度段、language presence 和 lower-language 段；triple 外层再3长度段。None dtype 与 xsd:string 相同，raw case language 归 lower，数值 lexical 不归一。每个新 lower、term buffer、外层 bytearray/bytes 的并持分别先票。 |
| ByteIndex.__init__ | 每节点 list+3 slots=4O，root 先票。 |
| ByteIndex.get | 每 byte 8 条二进制边，先16*len+4 W 和2*len D，再遍历；K 先票。 |
| ByteIndex.put | 同 get，另先4*(8len) W 为初始化，4*(8len) O 为节点最坏量；实际创建后释放未用票，不使用动态 native hash。 |
| ByteIndex.drop | 先删除 root，再按真实 nodes*4 释放；有限树由引用计数删除，不递归遍历业务 DAG。 |
| Capture.__init__ | 8O 固定控制容器，trie 自付；新 ledger 自动 begin。 |
| candidate / end_candidates | 每个候选（包括最终重复候选）先8W、4O，再增长计数；批消费后释放4*count O。parent 新 sort record/三个 key 引用需要额外 D 票，不包含在该4O内。 |
| Capture._reference | 每个 canonical key encode/get；未见 key 的 _Seed 先4O、4*encodedLen S，再 append/put；临时 encoded 消失后释放。 |
| insert | 仅真实首次闭包插入调用。重复结果整次 invalid/drop/failed，不覆盖已有；三原 key 类型门与 trie lookup，先32W、12O、4*encodedLen S，再分配 fixed step。depth 直接取两个已见对象的 depth；不检索 union witness。 |
| link_seed | 只连接原实际 leaf ID；固定74字符 lowercasehex语法门，不重 hash/签发 leaf。先字符串 scan/4*IDlen S，再写 seed reference；未用作 premise 的原 seed 也会入索引，保证 seed 完整。 |
| finish | 检查所有 seed 已 link 和 S≤100000−N；先 N+16S+4 W、48S+16 O。另预留 _owned_scalar 给仍持有原 result strings/leaf ID 的 native carrier；capture.drop 不释放这份独立票。才构造固定 schema dict/tuple，无 SeedKey 逃逸。 |
| Capture.drop | 先 trie.drop，再把 steps/seeds/引用清 None，释放私有 O/S 和候选票。carrier 和诊断仍持有已独立付费对象，不声称 live=0。 |
| _equal_strings / _same_key / _template | 每次字符串比较按双边长度 D；四模板固定字段比较先32W/12O，再构造仅三字段 expected tuple，比较后释放。range 只允许原 URIRef N3 边界。无闭包重算。 |
| _union | 两个已有 sorted ordinal tuple 做线性 DP merge，先8*(a+b)+16 W、24*(a+b)+16 D、3*(a+b)+8 O，覆盖 builder/slice/result 并持；保留 len(result)+1 O。 |
| _lookup / _put_key / _reference_key / _lookup_reference / _put_reference / _leaf_id | 所有动态 key 操作经编码和 finite trie，引用 key 也长度编码；每次临时 bytes 消失后释放其 scalar；叶 ID 仅语法检查。 |
| validate_direct_steps | 先 gate 固定 schema/cardinality；六个 trie、groups/leaves/validated 先票。seed_entries 按身份组归并多个 allowed representative，proofLeaves 每身份唯一且完整；steps ordinal 连续、无前向引用、结果唯一且恰好覆盖 rdfs，逐条四模板/depth验证；basis 和 proofLeaves 与 DP ordinal union 双向精确一致。每步 ordinal mask 的全N初始化/扫描都在8N+8dp+16 W、2N+16dp D、2N S下执行。所有派生索引/DP在 finally 清掉后释放。 |
| locate_roots / RootRef | 只定位已经校验 normalized entries；按 target/entry 顺序返回全部 leaf/step/ruleHead refs；没有权限推断、叶发行、reason 或去重掩盖。entries 索引 list slots 和 output list/tuple 并持各先 O，输出8len D；派生索引 finally 删除，返回 tuple 保留 len+1 O。 |

事件固定 12 项：action/domain/count/stage/workBefore/workAfter/scanBefore/scanAfter/objectsBefore/objectsAfter/scalarBefore/scalarAfter。events 不包含输入内容。receipt.events 是当时快照；capture.drop 可以在 receipt 后追加预付 cleanup 记录，所以最终诊断应保存 ledger.events，不能把 receipt.events 当作 GC 后终态。

## 已运行的证据

17—22 是最终源 SHA 上、独立环境的明确完整 env 运行。每项 JSON 保存完整 argv/cwd/gitHead/env/UTC 起止/独占 basetemp/exit/source before-after SHA；stdout/stderr 原始双流和 bytes/SHA 单独保留。env 是 run-clean.py.raw 实际传递的7项 clean environment，不继承秘密环境值。初始环境安装为本树自己的 uv frozen 环境，未借其他树 venv/node_modules。

- `17-clean-capture-budget`：纯 helper 四模板、domain→type depth2、原 ID link、identity aliases/all roots/事件链、capture 四域 exact/−1、duplicate invalid/drop、128 control 边界，通过。
- `18-clean-validator-budget`：validator 四域 exact/−1、foreign key 钩子门、completed reuse 用量不变，通过。
- `19-clean-fee-events`：保留 capture/validator/roots/identity 四个 helper ledger 的全部事件链；stdout 130266 bytes，SHA `cc8807cbc632e9d2864095745d3eea90d81e132e958ce0fb3e9dee9219c5a863`。
- `20-clean-scope`：139 accepted members exact bytes/SHA 全相等；源46459 bytes；51方法、40循环/推导式。
- `21-clean-ruff`、`22-clean-format`：最终文件静态检查和格式检查通过。

final capture helper（含 receipt）实际 W46300/D10371/Opeak13704/Speak37016；validator helper（接收已生成 seed_entries）W198423/D61410/Opeak46467/Speak120320。四域 required exact 成功，required−1 均 DIRECT_STEPS_LIMIT。包含在同一次 helper 创建 identity 的 validator 则 W204014/D64438/Opeak48339/Speak135574；二者计费入口不同，不能混用 required 值。

纯 helper 里的叶 ID 使用固定 fixture 旧公式建立，仅供局部 validator 测试；产品模块不会计算 leaf ID。真实 finite 首插入、同轮 first witness/后轮 duplicate、原 W/C/R/L 不变、schema/wire/whole J/hash、所有旧测试与独立预算审查均由主树集成及独立 agent 验证，不冒作本文件证据。真实 batch closure 的后轮 late-shorter 不可达证明由独立测试作者保留；本 helper duplicate 防御序列不称为真实图证据。

## 首失败和日志局限

最早 `uv sync --frozen --cache-dir /tmp/i05-directsteps-module-uv-cache-20261022` 在 supervisor 建立之前运行，工具历史显示 Python3.12.12、19 locked packages、成功；当时没有保存独立 stdout/stderr 文件或完整环境快照。最早 Ruff check --fix 的静态首失败（E501长行和F841未用局部，共16项）也只存在工具历史合并输出；之后 format 和删除3未用局部修复。本记录保留该缺口，不生成伪原始双流，也不把后续重跑改名为原首失败。01—16 的 supervisor 记录双流，但 env 字段只记录 overlay，不能称完整 inherited environment；17—22 才是完整 clean env。01—16 原文件保持原样。

最后一次 source 修改仅给 carrier 独立 scalar 票（parent 已确认）；其余 API 未改。完整新 J 的 projection/hash 和旧执行入口只由 parent 在六指定共享文件实现；本树无旧产品/测试修改，无 Goal、GUI、e2e、native、HMR、服务、模型、付费和 push。冻结提交后停止源写，供 parent 按 path 逐 Git 采用。
