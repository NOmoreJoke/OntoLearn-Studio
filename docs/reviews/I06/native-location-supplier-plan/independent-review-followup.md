# Native 位置供方方案：定点独立回读

2026-10-21。**D1/D2均关闭；最终方案静态审查无新增阻断。** 本次只核首审后的实际差异、表格列数、输入追加及报告格式保全，不重做产品/native验证，也不改变首审中的生产前置。

## 1. 最终受审身份

| 对象                                                            | bytes | SHA256                                                             |
| --------------------------------------------------------------- | ----: | ------------------------------------------------------------------ |
| 最终主稿 `docs/iterations/I06/native-location-supplier-plan.md` | 49472 | `34c4307e42c349b5d4fc40d0960655454727570eb565c4fc1c3d521663c57624` |
| 首审主稿 snapshot `main-plan-review-input.md`                   | 48256 | `ff21c9f0c10d2f40e48d5f93dbccdd880523ec03327bd687eb3c997545afb518` |
| 最终 `inputs.json`                                              | 19875 | `54a32efe8d54ef2b0b2b0418f2abc6b63a6f3f5fd9dba86d698645d3e1538955` |
| 首审 inputs 原件 `inputs-review-input.json`                     | 19602 | `0d31621bbde2fbf716fb06950ec842f3d554d529cb53ae1c16e83d463dd2b5eb` |
| 平台 canonical `platform-static.md`                             | 44109 | `65a4e5fef210c6efa9f05fe33bef0f81fdf93a66063f5d414f10526b83af017c` |
| 平台首审原件 `platform-static.original.txt`                     | 45555 | `fd09ac310c543a8c85d29efb13b1155a4589e5cdf162e013a49f357e5c03d882` |
| 本人首审原件 `independent-review-r1.original.txt`               | 12009 | `a6d67cb636a3183eced3cfb64383823bd49d038832252fc75cb8e0a19135092c` |
| 本人首审 canonical `independent-review-r1.md`                   | 13599 | `668640d8c9a6d302e80f4849496765bb610518a1a08abc6800280e34c5ecbf64` |

以上均由本人本次实际读取字节并实算。先以exclusive create保全本人12009B首审原件，后仅对canonical运行指定Prettier格式化；首审意见和当时结论未改。原件绑定首审ff21，不能将其改称最终34c4的首次审查。

## 2. D1/D2处置

**D1关闭。** 主稿§3“独占建立”行已重建四列，bitwise pipe转义，macOS原语、Windows FILE_CREATE及冲突拒绝分别在正确单元格。本人用按连续表格段计数、仅将未转义pipe当分隔符的静态扫描：最终主稿95个表格行、平台canonical65个表格行，均0列数错配。该检查证明本次文本列数闭合，不声称已经GUI渲染或验证任何OS原语。

平台首审与canonical去转义pipe、格式代码反引号、空白和表格横线长度后，按行文本相同。原fd09仍独立保存，没有把平台“自有CPython连接适配优先”改成主稿的同库重建选择；路线差异和未实施边界仍原样保留。

**D2关闭。** 最终§9 N0明确六件产品（ABI/core/两OS/Node binding/main私有owner）、三件测试（core test/child probe/TS owner test）和三件T03新构建文件。与§8精确路径对应；Python binding、capability VFS、SQLite patch、VFS Python测试及capability-Python构建明确排除，T01共享路径亦不在N0。若需T03既有配置delta，仍先列精确路径交根，不由本名单自动获权。SQLite/用户目录/生产bootstrap/持久B-R继续不在N0，N0不自动进入N1。

## 3. 其余实际差异与来源

本人完整比较ff21 snapshot到34c4主稿，除D1/D2外只见两类补正：

- 将根审计SHA从前缀补为完整值，与原inputs及新保全的17048B `root-integration-audit.txt`相符；准备指令 `authorization.txt` 5447B/15d40亦实际相符。
- 新增held对象ACL读取：macOS候选acl_get_fd_np、Windows GetSecurityInfo；未知规则/解析错误拒绝，不按path重开。明确ACL为快照、不防并发变化，目标macOS15未实测，精确策略仍待安装/principal来源冻结。该文字与首审已读SQLite补充中的官方接口依据一致，没有新增持续围栏或生产授权主张。

inputs结构比对只新增 `bmRootClosureDocsRef` 和 `bmRootClosureReceipt`。本人对固定6240748d83d2251664b3fe1e9808f5f67adeec41的root-closure.md静态Git回读，3077B/SHA256 `ab10ea451b362cb9f655aacd52e692ad8c23dd3b3086f45239267af5e119e443`相符；没有新增运行结论、采用其他产品或覆盖BM原manifest。旧inputs原件0d316保全。

## 4. 实际验证与边界

本次cwd固定 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-real-private-metadata`。静态Python stdlib执行bytes/SHA、diff、JSON结构比对和表格扫描；固定Git show仅回读追加的closure原件，均正常exit0。没有import产品/sqlite3或运行产品、测试、构建、native实验、GUI、用户目录/凭据操作，也没有修改主稿、平台/T01报告、BM64或AGENTS。

本人报告的格式动作仅使用本树已有 `node_modules/.bin/prettier --ignore-path /dev/null`：首审canonical执行write，新增followup随后执行write，两报告随后显式check；实际exit结果在交付回执单列，不将其当产品检查。本人写入集合仅获准的首审原件保全、首审canonical格式化与本followup。

最终结论限于49472B/34c4静态设计：**D1/D2闭合，无新增P1/P2。** 同一SQLite实际image/完整OS后端补丁与trace、持续namespace/源名围栏、main死后oldchild恢复、fresh历史与Windows/两目标OS耐久仍是具名生产前置。所有精确writer/构建/平台窗口仍待根批准；本审查不替指定双模型同版外审、不证明N0/N1/N2或父I06通过。
