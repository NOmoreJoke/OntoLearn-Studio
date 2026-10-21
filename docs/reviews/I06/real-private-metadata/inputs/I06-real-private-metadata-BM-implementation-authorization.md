# I06 B-M：真实私有元数据子集实施授权

2026-10-21。本文件仅在总控实际向原I06负责人发送后生效。固定方案ffb55e0e694bde00b64fed400260e47392aa3554的B-M最小子阶段；B-R/B-L、生产首内容IO、公开宿主和native未授权。按固定主方案44238B/b71667de836ee2bcf8f62107f170e808200a3b4f77c264ed06d7c21e9ceed605及根I06-controller-real-owner-B-plan-review.md的已核边界执行；方案中其他建议不自动生效。

## 1. 单一交付与固定树

由原I06同一功能会话继续，不新建/重建Goal。远端develop已实际核为5f910b52c69d86a1076b2032e5d3c63e715947f3，沿用其为dev。从该批准base新建 .worktrees/I06-real-private-metadata，分支 feature/I06-real-private-metadata，不改6a38旧树或e2c/961原件。先全文读本件与I06-real-private-metadata-fixed-inputs.json，逐项采用两件6a38原字节并单独固定采用ref，回执实际树/分支/base/head、两件bytes/SHA及受保护AGENTS摘要。旧脏改不stage，不使用别树可变环境。

两件采用后只读：apps/desktop/src/main/security/private-resource-inventory.ts（23598B/0f6a2125d5dea53b5e5badde99401086284d4fd776b0cefadad324e408c786e5），tests/unit/i06-private-resource-inventory.test.ts（22330B/7d82c1012bbe7fc35c5faf6eaf167b82d93a357e0b1060db6256ba809a118f49）。不整commit采用A的68路径、不采用cohort、e2c网关/canonical或native代码。

唯一新产品/测试writer：apps/desktop/src/main/security/private-resource-owner.ts、tests/unit/i06-private-resource-owner.test.ts。说明只新docs/iterations/I06/real-private-metadata.md与docs/reviews/I06/real-private-metadata/。完整相对5f为两采用+两新增+这些过程docs；其余产品/配置/依赖/旧测试/AGENTS只读。缺类型/接口先具体报告，不用any、stub、导出别名或第二协议绕过。

## 2. 实际能力与非生产边界

只实现内部Node真实metadata观察供方，配合既定A inventory，实际运行限本阶段专属临时目录。只能directory enumeration和metadata，不打开/读配置、密文、审计、SQLite等正文；不mkdir/写入/删除/更名用户内容，不调用内容仓库/decrypt/safeStorage/凭据/模型。测试建立受控临时文件和真实链接是明确允许的fixture准备与清理，必须同观察操作证据分开。

只接可信内部装配的根描述，拒任意renderer路径、UUID或safe布尔充权；本阶段没有app bootstrap装配，不能把固定userData或演示临时根当FR-002用户位置。真实子集为private-root、credentials、configurations、audit四角色；不合成profile/database/tasks/retirement或替T01登记。全应用仍incomplete/unknown，productionAdmission始终unsupported；Node观察标记node-observed-unfenced，不签发LocationLease、生产snapshot或内容IO权限。

私有根reserve覆盖实际未知/pending/孤儿及未来后代。已存在祖先与prospective组件必须有真实metadata依据；任意ENOENT不当空成功。根/祖先缺失、未知类型/symlink、权限错误、损坏、超限、竞态或初始化失败分别留保守状态，不能丢已知保护。三个bucket及根直属未知项分别归唯一实际供方；不能用旧内容仓库list过滤pending或只列已引用文件。

## 3. 观察、身份、计账

实际目录完整枚举，精确名/parent、类型、volume/dev/fileId/inode/linkCount及观察身份须可追溯。POSIX bigint无损转换为严格字符串身份；不先转浮点。真实symlink不follow；文件hardlink闭合按实际distinct names核，目录nlink不作文件alias证明。未知文件/目录/设备或不支持类型不能忽略以取得complete。32根、32768项、depth128、UTF8路径16384B、A每观察5000ms/并发2及capture界不放宽；在操作/分配前先占有限槽与预算，超额整体unknown不截断。

供方内部串行gate先接纳再启动每个真实FS操作。不得写track(owner, fsCall())这种先发操作后判断的表达式；包装超时/abort只改变逻辑结果，实际FS未结束仍占槽/保保护，真实终态才减槽。close/释放错误保unknown，不伪称OS已释放。无通用IO callback/租约工厂/对外resolver或自报count清零权。可提供精确内部mutation握手和失效机制供未来真实writer使用，但本阶段不接线旧仓库、模型或任意生产writer；测试只能证明这一供方自身计账，不能声称应用所有写者已接入。

观察与同供方mutation串行；mutation先reserve/beginMutation失效旧revision，再发允许动作。跨owner必须同process/profile/revision整轮重取，不能混旧bucket与新root。外部替换/ABA与跨进程写仍未fence；双stats一致不是原子来源，后续按路径reopen仍不获准。Windows真实FileId/reparse/ACL/native缺失保unsupported，不伪造POSIX值充Windows身份。

严格保持原A：同parent+components下旧absent-retired与新present-active即使新id也会被原locationKey唯一拒绝。本阶段必须真实替换文件覆盖并返回unknown、保旧新已知身份及保护，不漏历史、不复活旧id、不直接改A或以只报当前取绿。未来两路径A修订为另行阶段。本阶段retired只为当前进程已观察事实，不声称跨重启完整；无持久来源不能伪mechanism-restored。

## 4. 必须实际验证与交付

专项用每例专属真实临时目录，覆盖缺根/缺父/真实权限可验证部分、完整未知/pending/孤儿、真实symlink/hardlink/final+pending且nlink3、根或祖先rename/同址新inode、目录/深度/bytes/项数上限、观察遇本供方mutation及revision失效、真实未完FS在取消后仍占槽、失败init仍reserve、释放失败保未知、四角色子集不补全八角色、所有结果生产unsupported及首内容IO0。真实原语与错误注入分列：注入close失败不能称OS close故障实证；不能以mock替代所有真实枚举/链接/身份。无用户目录、网络、GUI、e2e/HMR或凭据提示。

完成本阶段实际专项、既定A专属回归、完整正常npm run check及verify:sources。使用本树独立依赖/运行环境、完整真实argv/cwd/环境/stdout/stderr/退出码与首失败；不得共享可变venv。现阶段无新build或平台adapter，不要求无关重打包，目标OS尚未验证如实登记。

独立agent审查实际metadata/竞态/预算和采用范围，真实发现逐项修复复审。冻结本地产品candidate，完整5f→candidate所有路径逐bytes/hash/ref清单、真实执行原件、阶段说明和独审报告后交根读回。不把普通独审当指定GLM-5.3最高与M3.1-Flash xhigh双方通过。两指定模型、父功能、CI、push/PR/合并仍保持原门；本件不允许push/PR/merge。

B-M只证明真实I06私有metadata子集及本供方有限操作计账。B-R控制位置/fresh/bootstrap/安装级writer/持久恢复、B-L仓库/网络/actual lifetime、T01 main/engine/Store/worker/canonical/dispatch以及T03构建源broker、native/VFS/两OS/正式ready/生产接线，均需各自精确前置和另行调度。未获批部分保持原件，不创建替代账本或回退成功路径。
