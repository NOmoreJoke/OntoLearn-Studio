# I05 正式集成候选 C1：验收与来源

本记录更新完整 I05 的实际集成证据，不把早期独立 v4 / adapter 检查点写为本候选通过。基线为正常 merge 的 I04 PR5：`5f910b52c69d86a1076b2032e5d3c63e715947f3`；集成 merge `9f8832f218517abe24009a30988a659529b1adc0`。产品源码受测头 `6b57078e30db8faffe05f4b2b2bc879aaaa85a6a`，最终仅原生测试入口修正头 `851be577b439d53ad081f2ba093b708e1acb3cdc`（0218为前一版ready门槛证据）。正式审查头由随后 candidate-1.json 固定；证据追加不改变上述受测源码。

## 已执行检查

| 实际检查 | 结果与范围 |
| --- | --- |
| Mac 无窗口 `npm run check` | 672 TypeScript、1511 Python 全通过；lint / format / typecheck / build / Ruff 同一命令通过。原日志 `logs/check-final.txt.raw`。 |
| `npm run verify:sources` | 12 份归档来源字节通过。指南另核验 SHA，保持 dirty、未 stage。 |
| Mac / Linux `package:dir` | 实际未签名目录包构建通过；Mac 不启动 Electron。Linux aarch64 与 Mac arm64 不代表首发平台或签名安装。 |
| Mac B1 完整无窗口验证 | 源码 / 包内同样例完整相等；原 S1 口径 12 条测量＋真正 fresh 子进程 12 条；本地合成接收端正校准1次，拒绝入口0命中，每运行时28项；完整原始输出、imports、动态链接、400引擎文件及许可清单见 `macos-parity-final/`。 |
| 两平台便携包内 CLI / stdio | `verify-i05-runtime.py` 实际完整语义 suite 相等，真实标准输入输出三能力 Job / 结果落库通过，native 许可来源与本机运行时精确匹配。 |
| 两平台 C4 包内回归 | `verify-i04-package.py` 公共样例326/11/30/9/7/41/51，17项真实驻留 / owner / worker / 包资源回归通过，实际 exit0。不是拿 I04 旧报告代替。 |
| Linux 源码语义桥接＋真实原生恢复 | 最终 harness 2项通过23.4秒：窄方法实际调用、完整分页、真实外联拒绝、reload / 显式取消；原生崩溃与真正死循环无响应恢复保持已提交语义结果。 |
| Linux 打包语义桥接＋真实原生恢复 | 最终 harness 2项通过24.4秒；先前同产品包的既有 CSP / 桌面3项已过，不重复不变用例。 |

原生产检查与0218检查点见 [117份原字节清单](evidence/integrated-c1/manifest.json)；表中851最终源/包native及harness静态检查见 [sealed原字节清单](evidence/integrated-c1-sealed/manifest.json)。两清单均记录文件路径 / SHA / 原收集路径。ready检查点源绑定 `bindings/source-binding-0218d6e.json.raw`：982个当时实际跟踪路径与隔离容器逐字一致；6b→0218只有 `tests/e2e/i05-semantics.spec.ts` 改变。最终851的198份全部执行输入与容器逐字一致，见文末sealed源绑定；生产源码 / 依赖 / 打包配置仍与6b逐字相等。包由6b源码产生，最终原生测试由851入口驱动，没有声称重建过不同产品包。

Mac 引擎 SHA `71d4b4bcb33c2d529560aaa76935a95c9d2991941345d9fc850705fbc6bb32d9`；Linux 引擎 SHA `f11e22844266a3d1bf40923191456a5d1316e82a427a7a7d61b683d1baf18ee2`。Mac 引擎目录37,632,518 bytes，完整 app561,702,426 bytes。设备、Python / 全部锁依赖版本、方法、每阶段原值、完整结果、stderr、OS缓存限制均在原始清单；不把样例当容量阈值或量化性能提升。

## 实际运行与窗口证据

Linux 使用本线 `ontolearn-i05-isolated-20261021-v2`，无 host mounts，独立 `/i05`、HOME、npm/uv缓存、依赖、SQLite和输出。工具镜像从已存在不可变系统镜像创建本线副本；只给测试容器 `CAP_SYS_ADMIN` 支持 Chrome sandbox namespace，chrome-sandbox 为 root:root 4755；所有应用/验证命令显式 `docker exec -u node`。不是生产权限建议；没有 `--no-sandbox`、隐藏窗口、禁用 hang monitor 或替身提示。`docker-isolation.txt.raw` 的 Config.User空串仅是容器默认，实际应用执行用户由上述命令指定。系统诊断 `linux-linkage-and-source.json.raw` 的顶层 python 是诊断 python3；真正产品 CPython3.12.15/BUILD20261013来自包内清单与实际探针。

最终源码和打包各自独立 Xvfb / Openbox / 新 fixture。两份 `i05-native-verified-evidence.json.raw` 均实际 `events=[crashed,unresponsive]`、`inspectorClosed=true`、`hangMonitorEnabled=true`、`noSandboxSwitch=false`；三个重建窗口可见；第二窗口 `focused=true` 且外部 `xdotool/XGetInputFocus` 正面记录可见 OntoLearn Studio。两个真正 GTK 恢复提示由外部窗口枚举和键盘操作完成，标题 `OntoLearn Studio 窗口恢复`，分别 crash / hang；不覆写 dialog API。三个时点完整 result metadata / 分页行 / snapshot / revision / operation身份相同，后台真实 COUNT worker仍running，最后显式取消且没有自动重放。

fixture保留G原业务事实，删除003名称后17条，再加10条独立负载事实共27条；COUNT用9个独立模式形成10^9候选组合。它是忙任务故障注入，不改120秒生产总时限、75秒harness、90秒测试时限、源/包一致要求或S1的18/180测量规模。

## 保留的失败与修正

- 首轮全库 check：新增5例导致公共样例326，旧计数断言321失败；修断言期望后完整检查通过。未删契约例或改变解析行为。
- 第一轮集成测试 fixture 误用非UUID事实身份，S1真实校验拒绝；修fixture后实际worker联验继续。原14errors/1failed不掩盖。
- 初次 Linux fixture含1000条无关负载事实，在现有完整source分页下拖慢恢复取证；改为10条、9模式维持同10^9工作量。未改生产Store、分页上限或扩大超时。
- 首次 Openbox 重定向缺少build目录；随后真正namespace检查拒绝无特权容器；各原日志保留。创建本线支持sandbox的隔离容器后才执行有效原生验收。
- 第一次最终打包 native 在故障注入前失败：主进程 inspector 早于 Electron 内建模块安装，外置hook得到路径字符串而非app。0218只加5秒真实 `app.isReady()` 门槛和 `awaitPromise`，无fallback/stub。定向type/lint通过，并对源码/打包各重跑完整2项真实语义/native验收关闭。
- 独立内部审查实际提出私有帧与公开1024协商预算混用、用户有限构造producer错误、输入词法预算错误阶段、最终validationBinding增行后预算错误、disabled规则误计预算；逐项修复并用真实worker反例关闭。208适配器golden、29实际运行联验及全库1511包含这些回归。

## 未取得的门禁与边界

截至冻结前本记录：指定 ZCode / MiniMax 新全范围任务、双报告实际终态与逐项处置、push/PR、真实三平台CI、正常合并和远端核验均尚未取得，不能由本地绿代替。当前原Goal工具仍blocked且无resume API；依总控解除依赖授权继续原完整工作，未新建Goal或假称完成。

Q6十二行各自采用/修订/淘汰决定仍开放；Q2/Q3/Q5/Q6/Q7/Q8/Q9没有替负责人决定。B1是有限候选技术验证与其必要真实任务接线，不声称整个M1、规则比较/单条多结论、业务编辑器、映射、行为、沙盘、模型外发或通用标准一致性完成。对象历史/resource上下文持续保留的增长及跨平台native许可未匹配时pending仍如实登记；Mac/Windows真实窗口矩阵、签名、干净设备、生产、容量阈值均不是本证据获得的结论。

## 最终 harness 封口补充

851be57将实际hook加载放到catch外，仅允许尚未安装的Electron内建模块探测暂时失败；hook自身异常必须立即失败，不能吞错后重复注册。生产源码未改，最终源/包2×2在独立sealed目录通过。原0218两次通过、117份原证据与manifest原样保留；最终覆盖关系、逐执行输入SHA、原始完整窗口/分页和fixture证据见 [sealed清单](evidence/integrated-c1-sealed/manifest.json) 与 [源绑定](evidence/integrated-c1-sealed/source-binding.json)。先前982路径绑定属于0218，不冒称851完整树；851全部执行输入与容器逐字一致，唯一晚变更仍只是此测试harness。
