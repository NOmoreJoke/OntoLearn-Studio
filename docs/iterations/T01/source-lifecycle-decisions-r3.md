# T01 来源生命周期选择 r3

已全文读I06固定b1283bce1daf7198fc6b0b62f8b0a6bbffa5a874的T01-owner-response-alignment-r1.md及68dfd71a950bab0cda2e53776c4aa3c5e7819d5c的T03-source-lifecycle-alignment-r1.md；寿命数值另核eabaf4d固定source-snapshot-transport-decision.md第2节。本次明确设计选择，不回写r1/r2历史字节，不批准runtime/公共3-ready。ff98761的内容intern幂等不等于以下上传协议已实现。

## 1. 明确选择与预算

T01选择**精确同块append幂等**，不是I06原“所有重复均拒绝”选项。第一次append只接受当前expected index/offset；原ordinal重复必须匹配原完整begin descriptor、session/project/upload/selection/phase/代次、index/offset/decodedLength/chunkSHA及逐字节内容，返回原ack。不得覆盖、推进两次、增加pin、延长idle/total/sealed寿命；不同内容或任何绑定差异拒绝并终止未接纳upload。ack未知先按原attempt/status对账，不用新attempt/operation重放。请I06据此同步本线设计，不能用cache intern的同hash去重代替实际append校验。

接受I06候选资源约束作为待实件验证的**技术预算**：全main/engine所有窗口项目合计1个实际未终态begin、2个未接纳lease，按声明raw长度预留合计不超过16777216字节；每upload最多一个未结chunk请求。pending、receiving、sealed、admission-unknown、取消/清理未settled都占用，主进程与引擎分别执行，不能靠换页面/broker或逻辑abort清账。已accepted输入转入持久pin计账，但不能因此获得无界存储。

寿命选择：receiving idle 30秒、begin起总传输120秒；seal后未接纳600秒。owner使用单调时钟，精确重复begin/append、status和迟到ack不延寿。新有效进度可重置idle，但总120秒固定；seal只建立新的固定600秒截止，不能不断seal延寿。到期先撤销新消费者/写受理资格，实际消费者停止/清理完成前仍占资源。读取许可与正式写Job pin分开，TTL不提前删除在用字节。

持久source缓存另提**256MiB逻辑encoded载荷预算**，计全部source块/manifest及尚未实际清理的暂存/孤儿，按实际编码字节保守预留，去重只在核真既有成员后结算；accepted/pinned同样计入。超限只能回收已无消费者/pin/必需引用的成员，不能删Job/历史需要的输入；仍不足则拒新来源，不破坏旧项目。该预算不是SQLite文件/WAL物理大小、整体RSS、XLSX展开容量或PRD Q5能力结论，平台实际磁盘不足仍走真实存储错误。此持久值需root/owner接受及实测边界后才可装配，当前模块没有配额/GC，不谎称已落实。

attempt/tombstone提案：每engine session最多256个传输attempt记录（含终态tombstone），记录原descriptor与权威终态，不在同session复用/逐出为不存在；满额拒新begin，健康/既有消费者继续原边界。它与原协议request-id上界独立；不得通过重建对象清空。受控新engine session先fence旧进程/清理和重建来源许可，不能用重启自动恢复旧活lease。

## 2. 同owner权威排序与unknown

main最终实际写帧前同步guard只解决**尚未dispatch**窗口。已dispatch请求与revoke按coordinator单一writer的权威scope版本/确认序号排序：撤销先线性化则写受理事务拒绝；受理先线性化则返回真实accepted Job/operation/pin，后续按正式取消/receipt处理。main本地时间或generation变化不作为远端排序证明。

begin先原子登记attempt/descriptor和配额再异步暂存。尚无uploadId的release按原attempt建立取消tombstone；后到begin不能分配/复活。status not-found本身不能证明请求未发或不会迟到。需要同writer barrier确认截至原请求的处理序及终态，或原进程实际结束/fence与受控清理证明；unknown仍占预留，不补发新begin。

读消费者保护在校验来源与开始读之间由同owner原子取得；它只授权inspection/preview只读计算，不授权正式域写。最终写Job事务同时核source phase/完整内容/选项/表与mapping计划/真实确认/当前scope、原全局operation，建立Job context及durable source pin。release/admit/回收同一writer排序，不能发生“ref验证后、pin前已回收”。接受/提交响应丢失只按原operation/request只读对账，不能改计划或新operation重放。

## 3. 稳定计划与临时接纳身份

稳定内容计划绑定typed source manifestRef/整体SHA/长度、format/encoding/sheet、真实parser完整implementation、tableDigest、mapping定义digest、domain base/必要应用CAS、真实Diff/planHash及其规范版本；不将upload/attempt/lease/TTL或engine session塞进“文件SHA/内容planHash”。实际准备/确认仍单独绑定真实actor、preview及其当时来源上下文，不能凭相同planHash借用确认。

首次受理另核临时AdmissionProof：当时有效engine session、source lifecycle/selection/generation/phase、lease、真实prepare/confirmation和main proof复验依据。权威接受context保留**原**稳定计划及这份实际接纳证据，完整claim指纹绑定两者。此后精确对账读取原context，不以新lease替换原证据；外层新连接session只认证当前调用者/项目读取，不能把旧来源凭据变成新授权。

选择明确规则：未接纳lease过期、被撤销或engine session改变，**同内容重传也必须新预览/新来源proof绑定和新人类确认**；底层内容块可去重，稳定内容planHash可能相同，但新确认/新AdmissionProof不能冒充原请求。若原operation受理仍unknown，先按原operation及原完整请求只读对账并取得同owner barrier/旧scope fence；不得先造新operation重放。确认从未受理且旧请求已不可能迟到受理后，新的明确用户确认才产生新operation。已存在的原全局claim则先认证当前项目权限、比较原完整请求/context，返回原Job/receipt，**不再要求原临时lease今天仍活跃**；不能重算当前CAS、重传来源或安装新lease来完成这个对账。不同原请求同operation继续拒绝。完整字段schema和此分支的跨session fixture由唯一canonical一次落实，各adapter不得自行放宽。

## 4. 必验与仍缺项

同块ack丢失精确重试不重写/不延寿，换任一descriptor/bytes拒；begin取消先后与tombstone/barrier；main未dispatch guard拒发、已dispatch受理/撤销两种权威先后；满1/2/16MiB、30/120/600秒、256attempt、256MiB逻辑预算各边界与清理未settled；去重/重复不绕配额；inspection与preview消费者保护、TTL/release/admit/GC竞争；未接纳lease失效后同内容新预览/新确认，unknown不换operation、已accepted原请求在lease过期/新连接后仍可授权只读对账；engine重启不复活活lease且accepted pin可按原Job恢复；actual CSV/XLSX与真实Store结果/receipt/取消及跨帧完整plan。测试须断言权威序号、真实持久输入和完整库，不凭本地标记。

以上资源值及新source专用quota/expiry错误、严格字段/字符串预算、跨语言tableDigest、typed worker输入/大结果形状仍需统一到唯一canonical并实际实现，原catalog不能借memory/frame/page错误假装精确新含义。小帧按r2在两段begin前明确拒，不悄改块profile；inspection配置换代仍签新phase绑定引用；完整有序表类型仍等待T03真实接口投影。本页给出明确选择，不将未实现机制写成已验收。
