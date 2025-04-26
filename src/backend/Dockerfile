# 🧠 Use a minimal Python 3.11 base image
FROM python:3.11-slim

# 👇 Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 🛠️ Install minimal system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 🐍 Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# 📦 Copy and install app dependencies (except torch for now)
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
# torch CPU
# ----------------------
RUN pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# sentence transformers deps
# ----------------------
RUN pip3 install keybert scikit-learn transformers pydantic fastapi qdrant_client uvicorn pandas python-multipart prometheus_fastapi_instrumentator 

# install sentence transformers no deps
# ----------------------
RUN pip3 install --no-deps sentence-transformers==4.1.0

# 🧠 Install latest PyTorch (CPU only)
# RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# 📁 Copy application code
COPY . .

# 🚀 Run the FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
