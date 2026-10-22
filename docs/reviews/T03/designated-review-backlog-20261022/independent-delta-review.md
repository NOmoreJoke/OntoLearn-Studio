# T03 发审包 F1：独立精确 delta 复核

结论：**F1 / P2 CLOSED；LIMITED_PREPARATION_DELTA_PASS**。真实修复候选 `806920ac8512d82a7a9b2c1977d23079bcb27fed` 已补齐各提示的共享包绝对入口和不可变身份；八份新提示可无猜测定位同一 ed9 原包及各自完整输入。没有发现此定位 delta 的新增问题。此结论只接受发审准备文档修复，不是源码审查、指定模型通过或实际派发许可；native 当前仍禁止以旧681/cf9快照派发。

## 身份与范围

- 树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-mapping`，分支 `feature/weekly-t03-mapping`。
- 首候选 `ed9cef968b17a1edefc0977b509906fb9f81a336`；首Fail三件先封存 `7a521a804eec31a2c98935b3eb12acb8956aa020`；新候选/入口HEAD `806920ac8512d82a7a9b2c1977d23079bcb27fed`。
- 新 `dispatch-v2/` 精确11件：10 payload共64580 B，delta-manifest2620 B，完整67200 B；manifest SHA-256 `d16d2095461d816e43b2a803d380eca089493f2c615177bd8439572ef3a1cc5d`。
- 逐件核 current = 新候选Git = manifest bytes/SHA；首报告commit→新candidate只有这11条新增路径，没有修改旧件。旧19及首Fail三件都逐字等其固定Git原件，原manifest和旧报告不追写。
- 入口index空，tracked修改只有受保护AGENTS；本次不stage/commit。

完整读取11件新文档/JSON；一次取得的提示文本保存held buffer后连续分段补齐。八份新提示的正文分别以ed9中对应旧提示完整原bytes作为suffix，逐字核同，没有把完整范围或原门缩成F1 delta；本审仅对新增前缀/定位表/处置说明作精确复核，不重复原完整源码或历史验收审查。

## F1 关闭依据

对八份提示逐一从**正文实际给定地址**独立完成：

1. 共享根明确为 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-mapping/docs/reviews/T03/designated-review-backlog-20261022`；Git读取仓库为该mapping工作树，固定ref为ed9。不是依赖当前所选source/profile/native树猜同名相对目录。
2. 原candidate-manifest绝对path与完整 `ed9:repo-path` 都明确；实取固定Git文档及当前文件，4301 B/SHA `60c52bd13dac43bb9685b5233db817118dda10341357794d9f27500f07301e6c`一致。
3. 本组 `*-fixed-inputs.json` 的绝对path、固定Git地址、bytes/SHA均正确，并与原manifest一致：mapping241447 B、native1377399 B、profile279964 B、source215883 B。locator-index八行与各提示完全对应，没有串组。
4. `historical-stage-inventory.md`、`coverage-matrix.json`、`coverage-summary.md` 明确在共享根及同一ed9 ref。已分别核固定Git=当前原件=原manifest身份；没有搜索或选择未固定版本。
5. 所有旧“本包”由前缀明确重绑定到上述外部只读共享包；工程仍按正文各自product/process读取，禁止切分支、复制/拼装其它分支源码。四个目标路径存在，使用其普通Git元数据也能解析同一ed9对象；无需实际复制材料到目标树。

因此首审提出的“所选工作树没有共享包，也缺少实际定位”的反例已被此前向修复关闭。原六份旧提示缺口和首Fail原件继续保留，不回填旧Pass。

## 保护与未验边界

mapping产品303→新候选的非docs工程路径没有变更；source/profile当前HEAD仍分别为4fa5d62/56a8523固定过程ref。native本组继续指明旧681/cf9仅登记，修caller与独立delta后需前向新输入；本次没有读其当前源码修复WIP，也不据此声称WIP未变或已经通过。

当前desktop policy3160 B/SHA `2032bd9e1cdbf398a0d505e092e1a08b80ff15df26b1d06c7d7e1c2e0a5a8ec1`与首审已全文读取版本相同，新前缀准确附加短lease/后台不独占政策。它不扩大static/native执行权。八提示保持完整原验收、双方独立与设置实读、真实终态全文报告、缺证不通过/无法验证及未签/被拒工作不得代跑。实际task ID/设置/报告/lease仍待真实派发，native禁止派发不变；此复核不创建任务或运行票。

本次仅普通文件/Git/JSON/hash和本人新文档formatter；未读源码/SDK/tool安装/二进制/descriptor/witness/index/原archive载荷，未运行产品、测试、caller/准备函数/runner/reader/helper/fixture/模拟/compiler，未用CUA/网络，未stage/commit/push/PR/merge。旧5232/1222完整元数据审查沿其未变字节身份，不冒新代码或运行验证。

仅新增本delta报告、independent-delta-checks.json及independent-delta-seal.json三件。完成格式检查、全文读回/hash seal后停写，供父agent全文接收并固定过程；后续真实派发、外审、意见关闭与所有原门继续据实完成。
