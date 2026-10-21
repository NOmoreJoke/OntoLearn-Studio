# Windows probe CLI：DOS basename P3 定点复核 R2

2026-10-22（Asia/Shanghai）。固定完整候选 `b1c54c3de840e657aba07906587681f6415085d6`；比较基准为首 CLI 修订 `1b025562b1011155e07130175fdadc522185453e`。只复核此前保留的 DOS basename P3 和本次 diff，不签根完整控制报告，不重开完整 N0 平台审查。

结论：此前保留的 DOS reserved basename **P3 在源码层闭合**；本次 diff 未发现新的确定问题或明显 C++17/数组边界缺陷。此结论是文本与分支审查，全部 static_assert 未编译、未求值、未执行；目标平台编译/链接/运行/故障仍未验，N0 技术仍未通过。

## 固定来源

| 输入 | bytes | SHA-256 |
| --- | ---: | --- |
| 固定 ref 的 packages/native-location/tests/location_core_test.cc | 29666 | 7d0965cafe74fcbaa0d6c0fcf57078d2969fd3f243d7a14d1e7244329017bcdc |
| cli-path-P3/source-static-check-r2.json | 6196 | 7512d0351452b5635ff385b174686daef0411b38c378dd57af25640fc7ff9f4f |
| cli-path-P3/followup-disposition.md | 2095 | 46011508d8853e68ab0c25a568913a8064613fb84ca2fc65d82dc564b566df83 |
| 固定 ref 中的原 independent-review.md | 8345 | 92c02742e6d46b351936dbf9a1610b50411926ebcdfdef661b336fa1cd6087a3 |

产品逐项从固定 ref 用 git show 读取并计算 bytes/hash，九源均匹配新清单；与 1b 比较，只有 core_test 改动，另八源精确未变。原独立首审 bytes/hash 已从本候选实际核对，没有倒写结论或改写原件。两份本次辅助记录已全文读取，不以它们的 exit 字段当编译/测试通过。

## 修复是否覆盖原反例

固定 `location_core_test.cc:70-88` 在既有非空组件判定后扫描首个点之前的 basename，保留实际 base_length，并仅复制最多 4 个宽字符到零初始化数组。ASCII a–z 转大写后，只在完整长度为 3 时拒 CON/PRN/AUX/NUL；完整长度为 4 且前三字母为 COM/LPT 时，拒 ASCII 1–9 和 U+00B9/U+00B2/U+00B3。

因此此前 `C:\NUL.exe`、`C:\CON`、混合大小写设备目录、COM1.exe 及多扩展形式不再仅靠“组件非空、没有禁用字符”通过。扩展名不能改变首点之前的保留 basename；上标数字不是 ASCII uppercase 转换的对象，而由明确宽字符常量比较覆盖。此处与此前引用的 [Microsoft 官方 Naming Files, Paths, and Namespaces](https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file) 所列保留名及带扩展名规则一致。

COM10 的实际 base_length 是 5，即使本地缓冲前四字母恰为 COM1，也不会进入长度为 4 的 port 判定；NUL-data 同样不进入长度为 3 的判定。这修复的是完整 basename 的有限列举，不是任意前缀过滤。

代码在所有组件切分点执行，普通 UNC 的 server/share 也明确应用同一保守规则；注释与作者处置均将其标为 fixture 策略，不声称 server/share 与磁盘文件 basename 的实际语义完全相同。该策略可能比系统可接受集合更窄，是作者明确选择的 CLI 合同，不是额外 OS 能力。

处置：原同级 P3 的具体反例在新源码分支闭合，**源码层关闭**。不将此有限列表推广成完整 Windows 名称解析、文件存在/身份/PE 格式/权限认证，也不新增 DLP 或任意同 UID 对抗保证。

## 数组边界与 C++17 可行性

basename 扫描的先决条件是 count 非零，且已有切分循环保证组件范围位于已知字符串 length 之内。`base_length < count` 在读取 `path[start + base_length]` 前短路；复制循环同时要求 `j < base_length` 与 `j < 4`，因此源索引在该组件内，目标索引在 base[0..3] 内。base 数组零初始化；即使 dotfile 的 base_length 为 0，之后 port 判定读取前三位也只是初始化的零，不会读取未初始化数据。保留完整长度与最多四字符的工作缓冲是两个不同量，没有将截断缓冲误当完整字符串。

扫描最多经过原 1023 字符以内的组件，未新增整数回绕或指针越界条件。新增局部初始化数组、有界循环、宽字符比较及 ASCII 范围内的算术转换，未见与 C++17 constexpr 写法冲突的构造；三个 UCN 宽字符常量可在现有目标宽字符集合中表达。以上仅是源码语义检查，没有运行编译器、constexpr evaluator 或脚本移植 helper 来证明结果。

## 反例与行为范围

新增源码 `location_core_test.cc:109-121` 共 13 条 static_assert：2 个非保留近似名称正例，11 个保留 basename/目录/大小写/多扩展/serial/parallel/上标/UNC 负例。与原 15 条一起为 28 条，即 5 正、23 负。源码所列标签与对应分支条件吻合；无本轮执行通过的声称。

本 diff 只在纯文本 helper 内加入比较和同文件字面断言，没有新增 OS API、文件/管道操作、子进程、权限参数、路径 fallback、Node API、ABI 或资源预算。原实际 Windows 路径仍是 UTF-8 转换成功后执行 helper，再创建 pipe/process；本次没有改变该调用顺序或 child/reaper/cleanup 归属。UNC 字符串被认可不等于本轮授权访问网络 artifact，后续仍须固定 T03 供方及精确运行窗口。

本次未扩大为对所有 Win32 兼容名称、文件系统限制、路径存在、名称映射或设备访问结果的测试；这些不由纯文本 guard 认证。没有为扩大覆盖再运行旧矩阵或读取 T03 实现。

## 本轮检查与限制

实际完成固定源码 diff、九源 bytes/hash 与未变标记比对、原首审 hash 保全，以及本新增文档 UTF-8/换行/行尾空白/表格/diff 检查。唯一新增本报告，不提交；不修改产品或任何旧报告。

未做 C++ 编译（含 syntax-only）、constexpr 求值、断言/测试执行、脚本复刻 helper、产品 import、native load、FS/child 实验、GUI、新依赖安装或 T03 WIP 采用。两 OS、工具链、实际 API 结果和故障的原门均保持；本报告只关闭固定 b1c54c3 的指定源码 P3，不替代根完整控制交付结论。
