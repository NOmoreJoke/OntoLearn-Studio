"""Pure document materialization. Reads fixed Git JSON/text; no product imports or calls.

This script does not generate a lock, approval, build or runtime observation.
Its only write roots are the two new protocol-v3 documentation prefixes.
"""

import copy
import hashlib
import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[4]
HERE = pathlib.Path(__file__).resolve().parent
OUT = ROOT / "docs/iterations/T03/i05-semantic-build-protocol-v3"
OLD = "docs/iterations/T03/i05-semantic-build-protocol/"
D1 = "docs/iterations/T03/i05-semantic-D1-plan/"
R1 = "docs/reviews/T03/i05-semantic-D1-plan/"
R0 = "docs/reviews/T03/i05-semantic-build-protocol/"
FIXED = "86d6297a8cac5ad780f1be4416ec9052b82f3aaf"
D0 = "c3eb0694daad26527cc3a1eb0127ed5033f2be25"
SCHEMAS = ["build-provenance.schema.json", "build-receipt.schema.json",
           "runtime-validation-receipt.schema.json", "runtime-header.schema.json"]
inputs = []


def identity(raw):
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def fixed(path, ref=FIXED):
    raw = subprocess.check_output(["git", "show", ref + ":" + path], cwd=ROOT)
    assert (ROOT / path).read_bytes() == raw, ("live-input-drift", path)
    if not any(r["path"] == path and r["ref"] == ref for r in inputs):
        inputs.append({"ref": ref, "path": path, **identity(raw),
                       "gitBlob": subprocess.check_output(["git", "rev-parse", ref + ":" + path], cwd=ROOT).decode().strip()})
    return raw


def load(path, ref=FIXED):
    return json.loads(fixed(path, ref))


def put(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def at(value, pointer):
    for part in pointer.removeprefix("#/").split("/"):
        key = part.replace("~1", "/").replace("~0", "~")
        value = value[int(key)] if isinstance(value, list) else value[key]
    return value


def replace_at(value, pointer, expected, new):
    parts = pointer.removeprefix("#/").split("/")
    for part in parts[:-1]:
        key = part.replace("~1", "/").replace("~0", "~")
        value = value[int(key)] if isinstance(value, list) else value[key]
    last = parts[-1].replace("~1", "/").replace("~0", "~")
    last = int(last) if isinstance(value, list) else last
    assert value[last] == expected
    value[last] = new


def change_strings(value, mapping):
    if isinstance(value, dict):
        return {k: change_strings(v, mapping) for k, v in value.items()}
    if isinstance(value, list):
        return [change_strings(v, mapping) for v in value]
    if isinstance(value, str):
        for old, new in mapping.items():
            value = value.replace(old, new)
    return value


def main():
    assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip() == FIXED
    for manifest_path, ref in [(R1 + "final-plan-manifest.json", FIXED), (R0 + "final-manifest.json", D0)]:
        m = load(manifest_path, ref)
        for row in m["files"]:
            raw = fixed(row["path"], ref)
            assert identity(raw) == {k: row[k] for k in ["bytes", "sha256"]}

    delta = load(D1 + "forward-schema-change-index.json")
    dependencies = load(D1 + "dependency-plan.json")
    union = load(R1 + "union-source-audit.json")
    guard = load(D1 + "guard-scope-matrix.json")
    originals = {n: load(OLD + n, D0) for n in SCHEMAS}
    new_schemas = copy.deepcopy(originals)
    actual_schema_changes = []
    for row in delta["schemaLiteralChanges"]:
        replace_at(new_schemas[row["schema"]], row["pointer"], row["old"], row["proposed"])
        actual_schema_changes.append({"schema": row["schema"], "pointer": row["pointer"], "old": row["old"], "new": row["proposed"], "kind": "D1-indexed-version-literal"})
    titles = {
        "build-provenance.schema.json": "Complete proposed build provenance v3; exact26 dependency contract; later actual evidence required",
        "build-receipt.schema.json": "Immutable build receipt v3; later runtime validation is a different document",
        "runtime-validation-receipt.schema.json": "Later immutable runtime validation receipt v3; full actual failures preserved",
        "runtime-header.schema.json": "Exact runtime header payload v2 for protocol3/profile4",
    }
    for n, doc in new_schemas.items():
        for key, value in [("title", titles[n]), ("$comment", originals[n]["$comment"].replace("protocol.md v2", "protocol.md v3.0.0").replace("consumer-contract.md v2", "consumer-contract.md v3.0.0") + " Complete protocol3 forward design; source lock26, canonical23, supplier22, runtime8 and source33 are distinct. No execution authority.")]:
            actual_schema_changes.append({"schema": n, "pointer": "#/" + key, "old": doc[key], "new": value, "kind": "descriptive-metadata-only"})
            doc[key] = value
        put(OUT / n, doc)

    responsibility = load(OLD + "field-responsibility.json", D0)
    for row in delta["fieldResponsibilityLiteralChanges"]:
        replace_at(responsibility, row["fieldResponsibilityPointer"], row["old"], row["proposed"])
    responsibility["format"] = "i05-d0-field-responsibility/4"
    responsibility["normativeCrossFieldRules"] = "protocol.md v3.0.0 CR-S/CR-A1/CR-A2/CR-C/CR-A3/CR-A4/CR-R/CR-H plus consumer-contract.md v3.0.0 sections5-6; dependency-specification.json and guard-adoption-matrix.json are separate exact source/guard obligations, not runtime receipt fields"
    put(OUT / "field-responsibility.json", responsibility)

    package_rows = []
    partitions = dependencies["baselineLockFullTextPartition"]
    for row in union["packages"]:
        name = row["name"]
        preferred = "mappingProduct" if name in ["defusedxml", "et-xmlfile", "openpyxl"] else "profileProduct"
        candidates = []
        for source in row["sources"]:
            block = next(p for p in partitions[source["label"]]["packages"] if p["name"] == name)
            candidates.append({**source, "exactOriginalBlock": block["exactBlock"], "blockBytes": block["blockBytes"], "blockSha256": block["blockSha256"]})
        package_rows.append({"name": name, "version": dependencies["proposedUnionPackageVersions"][name],
                             "referenceSelection": preferred, "originCandidates": candidates,
                             "combinedMetadataRequiresNewActualLock": name == "ontolearn-engine",
                             "actualCombinedPackagePin": None, "selectedInstalledArtifact": None,
                             "licenseApproved": None})
    spec = {"format": "i05-protocol3-exact-dependency-specification/1", "status": "complete normative design; actual lock and resolver unproduced",
            "lockPackageCount": 26, "lockPackageVersions": dependencies["proposedUnionPackageVersions"],
            "dependencyDirectRequirements": dependencies["preferredParentUnionDirectRequirements"],
            "requiresPython": dependencies["requiresPython"], "rootWorkspacePyprojectChange": False,
            "rootDevConstraints": dependencies["rootDevConstraints"], "semanticRuntimeDistributions": dependencies["runtimeEight"],
            "packageSources": package_rows, "exactOriginalLockHeaders": {label: {k: v for k, v in value.items() if k != "packages"} for label, value in partitions.items()},
            "crossFieldRules": [
                "Exactly26 unique normalized package names and exact versions;6 direct engine requirements, metadata.requires-dist and dependency edges must agree in the actual future lock.",
                "Reference blocks are immutable historical text, not a composed uv.lock. Preserve complete URLs/hash/size/upload-time, all platform wheel/sdist, registry, markers, extras and workspace/dev/build metadata. No resolver/install was run.",
                "Shared18 versions/artifacts agree statically; engine six-item dependency metadata requires deliberate actual lock generation. Preserve profile rdflib html extra and html5rdf edge; setuptools trailing whitespace difference is historical text only.",
                "openpyxl depends on et-xmlfile; retain defusedxml and all semantic dependencies. No dependency removal to make23 and no unreviewed version/artifact/marker/extra/hash change to reach26.",
                "Actual selected artifact/installed METADATA/RECORD/LICENSE/NOTICE/COPYING and owner obligation/classification remain unavailable. Lock hashes do not prove installed artifacts or licenses.",
                "Dedicated semantic runtime remains8 with actual build tools separately bound. A parent that includes XLSX requires its own whole-parent dependency/runtime/license profile; this schema does not authorize an11-runtime parent by implication.",
                "Any future resolver difference requires exact delta, first stdout/stderr/exit and root/fresh acceptance before a new dependencyRef can be approved.",
            ], "actualDependencyRef": None, "actualCombinedLock": None, "actualEnginePyproject": None, "executionAuthorization": False}
    put(OUT / "dependency-specification.json", spec)

    guard["format"] = "i05-protocol3-guard-adoption-matrix/1"
    guard["status"] = "complete normative source/owner obligations; no actual guard implemented or source adopted"
    guard["scopePolicyDocument"] = "guard-migration-contract.md"
    put(OUT / "guard-adoption-matrix.json", guard)
    strategy = fixed(D1 + "guard-migration-strategy.md").decode()
    strategy = strategy.replace("# Guard 迁移策略与完整43→33/58作用域", "# 协议3 Guard 迁移合同与完整43→33/58作用域")
    strategy = strategy.replace("此文件与guard-scope-matrix.json共同修复独审F1；后者是全部58路径的完整逐项账", "此文件与本目录guard-adoption-matrix.json共同定义全部58路径的完整逐项账")
    strategy = strategy.replace("guard-scope-matrix.json", "guard-adoption-matrix.json")
    strategy = strategy.replace("本方案", "本规范")
    strategy = strategy.replace("F1只由方案完整性修复申请独立delta复核，不自签运行或审查通过。", "D1的F1只在纯方案层关闭；本完整新规范另待fresh独审，不自签运行或审查通过。")
    (OUT / "guard-migration-contract.md").write_text(strategy)

    profile = load(OLD + "profile-descriptor.json", D0)
    old_profile = copy.deepcopy(profile)
    profile.update({"format": "i05-semantic-build-protocol-profile/4", "status": "complete-protocol3-author-candidate-fresh-review-pending", "id": "i05-source-package-parity-v3", "protocolVersion": "3.0.0", "baseRef": "5f910b52c69d86a1076b2032e5d3c63e715947f3", "schemaIds": [new_schemas[n]["$id"] for n in SCHEMAS],
                    "lockPackageCount": 26, "lockPackageVersions": dependencies["proposedUnionPackageVersions"],
                    "dependencyDirectRequirements": dependencies["preferredParentUnionDirectRequirements"],
                    "semanticRuntimeDistributionCount": 8, "sourceDeclaredSupplierCount": 22, "canonicalModuleCount": 23,
                    "dedicatedSourceInputCount": 33, "dependencySpecification": "dependency-specification.json",
                    "guardAdoptionMatrix": "guard-adoption-matrix.json", "independentParentProfile": None,
                    "historicalDescriptorBaseRef": old_profile["baseRef"], "sourceNormativeDesignRef": FIXED})
    profile["openDeltas"][0] = "Complete protocol3/profile4/schema/field responsibilities fresh independent review and exact root design acceptance"
    profile["schemaIdentitySource"] = "exact current path/bytes/SHA in external protocol-v3 candidate manifest; old D0 manifests and any old Pass remain historical and do not approve this version"
    profile["guardScopes"] = {}
    scope_specs = [("historical", "historicalScope", "historical-a4d-43/1", 45, "HIST-83/default-original"),
                   ("dedicatedSemantic", "dedicatedSemanticScope", "semantic-v3-33/1", 33, "dedicated-exact-single-build-flag"),
                   ("parentDefault", "parentDefaultScope", "parent-default-v3-58/1", 58, "default-and-preserved-exact-legacy-flags")]
    for name, key, version, count, entry in scope_specs:
        paths = [r["path"] for r in guard["rows"] if r[key]["applicable"]]
        assert len(paths) == count
        profile["guardScopes"][name] = {"scope": name, "guardVersion": version, "sourceGuardPaths": paths,
                                               "guardManifest": {"normativeDocument": "guard-adoption-matrix.json", "actualApprovedManifestPin": None},
                                               "entryBehavior": entry, "ownerAdoptionStatus": "not-approved; exact owner actual pins and scope/root resources required",
                                               "sourceRoot": None, "outputRoot": None, "environmentRoot": None, "actualGuardSourcePin": None,
                                               "executionAuthorization": False}
    put(OUT / "profile-descriptor.json", profile)

    protocol = fixed(OLD + "protocol.md", D0).decode()
    start = protocol.index("## 2. CR-S")
    protocol = """# T03 I05 semantic build protocol v3.0.0

2026-10-22。本目录是前向完整新规范候选，待原T03全文接收、固定candidate及fresh独审、总控精确设计接收；不是旧D0的覆盖或产品实施。D1纯方案已由总控限定接收（旧过程86d6297a8cac5ad780f1be4416ec9052b82f3aaf）；旧D0 c3eb0694daad26527cc3a1eb0127ed5033f2be25 的66件与23包规范完整冻结。新版本完整保CR来源、路径、真实CodeType、失败/信任/收据/观察合同。所有future actual pins保持null/空，executionAuthorization=false；没有安装、resolver、build或runtime实例。

## 1. 固定输入、版本和采用方式

正式批准base=5f910b52c69d86a1076b2032e5d3c63e715947f3；本纯文档作者树冻结输入HEAD=86d6297a8cac5ad780f1be4416ec9052b82f3aaf（不是新组合产品base）。旧offer/adoption/D0/D1完整历史保留，输入与本目录原bytes分别由包外input-manifest/candidate-manifest列身份；不预填未来自身commit/hash。JSON Schema2020-12 shape与本文、consumer全部跨字段规则同时必需，版本本身不授权产品读取。

| 文件 | 完整版本 / ID | 用途 |
| --- | --- | --- |
| build-provenance.schema.json | i05-source-package-parity-build/3 / urn:ontolearn:i05:source-package-parity-build:3 | E0后置包内完整构建声明 |
| build-receipt.schema.json | i05-build-receipt/3 / urn:ontolearn:i05:build-receipt:3 | E0包外immutable build receipt |
| runtime-validation-receipt.schema.json | i05-runtime-validation-receipt/3 / urn:ontolearn:i05:runtime-validation-receipt:3 | 后出完整runtime receipt |
| runtime-header.schema.json | i05-semantic-runtime-header/2 / urn:ontolearn:i05:runtime-header:2 | source/frozen完整header与失败观察 |
| profile-descriptor.json | i05-semantic-build-protocol-profile/4，id=i05-source-package-parity-v3 | 完整未批准profile |
| consumer-contract.md | 3.0.0 | 完整source/frozen/caller strict合同 |
| field-responsibility.json | i05-d0-field-responsibility/4 | 全部1241显式property pointer与actor/18安全码 |
| dependency-specification.json | i05-protocol3-exact-dependency-specification/1 | 全26包版本、各原block及全部artifact来源与六直接项规范 |
| guard-adoption-matrix.json / guard-migration-contract.md | 三scope完整逐项账/行为合同 | 历史45、semantic33、parent58互不混用 |

D2只可在新规范精确接收后按四schema同版映射、另授权窗实施新consumer并供新第23 pin；旧2cf仅祖先。T03四writer/锁与原I05/T01共享源各有唯一owner，产品/锁/collector/consumer没有在本窗口修改。G02/G03 business carrier由I05单独作者维护，本文不新增其schema；精确接口依赖另见interface-adoption-contract.md。旧T05实现限定收件及allocation/oracle后续独审原门不变。

""" + protocol[start:]
    protocol = protocol.replace("完整23包锁", "完整26包锁")
    protocol = protocol.replace("parent 原默认/旧 flag/43 guard 保留。", "parent/default遵守本目录完整三scope迁移合同：历史a4d根保原43+两writer45，新semantic只33，新parent58逐owner供兼容实际pin后才具构建资格；不能把9冲突的两版字节同时要求在同一checkout，也不删除21old-only或永久拒旧flag。")
    protocol = protocol.replace("完整26包锁（workspace/dev/build-tool/marker/extra/全平台wheel与sdist）由外部 source/witness 绑定；", "完整26包锁（workspace/dev/build-tool/marker/extra/全平台wheel与sdist）严格按本目录dependency-specification.json全部26名版本和六直接依赖，由外部source/witness绑定；")
    protocol = protocol.replace("本完整 D0", "本完整v3").replace("本D0", "本v3").replace("D0/D3 修订", "新协议/D3修订")
    protocol = protocol.replace("后继receipt版本为i05-runtime-validation-receipt/2；build provenance/receipt仍保持原版本、not-executed/null，不回填。", "后继receipt版本为i05-runtime-validation-receipt/3；build provenance和build receipt均为本目录/3版本，build receipt永久not-executed/null，不回填。")
    protocol = protocol.replace("D0 有限", "历史D0有限")
    protocol = protocol.replace("本窗自检仅普通Git/文件、stdlib JSON/AST/re/数学和已有Prettier；无已命名获准离线JSONSchema引擎，本轮未探环境、未安装、未网络。", "本窗只做普通Git/文件、stdlib JSON/哈希/TOML/有限关系及已有Prettier文档检查；无已命名获准离线JSONSchema引擎，本轮未探依赖环境、未安装、未网络。")
    protocol += """

## 10. CR-S26：依赖全集、版本与独立parent前置

dependency-specification.json逐26标准名保精确版本、profile/mapping完整原block、所有registry/markers/extras/workspace/dev/build字段和全平台wheel/sdist URL/hash/size/upload-time。六直接项恰defusedxml0.7.1、et-xmlfile2.0.0、openpyxl3.1.5、pyparsing3.3.3、pyshacl0.30.1、rdflib7.6.0。未来真实pyproject与lock中engine dependencies/metadata.requires-dist必须逐项同六项。共有包优先profile原block，三XLSX新增取mapping原block；engine合成metadata须另授实际resolver/锁维护窗口，不把原block拼接当真实锁。保rdflib[html]→html5rdf、openpyxl→et-xmlfile、全部平台marker和tools；不得删依赖凑23或擅自升级/改artifact来凑26。

26是完整workspace/dev/build/全平台package记录，23是canonical actual/frozen，22是source供应声明，8是专用semantic distributions，33是专用source inputs。六直接项不等八runtime；额外XLSX锁来源不自证安装、collect进专用artifact或许可证。实际artifact/METADATA/RECORD/LICENSE/NOTICE/COPYING和obligation/classification在E0获准后逐项补证，当前全部licenseApproved=null。任何新resolver/marker/extra/artifact差异须保首错、完整delta并重收，不得借本设计预签。

新parent/default58必须有独立parent guard/profile、完整依赖/runtime/许可闭包和root批准；不能在semantic33 provenance中混58源、把8改11或借semantic receipt证明wholeparent。guard-adoption-matrix完整58逐owner账保9冲突=2依赖+7源资源、21old-only/new-only11、mapping4；actualApprovedPin等保持null。历史独立根保23包旧源45 guard及原83入口；新semantic33、新parent58分别获批源/输出/env根并明确caller选择。任何owner兼容供pin、旧83/默认/原flags迁移回归缺失均阻断parent build eligibility，不阻断对其它纯规范逐项审查。

## 11. 前向采用、接口与文档验证边界

schema-change-index.json穷举14处版本literal及title/comment描述元数据delta；除此全部四schema节点逐值同旧D0。field-responsibility保全部1241 pointer、required、type、enum、$ref及actors/exactCodes，只同步10处shape.const、format/4与3.0.0规范链接。profile新增26/23/22/8/33计数及三scope源账；新descriptor与schema/collector必须在被依赖前具有实际固定Git/bytes/hash并获精确接收，本文和candidate manifest不充当授权签名或运行批准。

source declared22与actual23、frozen23与新consumer pin、header/2嵌入receipt/3、lock/dependencyRef两账、四writer和toolchain/root信任映射全部同版。任何old-v2 approval/Pass、旧profile配新锁、旧consumer2cf SHA冒新码均拒绝。I05业务carrier G02/G03的实现、schema字段与本项目独立新版本采用由其owner提交，本目录只精确列接口依赖，不代其定义或抢写。

本目录附有限synthetic设计反例与stdlib文档检查；不运行产品或import产品、不执行旧probe/collector/helper。有限shape/关系/字段/源集合与原hash检查不是离线JSONSchema2020-12引擎认证，也不是resolver/安装/compile/archive/loader/runtime/业务证据。旧D0/旧Fail/旧清单全部不改，新规范fresh独审与总控精确采用之前保持未采用。
"""
    (OUT / "protocol.md").write_text(protocol)

    consumer = fixed(OLD + "consumer-contract.md", D0).decode()
    consumer = consumer.replace("contract v2.1.0", "contract v3.0.0").replace("本件是 D0 完整消费合同", "本件是协议3.0.0完整消费合同").replace("本D0", "本v3")
    consumer = consumer.replace("runtime-validation-receipt/2", "runtime-validation-receipt/3")
    consumer += """

## 7. protocol3/profile4/26包的精确采用映射

只接本目录四schema：build provenance/3、build receipt/3、runtime validation receipt/3及header/2，profileId固定i05-source-package-parity-v3；receipt内嵌headerPayload必须与独立header完整shape同版。完整dependency-specification.json要求lock26精确标准名/版本/全部平台artifact与六直接项，dependencyRef绑定真实新pyproject/lock，两账身份全同。八runtime的名字/版本/selectedArtifact/RECORD/许可仍逐项核，不生成26 loader或把source声明变26。source声明22、actual canonical23、frozen声明23与新approvedConsumerPin照CR-H处理，old2cf不自签新pin。

root/caller批准入口必须钉同版schema/profile/consumer/lock/wrapper/collector/新composition及实际build receipt原bytes，header/2→receipt/3原raw逐字段回绑。旧v2 receipt/approval/指定Pass和旧profile+26锁混搭无效，版本字符串和SHA不是可信授权签名。真实信任来源/签名机制由root后续独立明确，本件不发明密钥、证书或现成验签函数。

semantic-v3-33/1与parent-default-v3-58/1以及historical-a4d-43/1必须按本目录完整guard合同分域；parent有独立profile/guard、依赖/runtime/许可及owner实际pins，不借本semantic8项schema证明wholeparent。新parent同词法旧profile入口须保83原输入/报告false/限额/真实失败语义，由I05/T01适配新7源资源并供兼容pin后再验证；任何未完成不由caller擅借历史exe、cwd或basename补救。

G02/G03 business carrier的schema由I05唯一作者在其新prefix完整定义、独审并共同精确接收，本目录仅列interface-adoption-contract.md依赖。消费其实际新规范前不拼入产品或更改typed业务payload，不因carrier提案取消本合同原全字段/失败保存/代码域/信任门。当前所有新actual pins/null、executionAuthorization=false继续保持；本目录完整文档不是产品实施窗口。
"""
    (OUT / "consumer-contract.md").write_text(consumer)

    put(OUT / "schema-change-index.json", {"format": "i05-protocol3-materialized-schema-change-index/1", "sourceIndexRef": FIXED, "sourceIndexPath": D1 + "forward-schema-change-index.json", "schemaChanges": actual_schema_changes, "fieldResponsibilityLiteralChanges": delta["fieldResponsibilityLiteralChanges"], "propertyIndexCount": 1241, "schemaFieldAdditionOrRemoval": False, "actualImplementationAdoption": False})
    profile_changes = []
    for key in sorted(set(profile) | set(old_profile)):
        if (key in old_profile) != (key in profile) or old_profile.get(key) != profile.get(key):
            profile_changes.append({"pointer": "#/" + key, "old": old_profile.get(key), "new": profile.get(key), "newProperty": key not in old_profile})
    put(OUT / "profile-change-index.json", {"format": "i05-protocol3-profile-change-index/1", "changes": profile_changes, "fieldResponsibilityNonLiteralMetadataChanges": ["#/format", "#/normativeCrossFieldRules"], "canonicalResourceAssetFunctionPathCodeDomainsPreserved": True})

    # Forward only synthetic document bytes and their synthetic digests. No product data is loaded.
    synthetic = load(R0 + "synthetic-design-cases.json", D0)
    original_header_raw = copy.deepcopy(synthetic["headerRawExamples"])
    mapping = {row["old"]: row["proposed"] for row in delta["schemaLiteralChanges"]}
    synthetic = change_strings(synthetic, mapping)
    valid = synthetic["valid"]
    old_provenance_hash = valid["buildReceipt"]["embeddedProvenance"]["sha256"]
    serialized = (json.dumps(valid["provenance"], ensure_ascii=False, indent=2) + "\n").encode()
    synthetic = change_strings(synthetic, {old_provenance_hash: identity(serialized)["sha256"]})
    # Versions have equal byte lengths; no raw path or original RECORD row is rewritten.
    valid = synthetic["valid"]
    valid["buildReceipt"]["embeddedProvenance"]["bytes"] = len(serialized)
    embedded_path = valid["buildReceipt"]["embeddedProvenance"]["path"]
    next(r for r in valid["buildReceipt"]["directoryFiles"] if r["path"] == embedded_path)["bytes"] = len(serialized)
    old_receipt_hash = valid["validationReceipt"]["buildReceipt"]["sha256"]
    receipt_raw = (json.dumps(valid["buildReceipt"], ensure_ascii=False, indent=2) + "\n").encode()
    synthetic = change_strings(synthetic, {old_receipt_hash: identity(receipt_raw)["sha256"]})
    synthetic["valid"]["validationReceipt"]["buildReceipt"]["bytes"] = len(receipt_raw)
    digest_updates = {}
    for path, row in synthetic["headerRawExamples"].items():
        raw = row["utf8"].encode()
        old_raw = original_header_raw[path]["utf8"].encode()
        digest_updates[identity(old_raw)["sha256"]] = identity(raw)["sha256"]
        row.update(identity(raw))
    synthetic = change_strings(synthetic, digest_updates)
    put(HERE / "synthetic-design-cases.json", synthetic)
    check = fixed(R0 + "document-selfcheck.py", D0).decode().replace('"iterations/T03/i05-semantic-build-protocol"', '"iterations/T03/i05-semantic-build-protocol-v3"')
    (HERE / "document-selfcheck.py").write_text(check)

    put(HERE / "input-manifest.json", {"format": "i05-protocol3-fixed-input-manifest/1", "fixedD1": FIXED, "fixedD0": D0, "inputs": inputs, "scope": "fixed ordinary Git/text/JSON documentary inputs only; no artifact/SDK/native/caller fee WIP", "productExecuted": False})
    print(json.dumps({"writtenNormativeFiles": sorted(p.name for p in OUT.iterdir()), "inputIdentityChecks": len(inputs), "schemaVersionLiteralChanges": len(delta["schemaLiteralChanges"]), "schemaMetadataChanges": len(actual_schema_changes) - len(delta["schemaLiteralChanges"]), "productExecuted": False}, ensure_ascii=False))


if __name__ == "__main__":
    main()
