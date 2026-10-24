# 固定设备运维示例资源

`equipment-maintenance-resource-source-v2.zip` 是 T09 已供给、T11/package087 已采用的原始22件ZIP，来源为 `outputs/20261023_t09_fr003_deployment_v2/equipment-maintenance-resource-source-v2.zip`。原ZIP为1344035B，SHA256 `b8717a53501e0825c5209faaf7e056e28d2f8c5f8c74b4b7e1f7bdf8b618164a`；独立校验值见同名 `.sha256`。

本目录只归档既有原字节，不生成新示例。ZIP保留完整source/reference及adapter映射，解包总计1338939B；provider为198B（含原尾LF）、load-input为10930B。`scripts/prepare-fr003-bundle.py` 在全部固定成员、路径、CRC、字节数和SHA256核同后，确定性准备到既有 `build/release-resources/fr003-bundle-v2/`。已有正确stage只复核；已有缺失、变更或额外成员则拒绝，不覆盖。

根级predev/pretest/prebuild与desktop workspace的prepackage:dir共享这一前置；直接workspace打包只准备资源，不重建JS或engine。POSIX下资源文件为0444、stage根及资源目录为0555；既有stage的集合、原字节或权限不符都会失败。准备在受控单写入者目录中使用协作锁，不承诺对不遵守锁的并发写入者提供平台级no-replace保证。产品入口与electron-builder仍消费原loader路径，不从网络或另一个工作区取资源。missing-root/changed-input测试继续操作各自临时副本，prepare不会替它们回填。
