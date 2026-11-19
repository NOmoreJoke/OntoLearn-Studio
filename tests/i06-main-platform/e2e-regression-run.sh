#!/bin/bash
# Existing approved repository tests, unchanged. This is regression evidence only;
# Playwright's Electron loader/basic/mock/native stubs are not safeStorage/native proof.
set -euo pipefail
unset ELECTRON_RUN_AS_NODE ELECTRON_RENDERER_URL I02_HMR I04_TEST_FIXTURE I04_NATIVE_ISOLATED
export DISPLAY=:111
export HOME=/probe-data/e2e-home
export XDG_CURRENT_DESKTOP=GNOME XDG_RUNTIME_DIR=/tmp/i06-e2e-runtime
export UV_CACHE_DIR=/tmp/i06-e2e-uv-cache UV_OFFLINE=1
mkdir -p "$HOME" /probe-data/main-platform/regression
mkdir -m 700 "$XDG_RUNTIME_DIR"
node tests/i06-main-platform/runtime-manifest.mjs /probe-data/main-platform/runtime-before.json
node tests/i06-main-platform/package-manifest.mjs /probe-data/main-platform/package-before.json
cp /opt/i06-main-identity.json /probe-data/main-platform/identity.json
cp /workspace/.i06-main-build-manifest.json /probe-data/main-platform/build-manifest.json
Xvfb :111 -screen 0 1440x1000x24 > /probe-data/main-platform/xvfb.log 2>&1 &
xvfb_pid=$!
trap 'kill "$xvfb_pid" 2>/dev/null || true' EXIT
for attempt in $(seq 1 100); do test -S /tmp/.X11-unix/X111 && break; sleep 0.05; done
dbus-run-session -- bash -euo pipefail -c '
  openbox > /probe-data/main-platform/openbox.log 2>&1 &
  printf "%s" "I06_E2E_SYNTHETIC_KEYRING_PASSWORD" | gnome-keyring-daemon --unlock --components=secrets > /probe-data/main-platform/keyring.log 2>&1
  export DEBUG=pw:browser
  export I02_EVIDENCE=/probe-data/main-platform/regression/source-i02.json
  export PLAYWRIGHT_JSON_OUTPUT_FILE=/probe-data/main-platform/regression/source-playwright.json
  set +e
  timeout 300s npm run test:e2e -- --output=/probe-data/main-platform/regression/source-traces --reporter=list,json > /probe-data/main-platform/regression/source.log 2>&1
  source_code=$?
  set -e
  printf "%s\n" "$source_code" > /probe-data/main-platform/regression/source-exit.txt
  cp -r test-results /probe-data/main-platform/regression/source-fixed-path-artifacts 2>/dev/null || true
  export ONTOLEARN_PACKAGED_EXECUTABLE=/workspace/release/linux-arm64-unpacked/@ontolearndesktop
  export I02_EVIDENCE=/probe-data/main-platform/regression/packaged-i02.json
  export PLAYWRIGHT_JSON_OUTPUT_FILE=/probe-data/main-platform/regression/packaged-playwright.json
  set +e
  timeout 300s npm run test:e2e -- --output=/probe-data/main-platform/regression/packaged-traces --reporter=list,json > /probe-data/main-platform/regression/packaged.log 2>&1
  package_code=$?
  set -e
  printf "%s\n" "$package_code" > /probe-data/main-platform/regression/packaged-exit.txt
  cp -r test-results /probe-data/main-platform/regression/packaged-fixed-path-artifacts 2>/dev/null || true
'
node tests/i06-main-platform/runtime-manifest.mjs /probe-data/main-platform/runtime-after.json
node tests/i06-main-platform/package-manifest.mjs /probe-data/main-platform/package-after.json
