FROM python:3.12-slim

WORKDIR /app

# 1) сначала зависимости (лучше кешируется)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2) потом код
COPY main.py .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
