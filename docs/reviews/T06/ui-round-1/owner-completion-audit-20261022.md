# UI 两指定原审查封存与处置

对象为base5f、产品 `da37709dcf09e04ded767ab2d08c26bbd8df24f3`、流程 `3b3af941c73b7a5d416fda50ec6fb8102992551f`。两独立原审查均已结束；**新增P2尚未关闭，不计为双无阻断通过**。owner已全文读取两报告、原始失败与修正链；原报告和全部中间版本保留，不修改标题或作者裁决。

| 项 | ZCode | MiniMax |
| --- | --- | --- |
| 实际session | session_498d6eba64585a20972eb406372bc4e2 | mvs_1e7a6b7b6e624cc28afb6f4bad4470e3 |
| 实际设置 | GLM-5.3 / max（最高）/ yolo（完全访问） | MiniMax-M3.1-Flash / xhigh / 始终授权 |
| 最终报告 | zcode-glm53.md，24568B | minimax-m31flash.md，45074B |
| 原字节SHA | b7715b6dd4d8b4caadfdeebc59136923e610ff1280590b63f4a0e04010061cfd | 929a20820b916c60d4ade7f57195f8db7a59c63359bccd9ea13e76d13b2c2a26 |
| 作者原结论 | 初轮无法验证，环境恢复后组件范围Pass | 写组件范围Pass，同时保留新增1P2、3P3与1脚本P3及装配前条件 |
| 真实结束证据 | 两轮turn.completed（10:04:26.178Z、10:11:15.993Z）及各自最终stop | 两最终stop、各query处理完成时间、GET idle0、90messages无more；原native SSE/turn_completed未捕获，不补造 |
| 工具/报告版本 | 101 calls、10报告版本重建一致 | 102 calls、6报告版本重建一致 |

实际设置由提交前后本任务CUA与正式GET/请求启动记录核验；报告模型自身不能证明设置，不意味着owner未核。首完整输入及后续环境补充的精确受理见两start receipt；第二补充全文2622B/SHA `35f8c5051d5398094a6e93843ea6067ed01bd6efbb151b783f128ec088778c2d` 已在两原session逐字节确认。桌面窗口均已交回总控，后续不占前台。

## 原件恢复与实际验证分账

工具包在 evidence/，只包含本任务工具业务值、原输入、报告各版、最终消息与实际产物，不含私有系统/headers/思考。父线逐regular成员读回、与来源字节比较并按manifest核SHA：

- ui-zcode-original-tool-evidence-20261022.tar.gz：3566845B/SHA `3fabc7472130653d15d50900f36a7015d2a6cac3e286a10c321d12f1a03c5b80`；1013regular、1012manifest数据件。
- ui-minimax-original-tool-evidence-20261022.tar.gz：1494644B/SHA `84d476e30e855aa4c0cce03164314e2512302103c521682052d84dedc806bfc5`；139regular、137manifest数据件，另manifest/SHA256SUMS两件。其collector实际输出位置为本体根outputs/ui-minimax-final-evidence，回执明确实际路径，没有冒称在日期子目录。

两者均实际运行了完整默认1248 headless夹具并查看新图；这证明未装配组件，不是正式引擎或原生验收。原脚本完整断言保留，临时副本仅组件/输出两行路径重定位。Z初轮未运行headless，环境消息后才运行exit0；MM首点击超时exit1，后3次exit0，所有原日志保留。MM多个运行覆盖了同一截图文件，现存PNG只能证明最后实际产物，不能补称每次PNG均独立保存；其八项额外探针两次均显示8passed，没有该组首败记录，也没有独立捕获每个管道上游Vitest退出码。

两原样check首exit1均由owner将历史解包物放入ui-review-evidence引起，不能当产品问题，也不能抹成原命令全绿。Z仅分项/排除证据后通过，原combined check没有绿；MM把自有51件证据完整核SHA、临时移出、原样check exit0、移回并核51/51字节一致，首败和全过程保留。下一候选/审查环境把这些已封存的自有过程证据置于冻结输入之外，不改lint/format忽略配置、不少扫受审源。

## 浏览器执行条件的纠正

1248是当前Playwright锁的默认配套，并非原用户额外版本硬门；owner派发新增“禁止1208/1217/1234、必须1248”的限制已由同一完整消息向双方纠正，原输入/TLS失败不改写。经Google官方同bucket/object JSON入口取得原ZIP，官方MD5/长度匹配、16成员CRC通过。Z由owner安全安装，MM已有副本由owner只读核16文件；两binary `--version` exit0=156.0.8078.4、SHA77d8278b…相同。安装/版本核验不等于UI通过，模型之后各自实际完整运行才形成运行证据。

Z称marker缺席，是实际探针检查binary子目录而非revision父目录；父目录INSTALLATION_COMPLETE真实存在，后续DEPENDENCIES_VALIDATED也存在，owner旁注保留，不改报告。Z报告§3“本轮无新截图”旧句与§4.2和两次成功新图Read矛盾，也保留原件并旁注。Z完整browser OS argv未捕获，modelIO有意省略传给模型的转换JPEG dataUrl；原PNG有原字节，不虚构当时转换后像素。MM完整argv来自后继launchServer探针，原browser.process()失败被tee掩码0，失败已保全；不能把后继argv倒推为之前每次运行的OS实录。

## 意见处置与后继

MM新P2是实质可达问题：同context等价callback身份变化令controller清pending，旧Promise尚未收尾即可第二次run，不能以宿主useMemo/装配前再修关闭。原UI独占agent在原behavior/与t06-*路径最小修复，分清物理operation token和显示epoch，保真实在途、防重入、旧回包归属与取消/最后finally不干扰后继。原候选与两reviewtree不改，后继须新固定来源、必要完整验证、完整独立审及双方全新同版审查。

混合保留键载荷继续整事件显式拒绝并保留原文，补提示/用例，不接受静默strip后放行普通字段；取消错配使用专用未确认提示；适配器自由文本白名单属于T00装配门，不加猜测路径过滤；脚本可操作性只做有界无副作用等待与首败诊断。Z的index key焦点/定位维护性提示保留，不扩大本轮核心修复。

放行前parent已再次逐字节核原UI树和两reviewtree的全部7源码与da匹配，原件封存完成后才向原owner放行。完整FR、App/bridge/Store/推理/G.3/Agent、原生两OS/包内/真人、CI/远端/发布门均不因本次封存关闭。
