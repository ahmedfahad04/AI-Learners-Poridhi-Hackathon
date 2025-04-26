# 🧠 Use an official PyTorch image with Python 3.11
FROM pytorch/pytorch:2.7.0-cuda11.8-cudnn9-runtime as base

# 👇 Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 🐍 Upgrade pip and install extra system tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    git gcc curl \
    && rm -rf /var/lib/apt/lists/*

# 📦 Install dependencies using requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 🧪 Optional: Separate additional installs for caching benefit
# RUN pip install --no-cache-dir fastapi uvicorn pydantic pandas python-multipart prometheus_fastapi_instrumentator

# 📁 Copy your full app
COPY . .

# 🚀 Launch the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
