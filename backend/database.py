"""Capa de datos: SQLAlchemy async — engine, sesión, creación de tablas y migraciones idempotentes."""

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from config import get_settings

engine = create_async_engine(get_settings().database_url, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with SessionLocal() as session:
        yield session


MIGRATIONS = (
    "ALTER TABLE projects ADD COLUMN IF NOT EXISTS solution TEXT",
    "ALTER TABLE projects ADD COLUMN IF NOT EXISTS title_en VARCHAR(200)",
    "ALTER TABLE projects ADD COLUMN IF NOT EXISTS category_en VARCHAR(100)",
    "ALTER TABLE projects ADD COLUMN IF NOT EXISTS challenge_en TEXT",
    "ALTER TABLE projects ADD COLUMN IF NOT EXISTS solution_en TEXT",
    "ALTER TABLE projects ADD COLUMN IF NOT EXISTS color VARCHAR(7)",
    "ALTER TABLE leads ADD COLUMN IF NOT EXISTS contacted_at TIMESTAMPTZ",
    "ALTER TABLE leads ADD COLUMN IF NOT EXISTS whatsapp VARCHAR(50)",
    "ALTER TABLE config ADD COLUMN IF NOT EXISTS skills TEXT[] DEFAULT '{}'",
    "ALTER TABLE config ADD COLUMN IF NOT EXISTS cv_url VARCHAR(500) DEFAULT '/CV_Julian_Cano.pdf'",
    "UPDATE config SET cv_url = '/CV_Julian_Cano.pdf' WHERE cv_url IS NULL",
    "ALTER TABLE config ADD COLUMN IF NOT EXISTS role_title_en VARCHAR(200)",
    "ALTER TABLE config ADD COLUMN IF NOT EXISTS tagline_en TEXT",
    "ALTER TABLE config ADD COLUMN IF NOT EXISTS description TEXT",
    "ALTER TABLE config ADD COLUMN IF NOT EXISTS description_en TEXT",
    "UPDATE config SET tagline = 'Sistemas donde convergen IA, automatización y desarrollo web' WHERE tagline IS NULL OR tagline = ''",
    "UPDATE config SET tagline_en = 'Building systems where AI, automation and web converge' WHERE tagline_en IS NULL",
    "UPDATE config SET description = 'Construyo sistemas que integran inteligencia artificial, automatización y desarrollo web — de la idea a producción.' WHERE description IS NULL OR description = ''",
    "UPDATE config SET description_en = 'I build systems that integrate AI, automation and web — from idea to production.' WHERE description_en IS NULL",
)

# Backfill only on databases created before the solution refactor (they still
# carry the legacy `result` column; fresh ones never had it).
RESULT_BACKFILL = (
    "UPDATE projects SET solution = result WHERE solution IS NULL AND result IS NOT NULL"
)


SHOWCASE_PROJECTS = [
    {
        "title": "Researcher App",
        "title_en": "Researcher App",
        "category": "Automation",
        "category_en": "Automation",
        "challenge": "Rastrear vacantes y remates judiciales publicados en decenas de sitios gubernamentales y portales privados sin API, con formatos y cadencias distintas. Había que deduplicar miles de registros semanales que aparecían repetidos entre fuentes, clasificarlos por tipo y entregar un resumen diario por WhatsApp a una lista grande de destinatarios sin caer en bloqueos ni requerir curación manual.",
        "challenge_en": "Tracking job vacancies and judicial auctions published across dozens of government sites and private portals with no APIs, each with different formats and publishing rhythms. Thousands of records per week appeared duplicated across sources and needed deduplication, classification and daily delivery via WhatsApp to a large recipient list without getting blocked or requiring manual curation.",
        "solution": "Pipeline headless en Next.js + Celery con scrapers programados por fuente, deduplicación en Redis por hash normalizado y colas de envío con retroceso exponente vía Evolution API. El sistema produce 3+ digests diarios (empleos, remates, tendencias) y supera los 87 reportes enviados sin intervención humana, corriendo 24/7 en VPS propio.",
        "solution_en": "Headless pipeline on Next.js + Celery with per-source scheduled scrapers, Redis deduplication by normalized hash, and exponential-backoff delivery queues through the Evolution API. The system produces 3+ daily digests (jobs, auctions, trends) and has sent over 87 reports with zero manual intervention, running 24/7 on its own VPS.",
        "stack": "Next.js · Celery · PostgreSQL · Redis · Evolution API · DataForSEO",
        "tags": ["Automation", "Scraping", "WhatsApp"],
        "image_url": "/images/researcher-app.webp",
        "color": "#2dd4bf",
        "sort_order": 0,
    },
    {
        "title": "OpenSEO Toolkit",
        "title_en": "OpenSEO Toolkit",
        "category": "Web",
        "category_en": "Web",
        "challenge": "Depender de SaaS de SEO implicaba costos recurrentes, límites de cuota y cero control sobre los datos. El objetivo era un toolkit self-hosted que expusiera sus herramientas vía MCP para que asistentes de AI pudieran consultarlas directamente, con monitoreo propio y sin ceder el stack a terceros.",
        "challenge_en": "Depending on SEO SaaS meant recurring costs, quota limits and zero control over the data. The goal was a self-hosted toolkit exposing its tools via MCP so AI assistants could query them directly, with own monitoring and no third-party stack.",
        "solution": "Instancia auto-gestionada sobre Pterodactyl y Docker que consume la API de DataForSEO y expone las herramientas como servidor MCP, de modo que cualquier agente de IA las invoca como herramientas nativas. Health checks automáticos, monitoreo en Uptime Kuma y despliegue reproducible con un comando mantienen la instancia estable en producción.",
        "solution_en": "Self-managed instance on Pterodactyl and Docker consuming the DataForSEO API and exposing the tools as an MCP server, so any AI agent can call them as native tools. Automated health checks, Uptime Kuma monitoring and a one-command reproducible deployment keep the instance stable in production.",
        "stack": "Pterodactyl · Docker · DataForSEO API · MCP · Uptime Kuma",
        "tags": ["SEO", "Self-hosted", "Docker"],
        "image_url": "/images/openseo.webp",
        "color": "#7dd3fc",
        "sort_order": 1,
    },
    {
        "title": "Colombia Aprende + AWS",
        "title_en": "Colombia Aprende + AWS",
        "category": "Cloud",
        "category_en": "Cloud",
        "challenge": "Entrar a la industria cloud con un estándar verificable y no solo con autodidaxia: hacer la formación dentro de un programa oficial y aplicarla de inmediato a infraestructura de proyectos reales, no a laboratorios desechables.",
        "challenge_en": "Entering the cloud industry with a verifiable standard instead of pure self-teaching: taking official training and applying it immediately to real project infrastructure, not throwaway labs.",
        "solution": "Formación oficial en cloud computing dentro del convenio entre la Alcaldía de Bogotá y AWS (Programa Colombia Aprende), con certificación Cloud Practitioner. Esa base sostiene hoy los despliegues reales: VPS dockerizados, pipelines con redeploy automático y la infraestructura que corre este propio portfolio en producción.",
        "solution_en": "Official cloud computing training under the Bogotá Mayor's Office and AWS agreement (Colombia Aprende program), with Cloud Practitioner certification. That foundation now backs real deployments: dockerized VPS, automated-redeploy pipelines, and the infrastructure running this very portfolio in production.",
        "stack": "AWS · Cloud Infrastructure",
        "tags": ["AWS", "Cloud"],
        "image_url": "/images/colombia-aprende.webp",
        "color": "#fbbf24",
        "sort_order": 2,
    },
]


async def init_db():
    from models import Config, Lead, Project  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        for statement in MIGRATIONS:
            await conn.execute(text(statement))
        column_check = await conn.execute(
            text(
                "SELECT 1 FROM information_schema.columns "
                "WHERE table_name = 'projects' AND column_name = 'result'"
            )
        )
        if column_check.scalar():
            await conn.execute(text(RESULT_BACKFILL))

    # Singleton de configuración + showcase inicial: un clon nuevo arranca
    # mostrando el portfolio real de JuliXR; cada uno lo personaliza desde el dashboard.
    async with SessionLocal() as db:
        config = await db.get(Config, 1)
        if config is None:
            db.add(Config(id=1))
        projects_count = (
            await db.scalar(select(func.count()).select_from(Project))
        ) or 0
        if projects_count == 0:
            for sample in SHOWCASE_PROJECTS:
                db.add(Project(**sample))
        await db.commit()
