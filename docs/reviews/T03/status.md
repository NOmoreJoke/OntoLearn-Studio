# T03 数据映射状态

2026-10-21（Asia/Shanghai）。Owner：功能开发聊天 `01a15bcd-f838-75a2-b2c3-692915cc91c3`；原Goal active。

## 当前结论

私有映射服务/受控页面、三项项目解析依赖与实际应用目录包CLI验证完成；正式业务接线、同候选指定双新外审、push/PR/CI/合并及父模块完整验收尚未完成。当前请求总控登记可独立合并T03-S1范围，不以该子范围关闭FR-300–304、D/G/11–12或跨模块验收。

## 固定身份与文件责任

- 工作树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-mapping`；分支 `feature/weekly-t03-mapping`；批准base及当前origin/develop均为 `5f910b52c69d86a1076b2032e5d3c63e715947f3`。
- 上一恢复提交 `438c4ba4dd6848cff8d3c25332cd583421c6a8ec`，随后仅status证据提交 `33d7440b36be0f7adaeee8d5fa16c255576ce2d8`；本轮新实现/测试/包证据已保存候选 `0ad7e0a75cc4583918b057885631934c0a9bd859`；旧通过范围不冒用于新候选指定外审。
- 保护AGENTS当前SHA `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759` 已实查，仍未暂存，不进入产品提交。
- 原独占mapping/renderer mapping/test_mapping_*.py/t03-*.test.ts/fixtures mapping/docs T03全部保留；新增唯一责任仅四文件 `packages/engine/pyproject.toml`、`uv.lock`、`scripts/build-engine.mjs`、`packages/engine/entrypoint.py`。
- 四文件交接已由原I05实际释放、本线逐项接受/root双树hash核验/独立复核及root登记生效。权威根 `I05-T03-build-ownership-handoff.md`，独立复核SHA `072dff2749fb32eb6852109761b73087e696ae2b748a949c19e7a10c4225f0cd`。本树旧check终态后顺序改写；未采用I05未批源码/锁/C2，未改I05旧树。CI/resources/verify脚本/其他现存测试/公共14文件/root tasks/state均未改。

## 实现与实际验证

- 真实CSV/XLSX解析、单/复合字符串身份001、跨表引用、明确转换、完整RDF/源行/owner/managed计划、增删改/身份变化、人工漂移/墓碑/其他来源冲突和旧预览重算；无第二Store或写入口。
- 私有三步受控页面：分页/冲突返回路径/显式确认，未接入回调时禁用操作；项目/revision/选择/sheet/encoding/generation/draft绑定，取消迟到不复活旧预览。8项状态与SSR转义证据保留，没有声称浏览器交互/视觉或业务接线通过。
- 新增9项实际取消/真实os._exit恢复测试，覆盖提交前/中整批回滚、提交后标记对账、精确六字段来源所有权、mapping定义/version/全部规则/sourceHash/sheet、mappingState和旧历史不变；独立复核通过，不替代正式I04 job/bridge/UI。
- 项目三精确依赖 openpyxl3.1.5/et-xmlfile2.0.0/defusedxml0.7.1已声明/唯一uv.lock/frozen安装。仅新增3包、其余17包记录逐字不变，实际发行SHA和许可证文件SHA与候选匹配。此为当前候选，尚未通过指定外审或合并批准。
- 最新 `npm run check` 实际exit0：638 TS tests、1107 Python tests全部通过零skip；日志 `check-project-xlsx-first.txt`。mapping专项55项零skip，覆盖正常/-O/拒绝额外参数/固定错误；旧overlay的4skip现已由真实项目依赖关闭。
- 最新 `npm run package:dir` 实际exit0；直接运行应用内 `release/mac-arm64/OntoLearn Studio.app/Contents/Resources/engine/ontolearn-engine --mapping-probe`，11组固定真实解析正反例与源码结果完全相同；参数拒绝exit2，包内唯一锁及全部三库许可证逐SHA相符。既有storage-probe同包实际exit0，精确结果A01/18三元组。
- 当前包为macOS27 arm64本机未签名目录包CLI；未启动Electron/GUI，不是macOS15/Windows11目标干净设备、签名安装、生产或发布证明。引擎SHA `5f40a5654350eec58db51000055e7157b452f6c9ca3294a47b646c7831aea482`，唯一锁SHA `9f5b6d2b93d994a3e4f8a46ce5cccae99d4e024ea7531ab62dd8e85d6aa1152e`，目录内容manifest实际文件SHA `98e2d8478d366d2463681d9232ea56353039a951043f90a911743fd230afc860`（去末尾换行后的规范内容SHA `9271f6c7b172f6591ec31434cced70ed68b0145c14bc1dc8ed8d08a1f1e28b5c`另列）。完整manifest保留build/T03-evidence避免大原件入库；摘要 `product-package-identity.json`，可复现脚本 `../../iterations/T03/verify-packaged-probe.py`。
- 独立agent `/root/t03_service_review` 对本轮完整代码/依赖/测试明确内审通过；先前5项问题及恢复证据补强均已关闭。交接旧文案已同步；包内证据脚本已独立复核，670项包内容逐一匹配；发现一处manifest末尾LF的文件hash/规范内容hash标注差异后已明确分列，并获独立材料复核明确关闭，未改变包或重复构建。不替代指定ZCode/MiniMax双新审。
- T09获批固定873 manifest/17项已验，本线equipment.csv字节与获批CSV相同；只采用固定输入，不读其变化HEAD服务、不用expected填Store。所有首失败原件保留。

## 剩余与下一交付

正式受信文件/sheet选择、公共契约/错误/统一分页/bridge/App仍须T00/I06安全交接；T01正式确认/原子Store.commit/operation取消对账、T02真实定义校验、T08草稿增强/T10迁移及原完整目标平台/父功能验收保留。具体请求见 `../../iterations/T03/integration-request.md`，依赖/构建四文件已按新责任完成，不再等待旧owner改写。

独立服务子范围申请已实际发给总控。正式最终候选须更新实际批准develop/依赖并必要联验，冻结base/head；同版ZCode GLM-5.3最高、MiniMax M3.1-Flash/xhigh各新完整任务实际通过/读回/全意见处置后才push/PR，实际CI通过后正常合并并核远端。外审应用仍按总控预约，不自行操作用户桌面。

## 操作与Goal审计

前一回合产生实现/证据提交，本回合新增恢复证据、完成有效四文件交接、项目依赖/包内实测，均为progress，不是状态空转。原Goal/分支/归档输入不重建。

第九节与无桌面全文已接收/透传，已有权益恢复仅官方/唯一负责人；Codex reset逐次本人确认/阈值/幂等。ZCode默认yolo、MiniMax默认bypassPermissions新政策已接收/透传，每任务仍读回模式且仅只读。无新增付费、外发、密钥读取、GUI/e2e/native/HMR权限；本轮均未执行。纯操作文档补充不触发无变化重验，产品/依赖/验收变化按新候选重验和原双审。
