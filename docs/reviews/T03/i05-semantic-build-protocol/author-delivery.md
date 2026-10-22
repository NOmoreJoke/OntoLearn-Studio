# D0 作者交付与有限自检说明

完整草案已写入唯一授权的两前缀；不stage、不commit，不写别树。原T03尚待全文读并给owner结论，实际candidate由原owner提交后另派fresh独审。此稿/自检不是提交后独审，也不是root对实际composition批准。

交付包括完整 build provenance v2、immutable build receipt v2、独立runtime validation receipt v1、完整未批准profile、主协议/consumer合同、逐显式property派生责任索引和exact安全码表、完整synthetic triplet及有限valid/invalid variants、可读纯文档自检源码。字段索引是schema派生检索表，不能替代三schema或完整数据全文读取。所有新文件的最终bytes/SHA在draft-manifest外报，该清单排除自身；清单本身身份另回报，不写未来commit。

## 实际阅读

全文读当前AGENTS、总控D0 window和limited root closure；全文读base bba31be固定adoption、owner-acceptance、提交后independent-owner-adoption-review及owner-disposition；全文读原6ba273a offer主文、profile和两schema的所有字段和值。初次合并输出有截断，adoption后段/owner acceptance再有界补读；大schema改从完整Git JSON buffer按全部properties、全部defs以及build/distribution完整结构补读，没有把一次被截断输出当全文。完整输入身份与读范围在input-identities。

固定47件offer与12件adoption逐件取普通Git对象记bytes/SHA；47的内容未全部再审，除上述四完整输入以外仅身份记账。12 adoption current=base固定Git逐字节同；四writer同base，AGENTS保护M保留。106原sources、43guard、33路径、417原有scope的历史审结沿用已读adoption/独审/root closure，不冒本人再次完整源码/新oracle审计。T05当前口径仅用root closure：实现限定收件、allocation delta另审。

## 实际验证与第一原件

执行新写 `document-selfcheck.py`，只import Python标准库并读取本两文档前缀的JSON；未读/执行产品或旧prepared脚本。它提供本次有限关键词形状断言、required/additionalProperties、局部refs/pattern、根/索引/固定集合/有限关系与依赖图检查。**不是命名JSONSchema2020-12引擎，不是标准完整性测试，也不证明协议所有真实证据约束。** 本轮没有命名获准的离线引擎，不探环境、不安装、不网络，不借产品venv。保每次真实stdout/stderr，first/second/third为形成过程的通过记录，final对应最终例集；不将后来例子回称首轮已验证。

synthetic-design-cases标明synthetic design data；valid仅指给定有限结构/关系断言。包、toolchain、安装、运行、批准、实际CodeType/co_consts、raw archive解码、真实license、真实417等均没有实例或观察。RECORD原字节拼接/摘要和synthetic provenance/build-receipt序列化hash只用于文档算术，不是实际build见证。compared=false valid variant用于说明比较发生不等于matched。

首次工具路径失败原件为formatter-path-first-failure.json：worktree-local `node_modules/.bin/prettier` 不存在。随后由原T03给出既有Prettier3.9.10精确路径，使用该既有formatter；未跑版本/能力探针、未安装。formatter-write-result保首次实际格式写结果，最终formatter-check/whitespace结果按validation-record记录。没有selfcheck断言失败被覆盖；新增反例/字段后重新运行是新改动对应验证。

## 边界

未执行产品/probe/builder/spec/reader/helper/局部函数、旧offer staticverify/generator、产品fixture模拟、pytest、业务compile/pycompile、archive解码、安装、环境/版本能力探针、网络/DB/native/GUI。未读旧binary/toolpayload/SDK/witness，不借R7/native票。没有push/PR/merge/新Goal/用户chat。静态/运行/打包/生产证据分开：本稿只有普通文件/Git与stdlib有限文档检查和已有Prettier，后三类全部未做。

旧offer47/adoption12全字节冻结；schema原有canonical23/bootstrap/四函数/八dist/METADATA/RECORD/extras/markers/全平台artifacts/许可/runtime/Python/code/全部原receipt字段保留，必要改变逐项写在protocol的A1–A4/N01；原v1直接实施仍needs-change。descriptor批准字段仍null/空，executionAuthorization=false。D1/D2/D3/E0以后、原完整417/独立oracle、B1/parent/S1/SQLite损坏HOLD/wholeH/正式Job/selected及指定双方审查/CI/两OS/真人/develop保持原门。
