#ifndef I06_LOCATION_ABI_H
#define I06_LOCATION_ABI_H

#include <stddef.h>
#include <stdint.h>

/* N0 fixture-only ABI. No path bootstrap, content IO, create or publish authority.
 * Public records use fixed-width fields; fixture intptr_t is exactly 64 bits on
 * the two supported targets. Reserved fields MUST be zero. A native
 * fixture harness supplies live borrowed OS objects and keeps them stable until
 * adoption returns. No renderer/JSON/JS integer handle is accepted by the addon.
 * Every nonzero owner returned, including on failed adoption, MUST be closed.
 * Budgets: 32 permanent owner records process-wide, at most 2 nonclosed owners.
 * Per owner: 128 lifetime cap slots INCLUDING root/failed/unknown attempts,
 * 16KiB names, depth 128, 2 child attempts and 2 pipes each. Slots never reuse.
 * Inflight is process-wide <=2, gate is try-lock/no queue, at most one OS call
 * chain executes. No caller-controlled limits or timeout-based slot release.
 * epoch=1 is active, epoch=2 revoked/closed, no resume or wrap. root/acquire/
 * observe/child-adopt require active epoch and nonexpired preparation TTL;
 * snapshot/revoke/release/poll/close remain legal for original-owner cleanup.
 * Revoke is terminal. close is nonblocking with respect to the registry gate:
 * BUSY/RETAINED permits later cleanup of OTHER resources / child waits only.
 * A failed close number is NEVER touched again. Neither result is release.
 * No caller may unload this library while any owner is retained. */
#define NL_ABI_VERSION 1u
#define NL_MAX_OWNER_HISTORY 32u
#define NL_MAX_ACTIVE_OWNERS 2u
#define NL_MAX_CAPS 128u
#define NL_MAX_COMPONENT_BYTES 255u
#define NL_MAX_NAME_BYTES 16384u
#define NL_MAX_DEPTH 128u
#define NL_MAX_CHILDREN 2u
#define NL_MAX_CHILD_PIPES 2u
#define NL_MAX_INFLIGHT 2u
#define NL_PREPARE_TTL_MS 30000u
#define NL_LOGICAL_WAIT_MS 5000u
/* N0 has no async worker queue, maps, messages or ancillary transfers. */
#define NL_MAX_ASYNC_WORK 0u
#define NL_MAX_MAPS 0u
#define NL_MAX_MESSAGE_BYTES 0u
#define NL_MAX_ANCILLARY 0u

#if defined(_WIN32)
#define NL_CALL __cdecl
#else
#define NL_CALL
#endif
#if defined(_WIN32) && defined(NL_BUILD_SHARED)
#define NL_API __declspec(dllexport)
#elif defined(_WIN32) && defined(NL_USE_SHARED)
#define NL_API __declspec(dllimport)
#elif defined(__GNUC__)
#define NL_API __attribute__((visibility("default")))
#else
#define NL_API
#endif
#ifdef __cplusplus
#define NL_NOEXCEPT noexcept
extern "C" {
#else
#define NL_NOEXCEPT
#endif

typedef uint32_t nl_status;
enum {
  NL_OK = 0, NL_INVALID = 1, NL_STALE = 2, NL_DENIED = 3,
  NL_UNSUPPORTED = 4, NL_BUDGET = 5, NL_BUSY = 6, NL_RETAINED = 7,
  NL_INTERNAL = 8
};
enum { NL_DIRECTORY = 1, NL_REGULAR_FILE = 2 };
enum { NL_METADATA_ONLY = 1 };
enum { NL_PLATFORM_MACOS = 1, NL_PLATFORM_WINDOWS = 2 };

typedef struct { uint64_t value; } nl_owner_ref;
typedef struct {
  uint64_t owner;
  uint32_t slot;
  uint32_t generation;
} nl_cap_ref;
/* volume: unsigned 64-bit little-endian; mac file: unsigned inode LE in
 * bytes[0..7], remaining bytes zero; Windows file: exact FILE_ID_128 bytes. */
typedef struct { uint8_t volume[8]; uint8_t file[16]; } nl_identity;
typedef struct {
  uint32_t abi_version;
  uint32_t kind;
  nl_identity identity;
  uint64_t link_count;
  uint32_t acl_checked;
  uint32_t held_object_only; /* Always 1; never continuous namespace evidence. */
} nl_metadata;

typedef struct {
  uint32_t abi_version;
  uint32_t platform;
  intptr_t borrowed_directory; /* FD on macOS; HANDLE bits on Windows. */
  uint32_t reserved[4];
} nl_fixture_anchor;

typedef struct {
  uint32_t abi_version;
  uint32_t platform;
  intptr_t borrowed_process; /* Windows hProcess; -1 on macOS. */
  int64_t child_pid;          /* Own waitable child only; zero on Windows. */
  intptr_t borrowed_pipes[NL_MAX_CHILD_PIPES]; /* -1 for an unused entry. */
  uint32_t reserved[4];
} nl_fixture_child;

typedef struct {
  uint32_t abi_version;
  uint32_t child_slot;
  uint32_t wait_owned; /* nonzero even after a later pipe-duplicate failure */
  uint32_t terminal;
  uint32_t owned_pipes;
  uint32_t reserved;
} nl_child_receipt;

typedef struct {
  uint32_t abi_version;
  uint32_t epoch;
  uint32_t accepting;
  uint32_t closed;
  uint32_t held_objects;
  uint32_t unknown_objects;
  uint32_t pending_children;
  uint32_t held_pipes;
  uint32_t inflight;
  uint32_t ever_caps;
  uint32_t name_bytes;
  uint32_t production_admission; /* Always 0 in N0. */
} nl_snapshot;

NL_API nl_status NL_CALL nl_fixture_owner_create(const nl_fixture_anchor*, nl_owner_ref*) NL_NOEXCEPT;
NL_API nl_status NL_CALL nl_owner_root(nl_owner_ref, nl_cap_ref*, nl_metadata*) NL_NOEXCEPT;
/* No components are resolved via an absolute path. expected may be NULL for
 * first metadata observation, or an earlier native identity as a reject filter.
 * It does not confer authority. Acquire retains the actual returned OS object. */
NL_API nl_status NL_CALL nl_owner_acquire(nl_owner_ref, uint32_t expected_epoch,
                           nl_cap_ref parent, const char* component,
                           uint32_t component_bytes, uint32_t kind,
                           const nl_identity* expected,
                           nl_cap_ref*, nl_metadata*) NL_NOEXCEPT;
NL_API nl_status NL_CALL nl_owner_observe(nl_owner_ref, nl_cap_ref, nl_metadata*) NL_NOEXCEPT;
NL_API nl_status NL_CALL nl_owner_release(nl_owner_ref, nl_cap_ref) NL_NOEXCEPT;
NL_API nl_status NL_CALL nl_owner_snapshot(nl_owner_ref, nl_snapshot*) NL_NOEXCEPT;
NL_API nl_status NL_CALL nl_owner_revoke(nl_owner_ref) NL_NOEXCEPT;
NL_API nl_status NL_CALL nl_owner_close(nl_owner_ref) NL_NOEXCEPT;
/* Native fixture harness only, NOT exposed by Node. Adopting a child transfers
 * sole wait/reap responsibility; borrowed handles are duplicated internally.
 * Receipt.wait_owned=1 means caller MUST NOT wait/reap/close transferred native
 * process responsibility, including non-OK partial adoption; wait_owned=0 means
 * caller retains sole reaper duty. Borrowed OS handles always remain caller-owned.
 * No other thread/reaper may act on the supplied child during or after adoption.
 * No terminate/kill or arbitrary spawn is exposed. Pipe EOF/child exit are NOT
 * inferred from a logical timeout. Each poll is a real nonblocking OS wait. */
NL_API nl_status NL_CALL nl_fixture_child_adopt(nl_owner_ref, const nl_fixture_child*,
                                  nl_child_receipt*) NL_NOEXCEPT;
NL_API nl_status NL_CALL nl_owner_poll_children(nl_owner_ref) NL_NOEXCEPT;
/* Explicit unsupported operations: these functions dispatch NO OS operation. */
NL_API nl_status NL_CALL nl_owner_publish(nl_owner_ref) NL_NOEXCEPT;

#ifdef __cplusplus
}
#endif

#ifdef NL_WITH_NODE
#include <node_api.h>
#ifdef __cplusplus
extern "C" {
#endif
/* Native fixture-host entry only; NOT a JS method. No owner construction from JS. */
NL_API nl_status NL_CALL nl_node_bind_fixture(napi_env, napi_value, nl_owner_ref) NL_NOEXCEPT;
#ifdef __cplusplus
}
#endif
#endif

#ifdef __cplusplus
/* Private cross-translation-unit interface; T03 must hide these symbols.
 * The sole header contains it because N0 permits no extra common helper files. */
static_assert(sizeof(intptr_t) == 8, "N0 requires a 64-bit target");
static_assert(sizeof(nl_identity) == 24 && alignof(nl_identity) == 1, "identity ABI");
static_assert(sizeof(nl_cap_ref) == 16 && offsetof(nl_cap_ref, slot) == 8, "cap ABI");
static_assert(sizeof(nl_metadata) == 48 && offsetof(nl_metadata, link_count) == 32, "metadata ABI");
static_assert(sizeof(nl_fixture_anchor) == 32 && offsetof(nl_fixture_anchor, borrowed_directory) == 8, "anchor ABI");
static_assert(sizeof(nl_fixture_child) == 56 && offsetof(nl_fixture_child, borrowed_pipes) == 24, "child ABI");
static_assert(sizeof(nl_child_receipt) == 24 && sizeof(nl_snapshot) == 48, "receipt ABI");
static_assert(sizeof(nl_owner_ref) == 8 && alignof(nl_owner_ref) == 8, "nl_owner_ref layout");
static_assert(offsetof(nl_owner_ref, value) == 0, "nl_owner_ref.value");
static_assert(sizeof(nl_cap_ref) == 16 && alignof(nl_cap_ref) == 8, "nl_cap_ref layout");
static_assert(offsetof(nl_cap_ref, owner) == 0, "nl_cap_ref.owner");
static_assert(offsetof(nl_cap_ref, slot) == 8, "nl_cap_ref.slot");
static_assert(offsetof(nl_cap_ref, generation) == 12, "nl_cap_ref.generation");
static_assert(sizeof(nl_identity) == 24 && alignof(nl_identity) == 1, "nl_identity layout");
static_assert(offsetof(nl_identity, volume) == 0, "nl_identity.volume");
static_assert(offsetof(nl_identity, file) == 8, "nl_identity.file");
static_assert(sizeof(nl_metadata) == 48 && alignof(nl_metadata) == 8, "nl_metadata layout");
static_assert(offsetof(nl_metadata, abi_version) == 0, "nl_metadata.abi_version");
static_assert(offsetof(nl_metadata, kind) == 4, "nl_metadata.kind");
static_assert(offsetof(nl_metadata, identity) == 8, "nl_metadata.identity");
static_assert(offsetof(nl_metadata, link_count) == 32, "nl_metadata.link_count");
static_assert(offsetof(nl_metadata, acl_checked) == 40, "nl_metadata.acl_checked");
static_assert(offsetof(nl_metadata, held_object_only) == 44, "nl_metadata.held_object_only");
static_assert(sizeof(nl_fixture_anchor) == 32 && alignof(nl_fixture_anchor) == 8, "nl_fixture_anchor layout");
static_assert(offsetof(nl_fixture_anchor, abi_version) == 0, "nl_fixture_anchor.abi_version");
static_assert(offsetof(nl_fixture_anchor, platform) == 4, "nl_fixture_anchor.platform");
static_assert(offsetof(nl_fixture_anchor, borrowed_directory) == 8, "nl_fixture_anchor.borrowed_directory");
static_assert(offsetof(nl_fixture_anchor, reserved) == 16, "nl_fixture_anchor.reserved");
static_assert(sizeof(nl_fixture_child) == 56 && alignof(nl_fixture_child) == 8, "nl_fixture_child layout");
static_assert(offsetof(nl_fixture_child, abi_version) == 0, "nl_fixture_child.abi_version");
static_assert(offsetof(nl_fixture_child, platform) == 4, "nl_fixture_child.platform");
static_assert(offsetof(nl_fixture_child, borrowed_process) == 8, "nl_fixture_child.borrowed_process");
static_assert(offsetof(nl_fixture_child, child_pid) == 16, "nl_fixture_child.child_pid");
static_assert(offsetof(nl_fixture_child, borrowed_pipes) == 24, "nl_fixture_child.borrowed_pipes");
static_assert(offsetof(nl_fixture_child, reserved) == 40, "nl_fixture_child.reserved");
static_assert(sizeof(nl_child_receipt) == 24 && alignof(nl_child_receipt) == 4, "nl_child_receipt layout");
static_assert(offsetof(nl_child_receipt, abi_version) == 0, "nl_child_receipt.abi_version");
static_assert(offsetof(nl_child_receipt, child_slot) == 4, "nl_child_receipt.child_slot");
static_assert(offsetof(nl_child_receipt, wait_owned) == 8, "nl_child_receipt.wait_owned");
static_assert(offsetof(nl_child_receipt, terminal) == 12, "nl_child_receipt.terminal");
static_assert(offsetof(nl_child_receipt, owned_pipes) == 16, "nl_child_receipt.owned_pipes");
static_assert(offsetof(nl_child_receipt, reserved) == 20, "nl_child_receipt.reserved");
static_assert(sizeof(nl_snapshot) == 48 && alignof(nl_snapshot) == 4, "nl_snapshot layout");
static_assert(offsetof(nl_snapshot, abi_version) == 0, "nl_snapshot.abi_version");
static_assert(offsetof(nl_snapshot, epoch) == 4, "nl_snapshot.epoch");
static_assert(offsetof(nl_snapshot, accepting) == 8, "nl_snapshot.accepting");
static_assert(offsetof(nl_snapshot, closed) == 12, "nl_snapshot.closed");
static_assert(offsetof(nl_snapshot, held_objects) == 16, "nl_snapshot.held_objects");
static_assert(offsetof(nl_snapshot, unknown_objects) == 20, "nl_snapshot.unknown_objects");
static_assert(offsetof(nl_snapshot, pending_children) == 24, "nl_snapshot.pending_children");
static_assert(offsetof(nl_snapshot, held_pipes) == 28, "nl_snapshot.held_pipes");
static_assert(offsetof(nl_snapshot, inflight) == 32, "nl_snapshot.inflight");
static_assert(offsetof(nl_snapshot, ever_caps) == 36, "nl_snapshot.ever_caps");
static_assert(offsetof(nl_snapshot, name_bytes) == 40, "nl_snapshot.name_bytes");
static_assert(offsetof(nl_snapshot, production_admission) == 44, "nl_snapshot.production_admission");
namespace i06_location_detail {
struct handle { intptr_t value = -1; };
struct child_handle { intptr_t process = -1; int64_t pid = 0; bool terminal = false; };
struct close_result { bool confirmed; }; // Failed close: never retry the number.
nl_status platform_duplicate_anchor(const nl_fixture_anchor&, handle&) noexcept;
nl_status platform_open_member(handle parent, const char*, uint32_t, uint32_t,
                               handle&) noexcept;
nl_status platform_metadata(handle, uint32_t, nl_metadata&) noexcept;
close_result platform_close(handle) noexcept;
nl_status platform_child_matches(const child_handle&, const nl_fixture_child&, bool&) noexcept;
nl_status platform_duplicate_child(const nl_fixture_child&, child_handle&) noexcept;
nl_status platform_duplicate_pipe(intptr_t, handle&) noexcept;
/* terminal=true means actual wait/reap (POSIX) or signaled hProcess (Windows).
 * Closing that process HANDLE remains separately required on Windows. */
nl_status platform_poll_child(child_handle&, bool& terminal) noexcept;
close_result platform_close_child(child_handle&) noexcept;
uint64_t platform_monotonic_ms() noexcept;
uint32_t platform_id() noexcept;
bool valid_component(const char*, uint32_t) noexcept;
}
#endif
#endif
