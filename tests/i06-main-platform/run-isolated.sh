#!/bin/bash
set -euo pipefail
unset ELECTRON_RUN_AS_NODE
export DISPLAY=:108
export XDG_CURRENT_DESKTOP=GNOME XDG_RUNTIME_DIR=/tmp/i06-main-runtime
mkdir -m 700 "$XDG_RUNTIME_DIR"
node tests/i06-main-platform/sandbox-preflight.mjs > /probe-data/main-platform/sandbox-preflight.json 2> /probe-data/main-platform/sandbox-preflight.stderr.log
Xvfb :108 -screen 0 1440x1000x24 > /probe-data/main-platform/xvfb.log 2>&1 &
xvfb_pid=$!
trap 'kill "$xvfb_pid" 2>/dev/null || true' EXIT
for attempt in $(seq 1 100); do
  test -S /tmp/.X11-unix/X108 && break
  sleep 0.05
done
node tests/i06-main-platform/runtime-manifest.mjs /probe-data/main-platform/runtime-before.json
cp /workspace/.i06-main-build-manifest.json /probe-data/main-platform/build-manifest.json
cp /opt/i06-main-identity.json /probe-data/main-platform/identity.json
dbus-run-session -- bash -euo pipefail -c '
  openbox > /probe-data/main-platform/openbox.log 2>&1 &
  printf "%s" "I06_MAIN_SYNTHETIC_KEYRING_PASSWORD" | gnome-keyring-daemon --unlock --components=secrets > /probe-data/main-platform/keyring.log 2>&1
  timeout 360s node tests/i06-main-platform/probe.mjs > /probe-data/main-platform/probe.stdout.log 2> /probe-data/main-platform/probe.stderr.log
'
node tests/i06-main-platform/runtime-manifest.mjs /probe-data/main-platform/runtime-after.json
node tests/i06-main-platform/scan.mjs
echo 'I06 actual main/preload/UI platform probe passed'
