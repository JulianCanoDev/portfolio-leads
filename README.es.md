# JuliXR Portfolio

Portfolio personal + dashboard de leads con FastAPI, Astro y PostgreSQL.
Hecho para aprender, forkear y personalizar.

[Español](README.es.md) · **English** → [README.md](README.md)

> **El template se clona con el portfolio real de JuliXR como showcase** — nombre, rol, colores, redes y proyectos de ejemplo. Todo se cambia desde `http://localhost:3000/dashboard` sin tocar código.
>
> 👉 Versión original en vivo: [portfolio.julixr.com](https://portfolio.julixr.com) — JuliXR Portfolio by Julian Cano, Full Stack & AI Developer.

## Stack

- **Frontend:** Astro 7.4 (SSR con `@astrojs/node`)
- **Backend:** FastAPI + PostgreSQL (SQLAlchemy async)
- **Infra:** Docker Compose + Nginx

## Quick start

```bash
cp .env.example .env   # Editar con tus datos
docker compose up -d --build
```

- Portfolio: `http://localhost:3000`
- Dashboard: `http://localhost:3000/dashboard` (login con `ADMIN_USER` / `ADMIN_PASS` del `.env`)

Desde el panel admin, **sin tocar código**: nombre, rol, tagline, colores, skills y redes sociales (**Settings**), proyectos con imágenes, solución y drag & drop (**Proyectos**), redimensionado automático de imágenes 800×500 WebP (**Imágenes**), y los leads del formulario (**Leads**). El portfolio público refleja los cambios al instante.

Atajos: `make up` · `make down` · `make logs` · `make reset`

## Estructura

```
portfolio/
├── src/                  # Astro frontend (portfolio + dashboard)
│   ├── components/       # Hero, Projects, Skills, Contact, Nav, DashboardLayout
│   ├── layouts/          # Layout.astro
│   ├── pages/            # index.astro, dashboard/ (login, leads, projects, settings, upload)
│   ├── lib/              # api.ts + cms.ts (SSR → FastAPI, con defaults de fallback)
│   └── styles/           # colors.css (tokens) + global.css
├── backend/              # FastAPI
│   ├── main.py           # Rutas y auth: leads, settings, projects, upload
│   ├── config.py         # Settings desde variables de entorno
│   ├── database.py       # SQLAlchemy async + seed inicial
│   ├── models.py         # Lead, Config, Project
│   └── image_utils.py    # Crop 16:10 → 800×500 → WebP
├── uploads/              # Imágenes subidas (volumen compartido con nginx)
├── nginx.conf            # Reverse proxy: /api/* y /uploads/* → backend, /* → frontend
├── docker-compose.yml    # postgres + backend + frontend + nginx
├── .env.example
├── Makefile
└── LICENSE
```

## API

| Método | Path | Auth | Descripción |
|--------|------|------|-------------|
| POST | `/api/contact` | — | Crea un lead `{ name, email, message }` |
| GET | `/api/health` | — | `{ status: "ok", total: N }` |
| GET | `/api/settings` | — | Configuración del sitio (CMS) |
| GET | `/api/projects` | — | Proyectos ordenados por `sort_order` |
| POST | `/api/auth/login` | — | `{ user, pass }` → JWT (cookie httpOnly + token) |
| POST | `/api/projects` | JWT | Crea proyecto → `{ id, title, image_url, status }` |
| PATCH | `/api/projects/{id}` | JWT | Actualización parcial (image_url, tags, …) |
| PATCH | `/api/projects/reorder` | JWT | `{ order: [ids] }` — drag & drop |
| DELETE | `/api/projects/{id}` | JWT | Borra proyecto y su imagen asociada |
| POST | `/api/projects/generate-upload-url` | JWT | URL firmada (15 min) para subir imágenes sin sesión |
| POST | `/api/upload` | JWT | Multipart → recorta 16:10 → 800×500 WebP |
| POST | `/api/upload/{token}` | URL firmada | Subida de imagen para agentes externos |
| GET | `/api/leads` | JWT | `?page` `?status` `?search` → paginado (20) |
| GET | `/api/leads/{id}` | JWT | Lead completo |
| PATCH | `/api/leads/{id}` | JWT | `{ status: "contacted" }` |
| GET | `/api/stats` | JWT | `{ total, new, contacted, today }` |

Los endpoints autenticados aceptan la cookie del dashboard o `Authorization: Bearer <token>` — pensados para que un agente externo (OpenClaw/LLM) los consuma. El backend nunca llama APIs de generación de imágenes: el agente genera la imagen con sus propias herramientas y la sube por URL firmada o multipart.

## Customización rápida

1. Editar `src/pages/index.astro` y `src/content/projects/*.md` → tu info y proyectos
2. Editar `.env` → tus credenciales
3. Opcional: cambiar colores en `src/styles/colors.css` (`:root { --accent: #6d28d9, ... }`)

## Variables fácil de editar

- **Astro:** `src/styles/colors.css` → tokens `:root`
- **Backend:** `backend/config.py` → Settings desde `.env`
- **Docker:** `docker-compose.yml` → puertos, volúmenes

## Licencia

MIT — ver [LICENSE](LICENSE).
