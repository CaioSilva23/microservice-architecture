# 🚨 Troubleshooting - Dashboard não aparece no Grafana

## Problema: Dashboard não aparece na interface

### ✅ Soluções:

#### 1. **Reiniciar Grafana com configurações limpas**
```bash
./restart-grafana.sh
```

#### 2. **Verificar se arquivos estão corretos**
```bash
# Verificar se os arquivos estão presentes
ls -la grafana/dashboards/
ls -la grafana/datasources.yml
ls -la grafana/dashboard-provider.yml

# Verificar se containers estão rodando
docker-compose ps
```

#### 3. **Importar dashboard manualmente**
Se o dashboard automático não funcionar:

1. Acesse http://localhost:3000
2. Login: `admin` / `admin`
3. Vá em **Dashboards** → **New** → **Import**
4. Cole o conteúdo do arquivo `grafana/dashboards/microservices-dashboard.json`
5. Clique em **Load** e depois **Import**

#### 4. **Verificar logs do Grafana**
```bash
docker-compose logs grafana
```

#### 5. **Verificar se Prometheus está funcionando**
```bash
# Testar Prometheus diretamente
curl http://localhost:9090/api/v1/query?query=up

# Verificar targets
curl http://localhost:9090/api/v1/targets
```

#### 6. **Recriar setup completo**
```bash
# Parar tudo
docker-compose down

# Remover volumes (CUIDADO: perde dados)
docker-compose down -v

# Subir novamente
docker-compose up -d

# Aguardar e configurar RabbitMQ
sleep 30
./setup-rabbitmq-metrics.sh

# Verificar
./check-monitoring.sh
```

## 🔍 **Verificações importantes:**

### Datasource Prometheus
1. Acesse **Configuration** → **Data sources**
2. Deve ter um datasource "Prometheus" apontando para `http://prometheus:9090`
3. Teste a conexão clicando em "Save & test"

### Dashboard provisioning
1. Verifique se `/etc/grafana/provisioning/dashboards/` está montado corretamente
2. Logs devem mostrar: `"provisioning.dashboard" msg="dashboard update from file"`

### Estrutura de arquivos no container
```bash
# Verificar estrutura dentro do container
docker exec grafana ls -la /etc/grafana/provisioning/
docker exec grafana ls -la /etc/grafana/dashboards/
```

## 📋 **Template de dashboard funcional:**

Se nada funcionar, use este dashboard simples:

```json
{
  "id": null,
  "title": "Simple Monitoring",
  "panels": [
    {
      "id": 1,
      "title": "Prometheus Up",
      "type": "stat",
      "targets": [
        {
          "expr": "up",
          "refId": "A"
        }
      ],
      "gridPos": {"h": 8, "w": 24, "x": 0, "y": 0}
    }
  ],
  "time": {"from": "now-1h", "to": "now"},
  "refresh": "5s"
}
```

## 🎯 **URLs para debug:**

- **Grafana**: http://localhost:3000
- **Prometheus**: http://localhost:9090
- **Prometheus Targets**: http://localhost:9090/targets
- **RabbitMQ**: http://localhost:15672

## 📞 **Se ainda não funcionar:**

1. Verifique se todos os serviços estão expondo `/metrics`
2. Teste queries direto no Prometheus
3. Importe dashboard manualmente
4. Verifique logs dos containers
