#!/bin/bash
set -euo pipefail
unset ELECTRON_RUN_AS_NODE
export DISPLAY=:107
mkdir -p /probe-data/combination-results
cp out/sources.json /probe-data/combination-results/sources.json
cat /etc/os-release > /probe-data/combination-results/os-release.txt
Xvfb :107 -screen 0 1280x800x24 > /probe-data/combination-results/xvfb.log 2>&1 &
xvfb_pid=$!
trap 'kill "$xvfb_pid" 2>/dev/null || true' EXIT
for attempt in $(seq 1 100); do
  test -S /tmp/.X11-unix/X107 && break
  sleep 0.05
done
run_electron() {
  local mode="$1"
  shift
  I06_PRIVATE_PROBE_MODE="$mode" timeout 60s /opt/i06-platform/node_modules/.bin/electron --no-sandbox "$@" probe.cjs \
    > "/probe-data/combination-results/$mode.stdout.log" 2> "/probe-data/combination-results/$mode.stderr.log"
}
export -f run_electron
dbus-run-session -- bash -euo pipefail -c '
  export XDG_CURRENT_DESKTOP=GNOME XDG_RUNTIME_DIR=/tmp/i06-private-runtime-secure
  mkdir -m 700 "$XDG_RUNTIME_DIR"
  openbox > /probe-data/combination-results/openbox.log 2>&1 &
  printf "%s" "I06_SYNTHETIC_COMBINATION_KEYRING" | gnome-keyring-daemon --unlock --components=secrets > /probe-data/combination-results/keyring.log 2>&1
  run_electron secure-send --password-store=gnome-libsecret
  run_electron recover-no-replay --password-store=gnome-libsecret
  run_electron corrupt --password-store=gnome-libsecret
'
dbus-run-session -- bash -euo pipefail -c '
  export HOME=/tmp/i06-private-new-keyring XDG_CURRENT_DESKTOP=GNOME XDG_RUNTIME_DIR=/tmp/i06-private-runtime-new
  mkdir -m 700 "$HOME" "$XDG_RUNTIME_DIR"
  printf "%s" "I06_ANOTHER_SYNTHETIC_COMBINATION_KEYRING" | gnome-keyring-daemon --unlock --components=secrets > /probe-data/combination-results/new-keyring.log 2>&1
  run_electron key-loss --password-store=gnome-libsecret
'
dbus-run-session -- bash -euo pipefail -c 'run_electron basic --password-store=basic'
DBUS_SESSION_BUS_ADDRESS=unix:path=/tmp/i06-private-missing-bus \
  run_electron unavailable --password-store=gnome-libsecret
node - <<'NODE'
const fs = require('node:fs')
const assert = require('node:assert/strict')
const directory = '/probe-data/combination-results'
const tokens = ['I06_COMBINATION_SYNTHETIC_SECRET', 'I06_COMBINATION_SYNTHETIC_BUSINESS', 'I06_SYNTHETIC_ENDPOINT_PATH', 'PRIVATE_PATH_MARKER']
const files = fs.readdirSync(directory).filter((name) => name.endsWith('.log'))
for (const name of files) {
  const bytes = fs.readFileSync(directory + '/' + name)
  for (const token of tokens) assert.equal(bytes.includes(Buffer.from(token)), false)
}
fs.writeFileSync(directory + '/log-scan.json', JSON.stringify({result:'passed', ordinaryLogFiles:files.length, forbiddenCredentialBusinessEndpointPathMarkers:false}) + '\n')
NODE
echo 'I06 actual private-storage gateway combination passed'
