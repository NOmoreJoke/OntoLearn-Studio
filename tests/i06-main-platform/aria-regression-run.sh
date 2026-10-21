#!/bin/bash
set -euo pipefail
unset ELECTRON_RUN_AS_NODE ELECTRON_RENDERER_URL I02_HMR I04_TEST_FIXTURE I04_NATIVE_ISOLATED
export DISPLAY=:112 HOME=/probe-data/e2e-home
export XDG_CURRENT_DESKTOP=GNOME XDG_RUNTIME_DIR=/tmp/i06-aria-runtime
export UV_CACHE_DIR=/opt/i06-aria-uv-cache UV_OFFLINE=1
mkdir -p "$HOME" /probe-data/main-platform/regression
mkdir -m 700 "$XDG_RUNTIME_DIR"
node tests/i06-main-platform/runtime-manifest.mjs /probe-data/main-platform/runtime-before.json
node tests/i06-main-platform/aria-package-manifest.mjs /probe-data/main-platform/package-before.json
cp /opt/i06-main-identity.json /probe-data/main-platform/identity.json
cp /workspace/.i06-main-build-manifest.json /probe-data/main-platform/build-manifest.json
Xvfb :112 -screen 0 1440x1000x24 > /probe-data/main-platform/xvfb.log 2>&1 &
xvfb_pid=$!
trap 'kill "$xvfb_pid" 2>/dev/null || true' EXIT
for attempt in $(seq 1 100); do test -S /tmp/.X11-unix/X112 && break; sleep 0.05; done
dbus-run-session -- bash -euo pipefail -c '
  openbox > /probe-data/main-platform/openbox.log 2>&1 &
  printf "%s" "I06_ARIA_SYNTHETIC_KEYRING_PASSWORD" | gnome-keyring-daemon --unlock --components=secrets > /probe-data/main-platform/keyring.log 2>&1
  export DEBUG=pw:browser
  for mode in source packaged; do
    if test "$mode" = packaged; then export ONTOLEARN_PACKAGED_EXECUTABLE=/workspace/release/linux-arm64-unpacked/@ontolearndesktop; else unset ONTOLEARN_PACKAGED_EXECUTABLE; fi
    export I02_EVIDENCE=/probe-data/main-platform/regression/$mode-i02.json
    export PLAYWRIGHT_JSON_OUTPUT_FILE=/probe-data/main-platform/regression/$mode-playwright.json
    set +e
    timeout 300s npm run test:e2e -- --output=/probe-data/main-platform/regression/$mode-traces --reporter=list,json > /probe-data/main-platform/regression/$mode.log 2>&1
    code=$?
    set -e
    printf "%s\n" "$code" > /probe-data/main-platform/regression/$mode-exit.txt
    set +e
    timeout 60s node tests/i06-main-platform/aria-regression-check.mjs "$mode" > /probe-data/main-platform/regression/$mode-aria.log 2>&1
    code=$?
    set -e
    printf "%s\n" "$code" > /probe-data/main-platform/regression/$mode-aria-exit.txt
    for scenario in native reload disconnect; do
      directory=/probe-data/main-platform/regression/$mode-$scenario-fixture
      if test "$scenario" = reload; then uv run --frozen python scripts/prepare-i04-fixture.py "$directory" --background-rounds 12; else uv run --frozen python scripts/prepare-i04-fixture.py "$directory"; fi
      export I04_TEST_FIXTURE=$directory/fixture.json
      unset I04_NATIVE_ISOLATED
      if test "$scenario" = native; then export I04_NATIVE_ISOLATED=1; pattern="native renderer"; elif test "$scenario" = reload; then pattern="reload re-queries"; else pattern="coordinator exit"; fi
      export PLAYWRIGHT_JSON_OUTPUT_FILE=/probe-data/main-platform/regression/$mode-$scenario-playwright.json
      set +e
      timeout 150s npx playwright test tests/e2e/i04-jobs.spec.ts --grep "$pattern" --output=/probe-data/main-platform/regression/$mode-$scenario-traces --reporter=list,json > /probe-data/main-platform/regression/$mode-$scenario.log 2>&1
      code=$?
      set -e
      printf "%s\n" "$code" > /probe-data/main-platform/regression/$mode-$scenario-exit.txt
      unset I04_TEST_FIXTURE I04_NATIVE_ISOLATED
    done
  done
'
node tests/i06-main-platform/runtime-manifest.mjs /probe-data/main-platform/runtime-after.json
node tests/i06-main-platform/aria-package-manifest.mjs /probe-data/main-platform/package-after.json
