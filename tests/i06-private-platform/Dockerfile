# The build launcher must verify this unique local tag has the recorded immutable image ID.
FROM i06-safe-storage-platform:base-0497417676f6
USER root
WORKDIR /opt/i06-private-platform
COPY out/*.js out/package.json out/sources.json ./out/
COPY probe.cjs run-isolated.sh ./
RUN mkdir -m 700 /probe-data/foreign-userdata && mkdir node_modules && \
    cp -a /opt/i06-platform/node_modules/zod node_modules/zod
USER i06
ENTRYPOINT ["bash", "/opt/i06-private-platform/run-isolated.sh"]
