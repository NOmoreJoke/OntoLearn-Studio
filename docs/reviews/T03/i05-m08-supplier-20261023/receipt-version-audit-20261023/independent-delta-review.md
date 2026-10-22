# M08 receipt 版本差异独立补审

结论：本次差异核验通过。交付 receipt 相对原独审实际覆盖的 receipt，只新增 `/supplementalDeclaredLicenseAudit/scriptIdentity` 与 `/supplementalDeclaredLicenseAudit/versionBoundary` 两字段；新增事实与实际 helper、首审计及补充审计边界吻合。产品与旧工件未变。原独审未覆盖这两个追加字段，本报告只对该差异补审，不回填原报告、不将其改称对交付版 receipt 的完整覆盖，也不补签任何运行通过结论。

## 版本身份与差异

| 新工件                               | bytes | SHA-256                                                          |
| ------------------------------------ | ----: | ---------------------------------------------------------------- |
| validation-receipt-reviewed-v1.json  | 17783 | fc249e62f858cb26ba58bb73428a6d2c546b56ab4deed904ab120b793be46746 |
| validation-receipt-delivered-v2.json | 18209 | eaf60afb8f95794d45c77fb2ba90da19de5c95505d45727816648d40b1153d7b |
| added-fields.json                    |   417 | dffe97a376362c49da7edbcd25cbf0515bab0d5bde67e9791f7ac31563e9ef34 |
| owner-delta-record.json              |  4122 | 9649df0c9be477c8739d600fb617f1509bbf2a93e47e9f8035ce4b7b8ab593a6 |

独立解析并递归比较两个 receipt，JSON 差异恰为上述两次新增，无原字段删除、修改或数组差异；新增值与 added-fields.json、owner 记录逐值相同。delivered-v2 副本与当前原交付 receipt 逐字节一致，净增加 426B。

独立在内存中从 delivered-v2 删除两字段，使用项目已安装 Prettier 和实际配置（printWidth 100、JSON parser）序列化，结果精确等于 reviewed-v1 的 17783B/fc249 身份。这证明可逆恢复的字节一致性；reviewed-v1 是此次恢复生成的已审版本副本，不是当时留下的原始备份，不据此倒填创建时间。

## 两个追加字段的实际含义

`scriptIdentity` 指向 `docs/reviews/T03/i05-m08-supplier-20261023/audit-packaged-supplier.py`，实际为 5293B，SHA `37bed088e4d5e4569804f50b90863db705d8cba9ca9c04832dbd2ab477f91781`，与新增字段完全一致。该 helper 的 metadata License-File 显式解析、安装路径内约束及 source/package 字节比较已在原终审覆盖；本次新增的是 receipt 中的身份记录，不是新增 helper 行为或产品改动。

`versionBoundary` 正确说明：当前 helper 加入逐项声明附件核验发生于首 17 审计之后；首结果仍是按 LICENSE/COPYING 前缀统计的十份文件，不能改写为十一份。独立重数保留的首审计与 v2 JSON，分别为 10 与 11；新增项为 html5rdf 的 AUTHORS.rst。实际源/包附件与最终 helper 曾在原独审中核验，本次字段补审未重新执行 helper，也不冒充对首审计过程的追溯扩展。

## 来源与旧工件保持

按 owner 给出的 source event ID 核对实际会话记录：`call_5c1267d04da34ac5a597062e94e4fd69` 为 custom_tool_call，时间 `2026-10-22T18:00:37.524Z`，即本地 `2026-10-23T02:00:37.524+08:00`；输入 1507B、SHA `0d877f0e47462e4d5574fbc2243f8d345eb646f42c13c5b91ca5fcf60ac1a0cd` 与 owner 记录吻合。其 M08 命令确为追加这两个字段并格式化 receipt。对应正式 CommandExecution `exec-ccbdb0a5-997a-46fa-a057-62c039e7e6be` 记录可定位。owner 记录已承认复核后追加、格式化原独审时未刷新 receipt 身份、冻结前未核齐的原因。工具事件时间与文件 birth/mtime、提交时间分别保留，不混作同一种时间证据。

原独审的表格仍明确引用 17783B/fc249 receipt；后来仅格式化原报告，不会使其覆盖扩展至追加字段。本次没有改动以下三份旧工件，独立与提交 `7abab04b223b0c6ca9c290b5b6bd8a702971d2e9` 的对应 Git blob 逐字节比对通过：

| 旧工件                  | bytes | SHA-256                                                          |
| ----------------------- | ----: | ---------------------------------------------------------------- |
| validation-receipt.json | 18209 | eaf60afb8f95794d45c77fb2ba90da19de5c95505d45727816648d40b1153d7b |
| independent-review.md   |  9013 | 917a1aba25a400a61f7ec8eb233dc45a5f199db5d4bfcd0531628be1a926ba23 |
| final-manifest.json     |  2478 | 6898ea4ad482d7ee3b395c136edde615ca57988f1165bb03fa9d52819921c9a0 |

当前 HEAD 为上述 7abab；产品目录、scripts 和 uv.lock 相对 `4e752177f3e350d0be94ed063aca2e866dbf7970` 无差异，工作区无产品改动或暂存改动。既有 AGENTS 修改仍为受保护的 15147B/SHA `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`；本次未修改。旧目录已跟踪工件无工作区差异，新记录限定在独占 receipt-version-audit-20261023 子目录。

## 本次覆盖边界

仅进行只读 JSON/字节/哈希/Git 和指定来源记录核验，外加内存格式恢复；唯一新写是本报告及其格式化。未安装、未构建、未执行 helper/engine/pytest/GUI/parity，未覆盖原独审。原三路径有限通过、整体 check 与八项 pytest 失败、B1 独立 exit UNKNOWN、frozen import/CLI parity 未建立等原边界全部保持。新增字段不改变运行事实、输入/预期或既有门禁。
