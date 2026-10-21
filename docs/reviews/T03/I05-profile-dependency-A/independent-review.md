# D1 依赖 A 面独立内审

2026-10-21。结论：**通过；本轮未发现未关闭的阻断问题。** 结论仅覆盖批准 5f 基线上的依赖 A 面两文件及其交付证据，不表示 D2 接线、产品包、I05 计算或指定双外审通过。

## 审查边界与候选身份

实际树为 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-profile-build`，分支 `feature/T03-profile-build`；审查时 HEAD/base 均为 `5f910b52c69d86a1076b2032e5d3c63e715947f3`。产品差异仅 `packages/engine/pyproject.toml` 与根唯一 `uv.lock`。

已全文读取本次实施授权（4518 B，SHA-256 `ec8f6c92c66daf2ba8b6bc8216a208a6801cbd226d91f297b5955cc7c5a15914`）、本树 AGENTS（`78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`）及共同指南（17891 B，`e437121a08053544c2a09151ac5183baf15b5fa67a3a604891aaa9e77ba971b0`），按完整第九节及本次更窄授权执行。审查者仅使用 git、文件、JSON/TOML/ZIP 与哈希静态读取；未安装、联网、导入产品、执行产品/测试/构建/包或启动 GUI，未恢复 Goal。唯一写入为本报告。

| 当前最终对象 | 字节数 | SHA-256 |
| --- | ---: | --- |
| `packages/engine/pyproject.toml` | 398 | `bcc8825b1f2902a66ae539e687df57e5b2554247f48a48a65215601a77958365` |
| `uv.lock` | 28440 | `86dfe82d952e2c88edcfc5658f488f6e1f0d04b4ec3b1e6f5c5d3bc4f57e8b73` |
| `product-patch.json` | 11232 | `bd3719132f4e3ff77b3b82dea3c84778512381b64a29e3fcbc15bd45cfb4ace0` |
| JSON 解码原始 patch | 10446 | `bd40fb379d0771a7321580ddbdd02ed49230f12ee2bb2a7590f20ce269991734` |
| `docs/iterations/T03/I05-profile-dependency-A.md` | 9101 | `7c035620246982422bb440b33eff9c2d44ca1ba82c34db8a95b7047a2a0e8879` |
| `dependency-evidence.json` | 29819 | `3c84eef58cb5ddf5427d99ea201dc2c7a0c6539b1e960fee7767055c5af45f56` |

表中 review 文件均在本报告同目录。逐项核对 `inputs.json`、`lock-delta.json` 与实际文件。原 `product.patch` 的标准 unified diff 空上下文行含单空格，负责人将其无损封装为 JSON，避免证据文件自身尾空白；审查者实际解码并与当前 `git diff -- packages/engine/pyproject.toml uv.lock` 比较，全部字节相同。该调整未改变产品、锁或运行原件。首读主稿为 9072 B / `d32a9162a83721870a05b867a8cd50f518465a97a5542f9a4059cd352b40b7ab`；最终仅 patch 载体链接调整，已重读最终全文并绑定上表身份。

## 两文件与闭包核验

`pyproject.toml` 仅增加 exact direct `pyparsing==3.3.3`、`pyshacl==0.30.1`，保留 `rdflib==7.6.0`。pyparsing 在 5f 锁中已有，本轮提升为 direct，未误算新增发行项。

锁从 18 变为 23 项：新增恰为 html5rdf、owlrl、prettytable、pyshacl、wcwidth；既有记录仅 engine 声明及 rdflib 的 html optional dependency 有实质变化。其余 16 条记录的字段/发行集合、非 package 顶层字段及 markers 均不变；逐块原文比较时，原末尾 setuptools 块仅因追加 wcwidth 多一个分隔空行，无字段变化。没有删除旧发行项或收窄平台 artifact 集合。

目标闭包为 pyshacl 0.30.1 → owlrl 7.6.2、packaging 26.3、prettytable 3.18.0、rdflib 7.6.0 **[html]**；owlrl → rdflib，prettytable → wcwidth 0.9.2，rdflib → pyparsing 3.3.3，html extra → html5rdf 1.2.1。八项版本、依赖及 optional edges、完整发行 URL/hash/size 集合均与批准固定 offer `4fa5d62eb13269351384527b1f84761c08811e79` 的静态输入记录吻合，没有遗漏 extra。

没有 openpyxl/et-xmlfile/defusedxml，未自动采用 B/XLSX 组合，未引入 I05/quality 实现。`scripts/build-engine.mjs`、`packages/engine/entrypoint.py`、根 pyproject 与 npm lock 均与批准 5f 相同，D2 未实施。AGENTS 是同步的保护规则，未将其当产品改动或授权提交项。

编号 01 的真实 argv 为 `uv lock` 加 owlrl/prettytable/wcwidth/html5rdf 四项 exact upgrade 约束及 `--no-progress`，原 stderr 记录 CPython 3.12.12、23 包解析及五项新增，退出 0。当前锁 SHA 恰与 C4 相同，不能仅凭相同 SHA 推断复制；现存新树命令及输出支持一次实际新解析，未见复制 C4 锁/可变环境的证据。

## 发行、许可与隔离证据

审查者静态检查 `run-command.py` 的 argv/cwd、独立日志与退出码记录，以及依赖证据脚本的路径约束、WHEEL 选择、hash/size、成员和 RECORD 校验逻辑。命令记录使用本树私有 `build/d1-uv-cache`、`UV_LINK_MODE=copy`、禁止解释器下载；`.venv`/`node_modules` 是本树实际目录，非符号链接。03 原输出明确新建 `.venv`，其配置不包含系统 site-packages；只共用只读受管 Python 解释器。跨平台锁 23 项与当前主机按 marker 安装 19 项相容。

独立静态读取八库本轮下载的 wheel：SHA/size 对应实际锁，**391 个 wheel 成员与安装文件逐字一致**，未发现差异；许可证文件存在且与 wheel/记录 SHA 相符。负责人 08 原始结果另提供 **417 项 RECORD hash/size** 校验通过；审查者检查实现与结果，未自行重跑该脚本。

许可按实际 metadata/classifier/文件记录：pyshacl Apache 2.0、pyparsing MIT、rdflib BSD-3-Clause、owlrl W3C-20150513、prettytable BSD-3-Clause、wcwidth MIT classifier + LICENSE（表达式字段为空）、html5rdf MIT classifier + LICENSE、packaging Apache-2.0 OR BSD-2-Clause。记录未把缺失表达式伪装为存在，也不代替法律许可意见。

证据脚本只导入第三方库，实际路径约束到本树 `.venv`。有限样例涵盖 pyparsing、html5rdf、owlrl、pyshacl 一正一负、PrettyTable、Unicode 宽度与 packaging。没有 import OntoLearn、调用 I05 reason/probe、写 Store/Job 或注册能力。wheel 首次下载与后续复用均核 exact 锁 hash/size；复用的是本 D1 已下载文件，不是他树环境或未批准字节。

## 原始验证终态与失败处置

以下是负责人实际运行、审查者读取原始 command/stdout/stderr 后确认的证据，不是审查者重新执行的矩阵：

| 编号 | 结果与边界 |
| --- | --- |
| 01–03 | 新解析、独立 npm 安装、新建 venv frozen 安装均退出 0；02 保留 deprecated 警告。 |
| 04 | 首轮依赖烟测退出 1：Turtle 将前缀冒号误写为点号。原 stderr 及当时完整脚本快照保留，未声称此轮成功。 |
| 05 | 首轮 check 退出 1：新增证据脚本 E501。首失败原件保留。 |
| 06 | source check 退出 0，12 个源归档匹配。 |
| 07 | 修正换行后的正常全量 check 退出 0；lint/format/types/build 通过，630 TS、1052 Python 通过，零 skip。构建记录不表示启动 Electron。 |
| 08 | 修正 Turtle 后依赖烟测退出 0；完整 stdout 与最终 dependency-evidence.json 逐字相同，stderr 空。 |
| 09–11 | frozen check、lock check、pip check 均退出 0；19 项环境无需变化，23 项锁可核，安装依赖相容。 |
| 12–13 | 最终证据脚本 ruff lint/format 退出 0；补足 07 后证据 helper 小改动的针对性验证。 |
| 14–16 | 主稿格式、当时 git diff 空白检查及最终主稿格式检查均退出 0。16 对应最终 JSON 封装链接版。 |

04 脚本快照与最终 helper 的相关变化为修复 Turtle 输入，以及对本轮已下载不可变 wheel 先读取再重新校验的复用逻辑；没有产品语义变化。07 后产品两文件 hash 未变，因此无需重复无变化全套矩阵。失败→修正→重跑链条可追溯，没有把旧失败覆盖成通过。最终 JSON patch 封装经独立字节比较成立。

## 最终意见与未验门槛

本轮无 P1/P2/P3 未关闭事项，无需修改两文件。依赖 A 的 exact 声明、完整锁闭包/extra/markers/artifacts、独立环境及现有验证证据满足本次 D1 内审范围。

仍须总控核验精确候选后另行批准固定提交接收；本报告不授权复制未批实现或改变唯一维护权。D2 构建/入口、I05 probe 合同与 assets/oracle、七 canonical quality 的源/包身份和真实计算矩阵、完整 source-package、PyInstaller data/metadata/license 收集、B1/目标平台/native、指定同版 ZCode/MiniMax 双新审、CI/正常合并及父范围验收仍未由 D1 完成。本轮未 push/PR/merge，未恢复 blocked Goal。
