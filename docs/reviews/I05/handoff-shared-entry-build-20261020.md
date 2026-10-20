# I05 → I04：共享入口与构建脚本责任交接

本记录只交接文件责任和既有实现的保留要求。来源为总控会话 `01a154de-843b-7a00-8a80-51ba1c0aebce` 本轮明确指令；不是完整 I05 恢复、语义能力发布、接口批准或验收完成。总控通知 I03 经 PR4 合并至 develop `e45e6038b5e0f8f4adc69ed55aafccd75b3d3500`，当时 Windows 合并后 CI 仍运行；本线未将此通知扩写为全部 CI 或 I04 已启动的独立核验。

## 生效责任

I04 实际启动后，由 I04 唯一维护：

- `packages/engine/src/ontolearn_engine/__main__.py` 与 `protocol.py` 的常驻 / v2 入口和协议接线。
- `packages/engine/entrypoint.py` 的普通运行入口与 CLI 分派。
- `scripts/build-engine.mjs` 的构建入口及 v2 规范资源打包接线。

I05 继续维护 Python 依赖 / `uv.lock`、新语义模块、专用测试 / probe / 验证、语义依赖与许可证清单，以及之后基于真实 I04 的正式语义集成。`scripts/i05-build-inventory.py` 和 native license provenance 仍为 I05 负责的专用清单来源。期间 I05 不并行修改上述共享入口与构建脚本；需要变化时向总控 / I04 交精确需求，由唯一负责人协调落地。

## 精确来源

唯一 I05 worktree：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-semantic-validation`；分支 `feature/I05-semantic-validation`。交接前 HEAD 为 `929ebffa837cdde5872dc5ab93868e4638630814`，v4 实施提交 `2a8dcad9f9036ae49b96282d8bf64f279846b14e`。下列工作文件与该 HEAD 的提交字节完全相同，也与 `independent-v4.json` 中对应来源哈希相同。

| 文件 | 字节数 | SHA-256 | Git blob OID |
| --- | ---: | --- | --- |
| `packages/engine/entrypoint.py` | 530 | `9e6f363dab3806d37835f5ed1b2b4a919955cadcee33a55eaa600f751ed9a34f` | `c8fd52e1a82c8b0dce3e4ded173b5d6f4bb94232` |
| `scripts/build-engine.mjs` | 1457 | `488d216919378e9284717640367b98426a0c9054ff918cecc1da9c577bcc3818` | `e6238eb7eb01e363ea8273b2b1709ce3c001c7b4` |

可从本地提交读取精确内容，无需提前推送：

```sh
git show 929ebffa837cdde5872dc5ab93868e4638630814:packages/engine/entrypoint.py
git show 929ebffa837cdde5872dc5ab93868e4638630814:scripts/build-engine.mjs
```

机器可读交接见同名 JSON。它记录文件字节哈希和责任，不把旧 v4 二进制或测量当成新 I04 集成证据。

## 入口必须承接的行为

- 显式 `--semantic-probe` 分支导入 `ontolearn_engine.semantic_probe.main`，移除该分派参数后传递剩余 CLI 参数。保留真实 suite / reject / measure / startup / fresh 路径；其中 fresh 的 `firstComplete` / `warmComplete` JSONL 与立即 flush 是现有首次结果测量的接口。
- 显式 `--storage-probe` 分支继续调用真实 `storage_probe.main` 并传递剩余参数，保留 S1 包内验证能力。
- 普通运行入口由 I04 升级为实际常驻 v2。两个专用 probe 分支仍须可直接无窗口执行，不依赖产品会话握手、启动 worker / 桌面或自动进入常驻 stdin 循环。导入普通 main 的位置可由 I04 为此调整，保留分派行为和既有真实 probe 模块即可。
- `--semantic-probe` 是合成数据 CLI 验证，不是公共业务方法或产品 capability 注册。当前 v4 校验器里 health 能力恰为 `["health"]` 的断言属于旧基线证据；I05 后续按 I04 实际获准 registry 调整专用验证，不要求新常驻基线退回旧声明，也不预先注册语义能力。

## 构建必须承接的处理

| 当前处理 | 承接要求与理由 |
| --- | --- |
| 先以 `uv run --frozen python scripts/i05-build-inventory.py` 生成清单；错误或非零退出即停止 | 保持锁依赖版本 / 许可 / native provenance 不完整时的失败处理；不能跳过清单后继续产出看似合格的包。 |
| PyInstaller `--collect-all rdflib / pyshacl / owlrl / html5rdf` | 保留真实插件、动态导入及数据资源收集，尤其 pySHACL assets、RDFLib parser/store/SPARQL 和固定 Turtle `SinkParser` 路径；不能仅因静态 import 成功缩成不完整模块集合。 |
| `--collect-data ontolearn_engine` | 保留现有 engine 数据，例如 `invalidation-v2.json`。该选项不自动涵盖 engine 包目录外的 I03 v2 规范资源；新增规范接线由 I04 明确实现并实际校验。 |
| `--copy-metadata rdflib`、`--copy-metadata pyparsing`、`--recursive-copy-metadata pyshacl` | 保留运行时版本 / 依赖元数据及 pySHACL 传递依赖元数据。 |
| 将绝对 `build/i05-inventory` 以 `--add-data` 置入 `i05-inventory` | 保留包内 `_internal/i05-inventory`：完整锁依赖 / 角色 / entry points / wheel 许可、CPython LICENSE、native-runtime 来源元数据 / 原字节上游 PYTHON 清单 / native 许可与哈希。现有验证按这些真实路径核对。 |
| `uv run --frozen pyinstaller --noconfirm --clean --onedir`，固定 entrypoint、name / dist / work / spec 路径 | 保留可重复构建与现有产物定位，路径调整须同步 I05 专用 verifier；不会自动启动产物。 |
| `cwd=root`、`shell=false`、继承环境并将 `PYINSTALLER_CONFIG_DIR` 指向本 worktree 的 `build/pyinstaller-cache` | 保持路径确定、shell 参数边界及独立构建缓存，不能链接其他线的可变环境。 |
| 子进程错误 / 退出码向上返回 | 保持失败可见，不能把缺依赖、清单失败或 PyInstaller 失败写成成功。 |

native 来源当前只匹配实际 PBS CPython 3.12.12 / macOS arm64；官方 full / stripped / 本机库的内容段匹配、上游缺失 zlib-ng 许可路径及实际 system-libz 的例外均已有记录。不同平台 / 运行时仍需实际来源匹配，不能复制本机记录就声称跨平台通过；也不能删除失败检查来完成接线。I05 后续负责相应语义打包证据，I04 按实际采用的运行时提出精确需求。

## 合并顺序与冲突判断

没有新增文件责任冲突：共享入口 / 构建脚本归 I04 唯一维护，语义 / 依赖 / 专用清单验证归 I05。现有两个分支会同时在这些文件留下不同职责的改动，需在真实基线同步时合并行为，不能整文件覆盖。

I05 独立分支尚未推送 / 合并。I04 不能只复制本记录的旧 `build-engine.mjs` 到缺少 `pyshacl` 锁依赖、清单生成器、许可来源的基线，便假定 hooks 可独立运行。I04 先在其实际已批准基线上完成 v2 构建接线；随后 I05 同步真实 I04 基线时，将本表语义 hooks 与 I04 新规范资源处理合并承接。若产生冲突，I05 保留冲突信息并向唯一负责人提交精确需求，由 I04 / 总控协调合并内容，不并行重写这两份脚本。

I05 完整运行时 / 存储 / 任务 / 选中结果 / 取消 / 错误 / 包内 / 窗口联验仍依赖实际 I04；之后仍须新基线验证、指定双方新全范围审查与原 PR / CI / 合并门槛。此交接没有恢复完整 Goal、改变 v4 实现、rebase、重跑不变测试、启动 GUI、push 或公开语义能力。
