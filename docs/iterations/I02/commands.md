# I02 实际验证命令

工作目录均为 `/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio`；Node v24.15.0、npm 11.12.1、uv 0.11.12；平台详细值见 evidence/package-manifest.json。

```sh
npm run check
npm run verify:sources
I02_EVIDENCE=docs/iterations/I02/evidence/build-matrix.json npm run test:e2e
npm run package:dir
ONTOLEARN_PACKAGED_EXECUTABLE="$PWD/release/mac-arm64/OntoLearn Studio.app/Contents/MacOS/OntoLearn Studio" I02_EVIDENCE=docs/iterations/I02/evidence/packaged-matrix.json npm run test:e2e
```

开发模式另开 `npm run dev`，确认固定 127.0.0.1:5173 启动后运行：

```sh
ELECTRON_RENDERER_URL=http://127.0.0.1:5173 I02_HMR=1 I02_EVIDENCE=docs/iterations/I02/evidence/development-matrix.json npx playwright test tests/e2e/csp-lifecycle.spec.ts
```

HMR 探针临时修改两份未变更的 renderer 源文件并 finally 恢复原始 Buffer；运行后 `git diff -- apps/desktop/src/renderer/src/App.tsx apps/desktop/src/renderer/src/style.css` 必须为空。审查者仅可运行默认测试；只读审查期间不要设置 I02_HMR=1。

普通页面矩阵由 Playwright 驱动实际应用。真正无响应测试另启同一 executable，用临时独立 user-data-dir；短暂主进程 inspector 装入本仓库 test-only native-recovery.cjs，关闭 inspector 后才执行真实 renderer crash/无限循环/input；renderer 始终未附加 CDP，未注入 Playwright 的 disable-hang-monitor。驱动只替代对话框的用户选择并记录它，不合成 render-process-gone/unresponsive，也不改 app.asar/main。

运行的原始日志、native 事件和提示、计算样式、enforce violation、HTTP 接收端请求、isPackaged/锁定 Electron 版本、构建与 asar 字节一致性分别保存在 evidence。自动化测试不是签名/安装器/干净设备/生产发布证据；I04 job 重连与真实项目 UI 尚未实现。
