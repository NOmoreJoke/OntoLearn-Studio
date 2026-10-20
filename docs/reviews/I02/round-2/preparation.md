# Round 2 准备记录（尚未冻结/未开始外部任务）

Round 1 candidate2cc03da双审通过历史保留。PR#3 head为caa0847，CI未全通过，门禁关闭，未合并。没有push本轮未审修订。

Windows：原生驱动错误复用Playwright shell launcher的spawnfile；锁定Playwright发行源码确有Windows shell=true。改从运行main读取process.execPath，保留显式packaged executable优先；本机build/packaged已运行通过，Windows待远端实测，不把推断写成已复现的exe值。

诊断：native驱动保存实际executable/args/exitCode与最多65536字符的stdout/stderr；从exit转为close后汇总，保留45秒上限与finally清理。新增测试真实模拟exit后、close前末尾输出，首次测试暴露一个旧exit监听未替换，修正后15TS全部通过，原失败日志保留。C1关键阶段有日志、清理前保存已有证据；CI Quality启用pw:browser及I02_EVIDENCE，不关闭sandbox、不跳过断言、不放宽超时。

Linux：attempt1 runner自身磁盘耗尽；单job重跑后得到实际C1 90s超时+worker cleanup30s超时、后续desktop首窗closed。日志保留linux-attempt-2.txt。当前不能确认卡点或根因。artifact12232567095(13KB)的Azure下载TLS EOF，gh/curl以及直接连接均失败；GitHub连接器404，未扩大权限/关闭TLS。仅记录下载限制，不据此认定仓库/报告不存在。

当前产品apps源码/配置、依赖与协议相对2cc03da无变化；更正design/acceptance/commands的整体stub边界与same-build语义。历史真实native Run2仍关联同一产品源码（全部apps字节相同），不把历史截图说成本轮新拍。任何实现/测试/配置/验收修改均新候选双模型新任务，不沿用旧通过。

本机现有Docker用于临时Linux arm64诊断（Node官方镜像node:24-bookworm、Debian图形依赖、临时git归档+测试覆盖）。不是GitHub Ubuntu x64等价环境；结果仅定位线索，不替代CI或生产隔离证明。自有container名ontolearn-i02-linux-diag，原有数据库/服务未改。诊断尚在安装依赖，未得结果。

## 诊断所得与下候选修订

root容器因非CI等价的root运行产生network service sandbox FATAL循环，已显式停止，未计通过。非root容器正常UI/CSP/异窗/崩溃重建均到达，native阶段明确报SUID helper须root属主及4755，desktop冒烟通过；该问题在容器内已证实，但不能归因GitHub的90s超时。完整日志、脚本、环境与部分矩阵见docker-diagnostic。TLS下载另试Docker网络仍SSL_ERROR_SYSCALL，停止重复下载。

独立内部agent核对后，Quality增加只针对锁定Electron官方helper的root/4755准备，使用本地install-electron bin；C1显式chromiumSandbox:true，不再接收PW默认no-sandbox，并断言主进程无该开关。未添加no-sandbox/disable-gpu-sandbox、未放宽90/45s时限、未跳过任何断言、未加容器capability/seccomp例外。该runner准备必须由实际CI确认，未声称已修复GitHub超时。桌面既有冒烟仍保留PW默认参数，不把它泛称C1隔离实测。

## 新候选前最终验证

未获焦方案一次超时、加焦点后仍一次超时（两次原始JSON/命令日志已保留），因此没有把焦点视为已证实根因。将故障改为不await的真实直接无限循环，主进程仍送真实输入；显式捕获Promise拒绝，仅旧窗口destroy后可接受，其他立即失败。输入前3s有界聚焦、250ms输入时复核、40/45秒总时限全部保留。新方案build2/2、packaged2/2、development C1 1/1全部通过；15TS/198Python完整check退出0，verify:sources13项成功。销毁后的Promise拒绝分支未在这些矩阵中实际出现，不声称该分支已运行。

最终内部独立只读综合复核未发现阻断；对原CI路径修复、官方helper准备、全部原断言/时限、故障catch/焦点/失败证据保存均核对。允许本地冻结，不替代指定模型或远端CI。16路径新freeze，64保护哈希全一致；产品apps/packages/依赖差异为空。只允许流程证据追加，任何受审文件变更须再建candidate双方新任务。
