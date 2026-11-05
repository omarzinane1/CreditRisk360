
# Environnement Python compatible avec CreditRisk360
FROM python:3.11-slim

# Configuration Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Répertoire principal du projet
WORKDIR /project

# Bibliothèque système nécessaire à certains calculs ML
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Installation des dépendances Python
COPY backend/requirements-docker.txt /project/backend/requirements-docker.txt

RUN python -m pip install --no-cache-dir \
    -r /project/backend/requirements-docker.txt

# Copie du code FastAPI
COPY backend/app /project/backend/app

# Copie du modèle E3 et de son prétraitement
COPY ml/artifacts /project/ml/artifacts
COPY ml/training /project/ml/training

# Dossier de travail de FastAPI
WORKDIR /project/backend

# Port interne du serveur
EXPOSE 8000

# Démarrage de FastAPI
CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000"]
