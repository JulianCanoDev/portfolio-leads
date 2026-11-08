// CMS data: defaults + server-side fetchers with fallback, so the public
// portfolio renders even without a reachable backend (local dev).

export interface SiteSettings {
  name: string;
  role_title: string;
  tagline: string;
  accent_color: string;
  secondary_color: string;
  linkedin_url: string;
  github_url: string;
  whatsapp_phone: string;
  cv_url: string;
  skills: string[];
}

export interface CmsProject {
  id: number;
  title: string;
  category: string;
  challenge: string | null;
  solution: string | null;
  stack: string | null;
  tags: string[];
  image_url: string | null;
  sort_order: number;
}

export const DEFAULT_SETTINGS: SiteSettings = {
  name: 'Julian Cano',
  role_title: 'Full Stack & AI Developer | AWS Cloud | AI Automation & Agents',
  tagline: '',
  accent_color: '#6d28d9',
  secondary_color: '#0d9488',
  linkedin_url: 'https://www.linkedin.com/in/juliancanodev/',
  github_url: 'https://github.com/JulianCanoDev',
  whatsapp_phone: '573237073472',
  cv_url: '/CV_Julian_Cano.pdf',
  skills: [],
};

export const DEFAULT_PROJECTS: CmsProject[] = [
  {
    id: -1,
    title: 'Researcher App',
    category: 'Automation',
    challenge:
      'Scraping de empleos y remates judiciales desde fuentes dispares (gov, portales). Deduplicación, clasificación y envío masivo diario por WhatsApp.',
    solution: '+87 reportes enviados, 3+ digests diarios (empleos, remates, tendencias). Automatización completa headless.',
    stack: 'Next.js · Celery · PostgreSQL · Redis · Evolution API · DataForSEO',
    tags: ['Automation', 'Scraping', 'WhatsApp'],
    image_url: '/images/researcher-app.webp',
    sort_order: 0,
  },
  {
    id: -2,
    title: 'OpenSEO Toolkit',
    category: 'Web',
    challenge: 'Desplegar y mantener un SEO toolkit self-hosted integrado con MCP para consultas desde el asistente AI.',
    solution: 'Instancia operativa con health checks automáticos, monitoreo vía Uptime Kuma, integración con AI vía MCP.',
    stack: 'Pterodactyl · Docker · DataForSEO API · MCP · Uptime Kuma',
    tags: ['SEO', 'Self-hosted', 'Docker'],
    image_url: '/images/openseo.webp',
    sort_order: 1,
  },
  {
    id: -3,
    title: 'Colombia Aprende + AWS',
    category: 'Cloud',
    challenge: 'Participación en el convenio Alcaldía de Bogotá y AWS para formación en tecnologías cloud.',
    solution: 'Formación oficial en cloud computing. Aplicación práctica en infraestructura de proyectos reales.',
    stack: 'AWS · Cloud Infrastructure',
    tags: ['AWS', 'Cloud'],
    image_url: '/images/colombia-aprende.webp',
    sort_order: 2,
  },
];

const serverBase = () => process.env.BACKEND_URL ?? 'http://localhost:8000';

export async function getSettings(): Promise<SiteSettings> {
  try {
    const res = await fetch(`${serverBase()}/api/settings`, { cache: 'no-store' });
    if (!res.ok) throw new Error(String(res.status));
    return { ...DEFAULT_SETTINGS, ...(await res.json()) };
  } catch {
    return DEFAULT_SETTINGS;
  }
}

export async function getProjects(): Promise<CmsProject[]> {
  try {
    const res = await fetch(`${serverBase()}/api/projects`, { cache: 'no-store' });
    if (!res.ok) throw new Error(String(res.status));
    return (await res.json()) as CmsProject[];
  } catch {
    return DEFAULT_PROJECTS;
  }
}

// Derived palette: given the two CMS colors, compute the glow/soft variants
// used across the theme so the whole site re-themes from 2 inputs.
function towardWhite(hex: string, amount: number): string {
  const channel = (start: number) =>
    Math.round(start + (255 - start) * amount)
      .toString(16)
      .padStart(2, '0');
  return `#${channel(parseInt(hex.slice(1, 3), 16))}${channel(parseInt(hex.slice(3, 5), 16))}${channel(parseInt(hex.slice(5, 7), 16))}`;
}

export function paletteVars(accent: string, secondary: string): Record<string, string> {
  return {
    '--accent': accent,
    '--accent-glow': towardWhite(accent, 0.28),
    '--accent-soft': towardWhite(accent, 0.6),
    '--secondary': secondary,
    '--secondary-soft': towardWhite(secondary, 0.4),
  };
}
