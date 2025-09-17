#!/bin/bash

echo "🔄 Reiniciando Grafana para aplicar configurações..."

# Parar o Grafana
echo "⏹️ Parando container do Grafana..."
docker-compose stop grafana

# Remover container antigo para garantir nova configuração
echo "🗑️ Removendo container antigo..."
docker-compose rm -f grafana

# Remover volume para garantir configuração limpa (opcional)
read -p "Deseja remover o volume do Grafana (perderá configurações personalizadas)? [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️ Removendo volume do Grafana..."
    docker volume rm projeto-tcc_grafana-storage 2>/dev/null || echo "Volume não existe ou já foi removido"
fi

# Iniciar Grafana novamente
echo "🚀 Iniciando Grafana..."
docker-compose up -d grafana

echo "⏳ Aguardando Grafana estar pronto..."
sleep 10

# Verificar se está respondendo
max_attempts=30
attempt=1

while [ $attempt -le $max_attempts ]; do
    if curl -s "http://localhost:3000/api/health" > /dev/null 2>&1; then
        echo "✅ Grafana está respondendo!"
        break
    fi
    echo "⏳ Tentativa $attempt/$max_attempts..."
    sleep 2
    ((attempt++))
done

if [ $attempt -gt $max_attempts ]; then
    echo "❌ Grafana não respondeu após $max_attempts tentativas"
    echo "📋 Verifique os logs: docker-compose logs grafana"
    exit 1
fi

echo ""
echo "🎯 Grafana configurado!"
echo "📊 Acesse: http://localhost:3000"
echo "🔑 Login: admin / admin"
echo "📈 Dashboard: 'TCC Project - Microservices Monitoring'"
echo ""
echo "💡 Se o dashboard não aparecer:"
echo "   1. Vá em 'Dashboards' → 'Browse'"
echo "   2. Procure por 'TCC Project - Microservices Monitoring'"
echo "   3. Ou importe manualmente o arquivo JSON"
