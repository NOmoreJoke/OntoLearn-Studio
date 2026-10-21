# T03 N0 供应过程追加交付说明

2026-10-22。CMake完整提取和13条限定版本/元信息查询已实际完成；SDK、compiler include/resource/runtime与所列工具的供应记录已固定。另授的10GiB窗口补齐固定81个arm64e cache对象的单次实物SHA。整体供应采用、内部image传递依赖解释、组件条款及postbuild used闭包仍待根分别核验，全部产品锁审批false，未运行configure/build/test/load。

本目录按阶段追加，不倒写旧pending原件：

| 阶段 | 固定原件 / 身份 | 准确解释 |
| --- | --- | --- |
| 提取/供应早声明 | supply-declaration-final.json | 虽文件名含final，read_bytes_before_hashing及remaining=7170636196、预计delta1278399410和map membership not yet proven均属较早声明；不混作末账 |
| 原8GiB末账 | read-budget.json378B/32ef2836d14e348f6e5919eeade542d08322f48d109f2c01d6c88f657587bd42 | 已计2699211379B、剩5890723213B；原81项未读7046515706B，最低delta1155792493B；21直接install-name已在map逐名命中 |
| 后授10GiB增量 | dyld-delta-cumulative-read.json / dyld-delta-read-result.json | 新读7046515706B、累计9745727085B，剩991691155B；81/81各一次hash且前后身份同、首失败null |

原unhashed-system-cache-objects.json24420B/a0a368c44eec7843270d9f65a517bf43fa546e3766aeeb3fceeea82b80c6f08c保持过去未读事实。新81项完整SHA另在dyld-delta-complete-inventory.jsonl，未把过去状态改成过去已完成。所有对象均来自该固定arm64e精确名单；整组身份hash不证明每个subcache被compiler实际使用，也不证明内部传递依赖完整，更不替代首编译后的used headers/depfiles/linkgraph。

原候选candidate-pins.json12011B/d17e5ab336d71f622904adcc806adb1789b70555679768372ee2ab52e5fb6b2d、原92条evidence-manifest、index及原预算均保原字节。新dyld-delta-manifest另覆盖该增量；本交付delivery-manifest进一步覆盖原件、两个授权原文、独审、追加说明及最新delta，三者scope分别明确，自身不循环收录。二进制只在tmp，SDK未复制入仓库。

供应总记录53092+原CMake成员9041+隐式容器1=62134，数量guard200000保持。SDK全树52590项，resource/runtime380项；13分片的记录数、bytes/SHA及三项canonical摘要由独立reviewer仅从docs重算，未重复读取大实物或运行探针。真实提取/探针和cache实物SHA属于材料agent的授权执行证据；独审不冒称独立重测。

13查询均独立一次exit0，CMake/CTest4.4.4、Xcode27.1/27A9275、SDK27.0、AppleClang21、GNU Make3.81、Apple Git2.54.0。它们不代表宿主构建或macOS15/Windows/Node/Electron/native资源终态通过。原首轮隐式容器失败、空目的地和原脚本保留，成功提取使用新的目的地。

原Xcode/SDK协议原文和LicenseInfo已保全；GNU Make/Git等独立组件完整notices、cache各image条款仍有缺口。本次不接受新许可、不作采用批准。新执行仅原6465授权13元信息查询及2347授权81实物哈希，后者不运行任何新进程或提取内部image。R5在fe98dab02375362fcc07ca9bb309de17b558fcf2另行静态关闭；产品锁、CMake和driver在本供应提交中均不修改。

最终独立供应报告 `independent-supply-review.md` 为13923B/SHA `45d3857094198233586eeff0564aef4d938fe1f956014b6e3016b1f2e4b856d7`：原阶段10124B正文原样保留，再追加新81项节。固定81项身份读取缺口可按授权记录关闭，其余采用和产物/运行门分别保留。独审仅docs元数据核对，没有重复读取7GB cache或运行版本/构建路径。
