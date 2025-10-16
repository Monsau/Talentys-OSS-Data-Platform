# Dremio 포트 시각적 가이드

**버전**: 3.2.5  
**최종 업데이트**: 2025년 10월 16일  
**언어**: 한국어

---

## Dremio 3개 포트 개요

```mermaid
graph TB
    subgraph "포트 9047 - REST API"
        direction TB
        A1[🌐 웹 UI 인터페이스]
        A2[🔧 관리]
        A3[📊 모니터링]
        A4[🔐 인증]
    end
    
    subgraph "포트 31010 - PostgreSQL 프록시"
        direction TB
        B1[💼 레거시 BI 도구]
        B2[🔌 표준 JDBC/ODBC]
        B3[🐘 PostgreSQL 호환성]
        B4[🔄 쉬운 마이그레이션]
    end
    
    subgraph "포트 32010 - Arrow Flight"
        direction TB
        C1[⚡ 최대 성능]
        C2[🎯 dbt Core]
        C3[📈 Apache Superset]
        C4[🐍 Python pyarrow]
    end
    
    D[🗄️ Dremio 코디네이터<br/>Dremio 26.0 OSS]
    
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

## PostgreSQL 프록시 상세 아키텍처

### 클라이언트 → Dremio 연결 흐름

```mermaid
graph LR
    subgraph "클라이언트 애플리케이션"
        direction TB
        A1[psql CLI]
        A2[DBeaver]
        A3[pgAdmin]
        A4[Python psycopg2]
        A5[Java JDBC]
        A6[Tableau Desktop]
    end
    
    subgraph "PostgreSQL Wire 프로토콜"
        P[포트 31010<br/>PostgreSQL 프록시]
    end
    
    subgraph "Dremio 엔진"
        direction TB
        M1[SQL 파서]
        M2[옵티마이저]
        M3[실행기]
    end
    
    subgraph "데이터 소스"
        direction TB
        S1[📦 Parquet 파일<br/>MinIO S3]
        S2[💾 PostgreSQL 테이블]
        S3[🔍 Elasticsearch 인덱스]
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

## 성능 비교

### 벤치마크: 100 GB 데이터 스캔

```mermaid
gantt
    title 프로토콜별 실행 시간 (초)
    dateFormat X
    axisFormat %s 초
    
    section REST API :9047
    100 GB 전송     :0, 180
    
    section PostgreSQL :31010
    100 GB 전송     :0, 90
    
    section Arrow Flight :32010
    100 GB 전송     :0, 5
```

### 데이터 처리량

```mermaid
graph LR
    subgraph "프로토콜별 네트워크 성능"
        A["포트 9047<br/>REST API<br/>📊 ~500 MB/s<br/>⏱️ 표준"]
        B["포트 31010<br/>PostgreSQL Wire<br/>📊 ~1-2 GB/s<br/>⏱️ 양호"]
        C["포트 32010<br/>Arrow Flight<br/>📊 ~20 GB/s<br/>⏱️ 우수"]
    end
    
    style A fill:#FF9800,color:#fff
    style B fill:#4CAF50,color:#fff
    style C fill:#2196F3,color:#fff
```

### 단순 쿼리 지연 시간

| 프로토콜 | 포트 | 평균 지연 시간 | 네트워크 오버헤드 |
|----------|------|----------------|------------------|
| **REST API** | 9047 | 50-100 ms | JSON (상세) |
| **PostgreSQL 프록시** | 31010 | 20-50 ms | Wire Protocol (간결) |
| **Arrow Flight** | 32010 | 5-10 ms | Apache Arrow (바이너리 컬럼형) |

---

## 포트별 사용 사례

### 포트 9047 - REST API

```mermaid
graph TB
    A[포트 9047<br/>REST API]
    
    A --> B1[🌐 웹 브라우저 인터페이스]
    A --> B2[🔧 서비스 구성]
    A --> B3[👤 사용자 관리]
    A --> B4[📊 모니터링 대시보드]
    A --> B5[🔐 OAuth/SAML 로그인]
    
    B1 --> C1[스페이스/폴더 생성]
    B1 --> C2[VDS 정의]
    B1 --> C3[데이터셋 탐색]
    
    B2 --> C4[소스 추가]
    B2 --> C5[Reflections 구성]
    B2 --> C6[시스템 구성]
    
    style A fill:#4CAF50,color:#fff,stroke:#000,stroke-width:3px
    style B1 fill:#81C784,color:#fff
    style B2 fill:#81C784,color:#fff
    style B3 fill:#81C784,color:#fff
    style B4 fill:#81C784,color:#fff
    style B5 fill:#81C784,color:#fff
```

### 포트 31010 - PostgreSQL 프록시

```mermaid
graph TB
    A[포트 31010<br/>PostgreSQL 프록시]
    
    A --> B1[💼 레거시 BI 도구]
    A --> B2[🔄 PostgreSQL 마이그레이션]
    A --> B3[🔌 표준 드라이버]
    
    B1 --> C1[Tableau Desktop<br/>Arrow Flight 미지원]
    B1 --> C2[Power BI Desktop<br/>ODBC]
    B1 --> C3[QlikView<br/>JDBC PostgreSQL]
    
    B2 --> D1[기존 JDBC 코드<br/>수정 불필요]
    B2 --> D2[psql 스크립트<br/>100% 호환]
    B2 --> D3[Python 앱<br/>psycopg2]
    
    B3 --> E1[PostgreSQL ODBC Driver]
    B3 --> E2[PostgreSQL JDBC Driver]
    B3 --> E3[OS 네이티브 드라이버]
    
    style A fill:#336791,color:#fff,stroke:#000,stroke-width:3px
    style B1 fill:#5C6BC0,color:#fff
    style B2 fill:#5C6BC0,color:#fff
    style B3 fill:#5C6BC0,color:#fff
```

### 포트 32010 - Arrow Flight

```mermaid
graph TB
    A[포트 32010<br/>Arrow Flight]
    
    A --> B1[⚡ 최대 성능]
    A --> B2[🎯 현대적 도구]
    A --> B3[🐍 Python 생태계]
    
    B1 --> C1[TB/PB 스캔]
    B1 --> C2[대규모 집계]
    B1 --> C3[제로 카피 전송]
    
    B2 --> D1[dbt Core<br/>profiles.yml]
    B2 --> D2[Apache Superset<br/>Database Config]
    B2 --> D3[Jupyter Notebooks<br/>pandas/polars]
    
    B3 --> E1[pyarrow 라이브러리]
    B3 --> E2[pandas via Arrow]
    B3 --> E3[Polars 통합]
    
    style A fill:#FF5722,color:#fff,stroke:#000,stroke-width:3px
    style B1 fill:#FF7043,color:#fff
    style B2 fill:#FF7043,color:#fff
    style B3 fill:#FF7043,color:#fff
```

---

## 의사 결정 트리: 어떤 포트를 사용할까?

```mermaid
graph TB
    Start[Dremio에 연결해야 함]
    
    Start --> Q1{애플리케이션 유형?}
    
    Q1 -->|웹 인터페이스<br/>관리| Port9047[✅ 포트 9047<br/>REST API]
    
    Q1 -->|BI 도구/SQL 클라이언트| Q2{Arrow Flight 지원?}
    
    Q2 -->|아니요<br/>레거시 도구| Port31010[✅ 포트 31010<br/>PostgreSQL 프록시]
    Q2 -->|예<br/>현대적 도구| Q3{성능이 중요?}
    
    Q3 -->|예<br/>프로덕션| Port32010[✅ 포트 32010<br/>Arrow Flight]
    Q3 -->|아니요<br/>개발/테스트| Port31010b[⚠️ 포트 31010<br/>더 쉬움]
    
    Q1 -->|사용자 정의 애플리케이션| Q4{프로그래밍 언어?}
    
    Q4 -->|Python/Java| Q5{성능이 중요?}
    Q5 -->|예| Port32010b[✅ 포트 32010<br/>Arrow Flight]
    Q5 -->|아니요| Port31010c[✅ 포트 31010<br/>JDBC/psycopg2]
    
    Q4 -->|기타<br/>Go/Rust/.NET| Port31010d[✅ 포트 31010<br/>PostgreSQL Wire]
    
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

## PostgreSQL 프록시 연결 예제

### 1. psql CLI

```bash
# 간단한 연결
psql -h localhost -p 31010 -U admin -d datalake

# 직접 쿼리
psql -h localhost -p 31010 -U admin -d datalake \
  -c "SELECT COUNT(*) FROM MinIO.datalake.customers;"

# 대화형 모드
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

### 2. DBeaver 구성

```yaml
연결 유형: PostgreSQL
연결 이름: Dremio via PostgreSQL Proxy

기본:
  호스트: localhost
  포트: 31010
  데이터베이스: datalake
  사용자: admin
  비밀번호: [your-password]
  
드라이버 속성:
  ssl: false
  
고급:
  연결 시간 초과: 30000
  쿼리 시간 초과: 0
```

### 3. Python psycopg2

```python
import psycopg2
from psycopg2 import sql

# 연결
conn = psycopg2.connect(
    host="localhost",
    port=31010,
    database="datalake",
    user="admin",
    password="your-password"
)

# 커서
cursor = conn.cursor()

# 간단한 쿼리
cursor.execute("SELECT * FROM MinIO.datalake.customers LIMIT 10")
rows = cursor.fetchall()

for row in rows:
    print(row)

# 매개변수화된 쿼리
query = sql.SQL("SELECT * FROM {} WHERE state = %s").format(
    sql.Identifier("MinIO", "datalake", "customers")
)
cursor.execute(query, ("CA",))

# 닫기
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
        String password = "your-password";
        
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

### 5. ODBC 연결 문자열 (DSN)

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
Password=your-password
SSLMode=disable
Protocol=7.4
```

---

## Docker Compose 구성

### Dremio 포트 매핑

```yaml
services:
  dremio:
    image: dremio/dremio-oss:26.0
    container_name: dremio
    ports:
      # 포트 9047 - REST API / Web UI
      - "9047:9047"
      
      # 포트 31010 - PostgreSQL 프록시 (ODBC/JDBC)
      - "31010:31010"
      
      # 포트 32010 - Arrow Flight (성능)
      - "32010:32010"
    environment:
      - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Xms4g -Xmx8g
    volumes:
      - ./docker-volume/dremio:/opt/dremio/data
    networks:
      - data-platform
```

### 포트 검증

```bash
# 3개 포트 모두 열려 있는지 확인
netstat -an | grep -E '9047|31010|32010'

# REST API 테스트
curl -v http://localhost:9047

# PostgreSQL 프록시 테스트
psql -h localhost -p 31010 -U admin -d datalake -c "SELECT 1;"

# Arrow Flight 테스트 (Python 사용)
python3 -c "
from pyarrow import flight
client = flight.connect('grpc://localhost:32010')
print('Arrow Flight OK')
"
```

---

## 빠른 시각적 요약

### 3개 포트 한눈에 보기

| 포트 | 프로토콜 | 주요 사용 | 성능 | 호환성 |
|------|-----------|-------------|------------|----------------|
| **9047** | REST API | 🌐 Web UI, 관리 | ⭐⭐ 표준 | ⭐⭐⭐ 범용 |
| **31010** | PostgreSQL Wire | 💼 BI 도구, 마이그레이션 | ⭐⭐⭐ 양호 | ⭐⭐⭐ 우수 |
| **32010** | Arrow Flight | ⚡ 프로덕션, dbt, Superset | ⭐⭐⭐⭐⭐ 최고 | ⭐⭐ 제한적 |

### 선택 매트릭스

```mermaid
graph TB
    subgraph "선택 가이드"
        A["🎯 사용 사례"]
        
        A --> B1["웹 인터페이스<br/>구성"]
        A --> B2["레거시 BI 도구<br/>Arrow Flight 없음"]
        A --> B3["PostgreSQL 마이그레이션<br/>기존 JDBC 코드"]
        A --> B4["dbt, Superset<br/>프로덕션"]
        A --> B5["Python pyarrow<br/>분석"]
        
        B1 --> C1["포트 9047<br/>REST API"]
        B2 --> C2["포트 31010<br/>PostgreSQL"]
        B3 --> C2
        B4 --> C3["포트 32010<br/>Arrow Flight"]
        B5 --> C3
    end
    
    style A fill:#2196F3,color:#fff
    style C1 fill:#4CAF50,color:#fff,stroke:#000,stroke-width:2px
    style C2 fill:#336791,color:#fff,stroke:#000,stroke-width:2px
    style C3 fill:#FF5722,color:#fff,stroke:#000,stroke-width:2px
```

---

## 추가 리소스

### 관련 문서

- [아키텍처 - 구성 요소](./components.md) - "Dremio용 PostgreSQL 프록시" 섹션
- [가이드 - Dremio 설정](../guides/dremio-setup.md) - "PostgreSQL 프록시를 통한 연결" 섹션
- [구성 - Dremio](../getting-started/configuration.md) - `dremio.conf` 구성

### 공식 링크

- **Dremio 문서**: https://docs.dremio.com/
- **PostgreSQL Wire 프로토콜**: https://www.postgresql.org/docs/current/protocol.html
- **Apache Arrow Flight**: https://arrow.apache.org/docs/format/Flight.html

---

**버전**: 3.2.5  
**최종 업데이트**: 2025년 10월 16일  
**상태**: ✅ 완료
