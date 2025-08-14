# DraftDiff ML Workspace

This workspace is for data ingestion, feature engineering, training, evaluation, and model packaging for runtime inference.

## Suggested stack

- Python 3.11
- Notebooks via Jupyter / Quarto
- DataFrames: Polars or pandas
- Modeling: scikit-learn, LightGBM, optional PyTorch
- Experiment tracking: Weights & Biases (optional)

## Layout

- `data/`: raw and processed data (gitignored)
- `notebooks/`: exploratory and report notebooks
- `src/`: reusable pipelines and training code
- `artifacts/`: exported models, metrics, plots

## Packaging models

Export models as Joblib to `artifacts/` and copy the chosen production model to `backend/models/model.joblib` for serving.
