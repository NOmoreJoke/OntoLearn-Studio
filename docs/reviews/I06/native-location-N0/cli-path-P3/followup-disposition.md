# CLI P3：保留设备名补充处置

2026-10-22。首修订 `1b025562b1011155e07130175fdadc522185453e` 的独审已保留 independent-review.md，8345B/SHA256 `92c02742e6d46b351936dbf9a1610b50411926ebcdfdef661b336fa1cd6087a3`：原 drive-relative P3 静态修正，但普通 artifact 合同仍应补 DOS reserved basename，属同级 P3，非实际运行漏洞或新 P1/P2。首修订、原报告和首15条断言均不倒写为最终通过。

作者实际读取 [Microsoft Naming Files, Paths, and Namespaces](https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file) 的 Naming Conventions，确认其列出的保留名称在文件/目录及带扩展名时仍受限，上标数字1–3也是 COM/LPT 保留变体。没有据此扩成完整 Windows namespace/文件身份认证或 DLP。

唯一产品/测试改动仍是 location_core_test.cc：29666B，SHA256 `7d0965cafe74fcbaa0d6c0fcf57078d2969fd3f243d7a14d1e7244329017bcdc`。在每个已有组件的首个点前，最多复制4个宽字符并作 ASCII 大小写无关比较，保留 basename 实长，拒 CON/PRN/AUX/NUL、COM/LPT1–9以及上标1–3；扩展名不绕过，COM10/NUL-data 不因前缀误拒。普通 UNC 的 server/share 也明确采用同一保守拒绝策略，这是一项 fixture 文本限制，不声称它们与文件 basename 的实际网络语义相同。

增加13条纯输入断言：11个保留名/扩展/大小写/目录/上标/UNC负例和2个近似名称正例。合计28条（5正23负），均仍是未编译、未求值、未执行的源码。C++17局部数组/有界索引之外没有新工具、OS调用或依赖；原 guard-before-pipes、child责任、ABI/Node12 API 和八件未变源码保持原样。新九源文本/hash清单见 source-static-check-r2.json。

本处置待新固定 ref 独立复核后才关闭剩余 P3。旧 fa1/ff0 的其余39件原件保持字节，不修改原交接/manifest/报告。没有编译、测试、constexpr求值、产品 import、native load、FS/child实验、T03 WIP采用或构建运行授权；根完整控制审查仍待其正式签收。
