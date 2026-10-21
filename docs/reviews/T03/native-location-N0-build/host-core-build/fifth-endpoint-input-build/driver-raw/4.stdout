#include "../include/location_abi.h"

#if defined(__APPLE__)
#include <cerrno>
#include <climits>
#include <cstdio>
#include <cstring>
#include <fcntl.h>
#include <sys/acl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

namespace i06_location_detail {
namespace {
nl_status error_status(int error) noexcept {
  if (error == EMFILE || error == ENFILE || error == ENOMEM) return NL_BUDGET;
  if (error == ENOSYS || error == ENOTSUP) return NL_UNSUPPORTED;
  return NL_DENIED;
}
void unsupported_error(const char* stage, int error) noexcept {
  std::fprintf(stderr, "N0 unsupported stage=%s errno=%d\n", stage, error);
  errno = error;
}
void unsupported_clock_reason(const char* reason) noexcept {
  const int saved_errno = errno;
  std::fprintf(stderr, "N0 unsupported stage=clock reason=%s\n", reason);
  errno = saved_errno;
}
void put64(uint8_t* out, uint64_t value) noexcept {
  for (unsigned i = 0; i < 8; ++i) { out[i] = static_cast<uint8_t>(value); value >>= 8; }
}
int fd(handle value) noexcept { return static_cast<int>(value.value); }
bool valid_fd(intptr_t value) noexcept { return value >= 0 && value <= INT_MAX; }
}
uint32_t platform_id() noexcept { return NL_PLATFORM_MACOS; }
uint64_t platform_monotonic_ms() noexcept {
  timespec now{};
  if (clock_gettime(CLOCK_MONOTONIC, &now) != 0) {
    const int error = errno;
    unsupported_error("clock", error);
    return UINT64_MAX;
  }
  if (now.tv_sec < 0) {
    unsupported_clock_reason("negative-sec");
    return UINT64_MAX;
  }
  if (static_cast<uint64_t>(now.tv_sec) > (UINT64_MAX - 999) / 1000) {
    unsupported_clock_reason("range");
    return UINT64_MAX;
  }
  return static_cast<uint64_t>(now.tv_sec) * 1000 + static_cast<uint64_t>(now.tv_nsec / 1000000);
}
nl_status platform_duplicate_anchor(const nl_fixture_anchor& value, handle& out) noexcept {
  out.value = -1;
  if (value.platform != NL_PLATFORM_MACOS || !valid_fd(value.borrowed_directory)) return NL_INVALID;
  const int duplicate = fcntl(static_cast<int>(value.borrowed_directory), F_DUPFD_CLOEXEC, 0);
  if (duplicate < 0) {
    const int error = errno;
    const auto status = error_status(error);
    if (status == NL_UNSUPPORTED) unsupported_error("duplicate", error);
    return status;
  }
  out.value = duplicate; // Caller owns this even if later metadata rejects it.
  return NL_OK;
}
nl_status platform_open_member(handle parent, const char* name, uint32_t bytes,
                               uint32_t kind, handle& out) noexcept {
  out.value = -1;
  if (!valid_fd(parent.value) || !valid_component(name, bytes)) return NL_INVALID;
  char component[NL_MAX_COMPONENT_BYTES + 1]{};
  std::memcpy(component, name, bytes);
  // O_EVTONLY gives no file-content read operation in N0. Directories need a
  // real directory FD for later root-relative acquire, without following links.
  const int flags = O_NOFOLLOW | O_CLOEXEC | O_NONBLOCK |
      (kind == NL_DIRECTORY ? O_RDONLY | O_DIRECTORY : O_EVTONLY);
  const int opened = openat(fd(parent), component, flags);
  if (opened < 0) return error_status(errno);
  out.value = opened;
  return NL_OK;
}
nl_status platform_metadata(handle object, uint32_t kind, nl_metadata& out) noexcept {
  out = {};
  if (!valid_fd(object.value)) return NL_INVALID;
  struct stat value{};
  if (fstat(fd(object), &value) != 0) {
    const int error = errno;
    const auto status = error_status(error);
    if (status == NL_UNSUPPORTED) unsupported_error("fstat", error);
    return status;
  }
  if ((kind == NL_DIRECTORY && !S_ISDIR(value.st_mode)) ||
      (kind == NL_REGULAR_FILE && !S_ISREG(value.st_mode))) return NL_DENIED;
  if (kind != NL_DIRECTORY && kind != NL_REGULAR_FILE) return NL_INVALID;
  if (value.st_uid != geteuid() || (value.st_mode & 0022) != 0 ||
      value.st_nlink == 0 || (kind == NL_REGULAR_FILE && value.st_nlink != 1)) return NL_DENIED;
  // Deliberately conservative fixture ACL policy: no extended ACE accepted.
  // Snapshot is not a continuing namespace/ACL grant. Failed query is unknown.
  acl_t acl = acl_get_fd_np(fd(object), ACL_TYPE_EXTENDED);
  if (acl == nullptr) {
    const int error = errno;
    const nl_status status = NL_UNSUPPORTED;
    unsupported_error("acl-null", error);
    return status;
  }
  acl_entry_t entry{};
  const int valid = acl_valid(acl);
  errno = 0;
  const int first = acl_get_entry(acl, ACL_FIRST_ENTRY, &entry);
  const int entry_error = errno;
  const int freed = acl_free(acl);
  // Apple returns 0 for an entry and -1/EINVAL for an empty valid ACL.
  if (freed != 0) return NL_RETAINED;
  if (valid != 0 || first != -1 || entry_error != EINVAL) return NL_DENIED;
  out.abi_version = NL_ABI_VERSION; out.kind = kind;
  put64(out.identity.volume, static_cast<uint64_t>(value.st_dev));
  put64(out.identity.file, static_cast<uint64_t>(value.st_ino));
  out.link_count = static_cast<uint64_t>(value.st_nlink);
  out.acl_checked = 1; out.held_object_only = 1;
  return NL_OK;
}
close_result platform_close(handle object) noexcept {
  if (!valid_fd(object.value)) return {false};
  // DO NOT retry EINTR: the number may already be closed and reused.
  return {close(fd(object)) == 0};
}
nl_status platform_child_matches(const child_handle& child,
                                  const nl_fixture_child& input, bool& same) noexcept {
  same = child.pid > 0 && child.pid == input.child_pid;
  return input.platform == NL_PLATFORM_MACOS ? NL_OK : NL_INVALID;
}
nl_status platform_duplicate_child(const nl_fixture_child& input, child_handle& out) noexcept {
  out = {};
  if (input.platform != NL_PLATFORM_MACOS || input.borrowed_process != -1 ||
      input.child_pid <= 0 || input.child_pid > INT_MAX) return NL_INVALID;
  // Only an actual own waitable child is admissible. PID absence is NEVER used
  // as release evidence. Caller has contractually stopped every other reaper.
  int status = 0;
  const auto result = waitpid(static_cast<pid_t>(input.child_pid), &status, WNOHANG);
  if (result < 0 && errno == ECHILD) return NL_DENIED;
  out.pid = input.child_pid; // Responsibility retained even if wait was interrupted.
  if (result < 0) return NL_RETAINED;
  if (result == input.child_pid) {
    if (!WIFEXITED(status) && !WIFSIGNALED(status)) return NL_RETAINED;
    out.pid = 0; out.terminal = true;
  }
  return NL_OK;
}
nl_status platform_duplicate_pipe(intptr_t borrowed, handle& out) noexcept {
  out.value = -1;
  if (!valid_fd(borrowed)) return NL_INVALID;
  const int duplicate = fcntl(static_cast<int>(borrowed), F_DUPFD_CLOEXEC, 0);
  if (duplicate < 0) return error_status(errno);
  out.value = duplicate;
  struct stat value{};
  if (fstat(duplicate, &value) != 0) return error_status(errno);
  return S_ISFIFO(value.st_mode) ? NL_OK : NL_DENIED;
}
nl_status platform_poll_child(child_handle& child, bool& terminal) noexcept {
  terminal = child.terminal;
  if (terminal) return NL_OK;
  if (child.pid <= 0 || child.pid > INT_MAX) return NL_INVALID;
  int status = 0;
  const auto result = waitpid(static_cast<pid_t>(child.pid), &status, WNOHANG);
  if (result < 0) return NL_RETAINED; // ECHILD/external reaper is unknown, NOT released.
  if (result == child.pid) {
    if (!WIFEXITED(status) && !WIFSIGNALED(status)) return NL_RETAINED;
    child.terminal = true; child.pid = 0; terminal = true;
  }
  return NL_OK;
}
close_result platform_close_child(child_handle& child) noexcept {
  return {child.terminal}; // Actual POSIX wait/reap already consumed its OS lifetime.
}
} // namespace i06_location_detail

#elif !defined(_WIN32)
/* Explicit unsupported host branch, never counted as either target platform. */
namespace i06_location_detail {
uint32_t platform_id() noexcept { return 0; }
uint64_t platform_monotonic_ms() noexcept { return UINT64_MAX; }
nl_status platform_duplicate_anchor(const nl_fixture_anchor&, handle&) noexcept { return NL_UNSUPPORTED; }
nl_status platform_open_member(handle, const char*, uint32_t, uint32_t, handle&) noexcept { return NL_UNSUPPORTED; }
nl_status platform_metadata(handle, uint32_t, nl_metadata&) noexcept { return NL_UNSUPPORTED; }
close_result platform_close(handle) noexcept { return {false}; }
nl_status platform_child_matches(const child_handle&, const nl_fixture_child&, bool&) noexcept { return NL_UNSUPPORTED; }
nl_status platform_duplicate_child(const nl_fixture_child&, child_handle&) noexcept { return NL_UNSUPPORTED; }
nl_status platform_duplicate_pipe(intptr_t, handle&) noexcept { return NL_UNSUPPORTED; }
nl_status platform_poll_child(child_handle&, bool&) noexcept { return NL_UNSUPPORTED; }
close_result platform_close_child(child_handle&) noexcept { return {false}; }
}
#endif
