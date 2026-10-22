# T09 四实际审查树派发准备独立审查

结论：**当前限定准备范围通过，无未关闭准备阻断。** 四份完整正文、实际工作区、固定输入物化和安装证据对应一致；执行补充明确覆盖旧路径、分支、静默和泛禁运行措辞，同时保留全部验收与真实不通过/无法验证门。本结论不是指定模型或产品 Pass，不关闭关键验收缺失，也不授予 GUI/model lease。

2026-10-22（Asia/Shanghai），独立 Codex 子 agent `t09_prd_audit`。本次仅静态 Git、文件/hash、JSON、路径及安装原件核对，唯一写入本报告；未重装依赖，未运行产品测试、构建、服务、GUI、模型任务或 Goal 操作。

## 固定包与正文

中心为 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T09-learning-baselines/docs/reviews/T09/dispatch-20261022`。最终 `dispatch-manifest.json` 为 17122 bytes，SHA-256 `88c1a67b1199d11094f8dc21c3c26dfe1674856f16b1689e8c8e2ae362876749`。

| 角色          | 全 tracked / 固定条目 / 运行源 | 完整正文 SHA-256                                                   |
| ------------- | ------------------------------ | ------------------------------------------------------------------ |
| s1-zcode      | 869 / 106 / 32                 | `ebdaf40e51c09a602174a9cca2060934e53d376b7a48c2555927eef2565d922f` |
| s1-minimax    | 869 / 106 / 32                 | `c9a468e258a0ddb18db63c2018e47ff31ab2bd6b8db0738f540e021506774c51` |
| stage-zcode   | 891 / 168 / 34                 | `e1020c9f833acb9917228596a56faa230d911aba3b4d40d6322d0d722c80c576` |
| stage-minimax | 891 / 168 / 34                 | `5213b77ef907452e0f8471bd746a614e819e0d9a9d3c2c98857d5e6afc64e2ca` |

实际四 root 与 manifest/总控 roots 来源一致，均为 detached HEAD。S1 两树固定 reviewHead `72aa83a80a973a3edeb62ed95518bf1a22178985`、product `76596656908ed84e577e8202a602e3256d5febcc`；stage 两树固定 reviewHead `245718c71ca9f5325ab0a899fe17ad6f4e472f27`、product `12699cc0f536f5875e8b021349b58c2c954145cc`。批准 shared base 均为 `5f910b52c69d86a1076b2032e5d3c63e715947f3`，stage 的 local parent 74b 与共享批准基线没有混淆。

四份 full-dispatch 均逐字节满足：对应旧完整 prompt + 分隔符 + 完整 execution-addendum；不是最后 delta 或 source-only 提示。完整旧提示已在原准备审查全文读取，本次又核对精确前缀；新补充全文读取并逐份比较，归一角色路径/身份后仅 stage 多一条 stage 专项参考命令。各 root 的本地 full-dispatch、mapping、source-bytes 与中心 hash 相同，实际本地派发目录只包含自己的角色包。

## 工作区、输入与环境

逐文件核对四树全部 tracked 路径集合、Git blob、实际字节/hash 与 source-bytes 清单，869/869/891/891 全部吻合；唯一预期覆盖为当前保护 AGENTS `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`，保持 M。32/34 运行源码/内容/测试分别等于各自 product，未拼接候选；S1 round-1 十一件与 stage-round-1 十二件均保持固定 reviewHead 原字节。

每树原 manifest 的 106/168 条角色/ref/path 集合与 mapping 完全相同，所有物化副本的 bytes、SHA、已有 Git blob 均正确，实际路径位于自己的 root。产品/流程同路径不同 ref 分开保存，未拿物理流程 HEAD 替换旧产品角色。`sourceBytesManifest.path` 等实际读取入口指向本地副本，不要求审查者访问开发中心或兄弟树。

四树 node_modules、.venv 均为独立目录且非 root symlink；两个 npm workspace 链接及 Python editable `.pth` 均指向本根。report/raw/scratch/metadata/npm-cache/uv-cache 的解析路径均留在自己的 root，互不重叠。四份安装收据与本地、中心副本一致；八份原日志的 bytes/SHA 与收据相符，记录 npm ci --ignore-scripts 和 uv sync --frozen 均 exit0。uv 日志的 editable wheel 构建属于依赖安装，不是产品构建/运行通过；setup 未冒称正常检查、浏览器或领域执行结果。runtimeVersions 是开发线记录，本审查未重复启动版本命令。

## 限定执行与真实结论

`normal-validation-analysis.json` 的 hash 与 manifest 一致；其 scripts 与固定 package.json 逐项相同。另静态读取 desktop scripts、Vitest include、Python 项目声明和真实 Session/I04 入口：正常 check 为 lint→格式→类型→普通 Vitest→electron-vite 构建→ruff/pytest，不等于 e2e/package/dev。原普通 pytest 确会启动受控 stdio 进程并使用临时 SQLite，不能因为 child 或 SQLite 一律禁止。

补充明确允许指定审查者针对具体疑点运行必要普通对应检查，并明确覆盖旧 stage“所有产品命令先另取票”及旧 S1 的泛禁解释；要求先读固定原件，无变化不机械重跑。运行仍在本根环境、独占临时目录与 raw 留存，不能扩成已拒物理资源研究、新 native/caller/producer、用户数据库、额外服务、dev/HMR、产品窗口、付费 API 或凭据操作。16 组件默认 skip 不记浏览器 Pass，显式浏览器验证仍需匹配 runtime 与具体授权。本准备审查未消费这些未来验证权限。

实际 CWD、detached HEAD 和唯一报告路径明确取代旧开发树/branch，只写自己的报告及必要运行证据/正常构建输出；禁止发现、搜索或读取 peer 本轮报告、状态、任务数据库、metadata 或兄弟树。当前非静默政策的三份快照与实际来源相同，并完整嵌入四补充；短 GUI lease 只用于任务创建/设置/正文/终态读回，不独占后台推理。metadata 增长要求据实保留，不删除或新增 ignore 求绿，未把 Git 不 clean 自动判成产品漂移。

所有原验收、历史逐项处置、领域/持久账本/正式接线/包/平台/真人/57P0/CI/远端门保留。关键缺失须按真实不通过或无法验证，禁止条件 Pass、有界 Pass 覆盖或预填结论。GLM-5.3/max/yolo 与 M3.1-Flash/xhigh/bypassPermissions 仍要求逐任务实际设置、正文受理、任务身份、完整终态及全文报告读回；mapping 当前 actual task/settings/terminal 为 null，GUI lease=false，没有把准备完成登记成任务或指定通过。

本次未发现须先修改派发输入的问题。后续仍须原 owner/总控绑定本报告和最终包，实际取得短创建 lease、分别派发完整新任务并保存真实终态；本报告仅证明以上准备对应关系。

EOF 规范化复核：四份 addendum 与四份 full-dispatch 均仅删除末尾一个多余 LF，保留一个终止换行；将当前字节补回一个 LF 后，八份均恢复本报告首轮审查时的旧 SHA。实际四 root 的对应副本一致，最终 manifest 与上表四正文 hash 已更新。此次只复核该字节差异，未重复全文探索或产品验证；结论不变。
