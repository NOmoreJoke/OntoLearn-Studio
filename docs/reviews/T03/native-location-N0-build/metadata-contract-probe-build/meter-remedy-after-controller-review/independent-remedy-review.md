# Independent static remedy review

Status: OPEN; no finding or approval is pre-signed.

## Exclusive prospective author ticket

Authorized scope: this report only, static files/Git/stdlib AST/text/hash; no runner/reader import, call, compile, dry run, fixture, dependency or capability probe. No implementation edits or commits.

Before reading any current-window file, this author irrevocably reserves metadata ticket 8000 and application-read payload 4194304 bytes (4 MiB), without borrowing or refund across phases. Fixed metadata phases: data/pins/controls 3000; finite code/method/selector textual facts 3500; report/closure 1500. These are static finite-field/table-item accounting charges, not claimed actual VM/OS internal object bounds. No large AST tree traversal.

Data phase precharge 3000: up to 6 decoded small JSONs, cumulative declared U <= 600, charged 3U+8 per decode (<=1848 total); 11 file-pin checks charged 32 each (=352); remaining 800 for bounded input facts. Call-plan and budget are text only; no whole JSON decode; no 117 identity-content reads. Code phase precharge 3500 covers bounded whole text facts and all required textual reevaluation. Report/closure precharge 1500 covers report construction, at most one final report readback and limited closure/Git facts. No refunds.

Byte reservation: inputs/control/pins <=524288; code/method/selector packet <=524288; up to four precise textual delta checks combined <=1048576; report/closure <=524288; remaining 1572864 reserved/unspent. Every read requires a prior bound; oversized input or exhausted phase stops work. Known bytes and actual scope will be recorded below.

The candidate is initially the parent-described 11-file, 138502-byte pinned set, runner 44500 bytes / efead51a988a48853ae870ac9a87a66ae1e3c3a96653d35770f00b2d29875829 and saved reader 35459 bytes / af6976158b2c604a02d099f5e0da2184139403b85a5cdccc5a107cf5735321c4. These values are unverified until read. No future revision approval is implied.

## Access ledger

Initial creation: exclusive create only; no input file read. Metadata precharge 8000/8000; byte precharge 4194304/4194304 reserved prospectively. Actual application-read bytes initially 0.

## Fixed candidate reviewed (version 1)

Conclusion: **NOT_CALL_READY; full static sufficiency is not accepted.** This is a new independent review of the 44500-byte runner and 35459-byte reader, not a reuse of the former 43415-byte review. F1's event/lifecycle/condition omissions have concrete new treatment. F2 now has a separately prepaid owner and two executable-in-principle pure-original reader methods, but their completeness claims exceed the implemented semantic checks. C1 still does not prove a joint wide-count8192 profile. No execution or future budget/entity acceptance follows.

Declared base: bff478ae35cd90fbc894354b859b3e38e795fe83. This review did not run Git or claim current==base. Exact current file bytes/SHA independently observed against candidate-pins.json:

| File relative to D | Bytes | SHA256 |
|---|---:|---|
| run-once.py | 44500 | efead51a988a48853ae870ac9a87a66ae1e3c3a96653d35770f00b2d29875829 |
| call-plan.json | 10227 | 37ce62f3ab92af66af9949e69b653899c9331f41eba3800ea82c5427941853c2 |
| meter-plan.json | 1091 | 4c8d88bca525ca6a5651c90e6615f953ef3b387c51c81f8f765a1cdc8dffaad4 |
| meter-history.json | 1703 | 232d6e0cdd0ee261b904e279f70aa1a23546e2b179c074c48f65d3fae9179da4 |
| budget-and-usage.json | 9942 | 7da565fdc38887848729f6156288c731ecde73abec03821d68ad3c6e55a3cf15 |
| control-method.md | 3018 | 91c175b42df2b9e31f2d22d0491277e180a79d326d039f4057ef8becb84f5943 |
| dependency-method.md | 2219 | 5424b9ed473d5b3cdd5dd794e7dc5bc1cbf843fd306f5a5508ca17a3a0b86239 |
| Q/meter-proof.md | 15693 | fc669a4b924bda35e4bfc037260fb0b064fc9d0560a042b0d917b4f59ad7d911 |
| Q/review-methods/review-saved.py | 35459 | af6976158b2c604a02d099f5e0da2184139403b85a5cdccc5a107cf5735321c4 |
| Q/review-methods/README.md | 13631 | a0365bce2299585a9700edc1eede187e8fe8bb34088aef0830a63567aaf1081c |
| Q/review-methods/method-plan.json | 1019 | 9e27f460cf3e78c62401e5decc8990266d60188f74c8bf6446858b429eb762d8 |

The eleven bytes sum138502. The candidate pin document itself was2015B/SHA48f7edf02c6f486775d5681babf2592695e47beb9b8b06521673ed5a15536a3a. Three new root originals matched the assigned lengths and hashes exactly: controller review18076/559fe1f6c34c646b46f8e58131431ca609d1353efe321793695f216d5171f4b1; budget amendment2972/1703de056754a40a474c7d0761e4dd67c609409539c91f4111e90c3bb042a9ac; remedy window5646/368a4e4d2dd29b2ab53ee439c21d6503cac4232763d801927ee6e0d64dec3f89. Limited closure1707/8e6c88cd9e79d8e60e00e5a7674cd614558c515e30bad401d68b4824e18f21f5 was read in full. Root originals supply authority/history, not new runtime evidence.

## Material findings

### R1 / P2 — complete compiler vector and selected-link review is not implemented

`review-saved.py:288-296,331` appends either a clang or ld argv, then checks only total selected length2. It does not require exactly one clang-cc1 and one ld. Two clang records with `-cc1`, source and SDK can satisfy the count without any ld vector. Neither membership test verifies the complete selected argument sequence; clang lacks a corresponding arm64/output relationship check, and ld only tests membership of `-o`, product, arm64 and SDK, not the values adjacent to options or a complete accepted vector. `-Dfoo` also escapes the exact `-D` / `-DNDEBUG` membership rejection. These are source-level counterexamples, not fixtures or executed simulations.

The broad `otool -l` field regex at316 also accepts arbitrary lower-case field/value lines, counts numbered headers without sequence association, and can set minOS from any `version`/`minos` line rather than tying it to the relevant command. Binary command lengths/counts are checked, but printed rows are not associated with their binary command type/size. Thus README39/proof61 cannot claim full semantic vectors/load-command verification merely because all lines were scanned. Preserve actual-open/stub/archive/ABI gates pending; also complete the specifically promised static evidence checks, with finite field/projection charges, before calling the static profile complete. Unknown syntax HOLD is valid for genuinely unsupported syntax; it cannot close a known unexamined accepted grammar branch.

### R2 / P2 — process binding and all-control/meter matrix have omitted semantic checks

`review-saved.py:370-400,425-437,521-525`: all eight controls are read/hash-pinned, but meter-plan and meter-history are not decoded or semantically checked; method-plan only checks three numeric fields. `control_review` decodes execution-attempt but only checks token/dispatchAttempted. Neither its inputProcessRef nor build-intent.authorizationInputRef is compared to cfg.inputProcessRef, even though peer facts and owner identity comparisons claim that process reference. Therefore both peers may report a common cfg reference different from the actual producer's recorded ref while these checks succeed.

Attempted/dispatched compact records have no index or meter checks; only planned/terminal meter snapshots are reconciled. Individual phase caps/reservation flags/active phase are not checked, and select/loop counters are only each <=cap, without cross-command monotonicity, select<=loop or final build-terminal totals. Build terminal compiler/static counts and total captured bytes are not reconciled with the six original streams. Root-controlled SHA pins are necessary identity evidence; they do not themselves implement the advertised full control review. Minimal repair is an explicit bounded schema/field matrix across all control JSON and all stages, with actual process/auth/ref binding and final totals, plus a revised U/F/fixed model. Do not just add native decoding without the missing validation.

### R3 / P2 —8192 is not proved for the joint wide candidate scope

Proof65's5974 table is a runtime candidate-visit table:3072 normalization,1024 binding,880 prior,512 modules,3×117 descriptor/pre/post,7SDK,128 fixed. Both peers additionally normpath/validate every D<=1024 binding at reader344-357. Under the preserved wide repeated-candidate scope, these contribute2048 more, making8022 before receiver file/config/output/parent/closure visits. Only170 remains. The statement that the72-object receiver profile is inside the same fixed128 does not allocate three independent receivers or their repeated visits. Using each role's explicit72 allowance as a conservative additional bound gives5974+2048+3×72=8238, already beyond8192 before separately classified external closure repeats. This8238 is an additive model demonstrating the missing scope/table; it is not claimed the minimal actual count or a measured lower bound. If some allowances overlap runtime128, an exact nonoverlapping allocation must prove that overlap without changing historical counts or deduplicating repeated visits.

Specify whether fresh8192 is runtime-only or all parties. For a joint ticket, provide a complete per-role wide table including canonical/binding, original/control/config/output/peer/parent/index/closure candidate visits and all repeats. Propose a sufficient fresh amount if needed, never borrow historical8192, silently reinterpret this as identity inventory or add a ticket here. Metadata and byte feasibility do not establish entity feasibility.

### R4 / P2 — external closure byte proof needs a tighter derived bound or explicit larger reservation

README49 reserves at most4MiB for full owner report/disposition read, up to8 closure copies and exact Git index byte verification together. Account permits owner output envelopes3.5MiB and report2MiB. Those declared envelopes alone cannot prove read+write+index re-read fits4MiB. The method must derive tighter source-specific attainable output bounds (including full embedded peer texts, every finding, indices/facts/parent/stderr) and all repeated read/write operations, or allocate a sufficiently large external subcap within C's independent48MiB and recheck the complete18MiB tail. In-place raw archival correctly avoids a second30MiB copy; it does not make report/commit repetition free. This is an upper-proof gap, not a claim any actual report currently exceeds4MiB. A runtime HOLD on exceeding an unproved cap is not a sufficient construction-time completion proof.

## What the new candidate does substantiate

F1 now explicitly constructs/records KqueueSelector, without fallback. Runner530 pays1024 before construction/registration,566-580 pays16 before each condition and256 before each select;128 selections/134 conditions are shared by all six commands, empty wakeups charged and cap arrival UNKNOWN without refund or retry. Kqueue source554-577 visibly uses max_ev from at most2 registered READ fds, creates kev/result collections and ready tuples, and unregister533-552 covers DELETE/OSError paths. Proof33-43 names40 library+72 caller per event and lifecycle normal/rollback/close work; normal-control10634+32768+6144+2144=51690/60000. No concrete remaining8-per-select omission was found in these visible paths.

Evidence limit: this author used the19536B saved selectors.py.raw, not the installation source and never imported it. The tool computed its SHA during the single read, but the middle of that long tool return was display-truncated, including its header and part of base implementation. Therefore this report does not claim an independently observed raw SHA equality or a complete independently displayed base-method audit. No second selector read was made to hide the gap. The complete F1 closure remains subject to that finite evidence gap; owner/root's existing named-source evidence is distinguishable from this author's visible source evidence. This does not expand permission to read SDK/tool/witness payloads.

M's described phase arithmetic is20292/22000 preflight,60075/61000 dependency,51690/60000 control,2208/3000 emergency, sum reserved146000. Phase counters, error phase switch, actual runner/plan/meter/history/proof/method SHA gates and explicit owner/peer/byte/entity auth checks are present; no fake auth or runtime call was made. Decoder shape/U checks and own builtin-only encoder avoid a second generic container JSON traversal. JSON3U+8/encoding3R remains an accepted semantic-record abstraction; these formulas are not actual CPython/heap/OS/loader upper bounds.

F2's formerly missing independent C is now concretely represented: owner read/hash of all originals, both full peer reports embedded unabridged, both complete53-row indices compared with native6-field dict equality, distinct peer identities, exact output/parent completion hashes, every retained finding OPEN and an explicit external process/Git closure. Native equality and repeated field comparisons now have4000 in fixed8000; owner formula46544/48000 and peer87720/90000 arithmetic are correct for the stated profiles. Deterministic file tables/no sort/no next search, pre-decode U/F limits, upfront output/R/T/error fees, no-follow bounded reads, sole saved buffers/hashes and full-tail retention are present. Pure file code has no subprocess/exec/eval/network/product dispatch. These facts improve the method but do not resolve R1-R4 or justify a generic static COMPLETE for the missing surfaces.

Runtime40 + owner48 + peers36+36 =160MiB; dep2 is explicitly separate from raw16+records/source8+artifact4, giving30MiB originals per receiver and tails18/6/6. M+C+P+P=374000 <=398737 leaves24737 and a hypothetical2575263/2600000. Current2201263 includes24000 isolation plus24000 new static preparation exactly as new root authority states. All remain proposals, not tickets applied or auth created. Historical2250000/old pools/all failures/UNKNOWN/255/author5280 minimum+other UNKNOWN/owner UNKNOWN remain; isolation is not actual, historical upper, reusable funding or retroactive compliance.

## Actual access and remaining review boundary

At this report section, known application-read payload is279519B: first root/pins packet28709; controls/proof/procedure/closure60250; runner44500; reader35459; precise recovery packet94908 (including saved selector19536 and a charged runner reread); exact proof recovery15693. Two precise textual recovery passes have been used out of the four reserved; all file/pin reads and displayed truncation still count. Zero JSON files were natively decoded by this author (U=0, F=0); call-plan/budget/pins were text, no large AST graph was built. The reserved data phase3000 covers11×32 pin validations and the bounded original/control/directory facts; code/method text3500 covers the finite checks above; report/closure1500 is retained. Each was paid before access; no refund or borrowing. The fixed8000 is a prospective semantic fee, not a measurement of VM internals. A later precise frozen delta may be checked only within the original remaining phases/bytes and in this same report; no future version is approved in advance.

Only file/text/hash/stat/limited directory metadata and this one report write occurred. No Git, AST compile, candidate import/call/extraction/simulation/dry-run, compiler/inspector/native/API/fixture/GUI/DB/network/dependency/version/capability probe, product/source/7 excerpts/117 identity payload/old880 witness/42772 index/old205 package, extra agent or other chat was accessed. Full display of selector base methods and all runtime evidence remain unverified. Actual selected-link/backend/stub/archive/compiler-open/loader/current headers/ABI/runtime/drain, original ninth-section/no-desktop/T01 damaged-SQLite/wholeH HOLD/rejected-action stops, designated dual-model/same-version/two-OS/human/CI/parentN0/remote gates remain pending. This report grants no execution permission.

## Author seal for fixed version1

One permitted report readback completed:15794B, verified all four finding sections and access ledger are present. Known application-read total through this seal is295313B (279519+15794), well within4MiB; initial creation and append writes together equal the final report length, with no rewrite of input or implementation. Fixed metadata8000 remains wholly reserved as3000/3500/1500, no borrowing/refund or historical reconciliation. Two of the four reserved precise text recovery passes were used. No candidate changed or later version was approved. The independent fixed-version1 disposition remains NOT_CALL_READY for R1-R4 and the explicitly disclosed finite selector display-evidence gap. Any subsequent frozen delta requires a separately identified appendix within the same original remaining ticket; this seal does not pre-sign it.

## Frozen v2 delta entrance (not yet reviewed)

Parent expressly requested a same-ticket frozen-v2 delta review. No fresh ticket is created: metadata8000 remains3000 data /3500 code-text /1500 report-closure, no borrowing/refund. The code-text allowance is now prospectively apportioned <=2000 for v1 finite checks and <=1500 for this frozen delta; report closure remains inside1500. Native JSON decode remains forbidden for call-plan/budget and is unnecessary here. The new12 pin checks (384) are charged within the original data3000, without borrowing the unused native-decoder allowance from another phase. This is a parent-authorized exact delta, not a new broad scan. At entrance known reads295313B. Remaining two exact text passes each stay<=512KiB; only frozen changed code/method/control text and bounded root v2 response are eligible. Final report hash/stat is charged in original closure, no free payload read. No selector/installed-source/witness/tool/SDK/source reread or candidate execution is allowed. V1 findings and selector display-evidence gap remain above. Frozen v2 cannot approve any subsequent revision.

## Frozen v2 delta review — final disposition

**HOLD / NOT_CALL_READY remains.** This appendix supersedes the v1 disposition only for the frozen v2 changes actually inspected. No v1 finding/evidence record is deleted. R2's identified semantic omissions and R4's repeated-byte arithmetic now have concrete remedies. R1 still accepts a missing typed load-command record; raw9T semantic-fee sufficiency and the corresponding complete joint entity bound remain OPEN/UNKNOWN. Arithmetic feasibility alone does not establish either complete upper bound. No additional candidate modification, third execution-like check, new ticket or authorization is implied.

### Exact v2 identity

Frozen delta-v2-pins.json was read as text only:3155B/SHA94b66de30b78b0ee3def1537107fa5f77b20ca9878ca1ce8a1c95308b12fa536. All twelve named current files were independently size/SHA checked, total162614B:

| Relative to D | Bytes | SHA256 |
|---|---:|---|
| run-once.py |44504|8c04c0ccbd5f2c374ff56b8b1dabc271b8af4475fb7591be86c6180e0cf4041f|
| call-plan.json |10229|f69ab1dd0c1398a89a2c3abee4959b6ac2a302bd173e7a81bca5a4e8578c348f|
| meter-plan.json |1093|ea44120ecb4c490a58d2b387828ab26af5bcae294b1c61c4de98e7ac7defa30b|
| meter-history.json |1703|85e4345cea0cb2f0bed5fe7537e228e30554818a96bac926d66f47faae00f0b1|
| budget-and-usage.json |9945|d5ab39ef77e32aafd80609cec843cc9f4686bd1e85a56f98e3f12eec5c864eee|
| control-method.md |3027|1a97ebf227eaab43df5aee65e48e0fdf0e6c698407e0c239299290c6c0fba18c|
| dependency-method.md |2360|040b253d64453faf343a18474562b5c88b231bba213381e6c85ce30c80ed3d5b|
| Q/meter-proof.md |17979|12e70c35d2188f2b66746ab790e26dbca80dd269a5ad8382581a73a03f9198fd|
| Q/review-methods/review-saved.py |54062|f202cd7d4dc60d0ced3e3a1129892168b0c9168c6f402a8183228767d477c1e1|
| Q/review-methods/README.md |15513|2d895734b5b421dbee9831914c9d34df9f59ff4cd80ed97b7645bde3081ef829|
| Q/review-methods/method-plan.json |1022|043fe7d70fe5ee08c3dfe3044aed6cc78e304bd10b98d6ed68079b77da1a893c|
| Q/joint-entity-table.json |1177|f69bb5fd62b615cce6d8802a8d3296c7d5eb250e871f75ea33bab2fe692e0995|

Declared HEAD/base remains bff478ae35cd90fbc894354b859b3e38e795fe83; no Git read was performed by this author. Whole-file pin verification is distinguished from the exact textual delta review: reader was available in full through the held tool-return buffer; runner text inspection was limited to the changed authority constants858-870, plan/budget to the affected proposal blocks, method/proof/procedure/entity table to their bounded texts. This is not a renewed broad audit of old protected source or the full prior package.

### R1 remains OPEN: missing command body can still pass typed load review

The new `driver_argv`255-326 consumes every supported token with explicit arity, rejects response/macro switches by prefix, checks required adjacent source/SDK/target/platform/output values, and returns the selected owned object. `raw_review`447-451 and479 now require exactly one cc1 and one ld sharing the same object. The former two-clang/no-linker and bare -Dfoo counterexamples are closed within that deliberately finite grammar. Complete driver lines are retained in peer reports; unknown flags/formats remain HOLD. Typed LC schemas now bind ordinal/command ID/cmdsize and associate minOS with the actual version LC, closing the former generic-field/minOS issue for records that are actually completed.

But `load_review.finish`349-351 immediately returns whenever kind is None. It does not distinguish the initial pre-command state from an already opened `Load command N` that has no `cmd`, `cmdsize` or fields. At369 a following correctly numbered header calls finish, silently skips that empty record, advances index and starts the next record. At409-410 the final check only compares header count and requires LC_MAIN/minOS somewhere. Consequently a missing body for an earlier binary command, including its type/size/required fields, can be skipped while other complete commands provide LC_MAIN and minOS. An empty final body can likewise evade finish if those requirements were already supplied. This is a direct control-flow counterexample, not an executed fixture or simulation. Distinguish the no-command-yet state and require a completed typed body for every opened header before permitting a new header or end. R1 cannot be marked closed on the frozen54062-byte reader.

### R2 targeted semantic repairs confirmed; complete fee sufficiency is separate

The new profile_review532-557 decodes/checks meter-plan and history; main651-664 checks the method's fixed parameters and reader SHA/byte length. Peer control_review568-617 binds attempt inputProcessRef/token/authorization SHA and intent authorizationInputRef/identity/runner/plan to the same root config, and the owner independently binds the actual attempt/intent at704-710. All four command stages now have index and meter checks; planned/terminal argv/env/cwd/path/backend/timeouts and terminal success/EOF/leader/failure/cleanup fields are checked. Meter_check510-529 validates phase caps, reservation flags/active phase, sum/reservation agreement, actual=null/noRefund and byte categories. Cumulative select/loop/captured counters are checked across commands and final compiler1/static5/runtime NOT_RUN/dep pending/closure totals reconciled. These specifically address v1 R2's recorded counterexamples; no additional R2 semantic miss was established within this bounded delta.

Twenty-seven meter snapshots is a correct count:attempt1+intent1+six commands×four stages24+final1. The written3048 matrix partition is1944+384+400+192+128; fixed5608 is512+3048+768+768+512. Peer fee arithmetic101520/102000 and owner46576/48000 is correct. That arithmetic does not prove raw9T/R/fixed submodels complete; the following unmodeled repeated schema work prevents accepting the complete peer upper. It is not paid by nominal480 peer slack or737 joint remainder.

### R5 / P2 — repeated per-field schema library traversal leaves raw9T unproved

`load_review352` derives a split/set required-field collection at each command finish. More materially,394 computes `set(schemas[kind][1].split()) | {'cmdsize'}` again for every ordinary field, then tests membership at395. The full list/string-member materialization, set conversion and union traversals recur even when the same schema is selected; they are explicit library semantic work, not byte hashing or OS internals. Finish then builds/compares further sets. The fixed fee table does not separately bound these repeated operations; raw9T is described as covering tokenization/materialization/full typed semantic and association passes.

LC_DYSYMTAB has18 schema names. Its18 numerical fields plus cmdsize cause19 repeated split/set/union constructions. For an ordinary two-word field line, projection contributes1+2×2=5T, so9T allocates45 units locally; just three18-member library passes already give54 before the rest of parsing, field-map checks, insertion and finish work. These are a concrete mismatch in the claimed per-projection amortization, not a measurement of actual CPython visits. This report does not manufacture an exact global additional fee or assert a tested >102000 overrun: the full accepted-command mix/whole raw phase needs a fresh complete bound. The raw9T sufficiency proof is **UNKNOWN**, so101520 cannot yet be accepted as a complete peer upper. A cap-triggered HOLD does not establish the construction-time sufficient model.

Minimal future direction: construct the schema field sets once in a fixed table, explicitly prepay initialization and later bounded membership/finish comparisons, then reuse them per field; or fully count all repetitions and derive a sufficient model. That would require a new frozen candidate and authorized independent delta review. No such change was made here, no unreviewed future version is pre-approved, and737/old tickets cannot be borrowed to conceal the gap.

### R3 arithmetic repaired; complete joint entity upper remains UNKNOWN

The v2 table correctly separates runtime5974 from each peer20472 and owner7096. Peer arithmetic3072+256+216+32+12288+4096+512=20472; owner216+2048+576+256+384+1536+2048+32=7096; joint5974+20472+20472+7096=54014, proposal57344/headroom3330. It expressly counts independent receiver/canonical/binding/output/index/parent/closure repeats and distinguishes the un-applied16384 planning cap, whose table gap is37630. Old8192/runtime rows are not borrowed or deduplicated. The earlier cross-role omission identified in R3 has a concrete wider table now.

However raw projection/materialization/validation3T is still justified only by input T. The per-field schema split/set/union repetitions in R5 are absent from its entity derivation. The table does not prove whether all these repeated materialized/member candidates are already bounded under raw3T, another explicit row, or are wholly metadata-field work outside the declared wide candidate domain. Under the preserved instruction to include repeated candidate/projection visits, silently treating them as zero or deduplicated is not acceptable. Thus **54014 is the exact sum of the stated rows, not a verified complete joint upper**; complete entity sufficiency is UNKNOWN/OPEN. No exact extra total is invented. Any exclusion must have an explicit scope argument consistent with the historical wide count; otherwise count the repeats or remove them in a later reviewed implementation. Fresh57344 is a proposal, not an accepted debit.

### R4's repeat-byte construction is now explicit and arithmetically sufficient for its stated method

Owner52MiB=30MiB original envelope+22MiB tail. Five external sources have S=2MiB report+1MiB archive+0.5MiB facts+16KiB parent completion+64KiB stderr=3751936B. One read into held buffers+one evidence-copy write+one Git-index blob read costs3S=11255808B; all auxiliary reads/writes jointly<=1048576B gives12304384B<=12582912B (12MiB). No second source read or repeated copy is permitted; full dispositions are inspected from held text. This closes v1 R4's omitted repetition model, conditional on actually following that exact finite procedure. The author did not run Git or observe future parent completion.

Owner tail0.125+0.5+1+1+2+0.125+0.03125+3.5+12=20.28125MiB<=22. Peer36MiB/runtime40MiB remain separately paid, all13 capture streams/raw16+records/source8+artifact4+dep2=30 receiver originals. Joint40+52+36+36=164MiB171966464. These are application-payload reservations, not physical OS/Git/compiler/loader/cache/heap bounds. A later extra pass must stop before access, not silently consume runtime/peer or history allowances.

### Joint/history/authority and unchanged gates

M146000 remains pre20292/22000+dep60075/61000+control51690/60000+emergency2208/3000 at the unchanged declared semantic abstraction; F1's v1 finite display-evidence gap remains expressly unclosed, with no selector or installation reread. The changed runner authority constants explicitly require joint398000/peer102000/byte171966464/entity57344. M146000+C48000+P102000+P102000=398000<=398737 leaves737, hypothetical2599263/2600000. This is arithmetic of a proposal with unresolved completeness;737 is not an unmodeled validation/error/closure buffer. Root has not funded/authorized any future role invocation. Entity hypothetical578800/600000 and remaining21200 likewise depend on root's separate future acceptance, not this report.

All prior tickets/2.25M/forward2.6M distinction, failures/UNKNOWN/255, author5280 minimum+other UNKNOWN, owner UNKNOWN and24000 historical isolation remain; no refund, historical upper or retrospective compliance is inferred. No runner/helper/reader import/call/compile/extraction/simulation/fixture/dry-run/native/API/network/source/SDK/tool/witness/index reads, extra agent or other chat occurred. No candidate was edited or committed by this author. Actual selected-link/backend/stub/archive/compiler-open/loader/current headers/ABI/runtime/drain, original T01/wholeH/no-desktop/ninth-section/rejected stops, designated same-version dual models/twoOS/human/CI/parentN0/remote gates remain pending.

### Same-ticket delta access closure

Delta input bytes are exactly165769=3155 pin text+54062 reader+108552 other11 frozen files. Cumulative known reads before final report hash are461082B=prior295313+165769; of this445288B is named review input and15794B was the v1 report readback. All four authorized precise textual passes are now spent (v1 two recovery passes, v2 reader/methods one and remaining11-file delta one). The complete v2 reader/doc tool-return strings were held and redisplayed from memory to recover rendering omissions, without candidate file rereads. No selector return-buffer recovery was fabricated for v1.

Native JSON decoding by this author remains0 files/U0; text-only pins/call-plan/budget/history/method/entity facts stayed in data3000. Total23 candidate-pin checks at32 each=736 fit that phase; no metadata or bytes borrowed/refunded. Code-text3500 retains the apportioned v1<=2000/v2<=1500 finite check model, and report/closure1500 retains both appendices/hash/stat. These are prospective bounded semantic allowances, not measured actual VM/OS work. No further candidate reads fit the expressly limited four-pass procedure; any follow-on review must be newly authorized. Final report bytes/SHA are computed by one bounded closure hash read, charged below, and supplied to the parent. The frozen v2 disposition remains HOLD/NOT_CALL_READY.

Final v2 author seal: bounded report hash/read consumed31289B. Cumulative known application-read payload is492371B (445288B review inputs plus15794B v1 report readback plus31289B final report hash/read), below4194304B. All four text passes are spent;8000 metadata remains retained at3000/3500/1500. Final file length and SHA are calculated from this held buffer plus this seal, with no second file read. The author makes no additional execution/actual/VM/OS claim. No later revision is approved. Final frozen-v2 disposition: HOLD / NOT_CALL_READY; R1 and R5 OPEN, complete R3 joint upper UNKNOWN, selector display boundary retained.
