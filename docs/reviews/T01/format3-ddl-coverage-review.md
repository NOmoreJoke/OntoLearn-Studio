# Store3 逐DDL覆盖补齐

总控固定4858cf1审计指出：原合同“每实际DDL四类故障”超过原用例覆盖。该候选及原始8log归档保留原样，不以改措辞降低F3-02承诺。

本增量仅向显式3迁移发出旧domain逐SCHEMA语句、v2每CREATE/各trigger/DROP/RENAME及migration_log回填的精确即时hook；SQL、顺序和外层事务不变，默认2不发新增hook。可选retirement补表从单OSError反例补成RuntimeError/KeyboardInterrupt/OSError/真实子进程os._exit四种。

新增定向172 passed、526 deselected；每次都真实命中指定故障，完整源库与backup逻辑摘要相等、原格式不变、lease释放。不重跑未变的旧大矩阵。SQLite trace独立按源0/1/2/1缺可选表观察实际53/29/21/30条DDL，逐条与即时hook及SQL hash一致；精确映射见evidence/format3-ddl-coverage.json。21条app DDL原四类矩阵不变，旧domain逐条缺口现已补齐。

独立store_interface_audit实际另跑172 passed/526 deselected、重建trace逐项匹配，ruff/格式/diff通过，明确通过此小增量。此证据只补齐实际范围；4858cf1的630TS/1699Python不冒称覆盖新增Job层/本新源码，后续完整基础候选仍需新全仓/包内/双审等。

原独立26/16/33/2探针和WIP失败工具原文现在单独封存于evidence/format3-independent-tool-records.tar.gz，SHA c7db39605609c08a3cb5a4fd18213c5ac739ce5e54e3cbbce3f24ee18c986239；manifest逐原session路径/行/byte offset/原字节hash，可核捕获prefix，3成员重读。仅抽相关tool-call/output JSONL原行，不含session_meta、用户对话或其他chat；不声称全部调试事件归档，更不声称原8logtar已包含它们。
