# Configuração para habilitar métricas do RabbitMQ

# Habilitar plugins do RabbitMQ para métricas
# Execute estes comandos no container do RabbitMQ após inicializar:
# rabbitmq-plugins enable rabbitmq_prometheus
# rabbitmq-plugins enable rabbitmq_management_agent

# As métricas estarão disponíveis em:
# http://rabbitmq:15692/metrics

# Para habilitar automaticamente, adicione esta configuração
# ao docker-compose.yml no serviço rabbitmq:

# environment:
#   - RABBITMQ_ENABLED_PLUGINS_FILE=/etc/rabbitmq/enabled_plugins

# E crie um arquivo enabled_plugins com:
# [rabbitmq_management,rabbitmq_prometheus].
