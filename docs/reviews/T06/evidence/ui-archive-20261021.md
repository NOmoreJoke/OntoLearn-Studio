# UI 原件恢复包

本次按总控明确的新原件保全任务封存；产品、验收和 Goal blocked 状态均保持。没有复测、重建或启动 GUI。

完整索引为 ui-archive-index-20261021.json，含两包字节数、SHA-256、Git blob、源记录与读回结果：

- ui-original-artifacts-20261021.tar.gz：2,232,198 字节，SHA-256 a51bfec8089f9a7db1578ebbfcc3570e1591beda51b956f2d8bf165a0cfab433。33 件原文件：当前9、旧571的11、main out独立5、临时脚本/当时index/previewJS/CSS/debug共5，以及固定Git来源清单3；另有内置 manifest.json。该 manifest 逐项列原绝对路径、字节数、SHA 和读回结果。
- ui-session-tool-records-20261021.tar.gz：6,698 字节，SHA-256 06d2e8636bbef29c6bb131bb3605c4f15e679d784137a2bffec5e58d472f5a3b。仅六条原工具JSONL行、最小manifest和说明，共8成员。原行来自已核验的审查者自己的子session；call/output身份、1-based行号、0-based字节偏移、含原换行长度及SHA均在包内manifest，父线再按offset读源片段逐字节核对。

历史原行对应：独立34单测 call647/output651，原始exit0，直接终态、无yield/wait链；旧571虚拟入口失败 call484/output487，exit1；旧571返回数组形态失败 call491/output494，exit1。未以开发线日志代替独立原件，未重跑制造历史证据。原始session_meta只核身份及源行hash，未复制其原文、人类/系统/开发者消息或整个会话。

两包已分别从Git暂存blob读回；所有42成员又恢复到独立scratch并与原封字节比较，通过。提交后可从包含此索引的Git提交提取两包，无需依赖原UI工作树、ignored目录或/tmp：

1. 用 git show 读取该提交中的两个archive路径，保存为二进制文件。
2. 先按索引的字节数及SHA核包，再以tarfile读取包内manifest。
3. 只恢复manifest/索引列举的regular成员，拒绝绝对路径、`..`和链接，逐文件核字节数/SHA；不要执行其中脚本或preview代码。

确需将约2.24MB二进制原件入本地Git的理由：本次明确要求清理后的恢复性，只有hash无法恢复ignored/tmp原件。包仅含精确白名单及最小来源，没有依赖环境、浏览器缓存、运行库或全会话。原文件均保留，无清理/覆盖。

本次请求目标均找到，无缺件；历史未记录的浏览器二进制SHA/完整argv仍未记录，不从当前metadata倒推。60仅为4×5×3合成组合；UI1052Python不混入S1的1174。旧negativeprobes已有Git固定副本2965字节，SHA dc8b54956bbfda1f0b2d0548ca7a8eecaa6fdbbf07c54306d0ef4c65b69562ab，不再称仅/tmp缺口。真实接口、审查桌面条件与完整父功能门均未解除。
