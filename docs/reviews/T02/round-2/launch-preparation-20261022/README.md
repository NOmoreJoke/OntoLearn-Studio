# C5 R2 实际派发准备

当前是准备包，两个 actualTask 均为 null，模型／思考／权限实际读回为 false，无本轮指定 Pass。总控创建两棵 detached 树，原 T02 为唯一 setup、后续创建和监控 owner；等待内部 GUI 窗口，不操作其他线任务。

两棵树 HEAD 均为 `7c52e33e92d76bb0a83938a0e50abc40b8fb234e`，产品 `e5ad54e5762157cafe532c2a0c07c22e8dd737cb`。具体 cwd、环境、报告、原始流与元数据映射见 `workspace-mapping.json`。根目录独立 `npm ci --ignore-scripts` 与 `uv sync --frozen` 均 exit 0；各树同名子目录保存全部 setup stdout/stderr、命令与锁前后 hash。没有运行产品验证；全仓必要验证由新审者独立执行。

`input-readback.json` 实际逐树核验完整 130 输入，固定 Git 均匹配；当前仅积压台账追加 C4/C5，与其原 516 历史字节不同，当前字节已另核 7c52。所有 20 产品／测试／fixture、5 harness 及其它输入保持固定。`../preparation-manifest.json` 固定 18 份 R2 payload 的 7c52 Git 内容，自身不纳入自身 hash。两树最新 AGENTS 为 de15，未暂存。

两份 `*-submitted-input.md` 是拟提交的完整正文，仅在不改原 R2／R1 字节的前提下前置实际映射和当前执行补充。31 新用例准确拆为 30 参数化拒绝反例＋1 合法 Unicode 正例；C4 原 Fail／原始首失败、11 项处置和 C5 内审来源继续保留。正常已批准 I04 受控 worker 回归可随必要 suite 执行，不再以泛化禁子进程跳过；被拒物理研究、未签 native 票、HMR 仍不可启动。

本包仅过程文件，保留完整 FR-200–204 和全部父验收。旧 493 两方 Pass 不转授，正式接口／生产／CI／合并／远端核验不在此完成。后续创建时保存真实 ID、逐方设置、完整正文实际接收证据；实际创建之前不得把“准备”写成“运行／通过”。

原始 setup 日志收于本地 Git 是为了在本轮尚无 CI artifact 的情况下保全实际安装命令、真实退出和前后锁记录；不包含凭据或运行库。
