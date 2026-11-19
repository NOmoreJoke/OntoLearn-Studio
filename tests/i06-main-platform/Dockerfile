# prepare-build.mjs verifies this tag's immutable image ID before every build.
FROM i06-safe-storage-platform:base-0497417676f6
USER root
RUN apt-get update && apt-get install -y --no-install-recommends python3-pip openssl \
    && rm -rf /var/lib/apt/lists/* \
    && python3 -m pip install --break-system-packages --no-cache-dir uv==0.11.12 \
    && npm install --global npm@11.12.1
ENV UV_PYTHON_INSTALL_DIR=/opt/i06-main-python UV_CACHE_DIR=/opt/i06-main-uv-cache
WORKDIR /workspace
COPY --chown=i06:i06 source/ ./
# Every mutable dependency belongs to this image, independently installed from project locks.
RUN npm ci && node node_modules/electron/install.js --no \
    && uv python install 3.12 && uv sync --frozen \
    && npm run build \
    && mkdir -p /probe-data/main-platform /probe-data/certificates \
    && chown -R i06:i06 /workspace /probe-data /opt/i06-main-python \
    && chown root:root /workspace/node_modules/electron/dist/chrome-sandbox \
    && chmod 4755 /workspace/node_modules/electron/dist/chrome-sandbox
COPY --chown=i06:i06 harness/ ./tests/i06-main-platform/
COPY --chown=i06:i06 identity.json /opt/i06-main-identity.json
USER i06
RUN npm exec -- eslint tests/i06-main-platform --max-warnings 0
RUN openssl req -x509 -newkey rsa:2048 -nodes -days 2 \
    -keyout /probe-data/certificates/ca.key -out /probe-data/certificates/ca.pem \
    -subj /CN=I06-SYNTHETIC-ONLY-CA \
    && openssl req -newkey rsa:2048 -nodes -keyout /probe-data/certificates/server.key \
    -out /probe-data/certificates/server.csr -subj /CN=127.0.0.1 \
    && printf 'subjectAltName=IP:127.0.0.1\nextendedKeyUsage=serverAuth\n' > /probe-data/certificates/server.ext \
    && openssl x509 -req -in /probe-data/certificates/server.csr -CA /probe-data/certificates/ca.pem \
    -CAkey /probe-data/certificates/ca.key -CAcreateserial -days 2 \
    -extfile /probe-data/certificates/server.ext -out /probe-data/certificates/server.pem
ENV NODE_EXTRA_CA_CERTS=/probe-data/certificates/ca.pem
RUN node tests/i06-main-platform/runtime-manifest.mjs /workspace/.i06-main-build-manifest.json
ENTRYPOINT ["bash", "/workspace/tests/i06-main-platform/run-isolated.sh"]
