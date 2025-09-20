# TCC: Arquitetura Híbrida para Comunicação entre Microsserviços com API Gateway e Mensageria

## 📋 Resumo da Pesquisa

Este repositório contém a implementação experimental de um estudo que investiga a aplicação de uma **arquitetura híbrida** para comunicação entre microsserviços, combinando chamadas síncronas via API Gateway com comunicação assíncrona baseada em mensageria.

### 🎯 Objetivo da Pesquisa

**Analisar e validar empiricamente os benefícios da arquitetura híbrida** de comunicação entre microsserviços, mensurando sua robustez, tolerância a falhas e desempenho sob diferentes cargas, comparando-a com modelos exclusivamente síncronos e assíncronos.

### ❓ Perguntas de Pesquisa

- **Q1**: O modelo híbrido mantém latência próxima à comunicação síncrona?
- **Q2**: Ele reduz o impacto em cascata e o tempo de recuperação, aproximando-se da comunicação assíncrona?
- **Q3**: Quais trade-offs operacionais emergem em termos de complexidade e observabilidade frente aos ganhos de resiliência?

## 🏗️ Estrutura do Estudo

O repositório contém **três protótipos** que implementam diferentes estratégias de comunicação:

### 1. 📡 [REST Puro (NGINX)](./3.%20Synchronous%20Architecture/)
- **Comunicação**: Exclusivamente síncrona via HTTP REST
- **Características**: Baixa latência, alta simplicidade, vulnerável a falhas em cascata
- **Implementação**: API Gateway NGINX + chamadas HTTP diretas

### 2. 🔄 [Mensageria Pura (RabbitMQ)](./2.%20Asynchronous%20Architecture/)
- **Comunicação**: Exclusivamente assíncrona via eventos
- **Características**: Alto desacoplamento, resiliente a falhas, maior latência
- **Implementação**: RabbitMQ com padrões pub/sub e filas

### 3. ⚖️ [Arquitetura Híbrida (NGINX + RabbitMQ)](./1.%20Hybrid%20Architecture/)
- **Comunicação**: Combinação estratégica de síncrona e assíncrona
- **Características**: Equilibra performance e resiliência
- **Implementação**: NGINX para APIs externas + RabbitMQ para eventos internos

## 🧪 Metodologia Experimental

### Ambiente de Teste
- **Microsserviços**: Order Service, Payment Service, Notification Service
- **Tecnologias**: Python + FastAPI, Docker, PostgreSQL
- **Monitoramento**: Prometheus + Grafana
- **Testes**: Locust para carga, simulações manuais para falhas

### Métricas Coletadas

| Categoria | Métricas | Objetivo |
|-----------|----------|----------|
| **Performance** | Latência (média, P95), Throughput, Uso de recursos | Comparar eficiência |
| **Resiliência** | Taxa de falhas, Tempo de recuperação, Propagação de erros | Avaliar robustez |
| **Observabilidade** | Cobertura de métricas, Facilidade de debug | Medir operabilidade |
| **Complexidade** | LOC, Configurações, Esforço de manutenção | Quantificar trade-offs |

## 📊 Principais Resultados

### Latência Média
- **REST Puro**: ~85ms (menor latência)
- **Híbrido**: ~120ms (balance intermediário)
- **Mensageria Pura**: ~180ms (maior latência)

### Taxa de Falhas (com falhas simuladas)
- **REST Puro**: 12% (vulnerável a cascata)
- **Híbrido**: 3% (resiliência moderada)
- **Mensageria Pura**: 1,5% (maior resiliência)

### Tempo de Recuperação
- **REST Puro**: 18s (maior dependência)
- **Híbrido**: 7s (recuperação moderada)
- **Mensageria Pura**: 6s (recuperação mais rápida)

## 🚀 Como Executar os Experimentos

### Pré-requisitos
```bash
# Verificar dependências
docker --version          # >= 20.10
docker-compose --version  # >= 1.29
python --version          # >= 3.10
```

### Execução de um Protótipo
```bash
# Escolha uma arquitetura
cd "1. Hybrid Architecture"

# Configure ambiente
cp .env.example .env

# Execute todos os serviços
docker-compose up -d

# Verifique status
docker-compose ps

# Configure métricas (se aplicável)
./scripts/setup-rabbitmq-metrics.sh

# Execute testes
./scripts/check-monitoring.sh
./scripts/test-resilience.sh
```

### URLs de Acesso
- **API Gateway**: http://localhost
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)
- **RabbitMQ Management**: http://localhost:15672 (guest/guest)

## 📁 Estrutura do Repositório

```
projeto-tcc/
├── 1. Hybrid Architecture/          # Protótipo híbrido (NGINX + RabbitMQ)
├── 2. Asynchronous Architecture/    # Protótipo mensageria pura (RabbitMQ)
├── 3. Synchronous Architecture/     # Protótipo REST puro (NGINX)
├── APENDICE_TCC.md                 # Documentação técnica completa
└── TCC caio batista.pdf            # Documento completo da pesquisa
```

## 📚 Documentação Adicional

- **[Apêndice Técnico](./APENDICE_TCC.md)**: Documentação completa das implementações
- **Documento do TCC**: `TCC caio batista.pdf` (análise completa e resultados)

## 🎓 Sobre o Trabalho

**Título**: Arquitetura Híbrida para Comunicação entre Microsserviços com API Gateway e Mensageria

**Autor**: Caio Cesar da Silva Batista

**Instituição**: Centro Universitário Carioca [UniCarioca]

**Curso**: Especialização em Engenharia de Software

**Ano**: 2025

## 🔄 Contribuições

As principais contribuições deste estudo são:

1. **Testbed Experimental**: Ambiente controlado com três estratégias de comunicação
2. **Protocolo de Testes**: Metodologia replicável com cargas e falhas simuladas
3. **Evidências Quantitativas**: Dados empíricos sobre performance, falhas e recuperação
4. **Diretrizes Práticas**: Orientações para decisões arquiteturais em sistemas distribuídos

## 📊 Conclusões

A **arquitetura híbrida** demonstrou ser uma solução eficaz que:

- ✅ **Equilibra performance e resiliência** melhor que abordagens puras
- ✅ **Reduz falhas em cascata** comparado ao modelo síncrono
- ✅ **Mantém latência controlada** comparado ao modelo assíncrono
- ⚠️ **Adiciona complexidade** operacional que deve ser considerada

**Recomendação**: A abordagem híbrida é especialmente adequada para **sistemas críticos ou de grande escala** onde robustez e disponibilidade são requisitos essenciais.