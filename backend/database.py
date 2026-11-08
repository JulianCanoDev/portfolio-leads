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
    "ALTER TABLE leads ADD COLUMN IF NOT EXISTS contacted_at TIMESTAMPTZ",
    "ALTER TABLE config ADD COLUMN IF NOT EXISTS skills TEXT[] DEFAULT '{}'",
    "ALTER TABLE config ADD COLUMN IF NOT EXISTS cv_url VARCHAR(500) DEFAULT '/CV_Julian_Cano.pdf'",
    "UPDATE config SET cv_url = '/CV_Julian_Cano.pdf' WHERE cv_url IS NULL",
    "UPDATE projects SET solution = result WHERE solution IS NULL AND result IS NOT NULL",
)


SHOWCASE_PROJECTS = [
    {
        "title": "Researcher App",
        "category": "Automation",
        "challenge": "Scraping de empleos y remates judiciales desde fuentes dispares (gov, portales). Deduplicación, clasificación y envío masivo diario por WhatsApp.",
        "solution": "+87 reportes enviados, 3+ digests diarios (empleos, remates, tendencias). Automatización completa headless.",
        "stack": "Next.js · Celery · PostgreSQL · Redis · Evolution API · DataForSEO",
        "tags": ["Automation", "Scraping", "WhatsApp"],
        "image_url": "/images/researcher-app.webp",
        "sort_order": 0,
    },
    {
        "title": "OpenSEO Toolkit",
        "category": "Web",
        "challenge": "Desplegar y mantener un SEO toolkit self-hosted integrado con MCP para consultas desde el asistente AI.",
        "solution": "Instancia operativa con health checks automáticos, monitoreo vía Uptime Kuma, integración con AI vía MCP.",
        "stack": "Pterodactyl · Docker · DataForSEO API · MCP · Uptime Kuma",
        "tags": ["SEO", "Self-hosted", "Docker"],
        "image_url": "/images/openseo.webp",
        "sort_order": 1,
    },
    {
        "title": "Colombia Aprende + AWS",
        "category": "Cloud",
        "challenge": "Participación en el convenio Alcaldía de Bogotá y AWS para formación en tecnologías cloud.",
        "solution": "Formación oficial en cloud computing. Aplicación práctica en infraestructura de proyectos reales.",
        "stack": "AWS · Cloud Infrastructure",
        "tags": ["AWS", "Cloud"],
        "image_url": "/images/colombia-aprende.webp",
        "sort_order": 2,
    },
]


async def init_db():
    from models import Config, Lead, Project  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        for statement in MIGRATIONS:
            await conn.execute(text(statement))

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
