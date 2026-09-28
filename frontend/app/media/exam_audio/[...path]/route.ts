import type { NextRequest } from 'next/server';

export const runtime = 'nodejs';

const responseHeaders = [
  'Content-Type', 'Content-Length', 'Content-Range', 'Accept-Ranges',
  'Content-Disposition', 'Last-Modified', 'X-Content-Type-Options',
];

async function proxy(request: NextRequest, path: string[], head = false) {
  const backend = process.env.BACKEND_URL?.replace(/\/$/, '');
  if (!backend) return new Response('Audio backend is unavailable.', { status: 503 });
  const headers = new Headers();
  for (const name of ['Range', 'If-Range']) {
    const value = request.headers.get(name);
    if (value) headers.set(name, value);
  }
  try {
    const url = `${backend}/media/exam_audio/${path.map(encodeURIComponent).join('/')}`;
    const upstream = await fetch(url, { method: head ? 'HEAD' : 'GET', headers, cache: 'no-store' });
    const forwarded = new Headers();
    for (const name of responseHeaders) {
      const value = upstream.headers.get(name);
      if (value) forwarded.set(name, value);
    }
    forwarded.set('X-Content-Type-Options', 'nosniff');
    return new Response(head ? null : upstream.body, { status: upstream.status, headers: forwarded });
  } catch {
    return new Response('Audio backend is unavailable.', { status: 502 });
  }
}

type Context = { params: Promise<{ path: string[] }> };

export async function GET(request: NextRequest, { params }: Context) {
  return proxy(request, (await params).path);
}

export async function HEAD(request: NextRequest, { params }: Context) {
  return proxy(request, (await params).path, true);
}
