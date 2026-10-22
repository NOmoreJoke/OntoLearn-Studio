# Store surrogate 输入线索核验

结论：原线索中的拒绝行为已在批准 base 与当前 C1 字节上分别复现；没有证据把它归为 C1 新增的数据写入缺陷。本轮不因此修改共享 canonical/digest 或放宽 Unicode 输入，也没有扩展 damaged-input / SQLite 物理研究。

## 原线索身份

静态读取 Git 固定对象并重算，均与总控交接一致：

- base `5f910b52c69d86a1076b2032e5d3c63e715947f3` 的 `storage.py`：55364 B / SHA256 `4abf1082f1b864eb9efa155c7cbc890ef70cb196f30e09ad12629ce7a0cf6842`。
- T02 `c61c7f1ed063172e0b3e29761a5a31c212c6573c` 的固定原证据归档：717671 B / SHA256 `0766fb7dcf79d847369908253856288cf343f95ac329e08e458f749a70567f3f`。
- 只读取其中指定 probe 的 75–85 行及 log 的 15–21 行，不执行外来脚本。两个 member 的完整 bytes/hash 与交接一致，见 `surrogate-static-origin-check.json`。
- 原日志的 `EXIT=0` 是捕获异常的包装脚本结束，不代表 Store.commit 成功。

## 本轮自有验证

自写脚本 `probe_surrogate_own_tmpdb.py`（1880 B / SHA256 `f59e3526284d9379a7a4b73471bbbaa554bb2d086214256b4afd3a72fbb05508`）分别导入从 base Git blob 导出的引擎源和本轮实际工作树源；每次核实际 `storage.__file__`。所有库都是脚本自己创建的健康临时库，未读取真实用户库、未制造损坏文件。

对 `Store.create_project('p')` 后的 legacy definition opaque payload，分别传 `x + U+D800`、`x + U+DFFF`：

| 观察                                          | base               | 当前 C1            |
| --------------------------------------------- | ------------------ | ------------------ |
| 拒绝类型                                      | UnicodeEncodeError | UnicodeEncodeError |
| 属于 ValueError / UnicodeError                | 是 / 是            | 是 / 是            |
| BEGIN / INSERT / UPDATE / DELETE 在拒绝前发生 | 无                 | 无                 |
| 拒绝前后完整 logical dump                     | 相同               | 相同               |
| revision / marker                             | 0 / 无 seed marker | 0 / 无 seed marker |
| 随后正常中文及非 BMP 标量的提交               | 成功，revision 1   | 成功，revision 1   |

两次自写 probe 均 exit 0，表示上述拒绝与零写入断言成立，**不是无效输入被接受**。另执行当前既有 `test_invalid_names_are_strict_and_zero_write`，7 passed / exit 0；其中 C1 创建名称的 U+D800 用例按固定 `CreationFault('input')` 拒绝，证明该线索与 C1 创建入口不是同一错误路径。

## 处置边界

`Store` 是接收已验证 domain plan 的私有持久接口；此处原行为是在 `digest(plan)` 做 UTF-8 编码前拒绝不可编码的孤立 surrogate，尚未开始交易。UnicodeEncodeError 本身属于 ValueError；现有证据没有持久污染、半提交、真实 wire 上接受非法 scalar 或 C1 回归。

若将来需要把所有 legacy Store 输入错误统一成新的内部固定分类，应先明确正常输入合同、调用者与版本兼容，再由唯一 owner 在独立候选处理；不能把这次观测直接变成全局 digest/canonical 规则变更。本轮不做该扩展，也不把“本次不改”写成外部模型对线索的签字关闭。

原始 argv/cwd/起止/exit/双流位于工作区外 `outputs/20261022_review_backlog/T01-C1-remediation-20261022/raw/{surrogate-base,surrogate-current,c1-invalid-name-boundary}/`；源身份和自写脚本另行纳入本轮 manifest。临时运行库不入库。
