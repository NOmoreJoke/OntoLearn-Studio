# T10 E1 原件保全

按总控固定66eeedd读回后的E1要求，只复制现存原件，不重跑测试/浏览器/产品，也不改变旧native或browser摘要。

## 旧原件

`evidence/legacy-raw-archive/index.json` 索引40个按原字节保存的文件，包含两份历史summary要求的11个raw、完整browser日志（内含实际执行脚本及结果/失败原文）、合成HTML/panel/invalid-panel及相关检查日志。11个raw均与历史登记SHA逐项一致。index SHA256：`4857d46acbe7f25d485c5ad81d2aff4604c4545e4a60ed9a6956c7bd1de18399`。

旧browser日志引用的runtime目录已迁移，实际文件在归档 `report-file-runtime/published-report.html`：3900字节，SHA256 `26af12303d80436e470fe30c5f1cffa57b424da0401ce1320e6bc5499ad676b6`。这与native attempt3的3896字节/ad367文件是两个实物，两次运行证据分别保留。

两条旧browser日志还引用已不存在的`.playwright-cli`页面snapshot，索引明确列为missing；未重建或虚称恢复这些文件。完整旧browser命令脚本/返回原文及HTML仍在。profile、缓存、凭据和无关文件均未归档；原始CR/空白保持不变。

## 运行后编译文件读回

固定native记录的 `compiled-sources.json` 只记录输入源码hash；66eeedd没有三份cjs输出原件，不能说其当时已独立逐字节归档。本次从**同一个已停止的attempt3固定容器ID**复制实际路径下csp.cjs/report.cjs/prepared-report-file.cjs，以`.raw`后缀保存在`evidence/native-compiled-postrun-readback/`，逐文件记录长度/hash；复制前后均核对相同image、exited0且未运行。

这是运行后的原文件保全，不能回溯成运行时独立hash证明，也不承诺离线完整恢复镜像。native原55文件manifest未改变。Git副本的权限不是原运行0600证明，原权限证据仍为native actualFile.mode及固定创建代码。源码引擎health也不变为产品包内引擎验证。
