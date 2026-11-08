# JuliXR Portfolio

Personal portfolio + leads dashboard with FastAPI, Astro and PostgreSQL.
Built to learn, fork and customize.

**English** · [Español](README.es.md)

> **This template ships with JuliXR's real portfolio as a showcase** — name, role, colors, socials and sample projects. Everything is editable from `http://localhost:3000/dashboard` without touching code.
>
> 👉 Live original: [portfolio.julixr.com](https://portfolio.julixr.com) — JuliXR Portfolio by Julian Cano, Full Stack & AI Developer.

## Features

- **CMS dashboard** — identity, role, tagline, accent & secondary colors (with live preview), social links, skills (tag chips) and CV upload (PDF)
- **Projects CRUD** — create, edit, delete, drag & drop reorder, tag chips and automatic image processing (center-crop 16:10 → 800×500 WebP q85)
- **Leads dashboard** — contact form submissions with status filters, search, pagination and mark-as-contacted
- **i18n ES/EN** — browser language detection (SSR, no flash) + ES/EN toggle in the nav
- **Agent-friendly API** — JWT auth (cookie or Bearer), signed temporary upload URLs for external LLM agents (OpenClaw)
- **One-command deploy** — `docker compose up -d --build`

## Stack

- **Frontend:** Astro 7.4 (SSR with `@astrojs/node`)
- **Backend:** FastAPI + PostgreSQL (SQLAlchemy async)
- **Infra:** Docker Compose + Nginx

## Quick start

```bash
cp .env.example .env   # Edit with your data
docker compose up -d --build
```

- Portfolio: `http://localhost:3000`
- Dashboard: `http://localhost:3000/dashboard` (log in with `ADMIN_USER` / `ADMIN_PASS` from `.env`)

Shortcuts: `make up` · `make down` · `make logs` · `make reset`

## Structure

```
portfolio/
├── src/                  # Astro frontend (portfolio + dashboard)
│   ├── components/       # Hero, Projects, Skills, CV, Contact, Nav, DashboardLayout
│   ├── i18n/             # es.json / en.json dictionaries + helpers
│   ├── layouts/          # Layout.astro
│   ├── pages/            # index.astro, dashboard/ (login, leads, projects, settings)
│   ├── lib/              # api.ts + cms.ts (SSR → FastAPI, with inline fallbacks)
│   ├── middleware.ts     # Locale resolution (cookie → Accept-Language → es)
│   └── styles/           # colors.css (design tokens) + global.css
├── backend/              # FastAPI
│   ├── main.py           # Routes & auth: leads, settings, projects, uploads
│   ├── config.py         # Settings from environment variables
│   ├── database.py       # SQLAlchemy async + idempotent migrations + showcase seed
│   ├── models.py         # Lead, Config, Project
│   └── image_utils.py    # Crop 16:10 → 800×500 → WebP
├── public/               # Static assets (favicon, covers, default CV)
├── nginx.conf            # Reverse proxy: /api/* and /uploads/* → backend, /* → frontend
├── docker-compose.yml    # postgres + backend + frontend + nginx
├── .env.example
├── Makefile
└── LICENSE
```

## API

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/contact` | — | Create a lead `{ name, email, message }` |
| GET | `/api/health` | — | `{ status: "ok", total: N }` |
| GET | `/api/settings` | — | Site configuration (CMS) |
| GET | `/api/projects` | — | Projects ordered by `sort_order` |
| POST | `/api/auth/login` | — | `{ user, pass }` → JWT (httpOnly cookie + token) |
| PUT | `/api/settings` | JWT | Update configuration (colors, socials, skills, CV URL…) |
| POST | `/api/settings/reset-defaults` | JWT | Restore default configuration |
| POST | `/api/projects` | JWT | Create project → `{ id, title, image_url, status }` |
| PATCH | `/api/projects/{id}` | JWT | Partial update (image_url, tags, …) |
| PATCH | `/api/projects/reorder` | JWT | `{ order: [ids] }` — drag & drop |
| DELETE | `/api/projects/{id}` | JWT | Delete project and its uploaded image |
| POST | `/api/projects/generate-upload-url` | JWT | Signed URL (15 min) to upload images without a session |
| POST | `/api/upload` | JWT | Multipart → center-crop 16:10 → 800×500 WebP |
| POST | `/api/upload/{token}` | Signed URL | Image upload for external agents |
| POST | `/api/upload/cv` | JWT | Upload PDF → replaces the CV and updates config |
| GET | `/api/leads` | JWT | `?page` `?status` `?search` → paginated (20) |
| GET | `/api/leads/{id}` | JWT | Full lead |
| PATCH | `/api/leads/{id}` | JWT | `{ status: "contacted" }` |
| GET | `/api/stats` | JWT | `{ total, new, contacted, today }` |

Authenticated endpoints accept the dashboard cookie or `Authorization: Bearer <token>`, so external agents (OpenClaw or any LLM) can consume them. The backend never calls image-generation APIs: the agent generates images with its own tools and uploads them via the signed URL or multipart.

### Agent flow (example)

1. `POST /api/projects` with `image_url: null` → project created
2. Agent generates an 800×500 image with its own tools
3. `POST /api/projects/generate-upload-url` → signed URL (15 min)
4. `POST` the image to the signed URL → public URL returned
5. `PATCH /api/projects/{id}` with `{ "image_url": "..." }` → done

## Customization

1. `/dashboard/settings` — name, role, tagline, colors, socials, skills, CV
2. `/dashboard/projects` — projects, images, tags and ordering (drag & drop)
3. Optionally: design tokens in `src/styles/colors.css` (`:root { --accent: #6d28d9, … }`)
4. Docker: ports and volumes in `docker-compose.yml`

The public portfolio reflects dashboard changes instantly. Project content can be localized: the three showcase projects carry ES/EN translations in `src/i18n/*.json`, applied while the CMS field still matches the Spanish canonical text — custom edits always win.

## License

MIT — see [LICENSE](LICENSE).
