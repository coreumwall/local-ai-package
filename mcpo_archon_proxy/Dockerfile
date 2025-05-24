# Dockerfile.mcpo_archon_proxy
FROM archon-mcp:latest

USER root
RUN apt-get update && \
    apt-get install -y --no-install-recommends python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
RUN pip3 install --no-cache-dir --break-system-packages mcpo

ENV ORIGINAL_MCP_COMMAND="python mcp_server.py"
WORKDIR /app

EXPOSE 8002

ENTRYPOINT ["mcpo"]
CMD ["--host", "0.0.0.0", "--port", "8002", "--", "/bin/sh", "-c", "$ORIGINAL_MCP_COMMAND"]