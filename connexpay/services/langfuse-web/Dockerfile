# Stage 1: Inherit upstream image
FROM langfuse/langfuse:3 AS base

# Stage 2: ConnexPay wrapper
FROM base AS wrapper

USER root

COPY ../../zscaler.crt /usr/local/share/ca-certificates/zscaler.crt

RUN apk --no-cache add ca-certificates && \
    update-ca-certificates

ENV NODE_EXTRA_CA_CERTS=/etc/ssl/certs/ca-cert-zscaler.pem

USER node