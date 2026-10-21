#include "../include/location_abi.h"

#if defined(_WIN32)
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#include <winternl.h>
#include <array>
#include <cstddef>
#include <cstring>

namespace i06_location_detail {
namespace {
constexpr DWORD metadata_access = FILE_READ_ATTRIBUTES | READ_CONTROL | SYNCHRONIZE;
// Exact NT create constants, independently gated by target SDK/build verification.
constexpr ULONG open_existing = 1;
constexpr ULONG directory_option = 0x00000001;
constexpr ULONG nondirectory_option = 0x00000040;
constexpr ULONG synchronous_option = 0x00000020;
constexpr ULONG reparse_option = 0x00200000;
constexpr NTSTATUS pending_status = static_cast<NTSTATUS>(0x00000103L);
struct open_record {
  HANDLE result = nullptr;
  IO_STATUS_BLOCK io{};
  NTSTATUS returned_status = 0; // Preserve pending versus failed-output ambiguity.
};
// Persistent kernel output storage. Unexpected STATUS_PENDING is retained, never
// returned as success and never allowed to write into an expired stack frame.
std::array<open_record, NL_MAX_OWNER_HISTORY * NL_MAX_CAPS> opens{};
uint32_t used_opens = 0; // Only accessed under the core's synchronous gate.
HANDLE native(handle value) noexcept { return reinterpret_cast<HANDLE>(value.value); }
bool valid(intptr_t value) noexcept { return value != -1 && value != 0; }
void put64(uint8_t* out, uint64_t value) noexcept {
  for (unsigned i = 0; i < 8; ++i) { out[i] = static_cast<uint8_t>(value); value >>= 8; }
}
nl_status win_error() noexcept {
  const auto error = GetLastError();
  if (error == ERROR_NOT_ENOUGH_MEMORY || error == ERROR_TOO_MANY_OPEN_FILES) return NL_BUDGET;
  if (error == ERROR_NOT_SUPPORTED || error == ERROR_INVALID_FUNCTION) return NL_UNSUPPORTED;
  return NL_DENIED;
}
nl_status duplicate(HANDLE input, DWORD access, handle& out) noexcept {
  out.value = -1;
  HANDLE result = nullptr;
  if (!DuplicateHandle(GetCurrentProcess(), input, GetCurrentProcess(), &result,
                       access, FALSE, 0)) return win_error();
  out.value = reinterpret_cast<intptr_t>(result);
  return NL_OK;
}
nl_status fixture_acl(HANDLE object) noexcept {
  // All metadata buffers have bounded storage and native alignment. No user-data
  // buffers or unbounded GetSecurityInfo/LocalAlloc result are accepted.
  alignas(std::max_align_t) std::array<unsigned char, 1024> descriptor{};
  alignas(std::max_align_t) std::array<unsigned char, 256> token_data{};
  DWORD needed = 0;
  if (!GetKernelObjectSecurity(object, OWNER_SECURITY_INFORMATION | DACL_SECURITY_INFORMATION,
      descriptor.data(), static_cast<DWORD>(descriptor.size()), &needed)) return win_error();
  if (needed == 0 || needed > descriptor.size() || !IsValidSecurityDescriptor(descriptor.data())) return NL_DENIED;
  const auto in_buffer = [](const void* pointer, size_t bytes, const void* buffer, size_t size) noexcept {
    const auto address = reinterpret_cast<uintptr_t>(pointer);
    const auto begin = reinterpret_cast<uintptr_t>(buffer);
    return bytes <= size && address >= begin && address - begin <= size - bytes;
  };
  PSID owner = nullptr; BOOL owner_defaulted = FALSE;
  PACL acl = nullptr; BOOL present = FALSE; BOOL defaulted = FALSE;
  if (!GetSecurityDescriptorOwner(descriptor.data(), &owner, &owner_defaulted) ||
      !owner || owner_defaulted || !in_buffer(owner, 8, descriptor.data(), needed) ||
      !in_buffer(owner, GetLengthSid(owner), descriptor.data(), needed) || !IsValidSid(owner) ||
      !GetSecurityDescriptorDacl(descriptor.data(), &present, &acl, &defaulted) ||
      !present || !acl || defaulted || !in_buffer(acl, sizeof(ACL), descriptor.data(), needed) ||
      !in_buffer(acl, acl->AclSize, descriptor.data(), needed) || !IsValidAcl(acl) ||
      acl->AceCount == 0 || acl->AceCount > 16) return NL_DENIED;
  DWORD token_needed = 0;
  // N0 does not support thread impersonation. Pseudo-token queries create no
  // owned HANDLE; ERROR_NO_TOKEN is the sole admitted non-impersonating case.
  if (GetTokenInformation(GetCurrentThreadToken(), TokenUser, token_data.data(),
      static_cast<DWORD>(token_data.size()), &token_needed) || GetLastError() != ERROR_NO_TOKEN)
    return NL_DENIED;
  token_needed = 0;
  // Windows pseudo-token: queried but never CloseHandle'd, no new owned HANDLE.
  const BOOL queried = GetTokenInformation(GetCurrentProcessToken(), TokenUser,
      token_data.data(), static_cast<DWORD>(token_data.size()), &token_needed);
  if (!queried || token_needed > token_data.size() || token_needed < sizeof(TOKEN_USER)) return NL_DENIED;
  const auto user = reinterpret_cast<TOKEN_USER*>(token_data.data())->User.Sid;
  if (!in_buffer(user, 8, token_data.data(), token_needed) ||
      !in_buffer(user, GetLengthSid(user), token_data.data(), token_needed) ||
      !IsValidSid(user) || !EqualSid(owner, user)) return NL_DENIED;
  for (DWORD i = 0; i < acl->AceCount; ++i) {
    void* raw = nullptr;
    if (!GetAce(acl, i, &raw)) return NL_DENIED;
    if (!in_buffer(raw, sizeof(ACE_HEADER), acl, acl->AclSize)) return NL_DENIED;
    const auto header = static_cast<ACE_HEADER*>(raw);
    if (!in_buffer(raw, header->AceSize, acl, acl->AclSize)) return NL_DENIED;
    // Fixture-only policy: no inherited/object/callback/deny/other-principal ACE.
    if (header->AceType != ACCESS_ALLOWED_ACE_TYPE || header->AceFlags != 0 ||
        header->AceSize < sizeof(ACCESS_ALLOWED_ACE)) return NL_DENIED;
    const auto ace = static_cast<ACCESS_ALLOWED_ACE*>(raw);
    const auto sid = reinterpret_cast<PSID>(const_cast<DWORD*>(&ace->SidStart));
    constexpr ACCESS_MASK known = FILE_ALL_ACCESS | GENERIC_READ | GENERIC_WRITE | GENERIC_EXECUTE | GENERIC_ALL;
    if ((ace->Mask & ~known) != 0 || !in_buffer(sid, 8, raw, header->AceSize) ||
        GetLengthSid(sid) > header->AceSize - offsetof(ACCESS_ALLOWED_ACE, SidStart) || !IsValidSid(sid) ||
        !EqualSid(sid, user)) return NL_DENIED;
  }
  return NL_OK;
}
} // namespace
uint32_t platform_id() noexcept { return NL_PLATFORM_WINDOWS; }
uint64_t platform_monotonic_ms() noexcept { return GetTickCount64(); }
nl_status platform_duplicate_anchor(const nl_fixture_anchor& value, handle& out) noexcept {
  out.value = -1;
  if (value.platform != NL_PLATFORM_WINDOWS || !valid(value.borrowed_directory)) return NL_INVALID;
  return duplicate(reinterpret_cast<HANDLE>(value.borrowed_directory), metadata_access | FILE_TRAVERSE, out);
}
nl_status platform_open_member(handle parent, const char* name, uint32_t bytes,
                               uint32_t kind, handle& out) noexcept {
  out.value = -1;
  if (!valid(parent.value) || !valid_component(name, bytes)) return NL_INVALID;
  if (used_opens >= opens.size()) return NL_BUDGET;
  wchar_t component[NL_MAX_COMPONENT_BYTES + 1]{};
  const int length = MultiByteToWideChar(CP_UTF8, MB_ERR_INVALID_CHARS, name,
      static_cast<int>(bytes), component, NL_MAX_COMPONENT_BYTES);
  if (length <= 0) return NL_INVALID;
  UNICODE_STRING text{};
  text.Buffer = component;
  text.Length = static_cast<USHORT>(length * sizeof(wchar_t));
  text.MaximumLength = text.Length;
  OBJECT_ATTRIBUTES attributes{};
  attributes.Length = sizeof(attributes); attributes.RootDirectory = native(parent);
  attributes.ObjectName = &text; attributes.Attributes = 0x40; // OBJ_CASE_INSENSITIVE
  auto& attempt = opens[used_opens++]; // Reserved BEFORE native dispatch.
  const ULONG options = synchronous_option | reparse_option |
      (kind == NL_DIRECTORY ? directory_option : nondirectory_option);
  const auto status = NtCreateFile(&attempt.result,
      metadata_access | (kind == NL_DIRECTORY ? FILE_TRAVERSE : 0),
      &attributes, &attempt.io, nullptr, 0, FILE_SHARE_READ | FILE_SHARE_WRITE,
      open_existing, options, nullptr, 0);
  attempt.returned_status = status;
  if (status == pending_status) return NL_RETAINED;
  if (status < 0) {
    // A failure does not authenticate an unexpected output number as our handle.
    // Retain ambiguous output storage instead of closing a possibly reused value.
    return attempt.result != nullptr && attempt.result != INVALID_HANDLE_VALUE ? NL_RETAINED : NL_DENIED;
  }
  if (attempt.result != nullptr && attempt.result != INVALID_HANDLE_VALUE)
    out.value = reinterpret_cast<intptr_t>(attempt.result);
  return out.value == -1 ? NL_INTERNAL : NL_OK;
}
nl_status platform_metadata(handle object, uint32_t kind, nl_metadata& out) noexcept {
  out = {};
  if (!valid(object.value)) return NL_INVALID;
  const auto value = native(object);
  if (GetFileType(value) != FILE_TYPE_DISK) return NL_DENIED;
  FILE_ID_INFO id{}; FILE_STANDARD_INFO standard{}; FILE_ATTRIBUTE_TAG_INFO attributes{};
  if (!GetFileInformationByHandleEx(value, FileIdInfo, &id, sizeof(id)) ||
      !GetFileInformationByHandleEx(value, FileStandardInfo, &standard, sizeof(standard)) ||
      !GetFileInformationByHandleEx(value, FileAttributeTagInfo, &attributes, sizeof(attributes))) return win_error();
  if (attributes.FileAttributes & (FILE_ATTRIBUTE_REPARSE_POINT | FILE_ATTRIBUTE_OFFLINE)) return NL_DENIED;
  if (attributes.ReparseTag != 0 || standard.DeletePending || standard.NumberOfLinks == 0 ||
      (kind == NL_DIRECTORY && !standard.Directory) ||
      (kind == NL_REGULAR_FILE && (standard.Directory || standard.NumberOfLinks != 1))) return NL_DENIED;
  if (kind != NL_DIRECTORY && kind != NL_REGULAR_FILE) return NL_INVALID;
  const auto acl = fixture_acl(value); if (acl != NL_OK) return acl;
  out.abi_version = NL_ABI_VERSION; out.kind = kind;
  put64(out.identity.volume, id.VolumeSerialNumber);
  std::memcpy(out.identity.file, id.FileId.Identifier, sizeof(out.identity.file));
  out.link_count = standard.NumberOfLinks; out.acl_checked = 1; out.held_object_only = 1;
  return NL_OK;
}
close_result platform_close(handle object) noexcept {
  return {valid(object.value) && CloseHandle(native(object)) != FALSE};
}
nl_status platform_child_matches(const child_handle& child,
                                  const nl_fixture_child& input, bool& same) noexcept {
  same = false;
  if (input.platform != NL_PLATFORM_WINDOWS || !valid(input.borrowed_process) ||
      !valid(child.process) || !GetProcessId(reinterpret_cast<HANDLE>(child.process)) ||
      !GetProcessId(reinterpret_cast<HANDLE>(input.borrowed_process))) return NL_DENIED;
  same = CompareObjectHandles(reinterpret_cast<HANDLE>(child.process),
      reinterpret_cast<HANDLE>(input.borrowed_process)) != FALSE;
  return NL_OK;
}
nl_status platform_duplicate_child(const nl_fixture_child& input, child_handle& out) noexcept {
  out = {};
  if (input.platform != NL_PLATFORM_WINDOWS || input.child_pid != 0 ||
      !valid(input.borrowed_process)) return NL_INVALID;
  const auto borrowed = reinterpret_cast<HANDLE>(input.borrowed_process);
  if (!GetProcessId(borrowed) || CompareObjectHandles(borrowed, GetCurrentProcess())) return NL_DENIED;
  handle duplicate_value;
  const auto status = duplicate(borrowed, SYNCHRONIZE | PROCESS_QUERY_LIMITED_INFORMATION, duplicate_value);
  if (duplicate_value.value != -1) out.process = duplicate_value.value;
  return status;
}
nl_status platform_duplicate_pipe(intptr_t borrowed_value, handle& out) noexcept {
  out.value = -1;
  if (!valid(borrowed_value)) return NL_INVALID;
  const auto borrowed = reinterpret_cast<HANDLE>(borrowed_value);
  DWORD flags = 0;
  // FILE_TYPE_PIPE alone includes sockets. Query actual named/anonymous pipe
  // metadata on the borrowed stable source, then duplicate only SYNCHRONIZE.
  if (GetFileType(borrowed) != FILE_TYPE_PIPE ||
      !GetNamedPipeInfo(borrowed, &flags, nullptr, nullptr, nullptr)) return NL_DENIED;
  return duplicate(borrowed, SYNCHRONIZE, out);
}
nl_status platform_poll_child(child_handle& child, bool& terminal) noexcept {
  terminal = child.terminal;
  if (terminal) return NL_OK;
  if (!valid(child.process)) return NL_INVALID;
  const auto status = WaitForSingleObject(reinterpret_cast<HANDLE>(child.process), 0);
  if (status == WAIT_OBJECT_0) { child.terminal = true; terminal = true; return NL_OK; }
  if (status == WAIT_TIMEOUT) return NL_OK;
  return NL_RETAINED;
}
close_result platform_close_child(child_handle& child) noexcept {
  if (!child.terminal) return {false};
  const bool result = valid(child.process) && CloseHandle(reinterpret_cast<HANDLE>(child.process)) != FALSE;
  child.process = -1; // Even error retires this number; caller keeps unknown.
  return {result};
}
} // namespace i06_location_detail
#endif
