# T02 双审已创建，前台已释放

ZCode `session_8fdff47bb96963af157c498504a58c72`：GLM-5.3／最高／完全访问，实际运行。MiniMax `mvs_06002009bb614b3bb56905f07eb5b240`：M3.1-Flash／xhigh／始终授权，实际运行。均由原T02 owner通过CUA新建，未触碰T06 session/stdio。前台输入窗口现在释放，后台继续，不等待终态。

完整正文及原提示精确包含证据见preflight.json和两份submitted-input；ZCode附件实测31959B/SHA2342bf340a2bff63e5362e18c194f7ecd30868cc6d71689a675b6059a7675f2f等于提交正文；MiniMax在发送前展开成正文后AX逐字包含完整32029B输入。创建/设置/ID/运行AX分别留档。只有实际创建，不记通过。后续监控和报告由原T02负责，保留全部积压。

成功UI路径：ZCode新项目→名称/选择精确隔离树→信任并创建→该项目新任务→完全访问/GLM5.3最高→粘贴全文（自动长附件）→发送。更多→复制会话ID，可在未发送新草稿paste读回后清空；不可贴到运行会话。MiniMax新建项目→本地→选隔离树，发现父项目已绑定时点击“新建任务”，或父项目新任务→工作目录按钮→最近T02隔离树→粘贴全文→在文本框中显示并核完整→发送。会话操作→复制→右键方向键展开→复制会话ID，同样只在未发送草稿读回后清空。MiniMax真实独立session可与原任务并行，无需另起runtime。

只读会话核验：ZCode本任务model-io在 `/Users/kyle/.zcode/cli/rollout/model-io-session_8fdff47bb96963af157c498504a58c72.jsonl`，实际long attachment `/Users/kyle/.zcode/tmp/paste-attachments/2026-10-22/pasted-text-20261022-171404-963c1447.txt`。MiniMax本任务ID由官方复制菜单实读；其存储路径尚待只读核验，不能猜造。

## 前台释放后的纯只读补核

ZCode真实model-io的turn为`turn_37540f4a-27ef-45f8-953c-feb594dc29da`，模型GLM-5.3、`output_config.effort=max`。从真实首次模型请求中的Read结果去除170行显示行号后，重建完整提交正文，SHA与31959B实际附件完全一致；见`zcode-request-readback.json`。

MiniMax当前会话实际存储目录已只读核实为`/Users/kyle/.minimax/v2/sessions/2026/10/22/09-17-33-224-session_bXZzXzA2MDAyMDA5YmI2MTRiM2JiNTY5MDVmMDdlYjViMjQw`，manifest的sessionId匹配，llm-call为MiniMax-M3.1-Flash、thinkingLevel=xhigh。messages首条用户消息的turn为`57f206cd-6e65-4989-aa43-d1a5ef34d3b8`；应用在正文前加入3907字符的runtime上下文、删除末尾一个换行，余下32028B与提交正文去除最后换行精确相等（accepted SHA `9806d53715ace97c702c9cb711bf87ed42ad6500eeef639e997b65de147c9c83`）。没有正文截短；原prompt仍完整保留。见`minimax-request-readback.json`。配置/权限以本任务官方UI读回作证，不用用户全局设置推断。
