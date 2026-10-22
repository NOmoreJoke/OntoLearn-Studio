# 作者自查修订记录

本记录保留已发生的设计偏差，不将早期绿测写成全部成本规则已正确。

1. D手算最初为115：F14 +两candidate16 +step32 +index3B×16=48 +COPY2/SCAN2=4 +link1。原事件片段为 `{"id":"three-index-bytes","charges":{"work":48,"scan_copy":6}}`。它把索引的2K扫描记入scan_copy，却漏了合同D:147“所有copy/encode/compare扫描同时计work和scan_copy”的另一维。第一次7个自测methods通过，只证明模型与这组手列事件向量相符；该向量自身遗漏的跨域收费没有被当时测试发现。不是产品/历史actual结果。
2. 自查对照D:139/147后修为121：index部分3×(16traversal+2scan work)=54，2K=6仍入scan_copy，故115+6=121。139417856继续标fixed traversal **子界**，不伪装完整D工作/额外钱包；若后继owner证明16K已经包含2K，须给具体包含关系和新同版映射，而非本窗猜测。hand-vectors、hand-examples与bound-formulas均同步；最终8个methods含新增local-bound检查通过。
3. 初版cache手算草稿使用cap257但逐事件总数269，在首次包含该向量的自测前，按F14+228+2+5+20更正cap269；没有发生该向量测试Fail。它的数学parse5明示为给定子账，非现行parse_value费用。最终差1cap268预付259+10失败。
4. 早期三个命令失败的精确exit字段未保留。后来状态消息将Git128/Python1惯例写得过于确定，正式retained-first-failures改为unknown并保所见combined-output转录，不伪造原双流/exit文件。最终实际验证命令另用subprocess记录argv/双流/returncode，均可读回。
5. root后补纯API参数声明只支持canonical rules=()/disabled=()条件默认。Turtle行新增条件dummy17L，但未将其当前producer接收调用合同或实际capture改成已证，113无条件+1条件分列。

所有这些修订都在首次正式candidate commit之前。未改原T05受审候选、原产品/预算/业务输入；root拥有的首作者not-independent事故原件完整保留且未读内容。新的独立审者应审最终固定Git候选，同时看到本记录中的旧错误与有限覆盖。
