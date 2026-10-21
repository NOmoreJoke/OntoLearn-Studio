# C4 冻结清单与派发输入独立 preflight

结论：**限定输入 preflight Pass，未发现阻断输入一致性的缺口；实际派发继续受环境门阻塞。** 本次不是产品全范围审查、指定模型终态或新验收，不把 boundary 的证据 Full Pass 改记为本人重跑。

## 固定对象与实际操作

只读主树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-semantic-validation`，分支 `feature/I05-semantic-validation`。固定完整 base `5f910b52c69d86a1076b2032e5d3c63e715947f3` → 冻结 head `523c478d5f39671c4ac7c1ea6997e51d3047d58e`。现场 checkout HEAD 为 `6e6e26e872c691eb75d058d05a3a51ca439b1dba`，相对冻结 head 恰为六份新增过程文件：candidate-4.json 和 round-4 的 full-review-input/input-manifest/observed-state/两份 prompt；没有冻结文件改写。`git status --short` 仅 ` M AGENTS.md`，其实际 SHA 为保护版78df。

本次写入只在本人 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-semantic-bridge/build/c4-freeze-preflight/`，未改主树、frozen status、root state 或其他聊天。没有产品测试、构建/打包、容器、GUI/CUA/native 操作，没有重建 Goal。

实际命令为系统 Python 标准库与只读 Git：`git ls-tree -rz --name-only <head>`、`git diff --name-only -z <base> <head>`、`git cat-file --batch`、`git diff --name-status <frozen> HEAD`、`git status --short`，以及文件完整 bytes/SHA/JSON 读回。可复现脚本 `preflight.py`，实际执行：

```text
python3 build/c4-freeze-preflight/preflight.py > build/c4-freeze-preflight/preflight.stdout.txt 2> build/c4-freeze-preflight/preflight.stderr.txt
```

退出码0；stderr为空。完整机器收据在 `readback.json`。首次交互式集合比对误用 Git 默认非ASCII路径转义，出现表示层不等；随即检查差集确认仅12个中文路径的quote表示，再改为NUL分隔 `-z`，完整集合相等。不是候选缺件，未改任何产品或输入。

## 清单与完整字节：通过

| 核查 | 本人实际结果 |
| --- | --- |
| candidate-4.json | 284374 B，SHA `bf68fb292647b0f7f6c3b9c78389ff7ea03cd045920b0019a2f54067ca9806b8`，与给定及 input-manifest 一致。 |
| 冻结完整变更集 | 523条名称与 base→head Git 差集精确相等；每份冻结 blob 完整 SHA 和现场文件 bytes 一致。 |
| 冻结完整跟踪集 | 除 AGENTS 外1284条与 frozen Git 跟踪集合精确相等；每份冻结 blob 完整 SHA 和现场 bytes 一致。 |
| 跟踪执行输入 | 205条全部完整 bytes 等于40c完整产品测试头、冻结523及现场工作文件；不是只核计数。另1254 raw绑定单列，不把205说成全部辅助driver。 |
| round-4 input-manifest | 四份输入的完整长度/SHA均逐项相符；full-review-input.md 为48263 B/SHA `60785d434221ac93f1cbd4be8074e8de68acc7bd10c235be2197e89d44a52ad4`。 |
| 历史原指令 | 末34007 B的 SHA为 `616916db3700cb0c7d3b5d585ee970f4811424e0e438076d7709b9deb2b90e11`，逐字等于 round-3 后缀；inputs-c1 三份完整 launch/resume/goal 文件各在其中完整出现一次，包括完整Goal及§9。 |
| 当前操作规则 | inputs-c4 的AGENTS15852 B/78df、common16317 B/ff5f、permission3729 B/3630均与各自当前源完整 bytes 相等，三份 snapshot 清单准确；前言要求优先读当前责任/安全条件，不让旧launch状态覆盖。 |

205输入的比较含源码、测试、配置、锁及验收，不代表此 preflight 已重新审查其实现。frozen AGENTS Git blob故意不是现场最新保护指南，1284清单明确排除；最新规则经snapshot另传，未stage保护文件。

## 派发范围、身份和权限：通过

全文读取 full-review-input 的本轮前言和两份 prompt；原始后缀完整读入并与原三文件/round-3逐字比较。输入明确完整原 I05/B1 base→head、真实 I04 Store/Job/bridge/native/包/许可/性能测量及全部历史意见，包含IB-1、C3-BASIS-1、I05-C3-STRING-1，**不是仅C4 string或历史发现列表**。C1原NotPass/条件Pass不继承，C2/C3开发阻断与实际指定任务0分开。FR505完整范围、Q6十二项及其他负责人未决保留，未把内部库事实或T05草稿当产品政策。

两个 prompt 固定同一根、branch、base/head和候选SHA，分别要求 ZCode GLM-5.3/最高、MiniMax M3.1-Flash/xhigh；现场模型/思考/权限/任务UUID必须实际核验，计划配置不冒充回执。两份主树唯一报告路径分别为 round-4/zcode-glm53.md 和 round-4/minimax-m31flash.md。产品/测试/依赖/配置/验收只读，固定导出与独立环境只能在各自ignored build，禁止共享可变环境、写他线/提交/推送/切分支/新Goal；禁止阅读本轮对方prompt、过程、报告或结论。历史报告可读但不得预设本轮Pass。

candidate编号4与下次真实完整双指定审查round2区分明确：candidate、input-manifest、observed-state均记录actualTaskCount=0，actual tasks/reports/dispatches为空，没有伪称UI终态或报告完成。全文要求实际读回报告并核终态，文件存在不等于完成。此处本人只核文档及目录，不进入应用验证其当前任务列表，不把“记录0”扩大成独立UI实查。

安全条件仍为未取得安全应用入口/root租约且无用户明确桌面时段，T06先排、需新实际预约；full access不解除桌面/只读门，Mac禁Electron/e2e/native/HMR/凭据/GUI/当前桌面，Linux既有证据仅可读且不冒充亲测。无push/PR/实际CI/正常merge/远端核验仍是记录的未完成项；本人未访问GitHub或CI实查，不把输入前置准备当已派发，也未自行开启应用。

## process追加、未来责任：通过

candidate的processAppendPolicy明确允许候选清单、派发/权限/所有权收据、报告等可识别纯过程追加；禁止改写冻结blob、205 tracked执行输入或1254 raw成员，产品/测试/配置/锁/验收/base变化必须新候选与双方全新完整审查。前言要求查固定SHA和当前责任，并将旧launch责任降为历史来源，因此以后root的纯所有权收据可独立记录，不自动改变受审源或授予更宽写权。

jsonl与task-presentation两个offer原字节仍分别为SHA089ef960…、aa23b9d7…，都明确尚未生效、独立接收和登记门。前言单列jsonl待门，task-presentation并未列成已生效owner；后者完整offer已在1284冻结资料内实核。未出现从jsonl接收推定另一个path接收、T01可采用未批I05或自动收回写权的授权。旧C4只读build及先停WIP保全后root exact-return条件继续保留。本preflight不代root或receiver完成交接。

## boundary原审计与清单绑定：通过，未重复1254审计

全文读取 seal-audit/report.md：10928 B，SHA `fe76a48e8fe0fe8a9cd0351eee1c3642e94d8e51c38afd46dd30fc310753bf68`，明确Full Pass仅限证据真伪、完整性和归属，不替代指定双审/CI/发布。本次实核其audit-manifest索引29份审计脚本/结果/原报告快照的完整长度和SHA均相符，copy-receipt绑定索引SHA `f62ec16a656596523201b53689c081e0132a2c0679d1ee1dfdd4d85dfe3b39c3`，没有丢其原观察器失败记录。

当前原证据manifest与audited-evidence-manifest完整 bytes 一致，SHA `b5c4bb3a8a5cd2a5cb401da71db71aefe77a791058478cd044615e7cab6396cd`；candidate、audit-bindings及原manifest的产品1a/测试40c/1254成员绑定一致。仅重新hash压缩archive6516119 B，SHA `eae749d05ac61b9cc726626f008507b3484d1ba8b1980f9f7a33eb0f51871acc`，与三端一致；没有展开1254成员重新审计payload/包/native、执行boundary脚本或重做其来源核验。其完整审计结论按原归属引用，不写为我的产品亲测。

## 最终边界

冻结清单、当前执行字节、原指令、规则快照、双prompt和原审计绑定未发现输入阻断，可在实际环境/预约条件满足后供双方各自新建全范围任务使用。**当前安全环境门未解除，实际双审、push/PR/CI/merge仍未完成；本报告没有批准这些动作或产品通过。** 无需因本次只读preflight重复产品测试或1254原件审计。
