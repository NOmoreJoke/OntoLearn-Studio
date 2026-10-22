# I05 asset-ref-r1 独立静态与真实证据审查

结论：Limited Pass，新增资产provenance常量正确分离封存输入身份与运行时源码身份，未降低固定资产guard，未发现新增P1/P2。真实定向red→green产物已核验；失败的全pytest仍保留，尚不能宣称12fail/31errors全部消除或完整check通过。

## 新失败与旧静态边界

full-pytest-01实际exit1，stdout37590B，SHA-256 `d1ae8bd16f071941d9700ef57773aeb31be5e954d0762b2ec6834710296d91d2`。独立读收据、stdout首尾及所有JUnit testcase记录：1179 collected = 1136passed + 12failed + 31errors，0skipped；31个error文本均含ASSET_VERSION_INVALID。JUnit205659B，SHA-256 `9cabbd82bea1337bf35281e49de351ea0c440b3850e7439e730b0f11b041e655`；stdout记录58.20s，launcher58.693227s，JUnit suite58.181s，保持计时域区分。

版本校验原将manifest.versions.supplierRef与SOURCE_REF比较。封存manifest固定6891，而运行时source已改23352，导致资产校验拒绝。31个setup error直接提供该异常证据；12个failure体现空输出、缺失观察或预期1却返回2等连带现象，未用这些现象声称修复后整轮必定通过。

前轮pin-refresh静态审查验证了身份/AST保留，没有识别SOURCE_REF同时承担封存provenance校验的语义耦合，也没有声称运行通过。旧Limited Pass报告原样保留；本轮以实际失败补充该限制，不倒改旧结论或失败记录。

## 修复严格性

当前probe102749B，SHA-256 `2996deca33083754132bf5f4eab8d1e273161b3e5fe722a8ee96856fb5cc0d5b`。相对已核验的pin-refresh版a6b6，只有：

- 新增 `ASSET_SUPPLIER_REF = "6891a5842302859a531cf82767c5a482417bc274"`，注释明确它是封存输入provenance。
- _validate_nested_assets内完整versions字典精确比较的supplierRef值，改为该常量。其余contractRef、b1InputMethodRef、generator、datasetCanonicalization，以及失败码ASSET_VERSION_INVALID保留。

独立从固定23352重建此前pin-refresh字节并先核对102607B/a6b6原hash；再移除当前新增常量、将唯一一处ASSET_SUPPLIER_REF load恢复SOURCE_REF，整个probe AST完全相同。因此所有其他SOURCE_REF调用仍使用运行时23352，PROCESS_REF仍513db，22源pins、八依赖、资源hash/bounds、精确schema、417预期和采集流程不变。没有any-ref、OR旧新ref、缺省fallback、跳过版本校验或异常吞并。

封存输入供应商6891在新常量中保留，不把它冒充当前执行源码；运行时supplier/header/material source_revision仍按原调用引用SOURCE_REF。这里区分两种事实，不是放松其任一种身份。

## 两JSON与新增回归

本轮实际读取两JSON字节，并与固定23352对应Git blob逐件比较：

- manifest21202B，SHA-256 `0b91c1a9366d170b5614d94c20006054a5a959be235e0f46cb150cf32335193a`。
- inputs8205267B，SHA-256 `47c66ffe18613eb8cc1af6365dcfc9d866821f22c48f96d9f44725f8f7c59eaa`。

二者current=fixed；manifest仍固定supplier6891，其inputAsset声明长度/hash与实际inputs相符，full-v1清单417项、输入observations417项。没有改原资产或期待。

当前测试76535B，SHA-256 `5fcf853fb48f5781758bdb0893357a9687f1ce7e35d9cc9352957b7d4fcaa4c9`。仅新增一条回归；删除该函数后整个测试AST与固定23352测试相同。回归deepcopy封存数据，先断言原6891真值；仅monkeypatch运行时SOURCE_REF为f×40后，validate_assets仍成功；再把复制的manifest supplierRef改为f×40，必须抛精确ASSET_VERSION_INVALID。它不改原JSON，也不让真实runtime preflight接受伪source；只隔离验证资产supplier语义。

主agent实际red为fixture setup的1error，不是新测试体断言失败：load_assets→validate_assets→_validate_nested_assets抛ASSET_VERSION_INVALID；0.22s，launcher0.603922s。green实际exit0，新增回归+原4个extra-key反例共5passed/0.34s，launcher0.728608s。三份命令收据的stdout/stderr字节/hash已独立逐对核验，stderr均0；未伪称是本审查执行。

## 后续边界

本审查仅Git、字节/hash、stdlib AST/JSON/XML操作，没有运行产品、pytest、formatter/Ruff，也没有重复原诊断或重跑整链。按root要求，等待T01配置供方后再由主agent进行获准完整check；定向5case不能代替该结果。

既有全pytest失败、原静态报告及全部历史red/green保留。CLI/frozen、physical/source-package parity与整体目标仍未由本轮关闭。
