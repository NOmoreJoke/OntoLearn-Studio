# 第四次诊断新输入：构建前独立定点审查

2026-10-22。结论：未发现阻断当前候选按新授权执行唯一第四次新输入构建的问题。真实授权／两文件采用／锁产品链成立，九源、完整12及锁八叶差异均核同。此为采用与静态前置审查；尚无本轮构建结果或诊断输出，不是指定双外审、native、N0或运行通过。

## 授权、供方与采用

已全文读取 `authorization.md.raw`，4089B／SHA-256 `434f4ee43a94912f0e74d500bc05c425edc421bf030018a3c1df652bf59503df`；工作字节与真实 `7b58202ce147c25ba31a45d61a066166b80ca57e` Git blob完全相同。该ref父级为113e324d7420ec06c885ca2d8a634e68f2d85c9e，仅新增本授权原件。

实际ref链为7b58202 → `b436cd614b08f2b9587dee5e3285ef4efb231e82` → `d87015bd1cb5196b9fde4b0153798602b52d60d9`。采用提交只改core_test和TS test两路径；产品提交只改toolchain-lock.json，没有wholecommit采用供方或夹带构建实现修改。

`provider-handoff.json.raw` 为3153B／`54d6ecc818cc4de89ab4cf373767c48d58f8760946a438d11da1afb61c2d2827`，逐字节等9410a89c27dde528e4faf4480e39c01ad4f633f1中指定handoff blob。其allNineSourcePins去除sameAsPrior说明字段后，与当前锁九pin／完整12前九项逐项相同。handoff本身只是路由材料、声明不授adoption/build/run；本次构建权限来自7b58202，不能由handoff字段自行扩大。

独立逐Git blob比较fc6237e8cad1a4043d46a1c7198439f1da06ad67和b59239f9c1ec2774c7922f95dfc67db4dc8754e8：仅以下两件改变，其余七件逐字节不变；当前工作九源全部等fc，两个adoption blob亦等fc原字节。

- core_test：30037B／`4cec7d67ba66fdf47d0ae26ba056372dc437e67ac076e768a548c334bd260319`。实际Git diff只给make_owner增加可空case_label、失败条件下有界 `%.18s` label／status／owner_nonzero诊断，并给原五处调用加固定label。原nl_fixture_owner_create调用、cleanup与require断言保持；没有根路径／指针地址输出或额外生产API调用。
- TS test：8424B／`4552db106b86a8a8a80b9fcb7b55292a1696f69b72a20bd97bdfaae2bdc104ce`。只移除提前let，将原赋值点改为const声明；mock安装、owner初始化、root／file调用顺序保持。没有改测试断言。

provider的currentDeltaOnly=TS／cpp sameAsPrior描述相对其前一I06提交；本次T03相对b592实际采用两件，二者不混淆。旧I06失败及首次native owner-create根因未知继续保留；本审没有运行或证明新的诊断已出现。

## 完整12和八字段锁差异

`approved-input-manifest.json`：2544B／`cd3508184b5acdaad1f3ffc5e8a67ba65c9cbb9d86c05e84ef26f90c162f4c93`。12个路径唯一，本审逐项只读计算工作文件bytes／SHA，全部吻合；auth/adoption/product/source/process各ref与真实对象及供方原件匹配。

当前锁10474B／`8f3045ebf9b2e8b61757669aee9564319ce6a1f5fc5e92f4047aa8036732693f`，工作字节等d87015产品blob。相对113e旧锁，拒重复键的严格JSON解析和递归全对象比较，实际恰八叶：source.ref改fc；source.files[6]的bytes／SHA改新core_test；source.files[8]的bytes／SHA改新TS test；source.approval.reference、Darwin toolchain approval.reference、Darwin/core execution.reference三项均改为真实7b58202授权。三approved保持true，其余API3／contract／staticassembly审批、七源pin、供应descriptor、selector、environment、limits及执行权限全部不变，Node／Windows／addon／fixture-addon未扩大。

CMake19815B／`f2b5522b92c5dfc9724b95c35b876ce5015a4955385f614a6da20fb9bce57645`，driver30056B／`ca4ef93024762ae5dfd3dc95133f8ab28ae2e63048af0b3a658bfeb98f62045c`冻结。由实际身份与全锁差异确认本轮未改算法、CLI或命令计划；不重复重审旧实现。

## 已有静态证据与预算

已读 `static-validation.json`（625B／`db87612a038e3b5c88ec120af72c416edc30025f1271d82438f752c72b1817be`）：锁JSON解析通过、原Prettier回执exit0；完整stdout66B为通过信息，stderr0B。本审亦独立解析新锁。未变driver的既有Node --check证据沿用，本次未重跑。授权转述的供方637TS／1052Python／native跳过等既有check，不是T03本次执行或本审新验证；不将skip写成native pass。

`authorization-receipt.json`保留owner已全文读取AGENTS/common的路径／摘要及前树clean观察；本审核小receipt，不将其冒称自己新增重读了长规则或供应材料。

`read-and-record-plan.json`：1776B／`23cb79f00bf34d2f058e0c609dfaf989746a260beb667cde8b960005e952f487`。独立核算：55068578800+17755667816+134217728=72958464344B，低于80GiB=85899345920B，余12940881576B；独立供应旧账9745727085B不重置，combined声明82704191429B／guard95645073005B。源净增331−36=295B，小Git／静态读取由新128MiB预付承接。

实体256632+85544=342176，小于400000。metadata从根保守1328343带入，加171088+2000+15000+15000+10000+15000=1556431，小于1800000，余243569。原超255／关闭界、既有预留及其它消费保留，不自行释放。字节和记录均是声明上界／预付，actual OS/compiler/loader IO仍未知；不是性能实测。

本审主读取为12工作文件、九源新旧18个Git blob、两个adoption blob、授权／provider／lock等少量Git对象及小JSON/patch/双流。保守逻辑访问上界256，小于本审1000预留；累计应用读取保守小于1MiB，小于4MiB上界，计入preflight2000和128MiB。未读取42772映射、SDK／供应实体或I06长审，没有实体pin实验。

## 后续窗口边界

owner固定新process HEAD与完整12后，可按新授权直接一次原driver CLI，不需为纯收件再等待根确认。原13命令、parallel2、每命令600000ms、shell:false、固定DEVELOPER_DIR和绝对供方维持；只configure／try_compile编译链接及两目标构建。指纹／供应不匹配须保原件回报，失败不自动第五次，不替换工具。

本审只新建此报告，没有修改产品或他人证据；未运行driver、verify-only、工具探针、测试、native、GUI/HMR、桌面或付费服务。无try_run、CTest或任何产物运行授权；成功也仅built-unverified/NOT_RUN。实际新digest、产物、诊断符号／依赖差异和费用须后验独审，selected linker／runtime、目标OS、父N0及外审／CI门不得提前关闭。
