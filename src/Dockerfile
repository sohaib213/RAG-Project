FROM python:3.12-slim

# Prevent Python from writing .pyc files & enable logs immediately
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies (important for PyMuPDF, torch, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .

# Upgrade pip
RUN pip install --upgrade pip

# Install PyTorch CPU version (compatible with sentence-transformers)
RUN pip install --no-cache-dir torch==2.2.2+cpu \
    -f https://download.pytorch.org/whl/torch_stable.html

# Install remaining dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

EXPOSE 5000

# Start FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]