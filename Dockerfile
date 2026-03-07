FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    NODE_MAJOR=20

WORKDIR /app

# Install Node.js + npm for Vite frontend build.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates gnupg \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key \
        | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_${NODE_MAJOR}.x nodistro main" \
        > /etc/apt/sources.list.d/nodesource.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install backend + frontend dependencies first for better layer caching.
COPY requirements.txt package.json ./
RUN python -m pip install --upgrade pip \
    && python -m pip install -r requirements.txt \
    && npm install

# Copy the full project and build frontend assets.
COPY . .
RUN npm run build

EXPOSE 8000
CMD ["sh", "-c", "python -m uvicorn backend_api:app --host 0.0.0.0 --port ${PORT:-8000}"]