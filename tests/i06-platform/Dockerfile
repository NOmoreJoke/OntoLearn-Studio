FROM node:24-bookworm@sha256:14078204b6bb268c107ceff6d3c43f45a888105e5c2b18b14c32b3409d93a1b0
RUN apt-get update && apt-get install -y --no-install-recommends \
    xvfb openbox dbus-x11 gnome-keyring libsecret-1-0 libgtk-3-0 libnss3 \
    libasound2 libgbm1 libxss1 libatk-bridge2.0-0 ca-certificates \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /opt/i06-platform
RUN npm install --no-save --package-lock=false electron@44.9.0 zod@4.6.7 && \
    node node_modules/electron/install.js --no
COPY out/ ./out/
COPY probe.cjs run-isolated.sh ./
RUN useradd --create-home --uid 1106 i06 && mkdir /probe-data && \
    chown -R i06:i06 /probe-data /opt/i06-platform
USER i06
ENV DISPLAY=:106
ENTRYPOINT ["bash", "/opt/i06-platform/run-isolated.sh"]
