// CMS data: defaults + server-side fetchers with fallback, so the public
// portfolio renders even without a reachable backend (local dev).

export interface Localized2 {}

export interface SiteSettings {
  name: string;
  role_title: Localized;
  tagline: Localized;
  description: Localized;
  accent_color: string;
  secondary_color: string;
  linkedin_url: string;
  github_url: string;
  whatsapp_phone: string;
  cv_url: string;
  skills: string[];
}

export interface Localized {
  es: string | null;
  en: string | null;
}

export interface CmsProject {
  id: number;
  title: Localized;
  category: Localized;
  challenge: Localized;
  solution: Localized;
  stack: string | null;
  tags: string[];
  image_url: string | null;
  color: string | null;
  sort_order: number;
}

export function pick(field: Localized | null | undefined, locale: string): string | null {
  if (!field) return null;
  if (locale === 'en') return field.en ?? field.es;
  return field.es ?? field.en;
}

export const DEFAULT_SETTINGS: SiteSettings = {
  name: 'Julian Cano',
  role_title: {
    es: 'Desarrollador Full Stack & IA | AWS Cloud | Automatización & Agentes de IA',
    en: 'Full Stack & AI Developer | AWS Cloud | AI Automation & Agents',
  },
  tagline: {
    es: 'Sistemas donde convergen IA, automatización y desarrollo web',
    en: 'Building systems where AI, automation and web converge',
  },
  description: {
    es: 'Construyo sistemas que integran inteligencia artificial, automatización y desarrollo web — de la idea a producción.',
    en: 'I build systems that integrate AI, automation and web — from idea to production.',
  },
  accent_color: '#6d28d9',
  secondary_color: '#0d9488',
  linkedin_url: 'https://www.linkedin.com/in/juliancanodev/',
  github_url: 'https://github.com/JulianCanoDev',
  whatsapp_phone: '573237073472',
  cv_url: '/CV_Julian_Cano.pdf',
  skills: [
    'FastAPI',
    'Astro',
    'PostgreSQL',
    'Docker',
    'n8n',
    'VPS',
    'AWS Cloud',
    'LangChain',
    'LangGraph',
    'Unity 3D',
    'OpenClaw',
    'Next.js',
    'Redis',
    'Celery',
    'Python',
    'WebSocket',
    'AI Agents',
    'Tailwind CSS',
    'Nginx',
    'GitHub',
  ],
};

export const DEFAULT_PROJECTS: CmsProject[] = [
  {
    id: -1,
    title: { es: 'Researcher App', en: 'Researcher App' },
    category: { es: 'Automation', en: 'Automation' },
    challenge: {
      es: 'Scraping de empleos y remates judiciales desde fuentes dispares (gov, portales). Deduplicación, clasificación y envío masivo diario por WhatsApp.',
      en: 'Scraping job listings and judicial auctions from disparate sources (gov sites, portals). Deduplication, classification, and daily mass delivery via WhatsApp.',
    },
    solution: {
      es: '+87 reportes enviados, 3+ digests diarios (empleos, remates, tendencias). Automatización completa headless.',
      en: '+87 reports sent, 3+ daily digests (jobs, auctions, trends). Fully headless automation.',
    },
    stack: 'Next.js · Celery · PostgreSQL · Redis · Evolution API · DataForSEO',
    tags: ['Automation', 'Scraping', 'WhatsApp'],
    image_url: '/images/researcher-app.webp',
    color: '#2dd4bf',
    sort_order: 0,
  },
  {
    id: -2,
    title: { es: 'OpenSEO Toolkit', en: 'OpenSEO Toolkit' },
    category: { es: 'Web', en: 'Web' },
    challenge: {
      es: 'Desplegar y mantener un SEO toolkit self-hosted integrado con MCP para consultas desde el asistente AI.',
      en: 'Deploy and maintain a self-hosted SEO toolkit integrated with MCP for AI assistant queries.',
    },
    solution: {
      es: 'Instancia operativa con health checks automáticos, monitoreo vía Uptime Kuma, integración con AI vía MCP.',
      en: 'Live instance with automated health checks, Uptime Kuma monitoring, AI integration via MCP.',
    },
    stack: 'Pterodactyl · Docker · DataForSEO API · MCP · Uptime Kuma',
    tags: ['SEO', 'Self-hosted', 'Docker'],
    image_url: '/images/openseo.webp',
    color: '#7dd3fc',
    sort_order: 1,
  },
  {
    id: -3,
    title: { es: 'Colombia Aprende + AWS', en: 'Colombia Aprende + AWS' },
    category: { es: 'Cloud', en: 'Cloud' },
    challenge: {
      es: 'Participación en el convenio Alcaldía de Bogotá y AWS para formación en tecnologías cloud.',
      en: "Participation in the Bogotá Mayor's Office and AWS agreement for cloud technology training.",
    },
    solution: {
      es: 'Formación oficial en cloud computing. Aplicación práctica en infraestructura de proyectos reales.',
      en: 'Official cloud computing training. Hands-on application in real project infrastructure.',
    },
    stack: 'AWS · Cloud Infrastructure',
    tags: ['AWS', 'Cloud'],
    image_url: '/images/colombia-aprende.webp',
    color: '#fbbf24',
    sort_order: 2,
  },
];

const serverBase = () => process.env.BACKEND_URL ?? 'http://localhost:8000';

// Older API versions returned some CMS fields as plain strings; wrap them
// into the localized shape so pick() keeps working during upgrades.
function normalize(data: Record<string, unknown>): Partial<SiteSettings> {
  for (const field of ['role_title', 'tagline', 'description'] as const) {
    if (typeof data[field] === 'string') {
      data[field] = { es: data[field] as string, en: null };
    }
  }
  return data as Partial<SiteSettings>;
}

export async function getSettings(): Promise<SiteSettings> {
  try {
    const res = await fetch(`${serverBase()}/api/settings`, { cache: 'no-store' });
    if (!res.ok) throw new Error(String(res.status));
    return { ...DEFAULT_SETTINGS, ...normalize(await res.json()) };
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
