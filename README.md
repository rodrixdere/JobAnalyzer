# Job Offer Analyzer

Aplicación full-stack para analizar la compatibilidad entre tu perfil profesional y ofertas de trabajo usando un LLM. Subís tu CV, la app extrae tus skills y experiencia, y compara cada oferta contra tu perfil devolviendo un *match score*, las skills que cumplís y las que te faltan. Incluye un tracker tipo Kanban para gestionar tus postulaciones y un panel de administración de usuarios.

## Características

- **Parseo de CV con IA** — Subí un PDF/DOCX (o pegá el texto) y el LLM extrae nombre, título, skills, experiencia, proyectos, educación, idiomas y enlaces.
- **Análisis de compatibilidad** — Pegá el texto de una oferta y obtené `match_score` (0–100), skills requeridas, skills que coinciden, skills faltantes y un resumen.
- **Tracker de postulaciones** — Seguimiento de aplicaciones con estado, fechas (aplicación, entrevista, deadline), keywords, link y notas.
- **Autenticación** — Registro/login con JWT; cuentas que pueden pausarse.
- **Panel de admin** — Listar, crear, pausar/activar y eliminar usuarios.

## Stack

**Backend**
- FastAPI + Uvicorn
- SQLAlchemy (async) + Alembic
- PostgreSQL (asyncpg) — pensado para Supabase
- Groq SDK — modelo `llama-3.3-70b-versatile`
- JWT (python-jose) + bcrypt (passlib)
- PyMuPDF y python-docx para extraer texto de PDF/DOCX
- Pytest

**Frontend**
- React 19 + TypeScript
- Vite
- Tailwind CSS v4
- React Router v7
- lucide-react

## Estructura

```
jobanalyzer/
├── backend/
│   ├── app/
│   │   ├── api/          # Routers: auth, profile, analysis, tracker, admin
│   │   ├── core/         # Config, seguridad (JWT), dependencias, cliente Groq
│   │   ├── db/           # Engine async, sesión, base declarativa
│   │   ├── models/       # User, UserProfile, Analysis, JobApplication
│   │   ├── schemas/      # Modelos Pydantic de request/response
│   │   ├── services/     # Parseo de CV, análisis de oferta, extracción de archivos
│   │   └── main.py       # App FastAPI + CORS + routers
│   ├── alembic/          # Migraciones
│   ├── tests/            # Tests con Pytest
│   └── requirements.txt
└── frontend/
    └── src/
        ├── pages/        # Dashboard, MyProfile, JobCompatibility, JobTracker, Login, AdminPanel
        ├── components/   # Sidebar
        ├── services/     # Cliente API (fetch)
        ├── hooks/        # useAuth
        └── types/        # Tipos compartidos
```

## Requisitos

- Python 3.11+
- Node.js 18+
- PostgreSQL (o una base en Supabase)
- Una API key de [Groq](https://console.groq.com/)

## Puesta en marcha

### Backend

```bash
cd backend
python -m venv venv
source venv/Scripts/activate   # En PowerShell: venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Creá el archivo `backend/.env` a partir de `.env.example` y completá los valores:

```env
DATABASE_URL=postgresql+asyncpg://usuario:password@host:puerto/postgres
SECRET_KEY=tu_clave_secreta
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
GROQ_API_KEY=tu_groq_api_key
ALLOWED_ORIGINS=["http://localhost:5173"]
```

Aplicá las migraciones y levantá el servidor:

```bash
alembic upgrade head
uvicorn app.main:app --reload
```

La API queda en `http://localhost:8000` y la documentación interactiva en `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

El frontend corre en `http://localhost:5173`. Vite redirige las llamadas a `/api` hacia `http://localhost:8000` (ver `vite.config.ts`), así que no hace falta configurar la URL del backend.

## API

Todas las rutas (excepto `/auth/*` y `/health`) requieren el header `Authorization: Bearer <token>`.

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/auth/register` | Registrar usuario y obtener token |
| `POST` | `/auth/login` | Login y obtener token |
| `GET` | `/auth/me` | Datos del usuario autenticado |
| `POST` | `/profile/upload-cv` | Subir CV (PDF/DOCX) y parsearlo |
| `POST` | `/profile/parse-cv` | Parsear CV a partir de texto plano |
| `GET` | `/profile/` | Obtener el perfil |
| `PUT` | `/profile/` | Actualizar el perfil |
| `POST` | `/analysis/` | Analizar una oferta contra el perfil |
| `GET` | `/analysis/` | Listar análisis |
| `GET` | `/analysis/{id}` | Ver un análisis |
| `DELETE` | `/analysis/{id}` | Eliminar un análisis |
| `GET` | `/tracker/` | Listar postulaciones |
| `POST` | `/tracker/` | Crear postulación |
| `PUT` | `/tracker/{id}` | Actualizar postulación |
| `DELETE` | `/tracker/{id}` | Eliminar postulación |
| `GET` | `/admin/users` | Listar usuarios (admin) |
| `POST` | `/admin/users` | Crear usuario (admin) |
| `PUT` | `/admin/users/{id}/toggle` | Pausar/activar usuario (admin) |
| `DELETE` | `/admin/users/{id}` | Eliminar usuario (admin) |

## Tests

```bash
cd backend
pytest
```

## Notas

- El backend usa SQLAlchemy en modo async con asyncpg; `statement_cache_size=0` está fijado para ser compatible con el pooler de Supabase (PgBouncer).
- El usuario administrador no se crea desde la UI: marcá `is_admin = true` directamente en la base o creá uno desde otro admin.
- Las respuestas del LLM se esperan en JSON estricto; si el modelo devuelve algo inválido, la API responde un error claro en lugar de datos corruptos.
