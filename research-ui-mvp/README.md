# Research UI MVP

A tiny Next.js frontend that ties together your local Flowise, n8n, SearXNG, Supabase (PostgREST), Neo4j, and Langfuse.

## Quick start
1. Copy `.env.example` to `.env.local` and adjust endpoints to your container names/ports.
2. `npm install`
3. `npm run dev` (or build + dockerize with the provided Dockerfile)

## API Proxies
- `POST /api/flowise/:id` → `${FLOWISE_URL}/prediction/:id` (Flowise Prediction API)
- `POST /api/n8n/:hook` → `${N8N_URL}/webhook/:hook` (Webhook must be set to 'When Last Node Finishes')
- `GET  /api/searx?q=...` → `${SEARX_URL}/search?format=json`
- `POST /api/sql` → `${SUPABASE_REST_URL}/rpc/raw_sql` (demo; prefer table endpoints/RPCs)
- `POST /api/neo4j` → run read queries against Neo4j

## Graph Tab
Uses `react-force-graph-3d` to render a simple force graph. Replace the demo data by calling `/api/neo4j` with a Cypher query and mapping the result to `{nodes,links}`.

## Notes
- Keep embeddings in pgvector with HNSW for fast KNN.
- Use n8n Webhook 'Respond when last node finishes' to return data directly to the UI.
- Enable JSON output in SearXNG for the Search tab.
