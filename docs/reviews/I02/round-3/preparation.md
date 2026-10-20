# I02 Round 3 准备：修正真实故障事件的跨平台断言

固定base仍为 `1b6df7a220fc9a67d7046133a340085f03f0a96c`。Round2双方通过candidate为76b9d18，后续流程head7e26155已push；PR#3未合并。

实际CI run39359486479 的LinuxQuality job118422017398失败，完整日志见round-2-linux-job.txt，原始artifact见round-2-linux-artifacts。日志唯一C1失败断言：期望events含killed，实际[crashed,unresponsive]。nativeRecovery自身PASS，3窗/2提示/3显式health成功、inspectorClosed=true、hangMonitor=true、noSandbox=false、输入时可见获焦；CSP receiver零请求、异窗口拒绝。随后desktop.spec成功。整体CI job仍为failure，顶层evidence未写PASS，不更改原始文件。

锁定安装包Electron44.9.0的官方electron.d.ts18656–18666写明forcefullyCrashRenderer的reason允许killed或crashed；记录完整文件SHA与版本于electron-force-crash-contract.json。只将csp-lifecycle.spec.ts的单个killed断言改为接受这两种理由，并加契约注释。没有接受clean-exit/oom等任意其他理由，没有模拟事件，没有跳过真实无限循环/输入/unresponsive，没有放宽原90/40/45秒时限，没有修改产品、CI、依赖或验收。

独立内部agent只读复核实际Linux原证据、锁定类型契约与diff：该修订符合原始真实崩溃恢复验收，无新增阻断。此结论不替代指定双模型新审或远端CI。只能据本次证据确定“测试对契约reason过度收窄”；原Round1 GitHub90s超时根因仍不明，R2失焦与首次无诊断失败仍保留。

新完整check退出0（15TS/198Python）、verify:sources13成功。后续将追加本次三环境原始运行证据、Windows旧head最终结果、新candidate/freeze与两方全新任务；不得在双审前push新测试变更。

Windows旧head job118422017293最终也为failure，完整日志round-2-windows-job.txt显示同一断言：期望killed，实收[crashed,unresponsive]，不是新的启动错误；后续desktop冒烟通过。日志显示native阶段已完成且此前result/inspector/hangMonitor/sandbox/packaged断言未失败，但Windows未上传原始matrix，本地没有该JSON，不能声称已下载Windows完整matrix。旧run最终macOS success、Windows failure、Quality failure，准确记录于round-2-ci-final.json。本候选断言修订同时覆盖两个目标平台的已知契约差异；新head实际全绿仍待双审后CI。

新候选冻结前本机验证全部完成：完整check退出0（15TS/198Python）、verify:sources13；build e2e2/2、真实packaged e2e2/2、development C1 1/1均PASS。原始日志与JSON直接归档本目录，sha与验收字段汇总见candidate-validation.json。真实终止事件本机仍为killed，独立unresponsive、三窗/两提示/三health及所有隔离/CSP断言保持；Linux/Windows的crashed分支有旧head真实运行证据，新测试在目标平台的实际CI仍未执行。未运行HMR写源探针。开发服务器使用本任务子进程组，完成后仅终止并回收该组；未操作其他服务。

原始CI材料入库理由：此前曾发生CI日志/artifact下载失败且错误上下文被后续运行覆盖，本次成功取得的同次小体积artifact、两平台失败日志是“唯一报告失败断言”的可核对依据，故连同关键JSON和hash保留，以便跨候选复查；截图/trace按完整原artifact保留，不据其存在额外宣称通过。Windows文本Git会标准化CRLF，另保留原始字节gzip及双hash。后续仍优先引用CI artifact与关键摘要，不无差别归档运行库或业务数据。
