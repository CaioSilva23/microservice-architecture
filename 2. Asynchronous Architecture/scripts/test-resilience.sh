#!/bin/bash

echo "🧪 Iniciando testes de resiliência do sistema..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para testar health checks
test_health_checks() {
    echo -e "\n${BLUE}📊 Testando Health Checks...${NC}"
    
    services=("order-service:8000" "payment-service:8001" "notification-service:8002")
    
    for service in "${services[@]}"; do
        service_name=$(echo $service | cut -d: -f1)
        port=$(echo $service | cut -d: -f2)
        
        echo -e "🔍 Testando health check do $service_name..."
        
        # Testar health check diretamente no container
        health_response=$(docker exec ${service_name//-/_} curl -s http://localhost:$port/health 2>/dev/null)
        
        if echo "$health_response" | grep -q "healthy"; then
            echo -e "✅ ${GREEN}$service_name está saudável${NC}"
        else
            echo -e "❌ ${RED}$service_name não está respondendo adequadamente${NC}"
        fi
    done
}

# Função para testar métricas de uptime
test_uptime_metrics() {
    echo -e "\n${BLUE}⏱️  Testando Métricas de Uptime...${NC}"
    
    services=("order-service" "payment-service" "notification-service")
    
    for service in "${services[@]}"; do
        echo -e "📈 Buscando métricas de uptime do $service..."
        
        uptime_metric=$(docker exec ${service//-/_} curl -s http://localhost:800$(echo $service | grep -o '[0-9]')/metrics 2>/dev/null | grep "${service//-/_}_uptime_seconds" | head -1)
        
        if [ ! -z "$uptime_metric" ]; then
            echo -e "✅ ${GREEN}Métrica de uptime encontrada: $uptime_metric${NC}"
        else
            echo -e "⚠️  ${YELLOW}Métrica de uptime não encontrada para $service${NC}"
        fi
    done
}

# Função para simular falhas e testar circuit breakers
test_circuit_breakers() {
    echo -e "\n${BLUE}🔌 Testando Circuit Breakers...${NC}"
    
    echo -e "📊 Verificando estado atual dos circuit breakers..."
    
    # Verificar métricas de circuit breaker
    for service in "order-service" "payment-service" "notification-service"; do
        echo -e "🔍 Verificando circuit breakers do $service..."
        
        cb_metrics=$(docker exec ${service//-/_} curl -s http://localhost:800$(echo $service | grep -o '[0-9]')/metrics 2>/dev/null | grep "circuit_breaker_state")
        
        if [ ! -z "$cb_metrics" ]; then
            echo -e "✅ ${GREEN}Circuit breakers encontrados:${NC}"
            echo "$cb_metrics" | while read line; do
                echo -e "   📈 $line"
            done
        else
            echo -e "⚠️  ${YELLOW}Nenhum circuit breaker ativo encontrado${NC}"
        fi
    done
}

# Função para testar métricas de recuperação
test_recovery_metrics() {
    echo -e "\n${BLUE}🔄 Testando Métricas de Recuperação...${NC}"
    
    services=("order-service" "payment-service" "notification-service")
    
    for service in "${services[@]}"; do
        echo -e "📊 Verificando métricas de recuperação do $service..."
        
        recovery_metrics=$(docker exec ${service//-/_} curl -s http://localhost:800$(echo $service | grep -o '[0-9]')/metrics 2>/dev/null | grep "recovery_time_seconds")
        
        if [ ! -z "$recovery_metrics" ]; then
            echo -e "✅ ${GREEN}Métricas de recuperação encontradas${NC}"
        else
            echo -e "⚠️  ${YELLOW}Métricas de recuperação não encontradas para $service${NC}"
        fi
    done
}

# Função para testar métricas de dependência
test_dependency_metrics() {
    echo -e "\n${BLUE}🔗 Testando Métricas de Dependência...${NC}"
    
    services=("order-service" "payment-service" "notification-service")
    
    for service in "${services[@]}"; do
        echo -e "📊 Verificando métricas de dependência do $service..."
        
        dep_metrics=$(docker exec ${service//-/_} curl -s http://localhost:800$(echo $service | grep -o '[0-9]')/metrics 2>/dev/null | grep "dependency_calls_total")
        
        if [ ! -z "$dep_metrics" ]; then
            echo -e "✅ ${GREEN}Métricas de dependência encontradas${NC}"
            echo "$dep_metrics" | head -3 | while read line; do
                echo -e "   📈 $line"
            done
        else
            echo -e "⚠️  ${YELLOW}Métricas de dependência não encontradas para $service${NC}"
        fi
    done
}

# Função para simular carga e verificar comportamento
simulate_load() {
    echo -e "\n${BLUE}🚀 Simulando Carga no Sistema...${NC}"
    
    echo -e "📦 Criando alguns pedidos para gerar métricas..."
    
    # Simular criação de pedidos através do API Gateway
    for i in {1..5}; do
        echo -e "📝 Criando pedido $i..."
        
        curl -s -X POST "http://localhost/orders" \
             -H "Content-Type: application/json" \
             -d '{
                "produto": "Produto Teste '$i'",
                "quantidade": '$i',
                "valor": '$((i * 10))'
             }' > /dev/null 2>&1
        
        sleep 1
    done
    
    echo -e "✅ ${GREEN}Carga simulada aplicada${NC}"
}

# Função para verificar Prometheus e alertas
check_prometheus_alerts() {
    echo -e "\n${BLUE}🚨 Verificando Alertas no Prometheus...${NC}"
    
    # Verificar se Prometheus está rodando
    if curl -s "http://localhost:9090/-/healthy" > /dev/null 2>&1; then
        echo -e "✅ ${GREEN}Prometheus está rodando${NC}"
        
        # Verificar regras de alerta
        echo -e "📋 Verificando regras de alerta..."
        alert_rules=$(curl -s "http://localhost:9090/api/v1/rules" 2>/dev/null)
        
        if echo "$alert_rules" | grep -q "microservices-health-alerts"; then
            echo -e "✅ ${GREEN}Regras de alerta carregadas com sucesso${NC}"
        else
            echo -e "⚠️  ${YELLOW}Regras de alerta não encontradas${NC}"
        fi
        
        # Verificar alertas ativos
        echo -e "🔍 Verificando alertas ativos..."
        active_alerts=$(curl -s "http://localhost:9090/api/v1/alerts" 2>/dev/null)
        
        if echo "$active_alerts" | grep -q '"state":"firing"'; then
            echo -e "🚨 ${RED}Existem alertas ativos${NC}"
        else
            echo -e "✅ ${GREEN}Nenhum alerta ativo encontrado${NC}"
        fi
    else
        echo -e "❌ ${RED}Prometheus não está acessível${NC}"
    fi
}

# Função para verificar Grafana dashboard
check_grafana_dashboard() {
    echo -e "\n${BLUE}📊 Verificando Dashboard do Grafana...${NC}"
    
    if curl -s "http://localhost:3000/api/health" > /dev/null 2>&1; then
        echo -e "✅ ${GREEN}Grafana está rodando${NC}"
        
        # Verificar se o dashboard foi carregado
        dashboard_check=$(curl -s -u admin:admin "http://localhost:3000/api/search?query=Enhanced" 2>/dev/null)
        
        if echo "$dashboard_check" | grep -q "Enhanced Microservices Monitoring"; then
            echo -e "✅ ${GREEN}Dashboard enhanced encontrado${NC}"
        else
            echo -e "⚠️  ${YELLOW}Dashboard enhanced não encontrado${NC}"
        fi
    else
        echo -e "❌ ${RED}Grafana não está acessível${NC}"
    fi
}

# Função principal
main() {
    echo -e "${GREEN}🎯 Teste de Resiliência - Sistema de Microserviços TCC${NC}"
    echo -e "${GREEN}=================================================${NC}"
    
    # Verificar se os serviços estão rodando
    echo -e "\n${BLUE}🔍 Verificando serviços básicos...${NC}"
    if ! docker-compose ps | grep -q "Up"; then
        echo -e "❌ ${RED}Serviços não estão rodando. Execute: docker-compose up -d${NC}"
        exit 1
    fi
    
    echo -e "✅ ${GREEN}Serviços estão rodando${NC}"
    
    # Executar testes
    test_health_checks
    test_uptime_metrics
    test_circuit_breakers
    test_recovery_metrics
    test_dependency_metrics
    simulate_load
    check_prometheus_alerts
    check_grafana_dashboard
    
    echo -e "\n${GREEN}🎉 Teste de Resiliência Concluído!${NC}"
    echo -e "\n${BLUE}📋 Resumo das URLs importantes:${NC}"
    echo -e "   📊 Grafana: http://localhost:3000 (admin/admin)"
    echo -e "   📈 Prometheus: http://localhost:9090"
    echo -e "   🐰 RabbitMQ: http://localhost:15672 (guest/guest)"
    echo -e "   🌐 API Gateway: http://localhost/"
    
    echo -e "\n${YELLOW}💡 Próximos passos:${NC}"
    echo -e "   1. Acesse o Grafana e verifique o dashboard 'Enhanced Microservices Monitoring'"
    echo -e "   2. Monitore as métricas de resiliência em tempo real"
    echo -e "   3. Simule falhas nos serviços para testar circuit breakers"
    echo -e "   4. Verifique os alertas no Prometheus em /alerts"
}

# Executar teste
main "$@"
