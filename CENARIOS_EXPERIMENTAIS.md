# Configuração dos Cenários Experimentais

## Cenários de Comunicação entre Microsserviços

Este projeto implementa três cenários distintos para avaliar diferentes estratégias de comunicação:

### 🔄 Cenário 1: REST Puro (NGINX)
**Diretório**: `3. Synchronous Architecture`
- **Comunicação**: Exclusivamente síncrona via HTTP REST
- **Gateway**: NGINX para roteamento
- **Padrão**: Request-Response direto
- **Características**: Baixa latência, alta simplicidade, acoplamento temporal

### 📨 Cenário 2: Mensageria Pura (RabbitMQ)  
**Diretório**: `2. Asynchronous Architecture`
- **Comunicação**: Exclusivamente assíncrona via eventos
- **Broker**: RabbitMQ com filas e exchanges
- **Padrão**: Publish-Subscribe, Event-Driven
- **Características**: Alto desacoplamento, resiliente, maior latência

### ⚖️ Cenário 3: Híbrido (NGINX + RabbitMQ)
**Diretório**: `1. Hybrid Architecture`  
- **Comunicação**: Combinação estratégica de síncrona e assíncrona
- **Gateway**: NGINX para APIs externas
- **Broker**: RabbitMQ para eventos internos
- **Padrão**: Request-Response + Event-Driven
- **Características**: Equilibrio entre performance e resiliência

## Métricas Comparativas

### Performance
| Métrica | REST Puro | Mensageria Pura | Híbrido |
|---------|-----------|-----------------|---------|
| Latência Média | ~85ms | ~180ms | ~120ms |
| Throughput | Alto | Moderado | Alto |
| Uso CPU | Baixo | Moderado | Moderado |

### Resiliência
| Métrica | REST Puro | Mensageria Pura | Híbrido |
|---------|-----------|-----------------|---------|
| Taxa de Falhas | 12% | 1,5% | 3% |
| Tempo Recuperação | 18s | 6s | 7s |
| Tolerância a Falhas | Baixa | Alta | Moderada |

### Complexidade
| Aspecto | REST Puro | Mensageria Pura | Híbrido |
|---------|-----------|-----------------|---------|
| Implementação | Simples | Complexa | Moderada |
| Monitoramento | Direto | Elaborado | Moderado |
| Manutenção | Fácil | Difícil | Moderada |

## Tecnologias Utilizadas

### Stack Comum
- **Linguagem**: Python 3.10+
- **Framework**: FastAPI
- **Containerização**: Docker & Docker Compose
- **Banco de Dados**: PostgreSQL (por serviço)
- **Monitoramento**: Prometheus + Grafana

### Stack Específico por Cenário

#### REST Puro
- **API Gateway**: NGINX
- **Comunicação**: HTTP REST
- **Padrões**: RESTful APIs, OpenAPI

#### Mensageria Pura  
- **Message Broker**: RabbitMQ
- **Comunicação**: AMQP Protocol
- **Padrões**: Pub/Sub, Event Sourcing, CQRS

#### Híbrido
- **API Gateway**: NGINX
- **Message Broker**: RabbitMQ  
- **Comunicação**: HTTP REST + AMQP
- **Padrões**: API Gateway + Event-Driven

## Objetivos de Cada Cenário

### Objetivo do REST Puro
- Demonstrar **máxima simplicidade** e **menor latência**
- Evidenciar **vulnerabilidade a falhas em cascata**
- Servir como **baseline** para comparação

### Objetivo da Mensageria Pura
- Demonstrar **máximo desacoplamento** e **resiliência**
- Evidenciar **overhead de latência** da comunicação assíncrona  
- Mostrar **complexidade operacional** da mensageria

### Objetivo do Híbrido
- Demonstrar **equilíbrio** entre performance e resiliência
- Evidenciar **flexibilidade** de escolha por contexto
- Validar **viabilidade prática** da abordagem combinada

## Cenários de Teste

### Testes de Carga
- **Ferramenta**: Locust
- **Cenários**: 50, 100, 200 usuários simultâneos
- **Duração**: 5 minutos por cenário
- **Métricas**: Latência, throughput, taxa de erro

### Testes de Falha
- **Simulações**: Parada de serviços individuais
- **Duração**: 30-60 segundos de indisponibilidade
- **Métricas**: Taxa de falha, tempo de recuperação, propagação de erros

### Testes de Recuperação
- **Cenários**: Restart de serviços, falhas de rede
- **Métricas**: Tempo até detecção, tempo de recuperação completa
- **Observação**: Comportamento dos circuit breakers e health checks