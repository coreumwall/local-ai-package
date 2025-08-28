import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const q = (req.query.q as string) || '';
  const url = `${process.env.SEARX_URL}/search?format=json&q=${encodeURIComponent(q)}`;
  const r = await fetch(url);
  const data = await r.json();
  res.status(200).json(data);
}
