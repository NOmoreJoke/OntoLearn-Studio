# 合同收口与证据口径澄清

本记录是固定读取阶段 `a816c2d018772ce8b172101d9debec787ffa434a` 的纯docs/process后续。原56路径、两条新代码/测试、实现文档、原代码独审、manifest与raw全部保留原Git字节；没有修改产品、测试、依赖、构建、配置、验收或重新运行全套。完整T01 Goal继续，未push/PR/merge。

## 源核验退出状态的严格口径

总控在实际读取a816证据后指出：`60f3c4` 的shell先运行 `npm run verify:sources > /tmp/t01-project-host-verify-sources-01.log 2>&1`，随后另运行Python继承/hash核验。该工具记录exit0严格属于最后Python及整段shell；脚本没有立即捕获npm的inner exit，也没有用`&&`将两命令状态绑定。

因此a816的validation、代码独审及此前回执中若把`60f3c4 exit0`直接归于npm独立退出，须以本记录澄清：**没有独立捕获npm verify:sources退出码，不倒填为0。** 111B原log SHA256 `1439dca3a0fd2dbc3702b336e9accceedc93893d0d65264c69da1aa175c45536` 确实打印“已核对12个归档源文件。”；这支持该源脚本的成功尾输出/完成事实。末尾Python另有逐48 Git/bytes/SHA一致的实际断言，exit0是它的工具终态。不能把两者拼成未记录的npm inner exit。

本澄清保留原raw与原报告，不覆盖历史证据。按根明确要求，不为此重跑无变化产品/check。最终check04是其命令序列的最后命令，有session5551/`70ca9d`的独立终态exit0，1125TS/2841Python通过与44原skip仍据该原件；本澄清不改变其范围或源码身份。

## 创建/resolution合同的独立交付

根明确允许已稳定读取代码先固定交付，合同继续原docs作者独立修订；本后续不把合同当a816采用项，也不将提案说成已实现。

- 初稿：30208B，SHA256 `d2d469acdc401f01fec3269647fcdeefb66dc0ca2ddfbf0717f663508f410675`。
- 初轮独审：10182B，SHA256 `402c0010938b41692d981d2630eac5aa76a3901259a94e1f77118233e3238724`。原文件被报告作者正常续写后，主线从原docs作者全文读取该报告的完整工具输出恢复原字节，实际核同原SHA；不是凭摘要重构。恢复来源为其rollout第2526行、call `call_160f1b9b6ac44940a620ea043cde9e35`、chunk `4b912f`、output UTF-8 offset152，详见原件归档内恢复收据。
- 修稿：39602B，SHA256 `ff725f2c0ee40cbdf61c9c4d27dfea1be3ccd2068df4399878b037976de4a5f3`，逐字复制到相邻实施文档目录。
- 最终独审：14753B，SHA256 `33b74eabb6bdc7c2f129214fd1bbf1b6a5177fc8cd9ab0b782c36371c8b25930`；已全文回读修稿并关闭两P2，报告停止写入。主线核字节与SHA一致。

P2-CR-01原物理库归因：新增原dispatch真实Store/位置能力/实例/generation的私有绑定，与当前许可及原host/Session来源分别核验。逐字复制库不靠migration_id或相同claim误认；丢失/不可重新证明则unknown，只能展示当前许可下真实持久记录。没有新增main持久意图账本，没有虚构I06已交付能力。

P2-CR-02完整读取预算：保留4096 ASCII名称导致完整metadata4178B的实际canonical反例；将来创建必须在首次写前核完整metadata、目录行、工作区、所有有效固定页及全库验证/快照/留存的持久预算相容，不能只验名称自身字节。暂存槽位等运行占用仍保持有限失败。当前读取模块及其限额未改。

旧apply_application遇创建namespace先identity-conflict的未来责任已明确列入job_store；新namespace的精确dispatcher、旧3安全拒绝、全新只读事务、缺旧Job来源unknown等仍是待实施合同。未来最小四产品/两新测试路径并不因为合同成文自动获准修改。

最终合同与报告只做文档格式检查及静态源依据审查，未运行创建/resolution产品或假称真实FS/人类选择验收。初稿、初审、修稿、修后独审和完整原工具记录分别归档；最终身份/成员清单见本次contract manifest/index。下一实现仍等待根对真实依赖、路径和阶段的精确批准。
