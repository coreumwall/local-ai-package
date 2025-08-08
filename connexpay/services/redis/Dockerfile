# Stage 1: Use a trusted Alpine builder with Zscaler injection
FROM alpine:3.22 AS cert-setup

# Inject the Zscaler cert
COPY ../../zscaler.crt /usr/local/share/ca-certificates/zscaler.crt

RUN apk add --no-cache ca-certificates && \
    update-ca-certificates

# Stage 2: Final Valkey image
FROM docker.io/valkey/valkey:8-alpine

USER root

# Copy updated cert bundle from Stage 1
COPY --from=cert-setup /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/ca-certificates.crt
COPY --from=cert-setup /etc/ssl/certs/ca-cert-zscaler.pem /etc/ssl/certs/ca-cert-zscaler.pem

# Optional: Set env var if using Node or another tool that honors it
ENV NODE_EXTRA_CA_CERTS=/etc/ssl/certs/ca-cert-zscaler.pem

USER valkey
