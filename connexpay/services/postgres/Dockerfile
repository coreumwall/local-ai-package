ARG POSTGRES_VERSION=latest
FROM postgres:${POSTGRES_VERSION}

USER root

COPY ../../zscaler.crt /usr/local/share/ca-certificates/zscaler.crt

RUN apk --no-cache add ca-certificates && \
    update-ca-certificates

ENV NODE_EXTRA_CA_CERTS=/etc/ssl/certs/ca-cert-zscaler.pem

USER node