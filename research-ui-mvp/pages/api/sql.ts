import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  // READ-ONLY passthrough; prefer safe RPCs for production
  const sql = (req.body?.sql as string) || '';
  const r = await fetch(`${process.env.SUPABASE_REST_URL}/rpc/raw_sql`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'apikey': process.env.SUPABASE_ANON_KEY || '',
      'Authorization': `Bearer ${process.env.SUPABASE_ANON_KEY || ''}`
    },
    body: JSON.stringify({ q: sql }),
  });
  const text = await r.text();
  try { res.status(r.status).json(JSON.parse(text)); }
  catch { res.status(r.status).send(text); }
}
