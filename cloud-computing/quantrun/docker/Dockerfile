FROM python:3.11-slim

WORKDIR /app
COPY models ./models

# no heavy deps needed for this demo

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# default entrypoint runs the model selected by MODEL env var
CMD ["python", "models/var_mc/run.py"]
