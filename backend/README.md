# AI Content Guardian — Backend

Backend FastAPI pour AI Content Guardian. Voir aussi `../README.md` pour la documentation générale.

## Structure

```
backend/
  main.py                  # FastAPI app
  routers/                 # endpoints
  services/                # logique métier
  models/                  # modèles entraînés
  data/                    # labeled_data.csv
  outputs/                 # artefacts d'évaluation
  train.py                 # entraînement
```

## Installation

```bash
uv sync
```

## Variables d'environnement

```env
FRONTEND_ORIGIN=http://localhost:3000
GROQ_API_KEY=gsk_...
GROQ_MODEL=llama-3.1-8b-instant
```

## Pipeline

```bash
# Entraînement + évaluation + audit + SHAP global
uv run python train.py

# Lancer l'API
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Avertissement

Prototype éducatif. Le proxy AAE est une approximation lexicale grossière, pas un classifieur de dialecte validé. Aucune décision de modération ne doit être prise automatiquement sans supervision humaine.
