# Dockerfile.mcpo_seq_think_proxy
FROM mcp/sequentialthinking:latest

# Assuming Alpine Linux base for the Node.js image, use apk.
USER root
RUN apk update && \
    apk add --no-cache python3 py3-pip wget && \
    rm -rf /var/cache/apk/*
RUN pip3 install --no-cache-dir --break-system-packages mcpo

ENV ORIGINAL_MCP_COMMAND="node dist/index.js"
WORKDIR /app

EXPOSE 8001

ENTRYPOINT ["mcpo"]
CMD ["--host", "0.0.0.0", "--port", "8001", "--", "/bin/sh", "-c", "$ORIGINAL_MCP_COMMAND"]