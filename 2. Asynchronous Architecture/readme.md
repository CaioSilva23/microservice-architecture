# Arquitetura de Mensageria Pura (RabbitMQ) - Comunicação Assíncrona entre Microsserviços

## 📋 Sobre o Projeto

Este projeto implementa o **modelo de mensageria pura** com comunicação exclusivamente assíncrona entre microsserviços, utilizando RabbitMQ como sistema de mensageria. Desenvolvido como parte de um trabalho de conclusão de curso (TCC) que investiga diferentes abordagens de comunicação em arquiteturas de microsserviços.

O sistema é composto por três microsserviços principais — Order Service, Payment Service e Notification Service — que se comunicam exclusivamente através de eventos e mensagens via RabbitMQ, demonstrando as características de desacoplamento e resiliência desta abordagem.

## 🎯 Objetivo do Estudo

Este protótipo implementa o **cenário de mensageria pura** como parte de uma pesquisa experimental que compara três abordagens de comunicação entre microsserviços:

1. **REST Puro (NGINX)** - Comunicação exclusivamente síncrona
2. **Mensageria Pura (RabbitMQ)** - Este protótipo - Comunicação exclusivamente assíncrona  
3. **Híbrida (NGINX + RabbitMQ)** - Combinação estratégica de ambas

### Características Avaliadas

- **⏱️ Latência**: Tempo de resposta das requisições (maior latência esperada devido ao overhead)
- **🛡️ Taxa de Falhas**: Tolerância a falhas através do desacoplamento (menor taxa esperada)
- **🔄 Tempo de Recuperação**: Capacidade de recuperação automática (menor tempo esperado)
- **🔧 Complexidade**: Gerenciamento de mensageria e eventual consistency (maior complexidade)

## 🏗️ Arquitetura dos Serviços

### Microsserviços

- **🛒 Serviço de Pedidos (Order Service)**: Responsável por registrar e consultar pedidos dos clientes
- **💳 Serviço de Pagamentos (Payment Service)**: Realiza o processamento do pagamento e validação das transações
- **📧 Serviço de Notificações (Notification Service)**: Envia notificações ao usuário com base em eventos do sistema

### Arquitetura de Mensageria Pura (RabbitMQ)

Este protótipo implementa o **modelo assíncrono puro** com:

- **📨 Comunicação via Eventos**: Todas as interações entre serviços através de mensagens RabbitMQ
- **� Desacoplamento Temporal**: Serviços operam independentemente sem dependências diretas
- **🛡️ Alta Resiliência**: Tolerância a falhas e recuperação automática através de filas persistentes
- **⏱️ Maior Latência**: Tempo de resposta superior devido ao overhead da mensageria
- **🔧 Complexidade**: Requer gerenciamento de filas, dead letters e eventual consistency

## 🛠️ Tecnologias Utilizadas

- **Linguagem**: Python 3.10+
- **Framework Web**: FastAPI
- **Containerização**: Docker & Docker Compose
- **API Gateway**: NGINX
- **Message Broker**: RabbitMQ
- **Monitoramento**: Prometheus + Grafana
- **Testes de Performance**: Locust
- **Banco de Dados**: [Especificar quando implementado]

## 📈 Métricas Monitoradas

- ⏱️ Tempo de resposta das APIs
- ❌ Número de falhas e erros
- 📊 Volume de mensagens processadas
- 🔄 Taxa de throughput por serviço
- 💾 Uso de recursos (CPU, memória)

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