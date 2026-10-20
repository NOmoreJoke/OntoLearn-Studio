set -e
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y --no-install-recommends xvfb xauth libgtk-3-0 libnss3 libasound2 libgbm1 libxss1 libatk-bridge2.0-0 libdrm2 libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 libxtst6 libxkbcommon0 python3-venv
python3 -m venv /opt/i02-tools
/opt/i02-tools/bin/pip install uv==0.11.12
export PATH=/opt/i02-tools/bin:$PATH
npm ci
uv sync --frozen
npm run build
DEBUG=pw:browser I02_EVIDENCE=/work/linux-diagnostic-matrix.json xvfb-run -a npm run test:e2e
