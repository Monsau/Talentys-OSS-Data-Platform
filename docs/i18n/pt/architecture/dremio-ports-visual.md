# Guia Visual das Portas do Dremio

**Versão**: 3.2.5  
**Última atualização**: 16 de outubro de 2025  
**Idioma**: Português

---

## Visão Geral das 3 Portas do Dremio

```mermaid
graph TB
    subgraph "Porta 9047 - API REST"
        direction TB
        A1[🌐 Interface Web UI]
        A2[🔧 Administração]
        A3[📊 Monitoramento]
        A4[🔐 Autenticação]
    end
    
    subgraph "Porta 31010 - Proxy PostgreSQL"
        direction TB
        B1[💼 Ferramentas BI Legacy]
        B2[🔌 JDBC/ODBC Padrão]
        B3[🐘 Compatibilidade PostgreSQL]
        B4[🔄 Migração Fácil]
    end
    
    subgraph "Porta 32010 - Arrow Flight"
        direction TB
        C1[⚡ Desempenho Máximo]
        C2[🎯 dbt Core]
        C3[📈 Apache Superset]
        C4[🐍 Python pyarrow]
    end
    
    D[🗄️ Coordenador Dremio<br/>Dremio 26.0 OSS]
    
    A1 & A2 & A3 & A4 --> D
    B1 & B2 & B3 & B4 --> D
    C1 & C2 & C3 & C4 --> D
    
    E1[(MinIO S3)]
    E2[(PostgreSQL)]
    E3[(Elasticsearch)]
    
    D --> E1 & E2 & E3
    
    style D fill:#FDB515,color:#000,stroke:#000,stroke-width:3px
    style A1 fill:#4CAF50,color:#fff
    style A2 fill:#4CAF50,color:#fff
    style A3 fill:#4CAF50,color:#fff
    style A4 fill:#4CAF50,color:#fff
    style B1 fill:#336791,color:#fff
    style B2 fill:#336791,color:#fff
    style B3 fill:#336791,color:#fff
    style B4 fill:#336791,color:#fff
    style C1 fill:#FF5722,color:#fff
    style C2 fill:#FF5722,color:#fff
    style C3 fill:#FF5722,color:#fff
    style C4 fill:#FF5722,color:#fff
```

---

## Arquitetura Detalhada do Proxy PostgreSQL

### Fluxo de Conexão Cliente → Dremio

```mermaid
graph LR
    subgraph "Aplicações Cliente"
        direction TB
        A1[psql CLI]
        A2[DBeaver]
        A3[pgAdmin]
        A4[Python psycopg2]
        A5[Java JDBC]
        A6[Tableau Desktop]
    end
    
    subgraph "Protocolo PostgreSQL Wire"
        P[Porta 31010<br/>Proxy PostgreSQL]
    end
    
    subgraph "Motor Dremio"
        direction TB
        M1[Parser SQL]
        M2[Otimizador]
        M3[Executor]
    end
    
    subgraph "Fontes de Dados"
        direction TB
        S1[📦 Arquivos Parquet<br/>MinIO S3]
        S2[💾 Tabelas PostgreSQL]
        S3[🔍 Índice Elasticsearch]
    end
    
    A1 & A2 & A3 --> P
    A4 & A5 & A6 --> P
    
    P --> M1
    M1 --> M2
    M2 --> M3
    
    M3 --> S1 & S2 & S3
    
    style P fill:#336791,color:#fff,stroke:#000,stroke-width:3px
    style M1 fill:#FDB515,color:#000
    style M2 fill:#FDB515,color:#000
    style M3 fill:#FDB515,color:#000
```

---

## Comparação de Desempenho

### Benchmark: Varredura de 100 GB de Dados

```mermaid
gantt
    title Tempo de Execução por Protocolo (segundos)
    dateFormat X
    axisFormat %s seg
    
    section API REST :9047
    Transferir 100 GB     :0, 180
    
    section PostgreSQL :31010
    Transferir 100 GB     :0, 90
    
    section Arrow Flight :32010
    Transferir 100 GB     :0, 5
```

### Desempenho de Dados

```mermaid
graph LR
    subgraph "Desempenho de Rede por Protocolo"
        A["Porta 9047<br/>API REST<br/>📊 ~500 MB/s<br/>⏱️ Padrão"]
        B["Porta 31010<br/>PostgreSQL Wire<br/>📊 ~1-2 GB/s<br/>⏱️ Bom"]
        C["Porta 32010<br/>Arrow Flight<br/>📊 ~20 GB/s<br/>⏱️ Excelente"]
    end
    
    style A fill:#FF9800,color:#fff
    style B fill:#4CAF50,color:#fff
    style C fill:#2196F3,color:#fff
```

### Latência de Consulta Simples

| Protocolo | Porta | Latência Média | Overhead de Rede |
|----------|------|----------------|------------------|
| **API REST** | 9047 | 50-100 ms | JSON (verboso) |
| **Proxy PostgreSQL** | 31010 | 20-50 ms | Wire Protocol (compacto) |
| **Arrow Flight** | 32010 | 5-10 ms | Apache Arrow (binário columnar) |

---

## Casos de Uso por Porta

### Porta 9047 - API REST

```mermaid
graph TB
    A[Porta 9047<br/>API REST]
    
    A --> B1[🌐 Interface Web Browser]
    A --> B2[🔧 Configuração de Serviços]
    A --> B3[👤 Gerenciamento de Usuários]
    A --> B4[📊 Painéis de Monitoramento]
    A --> B5[🔐 Login OAuth/SAML]
    
    B1 --> C1[Criar Espaços/Pastas]
    B1 --> C2[Definir VDS]
    B1 --> C3[Explorar Datasets]
    
    B2 --> C4[Adicionar Fontes]
    B2 --> C5[Configurar Reflections]
    B2 --> C6[Configuração do Sistema]
    
    style A fill:#4CAF50,color:#fff,stroke:#000,stroke-width:3px
    style B1 fill:#81C784,color:#fff
    style B2 fill:#81C784,color:#fff
    style B3 fill:#81C784,color:#fff
    style B4 fill:#81C784,color:#fff
    style B5 fill:#81C784,color:#fff
```

### Porta 31010 - Proxy PostgreSQL

```mermaid
graph TB
    A[Porta 31010<br/>Proxy PostgreSQL]
    
    A --> B1[💼 Ferramentas BI Legacy]
    A --> B2[🔄 Migração PostgreSQL]
    A --> B3[🔌 Drivers Padrão]
    
    B1 --> C1[Tableau Desktop<br/>sem Arrow Flight]
    B1 --> C2[Power BI Desktop<br/>ODBC]
    B1 --> C3[QlikView<br/>JDBC PostgreSQL]
    
    B2 --> D1[Código JDBC Existente<br/>sem modificações]
    B2 --> D2[Scripts psql<br/>100% compatível]
    B2 --> D3[Apps Python<br/>psycopg2]
    
    B3 --> E1[PostgreSQL ODBC Driver]
    B3 --> E2[PostgreSQL JDBC Driver]
    B3 --> E3[Drivers Nativos do SO]
    
    style A fill:#336791,color:#fff,stroke:#000,stroke-width:3px
    style B1 fill:#5C6BC0,color:#fff
    style B2 fill:#5C6BC0,color:#fff
    style B3 fill:#5C6BC0,color:#fff
```

### Porta 32010 - Arrow Flight

```mermaid
graph TB
    A[Porta 32010<br/>Arrow Flight]
    
    A --> B1[⚡ Desempenho Máximo]
    A --> B2[🎯 Ferramentas Modernas]
    A --> B3[🐍 Ecossistema Python]
    
    B1 --> C1[Varreduras de TB/PB]
    B1 --> C2[Agregações Massivas]
    B1 --> C3[Transferências Zero-Copy]
    
    B2 --> D1[dbt Core<br/>profiles.yml]
    B2 --> D2[Apache Superset<br/>Database Config]
    B2 --> D3[Jupyter Notebooks<br/>pandas/polars]
    
    B3 --> E1[Biblioteca pyarrow]
    B3 --> E2[pandas via Arrow]
    B3 --> E3[Integração Polars]
    
    style A fill:#FF5722,color:#fff,stroke:#000,stroke-width:3px
    style B1 fill:#FF7043,color:#fff
    style B2 fill:#FF7043,color:#fff
    style B3 fill:#FF7043,color:#fff
```

---

## Árvore de Decisão: Qual Porta Usar?

```mermaid
graph TB
    Start[Preciso Conectar ao Dremio]
    
    Start --> Q1{Tipo de Aplicação?}
    
    Q1 -->|Interface Web<br/>Administração| Port9047[✅ Porta 9047<br/>API REST]
    
    Q1 -->|Ferramenta BI/Cliente SQL| Q2{Suporta Arrow Flight?}
    
    Q2 -->|Não<br/>Ferramenta Legacy| Port31010[✅ Porta 31010<br/>Proxy PostgreSQL]
    Q2 -->|Sim<br/>Ferramenta Moderna| Q3{Desempenho Crítico?}
    
    Q3 -->|Sim<br/>Produção| Port32010[✅ Porta 32010<br/>Arrow Flight]
    Q3 -->|Não<br/>Dev/Test| Port31010b[⚠️ Porta 31010<br/>Mais Fácil]
    
    Q1 -->|Aplicação Personalizada| Q4{Linguagem?}
    
    Q4 -->|Python/Java| Q5{Desempenho Importante?}
    Q5 -->|Sim| Port32010b[✅ Porta 32010<br/>Arrow Flight]
    Q5 -->|Não| Port31010c[✅ Porta 31010<br/>JDBC/psycopg2]
    
    Q4 -->|Outra<br/>Go/Rust/.NET| Port31010d[✅ Porta 31010<br/>PostgreSQL Wire]
    
    style Start fill:#2196F3,color:#fff
    style Port9047 fill:#4CAF50,color:#fff,stroke:#000,stroke-width:2px
    style Port31010 fill:#336791,color:#fff,stroke:#000,stroke-width:2px
    style Port31010b fill:#336791,color:#fff,stroke:#000,stroke-width:2px
    style Port31010c fill:#336791,color:#fff,stroke:#000,stroke-width:2px
    style Port31010d fill:#336791,color:#fff,stroke:#000,stroke-width:2px
    style Port32010 fill:#FF5722,color:#fff,stroke:#000,stroke-width:2px
    style Port32010b fill:#FF5722,color:#fff,stroke:#000,stroke-width:2px
```

---

## Exemplos de Conexão Proxy PostgreSQL

### 1. psql CLI

```bash
# Conexão simples
psql -h localhost -p 31010 -U admin -d datalake

# Consulta direta
psql -h localhost -p 31010 -U admin -d datalake \
  -c "SELECT COUNT(*) FROM MinIO.datalake.customers;"

# Modo interativo
$ psql -h localhost -p 31010 -U admin -d datalake
Password for user admin: ****
psql (16.0, server 26.0)
Type "help" for help.

datalake=> \dt
           List of relations
 Schema |   Name    | Type  | Owner 
--------+-----------+-------+-------
 public | customers | table | admin
 public | orders    | table | admin
(2 rows)

datalake=> SELECT customer_id, name, state FROM customers LIMIT 5;
```

### 2. Configuração DBeaver

```yaml
Tipo de Conexão: PostgreSQL
Nome da Conexão: Dremio via PostgreSQL Proxy

Principal:
  Host: localhost
  Porta: 31010
  Banco de dados: datalake
  Usuário: admin
  Senha: [sua-senha]
  
Propriedades do Driver:
  ssl: false
  
Avançado:
  Tempo limite de conexão: 30000
  Tempo limite de consulta: 0
```

### 3. Python com psycopg2

```python
import psycopg2
from psycopg2 import sql

# Conexão
conn = psycopg2.connect(
    host="localhost",
    port=31010,
    database="datalake",
    user="admin",
    password="sua-senha"
)

# Cursor
cursor = conn.cursor()

# Consulta simples
cursor.execute("SELECT * FROM MinIO.datalake.customers LIMIT 10")
rows = cursor.fetchall()

for row in rows:
    print(row)

# Consulta parametrizada
query = sql.SQL("SELECT * FROM {} WHERE state = %s").format(
    sql.Identifier("MinIO", "datalake", "customers")
)
cursor.execute(query, ("CA",))

# Fechar
cursor.close()
conn.close()
```

### 4. Java JDBC

```java
import java.sql.*;

public class DremioPostgreSQLProxy {
    public static void main(String[] args) {
        String url = "jdbc:postgresql://localhost:31010/datalake";
        String user = "admin";
        String password = "sua-senha";
        
        try (Connection conn = DriverManager.getConnection(url, user, password)) {
            Statement stmt = conn.createStatement();
            ResultSet rs = stmt.executeQuery(
                "SELECT customer_id, name, state FROM MinIO.datalake.customers LIMIT 10"
            );
            
            while (rs.next()) {
                int id = rs.getInt("customer_id");
                String name = rs.getString("name");
                String state = rs.getString("state");
                System.out.printf("ID: %d, Name: %s, State: %s%n", id, name, state);
            }
            
            rs.close();
            stmt.close();
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
}
```

### 5. String de Conexão ODBC (DSN)

```ini
[ODBC Data Sources]
Dremio_PostgreSQL=PostgreSQL Unicode Driver

[Dremio_PostgreSQL]
Driver=PostgreSQL Unicode
Description=Dremio via PostgreSQL Proxy
Server=localhost
Port=31010
Database=datalake
Username=admin
Password=sua-senha
SSLMode=disable
Protocol=7.4
```

---

## Configuração Docker Compose

### Mapeamento de Portas Dremio

```yaml
services:
  dremio:
    image: dremio/dremio-oss:26.0
    container_name: dremio
    ports:
      # Porta 9047 - API REST / Web UI
      - "9047:9047"
      
      # Porta 31010 - Proxy PostgreSQL (ODBC/JDBC)
      - "31010:31010"
      
      # Porta 32010 - Arrow Flight (Desempenho)
      - "32010:32010"
    environment:
      - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms4g -Xmx8g
    volumes:
      - ./docker-volume/dremio:/opt/dremio/data
    networks:
      - data-platform
```

### Verificação de Portas

```bash
# Verificar se as 3 portas estão abertas
netstat -an | grep -E '9047|31010|32010'

# Testar API REST
curl -v http://localhost:9047

# Testar Proxy PostgreSQL
psql -h localhost -p 31010 -U admin -d datalake -c "SELECT 1;"

# Testar Arrow Flight (com Python)
python3 -c "
from pyarrow import flight
client = flight.connect('grpc://localhost:32010')
print('Arrow Flight OK')
"
```

---

## Resumo Visual Rápido

### As 3 Portas de Relance

| Porta | Protocolo | Uso Principal | Desempenho | Compatibilidade |
|------|-----------|-------------|------------|----------------|
| **9047** | API REST | 🌐 Web UI, Admin | ⭐⭐ Padrão | ⭐⭐⭐ Universal |
| **31010** | PostgreSQL Wire | 💼 Ferramentas BI, Migração | ⭐⭐⭐ Bom | ⭐⭐⭐ Excelente |
| **32010** | Arrow Flight | ⚡ Produção, dbt, Superset | ⭐⭐⭐⭐⭐ Máximo | ⭐⭐ Limitado |

### Matriz de Seleção

```mermaid
graph TB
    subgraph "Guia de Seleção"
        A["🎯 Caso de Uso"]
        
        A --> B1["Interface Web<br/>Configuração"]
        A --> B2["Ferramenta BI Legacy<br/>Sem Arrow Flight"]
        A --> B3["Migração PostgreSQL<br/>Código JDBC Existente"]
        A --> B4["dbt, Superset<br/>Produção"]
        A --> B5["Python pyarrow<br/>Analítica"]
        
        B1 --> C1["Porta 9047<br/>API REST"]
        B2 --> C2["Porta 31010<br/>PostgreSQL"]
        B3 --> C2
        B4 --> C3["Porta 32010<br/>Arrow Flight"]
        B5 --> C3
    end
    
    style A fill:#2196F3,color:#fff
    style C1 fill:#4CAF50,color:#fff,stroke:#000,stroke-width:2px
    style C2 fill:#336791,color:#fff,stroke:#000,stroke-width:2px
    style C3 fill:#FF5722,color:#fff,stroke:#000,stroke-width:2px
```

---

## Recursos Adicionais

### Documentação Relacionada

- [Arquitetura - Componentes](./components.md) - Seção "Proxy PostgreSQL para Dremio"
- [Guia - Configuração Dremio](../guides/dremio-setup.md) - Seção "Conexão via Proxy PostgreSQL"
- [Configuração - Dremio](../getting-started/configuration.md) - Configuração `dremio.conf`

### Links Oficiais

- **Documentação Dremio**: https://docs.dremio.com/
- **Protocolo PostgreSQL Wire**: https://www.postgresql.org/docs/current/protocol.html
- **Apache Arrow Flight**: https://arrow.apache.org/docs/format/Flight.html

---

**Versão**: 3.2.5  
**Última atualização**: 16 de outubro de 2025  
**Estado**: ✅ Completo
