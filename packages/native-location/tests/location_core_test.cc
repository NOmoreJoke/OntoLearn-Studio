#include "../include/location_abi.h"
#include <array>
#include <atomic>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cerrno>
#include <initializer_list>
#include <string>
#include <thread>
#include <chrono>
#include <stdexcept>

#if defined(NL_NODE_FIXTURE_HOST)
#ifndef NL_WITH_NODE
#error "NL_NODE_FIXTURE_HOST requires NL_WITH_NODE"
#endif
#include <node_api.h>
#endif
#if defined(__APPLE__)
#include <fcntl.h>
#include <spawn.h>
#include <signal.h>
#include <sys/acl.h>
#include <sys/stat.h>
#include <sys/stdio.h>
#include <sys/wait.h>
#include <unistd.h>
extern char** environ;
#elif defined(_WIN32)
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#include <cstddef>
#include <cwchar>
#endif

namespace {
void require(bool condition, const char* label) {
  if (!condition) throw std::runtime_error(label); // Fixed labels only, no paths.
}
[[maybe_unused]] bool identity_equal(const nl_identity& a, const nl_identity& b) {
  return std::memcmp(&a, &b, sizeof(a)) == 0;
}
// Test CLI spelling only, not file identity or permission evidence. Accept rooted
// drive paths and ordinary UNC paths with server/share/artifact components.
// Device namespaces, drive-relative/root-relative paths and ambiguous components
// are outside this fixture contract. Pure input cases below need no OS dispatch.
constexpr bool windows_probe_artifact_path(const wchar_t* path) noexcept {
  if (!path) return false;
  size_t length = 0;
  while (length < 1024 && path[length] != L'\0') ++length;
  if (length < 4 || length == 1024) return false;
  const auto separator = [](wchar_t c) constexpr { return c == L'\\' || c == L'/'; };
  const bool drive = ((path[0] >= L'A' && path[0] <= L'Z') ||
      (path[0] >= L'a' && path[0] <= L'z')) && path[1] == L':' && separator(path[2]);
  const bool unc = path[0] == L'\\' && path[1] == L'\\';
  if (!drive && !unc) return false;
  size_t start = drive ? 3 : 2;
  unsigned components = 0;
  for (size_t i = start; i <= length; ++i) {
    if (i < length && !separator(path[i])) {
      const auto c = path[i];
      if (c < L' ' || c == 0x7f || c == L':' || c == L'"' ||
          c == L'<' || c == L'>' || c == L'|' || c == L'*' || c == L'?') return false;
      continue;
    }
    // UNC uses its ordinary backslash spelling; no device/extended prefixes.
    if (unc && i < length && path[i] != L'\\') return false;
    const auto count = i - start;
    if (count == 0 || path[i - 1] == L'.' || path[i - 1] == L' ') return false;
    // Conservative ordinary-component policy also applies to UNC server/share.
    // DOS device basenames stay reserved with extensions and in directories.
    size_t base_length = 0;
    while (base_length < count && path[start + base_length] != L'.') ++base_length;
    wchar_t base[4]{};
    for (size_t j = 0; j < base_length && j < 4; ++j) {
      const auto c = path[start + j];
      base[j] = c >= L'a' && c <= L'z' ? static_cast<wchar_t>(c - L'a' + L'A') : c;
    }
    if (base_length == 3 && ((base[0] == L'C' && base[1] == L'O' && base[2] == L'N') ||
        (base[0] == L'P' && base[1] == L'R' && base[2] == L'N') ||
        (base[0] == L'A' && base[1] == L'U' && base[2] == L'X') ||
        (base[0] == L'N' && base[1] == L'U' && base[2] == L'L'))) return false;
    const bool port = (base[0] == L'C' && base[1] == L'O' && base[2] == L'M') ||
        (base[0] == L'L' && base[1] == L'P' && base[2] == L'T');
    if (base_length == 4 && port && ((base[3] >= L'1' && base[3] <= L'9') ||
        base[3] == L'\u00b9' || base[3] == L'\u00b2' || base[3] == L'\u00b3')) return false;
    ++components;
    start = i + 1;
  }
  return components >= (drive ? 1u : 3u);
}
static_assert(windows_probe_artifact_path(L"C:\\artifacts\\probe.exe"), "drive-rooted artifact");
static_assert(windows_probe_artifact_path(L"c:/artifacts/probe.exe"), "CMake drive-rooted spelling");
static_assert(windows_probe_artifact_path(L"\\\\server\\share\\probe.exe"), "ordinary UNC artifact");
static_assert(!windows_probe_artifact_path(L"C:probe.exe"), "reject drive-relative artifact");
static_assert(!windows_probe_artifact_path(L"C:"), "reject drive current directory");
static_assert(!windows_probe_artifact_path(L"1:\\probe.exe"), "reject non-letter drive");
static_assert(!windows_probe_artifact_path(L"\\probe.exe"), "reject rooted current-drive artifact");
static_assert(!windows_probe_artifact_path(L"probe.exe"), "reject relative artifact");
static_assert(!windows_probe_artifact_path(L"\\\\server\\share"), "reject UNC without artifact");
static_assert(!windows_probe_artifact_path(L"\\\\server\\\\probe.exe"), "reject empty UNC share");
static_assert(!windows_probe_artifact_path(L"\\\\?\\C:\\probe.exe"), "reject extended device namespace");
static_assert(!windows_probe_artifact_path(L"\\\\.\\pipe\\probe.exe"), "reject device namespace");
static_assert(!windows_probe_artifact_path(L"C:\\artifacts\\..\\probe.exe"), "reject parent segment");
static_assert(!windows_probe_artifact_path(L"C:\\artifacts\\probe.exe:stream"), "reject alternate stream");
static_assert(!windows_probe_artifact_path(L"C:\\artifacts\\probe.exe."), "reject trailing dot");
static_assert(windows_probe_artifact_path(L"C:\\artifacts\\COM10.exe"), "ordinary non-reserved port-like name");
static_assert(windows_probe_artifact_path(L"C:\\artifacts\\NUL-data.exe"), "ordinary non-reserved prefix");
static_assert(!windows_probe_artifact_path(L"C:\\NUL.exe"), "reject device basename with extension");
static_assert(!windows_probe_artifact_path(L"C:\\Con\\probe.exe"), "reject device directory case-insensitively");
static_assert(!windows_probe_artifact_path(L"C:\\prn.tar.exe"), "reject device basename with multiple extensions");
static_assert(!windows_probe_artifact_path(L"C:\\aux.exe"), "reject auxiliary device basename");
static_assert(!windows_probe_artifact_path(L"C:\\com1.exe"), "reject serial device basename");
static_assert(!windows_probe_artifact_path(L"C:\\LPT9.exe"), "reject parallel device basename");
static_assert(!windows_probe_artifact_path(L"C:\\COM\u00b9.exe"), "reject superscript-one device basename");
static_assert(!windows_probe_artifact_path(L"C:\\LPT\u00b2.exe"), "reject superscript-two device basename");
static_assert(!windows_probe_artifact_path(L"C:\\COM\u00b3.exe"), "reject superscript-three device basename");
static_assert(!windows_probe_artifact_path(L"\\\\server\\share\\NUL.exe"), "reject UNC device artifact basename");
static_assert(!windows_probe_artifact_path(L"\\\\CON\\share\\probe.exe"), "conservative UNC server component policy");
#if defined(__APPLE__)
struct fixture {
  nl_owner_ref node_owner{}; // Test-addon fallback retains the exact native owner.
  std::string path;
  int anchor = -1;
  bool cleaned = false;
  bool cleanup_ok = true;
  fixture() {
    try {
    char pattern[] = "/tmp/i06-n0-XXXXXX";
    const auto created = mkdtemp(pattern); require(created != nullptr, "fixture-create");
    path = created;
    anchor = open(path.c_str(), O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC);
    require(anchor >= 0, "fixture-anchor");
    acl_t acl = acl_init(0); require(acl != nullptr, "fixture-acl-allocate");
    const auto applied = acl_set_fd_np(anchor, acl, ACL_TYPE_EXTENDED);
    const auto freed = acl_free(acl); require(applied == 0 && freed == 0, "fixture-acl");
    require(mkdirat(anchor, "sub", 0700) == 0, "fixture-sub");
    empty("member");
    } catch (...) { cleanup(); throw; }
  }
  void empty(const char* name) {
    const int value = openat(anchor, name, O_CREAT | O_EXCL | O_WRONLY | O_CLOEXEC, 0600);
    require(value >= 0, "fixture-empty"); require(close(value) == 0, "fixture-empty-close");
  }
  nl_fixture_anchor input() const { return {NL_ABI_VERSION, NL_PLATFORM_MACOS, anchor, {0, 0, 0, 0}}; }
  void replace_member() {
    require(renameat(anchor, "member", anchor, "old") == 0, "fixture-replace-rename"); empty("member");
  }
  void alias_member() { require(linkat(anchor, "member", anchor, "alias", 0) == 0, "fixture-hardlink"); }
  void symlink_member() { require(symlinkat("member", anchor, "link") == 0, "fixture-symlink"); }
  void rename_root() {
    const auto moved = path + "-moved";
    require(renamex_np(path.c_str(), moved.c_str(), RENAME_EXCL) == 0, "fixture-root-rename"); path = moved;
  }
  bool cleanup() noexcept {
    if (cleaned) return cleanup_ok;
    cleaned = true;
    if (anchor >= 0) {
      for (const auto name : {"member", "old", "alias", "link"})
        if (unlinkat(anchor, name, 0) != 0 && errno != ENOENT) cleanup_ok = false;
      if (unlinkat(anchor, "sub", AT_REMOVEDIR) != 0 && errno != ENOENT) cleanup_ok = false;
      if (close(anchor) != 0) cleanup_ok = false;
      anchor = -1;
    }
    if (!path.empty() && rmdir(path.c_str()) != 0 && errno != ENOENT) cleanup_ok = false;
    return cleanup_ok;
  }
  ~fixture() { cleanup(); }
};
struct probe {
  pid_t pid = -1;
  int input = -1;
  int read_side = -1;
  bool native_wait = false;
  bool cleaned = false;
  bool cleanup_ok = true;
  posix_spawn_file_actions_t actions{};
  bool actions_live = false;
  explicit probe(const char* executable) {
    try {
      require(executable && executable[0] == '/', "probe-absolute");
      int pipes[2] = {-1, -1}; require(pipe(pipes) == 0, "probe-pipe");
      read_side = pipes[0]; input = pipes[1];
      require(fcntl(read_side, F_SETFD, FD_CLOEXEC) == 0 && fcntl(input, F_SETFD, FD_CLOEXEC) == 0, "probe-cloexec");
      require(posix_spawn_file_actions_init(&actions) == 0, "probe-actions"); actions_live = true;
      require(posix_spawn_file_actions_adddup2(&actions, read_side, STDIN_FILENO) == 0 &&
        posix_spawn_file_actions_addclose(&actions, read_side) == 0 &&
        posix_spawn_file_actions_addclose(&actions, input) == 0, "probe-actions-config");
      char option[] = "--hold-until-eof";
      char* argv[] = {const_cast<char*>(executable), option, nullptr};
      pid_t created = -1;
      const auto started = posix_spawn(&created, executable, &actions, nullptr, argv, environ);
      if (started == 0) pid = created;
      const auto destroyed = posix_spawn_file_actions_destroy(&actions); actions_live = false;
      const auto read_closed = close(read_side); read_side = -1;
      require(started == 0 && destroyed == 0 && read_closed == 0, "probe-spawn");
    } catch (...) { cleanup(); throw; }
  }
  nl_fixture_child input_record() const {
    return {NL_ABI_VERSION, NL_PLATFORM_MACOS, -1, pid, {input, -1}, {0, 0, 0, 0}};
  }
  void end_input() {
    if (input >= 0) { const auto closed = close(input); input = -1; require(closed == 0, "probe-input-close"); }
  }
  bool cleanup() noexcept {
    if (cleaned) return cleanup_ok;
    cleaned = true;
    if (actions_live) { if (posix_spawn_file_actions_destroy(&actions) != 0) cleanup_ok = false; actions_live = false; }
    for (int* value : {&input, &read_side}) {
      if (*value >= 0) { if (close(*value) != 0) cleanup_ok = false; *value = -1; }
    }
    if (pid > 0 && !native_wait) {
      // Still-unreaped own fixture only. Never kill/reap a transferred PID.
      kill(pid, SIGKILL); int status = 0;
      if (waitpid(pid, &status, 0) != pid || (!WIFEXITED(status) && !WIFSIGNALED(status))) cleanup_ok = false;
    }
    return cleanup_ok;
  }
  ~probe() { cleanup(); }
};
#elif defined(_WIN32)
struct fixture {
  nl_owner_ref node_owner{}; // Test-addon fallback retains the exact native owner.
  std::wstring path;
  HANDLE anchor = INVALID_HANDLE_VALUE;
  alignas(std::max_align_t) std::array<unsigned char, 256> user{};
  alignas(std::max_align_t) std::array<unsigned char, 256> acl_bytes{};
  SECURITY_DESCRIPTOR descriptor{};
  SECURITY_ATTRIBUTES attributes{};
  bool cleaned = false;
  bool cleanup_ok = true;
  fixture() {
    try {
    DWORD needed = 0;
    require(GetTokenInformation(GetCurrentProcessToken(), TokenUser, user.data(),
      static_cast<DWORD>(user.size()), &needed) && needed <= user.size(), "fixture-token");
    const auto sid = reinterpret_cast<TOKEN_USER*>(user.data())->User.Sid;
    const auto acl = reinterpret_cast<PACL>(acl_bytes.data());
    require(InitializeAcl(acl, static_cast<DWORD>(acl_bytes.size()), ACL_REVISION) &&
      AddAccessAllowedAce(acl, ACL_REVISION, FILE_ALL_ACCESS, sid) &&
      InitializeSecurityDescriptor(&descriptor, SECURITY_DESCRIPTOR_REVISION) &&
      SetSecurityDescriptorOwner(&descriptor, sid, FALSE) &&
      SetSecurityDescriptorDacl(&descriptor, TRUE, acl, FALSE) &&
      SetSecurityDescriptorControl(&descriptor, SE_DACL_PROTECTED, SE_DACL_PROTECTED), "fixture-security");
    attributes = {sizeof(attributes), &descriptor, FALSE};
    wchar_t temp[MAX_PATH + 1]{};
    const auto length = GetTempPathW(MAX_PATH, temp); require(length && length < MAX_PATH - 64, "fixture-temp");
    for (unsigned attempt = 0; attempt < 32; ++attempt) {
      wchar_t candidate[MAX_PATH + 1]{};
      require(std::swprintf(candidate, MAX_PATH, L"%lsi06-n0-%lu-%llu-%u", temp,
        GetCurrentProcessId(), static_cast<unsigned long long>(GetTickCount64()), attempt) > 0, "fixture-name");
      if (CreateDirectoryW(candidate, &attributes)) { path = candidate; break; }
      require(GetLastError() == ERROR_ALREADY_EXISTS, "fixture-create");
    }
    require(!path.empty(), "fixture-exclusive");
    anchor = CreateFileW(path.c_str(), FILE_READ_ATTRIBUTES | READ_CONTROL | FILE_TRAVERSE | SYNCHRONIZE,
      FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE, nullptr, OPEN_EXISTING,
      FILE_FLAG_BACKUP_SEMANTICS | FILE_FLAG_OPEN_REPARSE_POINT, nullptr);
    require(anchor != INVALID_HANDLE_VALUE, "fixture-anchor");
    require(CreateDirectoryW((path + L"\\sub").c_str(), &attributes), "fixture-sub"); empty(L"member");
    } catch (...) { cleanup(); throw; }
  }
  void empty(const wchar_t* name) {
    const auto file = CreateFileW((path + L"\\" + name).c_str(), GENERIC_WRITE,
      FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE, &attributes, CREATE_NEW, 0, nullptr);
    require(file != INVALID_HANDLE_VALUE, "fixture-empty"); require(CloseHandle(file), "fixture-empty-close");
  }
  nl_fixture_anchor input() const { return {NL_ABI_VERSION, NL_PLATFORM_WINDOWS, reinterpret_cast<intptr_t>(anchor), {0,0,0,0}}; }
  void replace_member() {
    require(MoveFileExW((path + L"\\member").c_str(), (path + L"\\old").c_str(), 0), "fixture-replace-rename"); empty(L"member");
  }
  void alias_member() { require(CreateHardLinkW((path + L"\\alias").c_str(), (path + L"\\member").c_str(), nullptr), "fixture-hardlink"); }
  void symlink_member() {
    require(CreateSymbolicLinkW((path + L"\\link").c_str(), L"member", SYMBOLIC_LINK_FLAG_ALLOW_UNPRIVILEGED_CREATE), "fixture-reparse-unavailable");
  }
  void rename_root() {
    const auto moved = path + L"-moved";
    if (MoveFileExW(path.c_str(), moved.c_str(), 0)) path = moved;
    else require(GetLastError() == ERROR_SHARING_VIOLATION || GetLastError() == ERROR_ACCESS_DENIED, "fixture-root-rename");
  }
  bool cleanup() noexcept {
    if (cleaned) return cleanup_ok;
    cleaned = true;
    if (anchor != INVALID_HANDLE_VALUE) {
      if (!CloseHandle(anchor)) cleanup_ok = false;
      anchor = INVALID_HANDLE_VALUE;
    }
    if (path.empty()) return cleanup_ok;
    for (const auto name : {L"member", L"old", L"alias", L"link"})
      if (!DeleteFileW((path + L"\\" + name).c_str()) && GetLastError() != ERROR_FILE_NOT_FOUND)
        cleanup_ok = false;
    if (!RemoveDirectoryW((path + L"\\sub").c_str()) && GetLastError() != ERROR_PATH_NOT_FOUND &&
        GetLastError() != ERROR_FILE_NOT_FOUND) cleanup_ok = false;
    if (!RemoveDirectoryW(path.c_str()) && GetLastError() != ERROR_PATH_NOT_FOUND &&
        GetLastError() != ERROR_FILE_NOT_FOUND) cleanup_ok = false;
    return cleanup_ok;
  }
  ~fixture() { cleanup(); }
};
struct probe {
  HANDLE process = nullptr;
  HANDLE input = nullptr;
  HANDLE output = nullptr;
  HANDLE read_input = nullptr;
  HANDLE write_output = nullptr;
  HANDLE thread = nullptr;
  alignas(std::max_align_t) std::array<unsigned char, 1024> attribute_bytes{};
  LPPROC_THREAD_ATTRIBUTE_LIST list = nullptr;
  bool list_live = false;
  bool native_wait = false;
  bool cleaned = false;
  bool cleanup_ok = true;
  explicit probe(const char* executable) {
    try {
    wchar_t target[1024]{};
    require(MultiByteToWideChar(CP_UTF8, MB_ERR_INVALID_CHARS, executable, -1, target, 1024) > 0 &&
      windows_probe_artifact_path(target), "probe-absolute");
    SECURITY_ATTRIBUTES security{sizeof(security), nullptr, TRUE};
    require(CreatePipe(&read_input, &input, &security, 0) &&
      CreatePipe(&output, &write_output, &security, 0), "probe-pipes");
    require(SetHandleInformation(input, HANDLE_FLAG_INHERIT, 0) &&
      SetHandleInformation(output, HANDLE_FLAG_INHERIT, 0), "probe-private-ends");
    SIZE_T needed = 0; InitializeProcThreadAttributeList(nullptr, 1, 0, &needed);
    require(needed && needed <= attribute_bytes.size(), "probe-attribute-size");
    list = reinterpret_cast<LPPROC_THREAD_ATTRIBUTE_LIST>(attribute_bytes.data());
    require(InitializeProcThreadAttributeList(list, 1, 0, &needed), "probe-attributes"); list_live = true;
    HANDLE inherited[] = {read_input, write_output};
    require(UpdateProcThreadAttribute(list, 0, PROC_THREAD_ATTRIBUTE_HANDLE_LIST,
      inherited, sizeof(inherited), nullptr, nullptr), "probe-handle-list");
    STARTUPINFOEXW startup{}; startup.StartupInfo.cb = sizeof(startup);
    startup.StartupInfo.dwFlags = STARTF_USESTDHANDLES;
    startup.StartupInfo.hStdInput = read_input;
    startup.StartupInfo.hStdOutput = write_output; startup.StartupInfo.hStdError = write_output;
    startup.lpAttributeList = list;
    wchar_t command[1152]{};
    require(std::swprintf(command, 1152, L"\"%ls\" --hold-until-eof", target) > 0, "probe-command");
    PROCESS_INFORMATION created{};
    const auto started = CreateProcessW(target, command, nullptr, nullptr, TRUE,
      EXTENDED_STARTUPINFO_PRESENT | CREATE_NO_WINDOW, nullptr, nullptr, &startup.StartupInfo, &created);
    if (started) { process = created.hProcess; thread = created.hThread; }
    DeleteProcThreadAttributeList(list); list_live = false;
    const auto closed_read = CloseHandle(read_input); read_input = nullptr;
    const auto closed_write = CloseHandle(write_output); write_output = nullptr;
    const auto closed_thread = !thread || CloseHandle(thread); thread = nullptr;
    require(started && closed_read && closed_write && closed_thread, "probe-spawn");
    } catch (...) { cleanup(); throw; }
  }
  nl_fixture_child input_record() const {
    // Only the read-capable output end is adopted; the fixture harness retains
    // stdin's write end to hold the child pending until explicit end_input.
    return {NL_ABI_VERSION, NL_PLATFORM_WINDOWS, reinterpret_cast<intptr_t>(process), 0,
      {reinterpret_cast<intptr_t>(output), -1}, {0,0,0,0}};
  }
  void end_input() { if (input) { const auto closed = CloseHandle(input); input = nullptr; require(closed, "probe-input-close"); } }
  bool cleanup() noexcept {
    if (cleaned) return cleanup_ok;
    cleaned = true;
    if (list_live) { DeleteProcThreadAttributeList(list); list_live = false; }
    for (HANDLE* value : {&input, &output, &read_input, &write_output, &thread}) {
      if (*value) { if (!CloseHandle(*value)) cleanup_ok = false; *value = nullptr; }
    }
    if (process) {
      if (!native_wait && WaitForSingleObject(process, 2000) != WAIT_OBJECT_0) {
        if (!TerminateProcess(process, 1) || WaitForSingleObject(process, 2000) != WAIT_OBJECT_0)
          cleanup_ok = false;
      }
      if (!CloseHandle(process)) cleanup_ok = false; process = nullptr;
    }
    return cleanup_ok;
  }
  ~probe() { cleanup(); }
};
#endif

#if defined(__APPLE__) || defined(_WIN32)
nl_owner_ref make_owner(fixture& tree) {
  const auto anchor = tree.input(); nl_owner_ref owner{};
  const auto status = nl_fixture_owner_create(&anchor, &owner);
  if (status != NL_OK && owner.value && nl_owner_close(owner) != NL_OK) {
    std::fputs("N0 failed adoption cleanup retained\n", stderr); std::abort();
  }
  require(status == NL_OK && owner.value != 0, "owner-create"); return owner;
}
[[maybe_unused]] void metadata_cases(fixture& tree) {
  const auto owner = make_owner(tree);
  nl_cap_ref root{}, old{}; nl_metadata root_metadata{}, old_metadata{};
  require(nl_owner_root(owner, &root, &root_metadata) == NL_OK, "root");
  require(nl_owner_acquire(owner, 1, root, "member", 6, NL_REGULAR_FILE, nullptr, &old, &old_metadata) == NL_OK, "member");
  require(old_metadata.held_object_only == 1 && old_metadata.acl_checked == 1, "metadata-boundary");
  nl_cap_ref rejected{}; nl_metadata unused{}; nl_snapshot before{}, after{};
  require(nl_owner_snapshot(owner, &before) == NL_OK, "snapshot-before");
  require(nl_owner_acquire(owner, 1, root, "a/b", 3, NL_DIRECTORY, nullptr, &rejected, &unused) == NL_INVALID, "component-reject");
  require(nl_owner_snapshot(owner, &after) == NL_OK && before.ever_caps == after.ever_caps, "reject-before-dispatch");
  auto forged = old; forged.owner += 1;
  require(nl_owner_observe(owner, forged, &unused) == NL_DENIED, "cross-owner");
  // Windows may deny a rename while its member handle denies share-delete.
#if defined(_WIN32)
  require(nl_owner_release(owner, old) == NL_OK, "release-before-replace");
#endif
  tree.replace_member();
  require(nl_owner_acquire(owner, 1, root, "member", 6, NL_REGULAR_FILE, &old_metadata.identity, &rejected, &unused) == NL_DENIED, "same-location-new-identity");
  nl_cap_ref current{}; nl_metadata current_metadata{};
  require(nl_owner_acquire(owner, 1, root, "member", 6, NL_REGULAR_FILE, nullptr, &current, &current_metadata) == NL_OK &&
    !identity_equal(current_metadata.identity, old_metadata.identity), "new-observation");
#if defined(_WIN32)
  require(nl_owner_release(owner, current) == NL_OK, "release-before-hardlink");
#endif
  tree.alias_member();
  require(nl_owner_acquire(owner, 1, root, "member", 6, NL_REGULAR_FILE,
    &current_metadata.identity, &rejected, &unused) == NL_DENIED, "new-hardlink-reject");
  tree.symlink_member();
  require(nl_owner_acquire(owner, 1, root, "link", 4, NL_REGULAR_FILE, nullptr, &rejected, &unused) == NL_DENIED, "link-reject");
  tree.rename_root();
  require(nl_owner_publish(owner) == NL_UNSUPPORTED, "publish-has-no-source-fence");
  require(nl_owner_revoke(owner) == NL_OK && nl_owner_root(owner, &rejected, &unused) == NL_STALE, "revoke-terminal");
  require(nl_owner_close(owner) == NL_OK, "metadata-close");
  require(nl_owner_snapshot(owner, &after) == NL_OK && after.closed == 1 && after.held_objects == 0 &&
    after.pending_children == 0 && after.production_admission == 0, "metadata-final");
}
[[maybe_unused]] void child_cases(fixture& tree, const char* executable) {
  const auto owner = make_owner(tree); probe child(executable);
  auto input = child.input_record(); nl_child_receipt receipt{};
  const auto status = nl_fixture_child_adopt(owner, &input, &receipt);
  child.native_wait = receipt.wait_owned != 0;
  require(status == NL_OK && child.native_wait, "child-adopt");
  nl_child_receipt second{}; input.borrowed_pipes[0] = -1; input.borrowed_pipes[1] = -1;
  require(nl_fixture_child_adopt(owner, &input, &second) == NL_DENIED && second.wait_owned == 0, "duplicate-reaper-reject");
  require(nl_owner_poll_children(owner) == NL_RETAINED, "live-child-not-drained");
  nl_snapshot live{};
  require(nl_owner_snapshot(owner, &live) == NL_OK && live.pending_children == 1 && live.held_pipes >= 1, "child-held");
  child.end_input();
  nl_status closed = NL_RETAINED;
  for (unsigned i = 0; i < 1000 && closed != NL_OK; ++i) {
    closed = nl_owner_close(owner);
    require(closed == NL_OK || closed == NL_RETAINED || closed == NL_BUSY, "child-close-status");
    if (closed != NL_OK) std::this_thread::sleep_for(std::chrono::milliseconds(2));
  }
  require(closed == NL_OK, "actual-child-close-timeout");
  require(nl_owner_snapshot(owner, &live) == NL_OK && live.closed == 1 &&
    live.pending_children == 0 && live.held_pipes == 0 && live.unknown_objects == 0, "child-final");
  require(child.cleanup(), "child-fixture-cleanup");
}
[[maybe_unused]] void partial_child_case(fixture& tree, const char* executable) {
  const auto owner = make_owner(tree); probe child(executable);
  auto input = child.input_record();
  input.borrowed_pipes[0] = tree.input().borrowed_directory; // Real non-pipe negative.
  input.borrowed_pipes[1] = -1;
  nl_child_receipt receipt{};
  const auto status = nl_fixture_child_adopt(owner, &input, &receipt);
  child.native_wait = receipt.wait_owned != 0;
  require(status == NL_DENIED && child.native_wait, "partial-child-has-reaper");
  nl_snapshot snapshot{};
  require(nl_owner_snapshot(owner, &snapshot) == NL_OK && snapshot.pending_children == 1,
    "partial-child-not-forgotten");
  child.end_input();
  nl_status closed = NL_RETAINED;
  for (unsigned i = 0; i < 1000 && closed != NL_OK; ++i) {
    closed = nl_owner_close(owner);
    require(closed == NL_OK || closed == NL_RETAINED || closed == NL_BUSY, "partial-close-status");
    if (closed != NL_OK) std::this_thread::sleep_for(std::chrono::milliseconds(2));
  }
  require(closed == NL_OK, "partial-child-actual-close");
  require(child.cleanup(), "partial-child-fixture-cleanup");
}
[[maybe_unused]] void revoke_and_budget_cases(fixture& tree) {
  const auto owner = make_owner(tree); nl_cap_ref root{}; nl_metadata metadata{};
  require(nl_owner_root(owner, &root, &metadata) == NL_OK, "concurrency-root");
  std::atomic<bool> start{false}, failure{false};
  std::thread observer([&] {
    while (!start.load()) std::this_thread::yield();
    for (unsigned i = 0; i < 16; ++i) {
      nl_cap_ref next{}; nl_metadata facts{};
      const auto status = nl_owner_acquire(owner, 1, root, "sub", 3, NL_DIRECTORY, nullptr, &next, &facts);
      if (status == NL_STALE) break;
      if (status != NL_OK || next.owner != owner.value || nl_owner_release(owner, next) != NL_OK) {
        failure.store(true); break;
      }
    }
  });
  start.store(true); const auto revoked = nl_owner_revoke(owner); observer.join();
  require(revoked == NL_OK && !failure.load(), "concurrent-revoke");
  require(nl_owner_close(owner) == NL_OK, "concurrent-close");
  // This is real concurrent characterization, not a deterministic proof that an
  // OS call was blocked during revoke; later target trace must identify coverage.
  const auto limited = make_owner(tree);
  require(nl_owner_root(limited, &root, &metadata) == NL_OK, "budget-root");
  for (unsigned i = 1; i < NL_MAX_CAPS; ++i) {
    nl_cap_ref next{};
    require(nl_owner_acquire(limited, 1, root, "sub", 3, NL_DIRECTORY, nullptr, &next, &metadata) == NL_OK,
      "cap-lifetime-reserve");
    require(nl_owner_release(limited, next) == NL_OK, "cap-lifetime-release");
  }
  nl_cap_ref denied{};
  require(nl_owner_acquire(limited, 1, root, "sub", 3, NL_DIRECTORY, nullptr, &denied, &metadata) == NL_BUDGET,
    "released-slot-not-recycled");
  require(nl_owner_close(limited) == NL_OK, "budget-close");
}

#endif
} // namespace

#if defined(NL_NODE_FIXTURE_HOST) && (defined(__APPLE__) || defined(_WIN32))
namespace i06_location_detail {
namespace {
void cleanup_fixture(void* data) noexcept {
  auto* tree = static_cast<fixture*>(data);
  // The bind may have failed before registering its own owner hook. Always keep
  // this exact fallback owner through teardown; repeated confirmed close is safe.
  const auto owner_closed = !tree->node_owner.value ||
      nl_owner_close(tree->node_owner) == NL_OK;
  if (!owner_closed) { std::fputs("N0 test owner cleanup retained\n", stderr); std::abort(); }
  const auto cleaned = tree->cleanup(); delete tree;
  if (!cleaned) { std::fputs("N0 test fixture cleanup unknown\n", stderr); std::abort(); }
}
}
// Test-only .node: this TU and the addon/core/platform MUST share ONE registry.
// No extra host source or JS path/fd/PID constructor is introduced.
nl_status fixture_node_bootstrap(napi_env env, napi_value exports) noexcept {
  fixture* tree = nullptr;
  nl_owner_ref owner{};
  try {
    tree = new fixture(); // Exactly one bounded test fixture per test-addon load.
    owner = make_owner(*tree);
    tree->node_owner = owner;
    // LIFO hooks: register harness cleanup first, so bound owner cleanup is first.
    if (napi_add_env_cleanup_hook(env, cleanup_fixture, tree) != napi_ok) {
      if (nl_owner_close(owner) != NL_OK || !tree->cleanup()) {
        std::fputs("N0 test hook-registration cleanup retained\n", stderr); std::abort();
      }
      delete tree; return NL_INTERNAL;
    }
    return nl_node_bind_fixture(env, exports, owner);
  } catch (...) {
    if (owner.value) nl_owner_close(owner);
    delete tree; return NL_INTERNAL;
  }
}
} // namespace i06_location_detail
#elif defined(NL_NODE_FIXTURE_HOST)
namespace i06_location_detail {
nl_status fixture_node_bootstrap(napi_env, napi_value) noexcept { return NL_UNSUPPORTED; }
}
#elif !defined(NL_NODE_FIXTURE_HOST)
int main(int argc, char** argv) {
  if (argc != 2) return 64;
#if defined(__APPLE__) || defined(_WIN32)
  try {
    fixture tree; metadata_cases(tree); child_cases(tree, argv[1]);
    partial_child_case(tree, argv[1]); revoke_and_budget_cases(tree);
    require(tree.cleanup(), "fixture-final-cleanup");
    std::puts("N0 controlled fixture cases completed; production admission remains unsupported"); return 0;
  } catch (const std::exception& error) {
    std::fprintf(stderr, "N0 fixture failure: %s\n", error.what()); return 1;
  } catch (...) { std::fputs("N0 fixture failure: internal\n", stderr); return 1; }
#else
  (void)argv; return 77; // Unsupported host, NEVER a target-platform pass.
#endif
}
#endif
