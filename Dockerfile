FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y postgresql-client && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*


# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code
COPY . .

# Environment
ENV PYTHONUNBUFFERED=1

# Run bot
CMD ["python", "-m", "src.main"]