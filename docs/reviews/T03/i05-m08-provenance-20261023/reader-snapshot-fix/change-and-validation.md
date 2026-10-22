# distribution Python 单次读取修正

独立审查对32d943发现F2/P2：Python distribution源文件首次以FILE_CAP=128MiB读取后，另一次以CODE_CAP=2MiB读取来编译，扩大首次读取上限，并可能令bytes/SHA与代码指纹来自不同版本。原实现和首审报告继续保留。

主控先添加两项参数化回归并在旧代码执行，20轮实际2 failed/96 deselected：首次读后替换文件，成功记录的codeHash不匹配原source bytes；超限文件在首次宽读取后被替换为小内容，也未按约定拒绝。没有通过真实全仓prepare或第三方导入来复现。

修正只在_dist_inventory对.py先选2MiB上限，读取一次raw，以同一份raw生成bytes、SHA和compile-code fingerprint；非.py保持既有artifact上限。不改schema、固定输入、consumer API、错误码、native等价域或root approval。两项回归分别要求同一内容快照和首次读取cap严格为CODE_CAP。

23轮目标测试98 passed in1.94s；21 Ruff和22 format --check均exit0，产品diff --check0。所有原始双流保留；没有真实PyInstaller、whole-repo prepare、native、full-v1/B1或GUI。首32d943的96项不改写成98项；修订830cdd仍需独立delta复核后交主控。

首次归档脚本发生stdin Non-UTF-8 SyntaxError，未产生目标目录；后续git add该目录也未成功，产品与先前补注已单独固定830cdd。现在仅补独占原件和说明，不改写830cdd或首次失败记录。此归档错误与产品测试结果分开。
