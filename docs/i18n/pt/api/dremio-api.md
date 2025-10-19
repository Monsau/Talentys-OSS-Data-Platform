# Referência da API Dremio

**Versão**: 3.2.0  
**Última atualização**: 16 de outubro de 2025  
**Idioma**: Francês

## Índice

1. [Visão geral](#visão geral)
2. [Autenticação](#autenticação)
3. [API REST](#api-rest)
4. [Arrow Flight SQL](#arrow-flight-sql)
5. [ODBC/JDBC](#odbcjdbc)
6. [Cliente Python](#client-python)
7. [Cliente Java](#java-client)
8. [Exemplos de API](#dapi-examples)

---

## Visão geral

Dremio fornece várias APIs para interagir com o data lakehouse:

| Tipo de API | Casos de uso | Porto | Protocolo |
|------------|--------|------|----------|
| API REST | Gestão, metadados | 9047 | HTTP/HTTPS |
| ArrowFlightSQL | Consultas de alto desempenho | 32010 | gRPC |
| ODBC | Conectividade da ferramenta de BI | 31010 | ODBC |
| JDBC | Aplicativos Java | 31010 | JDBC |

### Arquitetura de API

§§§CÓDIGO_0§§§

---

## Autenticação

### Gere um token de autenticação

**Ponto final**: `POST /apiv2/login`

**Solicitar** :
§§§CÓDIGO_2§§§

**Responder** :
§§§CÓDIGO_3§§§

### Use o token nas solicitações

§§§CÓDIGO_4§§§

### Expiração do token

Os tokens expiram após 24 horas por padrão. Configurar em `dremio.conf`:

§§§CÓDIGO_6§§§

---

## API REST

### URL base

§§§CÓDIGO_7§§§

### Cabeçalhos comuns

§§§CÓDIGO_8§§§

### Gerenciamento de catálogo

#### Listar itens do catálogo

**Ponto final**: `GET /catalog`

§§§CÓDIGO_10§§§

**Responder** :
§§§CÓDIGO_11§§§

#### Obtenha um item de catálogo por caminho

**Ponto final**: `GET /catalog/by-path/{path}`

§§§CÓDIGO_13§§§

**Responder** :
§§§CÓDIGO_14§§§

### Conjuntos de dados virtuais (VDS)

#### Crie um conjunto de dados virtual

**Ponto final**: `POST /catalog`

§§§CÓDIGO_16§§§

**Responder** :
§§§CÓDIGO_17§§§

#### Atualizar um conjunto de dados virtual

**Ponto final**: `PUT /catalog/{id}`

§§§CÓDIGO_19§§§

#### Excluir um conjunto de dados

**Ponto final**: `DELETE /catalog/{id}?tag={tag}`

§§§CÓDIGO_21§§§

### Execução SQL

#### Execute uma consulta SQL

**Ponto final**: `POST /sql`

§§§CÓDIGO_23§§§

**Responder** :
§§§CÓDIGO_24§§§

### Gerenciamento de trabalho

#### Obtenha o status de um trabalho

**Ponto final**: `GET /job/{jobId}`

§§§CÓDIGO_26§§§

**Responder** :
§§§CÓDIGO_27§§§

#### Listar empregos recentes

**Ponto final**: `GET /jobs`

§§§CÓDIGO_29§§§

#### Cancelar um trabalho

**Ponto final**: `POST /job/{jobId}/cancel`

§§§CÓDIGO_31§§§

###Reflexões

#### Listar reflexões

**Ponto final**: `GET /reflections`

§§§CÓDIGO_33§§§

**Responder** :
§§§CÓDIGO_34§§§

#### Crie um reflexo

**Ponto final**: `POST /reflections`

§§§CÓDIGO_36§§§

### Gerenciamento de fontes

#### Adicionar uma fonte S3

**Ponto final**: `PUT /source/{name}`

§§§CÓDIGO_38§§§

#### Atualizar metadados de origem

**Ponto final**: `POST /source/{name}/refresh`

§§§CÓDIGO_40§§§

---

## Arrow Flight SQL

Arrow Flight SQL fornece execução de consultas de alto desempenho (20-50x mais rápido que ODBC/JDBC).

### Cliente Python com PyArrow

#### Instalação

§§§CÓDIGO_41§§§

#### Conexão e consulta

§§§CÓDIGO_42§§§

#### Exemplo: Consulta com parâmetros

§§§CÓDIGO_43§§§

#### Processamento em lote

§§§CÓDIGO_44§§§

### Comparação de desempenho

§§§CÓDIGO_45§§§

---

## ODBC/JDBC

### Conexão ODBC

#### Configuração do Windows

1. **Baixe o driver ODBC**:
   §§§CÓDIGO_46§§§

2. **Configurar o DSN**:
   §§§CÓDIGO_47§§§

3. **Cadeia de conexão**:
   §§§CÓDIGO_48§§§

#### Configuração do Linux

§§§CÓDIGO_49§§§

### Conexão JDBC

#### Baixe o driver

§§§CÓDIGO_50§§§

#### Cadeia de conexão

§§§CÓDIGO_51§§§

#### Propriedades

§§§CÓDIGO_52§§§

---

## Cliente Python

### Exemplo completo

§§§CÓDIGO_53§§§

---

## Cliente Java

### Dependência do Maven

§§§CÓDIGO_54§§§

### Exemplo completo

§§§CÓDIGO_55§§§

---

## Exemplos de API

### Exemplo 1: relatórios automatizados

§§§CÓDIGO_56§§§

### Exemplo 2: Exportação de dados

§§§CÓDIGO_57§§§

### Exemplo 3: descoberta de metadados

§§§CÓDIGO_58§§§

---

## Resumo

Esta referência de API cobriu:

- **Autenticação**: autenticação baseada em token com API REST
- **API REST**: Catálogo, execução SQL, trabalhos, reflexões
- **Arrow Flight SQL**: consultas de alto desempenho (20-50x mais rápidas)
- **ODBC/JDBC**: conectividade da ferramenta de BI
- **Cliente Python**: implementação completa do cliente
- **Cliente Java**: exemplos JDBC
- **Exemplos práticos**: Relatórios, exportação, descoberta de metadados

**Principais conclusões**:
- Use Arrow Flight SQL para acesso a dados de alto desempenho
- Use API REST para gerenciamento e automação
- Utilizar ODBC/JDBC para integração de ferramentas de BI
- Sempre use tokens de autenticação
- Processe consultas grandes em lotes para melhor desempenho

**Documentação relacionada:**
- [Guia de configuração do Dremio](../guides/dremio-setup.md)
- [Arquitetura: Fluxo de Dados](../architecture/data-flow.md)
- [guia de desenvolvimento dbt](../guides/dbt-development.md)

---

**Versão**: 3.2.0  
**Última atualização**: 16 de outubro de 2025