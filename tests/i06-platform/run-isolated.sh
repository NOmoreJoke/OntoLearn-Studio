#!/bin/bash
set -euo pipefail
unset ELECTRON_RUN_AS_NODE
mkdir -p /probe-data/results
cp out/sources.json /probe-data/results/sources.json
cat /etc/os-release > /probe-data/results/os-release.txt
Xvfb :106 -screen 0 1280x800x24 > /probe-data/results/xvfb.log 2>&1 &
xvfb_pid=$!
trap 'kill "$xvfb_pid" 2>/dev/null || true' EXIT
for attempt in $(seq 1 100); do
  test -S /tmp/.X11-unix/X106 && break
  sleep 0.05
done
run_electron() {
  local mode="$1"
  shift
  I06_PROBE_MODE="$mode" timeout 45s node_modules/.bin/electron --no-sandbox "$@" probe.cjs \
    > "/probe-data/results/$mode.stdout.log" 2> "/probe-data/results/$mode.stderr.log"
}
export -f run_electron
dbus-run-session -- bash -euo pipefail -c '
  export XDG_CURRENT_DESKTOP=GNOME
  export XDG_RUNTIME_DIR=/tmp/i06-runtime-secure
  mkdir -m 700 "$XDG_RUNTIME_DIR"
  openbox > /probe-data/results/openbox.log 2>&1 &
  printf "%s" "I06_SYNTHETIC_KEYRING_PASSWORD" | gnome-keyring-daemon --unlock --components=secrets > /probe-data/results/keyring.log 2>&1
  run_electron secure-write --password-store=gnome-libsecret
  run_electron recover --password-store=gnome-libsecret
  run_electron corrupt --password-store=gnome-libsecret
'
dbus-run-session -- bash -euo pipefail -c '
  export HOME=/tmp/i06-new-keyring-home XDG_CURRENT_DESKTOP=GNOME XDG_RUNTIME_DIR=/tmp/i06-runtime-new
  mkdir -m 700 "$HOME" "$XDG_RUNTIME_DIR"
  printf "%s" "I06_ANOTHER_SYNTHETIC_PASSWORD" | gnome-keyring-daemon --unlock --components=secrets > /probe-data/results/new-keyring.log 2>&1
  run_electron key-loss --password-store=gnome-libsecret
'
dbus-run-session -- bash -euo pipefail -c 'run_electron basic --password-store=basic'
DBUS_SESSION_BUS_ADDRESS=unix:path=/tmp/i06-deliberately-missing-bus \
  run_electron unavailable --password-store=gnome-libsecret
cp /probe-data/*.json /probe-data/results/
rm /probe-data/results/synthetic-fixture.json
echo 'I06 isolated platform probes passed'
