# ai-content-guardian

Assistant de modération de contenu avec audit de biais et explicabilité.

## Structure

```
ai-content-guardian/
├── backend/          # API FastAPI + modèles ML
└── frontend/         # Interface Next.js + TypeScript + Tailwind CSS
```

## Backend

API REST construite avec FastAPI. Elle expose :

- `POST /analyze-comment`
- `POST /analyze-comments`
- `POST /generate-comments`
- `GET /metrics`
- `GET /bias-audit`
- `GET /model-info`

### Installation

```bash
cd backend
uv sync
```

### Variables d’environnement

Créez un fichier `backend/.env` :

```env
FRONTEND_ORIGIN=http://localhost:3000
GROQ_API_KEY=gsk_...
GROQ_MODEL=llama-3.1-8b-instant
```

### Lancer l’API

```bash
cd backend
uv run python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Frontend

Interface utilisateur en français, light mode only, basée sur Next.js, TypeScript, Tailwind CSS, shadcn/ui et Recharts.

### Installation

```bash
cd frontend
pnpm install
```

### Variables d’environnement

Créez un fichier `frontend/.env.local` :

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Lancer le frontend

```bash
cd frontend
pnpm dev
```

## Organisation des rôles

Voir `backend/docs/roles-equipe.md`.

## Notes

- Tous les textes affichés à l’utilisateur sont en français.
- Aucun emoji dans l’interface ; les indicateurs visuels utilisent `lucide-react`.
- Le modèle ne décide jamais seul d’une sanction : un modérateur humain valide chaque action.
