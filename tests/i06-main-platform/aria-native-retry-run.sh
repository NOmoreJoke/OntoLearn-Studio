#!/bin/bash
set -euo pipefail
unset ELECTRON_RUN_AS_NODE ELECTRON_RENDERER_URL I02_HMR I04_TEST_FIXTURE I04_NATIVE_ISOLATED ONTOLEARN_PACKAGED_EXECUTABLE
export DISPLAY=:113 HOME=/probe-data/e2e-home
export XDG_CURRENT_DESKTOP=GNOME XDG_RUNTIME_DIR=/tmp/i06-native-retry-runtime
export UV_CACHE_DIR=/opt/i06-aria-uv-cache UV_OFFLINE=1
mkdir -p "$HOME" /probe-data/main-platform/regression
mkdir -m 700 "$XDG_RUNTIME_DIR"
node tests/i06-main-platform/runtime-manifest.mjs /probe-data/main-platform/runtime-before.json
cp /opt/i06-main-identity.json /probe-data/main-platform/identity.json
cp /workspace/.i06-main-build-manifest.json /probe-data/main-platform/build-manifest.json
Xvfb :113 -screen 0 1440x1000x24 > /probe-data/main-platform/xvfb.log 2>&1 &
xvfb_pid=$!
trap 'kill "$xvfb_pid" 2>/dev/null || true' EXIT
for attempt in $(seq 1 100); do test -S /tmp/.X11-unix/X113 && break; sleep 0.05; done
set +e
dbus-run-session -- bash -euo pipefail -c '
  openbox > /probe-data/main-platform/openbox.log 2>&1 &
  printf "%s" "I06_RETRY_SYNTHETIC_KEYRING_PASSWORD" | gnome-keyring-daemon --unlock --components=secrets > /probe-data/main-platform/keyring.log 2>&1
  directory=/probe-data/main-platform/regression/source-native-retry-fixture
  uv run --frozen python scripts/prepare-i04-fixture.py "$directory"
  export I04_TEST_FIXTURE=$directory/fixture.json I04_NATIVE_ISOLATED=1
  export PLAYWRIGHT_JSON_OUTPUT_FILE=/probe-data/main-platform/regression/source-native-retry-playwright.json
  timeout 150s npx playwright test tests/e2e/i04-jobs.spec.ts --grep "native renderer" --output=/probe-data/main-platform/regression/source-native-retry-traces --reporter=list,json > /probe-data/main-platform/regression/source-native-retry.log 2>&1
'
code=$?
set -e
printf '%s\n' "$code" > /probe-data/main-platform/regression/source-native-retry-exit.txt
node tests/i06-main-platform/runtime-manifest.mjs /probe-data/main-platform/runtime-after.json
exit "$code"
