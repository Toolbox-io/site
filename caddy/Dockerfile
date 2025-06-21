FROM caddy:2-builder AS builder
RUN xcaddy build --with github.com/mholt/caddy-ratelimit

FROM caddy:2

COPY --from=builder /usr/bin/caddy /usr/bin/caddy

LABEL org.opencontainers.image.source="https://github.com/Toolbox-io/site"
LABEL org.opencontainers.image.description="Custom Caddy built for Toolbox.io"