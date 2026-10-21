# Local verification image only. No source is pushed or mounted into another task's runtime.
FROM node:24-bookworm@sha256:14078204b6bb268c107ceff6d3c43f45a888105e5c2b18b14c32b3409d93a1b0
COPY --from=ghcr.io/astral-sh/uv:0.11.12 /uv /uvx /usr/local/bin/
RUN apt-get update && apt-get install -y --no-install-recommends \
    xvfb xauth openbox xdotool dbus-x11 libgtk-3-0 libnss3 libxss1 libasound2 \
    libgbm1 libx11-xcb1 libdrm2 libxcomposite1 libxrandr2 libxtst6 libxdamage1 \
    libcups2 libatk-bridge2.0-0 fonts-noto-cjk ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && npm install -g npm@11.12.1 \
    && groupadd --gid 1110 t10 \
    && useradd --uid 1110 --gid 1110 --create-home --shell /bin/bash t10 \
    && mkdir -p /opt/t10 /opt/t10-controls /opt/t10-evidence /opt/python-managed /opt/uv-cache
COPY source.tar /tmp/t10-source.tar
RUN tar --no-same-owner --no-same-permissions -xf /tmp/t10-source.tar -C /opt/t10 \
    && rm /tmp/t10-source.tar \
    && chown -R 1110:1110 /opt/t10 /opt/t10-controls /opt/t10-evidence /opt/python-managed /opt/uv-cache
ENV UV_PYTHON_INSTALL_DIR=/opt/python-managed UV_CACHE_DIR=/opt/uv-cache T10_ISOLATED_NATIVE=1
WORKDIR /opt/t10
USER t10
RUN npm ci --ignore-scripts \
    && ./node_modules/.bin/install-electron \
    && uv sync --frozen --python 3.12 \
    && npm run build
USER root
RUN chown root:root /opt/t10/node_modules/electron/dist/chrome-sandbox \
    && chmod 4755 /opt/t10/node_modules/electron/dist/chrome-sandbox
RUN apt-get update && apt-get install -y --no-install-recommends imagemagick \
    && rm -rf /var/lib/apt/lists/*
COPY --chown=1110:1110 controls/ /opt/t10-controls/
USER t10
CMD ["bash", "/opt/t10-controls/run.sh"]
