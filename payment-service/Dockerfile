FROM python:3.9-slim

WORKDIR /app

# Configurar variáveis de ambiente para logs
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8

COPY . /app

# Copiar requirements e instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-u", "consumer.py"]