# O 隔离 launch 准备独立审查

结论：**Pass，仅限冻结的隔离输入、路径/执行补充和静态 setup 准备。未发现需退回的 P1/P2。** 两方实际 workspace、完整原提示、共同 scope、输入镜像及290件保护字节核同；新预检工具没有执行仓库代码的路径。此结论不代表已创建指定任务、真实模型设置已读回、正式完整审查通过或任何产品/父门完成。

## 固定身份与边界

| 项目 | 实际身份 |
| --- | --- |
| reviewer | `/root/projection_receiving_review_package_independent_review`，本轮独立限定准备审查 |
| setup owner / cwd | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T05-source-package-oracle` |
| branch | `feature/T05-source-package-oracle` |
| 冻结 setup candidate / 审查 HEAD | `3f840d6cc49ec71207d0ab9d6daed61702e878da` |
| parent / 资料过程 | `86df64a2c707355ed177d536ef5975a1986c0f0b` |
| 原 O 源码/工具/expected | `77852d27a3c4e84867a42f243e0f4e0f32b8df67` |
| repository base | `5f910b52c69d86a1076b2032e5d3c63e715947f3` |
| 共同 scope SHA256 | `371fcf080d86eb1649dc1edea16ff6066c96dced83ed059af05336ea148c93d9` |
| 唯一新增写面 | 本报告 |

全文读取本新前缀 authority、scope-contract、README、launch-index、两方 map/执行补充、原预检源码及权限快照；承接已读且 SHA 相同的 AGENTS/共同外控。授权来源按父 agent 透传及 authority 中总控聊天 `01a154de-843b-7a00-8a80-51ba1c0aebce` 记录使用，没有重新查询聊天、应用或全局任务状态。

本轮只用本审自有标准库/Git/文件只读逻辑与 AST。**没有执行新 verify-launch-input.py**，避免覆盖冻结 preflight；没有执行源 oracle、测试、builder、I05 model、产品、原工具、actual、GUI/网络/安装/Goal或其他运行探针。没有打开原 runtime actual ZIP、读取任一模型报告/意见/会话数据库；没有写两 workspace、修改 frozen39或 stage/commit。

## 完整正文、映射与独立物理输入

| 本方 | 实际 detached workspace | 完整正文 bytes / SHA256 |
| --- | --- | --- |
| zcode | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T05-O-zcode-review-e15ce44` | 12897 / `887066cd54f48216215faa2096cebd5ca95e1f851f8c93569aa6beca800ff6fd` |
| minimax | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T05-O-minimax-review-e15ce44` | 12946 / `4f585bddefe6ba504c9b5786b3b2db29078e0d07fa262da3facaed73bb04abf1` |

两实际树 HEAD 都是 `86df64a...`，`rev-parse --abbrev-ref HEAD` 均为 `HEAD`，cached index 空，tracked 差异恰为保护 `AGENTS.md`。两树 AGENTS 均15147 bytes，SHA256 `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`，与当前快照相等，未将 Git 中1056 bytes的历史指南冒充当前指南。

逐字节验证每份 `launch-prompt.md`：以本方 execution-supplement 原字节开头，以固定86df中本方原 O 提示完整原字节结尾，原提示只出现一次；中间仅追加“原始完整 O 提示”分隔标题。`frozen-original-prompt.md` 与固定 Git 原提示也精确相等，没有改写原冻结提示或替换为修复摘要。

两方执行补充在替换自身绝对 workspace 和模型要求后全文相同。原 owner 根及其子路径统一映射到本方同一相对路径，历史 feature 分支与实际 detached HEAD明确区分；原正文旧报告路径被唯一 own `launch-O/report.md` 替代。外部历史 tree 路径只保归属，缺原件应标缺证，不向另一指定模型树取材，不跨六实现拼接。

本方 `scratch/`、`raw/`、`preflight-setup.json`、`preflight-observe.json` 写面单列；报告和自动元数据不能写回 owner。明确禁止 peer workspace、当前报告、自动状态、全局 session DB/log及间接遍历读取；共同历史 Fail/独审/PRD仍可作为固定输入。当前仅检查报告路径不存在，没有读取报告内容或模型运行状态。

每方实际 launch 下11件 manifest输入全部与 owner对应镜像、bytes/SHA核同，manifest自身及 preflight、command/stdout/stderr 也与镜像相等。22件两方输入逐件 stat 检查没有跨方相同 device/inode，workspace不是 symlink；本方 scratch/tmp各自存在，未见 `.venv`/`node_modules`，未使用共享可变运行依赖。这里只确认当前文件和准备布局，不声称已验证未来应用的运行隔离。

## 受控源与290件字节证明

独立用 NUL Git tree/path数据复核：原778树914件，与 O full-engineering-inventory 完整metadata逐项相等；过程86df的tracked集合958件。149件工程/authoring清单，加原 declared-allocation 130件和资料 delivery 44件（均含各自manifest自身），合并为290个唯一受控路径，重叠身份无冲突。

对每个 workspace 的290件逐项检查：current bytes=固定86df Git、长度/SHA=相应原manifest或inventory；并与 preflight-setup 的290条 protectedFiles 全对象相等。原 manifests 自身也等各自固定 source/process Git。没有把914树metadata当已验证所有运行行为或外部依赖；290是明示保护字节集合，不是完整产品验收数。

setup candidate相对parent恰39个新增文件，全部在本新前缀，合计 **312624 bytes**。candidate-manifest的38成员+self精确覆盖39集合，各成员current bytes/SHA与清单相等，39件current也都等候选Git。两wrapper与owner镜像冻结不变，本审未重做未变化37/137/85的旧语义审查。

## 原 setup 预检证据与扫描时间界线

两方原 command载体记录的实际argv均为：

```text
python3 -B <本方launch-O/verify-launch-input.py> --phase setup
cwd=<本方实际workspace>
TMPDIR=<本方launch-O/scratch/tmp>
```

载体 exit均为0。独立读取实际 stdout、空 stderr及命令JSON，bytes/SHA与command及owner镜像相等；stdout JSON所列 workspace/phase/290/sourceAndInputBytesVerified/setupReady/unknownNewMetadataPaths 与snapshot相等。snapshot SHA/bytes也逐件等 launch-index 所指原件。本审核对既有真实载体及当前一致性，未重新执行预检。

扫描界线没有伪称全时间段冻结：每份snapshot实际记录12个额外输入（11输入+manifest自身），精确排除当次输出 `preflight-setup.json`；原流落盘后追加三件 raw命令/stdout/stderr。因此当前额外文件恰 **12+当次output自身1+后追加raw3=16**。本审只读枚举当前本方路径集，完全等上述集合，无未知额外文件、symlink目录或被ignore隐藏的输入；12件快照数据当前仍等原hash，snapshot文件mtime也不晚于三件raw文件。文件mtime仅作顺序相符的旁证，不独立证明业务时间或命令终态。

工具不靠gitignore筛除元数据。新官方元数据若出现，会登记路径/大小/不透明hash和 declaredOwnSurface，不删改求绿；unknown路径导致非零结果。当前setupReady=true仅指既有静态准备；actualTaskIdentityOrCountInspected=false，不把该工具当应用任务ID/模型设置/终态核验器。

## 新工具静态范围与未来正常验证

工具7383 bytes，SHA256 `5edd9178273d9b47e7e15cf8243a287ef3c84915e00a0e834d94741bf7799ef0`；owner原件、两个镜像和两方实际副本全相等。AST及全文检查：

- imports仅 argparse/hashlib/json/os/pathlib/subprocess；没有仓库模块 import。
- 唯一subprocess调用为 `subprocess.check_output(['git', *argv], cwd=root)`，调用点均为身份、树、diff/index、固定blob等Git读取；没有shell、产品/测试/模型执行。
- cwd和here必须属于 map指定本方根，HEAD/detached/index/保护AGENTS先验；local路径拒绝出界resolve或symlink。输入检查与文件遍历都限本方root，不访问peer/global task DB。
- 唯一文件写调用在源码 `:128`，输出本方 `preflight-setup.json` 或 `preflight-observe.json`；不写源码、fixture、旧manifest、raw或AGENTS。结果/额外元数据全量登记，无删除/ignore操作。

authority和scope精确区分setup与未来正式审查。setup没有运行两个原正常O命令；未来仅在总控预检后、独立必要时允许：

```text
python3 -B scripts/test-i05-source-package-oracle.py
python3 -B scripts/build-i05-source-package-oracle.py --check
```

它们绑定固定自有stdlib oracle；47是历史报告数，不是本次实跑数。第二条必须保留 `--check`，不得裸build写回。无变化不因调度强制重跑，own TMPDIR和原流/首错要求保留。没有因SQLite/child字面词泛禁原本合法正常suite，也没有借这两条扩到I05产品/模型/collector/actual、被拒物理资源研究、HOLD、未签native/caller、GUI/build/package、网络/钥匙/费用。当前共同指南的泛Goal/宽验证不会覆盖精确scope。

## 实际检查与非零探索

本审实际执行仅Git/自有标准库heredoc与文件读取，cwd固定owner树；tool记录保真实调用/输出，本文不伪造单独捕获的原始流文件。

| 实际调用族 | 结果 |
| --- | --- |
| `git status --short`、`git rev-parse`，`cat` authority/scope/map/补充/新工具/原载体 | exit0，读取准备材料 |
| `git diff --name-only -z`、`git ls-tree -r -l -z`、`git show ref:path` | exit0，39候选、914/958元数据、固定原提示/manifest及290字节 |
| `python3 - <<'PY'` 自有JSON/hash/AST/stat/路径集合断言 | 最终对应核对exit0，两输入镜像、290、raw界线、工具范围等均通过；不import/执行被审工具 |
| `git diff --check 86df64a2c707355ed177d536ef5975a1986c0f0b 3f840d6cc49ec71207d0ab9d6daed61702e878da -- <本新前缀>` | exit0，仅本准备delta |

本审一次非零探索准确保留：首个manifest检查错误地把本candidate-manifest的前缀内相对路径（如README.md）当cwd相对路径，断言失败exit1；更正为本新前缀根后，39文件/38成员+self/312624B与两wrapper核对完成exit0。没有写或修受审输入。另一次两补充的差异显示只因MiniMax模型名称/权限描述尚未完整归一，打印后用完整实际模型描述归一，全文相等；该只读命令本身exit0，不冒充产品失败。

作者原rg误指不存在README的exit2仍由launch-index/README准确披露；它是工具结果摘要，未伪造分离原始流。旧R1/R2与I05历史失败/非零均不被本局部exit0覆盖。

## 最终限定

本轮无新增应修发现，可把该固定setup作为总控后续根预检和短lease调度输入。所有 actualTaskId/actualSettings/actualTerminal/actualReport仍为null，actualDesignatedTaskCount=0，currentGUILeaseGranted=false；这些是当前准备材料和范围事实，本审未查询应用服务验证全历史。

正式创建、两模型各自实际设置/ID/完整受理/终态、独立完整报告及意见处置尚未发生；以后出现元数据须照实登记，不能清理或忽略换绿。137pending、417/280/false whole、26声明缺件、完整DTO/serializer/来源/held首错、正式Job/Store/selected/wholeH、17L/费用、S1/B1、CI两OS/真人/develop和父P0保持原状态。本 Pass只签准备范围。

本审仅新增此报告；最终bytes/SHA由落地后回读与交接消息提供，不自含自身hash。
