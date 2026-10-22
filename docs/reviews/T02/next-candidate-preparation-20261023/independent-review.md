# C/K/I06差分及四P3准备：独立静态审查

2026-10-23。固定 `ba2837fb7909cbb54cc983f58498effe1c3bd582`：**通过，未发现实质问题；仅为合同差分和下一候选准备的文档结论。** 未授T02实施、供方采用或typed Preview/Job/undo运行，四P3也没有被本报告记为已修。

## 固定身份与实际读取

全文读取本prefix两件：

| 文件 | bytes | SHA256 |
| --- | ---: | --- |
| deltas.md | 8760 | 58d23919f1ab6906f1a2ab413e707bc6e860b992206fa04c5b7b83afc0c6338c |
| delivery-manifest.json | 3353 | 23910f2b8a79df7fccc9de3247bad7cac9ffe5a041e6382bdebe13540472c62c |

manifest自排除正确，所列deltas字节/SHA与固定Git匹配。836c53c→ba2837的路径差异只有这两件docs；限定prefix的 `git diff --check` 实际exit0。这是Git空白检查，不是产品验证或独立Prettier结论。

全文读取manifest列的三份根材料，bytes/SHA逐项匹配：

- T01 helper实施票2217B／`7c4dfde3840cdd52b3f02d1f9abbcac0f357b57b3e76009d58819ee3a9a9e8a5`；
- 37bd reception3153B／`017b308c4e1e6d288ce455e4ea254a77c0e8fbbb066634f44e794d5156396906`；
- 根独审5854B／`633a378cb354a79742d9b6df822e7ed8a1b5208cf86288521f5c1d2eab51da86`。

根材料确证37bd限量正式接收并路由T01/I06；836收敛已接收，唯一T01获5f基线、新独立树、两纯helper文件票。票不向T02转授，不中断C1 native优先窗口，也不解物理HOLD。旧文当时pending仍留历史；本新记录表达新状态准确。

只核自有C5四文件的声明身份及当前字节相同：service.py、__init__.py、OntologyPage.tsx、view-model.ts。语义只读必要切片和限定名称查询：service100–153、208–232；__init__导出表；Page1–124与graph相关渲染片段；view-model20–110。未读取任何新T01/I06源码/helper，沿此前已读f20七docs的设计知识，不重新打开七大稿、36材料或旧闭包。受保护AGENTS仍15147B／de15声明哈希。

## 差分结论

1. **C bootstrap及深层预算没有放宽。** 可信owner/连接绑定与bootstrap policy先于本次首读/decode/复制/物化，开库先读不能事后追认；未知caller事务不进入也不回滚。调用库存含C5校验/RDF/bind/Preview/digest副本、原预演/envelope、全部页/历史、confirm/claim/commit/发布，执行前预扣、失败累计、真实释放ACK。cleanup和terminal独立封存，不因业务预算耗尽绕ownership侧写；真实I/O保首因与实际持久事实，不保证必能close/terminal。仍待真实同版调用图、预算合同与供方pin，不是已有meter证明。
2. **写会话、历史查询、新undo分层正确。** 原写生命周期跨页/确认/排队/首次commit保持；精确已受理operation重试只历史核真返回原Job，新claim/首次commit仍验current。重开查询用当前受信查询预算，新undo为新操作/预算，TTL不能清零spent；结束写会话不形成永久免费历史查询。释放/状态接口交真实issuer固定，没有新造费用authority。
3. **K是内部共同冻结前置。** 真实entityMetadata before/after、profile/version及proof材料须逐项区分仅私有envelope或跨strict参数/响应；不向旧v1追加可选字段冒新版本。K与M1/S2同版冻结、旧合法值/默认v2保持、TS/Python同判及实际必要path delta明确。renderer不能发行成本票/proof或把费用状态塞ontology value；内部K未被当公开RPC/产品host启用。
4. **I06六动作槽齐全且没有抢权。** 源/预览、全Diff页、显式确认、Job/取消、丢响应对账、undo，均消费T01真实authority；槽名不是新wire方法。包含project/session/revision/连接代次与request generation、草稿晚返、完整页链/UTF-8/重复拼段与合法重试、旧点击/恢复不自动签确认、queued不等成功、取消不篡已提交成功、unknown不换operation重放。真人动作证据与机制fixture分开，不发行“真人token”。具名DTO/方法、最小逐路径delta和新pin仍明确待回单，没有宽App重写或第二提交队列/authority。

## 四P3的源码定位与后继边界

- **digest最小私有化：** C5 service105为裸snapshot_digest，限定名称查询只有该定义及137/225两调用。137前有require_current的validate(current):136；225前有change_preview的validate(snapshot):152，且candidate也在215校验。__init__.__all__原本未导出digest。建议私有重命名并仅改两内部调用、adapter只走有校验公开入口/require_current，与实际结构吻合；没有误称私有命名等于输入校验或来源授权。若增加validate/meter须另列成本，合法摘要/Unicode语义保持。未要求镜像名称测试合理，真实adapter仍须结合新供方验证。
- **localGraph门控/memo：** Page105当前直接计算localGraph(view,selected,12)，tree已有104行useMemo；graph JSX265–290仅在graph页签显示。view-model64–79显示计算读取view.triples、focus与limit，含排序、截断与nodes/edges/total/truncated。拟新增memo的hook无条件、callback按tab门控、依赖覆盖完整图输入、JSX非空守卫，方向正确。view引用可作依赖的条件是I06不可变快照变化时必换新引用；合同未满足先修输入，不能依赖revision或selected单独缓存旧图。计划保留既有图语义及新候选回归，未量化性能或用21合成callback冒App/真人。
- **深链Set：** view-model27–60确有children索引、visited及每步ancestor集合复制。保持非阻断观察、不做无依据优化或自造Q5阈值，与已接受分流一致，没有声称整树线性或未测提升。
- **历史指针：** 旧delivery/stage/审查输入保持原件，下一完整候选包另给当前product/process索引，不将新记录补状态说成旧文已修。

四P3中前两项仍只是最小后继delta；实际新树/base/C5逐路径采用、两旧路径及必要专测权限待根固定。完整同版非空实际供方未供前不运行typed Preview/Job/undo；helper合法字段不能替真实M/provenance，identifier不派生，RDFS不变数据值保存门。完整CRUD/Turtle/T08/T10未被统一前置，也未从父验收删除。新候选独审、双方指定新审、CI/正常合并/远端发布与父Goal边界保留。

## 操作与未验边界

实际仅只读Git、文本、stdlib JSON/hash/字节核对和限定docs空白检查。最初按笼统“manifest”尝试读取manifest.json，Git报不存在；随后限定prefix清单定位delivery-manifest.json并成功读取，未写入任何对象，不属产品失败。

未执行产品/import/测试/探针/SQL/DB/JobStore/native/GUI/模型，未读取新供方源码或重新审36/34/130/825项。只新增本独立报告，未改原稿、源码、根控制、旧输入或Goal，未提交。本Pass不证明预算/事务/adapter/graph优化已实现，不替实际供方、后继运行或父功能验收。
