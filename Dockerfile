FROM python:3.10-slim

# Install system dependencies including libX11
RUN apt-get update && apt-get install -y \
    libx11-6 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    cmake \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
