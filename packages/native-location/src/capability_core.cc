#include "../include/location_abi.h"

#include <array>
#include <atomic>
#include <cstring>
#include <mutex>

namespace d = i06_location_detail;
namespace {
struct object_record {
  bool used = false;
  bool unknown = false;
  bool failed = false;
  uint32_t depth = 0;
  d::handle object;
  nl_metadata metadata{};
};
struct child_record {
  bool used = false;
  bool wait_owned = false;
  bool unknown = false;
  d::child_handle child;
  std::array<d::handle, NL_MAX_CHILD_PIPES> pipes{};
  std::array<bool, NL_MAX_CHILD_PIPES> pipe_unknown{};
};
struct owner_record {
  std::atomic<uint64_t> id{0}; // Published once; slots and IDs never recycle.
  std::atomic<uint32_t> epoch{2};
  bool closed = false;
  uint64_t started_ms = 0;
  uint32_t used_caps = 0;
  uint32_t used_children = 0;
  uint32_t name_bytes = 0;
  std::array<object_record, NL_MAX_CAPS> objects{};
  std::array<child_record, NL_MAX_CHILDREN> children{};
};
std::array<owner_record, NL_MAX_OWNER_HISTORY> owners;
std::mutex gate;
std::atomic<uint32_t> inflight{0};

/* Reservation precedes every OS call chain, including close, metadata, clock,
 * duplication and wait. There is no async queue or unregistered callback. */
struct admission {
  bool reserved = false;
  bool locked = false;
  nl_status status = NL_BUSY;
  admission() noexcept {
    uint32_t count = inflight.load();
    while (count < NL_MAX_INFLIGHT) {
      if (inflight.compare_exchange_weak(count, count + 1)) {
        reserved = true;
        break;
      }
    }
    if (!reserved) { status = NL_BUDGET; return; }
    try { locked = gate.try_lock(); } catch (...) { status = NL_INTERNAL; }
    if (locked) status = NL_OK;
  }
  ~admission() {
    if (locked) gate.unlock();
    if (reserved) inflight.fetch_sub(1);
  }
};
owner_record* find(nl_owner_ref ref) noexcept {
  if (ref.value == 0 || ref.value > NL_MAX_OWNER_HISTORY) return nullptr;
  auto& value = owners[static_cast<size_t>(ref.value - 1)];
  return value.id.load() == ref.value ? &value : nullptr;
}
bool equal(const nl_identity& a, const nl_identity& b) noexcept {
  return std::memcmp(&a, &b, sizeof(a)) == 0;
}
bool active(owner_record& owner) noexcept {
  if (owner.closed || owner.epoch.load() != 1) return false;
  const auto now = d::platform_monotonic_ms();
  if (now == UINT64_MAX || now < owner.started_ms || now - owner.started_ms > NL_PREPARE_TTL_MS) {
    owner.epoch.store(2);
    return false;
  }
  return owner.epoch.load() == 1;
}
object_record* cap(owner_record& owner, nl_cap_ref ref) noexcept {
  if (ref.owner != owner.id.load() || ref.generation != 1 ||
      ref.slot >= owner.used_caps) return nullptr;
  auto& object = owner.objects[ref.slot];
  return object.used ? &object : nullptr;
}
bool close_object(object_record& object) noexcept {
  if (object.unknown) return false;
  if (object.object.value == -1) return true;
  const auto result = d::platform_close(object.object);
  // Even on error the numeric handle is retired. No second close of a reused FD.
  object.object.value = -1;
  object.unknown = !result.confirmed;
  return result.confirmed;
}
bool poll_children(owner_record& owner) noexcept {
  bool ended = true;
  for (uint32_t i = 0; i < owner.used_children; ++i) {
    auto& value = owner.children[i];
    if (!value.wait_owned) continue;
    if (value.unknown) { ended = false; continue; }
    if (!value.child.terminal) {
      bool terminal = false;
      const auto status = d::platform_poll_child(value.child, terminal);
      if (status != NL_OK || !terminal) { ended = false; continue; }
    }
    const auto result = d::platform_close_child(value.child);
    if (!result.confirmed) { value.unknown = true; ended = false; continue; }
    value.wait_owned = false;
  }
  return ended;
}
bool close_all(owner_record& owner) noexcept {
  bool ended = true;
  for (uint32_t i = owner.used_caps; i > 0; --i)
    if (!close_object(owner.objects[i - 1])) ended = false;
  for (uint32_t i = 0; i < owner.used_children; ++i) {
    auto& value = owner.children[i];
    for (uint32_t j = 0; j < NL_MAX_CHILD_PIPES; ++j) {
      if (value.pipe_unknown[j]) { ended = false; continue; }
      if (value.pipes[j].value == -1) continue;
      const auto result = d::platform_close(value.pipes[j]);
      value.pipes[j].value = -1;
      if (!result.confirmed) { value.pipe_unknown[j] = true; ended = false; }
    }
  }
  if (!poll_children(owner)) ended = false;
  if (ended) owner.closed = true;
  return ended;
}
void output_cap(owner_record& owner, uint32_t index,
                nl_cap_ref* ref, nl_metadata* metadata) noexcept {
  *ref = {owner.id.load(), index, 1};
  *metadata = owner.objects[index].metadata;
}
} // namespace

namespace i06_location_detail {
bool valid_component(const char* name, uint32_t length) noexcept {
  if (!name || length == 0 || length > NL_MAX_COMPONENT_BYTES) return false;
  if ((length == 1 && name[0] == '.') ||
      (length == 2 && name[0] == '.' && name[1] == '.')) return false;
  if (name[length - 1] == '.' || name[length - 1] == ' ') return false;
  // Validate UTF-8 without normalization; OS object identity, not string case,
  // is the observation. Reject ADS/device/separator/control spellings on BOTH OSes.
  for (uint32_t i = 0; i < length;) {
    const auto first = static_cast<unsigned char>(name[i++]);
    if (first < 0x80) {
      if (first < 0x20 || first == 0x7f || first == '/' || first == '\\' ||
          first == ':' || first == '*' || first == '?' || first == '"' ||
          first == '<' || first == '>' || first == '|') return false;
      continue;
    }
    uint32_t code = 0, extra = 0, minimum = 0;
    if (first >= 0xc2 && first <= 0xdf) { code = first & 31; extra = 1; minimum = 0x80; }
    else if (first >= 0xe0 && first <= 0xef) { code = first & 15; extra = 2; minimum = 0x800; }
    else if (first >= 0xf0 && first <= 0xf4) { code = first & 7; extra = 3; minimum = 0x10000; }
    else return false;
    if (extra > length - i) return false;
    for (uint32_t j = 0; j < extra; ++j) {
      const auto next = static_cast<unsigned char>(name[i++]);
      if ((next & 0xc0) != 0x80) return false;
      code = (code << 6) | (next & 63);
    }
    if (code < minimum || code > 0x10ffff || (code >= 0xd800 && code <= 0xdfff)) return false;
  }
  char base[5]{};
  uint32_t n = 0;
  while (n < length && name[n] != '.' && n < 4) {
    const auto c = name[n];
    base[n] = c >= 'a' && c <= 'z' ? static_cast<char>(c - 'a' + 'A') : c;
    ++n;
  }
  const bool complete = n == length || name[n] == '.';
  if (complete && ((n == 3 && (!std::memcmp(base, "CON", 3) ||
      !std::memcmp(base, "PRN", 3) || !std::memcmp(base, "AUX", 3) ||
      !std::memcmp(base, "NUL", 3))) || (n == 4 && base[3] >= '1' &&
      base[3] <= '9' && (!std::memcmp(base, "COM", 3) || !std::memcmp(base, "LPT", 3)))))
    return false;
  return true;
}
} // namespace i06_location_detail

extern "C" {
nl_status NL_CALL nl_fixture_owner_create(const nl_fixture_anchor* input,
                                          nl_owner_ref* out) noexcept {
  if (!out) return NL_INVALID;
  *out = {};
  if (!input || input->abi_version != NL_ABI_VERSION ||
      input->platform != d::platform_id() || d::platform_id() == 0) return NL_UNSUPPORTED;
  for (auto reserved : input->reserved) if (reserved) return NL_INVALID;
  admission call;
  if (!call.locked) return call.status;
  uint32_t active_count = 0;
  owner_record* owner = nullptr;
  uint64_t id = 0;
  for (size_t i = 0; i < owners.size(); ++i) {
    if (owners[i].id.load() && !owners[i].closed) ++active_count;
    if (!owner && !owners[i].id.load()) { owner = &owners[i]; id = i + 1; }
  }
  if (!owner || active_count >= NL_MAX_ACTIVE_OWNERS) return NL_BUDGET;
  owner->epoch.store(1);
  owner->started_ms = d::platform_monotonic_ms();
  owner->id.store(id);
  *out = {id}; // From here on even a failure has a cleanup owner.
  owner->used_caps = 1;
  auto& root = owner->objects[0];
  root.used = true;
  auto status = owner->started_ms == UINT64_MAX ? NL_UNSUPPORTED :
      d::platform_duplicate_anchor(*input, root.object);
  if (status == NL_OK) status = d::platform_metadata(root.object, NL_DIRECTORY, root.metadata);
  if (status != NL_OK || owner->epoch.load() != 1) {
    if (status == NL_RETAINED) root.unknown = true;
    owner->epoch.store(2);
    root.failed = true;
    close_all(*owner);
    return status != NL_OK ? status : NL_STALE;
  }
  return NL_OK;
}
nl_status NL_CALL nl_owner_root(nl_owner_ref ref, nl_cap_ref* result,
                                nl_metadata* metadata) noexcept {
  if (!result || !metadata) return NL_INVALID;
  *result = {}; *metadata = {};
  admission call; if (!call.locked) return call.status;
  auto* owner = find(ref); if (!owner) return NL_INVALID;
  if (!active(*owner)) return NL_STALE;
  auto& root = owner->objects[0];
  if (root.failed || root.unknown || root.object.value == -1) return NL_RETAINED;
  output_cap(*owner, 0, result, metadata);
  return NL_OK;
}
nl_status NL_CALL nl_owner_acquire(nl_owner_ref ref, uint32_t epoch,
                                   nl_cap_ref parent_ref, const char* name,
                                   uint32_t bytes, uint32_t kind,
                                   const nl_identity* expected, nl_cap_ref* result,
                                   nl_metadata* metadata) noexcept {
  if (!result || !metadata) return NL_INVALID;
  *result = {}; *metadata = {};
  if (!d::valid_component(name, bytes) || (kind != NL_DIRECTORY && kind != NL_REGULAR_FILE)) return NL_INVALID;
  admission call; if (!call.locked) return call.status;
  auto* owner = find(ref); if (!owner) return NL_INVALID;
  if (epoch != 1 || !active(*owner)) return NL_STALE;
  auto* parent = cap(*owner, parent_ref);
  if (!parent || parent->failed || parent->unknown || parent->object.value == -1 ||
      parent->metadata.kind != NL_DIRECTORY) return NL_DENIED;
  if (owner->used_caps == NL_MAX_CAPS || parent->depth >= NL_MAX_DEPTH ||
      bytes > NL_MAX_NAME_BYTES - owner->name_bytes) return NL_BUDGET;
  // Reserve the lifetime slot and bytes BEFORE rechecking parent / opening.
  const auto index = owner->used_caps++;
  auto& value = owner->objects[index]; value.used = true;
  value.depth = parent->depth + 1; owner->name_bytes += bytes;
  nl_metadata current{};
  auto status = d::platform_metadata(parent->object, NL_DIRECTORY, current);
  if (status == NL_RETAINED) parent->unknown = true;
  if (status == NL_OK && !equal(current.identity, parent->metadata.identity)) status = NL_DENIED;
  if (status == NL_OK && owner->epoch.load() == 1) {
    status = d::platform_open_member(parent->object, name, bytes, kind, value.object);
    if (status == NL_RETAINED) {
      // Unexpected pending native open keeps its original work reservation and
      // persistent platform output storage. N0 never fabricates its completion.
      value.unknown = true;
      call.reserved = false;
    }
  } else if (status == NL_OK) status = NL_STALE;
  if (status == NL_OK) {
    status = d::platform_metadata(value.object, kind, value.metadata);
    if (status == NL_RETAINED) value.unknown = true;
  }
  if (status == NL_OK && expected && !equal(*expected, value.metadata.identity)) status = NL_DENIED;
  if (status == NL_OK && !active(*owner)) status = NL_STALE;
  if (status != NL_OK) {
    value.failed = true;
    close_object(value); // Unknown close remains in this original owner's slot.
    return status;
  }
  output_cap(*owner, index, result, metadata);
  return NL_OK;
}
nl_status NL_CALL nl_owner_observe(nl_owner_ref ref, nl_cap_ref object_ref,
                                   nl_metadata* out) noexcept {
  if (!out) return NL_INVALID; *out = {};
  admission call; if (!call.locked) return call.status;
  auto* owner = find(ref); if (!owner) return NL_INVALID;
  if (!active(*owner)) return NL_STALE;
  auto* object = cap(*owner, object_ref);
  if (!object || object->failed || object->unknown || object->object.value == -1) return NL_DENIED;
  nl_metadata observed{};
  auto status = d::platform_metadata(object->object, object->metadata.kind, observed);
  if (status == NL_OK && !equal(observed.identity, object->metadata.identity)) status = NL_DENIED;
  if (status != NL_OK) {
    if (status == NL_RETAINED) object->unknown = true;
    object->failed = true; return status;
  }
  if (!active(*owner)) return NL_STALE;
  object->metadata = observed; *out = observed; return NL_OK;
}
nl_status NL_CALL nl_owner_release(nl_owner_ref ref, nl_cap_ref object_ref) noexcept {
  admission call; if (!call.locked) return call.status;
  auto* owner = find(ref); if (!owner) return NL_INVALID;
  auto* object = cap(*owner, object_ref); if (!object) return NL_INVALID;
  object->failed = true;
  return close_object(*object) ? NL_OK : NL_RETAINED;
}
nl_status NL_CALL nl_owner_revoke(nl_owner_ref ref) noexcept {
  // IDs publish once and owner memory is static: safe even while OS work holds gate.
  auto* owner = find(ref); if (!owner) return NL_INVALID;
  owner->epoch.store(2); return NL_OK;
}
nl_status NL_CALL nl_owner_snapshot(nl_owner_ref ref, nl_snapshot* out) noexcept {
  if (!out) return NL_INVALID; *out = {};
  admission call; if (!call.locked) return call.status;
  auto* owner = find(ref); if (!owner) return NL_INVALID;
  out->abi_version = NL_ABI_VERSION; out->epoch = owner->epoch.load();
  out->closed = owner->closed ? 1 : 0;
  out->accepting = active(*owner) ? 1 : 0; out->epoch = owner->epoch.load();
  out->inflight = inflight.load(); out->ever_caps = owner->used_caps;
  out->name_bytes = owner->name_bytes;
  for (uint32_t i = 0; i < owner->used_caps; ++i) {
    const auto& value = owner->objects[i];
    if (value.object.value != -1) ++out->held_objects;
    if (value.unknown) ++out->unknown_objects;
  }
  for (uint32_t i = 0; i < owner->used_children; ++i) {
    const auto& value = owner->children[i];
    if (value.wait_owned || value.unknown) ++out->pending_children;
    for (uint32_t j = 0; j < NL_MAX_CHILD_PIPES; ++j) {
      if (value.pipes[j].value != -1) ++out->held_pipes;
      if (value.pipe_unknown[j]) ++out->unknown_objects;
    }
  }
  return NL_OK;
}
nl_status NL_CALL nl_owner_close(nl_owner_ref ref) noexcept {
  const auto status = nl_owner_revoke(ref); if (status != NL_OK) return status;
  admission call; if (!call.locked) return call.status;
  auto* owner = find(ref); if (!owner) return NL_INVALID;
  return close_all(*owner) ? NL_OK : NL_RETAINED;
}
nl_status NL_CALL nl_fixture_child_adopt(nl_owner_ref ref, const nl_fixture_child* input,
                                        nl_child_receipt* out) noexcept {
  if (!out) return NL_INVALID; *out = {}; out->abi_version = NL_ABI_VERSION;
  if (!input || input->abi_version != NL_ABI_VERSION || input->platform != d::platform_id()) return NL_INVALID;
  for (auto reserved : input->reserved) if (reserved) return NL_INVALID;
  admission call; if (!call.locked) return call.status;
  auto* owner = find(ref); if (!owner) return NL_INVALID;
  if (!active(*owner)) return NL_STALE;
  if (owner->used_children == NL_MAX_CHILDREN) return NL_BUDGET;
  const auto index = owner->used_children++;
  auto& value = owner->children[index]; value.used = true; out->child_slot = index;
  // Reject a second reaper/holder before the adoption can reap a POSIX child.
  for (auto& other_owner : owners) {
    for (uint32_t i = 0; i < other_owner.used_children; ++i) {
      auto& previous = other_owner.children[i];
      if (!previous.wait_owned) continue;
      bool same = false;
      const auto checked = d::platform_child_matches(previous.child, *input, same);
      if (checked != NL_OK) return checked;
      if (same) return NL_DENIED;
    }
  }
  auto status = d::platform_duplicate_child(*input, value.child);
  value.wait_owned = value.child.process != -1 || value.child.pid > 0 || value.child.terminal;
  out->wait_owned = value.wait_owned ? 1 : 0;
  out->terminal = value.child.terminal ? 1 : 0;
  if (status != NL_OK) return status;
  for (uint32_t i = 0; i < NL_MAX_CHILD_PIPES; ++i) {
    if (input->borrowed_pipes[i] == -1) continue;
    if (owner->epoch.load() != 1) return NL_STALE;
    status = d::platform_duplicate_pipe(input->borrowed_pipes[i], value.pipes[i]);
    if (value.pipes[i].value != -1) ++out->owned_pipes;
    if (status != NL_OK) return status; // Partial adoption is not rolled back fiction.
  }
  return active(*owner) ? NL_OK : NL_STALE;
}
nl_status NL_CALL nl_owner_poll_children(nl_owner_ref ref) noexcept {
  admission call; if (!call.locked) return call.status;
  auto* owner = find(ref); if (!owner) return NL_INVALID;
  return poll_children(*owner) ? NL_OK : NL_RETAINED;
}
nl_status NL_CALL nl_owner_publish(nl_owner_ref) noexcept { return NL_UNSUPPORTED; }
} // extern C
