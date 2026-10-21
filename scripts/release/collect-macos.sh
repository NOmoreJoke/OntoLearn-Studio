#!/bin/bash
# Read-only metadata/verification, only on the approved isolated target. Does not launch the app.
set -euo pipefail
if [[ $# -ne 4 || "$1" != '--approved-isolated-session' ]]; then
  echo 'Usage: collect-macos.sh --approved-isolated-session APP_PATH DMG_PATH NEW_OUTPUT_DIR' >&2
  exit 2
fi
if [[ "$(uname -m)" != arm64 || "$(sw_vers -productVersion)" != 15.* ]]; then
  echo 'TARGET_REQUIRED: macOS 15 arm64' >&2
  exit 1
fi
app_path="$2"
dmg_path="$3"
output_dir="$4"
[[ -d "$app_path/Contents" && -f "$dmg_path" && ! -e "$output_dir" ]] || exit 2
mkdir "$output_dir"
sw_vers > "$output_dir/os.txt"
uname -m > "$output_dir/architecture.txt"
# Avoid serial numbers, host names, user names and Keychain enumeration.
sysctl -n machdep.cpu.brand_string hw.memsize > "$output_dir/hardware.txt"
/usr/bin/shasum -a 256 "$dmg_path" > "$output_dir/installer-sha256.txt"
/usr/bin/plutil -extract CFBundleShortVersionString raw "$app_path/Contents/Info.plist" > "$output_dir/version.txt"
/usr/bin/file "$app_path/Contents/MacOS/"* > "$output_dir/app-architecture.txt"
/usr/bin/file "$app_path/Contents/Resources/engine/ontolearn-engine" > "$output_dir/engine-architecture.txt"
/usr/bin/codesign --display --verbose=4 "$app_path" > "$output_dir/signature.txt" 2>&1
/usr/bin/codesign --verify --deep --strict --verbose=4 "$app_path" > "$output_dir/codesign-verify.txt" 2>&1
/usr/sbin/spctl --assess --type execute --verbose=4 "$app_path" > "$output_dir/gatekeeper.txt" 2>&1
# stapler validate is read-only. This script never submits notarization, signs, unlocks, installs or launches.
xcrun stapler validate "$dmg_path" > "$output_dir/stapler.txt" 2>&1
printf '%s\n' 'Metadata collected. Native operation, nested-code inventory and evidence review remain separate.' > "$output_dir/scope.txt"
