# EXCL fixture 新输入：构建前独立定点审查

2026-10-22。结论：未发现阻断当前固定候选执行授权内唯一第三次新输入构建的问题。真实授权／单文件采用／锁产品 ref 链成立，完整 12 项身份相符，锁实际恰六叶字段变化。此结论只接受采用与构建前窄审批，不代表新源码已编译、EXCL 的文件系统行为已实测或 N0 通过；本审没有 dispatch 构建。

## 真实授权与单文件采用

已全文读取 `authorization.md.raw`：5330B／SHA-256 `93e984634949b4351c39917bb3d259d7709b7645c2ddce5345477f0b0d6f5bbc`，其工作字节与真实授权提交 `a5849a47abadee1e27cae1270bbbd213f3e1c0aa` 的 Git blob 完全相同。该提交父级 a3afc5c85d740ea99d2397544259aa56de8fd654，仅新增该授权原件。

实际 Git 链为 a5849a → `e4dc6ec726481f6b966cd82344ccdc4975591e46`（只采用 location_core_test.cc）→ `4e4af36de8353fd72f9c43c14001992a1e936060`（只改 toolchain-lock.json）。没有 wholecommit 采用 I06。

独立逐 Git blob 比对 b59239f9c1ec2774c7922f95dfc67db4dc8754e8 与旧 b1c54c3de840e657aba07906587681f6415085d6 九路径：除 core_test 外，其余八项逐字节相同；当前工作九文件均与 b592 各自 blob 相同。采用提交中的 core_test 也逐字节等 b592：29706B／`f1684029430f28918fd4caa062eb8d250f97d5d34aa3ab65c517e44954525037`。

实际源 diff 恰两 hunk：新增 `<sys/stdio.h>`；fixture rename_root 中将 `rename(path,moved)` 改为 `renamex_np(path,moved,RENAME_EXCL)`。没有其它源差异。该字节采用符合授权，具体 SDK 声明／可用性沿既有 I06/根证据；本审未重读 SDK 或做编译、链接、文件系统实验，不能提前声称新符号已解析或不覆盖行为已通过。

## 完整 12 与六字段锁差异

`approved-input-manifest.json`：2478B／`f33fccff21b5a3d9404396518e72613fda75a6cb4a3c921b42049bb8d7dadf06`。其 12 路径唯一；本次只读计算全部当前工作文件 bytes／SHA，12 项全部吻合，前九项与锁 source.files 逐项相等。清单中的真实 auth、adoption、product、source ref 与上述 Git 对象一致。

锁当前 bytes 与 4e4af36 产品 blob 相同，10474B／`b5f121b76da2c216809cf69cc98815c31a1f990dc61ec21cadc1a89a316e8215`。相对第二次固定输入 b65751963a8c1f0c35e6ef680e816a99c4026e24，严格 JSON 解析（拒重复键）及递归全对象比较，实际只有：

1. source.ref：b1c → b592。
2. source.files[6].bytes：29666 → 29706。
3. source.files[6].sha256：7d0965… → f1684029…。
4. source.approval.reference：ac37 → a5849a。
5. toolchains.darwin-arm64.approval.reference：228815 → a5849a。
6. execution.darwin-arm64.core.reference：228815 → a5849a。

后三个 ref 均为上述真实新授权。approved 值、API3、旧 contract／bindingMinimum／testAssembly 审批、八源 pins、全部供方 inventory descriptor／环境及其余字段均不变。Node／Windows／addon／fixture-addon 权限未扩大。

CMake 19815B／`f2b5522b92c5dfc9724b95c35b876ce5015a4955385f614a6da20fb9bce57645`、driver 30056B／`ca4ef93024762ae5dfd3dc95133f8ab28ae2e63048af0b3a658bfeb98f62045c` 保持冻结。由原实现身份及此次锁全差异可确认未夹带 CLI、命令规划、环境、R5 或 timeout 放宽；本审不重审旧代码或运行前门。

## 静态记录及预算

已读取 `static-validation.json`（922B／`81bc88c05b4bb6e14b9b898f549cbc89cc156cbb57ddb1521d81acbeb3e95f68`）及完整双流：原 Node --check 与锁 Prettier 回执均 exit 0；Node 双流为空，Prettier stdout 66B 为通过信息、stderr 为空。这是已保存静态检查证据，本审没有重跑。测试仍 NOT_RUN。

`read-and-record-plan.json`：1717B／`b58995c5888391ee81faa9c3e9c8d880737961786e4d494c6bce89c417e947d5`。独立核算：37178693256 + 17755667816 + 134217728 = 55068578800B，低于本授权 64GiB（68719476736B），余13650897936B；原供应9745727085B独账保留，合声明64814305885B，组合guard78465203821B。源 test 增40B及小锁／Git读取由128MiB收尾预留承接，未假称源输入毫无变化。

实体171088+85544=256632，低于300000。metadata 1100255+171088+2000+15000+15000+10000=1313343，低于1500000，余186657。原1100000超255及1100287关闭界照保，不能倒写为旧窗口从未超界。`initial-plan-correction.json` 保留最初把总和误写1318343触发 AssertionError、在依赖工作前纠正的历史；本审核当前正确算式，不删除该失败。上述是声明上界／预留，不是 OS、compiler、loader I/O 实测。

本审实际主读取为完整12小文件、九源新旧18个 Git blob及有限 ref／锁／单文件采用比对、小 JSON/patch/双流；保守逻辑访问上界256，小于本审1000预留，应用读取保守小于1MiB，小于4MiB缓冲界，并计入 prebuild2000／128MiB预付。未读42772清单／sidecar映射、供应实体或大材料，没有新增实体 pin 验证。

## 执行前后边界

owner 可按授权固定新完整输入 process HEAD 后直接执行唯一原 CLI：`/usr/local/bin/node scripts/build-native-location.mjs --target darwin-arm64 --component core --build`。仍原13命令、每命令600000ms、parallel2、shell:false、固定DEVELOPER_DIR和绝对供方 pin，只允许 configure／try_compile 编译链接并构建两目标，不加 try_run、CTest、产物／child／native／addon／Electron 执行，不自动第四次构建。R5 意图／原始双流／真实PID／首因及失败停止要求保持。

本审只新建此报告，没有修改产品、九源、他人证据或旧报告，未运行构建、verify-only、工具探针或测试。第三次实际结果、renamex_np 新符号解析、真实新增依赖及具体预算须后验审查；旧两轮产物和全部失败保留，最终 selected linker／archive／runtime 闭包仍不得提前关闭。无额外 delta 时，不需为常规成功回执再向根请求同一窗口确认。
