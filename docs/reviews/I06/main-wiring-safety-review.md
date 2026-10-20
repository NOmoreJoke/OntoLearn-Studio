# I06 正式接线阶段内审记录

固定代码9fcba6634d5c16983c36ef671d4ec8e79694b6d6；内部独立只读agent /root/i06_design_review，分增量检查并回传实际SHA，不替指定GLM/MiniMax双审。

## 已修复与实际证据

1. 配置journal原用随机文件名，多个仓库实例可同序号分叉。改为sequenceId唯一原子槽与恢复身份核对；真实两个独立实例停在file-synced barrier后竞争，1成1拒，恢复正确。同实例tail只负责串行，未被冒充跨实例锁。
2. 配置publish最终link后仍可能因目录同步/安全复核失败reject。服务现在任何replace失败立即failed，关闭材料/定向取消请求、移除core配置/授权并返回unavailable/null，不能继续旧内存grant。真实私有文件post-link故障+Store/HTTPS请求凭据等待反例均运行：磁盘有新endpoint/missing binding，旧grant不能发送，receiver零请求。
3. 定时status刷新原会将用户明确新建空串选项改为第一已有配置，清空草稿。null初始、空串显式新建已分离，独立静态复核关闭；实际UI跨轮询行为待平台运行。
4. 根复核补充凭据输入需绑定配置版本：独立password form以configurationId/version为key；轮询接收新endpoint/version时旧input卸载清空，不把旧key输入配上新的expectedVersion。secret不进入React state、不回显，main仍校验并发版本；独立静态复核关闭，实际UI待平台。
5. 配置journal CAS仅证明不分叉，不证明多活owner授权同步；index实际申请同profile单实例锁，未持锁whenReady不启动Store/model/window，也不聚焦/转发已有实例。静态已核对，真实进程行为待容器运行。
6. transport原替换解码可将小于1MiB的坏UTF8字节膨胀成大于1MiB公开文本。现累计原bytes限额后一次fatal UTF8解码；新增malformed与跨chunk中文两项实际本地receiver反例通过。上游正文/异常不进入错误或审计。

窗口恢复只读status/outcome，不start/confirm；终态cache按ID/state更新、按当前ledger淘汰，失context清空。初始化失败独立于本地窗口/任务，退出先取消模型再收尾私有仓库并在5秒边界后停引擎，不能声称可取消同步OS提示或超时前所有IO均完成。

## 证据边界

r9完整check998TS/1052Python及source12已在最终代码上通过；46专属Store/字段/service/config项含真实approved Store/coordinator/test.read、私有密文/配置/审计文件与经证书校验的HTTPSreceiver。headless服务中safeStorage是明确double，TLS trust只在测试worker内加入合成CA；没有操作Mac系统证书/Keychain/GUI。合成receiver完整body已单独保存，无headers；它不充当真实Electron/preload/UI/native通过。

main有限field policy只由既有可信fixture path+env且unpackaged选择固定literal，implementation锁摘要由main读本应用uv.lock，正常product models=[]；tag仅校验shape，不由结果自选权限。I05尚未批准的新版本/候选未采纳。读→send窗口和所选不可变版本按实际展示，不引入live-current lease承诺。

Linux平台在独立worktree从9fc正常合入后构建/运行；完整S3、可用导出事实、适用I05批准merge联验、指定双方全新同候选审查及PR/CI/远端合并仍待完成。
