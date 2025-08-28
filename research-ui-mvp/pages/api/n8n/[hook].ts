import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { hook } = req.query;
  const url = `${process.env.N8N_URL}/webhook/${hook}`;
  const r = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req.body || {}),
  });
  const text = await r.text();
  res.status(r.status).send(text);
}
