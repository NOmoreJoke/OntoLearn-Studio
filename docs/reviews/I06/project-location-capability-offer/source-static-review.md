新offer的inventory/cohort主线与固定源码一致。已读回当前草案，SHA `647ebc71a51cb6b912aaf9a15c96409cc97a21623cf6bed5c3ea4419e8559eba`；有两处需纠正、一处建议澄清：

1. **第24行的4096/10000不是恢复inventory上限。**
   `ciphertext-repository.ts:64–70`的scan没有4096条上限；4096只在write准入检查（87–88）。`persistent-audit.ts:94–111`的recover也没有10000条上限；10000只限制append（118）。建议改为“配置journal最多1024；密文新增写入阈值4096、audit追加阈值10000；恢复扫描不能据这两个阈值截断或宣布完整”。底层目录枚举另有限11024项。

2. **第5节完整持有者清单漏了兼容局部探针。**
   `engine.ts:530–535`的 `readEngineHealth()`会局部创建supervisor，finally调用stop。固定desktop源码没有调用它，可标“当前未接入”；未来不能绕cohort使用。其余直接持有者已齐：main全局、TaskService、ModelGatewayService、StoredResultSource；Application/Projector为间接source链。

3. **第119行late-install宜明确是未来重初始化缺口。**
   当前e2c只启动一次 `initializeModels()`（index310），并在owner返回后检查quitting（123–125）。现无cohort/generation fence，但不宜写成已发生的并发旧初始化覆盖新组。可写“若引入重复/并发初始化，现接口没有防旧结果安装的cohort fence”。

其余重点核对结果：

- **完整userData保护与精确DB例外已写清。**第35行与默认 `userData/engine.sqlite`（e2c index223；5f index123）相容：容器保护保留、模型整根绝不例外、DB能力须按真实对象/用途另冻结。没有要求改961或删除DB保护。
- **初始化失败不当空inventory写准。**三个repository.open都会读内容；密文listBindings也读密文JSON，不能复用为metadata-only恢复。PrivateDirectory.open还可能已mkdir/fsync后失败，reserve必须先于这些动作。
- **pending/retired事实写准。**list过滤pending但不删；发布失败可留下final/pending；旧journal、未引用密文无现成退役清理协议。当前没有active/retired inventory，未来持久退役记录仍是待批准项。
- **close不等于settled写准。**source abort可先结束包装Promise；engine RPC仍在途。PrivateOperations等待登记操作；model-service.close只等serial tail；Application.close为void；Supervisor.stop不等待child close。5秒退出race不能作为资源释放receipt。
- **同UUID与普通恢复区分写准。**TaskService同UUID不触发模型hook，ModelGatewayService同UUID早返；主动重开/迁移确需新lifecycle接口。普通renderer恢复/同Supervisor瞬断不能因此擅自重置grant。
- **加密backend需单列事实。**`createElectronCredentialBoundary()`只检查main/app-ready；真正backend检查在credential store/read时。模型初始化成功不证明Keychain/backend可用，也不影响metadata能否独立complete。

只读沿用已有固定源码核对；未写文件、未重测或打开GUI。
