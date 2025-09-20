# Arquitetura Híbrida para Comunicação entre Microsserviços com API Gateway e Mensageria

## 📋 Sobre o Projeto

Este projeto implementa uma **arquitetura híbrida** para comunicação entre microsserviços, combinando chamadas síncronas via API Gateway (NGINX) com comunicação assíncrona baseada em mensageria (RabbitMQ). Desenvolvido como trabalho de conclusão de curso (TCC), o sistema demonstra os benefícios da abordagem híbrida em termos de desempenho, tolerância a falhas e robustez comparado a modelos exclusivamente síncronos ou assíncronos.

O sistema é composto por três microsserviços principais — Order Service, Payment Service e Notification Service — que se comunicam através de uma combinação estratégica de REST via NGINX e eventos via RabbitMQ.

## 🎯 Objetivo do Estudo

Este protótipo faz parte de uma pesquisa experimental que visa **analisar e validar empiricamente os benefícios da arquitetura híbrida** de comunicação entre microsserviços. O estudo compara três abordagens distintas:

1. **REST Puro (NGINX)** - Comunicação exclusivamente síncrona
2. **Mensageria Pura (RabbitMQ)** - Comunicação exclusivamente assíncrona  
3. **Híbrida (NGINX + RabbitMQ)** - Combinação estratégica de ambas

### Perguntas de Pesquisa

- **Q1**: O modelo híbrido mantém latência próxima à comunicação síncrona?
- **Q2**: Ele reduz o impacto em cascata e o tempo de recuperação, aproximando-se da comunicação assíncrona?
- **Q3**: Quais trade-offs operacionais emergem em termos de complexidade e observabilidade frente aos ganhos de resiliência?

## 🏗️ Arquitetura dos Serviços

### Microsserviços

- **🛒 Serviço de Pedidos (Order Service)**: Responsável por registrar e consultar pedidos dos clientes
- **💳 Serviço de Pagamentos (Payment Service)**: Realiza o processamento do pagamento e validação das transações
- **📧 Serviço de Notificações (Notification Service)**: Envia notificações ao usuário com base em eventos do sistema

### Arquitetura Híbrida (NGINX + RabbitMQ)

Este protótipo implementa o **modelo híbrido** que combina:

- **🚪 API Gateway (NGINX)**: Ponto único de entrada para chamadas síncronas externas, proporcionando controle, segurança e roteamento inteligente
- **📨 Mensageria (RabbitMQ)**: Comunicação assíncrona para eventos internos, promovendo desacoplamento e tolerância a falhas
- **⚖️ Equilíbrio**: Mantém latência próxima à comunicação síncrona enquanto reduz impacto de falhas em cascata

## 🛠️ Tecnologias Utilizadas

- **Linguagem**: Python 3.10+
- **Framework Web**: FastAPI
- **Containerização**: Docker & Docker Compose
- **API Gateway**: NGINX
- **Message Broker**: RabbitMQ
- **Monitoramento**: Prometheus + Grafana
- **Testes de Performance**: Locust
- **Banco de Dados**: [Especificar quando implementado]

## 📈 Métricas Monitoradas para Comparação

Este protótipo coleta métricas específicas para comparação experimental:

### Desempenho
- ⏱️ **Latência média e P95** das requisições HTTP
- 🔄 **Throughput** (requisições por segundo)
- 💾 **Uso de recursos** (CPU, memória, I/O)

### Resiliência  
- ❌ **Taxa de falhas** durante simulações de indisponibilidade
- 🔄 **Tempo de recuperação** após falhas dos serviços
- 🌊 **Propagação de falhas** em cascata

### Observabilidade
- 📊 **Cobertura de métricas** para troubleshooting
- � **Facilidade de rastreamento** de requisições
- 🚨 **Detecção automática** de problemas

### Complexidade
- � **Linhas de código** por funcionalidade
- ⚙️ **Configurações** necessárias
- 🛠️ **Esforço de manutenção** operacional

## 🚀 Como Executar

### Pré-requisitos

- Docker
- Docker Compose
- Python 3.10+ (para desenvolvimento local)

### Execução com Docker Compose

```bash
# Clone o repositório
git clone <url-do-repositorio>
cd projeto-tcc

# Execute todos os serviços
docker-compose up -d

# Verifique o status dos containers
docker-compose ps

# Para parar os serviços
docker-compose down
```

### Desenvolvimento Local

```bash
# Navegue até o serviço desejado
cd order-service

# Instale as dependências
pip install -r requirements.txt

# Execute o serviço
python main.py
```

## 📋 Endpoints dos Serviços

### Order Service
- `GET /orders` - Lista todos os pedidos
- `POST /orders` - Cria um novo pedido
- `GET /orders/{order_id}` - Busca pedido por ID
- `PUT /orders/{order_id}` - Atualiza um pedido

### Payment Service
- `POST /payments` - Processa um pagamento
- `GET /payments/{payment_id}` - Consulta status do pagamento

### Notification Service
- `POST /notifications` - Envia uma notificação
- `GET /notifications/{user_id}` - Lista notificações do usuário

## 🔧 Configuração do Ambiente

### Variáveis de Ambiente

Copie o arquivo `.env.example` para `.env` e configure as variáveis necessárias:

```bash
cp .env.example .env
```

### Monitoramento

- **Grafana**: http://localhost:3000
- **Prometheus**: http://localhost:9090
- **RabbitMQ Management**: http://localhost:15672

## 🧪 Testes

### Testes de Carga com Locust

```bash
# Instale o Locust
pip install locust

# Execute os testes de carga
locust -f tests/load/locustfile.py --host=http://localhost
```

### Testes de Falha

```bash
# Execute scripts de simulação de falhas
./tests/failure/simulate_failures.sh
```

## 📊 Estrutura do Projeto

```
projeto-tcc/
├── order-service/          # Serviço de Pedidos
├── payment-service/        # Serviço de Pagamentos
├── notification-service/   # Serviço de Notificações
├── nginx/                  # Configuração do API Gateway
├── monitoring/             # Configurações do Prometheus/Grafana
├── tests/                  # Testes de carga e falha
├── docker-compose.yml      # Orquestração dos serviços
└── README.md              # Este arquivo
```

## 🔍 Monitoramento e Observabilidade

O projeto inclui um stack completo de monitoramento:

- **Métricas de Aplicação**: Coletadas via Prometheus
- **Dashboards**: Visualização no Grafana
- **Logs Centralizados**: [A implementar]
- **Tracing Distribuído**: [A implementar]

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👨‍💻 Autor

Desenvolvido como projeto de TCC em Arquitetura de Microsserviços.

## 📚 Referências

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Documentation](https://docs.docker.com/)
- [RabbitMQ Documentation](https://www.rabbitmq.com/documentation.html)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)