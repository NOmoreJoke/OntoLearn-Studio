现有草案路线可保留，建议补正以下五点；无需增加候选文件。

1. **macOS 发布原语可以具体化。**
   `macos-location.cc` 可采用持有父目录 fd＋受控单组件名的 `renameatx_np(..., RENAME_EXCL | RENAME_NOFOLLOW_ANY)`。Apple 固定 XNU `11215.1.10` 头文件含这两个 flag，函数标注自 macOS 10.12 可用；目标卷不支持 exclusive rename 或能力未知则拒绝，不能降级普通 rename，也不用当前新系统的其他 flag 代替 macOS 15 证明。原子不覆盖仍须在实际 APFS 上验证目标冲突及错误分支。[Apple 固定头文件](https://github.com/apple-oss-distributions/xnu/blob/xnu-11215.1.10/bsd/sys/stdio.h)

2. **§3.2 发布耐久顺序需补“发布后”。**
   目前“同步文件及所需目录，再 publish”不足以证明新目录项耐久。建议明确：候选连接/映射实际关闭、必要文件同步 → 不覆盖 rename → 发布后同步受影响父目录 → 核验身份与耐久结果。Apple 明确说明普通 `fsync` 不保证驱动器缓存已落到永久介质，数据库严格顺序需考虑 `F_FULLFSYNC`。但公开文档不能替本方案证明 APFS 目录同步、rename 与掉电后的完整效果；这些仍须实测。rename 成功而后续同步失败，应记录“已发布、耐久未确认”，保留原件且不得重新发布。[Apple fsync](https://developer.apple.com/library/archive/documentation/System/Conceptual/ManPages_iPhoneOS/man2/fsync.2.html)、[fcntl](https://developer.apple.com/library/archive/documentation/System/Conceptual/ManPages_iPhoneOS/man2/fcntl.2.html)

3. **Windows 身份字段可直接冻结到实际 HANDLE。**
   使用 `GetFileInformationByHandleEx`：`FileIdInfo` 的 **VolumeSerialNumber＋128-bit FileId** 比较对象，`FileStandardInfo` 核 `NumberOfLinks/DeletePending/Directory`，另核重解析 tag。查询失败、不支持或身份不稳定均拒绝；不要用路径 lowerCase、截断后的 FileId 或裸数值跨生命周期比较。草案现有 NTFS 首阶段和多链接拒绝方向合适。[FILE_ID_INFO](https://learn.microsoft.com/en-us/windows/win32/api/winbase/ns-winbase-file_id_info)、[FILE_STANDARD_INFO](https://learn.microsoft.com/en-us/windows/win32/api/winbase/ns-winbase-file_standard_info)

4. **share-delete 要按角色设计，不能全程一刀切。**
   缺少 `FILE_SHARE_DELETE` 会限制删除/改名访问，且共享模式持续到 HANDLE 关闭。若 broker 持有阻止 DELETE 的候选文件句柄，之后再开发布句柄可能与自己冲突。建议在 `windows-location.cc` 明确父锚点、活动 DB/sidecar、发布源三类 HANDLE 的 access/share 策略；发布优先使用原受控源 HANDLE，`SetFileInformationByHandle` 的 `FILE_RENAME_INFO` 可指定目标目录 HANDLE，并令 `ReplaceIfExists=false`。仍须先排空 SQLite/SHM 与重复句柄，不能为绕过 sharing violation 偷偷释放身份 fence 后按 path reopen。[CreateFileW 共享规则](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew)、[FILE_RENAME_INFO](https://learn.microsoft.com/en-us/windows/win32/api/winbase/ns-winbase-file_rename_info)

5. **Windows 取消须区分实际调用种类与所属进程。**
   `CancelIoEx` 只请求取消**调用进程**的在途 I/O，不等待完成；返回成功或 `ERROR_NOT_FOUND` 均不能直接释放槽。每次 overlapped 操作须保留 buffer/OVERLAPPED，按原完成通道取得成功、`ERROR_OPERATION_ABORTED` 或其他失败的实际终态。main 对 duplicated HANDLE 调用它，不能据此断言 child 的 I/O 已取消。同步 acquire/create/rename 则必须等待实际原生调用返回；`CancelSynchronousIo` 同样只是取消请求，不是 settled receipt。[CancelIoEx](https://learn.microsoft.com/en-us/windows/win32/api/ioapiset/nf-ioapiset-cancelioex)、[GetOverlappedResult](https://learn.microsoft.com/en-us/windows/win32/api/ioapiset/nf-ioapiset-getoverlappedresult)、[CancelSynchronousIo](https://learn.microsoft.com/en-us/windows/win32/api/ioapiset/nf-ioapiset-cancelsynchronousio)

对应新增验收点只需纳入已有矩阵：APFS 发布前后同步失败与冲突；NTFS 自身 HANDLE 的分享冲突；取消成功但操作正常完成、ERROR_NOT_FOUND、实际未完成；child 在途 I/O 与 main 重复句柄分别关闭。SQLite 原生锁/SHM 兼容性仍须同 build VFS 实测，不能以这些 OS 文档关闭该门。

以上仅只读补核；未修改草案，未运行 native、测试或构建。
