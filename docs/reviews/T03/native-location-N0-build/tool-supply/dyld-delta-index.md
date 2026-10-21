# T03 N0 固定81项dyld身份读取增量

固定81项供应实物的身份与单次完整SHA-256读取已完成；**不等于runtime内部传递依赖、编译后used闭包、条款完整或toolchain采用批准**。所有approval仍false，旧pending清单作为历史原件保持原样。

- 新授权原文：[dyld-delta-authorization.md](dyld-delta-authorization.md)，2347B/SHA `b9da09643f78d64e506e20fd4c81d8b8a058c49134124b18b46e9580b449b95c`。
- 固定输入身份：[dyld-delta-inputs.json](dyld-delta-inputs.json)。只采用原24420B/SHA a0a368清单中的81个精确路径，没有枚举新目录、新链接、其它缓存架构或对象。
- 实际原件：[dyld-delta-complete-inventory.jsonl](dyld-delta-complete-inventory.jsonl)保存全部81个SHA、开始结束、读bytes、逐项前后stat和累计；[dyld-delta-read-events.jsonl](dyld-delta-read-events.jsonl)保存顺序事件。各项只流式只读一次，无复制或内部image提取。
- 实际费用：[dyld-delta-cumulative-read.json](dyld-delta-cumulative-read.json)。旧累计2,699,211,379B没有重置，新增7,046,515,706B，实际累计 **9,745,727,085B**；10GiB=10,737,418,240B，剩 **991,691,155B**。数量guard保持200000，原供应计数62134不变。
- [结果](dyld-delta-read-result.json)：81/81完成，首失败null，无预算/IO/身份变化失败。核对regular类型、realpath、size及O_NOFOLLOW打开fd身份；比较device/inode/mode/bytes/mtime_ns/ctime_ns前后相同，不宣称未采集的其它stat字段比较或跨文件原子快照。
- [候选补充](dyld-delta-candidate-supplement.json)仅追加本次81身份闭合，保留runtime内部image传递、postbuild used与组件条款缺口；没有修改原candidate-pins.json，未将source/toolchain/execution等approval置true。

[记录核验](dyld-delta-verification.json)未再次读cache实物；核81路径/大小/记录、总字节和累计，并核旧24420清单、378预算、candidate、manifest及index仍与既有固定身份一致。全部原raw和旧状态未覆盖。新证据只列在[dyld-delta-manifest.json](dyld-delta-manifest.json)，不修改原evidence-manifest。

本增量没有运行新进程探针、编译、配置、链接、测试、native、FS、GUI或网络，也没有提取image、接受许可、改变系统/SDK/权限、复制cache、写产品/lock、提交或变更Goal。
