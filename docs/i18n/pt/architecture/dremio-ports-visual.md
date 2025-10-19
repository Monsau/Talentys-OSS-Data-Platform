# Guia visual das portas Dremio

**Versão**: 3.2.3  
**Última atualização**: 16 de outubro de 2025  
**Idioma**: Francês

---

## Visão geral dos 3 portos Dremio

§§§CÓDIGO_0§§§

---

## Arquitetura detalhada do proxy PostgreSQL

### Fluxo de Conexão do Cliente → Dremio

§§§CÓDIGO_1§§§

---

## Comparação de desempenho

### Benchmark: verificação de 100 GB de dados

§§§CÓDIGO_2§§§

### Taxa de dados

§§§CÓDIGO_3§§§

### Latência de consulta simples

| Protocolo | Porto | Latência média | Sobrecarga de rede |
|---------------|------|-----------------|-----------------|
| **API REST** | 9047 | 50-100ms | JSON (detalhado) |
| **Proxy PostgreSQL** | 31010 | 20-50ms | Protocolo Wire (compacto) |
| **Vôo de Flecha** | 32010 | 5-10ms | Apache Arrow (colunar binário) |

---

## Caso de uso por porta

### Porta 9047 - API REST

§§§CÓDIGO_4§§§

### Porta 31010 - Proxy PostgreSQL

§§§CÓDIGO_5§§§

### Porta 32010 - Voo Flecha

§§§CÓDIGO_6§§§

---

## Árvore de decisão: qual porta usar?

§§§CÓDIGO_7§§§

---

## Exemplos de conexão proxy PostgreSQL

### 1. CLI do psql

§§§CÓDIGO_8§§§

### 2. Configuração do DBeaver

§§§CÓDIGO_9§§§

### 3. Python com psycopg2

§§§CÓDIGO_10§§§

### 4.Java JDBC

§§§CÓDIGO_11§§§

### 5. Sequência ODBC (DSN)

§§§CÓDIGO_12§§§

---

## Configuração do Docker Compose

### Mapeamento do Porto Dremio

§§§CÓDIGO_13§§§

### Verificação de porta

§§§CÓDIGO_14§§§

---

## Resumo visual rápido

### Resumo das 3 portas

| Porto | Protocolo | Uso principal | Desempenho | Compatibilidade |
|------|----------|-------------|------------|---------------|
| **9047** | API REST | 🌐 Interface Web, Administrador | ⭐⭐Padrão | ⭐⭐⭐ Universal |
| **31010** | Fio PostgreSQL | 💼 Ferramentas de BI, Migração | ⭐⭐⭐ Bom | ⭐⭐⭐ Excelente |
| **32010** | Voo de Flecha | ⚡ Produção, dbt, Superset | ⭐⭐⭐⭐⭐ Máximo | ⭐⭐ Limitado |

### Matriz de seleção

§§§CÓDIGO_15§§§

---

## Recursos Adicionais

### Documentação Relacionada

- [Arquitetura - Componentes](./components.md) - Seção "PostgreSQL Proxy para Dremio"
- [Guia - Configuração do Dremio](../guides/dremio-setup.md) - Seção "Conexão via PostgreSQL Proxy"
- [Configuração - Dremio](../getting-started/configuration.md) - Parâmetros `dremio.conf`

### Links Oficiais

- **Documentação Dremio**: https://docs.dremio.com/
- **Protocolo PostgreSQL Wire**: https://www.postgresql.org/docs/current/protocol.html
- **Apache Arrow Flight**: https://arrow.apache.org/docs/format/Flight.html

---

**Versão**: 3.2.3  
**Última atualização**: 16 de outubro de 2025  
**Status**: ✅ Concluído