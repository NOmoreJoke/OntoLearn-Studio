#!/bin/bash
set -euo pipefail
test "$(id -u)" = 1110
test "$(stat -c '%u:%a' node_modules/electron/dist/chrome-sandbox)" = '0:4755'
unset ELECTRON_RUN_AS_NODE ELECTRON_DISABLE_SANDBOX ELECTRON_RENDERER_URL NODE_OPTIONS I02_HMR
node --version > /opt/t10-evidence/node-version.txt
npm --version > /opt/t10-evidence/npm-version.txt
uv --version > /opt/t10-evidence/uv-version.txt
.venv/bin/python --version > /opt/t10-evidence/python-version.txt
npx vitest run tests/unit/t10-report.test.ts tests/unit/t10-report-file.test.ts > /opt/t10-evidence/units.txt 2>&1
uv run --frozen pytest packages/engine/tests/test_transfer_inspection.py -q > /opt/t10-evidence/pytest.txt 2>&1
node /opt/t10-controls/prepare-native.mjs
dbus-run-session -- xvfb-run -a -s '-screen 0 1280x900x24' sh -c '
  openbox > /opt/t10-evidence/openbox.txt 2>&1 &
  task_openbox_pid=$!
  trap '\''kill "$task_openbox_pid" 2>/dev/null || true'\'' EXIT
  node /opt/t10-controls/native-driver.mjs
'
