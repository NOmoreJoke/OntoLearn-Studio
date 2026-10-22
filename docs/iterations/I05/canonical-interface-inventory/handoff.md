# 既有接口库存交接

这是fixed2cf源码事实库存，不是产品修改或新规范。先读current-disposition.json，再读interface-facts.md及helper-interface-facts.md；api-layouts/digest-recipes/additional-return-layouts提供结构化字段和出处，两个source-inputs清单固定各自窗口。reviews的源码索引只用于审计，不授权D2追到源码或外部helper。

原owner与非D2独立静态审查者受相同绑定：八个初始文件可按接口目的静读；11个追加文件只核指定类型/接口/返回/serializer字段，不读ledger算术、费率、恢复/物理预算算法；resources只准646B函数片段和另行绑定的187B IMPLEMENTATION赋值片段；RootRef只准装饰器/类头/五字段声明。没有运行product/probe/model/import/exec/runpy、第三方schema引擎、测试、安装、网络、DB、native或build。原source树和锁/共享writer、retained两提示和输入副本不变。

源码输出流由不可变Git blob完整保全，命令记录列真实argv/cwd/exit、bytes/SHA与原stderr；不在纯材料内复制整份源码。最初交互式定向静读仅有工具转录，不能在后续补造初始独立双流；首两个索引脚本的外层实际exit0见原工具a1e905/76505c。后续新增摘要不把实际读取冒成执行验证。

固定候选后由独立审查者核源字段、preimage描述、继承顺序、窗口边界、未知项和不越权声明。总控精确接收哪些纯文档后，D2才可采用；不存在“source pin在文档里所以可读源码”的授权。未闭合的旧codec/类型union/同issue/权限保持pending，不能因为库存被接收而签发actual、费用/issuer/17L或运行门。
