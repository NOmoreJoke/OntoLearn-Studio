# R2 实际 setup 收据

固定 packet candidate：92652c2db7ad600e9c4ab304812fede7943a8f01；实际副本与其中 physical-copy-spec-r2.json、本人完整 prompt 的冻结字节一致。两 wrapper 均为普通独立目录，无 .git、branch=N/A，每根仅有本人一份当前 prompt。

两根各完整 materialize 22492 个 member，3006 个实际 payload inode 与19486 个后向根内 hardlink。全部路径/类型/目标在写数据前已核，每个独立 inode 完整 SHA/Git blob 读回且每路径匹配；16 namespace 分离，未把互斥版本拼成产品。根内完整文件/目录/bytes/mode/inode 清单见两 preflight，逐件源ref与hash见本人 instructions/own-input-manifest.json。

共同输入60件，加本人固定输入4件和本人实际 manifest1件，每根共22557文件。输入0444、目录0555；本人 reports/scratch/review-status 为0700。两根共享 inode=0，input/output共享inode=0，无symlink/特殊文件/共享.git。真实空 baseline 和当前空输出已核；不是应用创建后的 metadata growth 实测。

旧134件当前与1106固定原件全等，bundle84876346B SHA4bbbd798e6c7a67153db51e185c8795d9ac3509cc4442a81e2071bf319dfaa12不变。R1归档未重压，旧作者器和原首失败未改。R2首次formatter活跃日志样式失败与完整流封存；随后静态formatter/check和staged whitespace准确记录于新顺序收据。

结论仅 input-copy-ready。当前指定模型任务0、真实任务ID/模型设置读回pending、应用metadata增长未测，R2独立delta审查pending；未运行产品/测试/探针/生成器/native/DB/network/install/GUI/模型，无push/PR/merge。
