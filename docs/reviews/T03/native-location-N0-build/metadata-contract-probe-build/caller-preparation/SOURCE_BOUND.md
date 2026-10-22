# Real caller: complete source envelope, not funded

This is the new caller alone. No runner, reader, original M/C/P ticket or frozen f2b payload is modified. `caller.py` is prepared source, never invoked, including local functions. A fresh committed-source review remains required. The source is under48KiB and Python3.9 syntax is checked only with stdlib AST.

## Distinct domains and honest result

The proposed four-role caller tickets are **112000 metadata,108000 entity and13MiB application I/O**. These are prospective reservations, not actual consumption. Each role requires metadata28000/entity27000; byte tickets are producer2MiB, peer-a3MiB, peer-b3MiB, owner5MiB. No runtime ticket is funded.

Root current is metadata2291263/3200000, entity521456/1300000, build109086362664/137438953472. Original M167000+C103000+P268000+P268000=806000/164MiB/entity737280 is also unfunded. Applying both proposals would give:

| Domain | Prospective aggregate | Current guard | Deficit |
| --- | ---: | ---: | ---: |
| metadata | 3209263 | 3200000 | 9263 |
| entity | 1366736 | 1300000 | 66736 |
| build bytes | 109271960616 | 137438953472 | no deficit |

Therefore **METADATA_AND_ENTITY_NOT_FIT / NOT_CALL_READY**. This packet does not raise either guard. A later trusted root window must explicitly approve guards at least equal to the complete aggregate and fund all original and caller tickets before any launch. The code accepts such explicit guards only from the exact root admission whose digest comes from the trusted root tool invocation. It does not choose a higher guard itself. The unsigned template deliberately retains current insufficient guards.

Frozen native history in f2b still says2273263/3200000 and entity521456/1300000. This is the limited native snapshot, not the new root current global accounting. The extra static18000/6MiB is already in root2291263/build109086362664. The caller checks separate root aggregate fields; it never rewrites the37 files to make the old history pretend to include new static/caller costs.

Earlier owner drafting estimates102656/98304 were not accepted tickets. Expanding the fixed output/lifecycle and repeated binding paths showed that the initial2048 fixed allowance was insufficient. Final fixed4096 includes all four below. This correction is retained rather than silently excluding the work or reclassifying it as free byte work.

## Source ledger per role

The counting domain is the inherited semantic record/event model: named fields, members, containers, native JSON graphs, source-level record projections/materializations and I/O/control events. Ordinary string/byte spelling and hashing are byte work, with explicit byte bounds; this does not remove field/member/container visits. It is not a certificate about Python VM allocations, libc/OS internal work, physical memory or filesystem cache I/O.

| Class | Source limit and prepaid fee | Metadata | Entity |
| --- | --- | ---: | ---: |
| fixed whole role | complete admission/config bindings1536 + owned lifecycle1536 + repeated output construction/encoding896 + initial tables/views128 | 4096 | 4096 |
| file actions | at most37, each216/200 before action | 7992 | 7400 |
| JSON structure/native | F<=7, sum reserved U<=1200; each8c+80 before scan/native | 10160 | 10160 |
| selector native/backend | <=16 calls,256/256 each before `select` | 4096 | 4096 |
| returned entries | <=32,16/8 each before accessing entry/reading | 512 | 256 |
| output write attempts | <=96,8/4 before each write | 768 | 384 |
| **complete upper** | sums above | **27624** | **26392** |
| fixed role ticket | no refunds/borrowing | **28000** | **27000** |
| headroom | error prefixes already included, not another ticket | 376 | 608 |

All four full upper totals are110496 metadata and105568 entity; fixed proposals are112000 and108000. Every check stops before the next constrained operation if its cap would be exceeded. Guards are an extra defense, not the proof that omitted work is free. A failure can consume a prefix of the same caps and then one bounded cleanup/output path; no retry or second decode is allowed after an escaping failure.

### Fixed whole-role details

-1536 admission/binding slots cover the whole schema/keyset, root refs/time and four distinct IDs, actual auth/profile/control fields, all config fields, complete imported-name loop up to128 (row/type/length/two forbidden fragments/gate), all predecessor pins, actual facts/index/report projections and complete global-budget comparison. It is not an incremental-only allowance.
-1536 lifecycle slots cover own Popen keyword/stdio objects and transitions, Kqueue create/register/unregister/close, initial private base/run/nonces/role and active-lock operations, both pipe handles, monotonic/UTC observations, poll/wait, terminate1s/kill1s, bounded close/fsync/error records and final lock release. The256-per-select fee separately prepays backend event/key/tuple/list return graphs before the call. Only own unreaped Popen leader may be signaled; descendant drain stays UNKNOWN.
-896 output slots cover repeated common dictionaries in three stages, terminal including meter/error/stream fields, completion8 fields, one emergency persistence-failure object and the top-level bounded stderr failure object, plus JSON/native encoding and repeated projections. Arrays of cleanup errors are kept up to8 plus an overflow flag. First cause is never replaced by a cleanup cause. Final close/unlink outcomes cannot be folded back into an already written terminal: the actual root tool outcome must therefore also be pinned by the next stage's root admission.
-128 initial slots cover fixed role/control/auth-key/argv/environment views and finite source-level tables. Interpreter imports/VM/internal allocation and real filesystem cache activity remain outside the semantic-record model, not measured or claimed.

### File actions, paths and chunks

The37 limit includes each named read, exclusive structured write and nonce claim. Worst owner path uses29 reads (including three root observations, three terminal predecessors, two completions, final input/config/admission rechecks and three reader outputs), plus nonce, three launch records, method.stderr, completion and terminal, giving36; one persistence-failure record is37. Earlier failure omits some later reads and uses explicit absent-stage records, staying within that same envelope. Producer/peer paths are smaller. Raw stdout/stderr handles, active lock and private-directory lifecycle are in fixed lifecycle, not uncounted extra file actions.

Each216 metadata file fee covers up to24 path components x3 open/close/member events=72,48 native stat/identity/mode/presence/close projections and up to32 read chunks x3=96. Entity200 covers72 path events,48 metadata objects/projections,64 chunk/member/native entries and16 reserve. The actual source limits absolute paths to24 components, regular inputs to one hardlink, no-follow opens at every directory and final leaf, stable before/after dev/inode/mode/uid/nlink/size/mtime, and chunk count before reading the33rd. Byte reservation precedes input access. Fixed private-directory/lifecycle actions are distinct from these per-file reads/writes.

No directory listing, recursive seek, SDK scan or binary payload hashing occurs. Future caller reads only the approved identity **manifest metadata bytes**, needed to reproduce the producer token; it never decodes that table or reads descriptor/tool/SDK/witness/index payload. The producer's original authorized preflight remains responsible for its own actual descriptor/identity checks. The preparation phase read none of those payloads.

### JSON full entrance and failure paths

The maximum schedule is admission256 + producer AUTH96 + role cfg256 + up to three predecessor terminal96 each + own facts256 =1152U/7 files for owner; the ledger conservatively reserves1200. Producer/peers use fewer. Root observation and completion objects are opaque hash-pinned bytes, not decoded. No caller JSON cap is silently added to the old reader.

Before UTF-8/native decode, `Meter.json` pays8c+80 in both domains and checks total U/F. The single packed scanner counts a container, every object field and every array member before accepting it, including separate array-member+container actions. Root scalar is a unit. Object key payment covers its scalar value; nested container pays additionally. Depth is limited to12 containers with a root sentinel; no per-open frame lists are materialized. Every byte advances once, except bounded delimiter tests; UTF-8/escape/grammar is finally checked by exactly one native decode. Partial/invalid syntax, duplicate key and native failure escape the role; no next decode follows.

The8c term covers native3c plus structural/token/key/field/member/projection work5c;80 covers per-file admission/packed-state/native fixed/duplicate failure cleanup. `object_pairs_hook` constructs the exact dictionary, rejects repeated keys, retains all rows before any successful return, and is not a free second unbounded walk. It is included in native3c plus structural5c, not borrowed from file or byte tickets. Short integer tokens<=32 bytes avoid an unbounded numeric conversion path; floats/NaN/Infinity are rejected. Scalar string spelling is bounded by input byte caps and is not treated as a new member per character.

### Streams and bytes

The caller reserves262144B before capture: each of stdout/stderr is at most65536B, once kernel-read and once raw-file-written. An exact cap is incomplete, with no lookahead; call/event cap also gives HOLD before more reads. Each read requests only remaining bytes. A partial raw write records observed-read length separately from actually saved length/hash, never hashes an unwritten buffer as a saved file. Full completion requires EOF on both pipes, real own leader termination, no first/cleanup error and real exit0. No successful availability/600s promise follows from a finite event cap.

Worst owner application-byte reservations stay below5MiB: all named inputs including root/config rechecks<0.7MiB, raw0.25MiB, method.stderr<=0.0625MiB, own facts<=0.0625MiB, report<=2MiB, index<=1MiB, all structured/nonce/lock writes<0.2MiB. Peers need<3MiB, producer<2MiB. Fees count actual file read reservations and writes, including duplicate final config/admission checks; held in-memory reuse is not another I/O read. OS/Git cache I/O remains UNKNOWN.

## Trust and observational limits

`authorized=true`,600 permissions or a template is not the trust anchor. Root's actual tool invocation supplies the exact SHA256 of a real per-role admission; the caller reads only its fixed path and compares bytes before trusting any value. It also binds its source SHA, root-created auth/config bytes, actual loose Git ref, immutable controls, exact child argv/cwd/minimal env and known interpreter alias/canonical metadata. Root must record the actual calling task identity and original tool result externally; the caller cannot authenticate an LLM identity from a string.

Predecessor root observation files are pinned by the trusted root admission, with actual prior outer exit0 attested there; the caller does not manufacture them. This closes the distinction between a child terminal saved before final parent close and the actual caller process's observed final exit. No signature primitive is claimed. Metadata stat-to-exec/source-open TOCTOU, dynamic loader/open closure and descendant drain remain unknown; exact argv and pins do not prove atomic executable opens.
