# T09 四实际审查树完整派发准备

四份正文均为对应旧完整提示的精确字节前缀，加实际路径、当前政策和明确执行补充；保留全部工程、原验收、历史失败与关闭，不只最后delta。两候选分别完整双审，无混版。当前仅准备完成，未创建模型任务、未获GUI lease，父Goal保持blocked。

| 任务          | 固定reviewHead / product                                                            | 全tracked文件 / 固定输入 | 完整正文SHA-256                                                  |
| ------------- | ----------------------------------------------------------------------------------- | ------------------------ | ---------------------------------------------------------------- |
| s1-zcode      | 72aa83a80a973a3edeb62ed95518bf1a22178985 / 76596656908ed84e577e8202a602e3256d5febcc | 869 / 106                | ebdaf40e51c09a602174a9cca2060934e53d376b7a48c2555927eef2565d922f |
| s1-minimax    | 72aa83a80a973a3edeb62ed95518bf1a22178985 / 76596656908ed84e577e8202a602e3256d5febcc | 869 / 106                | c9a468e258a0ddb18db63c2018e47ff31ab2bd6b8db0738f540e021506774c51 |
| stage-zcode   | 245718c71ca9f5325ab0a899fe17ad6f4e472f27 / 12699cc0f536f5875e8b021349b58c2c954145cc | 891 / 168                | e1020c9f833acb9917228596a56faa230d911aba3b4d40d6322d0d722c80c576 |
| stage-minimax | 245718c71ca9f5325ab0a899fe17ad6f4e472f27 / 12699cc0f536f5875e8b021349b58c2c954145cc | 891 / 168                | 5213b77ef907452e0f8471bd746a614e819e0d9a9d3c2c98857d5e6afc64e2ca |

精确实际workspace/CWD、完整正文/原件hash、逐条role物化路径、全部tracked Git字节、独占报告/raw/scratch/metadata/env/cache、setup回执见dispatch-manifest.json及各任务子目录。实际每个review根只放该任务自己的派发包，审查者不得读取/发现peer报告、状态、任务metadata或兄弟树。

四根npm ci --ignore-scripts与uv sync --frozen全部exit0；node_modules和.venv均为各自独立目录，workspace与Python editable指向本根。八份setup原始日志和四份收据保留；uv可能构建editable wheel，这是安装准备，不是产品构建或运行验证。未执行check/pytest/浏览器/产品/服务。当前保护指南四根均de15、M不stage，未加ignore或清理metadata求绿。

normal-validation-analysis.json静态记录正常check调用。指定审者可为实际疑点运行必要普通对应检查/原suite的受控worker与临时SQLite，不泛禁child或SQLite；无变化历史不机械全重跑。禁止扩大到已拒物理资源研究、新native/caller/producer、额外服务/dev/HMR、产品窗口、API付费/密钥读取。组件16套默认skip，不冒充浏览器通过。

旧S1 round-1及旧stage-round-1原件/manifest未改；产品字节未变。当前完整正文要求真实模型设置/正文受理/任务ID/完整终态/全文报告，未预填指定或产品Pass。关键验收缺失和全部父门如实保留；独立准备审查只核本包，后续由root预检并安排短GUI。
