# 项目位置能力合同：审查处置

2026-10-21。原I06会话内完成，仅docs。独立首审为 `/root/i06_design_review`；源码静态核对为 `/root/i06_interface_docs`；官方平台补核为 `/root/i06_platform`。三者仅只读，无产品验证；完整结论各按原文保存，不替指定模型审查。

## 固定版本与原件

- 最初30783B草案：offer-before-independent-review.md，SHA256 `e89e110b64c948165edaa7ae5a7c69e2f8df9b54768d638dc5be971e2fc21bee`。
- 独立首审与源码复核实际读到39999B版本：offer-reviewed-r1.md，SHA256 `647ebc71a51cb6b912aaf9a15c96409cc97a21623cf6bed5c3ea4419e8559eba`。写修正时未另存该中间版，随后由修正逆变换恢复，并实算SHA与两位审查agent已报告值完全一致；该保存件未再格式化。
- 修正后交复核的主合同46365B，SHA256 `561ec272c07f0c0f026c9aa17b717b99d3e110e31cb4ee45f0663254e9517443`。最终是否无阻断以独立followup原文为准，不由作者替审查改判。
- inputs.json固定31项Git/操作规则输入；inputs/中保存T01设计全文、961设计及本轮准备指令的原字节。政策78df/e437实际适用，历史ownership由四文件生效登记覆盖。

## 逐项处置

| 来源/问题                                         | 处置与当前合同位置                                                                                                                                                                                                | 必要边界                                                                                    |
| ------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| 独立首审P2：retired一概拒绝会永久阻断同库重开     | §2.1区分private-deny、profile-container、database-managed；DB的released-retained不删记录，仍受transfer保护；§3.2改为拒private/未释放DB，而真正released的精确DB仅凭新可信用途、旧实际释放及重取原生锁/身份再获能力 | 私有永不例外；unsettled/unknown不得重开；不凭同UUID恢复grant；崩溃缺receipt另需受控恢复实证 |
| 独立首审P2：final占位与no-replace publish相冲突   | §3用途表与§3.2统一为authority内最终名预留，OS独占staging文件组，关闭/sync后一次native no-replace发布；final无本方占位，不unlink或replace                                                                          | 应用名预留不阻外部抢占；冲突保留staging/证据，不能当成功                                    |
| 独立建议：多链接闭合不充分                        | §2.1规定同观察边界distinct目录项数等于linkCount且全部受保护；nlink=3只有final/pending两名仍unknown                                                                                                                | 不扫描全盘；外部候选nlink>1继续拒绝                                                         |
| 源码核对：4096/10000误作恢复上限                  | §2事实表改为密文新增写/审计追加阈值；恢复不能据阈值截断；底层目录11024另列                                                                                                                                        | 与配置journal1024上界分开                                                                   |
| 源码核对：局部health Supervisor遗漏               | §5补readEngineHealth的局部Supervisor/finally stop，当前固定desktop未调用                                                                                                                                          | 未来不得绕cohort，无新增调用权                                                              |
| 源码核对：late初始化应为未来风险                  | §5说明当前一次初始化且检查quitting；未来重复初始化缺cohort fence                                                                                                                                                  | 不虚构当前已发生并发覆盖                                                                    |
| 源码核对：加密backend检查时点                     | §5明确factory核main/app-ready，backend于credential store/read检查                                                                                                                                                 | 模型init成功不证明Keychain可用；metadata独立complete不调用凭据                              |
| 平台补核：mac具体发布及发布后耐久                 | §3.2及§4补RENAME_EXCL/NOFOLLOW_ANY、实际卷支持门；发布后目录同步/身份核验、F_FULLFSYNC差异                                                                                                                        | 已发布但sync失败属于耐久未确认，不重新发布或删final；APFS仍未实测                           |
| 平台补核：Windows完整身份/share-delete/原句柄发布 | §4补VolumeSerialNumber+128bit FileId、links/deletepending/reparse；按三种角色冻结share策略，原HANDLE相对RootDirectory no-replace发布                                                                              | 不通过释放fence后path reopen绕sharing；NTFS/ABI/SQLite锁未实测                              |
| 平台补核：取消不等于settled                       | §4和§7增加CancelIoEx当前进程、OVERLAPPED完成通道、main duplicate与child IO分离、同步调用实际返回                                                                                                                  | abort/取消成功/ERROR_NOT_FOUND均不得腾实际槽                                                |

## 静态验证口径

首次文档Prettier check提示主offer格式问题，随后仅格式化新主offer；无产品首跑/测试失败。最终只核新规范文档/JSON、Git范围和固定输入/旧产品字节；快照与agent原文不批量格式化。真实FS、原生VFS/ABI/锁、发布耐久、包、main/UI、目标OS和指定双方审查仍是未执行计划。

下一执行范围须总控逐路径批准。本文不改Goal、共享实现、旧冻结文档、总控state或既有review输入；无push/PR/merge。
