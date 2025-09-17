#!/bin/bash

# Script para reiniciar o projeto limpo, garantindo que a configuração do nginx seja aplicada corretamente

echo "🔄 Parando containers..."
docker-compose down

echo "🗑️ Removendo imagem antiga do api-gateway..."
docker rmi projeto-tcc_api-gateway 2>/dev/null || echo "Imagem não existia"

echo "🔨 Reconstruindo api-gateway sem cache..."
docker-compose build --no-cache api-gateway

echo "🚀 Iniciando todos os containers..."
docker-compose up -d

echo "⏳ Aguardando containers inicializarem..."
sleep 10

echo "🔍 Verificando configuração do nginx..."
docker exec api-gateway cat /etc/nginx/conf.d/default.conf

echo "✅ Projeto reiniciado com sucesso!"
echo "📡 Testando rota: curl http://localhost/orders/listar"
