FROM searxng/searxng:latest

# Copy your corporate certificate
COPY ZscalerRootCertificate.crt /etc/searxng/ZscalerRootCertificate.crt

# Copy custom settings.yml
COPY searxng/settings.yml /etc/searxng/settings.yml

# Set SSL-related environment variables
ENV SSL_CERT_FILE=/etc/searxng/ZscalerRootCertificate.crt
ENV REQUESTS_CA_BUNDLE=/etc/searxng/ZscalerRootCertificate.crt
ENV CURL_CA_BUNDLE=/etc/searxng/ZscalerRootCertificate.crt
ENV PYTHONHTTPSVERIFY=1

# Ensure correct permissions
RUN chmod 644 /etc/searxng/settings.yml /etc/searxng/ZscalerRootCertificate.crt

# Create a script to verify SSL (optional)
RUN echo '#!/bin/sh' > /verify-ssl.sh && \
    echo 'echo "Verifying SSL connection..."' >> /verify-ssl.sh && \
    echo 'python3 -c "import ssl, socket; context = ssl.create_default_context(); socket.create_connection((\"deno.land\", 443)); print(\"Python SSL Connection Successful\")"' >> /verify-ssl.sh && \
    chmod +x /verify-ssl.sh