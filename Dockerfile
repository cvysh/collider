# The deployed API serves precomputed artifacts. It imports only the standard
# library, Pydantic and FastAPI, so this image installs the project without its
# `pipeline` extra: uproot, matplotlib, scikit-learn and XGBoost would add
# roughly a gigabyte for code that never executes in production.

FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Dependencies first, so editing source does not reinstall them.
COPY pyproject.toml ./
COPY src/ src/
RUN pip install --no-cache-dir .

# The artifacts the API reads. Paths match the defaults in collider.api.app and
# can be overridden with COLLIDER_EVENTS / COLLIDER_DISTRIBUTIONS / COLLIDER_REGISTRY.
COPY data/processed/events/ data/processed/events/
COPY data/processed/distributions/ data/processed/distributions/
COPY ml/models/registry.json ml/models/

EXPOSE 8123

# Railway (and most hosts) inject PORT; 8123 is the local default.
CMD ["sh", "-c", "uvicorn collider.api.app:app --host 0.0.0.0 --port ${PORT:-8123}"]
