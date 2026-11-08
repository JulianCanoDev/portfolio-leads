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
    "ALTER TABLE config ADD COLUMN IF NOT EXISTS skills TEXT[] DEFAULT '{}'",
    "ALTER TABLE config ADD COLUMN IF NOT EXISTS cv_url VARCHAR(500) DEFAULT '/CV_Julian_Cano.pdf'",
    "UPDATE config SET cv_url = '/CV_Julian_Cano.pdf' WHERE cv_url IS NULL",
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
        "challenge": "Scraping de empleos y remates judiciales desde fuentes dispares (gov, portales). Deduplicación, clasificación y envío masivo diario por WhatsApp.",
        "challenge_en": "Scraping job listings and judicial auctions from disparate sources (gov sites, portals). Deduplication, classification, and daily mass delivery via WhatsApp.",
        "solution": "+87 reportes enviados, 3+ digests diarios (empleos, remates, tendencias). Automatización completa headless.",
        "solution_en": "+87 reports sent, 3+ daily digests (jobs, auctions, trends). Fully headless automation.",
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
        "challenge": "Desplegar y mantener un SEO toolkit self-hosted integrado con MCP para consultas desde el asistente AI.",
        "challenge_en": "Deploy and maintain a self-hosted SEO toolkit integrated with MCP for AI assistant queries.",
        "solution": "Instancia operativa con health checks automáticos, monitoreo vía Uptime Kuma, integración con AI vía MCP.",
        "solution_en": "Live instance with automated health checks, Uptime Kuma monitoring, AI integration via MCP.",
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
        "challenge": "Participación en el convenio Alcaldía de Bogotá y AWS para formación en tecnologías cloud.",
        "challenge_en": "Participation in the Bogotá Mayor's Office and AWS agreement for cloud technology training.",
        "solution": "Formación oficial en cloud computing. Aplicación práctica en infraestructura de proyectos reales.",
        "solution_en": "Official cloud computing training. Hands-on application in real project infrastructure.",
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
