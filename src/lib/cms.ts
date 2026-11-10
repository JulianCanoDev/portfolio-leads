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
    title: { es: "Researcher App", en: "Researcher App" },
    category: { es: "Automation", en: "Automation" },
    challenge: {
      es: "Rastrear vacantes y remates judiciales publicados en decenas de sitios gubernamentales y portales privados sin API, con formatos y cadencias distintas. Había que deduplicar miles de registros semanales que aparecían repetidos entre fuentes, clasificarlos por tipo y entregar un resumen diario por WhatsApp a una lista grande de destinatarios sin caer en bloqueos ni requerir curación manual.",
      en: "Tracking job vacancies and judicial auctions published across dozens of government sites and private portals with no APIs, each with different formats and publishing rhythms. Thousands of records per week appeared duplicated across sources and needed deduplication, classification and daily delivery via WhatsApp to a large recipient list without getting blocked or requiring manual curation.",
    },
    solution: {
      es: "Pipeline headless en Next.js + Celery con scrapers programados por fuente, deduplicación en Redis por hash normalizado y colas de envío con retroceso exponente vía Evolution API. El sistema produce 3+ digests diarios (empleos, remates, tendencias) y supera los 87 reportes enviados sin intervención humana, corriendo 24/7 en VPS propio.",
      en: "Headless pipeline on Next.js + Celery with per-source scheduled scrapers, Redis deduplication by normalized hash, and exponential-backoff delivery queues through the Evolution API. The system produces 3+ daily digests (jobs, auctions, trends) and has sent over 87 reports with zero manual intervention, running 24/7 on its own VPS.",
    },
    stack: "Next.js · Celery · PostgreSQL · Redis · Evolution API · DataForSEO",
    tags: ["Automation", "Scraping", "WhatsApp"],
    image_url: "/images/researcher-app.webp",
    color: "#2dd4bf",
    sort_order: 0,
  },
  {
    id: -2,
    title: { es: "OpenSEO Toolkit", en: "OpenSEO Toolkit" },
    category: { es: "Web", en: "Web" },
    challenge: {
      es: "Depender de SaaS de SEO implicaba costos recurrentes, límites de cuota y cero control sobre los datos. El objetivo era un toolkit self-hosted que expusiera sus herramientas vía MCP para que asistentes de AI pudieran consultarlas directamente, con monitoreo propio y sin ceder el stack a terceros.",
      en: "Depending on SEO SaaS meant recurring costs, quota limits and zero control over the data. The goal was a self-hosted toolkit exposing its tools via MCP so AI assistants could query them directly, with own monitoring and no third-party stack.",
    },
    solution: {
      es: "Instancia auto-gestionada sobre Pterodactyl y Docker que consume la API de DataForSEO y expone las herramientas como servidor MCP, de modo que cualquier agente de IA las invoca como herramientas nativas. Health checks automáticos, monitoreo en Uptime Kuma y despliegue reproducible con un comando mantienen la instancia estable en producción.",
      en: "Self-managed instance on Pterodactyl and Docker consuming the DataForSEO API and exposing the tools as an MCP server, so any AI agent can call them as native tools. Automated health checks, Uptime Kuma monitoring and a one-command reproducible deployment keep the instance stable in production.",
    },
    stack: "Pterodactyl · Docker · DataForSEO API · MCP · Uptime Kuma",
    tags: ["SEO", "Self-hosted", "Docker"],
    image_url: "/images/openseo.webp",
    color: "#7dd3fc",
    sort_order: 1,
  },
  {
    id: -3,
    title: { es: "Colombia Aprende + AWS", en: "Colombia Aprende + AWS" },
    category: { es: "Cloud", en: "Cloud" },
    challenge: {
      es: "Entrar a la industria cloud con un estándar verificable y no solo con autodidaxia: hacer la formación dentro de un programa oficial y aplicarla de inmediato a infraestructura de proyectos reales, no a laboratorios desechables.",
      en: "Entering the cloud industry with a verifiable standard instead of pure self-teaching: taking official training and applying it immediately to real project infrastructure, not throwaway labs.",
    },
    solution: {
      es: "Formación oficial en cloud computing dentro del convenio entre la Alcaldía de Bogotá y AWS (Programa Colombia Aprende), con certificación Cloud Practitioner. Esa base sostiene hoy los despliegues reales: VPS dockerizados, pipelines con redeploy automático y la infraestructura que corre este propio portfolio en producción.",
      en: "Official cloud computing training under the Bogotá Mayor's Office and AWS agreement (Colombia Aprende program), with Cloud Practitioner certification. That foundation now backs real deployments: dockerized VPS, automated-redeploy pipelines, and the infrastructure running this very portfolio in production.",
    },
    stack: "AWS · Cloud Infrastructure",
    tags: ["AWS", "Cloud"],
    image_url: "/images/colombia-aprende.webp",
    color: "#fbbf24",
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
