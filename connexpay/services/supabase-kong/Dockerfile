FROM kong:2.8.1

# Switch to root user for modifications
USER root

# Temporarily disable SSL verification for apk
RUN sed -i 's/https/http/g' /etc/apk/repositories || true

# Install necessary tools
RUN apk update && \
    apk add --no-cache \
    ca-certificates \
    wget \
    openssl

# Copy your corporate certificate
COPY ZscalerRootCertificate.crt /usr/local/share/ca-certificates/ZscalerRootCertificate.crt

# Add the certificate and update the certificate store
RUN cp /usr/local/share/ca-certificates/ZscalerRootCertificate.crt /etc/ssl/certs/ && \
    # Revert to HTTPS repositories
    sed -i 's/http/https/g' /etc/apk/repositories || true && \
    update-ca-certificates

# Create a script to verify certificate
RUN echo '#!/bin/sh' > /verify-ssl.sh && \
    echo 'echo "Verifying SSL connection..."' >> /verify-ssl.sh && \
    echo 'wget -O- https://deno.land' >> /verify-ssl.sh && \
    echo 'echo | openssl s_client -connect deno.land:443' >> /verify-ssl.sh && \
    chmod +x /verify-ssl.sh

# Switch back to the original user if needed
USER kong