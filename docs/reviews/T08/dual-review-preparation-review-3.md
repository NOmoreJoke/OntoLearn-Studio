# 双审准备包归档字节独立增量复核

独立agent `/root/t08_internal_review`；manifest SHA256 `33deedd2aaeb18852d513bef4d46ab047a27ded380d7fff9ef03e3eb9e9ba317`。

新增复核理由：材料复核2通过后，首次暂存按现有Git text规则规范化两份控制CSV的CRLF，并将原PRD的Markdown硬换行报作trailing whitespace。该次git diff --cached --check为exit2，不是产品check失败；原文件未改。已仅在本包新增.gitattributes，对inputs/**指定-text -diff，并限定该输入目录重新暂存以保全原字节。原4d85清单保存在包外dual-review-preparation-manifest-before-archive-attributes.json。

原始明确结论：**最终准备包增量复核通过**。

- 新增.gitattributes仅作用本包inputs/**，未改变共享或产品配置。
- 101项文件的工作区、暂存blob与manifest大小/SHA全部一致；两份控制CSV的CRLF原字节完整保留，PRD原始空白未改。
- 25项源码范围、44项差异、828项产品树、完整提示与原验收门均未变化；git diff --cached --check通过。

未改文件，未运行产品检查、探针、API、GUI或指定模型；结论仅针对准备包。前两次原意见及身份保留，不将首次暂不通过改写为通过，不因无变化强设三轮；本次由实际归档字节问题触发。
