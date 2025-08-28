import type { NextApiRequest, NextApiResponse } from 'next';
import neo4j from 'neo4j-driver';

const driver = () => neo4j.driver(
  process.env.NEO4J_URL!,
  neo4j.auth.basic(process.env.NEO4J_USER!, process.env.NEO4J_PASSWORD!)
);

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { cypher, params } = req.body || {};
  const d = driver();
  const session = d.session();
  try {
    const result = await session.run(cypher, params || {});
    const records = result.records.map(r => r.toObject());
    res.status(200).json({ records });
  } catch (e:any) {
    res.status(500).json({ error: e.message });
  } finally {
    await session.close();
    await d.close();
  }
}
