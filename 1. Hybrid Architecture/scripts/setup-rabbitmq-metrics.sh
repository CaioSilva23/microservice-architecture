#!/bin/bash

# Script para configurar métricas do RabbitMQ
echo "🐰 Configurando métricas do RabbitMQ..."

# Aguardar o RabbitMQ estar pronto
echo "⏳ Aguardando RabbitMQ estar pronto..."
sleep 10

# Habilitar plugins do Prometheus
echo "🔌 Habilitando plugins do Prometheus..."
docker exec tcc-rabbitmq rabbitmq-plugins enable rabbitmq_prometheus
docker exec tcc-rabbitmq rabbitmq-plugins enable rabbitmq_management_agent

echo "✅ Métricas do RabbitMQ configuradas!"
echo "📊 Métricas disponíveis em: http://localhost:15692/metrics"
echo "🌐 Management UI disponível em: http://localhost:15672"
