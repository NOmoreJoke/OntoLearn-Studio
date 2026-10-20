# develop 门禁读取

2026-10-20，本开发会话只读查询 GitHub：

- `gh api repos/NOmoreJoke/OntoLearn-Studio/branches/develop/protection`：HTTP 403，GitHub 返回 Upgrade to GitHub Pro or make this repository public to enable this feature。
- `gh api repos/NOmoreJoke/OntoLearn-Studio/rulesets`：同样 HTTP 403。

不据此声称已读取全部保护配置。此项不是允许绕过检查的证据；指定双审全部通过后才push/PR，等待实际CI和GitHub可合并状态，使用普通merge，不使用admin/bypass。若GitHub实际拒绝合并，保留受阻记录。
