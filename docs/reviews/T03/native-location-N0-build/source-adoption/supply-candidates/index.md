# 固定fb40供应元数据派生候选

SDK与resource两份完整 `roots + files` 四pin JSON已生成，供根后续审批；**toolchain、execution、Node、Windows均未采用**。本任务只读固定Git JSON/JSONL/文本，未重读/hash SDK、cache、大实物、归档或任何工具，未新probe、运行driver、解析新源码/runtime或改lock/旧证据。

源固定 `fb40bde92cc35269c25c11a8628a71d5f750be4e` 的109个tool-supply文档；实际消费body的ref/path/bytes/SHA/Git blob与派生规则见[source-bodies-manifest.json](source-bodies-manifest.json)。既定driver为`fe98dab02375362fcc07ca9bb309de17b558fcf2`，只读其现有schema/env字面值。

- [SDK清单](sdk-files-inventory.json)：**33464 regular**、931393813B供方对象，JSON **14649771B**，小于16MiB/50000；canonical root `/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk`。无删项、无截断。
- [Resource清单](resource-files-inventory.json)：**9307 regular**，JSON **4717231B**；含全部8839 CMake regular、compiler resource/include/已定位工具runtime、81个完成cache身份及原map，合法0B hello.f保留。按记录的canonical realpath去重且同身份需bytes/SHA一致，不是重新测实物。
- [Darwin锁形候选](darwin-toolchain-candidate.json)保持当前schema，approval=false/reference=null；不写实际lock。[目录/链接指针](directory-link-source-pointers.json)保原全type记录与隐式容器；root只是文件allowlist的containment，不授新扫描范围。
- [实际工具/SDK/条款映射](tool-routing-sdk-terms.json)：cmake/c/cxx用原真实探针pin；make/git优先固定Developer/usr/bin实际backend，另列/usr/bin Apple dispatcher及其版本来源。未把相同dispatcher SHA当backend证明，也未新增backend版本探针。linker ld与runtime仅复用已有元数据。
- [环境候选](environment-candidate.json)明确提出未采用的`DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer`，以及现driver的PATH=/usr/bin:/bin、LANG=C、LC_ALL=C，HOME/TMPDIR由未来精确buildDir派生。**现Darwin schema要求env={}，build env又硬编码不承接DEVELOPER_DIR**；侧文列出两处最小未来owner delta，当前没有修改或冒用该环境。

[边界与缺口](coverage-and-gaps.json)分别保留cache嵌入传递、postbuild used、条款、当前实物漂移与未批环境等具体事项。systemLibraries空候选表示没有猜测或新增显式链接库，不能解释为没有隐式系统runtime或豁免根对core链接合同的审批；未加入Linux库或任意系统lib。Xcode/SDK原开发协议和未来分发第三方notices分别列明。Node/Windows/Electron未批，不能据此阻止不依赖它们的core候选准备。

本轮供方body新增读取0B；原累计9745727085B保留，未重置。未commit。所有文件bytes/SHA见[delivery-manifest.json](delivery-manifest.json)。
