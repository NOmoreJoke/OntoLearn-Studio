set -e
cp -a /root/.local/share/uv/python /opt/i02-python
mv /work/.venv /work/.venv-root-diagnostic
chown -R node:node /work /opt/i02-python
runuser -u node -- env HOME=/home/node PATH=/opt/i02-tools/bin:/usr/local/bin:/usr/bin:/bin UV_PYTHON_INSTALL_DIR=/opt/i02-python UV_CACHE_DIR=/tmp/i02-uv-cache bash -c 'uv sync --frozen && DEBUG=pw:browser I02_EVIDENCE=/work/linux-user-diagnostic-matrix.json xvfb-run -a npm run test:e2e'
