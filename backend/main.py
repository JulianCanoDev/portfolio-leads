"""API del portfolio: auth JWT, leads, settings (CMS) y proyectos (CRUD + imágenes)."""

import hmac
import math
import mimetypes
import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, FastAPI, HTTPException, Request, Response, UploadFile
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
from database import get_db, init_db
from image_utils import InvalidImage, process_upload
from models import Config, Lead, Project

settings = get_settings()
JWT_ALGORITHM = "HS256"
COOKIE_NAME = "julixr_token"
PAGE_SIZE = 20
HEX_COLOR = r"^#[0-9a-fA-F]{6}$"


# --------------------------------------------------------------------------
# Schemas
# --------------------------------------------------------------------------
class ContactIn(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    message: str = Field(min_length=1, max_length=5000)


class ContactOut(BaseModel):
    id: int
    status: str = "ok"


class LoginIn(BaseModel):
    user: str = Field(min_length=1, max_length=200)
    pass_: str = Field(alias="pass", min_length=1, max_length=200)

    model_config = {"populate_by_name": True}


class LoginOut(BaseModel):
    token: str
    expires_in: int


class LeadOut(BaseModel):
    id: int
    name: str
    email: str
    message: str
    status: str
    contacted_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class LeadsPage(BaseModel):
    items: list[LeadOut]
    page: int
    pages: int
    total: int


class StatusIn(BaseModel):
    status: str = Field(pattern="^(new|contacted)$")


class StatsOut(BaseModel):
    total: int
    new: int
    contacted: int
    today: int


class SettingsOut(BaseModel):
    name: str
    role_title: str
    tagline: str
    accent_color: str
    secondary_color: str
    linkedin_url: str
    github_url: str
    whatsapp_phone: str
    cv_url: str
    skills: list[str]
    updated_at: datetime

    model_config = {"from_attributes": True}


class SettingsIn(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    role_title: str | None = Field(default=None, min_length=1, max_length=200)
    tagline: str | None = Field(default=None, max_length=1000)
    accent_color: str | None = Field(default=None, pattern=HEX_COLOR)
    secondary_color: str | None = Field(default=None, pattern=HEX_COLOR)
    linkedin_url: str | None = Field(default=None, max_length=255)
    github_url: str | None = Field(default=None, max_length=255)
    whatsapp_phone: str | None = Field(default=None, max_length=50)
    cv_url: str | None = Field(default=None, max_length=500)
    skills: list[str] | None = Field(default=None, max_length=50)


class ProjectIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    category: str = Field(default="Web", max_length=100)
    challenge: str | None = Field(default=None, max_length=5000)
    solution: str | None = Field(default=None, max_length=5000)
    stack: str | None = Field(default=None, max_length=2000)
    tags: list[str] = Field(default_factory=list, max_length=20)
    image_url: str | None = Field(default=None, max_length=500)
    sort_order: int | None = None


class ProjectCreateOut(BaseModel):
    id: int
    title: str
    image_url: str | None
    status: str


class ProjectPatchIn(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    category: str | None = Field(default=None, min_length=1, max_length=100)
    challenge: str | None = Field(default=None, max_length=5000)
    solution: str | None = Field(default=None, max_length=5000)
    stack: str | None = Field(default=None, max_length=2000)
    tags: list[str] | None = Field(default=None, max_length=20)
    image_url: str | None = Field(default=None, max_length=500)
    sort_order: int | None = None


class ProjectOut(BaseModel):
    id: int
    title: str
    category: str
    challenge: str | None
    solution: str | None
    stack: str | None
    tags: list[str]
    image_url: str | None
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ReorderIn(BaseModel):
    order: list[int] = Field(min_length=1, max_length=200)


class UploadOut(BaseModel):
    url: str


class UploadUrlOut(BaseModel):
    upload_url: str
    expires_in: int


# --------------------------------------------------------------------------
# Auth: JWT en cookie httpOnly (dashboard) o header Bearer (agentes)
# --------------------------------------------------------------------------
def make_token(user: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user,
        "iat": now,
        "exp": now + timedelta(hours=settings.jwt_ttl_hours),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=JWT_ALGORITHM)


async def require_admin(request: Request) -> str:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        auth = request.headers.get("authorization", "")
        if auth.lower().startswith("bearer "):
            token = auth[7:].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if payload.get("sub") != settings.admin_user:
        raise HTTPException(status_code=401, detail="Invalid token subject")
    return payload["sub"]


async def get_config_row(db: AsyncSession) -> Config:
    config = await db.get(Config, 1)
    if config is None:
        config = Config(id=1)
        db.add(config)
        await db.commit()
        await db.refresh(config)
    return config


# --------------------------------------------------------------------------
# App
# --------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(_: FastAPI):
    os.makedirs(get_settings().upload_dir, exist_ok=True)
    await init_db()
    yield


app = FastAPI(title="JuliXR Portfolio API", lifespan=lifespan)
mimetypes.add_type("image/webp", ".webp")
app.mount(
    "/uploads",
    StaticFiles(directory=get_settings().upload_dir, check_dir=False),
    name="uploads",
)


# ---------- Public ----------
@app.get("/api/health")
async def health(db: AsyncSession = Depends(get_db)):
    total = (await db.scalar(select(func.count()).select_from(Lead))) or 0
    return {"status": "ok", "total": total}


@app.post("/api/contact", response_model=ContactOut, status_code=201)
async def create_lead(data: ContactIn, db: AsyncSession = Depends(get_db)):
    lead = Lead(name=data.name.strip(), email=str(data.email), message=data.message.strip())
    db.add(lead)
    await db.commit()
    return ContactOut(id=lead.id)


# ---------- Auth ----------
@app.post("/api/auth/login", response_model=LoginOut)
async def login(data: LoginIn, response: Response):
    user_ok = hmac.compare_digest(data.user, settings.admin_user)
    pass_ok = hmac.compare_digest(data.pass_, settings.admin_pass)
    if not (user_ok and pass_ok):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
    token = make_token(data.user)
    response.set_cookie(
        COOKIE_NAME,
        token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=settings.jwt_ttl_hours * 3600,
        path="/",
    )
    return LoginOut(token=token, expires_in=settings.jwt_ttl_hours * 3600)


@app.post("/api/auth/logout")
async def logout(response: Response):
    response.delete_cookie(COOKIE_NAME, path="/")
    return {"ok": True}


# ---------- Leads ----------
@app.get("/api/leads", response_model=LeadsPage, dependencies=[Depends(require_admin)])
async def list_leads(
    page: int = 1,
    status: str | None = None,
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    page = max(1, page)
    query = select(Lead).order_by(Lead.created_at.desc(), Lead.id.desc())
    count_query = select(func.count()).select_from(Lead)

    if status in ("new", "contacted"):
        query = query.where(Lead.status == status)
        count_query = count_query.where(Lead.status == status)
    if search and search.strip():
        like = f"%{search.strip()}%"
        match = Lead.name.ilike(like) | Lead.email.ilike(like) | Lead.message.ilike(like)
        query = query.where(match)
        count_query = count_query.where(match)

    total = (await db.scalar(count_query)) or 0
    pages = max(1, math.ceil(total / PAGE_SIZE))
    leads = (await db.scalars(query.limit(PAGE_SIZE).offset((page - 1) * PAGE_SIZE))).all()

    return LeadsPage(
        items=[LeadOut.model_validate(lead) for lead in leads],
        page=page,
        pages=pages,
        total=total,
    )


@app.get("/api/leads/{lead_id}", response_model=LeadOut, dependencies=[Depends(require_admin)])
async def get_lead(lead_id: int, db: AsyncSession = Depends(get_db)):
    lead = await db.get(Lead, lead_id)
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@app.patch("/api/leads/{lead_id}", response_model=LeadOut, dependencies=[Depends(require_admin)])
async def set_lead_status(lead_id: int, data: StatusIn, db: AsyncSession = Depends(get_db)):
    lead = await db.get(Lead, lead_id)
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    lead.status = data.status
    lead.contacted_at = datetime.now(timezone.utc) if data.status == "contacted" else None
    await db.commit()
    await db.refresh(lead)
    return lead


# ---------- Stats ----------
@app.get("/api/stats", response_model=StatsOut, dependencies=[Depends(require_admin)])
async def stats(db: AsyncSession = Depends(get_db)):
    async def count_where(*conditions) -> int:
        q = select(func.count()).select_from(Lead)
        for condition in conditions:
            q = q.where(condition)
        return (await db.scalar(q)) or 0

    return StatsOut(
        total=await count_where(),
        new=await count_where(Lead.status == "new"),
        contacted=await count_where(Lead.status == "contacted"),
        today=await count_where(Lead.created_at >= func.date_trunc("day", func.now())),
    )


# ---------- Settings (CMS) — lectura pública, escritura autenticada ----------
@app.get("/api/settings", response_model=SettingsOut)
async def get_settings_row(db: AsyncSession = Depends(get_db)):
    return await get_config_row(db)


@app.put("/api/settings", response_model=SettingsOut, dependencies=[Depends(require_admin)])
async def update_settings(data: SettingsIn, db: AsyncSession = Depends(get_db)):
    config = await get_config_row(db)
    changes = data.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(config, field, value)
    await db.commit()
    await db.refresh(config)
    return config


@app.post(
    "/api/settings/reset-defaults",
    response_model=SettingsOut,
    dependencies=[Depends(require_admin)],
)
async def reset_settings(db: AsyncSession = Depends(get_db)):
    config = await get_config_row(db)
    for column in Config.__table__.columns:
        if column.name in ("id", "updated_at"):
            continue
        setattr(config, column.name, column.default.arg if column.default else None)
    await db.commit()
    await db.refresh(config)
    return config


# ---------- Projects (CMS) — lectura pública, escritura autenticada ----------
@app.get("/api/projects", response_model=list[ProjectOut])
async def list_projects(db: AsyncSession = Depends(get_db)):
    projects = (
        await db.scalars(select(Project).order_by(Project.sort_order, Project.id))
    ).all()
    return [ProjectOut.model_validate(project) for project in projects]


@app.get("/api/projects/{project_id}", response_model=ProjectOut)
async def get_project(project_id: int, db: AsyncSession = Depends(get_db)):
    project = await db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.post(
    "/api/projects",
    response_model=ProjectCreateOut,
    status_code=201,
    dependencies=[Depends(require_admin)],
)
async def create_project(data: ProjectIn, db: AsyncSession = Depends(get_db)):
    max_order = (await db.scalar(select(func.max(Project.sort_order)))) or 0
    project = Project(
        title=data.title.strip(),
        category=data.category.strip() or "Web",
        challenge=data.challenge,
        solution=data.solution,
        stack=data.stack,
        tags=[t.strip() for t in data.tags if t.strip()],
        image_url=data.image_url,
        sort_order=data.sort_order if data.sort_order is not None else max_order + 1,
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return ProjectCreateOut(
        id=project.id,
        title=project.title,
        image_url=project.image_url,
        status="created_with_image" if project.image_url else "created_no_image",
    )


@app.put(
    "/api/projects/{project_id}",
    response_model=ProjectOut,
    dependencies=[Depends(require_admin)],
)
async def update_project(project_id: int, data: ProjectIn, db: AsyncSession = Depends(get_db)):
    project = await db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    project.title = data.title.strip()
    project.category = data.category.strip() or "Web"
    project.challenge = data.challenge
    project.solution = data.solution
    project.stack = data.stack
    project.tags = [t.strip() for t in data.tags if t.strip()]
    project.image_url = data.image_url
    await db.commit()
    await db.refresh(project)
    return project


@app.patch(
    "/api/projects/reorder",
    response_model=list[ProjectOut],
    dependencies=[Depends(require_admin)],
)
async def reorder_projects(data: ReorderIn, db: AsyncSession = Depends(get_db)):
    for index, project_id in enumerate(data.order):
        project = await db.get(Project, project_id)
        if project is not None:
            project.sort_order = index
    await db.commit()
    projects = (
        await db.scalars(select(Project).order_by(Project.sort_order, Project.id))
    ).all()
    return [ProjectOut.model_validate(project) for project in projects]


@app.patch(
    "/api/projects/{project_id}",
    response_model=ProjectOut,
    dependencies=[Depends(require_admin)],
)
async def patch_project(project_id: int, data: ProjectPatchIn, db: AsyncSession = Depends(get_db)):
    project = await db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    changes = data.model_dump(exclude_unset=True)
    if "title" in changes and changes["title"]:
        project.title = changes["title"].strip()
    if "category" in changes and changes["category"]:
        project.category = changes["category"].strip()
    if "tags" in changes and changes["tags"] is not None:
        project.tags = [t.strip() for t in changes["tags"] if t.strip()]
    for field in ("challenge", "solution", "stack", "image_url", "sort_order"):
        if field in changes:
            setattr(project, field, changes[field])
    await db.commit()
    await db.refresh(project)
    return project


@app.delete("/api/projects/{project_id}", dependencies=[Depends(require_admin)])
async def delete_project(project_id: int, db: AsyncSession = Depends(get_db)):
    project = await db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.image_url and project.image_url.startswith("/uploads/"):
        filename = os.path.basename(project.image_url)
        path = os.path.join(settings.upload_dir, filename)
        if os.path.isfile(path):
            os.remove(path)
    await db.delete(project)
    await db.commit()
    return {"ok": True}


# ---------- Upload ----------
UPLOAD_URL_TTL_SECONDS = 900


async def _process_upload(file: UploadFile) -> str:
    content_type = file.content_type or ""
    file_bytes = await file.read()
    try:
        return process_upload(file_bytes, content_type)
    except InvalidImage as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@app.post("/api/upload", response_model=UploadOut, dependencies=[Depends(require_admin)])
async def upload_image(file: UploadFile):
    return UploadOut(url=await _process_upload(file))


MAX_CV_BYTES = 10 * 1024 * 1024


@app.post("/api/upload/cv", dependencies=[Depends(require_admin)])
async def upload_cv(file: UploadFile, db: AsyncSession = Depends(get_db)):
    """Reemplaza el CV: guarda uploads/cv.pdf y actualiza config.cv_url."""
    content_type = (file.content_type or "").lower()
    filename = (file.filename or "").lower()
    if content_type != "application/pdf" and not filename.endswith(".pdf"):
        raise HTTPException(status_code=422, detail="Solo se aceptan archivos PDF")
    data = await file.read()
    if len(data) > MAX_CV_BYTES:
        raise HTTPException(status_code=422, detail="El PDF supera los 10 MB")
    if not data.startswith(b"%PDF"):
        raise HTTPException(status_code=422, detail="El archivo no parece un PDF valido")

    os.makedirs(get_settings().upload_dir, exist_ok=True)
    with open(os.path.join(get_settings().upload_dir, "cv.pdf"), "wb") as target:
        target.write(data)

    config = await get_config_row(db)
    config.cv_url = "/uploads/cv.pdf"
    await db.commit()
    return {"url": "/uploads/cv.pdf", "filename": file.filename, "size": len(data)}


@app.post(
    "/api/projects/generate-upload-url",
    response_model=UploadUrlOut,
    dependencies=[Depends(require_admin)],
)
async def generate_upload_url():
    """URL firmada y temporal para que un agente externo suba la imagen sin sesión."""
    now = datetime.now(timezone.utc)
    token = jwt.encode(
        {"scope": "upload", "exp": now + timedelta(seconds=UPLOAD_URL_TTL_SECONDS)},
        settings.jwt_secret,
        algorithm=JWT_ALGORITHM,
    )
    return UploadUrlOut(upload_url=f"/api/upload/{token}", expires_in=UPLOAD_URL_TTL_SECONDS)


@app.post("/api/upload/{token}", response_model=UploadOut)
async def upload_image_signed(token: str, file: UploadFile):
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired upload URL")
    if payload.get("scope") != "upload":
        raise HTTPException(status_code=401, detail="Invalid upload URL")
    return UploadOut(url=await _process_upload(file))
