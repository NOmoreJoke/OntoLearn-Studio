# 第五新输入：单 Mac 终点诊断构建前独立审查

2026-10-22。结论：未发现阻断当前固定候选按授权执行唯一第五次新输入构建的问题。真实授权／单Mac采用／锁产品链成立，完整12、九源供方身份和锁六叶差异均核同。此结论仅接受有界源码采用与构建前静态检查；没有证明四终点诊断已出现、实际errno／UNSUPPORTED根因、EXCL或N0通过，也不授权产物运行。

## 授权、源收件与真实ref

已全文读取 `authorization.md.raw`：3898B／SHA-256 `bb193a8f8a54e4221388eb1f649798e8c4a58f4e17964e4b61bcbedc34a4edaa`。工作字节与真实授权提交 `a447556e2cbbd81ede38bf2148714e5f1f59fbfd` blob完全相同，其父级为d51a0555e6feb062fc935173222cc142687901a5，只新增授权原件。

已全文读取 `I06-source-root-closure.md.raw`：1221B／`428615e7039850f308d39212706260c6ad6d01b286d94c9afe1de6e366d1eea3`，与authorization-receipt固定值相符。它记根已审6798B源增量、四终点未实际观测，既有完整check不编译C++。本审不再重读该长审或旧算法；源收件自身不授运行。

实际链为a447556 → `0497e0ea48062bb45f8ef25c2949adc61cec3564`（只采用platform_macos.cc）→ `e7cbf3e829349a488fd6f99ae537a4611edbc1eb`（只改toolchain-lock.json）。没有wholecommit采用供方或改T03构建算法。

`provider-handoff.json.raw`：3348B／`78847490d4fba70e8e5a4b2b2929dac8294a65254fbe6d07cf2795ea8bca077c`，逐字节等6fda0648299ae7e7d7d049ad5852e6d61b1618c5指定unsupported-endpoint-diagnostic/provider-handoff.json blob；九pin去说明字段后逐项等当前锁九pin及完整12前九项。handoff的无build/run授权字段是供方路由边界；本轮一次构建另由a447556授予，不能把路由材料冒作运行许可。

独立逐Git blob比对fc9853f3521faced3a3b88ab8254310c9748a6a6与fc6237e8cad1a4043d46a1c7198439f1da06ad67，唯一变化为Mac8670B／`e1fbbcd9c9b73916bd9a030da8bc237dd46230fdd8d0366f0e2424168d4cd71a`；其余八源逐字节相同。当前九源均等fc9853，Mac采用提交blob亦精确等该供方。

## 实际Mac小diff与errno边界

本审读取Git实际单文件diff，与采用patch一致：新增cstdio及两个内部诊断helper，只在既有clock、duplicate、fstat、acl-null失败终点附加输出。

clock_gettime仍只调用一次；原短路条件依次展开为调用失败、negative-sec、range，顺序和返回UINT64_MAX保持。syscall失败立即捕获errno，fprintf后恢复该值；非syscall clock理由保存／恢复进入诊断时的errno。duplicate与fstat先保存errno并按原error_status算status，仅UNSUPPORTED分支记录并恢复errno；其它status返回保持。acl-null仍无条件返回NL_UNSUPPORTED，保留原查询一次及errno值，没有增加ACL重试、成功回退或放宽安全判断。

stage/reason均来自固定字面量，已有源收件的49B/96B结论只是静态格式上界。新增stdio诊断有I/O成本，不能称零成本；保存errno也不等于本审验证过真实输出或运行时errno。上述只审授权内diff，不重复旧算法或宣称具体002失败终点已经定位。

## 完整12及锁六字段

`approved-input-manifest.json`：2544B／`dd1ea0ed200156a4d0b2898853d6c1c96c4b540bb72aac71c96bf8781096ee53`。12路径唯一；本次逐项只读计算当前工作文件bytes／SHA，全部吻合。source/process/auth/adoption/product各ref与实际对象及供方匹配。

锁当前10474B／`2aadb0453b6c474f096445b979678b93ca9075a1c2d520f7ed851a8bbbada682`，工作字节等e7cbf3产品blob。相对d51旧锁，拒重复键JSON解析及递归全对象比较，实际恰六叶：source.ref改fc9853；source.files[2].bytes由7675改8670及该项SHA更新；source.approval.reference、Darwin toolchain approval.reference、Darwin/core execution.reference三项均指向真实a447556。approved保持true，八源pin、API3／contract／staticassembly、全部供应descriptor、selector、flags／limits、environment及其它权限不变；Node／Windows／addon／fixture-addon未扩大。

CMake19815B／`f2b5522b92c5dfc9724b95c35b876ce5015a4955385f614a6da20fb9bce57645`、driver30056B／`ca4ef93024762ae5dfd3dc95133f8ab28ae2e63048af0b3a658bfeb98f62045c`保持冻结。因此本轮没有T03算法、CLI或命令计划修改，不重新维护或重审旧实现。

## 静态结果、预算与读取界

已读新锁JSON／Prettier原回执及完整双流：exit0、stdout66B为格式通过信息、stderr0B。本审另独立解析锁。`static-validation.json`：309B／`87aac2f97418f624bf870821620a92b39e84572ae0d225fcc9a6b9ac82d44a2d`。未变driver的既有语法证据沿用，未重跑Node --check或npm整套；637TS／1052Python／1native skip属于I06既有源证据，不是T03新执行，也不证明C++编译或native成功。AGENTS/common同字节复用由owner receipt保留，本审只核小receipt，不冒称新增全文重读。

`read-and-record-plan.json`：1425B／`c1ea1367b5b86cab8d87d8c2d5633b834a296f21747d59cf9339cf80dff4638a`。独立算式：72958464344+17755667816+134217728=90848349888B，低于96GiB=103079215104B，余12230865216B。原供应9745727085B独账保留，combined声明100594076973B／guard112824942189B。必要小源Git／静态／review／closing读取由本轮128MiB预付，不把该预算当实际OS IO。

实体342176+85544=427720，低于500000。metadata1556431+171088+2000+15000+15000+10000+15000=1784519，低于1800000，余15481；root另15000与作者票分别保留，旧票不释放、历史超255／关闭界和未知drain不改。余量有限不构成省略必要动作的理由；新动作若不能覆盖须执行前报具体差额，不擅自抬guard或记未知为0。actual OS/compiler/loader IO仍未知，不量化性能。

本审仅核12小工作文件、九源新旧18个Git blob及少量授权／provider／lock／采用对象、小JSON和patch。保守宽访问上界256，低于本审1000，计入pre2000；应用累计读取保守小于1MiB，低于4MiB，计入新128MiB。未读42772清单或SDK／供应实体，无工具／编译／native实验。

本审一个只读辅助Git查询曾误假定root-closure副本也属于授权commit，返回exit128（工具0e9bc1）；实际授权commit只固定授权原件，与任务范围相符。随后按1221B原件及receipt核该副本，不把它写成缺权限，不重复源hash、不修改任何文件消错。此核对修正计入上述读取上界。

## 后续执行范围

owner固定新process HEAD及完整12后，可直接按授权执行一次原driver CLI；原13命令、parallel2、每命令600000ms、shell:false、固定DEVELOPER_DIR/CMake/gnumake供应及core/child两目标保持。try_compile只编译链接，禁try_run、CTest和任何产物运行。供应／前门pin不匹配须保原件回报，不自动换工具、补trace、提权或第六次构建。

本审只新建此报告，没有修改产品或其它证据，没有运行构建、verify-only、工具探针、测试、native、GUI/桌面/HMR或付费服务。新digest／产物、真实依赖增量、终点诊断或后继调用须按新窗口后验收件；成功也仅built-unverified/NOT_RUN，根因／EXCL／目标OS／父N0／指定双外审与CI门继续开放。
