#include <node_api.h>
#include "../include/location_abi.h"

#include <array>
#include <atomic>
#include <cstring>
#include <mutex>
#include <new>

#if defined(NL_NODE_FIXTURE_HOST)
namespace i06_location_detail {
nl_status fixture_node_bootstrap(napi_env, napi_value) noexcept;
}
#endif

// No addon load-path resolver, absolute path opener or child bootstrap is exported
// to JS. A trusted native fixture harness calls nl_node_bind_fixture after native
// anchor adoption. Merely importing the addon exposes version/unsupported flags.
namespace {
struct token { bool issued = false; nl_cap_ref ref{}; nl_identity identity{}; };
struct binding {
  std::atomic<bool> used{false};
  bool cleanup_registered = false;
  std::atomic<napi_env> env{nullptr};
  nl_owner_ref owner{};
  std::array<token, NL_MAX_CAPS> tokens{};
};
std::array<binding, NL_MAX_OWNER_HISTORY> bindings{};
std::mutex binding_gate;

bool property(napi_env env, napi_value object, const char* name, napi_value value) noexcept {
  return napi_set_named_property(env, object, name, value) == napi_ok;
}
napi_value number(napi_env env, uint32_t value) noexcept {
  napi_value result = nullptr;
  return napi_create_uint32(env, value, &result) == napi_ok ? result : nullptr;
}
napi_value response(napi_env env, nl_status status) noexcept {
  napi_value result = nullptr;
  if (napi_create_object(env, &result) != napi_ok) return nullptr;
  const auto code = number(env, status);
  return code && property(env, result, "status", code) ? result : nullptr;
}
bool field(napi_env env, napi_value value, const char* key, uint32_t x) noexcept {
  const auto item = number(env, x); return item && property(env, value, key, item);
}
napi_value hex(napi_env env, const uint8_t* value, size_t bytes) noexcept {
  static constexpr char digits[] = "0123456789abcdef";
  char text[33]{};
  if (bytes > 16) return nullptr;
  for (size_t i = 0; i < bytes; ++i) {
    text[i * 2] = digits[value[i] >> 4]; text[i * 2 + 1] = digits[value[i] & 15];
  }
  napi_value result = nullptr;
  return napi_create_string_utf8(env, text, bytes * 2, &result) == napi_ok ? result : nullptr;
}
bool metadata(napi_env env, napi_value result, const nl_metadata& value) noexcept {
  napi_value object = nullptr;
  if (napi_create_object(env, &object) != napi_ok) return false;
  const auto volume = hex(env, value.identity.volume, 8);
  const auto file = hex(env, value.identity.file, 16);
  // link_count is serialized without passing through floating point.
  char links[21]{}; uint64_t n = value.link_count; size_t length = 0;
  do { links[length++] = static_cast<char>('0' + n % 10); n /= 10; } while (n && length < 20);
  for (size_t i = 0; i < length / 2; ++i) {
    const auto c = links[i]; links[i] = links[length - i - 1]; links[length - i - 1] = c;
  }
  napi_value count = nullptr;
  if (napi_create_string_utf8(env, links, length, &count) != napi_ok) return false;
  return volume && file && field(env, object, "kind", value.kind) &&
      property(env, object, "volume", volume) && property(env, object, "file", file) &&
      property(env, object, "links", count) && field(env, object, "aclChecked", value.acl_checked) &&
      field(env, object, "heldObjectOnly", 1) && field(env, object, "productionAdmission", 0) &&
      property(env, result, "metadata", object);
}
bool add_cap(binding& state, napi_value result, nl_cap_ref ref,
             const nl_metadata& observed) noexcept {
  if (ref.owner != state.owner.value || ref.slot >= state.tokens.size()) return false;
  auto& value = state.tokens[ref.slot];
  if (value.issued && (value.ref.owner != ref.owner || value.ref.generation != ref.generation)) return false;
  value.issued = true; value.ref = ref; value.identity = observed.identity;
  napi_value external = nullptr;
  // External pointers are NEVER dereferenced before exact membership validation.
  if (napi_create_external(state.env, &value, nullptr, nullptr, &external) != napi_ok) return false;
  return property(state.env, result, "cap", external) && metadata(state.env, result, observed);
}
token* parse_cap(binding& state, napi_value input) noexcept {
  void* pointer = nullptr;
  if (napi_get_value_external(state.env, input, &pointer) != napi_ok) return nullptr;
  for (auto& candidate : state.tokens)
    if (&candidate == pointer && candidate.issued) return &candidate;
  return nullptr;
}
binding* args(napi_env env, napi_callback_info info, size_t& count, napi_value* values) noexcept {
  void* data = nullptr;
  if (napi_get_cb_info(env, info, &count, values, nullptr, &data) != napi_ok) return nullptr;
  // Callback data is a private native registry entry, never supplied by JS.
  for (auto& candidate : bindings)
    if (&candidate == data && candidate.used && candidate.env == env) return &candidate;
  return nullptr;
}
napi_value root(napi_env env, napi_callback_info info) noexcept {
  size_t n = 0; auto* state = args(env, info, n, nullptr);
  if (!state) return response(env, NL_INVALID);
  nl_cap_ref ref{}; nl_metadata observed{};
  const auto status = nl_owner_root(state->owner, &ref, &observed);
  const auto result = response(env, status);
  if (status == NL_OK && result && !add_cap(*state, result, ref, observed)) {
    nl_owner_revoke(state->owner); return response(env, NL_INTERNAL);
  }
  return result;
}
napi_value acquire(napi_env env, napi_callback_info info, uint32_t kind) noexcept {
  size_t n = 3; napi_value values[3]{}; auto* state = args(env, info, n, values);
  if (!state || n < 2) return response(env, NL_INVALID);
  auto* parent = parse_cap(*state, values[0]); if (!parent) return response(env, NL_INVALID);
  napi_valuetype type = napi_undefined;
  if (napi_typeof(env, values[1], &type) != napi_ok || type != napi_string) return response(env, NL_INVALID);
  size_t units = 0;
  if (napi_get_value_string_utf16(env, values[1], nullptr, 0, &units) != napi_ok ||
      units == 0 || units > NL_MAX_COMPONENT_BYTES) return response(env, NL_INVALID);
  char16_t utf16[NL_MAX_COMPONENT_BYTES + 1]{}; size_t copied_units = 0;
  if (napi_get_value_string_utf16(env, values[1], utf16, NL_MAX_COMPONENT_BYTES + 1,
      &copied_units) != napi_ok || copied_units != units) return response(env, NL_INVALID);
  for (size_t i = 0; i < units; ++i) {
    const auto unit = static_cast<uint16_t>(utf16[i]);
    if (unit >= 0xd800 && unit <= 0xdbff) {
      if (++i >= units || utf16[i] < 0xdc00 || utf16[i] > 0xdfff) return response(env, NL_INVALID);
    } else if (unit >= 0xdc00 && unit <= 0xdfff) return response(env, NL_INVALID);
  }
  size_t bytes = 0;
  if (napi_get_value_string_utf8(env, values[1], nullptr, 0, &bytes) != napi_ok ||
      bytes == 0 || bytes > NL_MAX_COMPONENT_BYTES) return response(env, NL_INVALID);
  char name[NL_MAX_COMPONENT_BYTES + 1]{}; size_t copied = 0;
  if (napi_get_value_string_utf8(env, values[1], name, sizeof(name), &copied) != napi_ok || copied != bytes)
    return response(env, NL_INVALID);
  token* expected = nullptr;
  if (n == 3) {
    expected = parse_cap(*state, values[2]);
    if (!expected) return response(env, NL_INVALID);
  }
  nl_cap_ref ref{}; nl_metadata observed{};
  const auto status = nl_owner_acquire(state->owner, 1, parent->ref, name,
      static_cast<uint32_t>(bytes), kind, expected ? &expected->identity : nullptr, &ref, &observed);
  const auto result = response(env, status);
  if (status == NL_OK && result && !add_cap(*state, result, ref, observed)) {
    nl_owner_revoke(state->owner); return response(env, NL_INTERNAL);
  }
  return result;
}
napi_value directory(napi_env env, napi_callback_info info) noexcept { return acquire(env, info, NL_DIRECTORY); }
napi_value file(napi_env env, napi_callback_info info) noexcept { return acquire(env, info, NL_REGULAR_FILE); }
napi_value observe(napi_env env, napi_callback_info info) noexcept {
  size_t n = 1; napi_value values[1]{}; auto* state = args(env, info, n, values);
  if (!state || n != 1) return response(env, NL_INVALID);
  auto* value = parse_cap(*state, values[0]); if (!value) return response(env, NL_INVALID);
  nl_metadata observed{};
  const auto status = nl_owner_observe(state->owner, value->ref, &observed);
  const auto result = response(env, status);
  if (status == NL_OK && result && !metadata(env, result, observed)) return response(env, NL_INTERNAL);
  return result;
}
napi_value release(napi_env env, napi_callback_info info) noexcept {
  size_t n = 1; napi_value values[1]{}; auto* state = args(env, info, n, values);
  if (!state || n != 1) return response(env, NL_INVALID);
  auto* value = parse_cap(*state, values[0]);
  return response(env, value ? nl_owner_release(state->owner, value->ref) : NL_INVALID);
}
napi_value revoke(napi_env env, napi_callback_info info) noexcept {
  size_t n = 0; auto* state = args(env, info, n, nullptr);
  return response(env, state ? nl_owner_revoke(state->owner) : NL_INVALID);
}
napi_value close_owner(napi_env env, napi_callback_info info) noexcept {
  size_t n = 0; auto* state = args(env, info, n, nullptr);
  return response(env, state ? nl_owner_close(state->owner) : NL_INVALID);
}
napi_value snapshot(napi_env env, napi_callback_info info) noexcept {
  size_t n = 0; auto* state = args(env, info, n, nullptr);
  if (!state) return response(env, NL_INVALID);
  nl_snapshot value{}; const auto status = nl_owner_snapshot(state->owner, &value);
  const auto result = response(env, status);
  if (status != NL_OK || !result) return result;
  if (!field(env, result, "abiVersion", value.abi_version) ||
      !field(env, result, "epoch", value.epoch) || !field(env, result, "accepting", value.accepting) ||
      !field(env, result, "closed", value.closed) || !field(env, result, "heldObjects", value.held_objects) ||
      !field(env, result, "unknownObjects", value.unknown_objects) ||
      !field(env, result, "pendingChildren", value.pending_children) || !field(env, result, "heldPipes", value.held_pipes) ||
      !field(env, result, "inflight", value.inflight) || !field(env, result, "everCaps", value.ever_caps) ||
      !field(env, result, "nameBytes", value.name_bytes) || !field(env, result, "productionAdmission", 0))
    return response(env, NL_INTERNAL);
  return result;
}
void cleanup(void* data) noexcept {
  auto* state = static_cast<binding*>(data);
  // One real cleanup attempt only. A retained owner stays in the static native
  // registry; env teardown does not sign release, retry a close number or kill.
  nl_owner_revoke(state->owner); nl_owner_close(state->owner);
  state->env = nullptr;
}
napi_value init(napi_env env, napi_value exports) {
  field(env, exports, "abiVersion", NL_ABI_VERSION);
  field(env, exports, "fixtureBound", 0);
  field(env, exports, "productionAdmission", 0);
#if defined(NL_NODE_FIXTURE_HOST)
  if (i06_location_detail::fixture_node_bootstrap(env, exports) != NL_OK)
    field(env, exports, "fixtureBound", 0);
#endif
  return exports;
}
} // namespace

/* Trusted native test-host entry, not a JS export. No raw external from JS is
 * accepted as owner. T03 must document how its native fixture host calls this. */
extern "C" NL_API nl_status NL_CALL nl_node_bind_fixture(napi_env env, napi_value target,
                                                        nl_owner_ref owner) noexcept {
  if (!env || !target) return NL_INVALID;
  try {
    std::lock_guard<std::mutex> lock(binding_gate);
    nl_snapshot current{};
    if (nl_owner_snapshot(owner, &current) != NL_OK || current.closed) return NL_INVALID;
    binding* state = nullptr;
    for (auto& value : bindings) {
      if (value.used && value.env == env) return NL_DENIED; // One binding per env.
      if (!value.used && !state) state = &value;
    }
    if (!state) return NL_BUDGET;
    state->used = true; state->env = env; state->owner = owner;
    if (napi_add_env_cleanup_hook(env, cleanup, state) != napi_ok) {
      nl_owner_revoke(owner); nl_owner_close(owner); return NL_INTERNAL;
    }
    state->cleanup_registered = true;
    const napi_property_descriptor methods[] = {
      {"root", nullptr, root, nullptr, nullptr, nullptr, napi_default, state},
      {"directory", nullptr, directory, nullptr, nullptr, nullptr, napi_default, state},
      {"file", nullptr, file, nullptr, nullptr, nullptr, napi_default, state},
      {"observe", nullptr, observe, nullptr, nullptr, nullptr, napi_default, state},
      {"release", nullptr, release, nullptr, nullptr, nullptr, napi_default, state},
      {"snapshot", nullptr, snapshot, nullptr, nullptr, nullptr, napi_default, state},
      {"revoke", nullptr, revoke, nullptr, nullptr, nullptr, napi_default, state},
      {"close", nullptr, close_owner, nullptr, nullptr, nullptr, napi_default, state},
    };
    if (napi_define_properties(env, target, sizeof(methods) / sizeof(methods[0]), methods) != napi_ok ||
        !field(env, target, "abiVersion", NL_ABI_VERSION) || !field(env, target, "fixtureBound", 1) ||
        !field(env, target, "productionAdmission", 0)) {
      nl_owner_revoke(owner); nl_owner_close(owner); return NL_INTERNAL;
    }
    return NL_OK;
  } catch (...) { nl_owner_revoke(owner); nl_owner_close(owner); return NL_INTERNAL; }
}
NAPI_MODULE(i06_native_location, init)
