# Guía Visual de los Puertos de Dremio

**Versión**: 3.2.5  
**Última actualización**: 16 de octubre de 2025  
**Idioma**: Español

---

## Vista General de los 3 Puertos de Dremio

```mermaid
graph TB
    subgraph "Puerto 9047 - API REST"
        direction TB
        A1[🌐 Interfaz Web UI]
        A2[🔧 Administración]
        A3[📊 Monitoreo]
        A4[🔐 Autenticación]
    end
    
    subgraph "Puerto 31010 - Proxy PostgreSQL"
        direction TB
        B1[💼 Herramientas BI Legacy]
        B2[🔌 JDBC/ODBC Estándar]
        B3[🐘 Compatibilidad PostgreSQL]
        B4[🔄 Migración Fácil]
    end
    
    subgraph "Puerto 32010 - Arrow Flight"
        direction TB
        C1[⚡ Rendimiento Máximo]
        C2[🎯 dbt Core]
        C3[📈 Apache Superset]
        C4[🐍 Python pyarrow]
    end
    
    D[🗄️ Coordinador Dremio<br/>Dremio 26.0 OSS]
    
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

## Arquitectura Detallada del Proxy PostgreSQL

### Flujo de Conexión Cliente → Dremio

```mermaid
graph LR
    subgraph "Aplicaciones Cliente"
        direction TB
        A1[psql CLI]
        A2[DBeaver]
        A3[pgAdmin]
        A4[Python psycopg2]
        A5[Java JDBC]
        A6[Tableau Desktop]
    end
    
    subgraph "Protocolo PostgreSQL Wire"
        P[Puerto 31010<br/>Proxy PostgreSQL]
    end
    
    subgraph "Motor Dremio"
        direction TB
        M1[Parser SQL]
        M2[Optimizador]
        M3[Ejecutor]
    end
    
    subgraph "Fuentes de Datos"
        direction TB
        S1[📦 Archivos Parquet<br/>MinIO S3]
        S2[💾 Tablas PostgreSQL]
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

## Comparación de Rendimiento

### Benchmark: Escaneo de 100 GB de Datos

```mermaid
gantt
    title Tiempo de Ejecución por Protocolo (segundos)
    dateFormat X
    axisFormat %s seg
    
    section API REST :9047
    Transferir 100 GB     :0, 180
    
    section PostgreSQL :31010
    Transferir 100 GB     :0, 90
    
    section Arrow Flight :32010
    Transferir 100 GB     :0, 5
```

### Rendimiento de Datos

```mermaid
graph LR
    subgraph "Rendimiento de Red por Protocolo"
        A["Puerto 9047<br/>API REST<br/>📊 ~500 MB/s<br/>⏱️ Estándar"]
        B["Puerto 31010<br/>PostgreSQL Wire<br/>📊 ~1-2 GB/s<br/>⏱️ Bueno"]
        C["Puerto 32010<br/>Arrow Flight<br/>📊 ~20 GB/s<br/>⏱️ Excelente"]
    end
    
    style A fill:#FF9800,color:#fff
    style B fill:#4CAF50,color:#fff
    style C fill:#2196F3,color:#fff
```

### Latencia de Consulta Simple

| Protocolo | Puerto | Latencia Promedio | Sobrecarga de Red |
|----------|------|-----------------|------------------|
| **API REST** | 9047 | 50-100 ms | JSON (verboso) |
| **Proxy PostgreSQL** | 31010 | 20-50 ms | Wire Protocol (compacto) |
| **Arrow Flight** | 32010 | 5-10 ms | Apache Arrow (binario columnar) |

---

## Casos de Uso por Puerto

### Puerto 9047 - API REST

```mermaid
graph TB
    A[Puerto 9047<br/>API REST]
    
    A --> B1[🌐 Interfaz de Navegador Web]
    A --> B2[🔧 Configuración de Servicios]
    A --> B3[👤 Gestión de Usuarios]
    A --> B4[📊 Paneles de Monitoreo]
    A --> B5[🔐 Login OAuth/SAML]
    
    B1 --> C1[Crear Espacios/Carpetas]
    B1 --> C2[Definir VDS]
    B1 --> C3[Explorar Datasets]
    
    B2 --> C4[Añadir Fuentes]
    B2 --> C5[Configurar Reflections]
    B2 --> C6[Configuración del Sistema]
    
    style A fill:#4CAF50,color:#fff,stroke:#000,stroke-width:3px
    style B1 fill:#81C784,color:#fff
    style B2 fill:#81C784,color:#fff
    style B3 fill:#81C784,color:#fff
    style B4 fill:#81C784,color:#fff
    style B5 fill:#81C784,color:#fff
```

### Puerto 31010 - Proxy PostgreSQL

```mermaid
graph TB
    A[Puerto 31010<br/>Proxy PostgreSQL]
    
    A --> B1[💼 Herramientas BI Legacy]
    A --> B2[🔄 Migración PostgreSQL]
    A --> B3[🔌 Drivers Estándar]
    
    B1 --> C1[Tableau Desktop<br/>sin Arrow Flight]
    B1 --> C2[Power BI Desktop<br/>ODBC]
    B1 --> C3[QlikView<br/>JDBC PostgreSQL]
    
    B2 --> D1[Código JDBC Existente<br/>sin modificaciones]
    B2 --> D2[Scripts psql<br/>100% compatible]
    B2 --> D3[Apps Python<br/>psycopg2]
    
    B3 --> E1[PostgreSQL ODBC Driver]
    B3 --> E2[PostgreSQL JDBC Driver]
    B3 --> E3[Drivers Nativos del SO]
    
    style A fill:#336791,color:#fff,stroke:#000,stroke-width:3px
    style B1 fill:#5C6BC0,color:#fff
    style B2 fill:#5C6BC0,color:#fff
    style B3 fill:#5C6BC0,color:#fff
```

### Puerto 32010 - Arrow Flight

```mermaid
graph TB
    A[Puerto 32010<br/>Arrow Flight]
    
    A --> B1[⚡ Rendimiento Máximo]
    A --> B2[🎯 Herramientas Modernas]
    A --> B3[🐍 Ecosistema Python]
    
    B1 --> C1[Escaneos de TB/PB]
    B1 --> C2[Agregaciones Masivas]
    B1 --> C3[Transferencias Zero-Copy]
    
    B2 --> D1[dbt Core<br/>profiles.yml]
    B2 --> D2[Apache Superset<br/>Database Config]
    B2 --> D3[Jupyter Notebooks<br/>pandas/polars]
    
    B3 --> E1[Biblioteca pyarrow]
    B3 --> E2[pandas via Arrow]
    B3 --> E3[Integración Polars]
    
    style A fill:#FF5722,color:#fff,stroke:#000,stroke-width:3px
    style B1 fill:#FF7043,color:#fff
    style B2 fill:#FF7043,color:#fff
    style B3 fill:#FF7043,color:#fff
```

---

## Árbol de Decisión: ¿Qué Puerto Usar?

```mermaid
graph TB
    Start[Necesito Conectarme a Dremio]
    
    Start --> Q1{¿Tipo de Aplicación?}
    
    Q1 -->|Interfaz Web<br/>Administración| Port9047[✅ Puerto 9047<br/>API REST]
    
    Q1 -->|Herramienta BI/Cliente SQL| Q2{¿Soporta Arrow Flight?}
    
    Q2 -->|No<br/>Herramienta Legacy| Port31010[✅ Puerto 31010<br/>Proxy PostgreSQL]
    Q2 -->|Sí<br/>Herramienta Moderna| Q3{¿Rendimiento Crítico?}
    
    Q3 -->|Sí<br/>Producción| Port32010[✅ Puerto 32010<br/>Arrow Flight]
    Q3 -->|No<br/>Dev/Test| Port31010b[⚠️ Puerto 31010<br/>Más Fácil]
    
    Q1 -->|Aplicación Personalizada| Q4{¿Lenguaje?}
    
    Q4 -->|Python/Java| Q5{¿Rendimiento Importante?}
    Q5 -->|Sí| Port32010b[✅ Puerto 32010<br/>Arrow Flight]
    Q5 -->|No| Port31010c[✅ Puerto 31010<br/>JDBC/psycopg2]
    
    Q4 -->|Otro<br/>Go/Rust/.NET| Port31010d[✅ Puerto 31010<br/>PostgreSQL Wire]
    
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

## Ejemplos de Conexión Proxy PostgreSQL

### 1. psql CLI

```bash
# Conexión simple
psql -h localhost -p 31010 -U admin -d datalake

# Consulta directa
psql -h localhost -p 31010 -U admin -d datalake \
  -c "SELECT COUNT(*) FROM MinIO.datalake.customers;"

# Modo interactivo
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

### 2. Configuración DBeaver

```yaml
Tipo de Conexión: PostgreSQL
Nombre de Conexión: Dremio via PostgreSQL Proxy

Principal:
  Host: localhost
  Puerto: 31010
  Base de datos: datalake
  Usuario: admin
  Contraseña: [tu-contraseña]
  
Propiedades del Driver:
  ssl: false
  
Avanzado:
  Tiempo de espera de conexión: 30000
  Tiempo de espera de consulta: 0
```

### 3. Python con psycopg2

```python
import psycopg2
from psycopg2 import sql

# Conexión
conn = psycopg2.connect(
    host="localhost",
    port=31010,
    database="datalake",
    user="admin",
    password="tu-contraseña"
)

# Cursor
cursor = conn.cursor()

# Consulta simple
cursor.execute("SELECT * FROM MinIO.datalake.customers LIMIT 10")
rows = cursor.fetchall()

for row in rows:
    print(row)

# Consulta parametrizada
query = sql.SQL("SELECT * FROM {} WHERE state = %s").format(
    sql.Identifier("MinIO", "datalake", "customers")
)
cursor.execute(query, ("CA",))

# Cerrar
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
        String password = "tu-contraseña";
        
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

### 5. Cadena de Conexión ODBC (DSN)

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
Password=tu-contraseña
SSLMode=disable
Protocol=7.4
```

---

## Configuración Docker Compose

### Mapeo de Puertos Dremio

```yaml
services:
  dremio:
    image: dremio/dremio-oss:26.0
    container_name: dremio
    ports:
      # Puerto 9047 - API REST / Web UI
      - "9047:9047"
      
      # Puerto 31010 - Proxy PostgreSQL (ODBC/JDBC)
      - "31010:31010"
      
      # Puerto 32010 - Arrow Flight (Rendimiento)
      - "32010:32010"
    environment:
      - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms4g -Xmx8g
    volumes:
      - ./docker-volume/dremio:/opt/dremio/data
    networks:
      - data-platform
```

### Verificación de Puertos

```bash
# Verificar que los 3 puertos estén abiertos
netstat -an | grep -E '9047|31010|32010'

# Probar API REST
curl -v http://localhost:9047

# Probar Proxy PostgreSQL
psql -h localhost -p 31010 -U admin -d datalake -c "SELECT 1;"

# Probar Arrow Flight (con Python)
python3 -c "
from pyarrow import flight
client = flight.connect('grpc://localhost:32010')
print('Arrow Flight OK')
"
```

---

## Resumen Visual Rápido

### Los 3 Puertos de un Vistazo

| Puerto | Protocolo | Uso Principal | Rendimiento | Compatibilidad |
|------|-----------|-------------|-------------|---------------|
| **9047** | API REST | 🌐 Web UI, Admin | ⭐⭐ Estándar | ⭐⭐⭐ Universal |
| **31010** | PostgreSQL Wire | 💼 Herramientas BI, Migración | ⭐⭐⭐ Bueno | ⭐⭐⭐ Excelente |
| **32010** | Arrow Flight | ⚡ Producción, dbt, Superset | ⭐⭐⭐⭐⭐ Máximo | ⭐⭐ Limitado |

### Matriz de Selección

```mermaid
graph TB
    subgraph "Guía de Selección"
        A["🎯 Caso de Uso"]
        
        A --> B1["Interfaz Web<br/>Configuración"]
        A --> B2["Herramienta BI Legacy<br/>Sin Arrow Flight"]
        A --> B3["Migración PostgreSQL<br/>Código JDBC Existente"]
        A --> B4["dbt, Superset<br/>Producción"]
        A --> B5["Python pyarrow<br/>Analítica"]
        
        B1 --> C1["Puerto 9047<br/>API REST"]
        B2 --> C2["Puerto 31010<br/>PostgreSQL"]
        B3 --> C2
        B4 --> C3["Puerto 32010<br/>Arrow Flight"]
        B5 --> C3
    end
    
    style A fill:#2196F3,color:#fff
    style C1 fill:#4CAF50,color:#fff,stroke:#000,stroke-width:2px
    style C2 fill:#336791,color:#fff,stroke:#000,stroke-width:2px
    style C3 fill:#FF5722,color:#fff,stroke:#000,stroke-width:2px
```

---

## Recursos Adicionales

### Documentación Relacionada

- [Arquitectura - Componentes](./components.md) - Sección "Proxy PostgreSQL para Dremio"
- [Guía - Configuración Dremio](../guides/dremio-setup.md) - Sección "Conexión via Proxy PostgreSQL"
- [Configuración - Dremio](../getting-started/configuration.md) - Configuración `dremio.conf`

### Enlaces Oficiales

- **Documentación Dremio**: https://docs.dremio.com/
- **Protocolo PostgreSQL Wire**: https://www.postgresql.org/docs/current/protocol.html
- **Apache Arrow Flight**: https://arrow.apache.org/docs/format/Flight.html

---

**Versión**: 3.2.5  
**Última actualización**: 16 de octubre de 2025  
**Estado**: ✅ Completo
