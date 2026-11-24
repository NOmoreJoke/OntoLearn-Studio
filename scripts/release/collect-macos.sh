#!/bin/bash
# Read-only metadata/verification, only on the approved isolated target. Does not launch the app.
set -euo pipefail
if [[ $# -ne 4 || "$1" != '--approved-isolated-session' ]]; then
  printf '%s\n' 'Usage: collect-macos.sh --approved-isolated-session APP_PATH DMG_PATH NEW_OUTPUT_DIR' >&2
  exit 2
fi
if [[ "$(/usr/bin/uname -m)" != arm64 || "$(/usr/bin/sw_vers -productVersion)" != 15.* ]]; then
  printf '%s\n' 'TARGET_REQUIRED: macOS 15 arm64' >&2
  exit 1
fi
app_path="$2"
dmg_path="$3"
output_dir="$4"
# Absolute input/output arguments also prevent paths beginning with '-' becoming command options.
[[ "$app_path" = /* ]] || app_path="$PWD/$app_path"
[[ "$dmg_path" = /* ]] || dmg_path="$PWD/$dmg_path"
[[ "$output_dir" = /* ]] || output_dir="$PWD/$output_dir"
[[ -d "$app_path/Contents" && -f "$dmg_path" && ! -e "$output_dir" ]] || exit 2
/bin/mkdir "$output_dir"
step='initializing'
complete=0
write_status() {
  printf '{"schemaVersion":1,"status":"%s","step":"%s","exitCode":%d}\n' "$1" "$step" "$2" > "$output_dir/collector-status.json.tmp"
  /bin/mv -f "$output_dir/collector-status.json.tmp" "$output_dir/collector-status.json"
}
finish() {
  local result="$1"
  trap - EXIT INT TERM
  if [[ "$complete" -ne 1 ]]; then
    [[ "$result" -ne 0 ]] || result=1
    # If storage fails, retain the previous pending/malformed marker and all raw files; neither passes verification.
    set +e
    write_status failed "$result"
    printf '%s\n' 'COLLECTION_FAILED' >&2
  fi
  exit "$result"
}
trap 'finish "$?"' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
write_status pending 0
step='os'; write_status pending 0
/usr/bin/sw_vers > "$output_dir/os.txt" 2>&1
step='architecture'; write_status pending 0
/usr/bin/uname -m > "$output_dir/architecture.txt" 2>&1
# Avoid serial numbers, host names, user names and Keychain enumeration.
step='hardware'; write_status pending 0
/usr/sbin/sysctl -n machdep.cpu.brand_string hw.memsize > "$output_dir/hardware.txt" 2>&1
step='installer-hash'; write_status pending 0
/usr/bin/shasum -a 256 "$dmg_path" > "$output_dir/installer-sha256.txt" 2>&1
step='version'; write_status pending 0
/usr/bin/plutil -extract CFBundleShortVersionString raw "$app_path/Contents/Info.plist" > "$output_dir/version.txt" 2>&1
step='app-architecture'; write_status pending 0
/usr/bin/file "$app_path/Contents/MacOS/"* > "$output_dir/app-architecture.txt" 2>&1
step='engine-architecture'; write_status pending 0
/usr/bin/file "$app_path/Contents/Resources/engine/ontolearn-engine" > "$output_dir/engine-architecture.txt" 2>&1
step='signature'; write_status pending 0
/usr/bin/codesign --display --verbose=4 "$app_path" > "$output_dir/signature.txt" 2>&1
step='codesign-verify'; write_status pending 0
/usr/bin/codesign --verify --deep --strict --verbose=4 "$app_path" > "$output_dir/codesign-verify.txt" 2>&1
step='gatekeeper'; write_status pending 0
/usr/sbin/spctl --assess --type execute --verbose=4 "$app_path" > "$output_dir/gatekeeper.txt" 2>&1
# stapler validate is read-only. Never submits notarization, signs, unlocks, installs or launches.
step='stapler'; write_status pending 0
/usr/bin/xcrun stapler validate "$dmg_path" > "$output_dir/stapler.txt" 2>&1
step='scope'; write_status pending 0
printf '%s\n' 'Metadata collected. Completion marker is not signature, native-operation or same-package provenance proof; independent evidence review remains required.' > "$output_dir/scope.txt"
step='complete'
write_status complete 0
complete=1
