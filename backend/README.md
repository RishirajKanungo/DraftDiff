# DraftDiff Backend

Tech: FastAPI, Pydantic v2, Uvicorn, SQLAlchemy, Redis, scikit-learn/LightGBM.

## Local development

- Create `.env` from `.env.example`.
- Install Poetry, then install deps:

```bash
poetry install
```

- Start API:

```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Health check: `GET http://localhost:8000/api/v1/health`
- Predict: `POST http://localhost:8000/api/v1/predict`

## Structure

- `app/main.py`: FastAPI app entrypoint
- `app/api/routes/predictions.py`: prediction endpoint
- `app/services/prediction_service.py`: model loading and inference logic
- `app/core/config.py`: settings via environment
- `models/`: persisted models (ignored in VCS)
