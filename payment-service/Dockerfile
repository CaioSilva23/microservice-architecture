FROM python:3.9-slim

WORKDIR /app

# Configurar variáveis de ambiente para logs
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8
ENV PYTHONPATH=/app

# Copiar requirements e instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . /app

CMD ["python", "-u", "main.py"]