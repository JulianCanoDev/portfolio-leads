export const API_COOKIE = 'julixr_token';

export interface Lead {
  id: number;
  name: string;
  email: string;
  message: string;
  status: string;
  created_at: string;
}

export interface LeadsPage {
  items: Lead[];
  page: number;
  pages: number;
  total: number;
}

export interface Stats {
  total: number;
  new: number;
  contacted: number;
  today: number;
}

export const PAGE_SIZE = 20;

// Server-side base URL: inside docker-compose the FastAPI service is
// reachable at http://backend:8000. Browser code never uses this module —
// it calls /api/* directly through the nginx reverse proxy.
const serverBase = () => process.env.BACKEND_URL ?? 'http://localhost:8000';

async function apiGet<T>(path: string, token: string): Promise<T | null> {
  try {
    const res = await fetch(`${serverBase()}${path}`, {
      headers: { authorization: `Bearer ${token}` },
      cache: 'no-store',
    });
    if (res.status === 401 || res.status === 403) return null;
    if (!res.ok) throw new Error(`API responded ${res.status}`);
    return (await res.json()) as T;
  } catch {
    return null;
  }
}

export async function fetchLeads(
  token: string,
  page: number,
  status?: string,
  search?: string,
): Promise<LeadsPage | null> {
  const params = new URLSearchParams();
  params.set('page', String(Math.max(1, page)));
  if (status === 'new' || status === 'contacted') params.set('status', status);
  if (search && search.trim()) params.set('search', search.trim());
  return apiGet<LeadsPage>(`/api/leads?${params.toString()}`, token);
}

export async function fetchStats(token: string): Promise<Stats | null> {
  return apiGet<Stats>('/api/stats', token);
}
