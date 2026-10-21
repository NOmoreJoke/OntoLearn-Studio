# I05 profile：D1 依赖 A 面实际候选

2026-10-21。D1 两文件候选已完成真实解析、独立 frozen 安装、八库发行/metadata/许可核对及有限依赖烟测，正常 check/source 通过。交总控核验后才能按原字节交 I05 消费；D2 构建/入口仍未实施，包、真实 I05 probe 和父验收待后续授权与实测。原 T03 Goal 工具状态保持 blocked，不重建。

## 来源、隔离与实际改动

- 准备依据为 `4fa5d62eb13269351384527b1f84761c08811e79` 的 A 面；实际实施授权 4518B / SHA `ec8f6c92c66daf2ba8b6bc8216a208a6801cbd226d91f297b5955cc7c5a15914`，原文保存在 [authorization.md](../../reviews/T03/I05-profile-dependency-A/authorization.md)。最新共同指南 SHA `e437121a08053544c2a09151ac5183baf15b5fa67a3a604891aaa9e77ba971b0` 已全文读取。
- 核空后新建实际树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-profile-build`，分支 `feature/T03-profile-build`，base/初始 HEAD 均为批准 `5f910b52c69d86a1076b2032e5d3c63e715947f3`。新树 `.venv`、`node_modules` 是独立实际目录；uv cache 与下载证据在本树 build 私有目录，安装 link-mode=copy。只共用只读受管 Python 解释器，不使用其他树/C4 可变环境。
- `packages/engine/pyproject.toml` 仅新增 exact direct `pyparsing==3.3.3`、`pyshacl==0.30.1`，保留 `rdflib==7.6.0`。其余声明不变。
- 根唯一 `uv.lock` 由实际 resolver 生成，18→23 条：新增 html5rdf/owlrl/prettytable/pyshacl/wcwidth；既有只 engine 依赖声明和 rdflib 的 html extra 改变，其余 16 条及非 package 顶层字段、markers、平台发行集合/哈希保持一致。没有 B/XLSX 三库，没有新 I05/quality 源码。
- `scripts/build-engine.mjs`、`packages/engine/entrypoint.py`、根 pyproject 与 npm lock 均逐字等批准 5f；旧 source-selection/mapping、C4 和 I05 树未修改。AGENTS 同步保护版本 SHA `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`，不 stage。

实际 lock SHA 为 `86dfe82d952e2c88edcfc5658f488f6e1f0d04b4ec3b1e6f5c5d3bc4f57e8b73`；与固定 C4 恰好相同是新解析的结果，没有复制 C4 lock。真实命令及输出保留为编号 01；完整两文件 [product-patch.json](../../reviews/T03/I05-profile-dependency-A/product-patch.json) 解码原始 patch SHA `bd40fb379d0771a7321580ddbdd02ed49230f12ee2bb2a7590f20ce269991734`，静态记录在 [lock-delta.json](../../reviews/T03/I05-profile-dependency-A/lock-delta.json) 与 [inputs.json](../../reviews/T03/I05-profile-dependency-A/inputs.json)。

## 实际闭包与发行证据

| distribution | 实际版本 | 实际 metadata/文件中的许可证标识                   |
| ------------ | -------- | -------------------------------------------------- |
| pyshacl      | 0.30.1   | Apache 2.0                                         |
| pyparsing    | 3.3.3    | MIT                                                |
| rdflib       | 7.6.0    | BSD-3-Clause                                       |
| owlrl        | 7.6.2    | W3C-20150513                                       |
| prettytable  | 3.18.0   | BSD-3-Clause                                       |
| wcwidth      | 0.9.2    | MIT classifier + LICENSE；表达式字段为空，如实保留 |
| html5rdf     | 1.2.1    | MIT classifier + LICENSE                           |
| packaging    | 26.3     | Apache-2.0 OR BSD-2-Clause                         |

pyshacl → owlrl/packaging/prettytable/rdflib[html]，owlrl → rdflib，prettytable → wcwidth，rdflib → pyparsing，html extra → html5rdf。每个已激活 metadata 依赖约束均由实际安装版本满足；`uv pip check` 成功。跨平台锁 23 条在当前 macOS arm64 按 marker 安装 19 个发行项，数量不同并非丢锁。

八库模块全部从本树 `.venv` 导入。根据实际 dist-info/WHEEL tags 选择对应锁 URL，再真实下载并核 SHA/size；391 个 wheel 成员与已安装文件逐字相同，417 个 installed RECORD 哈希/长度通过。八库均有实际许可证文件，保存各文件长度/SHA、metadata 原字段与 classifiers。wcwidth 实装 `cp310-abi3-macosx_11_0_arm64`，锁里其他平台 wheel 未删。原下载 wheel 保存在 `build/d1-distributions/`，不将大二进制入库；JSON 提供固定 URL/hash/size 与本地定位。

[dependency-evidence.json](../../reviews/T03/I05-profile-dependency-A/dependency-evidence.json) 是实际结果，编号 08 为完整 stdout。有限烟测包含 pyparsing `count=7`、html5rdf 内存 HTML、owlrl 的微型 RDFS 扩展、pyshacl 一正一负约束、PrettyTable、Unicode 宽度及 packaging 版本比较。它只验证第三方库，不 import OntoLearn，不实现或执行 I05 reason/probe，不代其 oracle、容量或包验收。

## 命令终态与首失败

所有编号命令保存 argv、cwd、受控环境、开始时刻、耗时、退出码和未经覆盖的 stdout/stderr。原始文本入库用于 root 核对真实终态、保留首失败，不提交缓存/venv/大二进制。

| 编号 | 实际命令/范围                                                            | 终态                                                                                                                                |
| ---- | ------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------- |
| 01   | `uv lock`，仅以四个新传递项的 exact `--upgrade-package` 约束选择目标版本 | 0；解析 23 包、新增 5                                                                                                               |
| 02   | `npm ci --ignore-scripts --no-audit --no-fund`                           | 0；独立 node_modules，未启动 Electron；保留原有 deprecated 提示，不无关升级                                                         |
| 03   | `uv sync --frozen --no-progress`                                         | 0；新建独立 .venv，安装 19 项                                                                                                       |
| 04   | 首轮有限依赖烟测                                                         | 1；证据脚本 Turtle 将 `ex:Shape` 等误写成点号，原 stderr 与当时完整脚本 `04-dependency-evidence.input.py.txt` 保留；未生成成功 JSON |
| 05   | 首轮 `npm run check`                                                     | 1；630 TS/构建已通过，后续 ruff 在新增证据脚本发现一行 108 字符 E501；修正文档脚本换行，未改产品                                    |
| 06   | `npm run verify:sources`                                                 | 0；12 个归档源全部匹配                                                                                                              |
| 07   | 修正 E501 后正常完整 `npm run check`                                     | 0；lint/格式/类型/构建通过，630 TS、1052 Python 全通过，零 skip                                                                     |
| 08   | 修正 Turtle 后有限依赖烟测                                               | 0；复用本 D1 首轮下载的不可变 wheel 并重新核完整 hash/字节，八库及全部有限样例通过                                                  |
| 09   | `uv sync --frozen --check --no-progress`                                 | 0；19 项同步，无需修改                                                                                                              |
| 10   | `uv lock --check --no-progress`                                          | 0；23 包锁与两文件声明一致                                                                                                          |
| 11   | `uv pip check`                                                           | 0；实际安装依赖相容                                                                                                                 |

07 后只修正证据烟测的输入及本轮 wheel 复用逻辑，对变化脚本单独做 ruff check/format 与实际 08 重跑；产品/lock 没变，不重复整套矩阵。原 04/05 失败未改写成通过，最终本线独审及交付收据位于同一 review 目录。

## 后续交付条件

总控核验本精确两文件候选后，可另授权 I05 原字节接收；两文件维护权仍唯一 T03。本轮没有 push/PR/CI/merge，没有新建或恢复 Goal，也未运行 GUI/Electron/native/e2e/HMR。

D2 两条构建/入口仍只读，须等 I05 固定新 probe 的 ref/path/hash/main/CLI/私有 JSON/身份/预算、唯一 inputs/assets 与分离 oracle 后，再获总控精确接线许可。实际 PyInstaller 库/data/metadata/许可与七 canonical quality 身份、源码/包内同输入完整计算与失败矩阵、B1/目标平台/父范围、指定同版双新审与 CI/正常合并门全部保留；D1 源依赖烟测不代包通过。
