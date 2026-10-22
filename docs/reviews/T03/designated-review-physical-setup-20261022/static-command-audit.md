只读静态核对完成，三棵树 HEAD 均符合指定值；本轮未安装依赖、未执行产品/测试/编译、未写文件或提交。三树受审配置字节相同，除 `scripts/build-engine.mjs` 与引擎依赖；工作区均仅见 `AGENTS.md` 为已存在的修改。

以下简称：

- **M**：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-mapping-S1-zcode-review-3031941`
- **S**：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-source-selection-zcode-review-8c904b5`
- **P**：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-profile-D2-zcode-review-a4d1457`

三树 `package.json:13-28`、desktop/contracts package、Playwright/Vitest config、builder 配置及三个 e2e spec 的 Git blob 一致；实际工作文件抽查哈希也一致。

### 正常命令的实际调用

**`npm run check`**，三树相同：

```text
eslint . --max-warnings 0
&& prettier --check .
&& (
  npm run typecheck --workspace @ontolearn/contracts
  && tsc --noEmit -p tsconfig.unit.json
  && npm run typecheck --workspace @ontolearn/desktop
)
&& vitest run
&& npm run build --workspace @ontolearn/desktop
&& uv run --frozen ruff check .
&& uv run --frozen ruff format --check .
&& uv run --frozen pytest
```

- Contracts/Desktop typecheck 均展开为各 workspace `tsc --noEmit -p tsconfig.json`。
- Desktop build 展开为 `electron-vite build`。
- Vitest 选取 `tests/unit/**/*.test.ts`，见 `vitest.config.mts:1-2`。
- Pytest 选取 `packages/engine/tests`，见 `pyproject.toml:16-17`。
- **不能描述为“纯静态验证”**：`tests/unit/task-runtime.test.ts:20-31,114-145` 会运行本树 Python、真实 coordinator/worker/SQLite；Python resident-runtime 测试也运行真实子进程，见 `packages/engine/tests/test_resident_runtime.py:19-40`。
- 非 GUI 正常产物包括本树 `apps/desktop/out/**`、测试临时 SQLite/markers，以及工具默认缓存。`.venv/`、`.ruff_cache/`、`.pytest_cache/`、`__pycache__/`、`out/` 等在 `.gitignore:1-14` 被忽略；忽略不代表可以跨树共享。
- `prettier --check .` 不写源码；不得误换成 `npm run format`，后者为 `prettier --write .`。

**`npm run verify:sources`**：

```text
node scripts/verify-sources.mjs
```

`scripts/verify-sources.mjs:3-9` 从脚本所在物理树读取 `docs/source-manifest.json` 及列出的原件并核 SHA-256；脚本本身无写入点。未来正常执行与本轮“不要读取 archives 载荷”的静态 setup 范围应分清。

**`npm run test:e2e`**：

```text
install-electron && playwright test
```

- `package-lock.json:2910-2923` 将 `install-electron` 映射到 Electron 包的 `install.js`。它是安装入口，不能承诺离线或无安装写入。
- `playwright.config.ts:3-8`：`tests/e2e`、workers=1、retries=0、list reporter、30 秒、失败保留 trace；没有显式 `outputDir`。
- 会直接运行真实 Electron/引擎；本命令不先 build。
- `desktop.spec.ts:9-15,61-67` 默认参数为本树绝对 `apps/desktop`，cwd 为该目录；显式 `ONTOLEARN_PACKAGED_EXECUTABLE` 才改为包内应用。
- 直接截图写到 `test-results/desktop-1280.png`、`test-results/desktop-1024.png`；`desktop.spec.ts:149`、`i04-jobs.spec.ts:238,471` 的 JSON 写到 `testInfo.outputPath(...)`。

**`npm run package:dir`**：

```text
npm run build
&& node scripts/build-engine.mjs
&& npm run package:dir --workspace @ontolearn/desktop
```

最后一步为 `electron-builder --dir --publish never`，见 `apps/desktop/package.json:8-12`。

- `apps/desktop/electron-builder.yml:3-12` 输出为本树 `release/**`，读取本树 `apps/desktop/out/**`、`build/engine/ontolearn-engine`、`packages/contracts/v2`。
- `mac.identity: null`，见该文件 `:15-17`；这是现有 unsigned 本地目录打包行为。
- 不含“运行同一样例”；包内验收是另一步。
- `scripts/verify-i04-package.py:15-77` 的正常包内验收入口参数为 `executable output`：执行包内 `--protocol-resources`、`--contract-probe`，再以 `ONTOLEARN_TEST_ENGINE=<本次包内engine>` 跑三个既有 pytest 目标。输出为新建目录中的 `resources.json`、`common-examples.json`、`runtime.stdout/.stderr/.exit`，另有临时 `i04-bundled-cwd-*`。
- 该验收脚本是**实际产品运行**，setup 阶段不能执行。

### 三组 engine build 差异

**S：`scripts/build-engine.mjs:4-49`**

```text
uv run --frozen pyinstaller --noconfirm --clean --onedir
  --collect-all rdflib
  --collect-data ontolearn_engine
  --copy-metadata rdflib
  --copy-metadata pyparsing
  --add-data <S>/packages/contracts/python/contract_v2.py:contracts/python
  --add-data <S>/packages/contracts/v2:contracts/v2
  --add-data <S>/uv.lock:provenance
  --name ontolearn-engine
  --distpath build/engine
  --workpath build/pyinstaller
  --specpath build
  packages/engine/entrypoint.py
```

cwd=S；硬设置 `PYINSTALLER_CONFIG_DIR=<S>/build/pyinstaller-cache`。本树依赖仅 `rdflib==7.6.0`，见 `packages/engine/pyproject.toml:5-8`。

**M：`scripts/build-engine.mjs:4-55`**

与 S 相同，但额外：

```text
--collect-all openpyxl
--collect-all et_xmlfile
--collect-all defusedxml
```

依赖增加 `openpyxl==3.1.5`、`et-xmlfile==2.0.0`、`defusedxml==0.7.1`，见 `packages/engine/pyproject.toml:5-11`。

**P：`scripts/build-engine.mjs:245-391`**

在 PyInstaller 前还有真实检查：

1. 读取脚本中逐项承诺的 fixedInputs，核 bytes/SHA，失败为 `ENGINE_BUILD_INPUT_CHANGED`。
2. 对 fixedInputs 和两个 writer 跑 `git diff --exit-code HEAD -- ...`，读取实际 HEAD，见 `:254-260`。
3. `uv run --frozen python -c <metadataCode>`，见 `:262-305`。
4. 写 `<P>/build/profile-d2/provenance/d2-build-inputs.json`，见 `:315,360-380`。
5. 运行 PyInstaller。

PyInstaller 相对 S 的主要参数增量：

```text
--optimize 0
--collect-all pyshacl
--collect-all owlrl
--collect-all html5rdf
```

并：

- `--copy-metadata` 八个分发：rdflib、pyshacl、pyparsing、owlrl、html5rdf、prettytable、wcwidth、packaging，见 `:223-232,336`。
- `--hidden-import` 固定 17 个 canonical module，加 prettytable/wcwidth/packaging，见 `:307-339`。
- 排除 quality.definitions、quality.planning、quality.rule_revalidation，见 `:233-237,340`。
- 增加固定 profile 输入和本次 provenance 的 `--add-data`，见 `:341-348`。
- 相同 `build/engine`、`build/pyinstaller`、`build` 和 `build/pyinstaller-cache`，见 `:349-385`。
- Python metadata 精确要求 PyInstaller `6.22.3`、engine `0.1.0`，见 `:304-305`。

**隔离的硬约束**：P 的 `:268-279` 要求 `sys.prefix.resolve() == <P>/.venv`，且实际分发文件 resolve 后仍属于 `<P>/.venv`。不能把 `UV_PROJECT_ENVIRONMENT` 指到树外共享环境，也不能用解析到外部的 `.venv` 符号链接冒充本树环境；否则 metadata subprocess 失败，被外层转成 `ENGINE_BUILD_PRECONDITION_FAILED`。缓存和 TMP 可另行隔离。

### Node/Python、默认 Mac 运行路径与环境

- 三树根 `package.json:6-7,49`：Node `>=24 <25`，npm `11.12.1`。
- 根 `pyproject.toml:4,13-14`：Python `>=3.12,<3.13`；dev requirements 为 pytest、ruff、PyInstaller；三锁头均 `requires-python="==3.12.*"`。
- **三组正常开发引擎固定使用本树 `.venv`**：`apps/desktop/src/main/engine.ts:14-23`：
  - Mac/Linux：`<tree>/.venv/bin/python -I -m ontolearn_engine`
  - Windows：`<tree>/.venv/Scripts/python.exe -I -m ontolearn_engine`
  - packaged：`<resourcesPath>/engine/ontolearn-engine`（Windows `.exe`）
- 因此即使绕开 P 打包 guard，外置 `UV_PROJECT_ENVIRONMENT` 也不能代替普通 Vitest/e2e 所需的本树 `.venv`。
- `tests/unit/task-runtime.test.ts:18,123-145` 支持 `ROOT_SOURCE_PATH` 改读另一 checkout。冻结常规回归应保持未设置，避免意外跨树。
- `ONTOLEARN_TEST_ENGINE` 可改变 Python 正常 runtime 测试的执行目标；`ONTOLEARN_PACKAGED_EXECUTABLE` 改变 e2e 应用目标。只应为本次明确的包内验收赋值。
- `ELECTRON_RENDERER_URL` 会进入 dev 页面分支，固定 dev 地址为 `127.0.0.1:5173` 且 strictPort，见 `electron.vite.config.ts:34`。
- **初始 Electron 数据没有被 worktree 自动隔离**：`desktop.spec.ts` 和 C1 初始 launch 未传 `--user-data-dir`；`main/index.ts:123` 默认 DB 为 `app.getPath('userData')/engine.sqlite`。仅设置 TMP/缓存不能证明应用数据隔离。源码未硬编码 macOS `~/Library/Application Support/...` 的最终目录名，不能静态自报实际路径。
- 引擎环境构造只继承 HOME/TMPDIR/TMP/TEMP/locale 等白名单，随后由 main 明确设置 DB、allowedProjects/testMode，见 `engine.ts:119-134`；单独在外层设 `ONTOLEARN_DB_PATH` 不会覆盖 main 给出的默认 dataPath。

### C1/I04 未改回归的权限和平台边界

**C1 不存在 `I02_NATIVE=1` 启用开关，也无 Linux-only gate。**

- `csp-lifecycle.spec.ts:9-37` 起始就跑真实 Electron，并监听本机 `127.0.0.1` 随机端口。
- `:265-302` **无条件**调用既有 `runNativeRecovery`；Mac 默认也执行。
- Native executable 从初始应用 `process.execPath` 读取，或使用本次 `ONTOLEARN_PACKAGED_EXECUTABLE`。
- 子进程参数：
  ```text
  --user-data-dir=<tmpdir>/ontolearn-i02-*
  <tree>/apps/desktop                 # 非packaged才加入
  ```
- `native-driver.ts:11,100-107` 加 `--inspect=0`，载入本树既有 `tests/e2e/native-recovery.cjs`，故障前关闭 main inspector。
- `I02_NATIVE_EVIDENCE` 是内部输出路径，非启用开关；输出 `native.json`。`I02_EVIDENCE` 可指定 C1 总 JSON，见 `csp-lifecycle.spec.ts:308-317`。
- `native-recovery.cjs:44-87` 真实 crash/hang，需要可见窗口与焦点；该历史 hook 自动回应恢复选择。不能将该基线测试的通过宣传成所有原生提示均未经 stub 的真实人工选择证据。
- **`I02_HMR=1` 明确禁止**：仅 development 分支触发，临时改 `style.css` 与 `App.tsx` 后恢复，见 `csp-lifecycle.spec.ts:75-110`；冻结 AGENTS `:51` 明文禁止。

**I04：**

- reload：需 `I04_TEST_FIXTURE`，否则 skip，见 `i04-jobs.spec.ts:21-29`。
- coordinator exit：还需 Linux，见 `:97-109`；使用 `ps`、`/proc/<pid>/cmdline` 并 SIGKILL 识别到的唯一自有 engine，见 `:169-179`。
- real native：还需 Linux 且 `I04_NATIVE_ISOLATED=1`，见 `:316-329`；要求隔离 Linux display/openbox/xdotool/fresh fixture。Mac 正常 skip 此项。
- I04 real-native 的默认 executable 字面值是 `<tree>/node_modules/electron/dist/electron`；仅 Linux gate 下使用，不能拿它作为 Mac 默认执行路径。
- `scripts/prepare-i04-fixture.py:14-22,99-101` 参数为新目录，创建该目录内 `engine.sqlite`、`fixture.json`；它执行真实 JobStore，setup 不得运行。
- main 要求 fixture 绝对路径、命令参数与 `I04_TEST_FIXTURE` 完全相等，见 `main/index.ts:93-118`。
- native 临时写 `<tmpdir>/i04-native-*/native.cjs`、`evidence.json`；验证 JSON 和附件写 Playwright outputPath，见 `i04-jobs.spec.ts:322-329,471-498`。

上述是**未改的普通基线回归入口**，不应被泛化为 T03-N0 未签 native/producer/caller 专票或被拒资源研究。未来正常回归按最新授权执行，由 root 内部串行协调 GUI、焦点、端口、应用数据与自有 PID；不需再次向用户申请桌面时段。本轮 setup 仍不执行它们。当前 AGENTS `:56-58,66,99` 支持这个区分。

### 已有首失败记录及证据限制

- M `docs/reviews/T03/check-first.txt:80-94`：历史首次 check 在 Ruff 处因 `test_mapping_source.py:68:101` 的 E501 失败；更早 lint/format/types/Vitest/build 已完成。`validation.json:38-49` 另外记录后续 check exit0。这是旧树历史，不是新审查树实测。
- S `docs/reviews/T03/source-selection/check-first.txt:6-13`：历史首次失败为 unit test 第331行 `prefer-const`；`npm-ci-first.txt:5-10` 是成功安装历史，不能误报安装失败。
- P 未发现可直接当作这棵新审查树“四个正常命令首失败”的当前执行证据；未读取 archive 载荷，也未运行命令补造。
- P 所读固定历史观察明确为旧 producer 观察，不能替代本次正常回归。因本任务无需重新核其载荷，未展开 archive 或调用探针。
- `.prettierignore:1-19` 与 ESLint ignores 仅覆盖既有若干输出根；新增 scratch/report 文件放到未排除位置，可能改变 `eslint .` / `prettier --check .` 的扫描范围。隔离记录应放 root 约定输出目录，不能为通过检查修改冻结配置。
- 读取时两次路径名误选（不存在的 `vitest.config.ts`；在 M 查 P 专属文档）只产生读取错误，已纠正；不构成产品验证结果。

---

### 补充：仅依赖 setup 的 lifecycle 与 editable hook 边界

本节为 root 后续要求增加的静态元数据补充；上述原报告全文保留。“本轮未写文件”描述原报告生成时点；本次后续授权仅创建本报告文件，没有安装、执行产品、改旧包或提交。

#### npm 元数据核对与受限安装方案

补查范围为上述 M 的根锁文件，以及已有开发树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-mapping` 的根 `package-lock.json` 和 `node_modules/<name>/package.json` 元数据。未读取或执行这些依赖的实现文件、install.js 或编译器。

- 根、desktop、contracts 的 package.json 均没有 preinstall/install/postinstall/prepare lifecycle；根 `test:e2e` 显式写 `install-electron && playwright test`，不能用它做“仅依赖 setup”。
- root 锁为 lockfileVersion=3；整个锁仅两个条目带 `hasInstallScript:true`：`electron-winstaller@5.4.0`（`package-lock.json:3023-3028`）和 Darwin optional 的 `fsevents@2.3.3`（`:3582-3587`）。这不是“锁文件列出所有包 scripts 原文”的保证。
- 已有 `node_modules/electron-winstaller/package.json` 元数据确认 `install: node ./script/select-7z-arch.js`；不能默认执行所有 lifecycle 都是无影响动作。
- 已有 `node_modules/fsevents/package.json` 元数据有 node-gyp build/clean 与 prepublishOnly 命令，但没有显式 install。锁的 install 标志仍须尊重；本次没有读其 binding.gyp 或 native 文件，不能进一步证明 npm 是否会落入隐式 native build。
- 锁文件**没有任何 esbuild package 条目**，已有树也没有 `node_modules/esbuild/package.json`。本候选的 Vite/electron-vite 组合锁到 Rolldown：`electron-vite@6.0.0` 的 dependency 为 `rolldown:~1.2.10`（`:2993-3005`）；已有 Rolldown 元数据版本为 `1.2.14`。因此“要跳过 esbuild 可执行自测”在本锁中没有对应的 esbuild install 入口，不应额外补装或执行 esbuild。
- 已有 Electron 元数据为 `44.9.0`，无 scripts 字段，bin 为 `electron:cli.js`、`install-electron:install.js`，与根锁 `:2910-2923` 一致。

**可行性判断**：`npm ci --ignore-scripts` 是禁用 npm lifecycle 的受限安装方式，随后只显式调用 `node <本审查树>/node_modules/electron/install.js`，可以把允许的依赖安装入口缩小到 Electron 安装脚本，而不运行根测试、build 或全部包 lifecycle。本静态元数据检查并未安装验证，也没有读 install.js 的内部调用，因此**不能仅凭 bin 映射保证该脚本绝不启动任何已下载可执行文件、绝不访问网络或所有后续工具都已可用**。要把“仅依赖且零 executable 自测”当作已证实门禁，仍需 root 在允许的依赖 setup 范围内静态核 install.js 的实际调用，再单独记录实际安装命令与结果；不能调用 Electron 应用、esbuild/Rolldown CLI、npm test/check/e2e/package 来试探。该限制是证据范围，不是新增用户批准要求。

`--ignore-scripts` 后故意跳过的 installer 可能影响后续 Windows packaging 或 optional watcher；未运行验证前只能记录“依赖解包/显式 Electron 安装”，不能声明全部正常回归或跨平台打包可运行。

#### uv frozen sync 与 engine 安装

- 根 `pyproject.toml:7-11` 声明 engine 为 workspace dependency；M 的 `uv.lock:69-71` 将 engine 锁为 `source = { editable = "packages/engine" }`，`:103` 也保留 editable dependency 元数据。
- engine 的 build backend 是 `hatchling.build`，build requirement 为 `hatchling>=1.27,<2`，见 `packages/engine/pyproject.toml:16-18`（S/P 对应末段相同 backend）。engine 是有 build-system 的源码包，不是仅复制一个第三方 wheel 就完成 editable 安装。
- `uv sync --frozen` 的 frozen 约束锁文件解析，不是“禁止 build backend hooks”的同义词。按当前 editable 锁安装 engine 时，生成 editable 安装元数据/链接需要 backend 的 editable build 流程；本任务没有执行该流程，也没有运行 hatchling 或产品 import。
- 若 setup 政策**绝对禁止 editable/backend build hooks**，则不能同时声称 engine 已按当前锁安装完成。可以先只安装可直接使用的锁定第三方 wheel，明确将 engine 标为未安装；但不能据此宣称正常 `check`/e2e ready，因为它们使用 `<tree>/.venv/bin/python -I`，真实 worker import 要求 engine 在该 `.venv` 可导入。
- 手写 `.pth`、复制源码、设置 PYTHONPATH、把 `ROOT_SOURCE_PATH` 指向其他 checkout、借用旧 `.venv` 都不是当前 frozen editable 安装的等价交付；`-I` 和现有测试的 worker 路径断言也使其中多种替代不成立。P 的 metadata guard 还要求 engine distribution 版本与分发文件位置。
- 完成 engine 安装必须明确选择：允许**限于该树 engine 的正常 Hatchling editable 安装 hook**（不运行产品/probe/测试），或提供已经批准且与固定源码对应的预构建 engine wheel，并对其 provenance/安装方式及偏离 editable 锁的影响另作记录。后者不能直接被称为本锁的未改正常安装。

本次没有查询 uv CLI help/执行 sync，故不把未核对版本的 `--no-install-*`/`--no-build` 具体开关组合写成已经验证可用的命令。root 若保持所有 build hooks 全禁，应把环境登记为“third-party-only，engine 缺口待处理”，而不是通过运行产品补探。
