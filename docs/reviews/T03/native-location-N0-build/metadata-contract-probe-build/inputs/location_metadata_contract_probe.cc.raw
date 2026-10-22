// Private Darwin-only characterization, not a native-location product test.
// Frozen design: 7ea3bfb, metadata-full-positive-contract/decision-experiment.md.
// No product ABI, owner registry, command-line path, retry, or fallback route.
#if !defined(__APPLE__)
#error This private experiment requires the separately pinned Darwin SDK.
#endif

#include <sys/types.h>
#include <sys/acl.h> // Also exposes the user-space kauth wire definitions.
#include <sys/attr.h>
#include <sys/stat.h>
#include <sys/vnode.h>
#include <fcntl.h>
#include <membership.h>
#include <unistd.h>
#include <uuid/uuid.h>

#include <cerrno>
#include <climits>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <limits>
#include <type_traits>

namespace {
constexpr std::size_t kBufferBytes = 4096;
constexpr std::size_t kLineBytes = 96;
constexpr std::size_t kHeaderBytes =
    offsetof(kauth_filesec, fsec_acl) + offsetof(kauth_acl, acl_ace);
constexpr std::size_t kACEBytes = sizeof(kauth_ace);
constexpr std::uint32_t kCommon =
    ATTR_CMN_RETURNED_ATTRS | ATTR_CMN_DEVID | ATTR_CMN_OBJTYPE |
    ATTR_CMN_OWNERID | ATTR_CMN_GRPID | ATTR_CMN_ACCESSMASK |
    ATTR_CMN_EXTENDED_SECURITY | ATTR_CMN_FILEID;
constexpr std::uint32_t kPermissions = 07777;

// These are profile binding checks, not assertions about all SDKs/runtimes.
static_assert(CHAR_BIT == 8 && sizeof(unsigned) == 4 && sizeof(int) == 4);
static_assert(sizeof(std::uint32_t) == 4 && sizeof(std::uint64_t) == 8);
static_assert(std::numeric_limits<int>::min() == INT32_MIN);
static_assert(std::numeric_limits<unsigned>::max() == UINT32_MAX);
static_assert(sizeof(dev_t) == 4 && sizeof(uid_t) == 4 && sizeof(gid_t) == 4);
static_assert(sizeof(fsobj_type_t) == 4);
static_assert(ATTR_BIT_MAP_COUNT == 5 && sizeof(attribute_set_t) == 20);
static_assert(offsetof(attribute_set_t, commonattr) == 0);
static_assert(offsetof(attribute_set_t, volattr) == 4);
static_assert(offsetof(attribute_set_t, dirattr) == 8);
static_assert(offsetof(attribute_set_t, fileattr) == 12);
static_assert(offsetof(attribute_set_t, forkattr) == 16);
static_assert(sizeof(attrreference_t) == 8);
static_assert(offsetof(attrreference_t, attr_dataoffset) == 0);
static_assert(offsetof(attrreference_t, attr_length) == 4);
static_assert(std::is_same<decltype(attrreference_t{}.attr_dataoffset),
                           std::int32_t>::value);
static_assert(sizeof(guid_t) == 16 && sizeof(uuid_t) == 16);
static_assert(offsetof(kauth_filesec, fsec_magic) == 0);
static_assert(offsetof(kauth_filesec, fsec_owner) == 4);
static_assert(offsetof(kauth_filesec, fsec_group) == 20);
static_assert(offsetof(kauth_filesec, fsec_acl) == 36);
static_assert(offsetof(kauth_acl, acl_entrycount) == 0);
static_assert(offsetof(kauth_acl, acl_flags) == 4);
static_assert(offsetof(kauth_acl, acl_ace) == 8 && kHeaderBytes == 44);
static_assert(offsetof(kauth_ace, ace_applicable) == 0);
static_assert(offsetof(kauth_ace, ace_flags) == 16);
static_assert(offsetof(kauth_ace, ace_rights) == 20 && kACEBytes == 24);
// Semantic basis: SDK named definitions + pinned Libc acl_entry/acl_perm/
// acl_translate native export excerpts in this experiment's process archive.
// Export copies qualifier/rights and combines tag(kind) with non-kind flags.
static_assert(ACL_EXTENDED_ALLOW == KAUTH_ACE_PERMIT);
static_assert(ACL_READ_DATA == KAUTH_VNODE_READ_DATA);
static_assert(ACL_LIST_DIRECTORY == KAUTH_VNODE_LIST_DIRECTORY);
static_assert((KAUTH_ACE_PERMIT & ~KAUTH_ACE_KINDMASK) == 0);
static_assert(KAUTH_FILESEC_NOACL == UINT32_MAX);

enum class Decision { eligible, unproven, failed, retained };
struct State {
  Decision decision = Decision::eligible;
  bool output_ok = true;
  uid_t uid{};
  uuid_t uuid{};
  unsigned fstats = 0;
  unsigned attr_reads = 0;
  unsigned cases = 0;
  unsigned output_bytes = 0;
  unsigned output_lines = 0;
  void fail() {
    if (decision == Decision::eligible) decision = Decision::failed;
  }
  void retain() { decision = Decision::retained; }
  void output_failure() {
    output_ok = false;
    if (decision != Decision::retained) decision = Decision::failed;
  }
  bool ready() const { return decision == Decision::eligible && output_ok; }
};

struct Identity { dev_t device{}; ino_t file{}; };
struct Fixture {
  char path[sizeof("/tmp/i06-n0-XXXXXX")] = "/tmp/i06-n0-XXXXXX";
  int anchor = -1;
  int sub = -1;
  int member = -1;
  int creation = -1;
  bool root_created = false;
  bool sub_created = false;
  bool member_created = false;
  Identity created_member{};
};

// A retired descriptor number is never closed again, even on EINTR/error.
void close_once(int& slot, State& state) {
  if (slot < 0) return;
  const int fd = slot;
  slot = -1;
  if (::close(fd) != 0) state.retain();
}

void cleanup(Fixture& tree, State& state) {
  close_once(tree.creation, state);
  close_once(tree.member, state);
  close_once(tree.sub, state);
  if (tree.member_created) {
    tree.member_created = false;
    if (::unlinkat(tree.anchor, "member", 0) != 0) state.retain();
  }
  if (tree.sub_created) {
    tree.sub_created = false;
    if (::unlinkat(tree.anchor, "sub", AT_REMOVEDIR) != 0) state.retain();
  }
  close_once(tree.anchor, state);
  if (tree.root_created) {
    tree.root_created = false;
    if (::rmdir(tree.path) != 0) state.retain();
  }
}

// No exceptions/early process exit while a known fixture resource is live.
// Only this helper owns an ACL working copy; entry/permset/flagset are borrowed.
bool set_acl(int fd, bool one, bool directory, State& state) {
  acl_t acl = ::acl_init(one ? 1 : 0);
  if (acl == nullptr) { state.fail(); return false; }
  bool known = true;
  bool ok = true;
  if (one) {
    acl_entry_t entry{};
    const acl_t before = acl;
    const int made = ::acl_create_entry(&acl, &entry);
    if (made != 0) {
      ok = false;
      if (acl != before) known = false;
    } else if (acl == nullptr || entry == nullptr) {
      // Broken success/output ownership is not a pointer we can guess/free.
      known = false;
      ok = false;
    }
    if (ok) ok = ::acl_set_tag_type(entry, ACL_EXTENDED_ALLOW) == 0;
    if (ok) ok = ::acl_set_qualifier(entry, state.uuid) == 0;
    acl_permset_t permissions{};
    if (ok) ok = ::acl_get_permset(entry, &permissions) == 0;
    if (ok) ok = permissions != nullptr;
    if (ok) ok = ::acl_clear_perms(permissions) == 0;
    if (ok) ok = ::acl_add_perm(permissions,
                              directory ? ACL_LIST_DIRECTORY : ACL_READ_DATA) == 0;
    if (ok) ok = ::acl_set_permset(entry, permissions) == 0;
    acl_flagset_t flags{};
    if (ok) ok = ::acl_get_flagset_np(entry, &flags) == 0;
    if (ok) ok = flags != nullptr;
    if (ok) ok = ::acl_clear_flags_np(flags) == 0;
    if (ok) ok = ::acl_set_flagset_np(entry, flags) == 0;
  }
  if (ok && one) ok = ::acl_valid(acl) == 0; // Original empty setup has no extra gate.
  if (ok) ok = ::acl_set_fd_np(fd, acl, ACL_TYPE_EXTENDED) == 0;
  if (!known) state.retain();
  else if (::acl_free(acl) != 0) state.retain(); // Exactly one release attempt.
  if (!ok) state.fail();
  return ok && state.ready();
}

bool safe_stat(const struct stat& st, bool directory, const State& state) {
  return (directory ? S_ISDIR(st.st_mode) : S_ISREG(st.st_mode)) &&
         st.st_uid == state.uid && (st.st_mode & 0022) == 0 &&
         (directory ? st.st_nlink != 0 : st.st_nlink == 1);
}

bool make_fixture(Fixture& tree, bool negative, State& state) {
  if (::mkdtemp(tree.path) == nullptr) { state.fail(); return false; }
  tree.root_created = true;
  tree.anchor = ::open(tree.path, O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC);
  if (tree.anchor < 0) { state.fail(); return false; }
  if (!set_acl(tree.anchor, false, true, state)) return false;
  if (::mkdirat(tree.anchor, "sub", 0700) != 0) { state.fail(); return false; }
  tree.sub_created = true;
  tree.creation = ::openat(tree.anchor, "member",
                          O_CREAT | O_EXCL | O_WRONLY | O_CLOEXEC, 0600);
  if (tree.creation < 0) { state.fail(); return false; }
  tree.member_created = true;
  struct stat created{};
  ++state.fstats; // At most two creation identity records, not ACL observations.
  if (::fstat(tree.creation, &created) != 0 || !safe_stat(created, false, state)) {
    state.fail();
    return false;
  }
  tree.created_member = {created.st_dev, created.st_ino};
  if (negative && !set_acl(tree.creation, true, false, state)) return false;
  close_once(tree.creation, state);
  if (!state.ready()) return false;
  if (negative && !set_acl(tree.anchor, true, true, state)) return false;
  return state.ready();
}

struct Observation {
  unsigned id{}, api{};
  int error{};
  unsigned bytes{}, attrs{}, sec{};
  unsigned known{}, same{}, type{}, owner{}, mode{}, links{};
  unsigned ref{}, magic{}, form{}, flags{}, count{};
};

// All access is memcpy; no buffer-to-struct casts or unaligned dereference.
struct Reader {
  const unsigned char* data;
  std::size_t size;
  std::size_t position = 0;
  template <typename T> bool take(T& value) {
    static_assert(std::is_trivially_copyable<T>::value);
    if (position % 4 != 0 || position > size || sizeof(T) > size - position)
      return false;
    std::memcpy(&value, data + position, sizeof(T));
    position += sizeof(T);
    return position % 4 == 0;
  }
};

bool checked_add(std::size_t a, std::size_t b, std::size_t& result) {
  if (b > std::numeric_limits<std::size_t>::max() - a) return false;
  result = a + b;
  return true;
}
bool checked_mul(std::size_t a, std::size_t b, std::size_t& result) {
  if (a != 0 && b > std::numeric_limits<std::size_t>::max() / a) return false;
  result = a * b;
  return true;
}
bool rounded4(std::size_t value, std::size_t& result) {
  if (!checked_add(value, 3, result)) return false;
  result &= ~std::size_t{3};
  return true;
}

Decision parse(const unsigned char (&buffer)[kBufferBytes], const struct stat& st,
               bool directory, bool one, const Identity* expected,
               const State& state, Observation& out) {
  std::uint32_t length{};
  std::memcpy(&length, buffer, sizeof(length));
  out.bytes = length; // Only invoked after successful fgetattrlist.
  if (length < sizeof(length) + sizeof(attribute_set_t) || length > kBufferBytes ||
      length % 4 != 0) return Decision::failed;
  Reader reader{buffer, length, sizeof(length)};
  attribute_set_t returned{};
  if (!reader.take(returned)) return Decision::failed;
  const std::uint32_t file_mask = directory ? 0 : ATTR_FILE_LINKCOUNT;
  if ((returned.commonattr & ~kCommon) != 0 || returned.volattr != 0 ||
      returned.dirattr != 0 || returned.forkattr != 0 ||
      (returned.fileattr & ~file_mask) != 0) return Decision::failed;
  out.sec = (returned.commonattr & ATTR_CMN_EXTENDED_SECURITY) != 0;
  out.attrs = returned.commonattr == kCommon && returned.fileattr == file_mask;
  const auto required = kCommon & ~ATTR_CMN_EXTENDED_SECURITY;
  if ((returned.commonattr & required) != required ||
      returned.fileattr != file_mask) return Decision::failed;
  dev_t device{};
  fsobj_type_t type{};
  uid_t owner{};
  gid_t group{};
  std::uint32_t access{};
  attrreference_t security{};
  std::uint64_t file{};
  std::uint32_t links{};
  if (!reader.take(device) || !reader.take(type) || !reader.take(owner) ||
      !reader.take(group) || !reader.take(access)) return Decision::failed;
  const std::size_t reference_at = reader.position;
  if (!reader.take(security) || !reader.take(file) ||
      (!directory && !reader.take(links))) return Decision::failed;
  const bool identity = device == st.st_dev && file == st.st_ino &&
      (expected == nullptr || (device == expected->device && file == expected->file));
  out.same = identity;
  if (!identity || type != (directory ? VDIR : VREG) || owner != st.st_uid ||
      group != st.st_gid || (access & kPermissions) != (st.st_mode & kPermissions) ||
      (!directory && links != st.st_nlink)) return Decision::failed;
  // PACK_INVAL occupies the fixed slot, but a missing bit/zero placeholder
  // never attests absence. Do not interpret the placeholder as a kauth header.
  if (!out.sec || security.attr_length == 0)
    return one ? Decision::failed : Decision::unproven;
  if (security.attr_dataoffset % 4 != 0 || security.attr_length % 4 != 0)
    return Decision::failed;
  // Do the signed addition in a range wide enough for the 4KiB base + Int32.
  const std::int64_t signed_start = static_cast<std::int64_t>(reference_at) +
                                   security.attr_dataoffset;
  if (signed_start < 0 || static_cast<std::uint64_t>(signed_start) > length)
    return Decision::failed;
  const auto start = static_cast<std::size_t>(signed_start);
  std::size_t end{};
  if (start < reader.position || start % 4 != 0 ||
      !checked_add(start, security.attr_length, end) || end != length ||
      start != reader.position || security.attr_length < kHeaderBytes)
    return Decision::failed;
  out.ref = 1;
  Reader acl{buffer + start, security.attr_length};
  std::uint32_t magic{}, count{}, flags{};
  guid_t ignored_owner{}, ignored_group{};
  if (!acl.take(magic) || !acl.take(ignored_owner) || !acl.take(ignored_group) ||
      !acl.take(count) || !acl.take(flags) || magic != KAUTH_FILESEC_MAGIC)
    return Decision::failed;
  out.magic = 1;
  out.count = count;
  out.flags = flags == 0;
  if (flags != 0) return one ? Decision::failed : Decision::unproven;
  // Distinguish sentinel BEFORE any count multiplication.
  const bool no_acl = count == KAUTH_FILESEC_NOACL;
  if (!no_acl && count > 1) return Decision::failed;
  std::size_t ace_bytes{}, payload{}, rounded{};
  if (!checked_mul(no_acl ? 0 : count, kACEBytes, ace_bytes) ||
      !checked_add(kHeaderBytes, ace_bytes, payload) || !rounded4(payload, rounded) ||
      rounded != security.attr_length) return Decision::failed;
  if (!one) {
    if (!no_acl && count != 0) return Decision::failed;
    out.form = no_acl ? 1 : 2;
    return Decision::eligible;
  }
  if (no_acl || count != 1) return Decision::failed;
  guid_t applicable{};
  std::uint32_t entry_flags{}, rights{};
  if (!acl.take(applicable) || !acl.take(entry_flags) || !acl.take(rights) ||
      acl.position != security.attr_length ||
      std::memcmp(&applicable, state.uuid, sizeof(applicable)) != 0 ||
      entry_flags != KAUTH_ACE_PERMIT ||
      rights != (directory ? KAUTH_VNODE_LIST_DIRECTORY : KAUTH_VNODE_READ_DATA))
    return Decision::failed;
  out.form = 3;
  return Decision::eligible;
}

// Bounded line formatting. One write attempt, no retry/alternate stream.
template <typename... Args>
void line(State& state, const char* format, Args... args) {
  if (!state.output_ok) return;
  char bytes[kLineBytes + 1]{};
  const int length = std::snprintf(bytes, sizeof(bytes), format, args...);
  if (length < 0 || static_cast<unsigned>(length) > kLineBytes ||
      state.output_lines >= 16 || state.output_bytes > 1018 ||
      static_cast<unsigned>(length) > 1018 - state.output_bytes) {
    state.output_failure();
    return;
  }
  ++state.output_lines;
  state.output_bytes += static_cast<unsigned>(length);
  if (std::fwrite(bytes, 1, static_cast<std::size_t>(length), stdout) !=
      static_cast<std::size_t>(length)) {
    state.output_failure();
  }
}

void emit(const Observation& o, State& state) {
  line(state, "N0 ACL obs case=%u api=%u err=%d bytes=%u attrs=%u sec=%u\n",
       o.id, o.api, o.error, o.bytes, o.attrs, o.sec);
  line(state, "N0 ACL obj case=%u known=%u same=%u type=%u owner=%u mode=%u links=%u\n",
       o.id, o.known, o.same, o.type, o.owner, o.mode, o.links);
  line(state, "N0 ACL val case=%u ref=%u magic=%u form=%u flags=%u count=%u\n",
       o.id, o.ref, o.magic, o.form, o.flags, o.count);
}

bool observe(unsigned id, int fd, bool directory, bool one,
             const Identity* expected, unsigned char (&buffer)[kBufferBytes],
             State& state, Observation& out) {
  if (!state.ready() || id != state.cases || id > 4 || state.fstats >= 7 ||
      state.attr_reads >= 5) { state.fail(); return false; }
  ++state.cases;
  out = {};
  out.id = id;
  out.api = 1;
  struct stat st{};
  ++state.fstats;
  if (::fstat(fd, &st) != 0) {
    out.error = errno;
    state.fail();
  } else {
    out.known = 1;
    out.type = directory ? S_ISDIR(st.st_mode) : S_ISREG(st.st_mode);
    out.owner = st.st_uid == state.uid;
    out.mode = (st.st_mode & 0022) == 0;
    out.links = directory ? st.st_nlink != 0 : st.st_nlink == 1;
    if (!safe_stat(st, directory, state)) state.fail();
    else {
      struct attrlist request{};
      request.bitmapcount = ATTR_BIT_MAP_COUNT;
      request.commonattr = kCommon;
      request.fileattr = directory ? 0 : ATTR_FILE_LINKCOUNT;
      std::memset(buffer, 0, sizeof(buffer));
      out.api = 2;
      ++state.attr_reads;
      if (::fgetattrlist(fd, &request, buffer, sizeof(buffer),
                        FSOPT_REPORT_FULLSIZE | FSOPT_PACK_INVAL_ATTRS) != 0) {
        out.error = errno;
        state.fail();
      } else state.decision = parse(buffer, st, directory, one, expected, state, out);
    }
  }
  return state.ready();
}
} // namespace

int main(int argc, char**) {
  State state{};
  Fixture empty{}, negative{};
  Observation observations[5]{}; // Fixed bookkeeping, not extra response buffers.
  static_assert(sizeof(observations) == 340);
  unsigned char buffer[kBufferBytes]{}; // One reusable application response buffer.
  // Unbuffered output makes each checked write the only application attempt.
  // No claim about libc internal buffering, allocation, or wall-clock bounds.
  if (std::setvbuf(stdout, nullptr, _IONBF, 0) != 0) {
    state.output_failure();
  }
  if (argc != 1) state.fail();
  if (state.ready()) {
    state.uid = ::geteuid(); // Exactly once; no self UID/groups mutation.
    if (make_fixture(empty, false, state) &&
        observe(0, empty.anchor, true, false, nullptr, buffer, state, observations[0])) {
      empty.sub = ::openat(empty.anchor, "sub",
          O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC | O_NONBLOCK);
      if (empty.sub < 0) state.fail();
      if (state.ready() && observe(1, empty.sub, true, false, nullptr, buffer, state, observations[1])) {
        empty.member = ::openat(empty.anchor, "member",
            O_EVTONLY | O_NOFOLLOW | O_CLOEXEC | O_NONBLOCK);
        if (empty.member < 0) state.fail();
        if (state.ready() && observe(2, empty.member, false, false,
                                    &empty.created_member, buffer, state, observations[2])) {
          // Do not allocate N or query UUID until ALL three E samples qualify.
          if (::mbr_uid_to_uuid(state.uid, state.uuid) != 0) state.fail();
          if (state.ready() && make_fixture(negative, true, state) &&
              observe(3, negative.anchor, true, true, nullptr, buffer, state, observations[3])) {
            negative.member = ::openat(negative.anchor, "member",
                O_EVTONLY | O_NOFOLLOW | O_CLOEXEC | O_NONBLOCK);
            if (negative.member < 0) state.fail();
            if (state.ready()) observe(4, negative.member, false, true,
                                      &negative.created_member, buffer, state, observations[4]);
          }
        }
      }
    }
  }
  // All known resources are handled once even after query/setup/output failure.
  cleanup(negative, state);
  cleanup(empty, state);
  if (state.decision == Decision::eligible &&
      (state.cases != 5 || state.fstats != 7 || state.attr_reads != 5)) state.fail();
  // Defer all writes until after cleanup: even a broken stdout/SIGPIPE cannot
  // bypass the known-resource cleanup path. No signal/process API is added.
  for (unsigned i = 0; i < state.cases; ++i) emit(observations[i], state);
  const char* token = "failed";
  switch (state.decision) {
    case Decision::eligible: token = "eligible"; break;
    case Decision::unproven: token = "unproven"; break;
    case Decision::failed: token = "failed"; break;
    case Decision::retained: token = "retained"; break;
  }
  line(state, "N0 ACL disposition=%s\n", token);
  return state.output_ok && state.decision == Decision::eligible ? 0 :
         state.decision == Decision::retained ? 3 :
         state.decision == Decision::unproven ? 2 : 1;
}
