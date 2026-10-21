# T05 私有组件 headless 交互记录

固定源 `2fcd36b915b190963a1d89d608e896da1a15284e`；完整状态见 `status.md`，机器可读来源、运行和归档清单见 `browser-ui-evidence.json`。

## 发现与修复

真实浏览器先复现：必填约束成功生成草稿后，将版本改为1.2再提交，虽显示错误，原版本1的草稿仍留在下方。现将准备结果及错误与生成时的全部表单输入绑定；任一输入、条件/结论增删或启停变化后，不展示旧草稿/旧错误。失败生成替换旧准备结果，表单输入不丢失。结果刷新不改写草稿，项目隔离保持。

独立reviewer只读审查实现/夹具及前后原反例通过；没有接管浏览器或重复全检查。完整`npm run check`退出0：635 TS / 1200 Python（Python38.58s）。夹具另经显式strict TypeScript检查，退出0。

## 实际交互范围

Playwright CLI 0.1.22，显式headless Chrome for Testing151.0.7922.34；viewport1280×900。使用本地file夹具，无测试HTTP服务器、Electron、App/IPC/引擎或Store。夹具醒目标明synthetic props；不把合成检查状态、结果和问题当实际领域输出。

- 五模板分别真实填表并核对生成JSON；maxCount=0保留，1.5拒绝，范围typed literal保留。只证明草稿序列化，不证明约束有效或SHACL执行。
- 编辑即隐藏旧草稿、非法版本不保留旧输出、增加条件隐藏旧稿；规则类型/属性/比较合取及同规则多结论、启停草稿正确生成。
- 合成的同数量错集合正确显示缺少001/多出002；过期、不支持、未执行及无依据的显示保持区别。定位只证明回调target准确，不证明App导航。
- 结果props刷新保留草稿/样本/预期；project B排除迟到的project A观察并重置本页输入；未接线执行按钮和含推导范围仍禁用。真实项目服务的保存/切换确认另待联验。

共18个有名DOM断言由CLI实际执行，原命令、断言输出和快照均保留。两张全页截图不是viewport尺寸；仅用于查看私有组件布局，不是产品截图或原生验收。

## 环境与首失败保留

配置`headless:true`、`chromiumSandbox:true`；已读取实际自有browser PID45677的argv，无`--no-sandbox`/`--disable-hang-monitor`，收据含完整自有父子进程。这里只证明配置、启动与参数；没有把它升级为OS sandbox或Electron原生证据。初次探测发现Playwright默认关闭hang monitor，已关该自有探测会话并显式移除默认参数后重新开独立会话；未将原探测算作通过。

其他初始失败均保留：技能wrapper不可直接执行，改用bash；CLI默认拒绝file导航，关闭原会话后使用显式本会话本地夹具配置；初始IIFE未替换React的NODE_ENV而抛process未定义，已在独立build helper修正。最终新会话console为0错误/0警告，未列出远程HTTP请求；这不否认工具包解析可能访问npm注册表，也不声称全机器离线。自有CLI会话已明确关闭，PID45676/45677实查消失，没有结束他人进程。

CLI原日志含历史非UTF-8字节：保持原字节归档，文本判读使用替换解码，不重写原件。证据归档脚本首次严格解码失败，随后只调整读法；源文件/受测实现未因此改变。

## 恢复和重现

`node tests/fixtures/quality/build-browser-harness.mjs`只构建IIFE和本地HTML，不自动打开浏览器。运行CLI须显式给独立会话、经核实的headless executable及配置；归档内保存本次实际配置、runtime路径/版本/hash、所有执行源码、构建产物、CLI过程和截图。按snapshot重新取得refs，依原CLI日志的真实填表/断言步骤重现；不得复用旧refs操作其他会话。

原件尚无CI artifact归档，故将本次有界原件无损打包在`evidence/browser-ui-draft-recovery.tar.gz`，外部JSON逐成员记录长度/hash；已逐成员解包字节复核。它与R1/R2原始运行归档分开，不能替代正式双范围、真实parse/SHACL/推理、保存失效/撤回/历史认证、指定双审/CI或父功能验收。
