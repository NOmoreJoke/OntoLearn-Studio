# T08 Agent与模型：独立实现启动

全文读取 developer-common-instructions.md、decisions.md、T11-release-resource-preflight.md、plan/tasks/requirements 的本项与原PRD FR-800–806/900–902/904、附录F/G.5、11.3/12.2。唯一功能T08，不接手I06原Goal或冻结实现。

工作树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T08-agent-model`；分支 `feature/weekly-t08-agent-model`；base `5f910b52c69d86a1076b2032e5d3c63e715947f3`。先核验实际身份、受保护指南哈希和无路径冲突，建立本功能Goal及 docs/reviews/T08/status.md。

初始独占新增路径：`apps/desktop/src/main/agent/`、`apps/desktop/src/renderer/src/agent/`、`tests/unit/t08-*.test.ts`、`tests/fixtures/agent/`、`docs/reviews/T08/`、`docs/iterations/T08/`。不改I06 model-gateway任何现存文件、contracts/main/preload/App/锁/CI/Python；需要公共或网关接口先精确提案。Python不能持钥或调用模型；不能另开第二网关或绕过字段授权。接入实际I06安全传输仍等待批准依赖。

现在实施独立模块：DeepSeek Chat Completions严格协议codec/响应schema/tool call与reasoning_content多轮关联/能力探测判定；Agent白名单工具描述/受信上下文动作/草稿与版本化Diff建议/失败或过期如实表达；版本化零伪造评估集及合法/恶意/空JSON/错工具参数/超时取消/提示注入的可执行合成反例。所有工具的真实执行等待相应已批准领域服务，不能用test.*改名或生成假查询/推理/场景结果声称通过；无API离线功能可继续。

用户委托已选首选官方 `https://api.deepseek.com` + Chat Completions + deepseek-v4-pro；它是别名，正式模式必须经原评估集固定，记录实际时间/返回model/模式/漂移。使用官方文档核对技术细节，不能凭记忆想象协议；当前无可用API主体/批准消费上限证明，不读取.env/密钥/环境secret，不发真实服务请求、不购买。可用本线独立合成HTTPS服务做协议测试，但不能当真实供应方验收。thinking多轮字段不能为赶工删去，应用strict校验、最终字段授权、确定性真值与人类Diff确认不变。不要把provider codec变成新通用外发入口。

先交本地可审查协议/Agent纯服务和评估manifest、完整输入/预期、独立内审与必要check，缺I06接口给具体输入输出/取消/预算/授权材料需求；未批准代码不消费。字段真实业务溯源及全部实际工具联验/真实API零伪造/页面/同候选双方全新指定审查/门禁push合并都继续本聊天。当前外审预约I05，你不自行操作应用；不在本机开窗口或凭据提示。实际状态/报告给总控，不写root tasks/state。
