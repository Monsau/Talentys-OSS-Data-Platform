# Componentes da plataforma

**Versão**: 3.2.0  
**Última atualização**: 16/10/2025  
**Idioma**: Francês

---

## Visão geral dos componentes

A Plataforma de Dados consiste em 7 componentes principais que trabalham juntos para fornecer uma solução completa.

§§§CÓDIGO_0§§§

---

## 1. Airbyte – Plataforma de integração de dados

### Visão geral

Airbyte é um mecanismo de integração de dados de código aberto que consolida dados de múltiplas fontes até destinos.

**Versão**: 0.50.33  
**Licença**: MIT  
**Site**: https://airbyte.com

### Principais recursos

- **Mais de 300 conectores pré-construídos**: bancos de dados, APIs, arquivos, aplicativos SaaS
- **Change Data Capture (CDC)**: replicação de dados em tempo real
- **Conectores personalizados**: crie com Python ou CDK de baixo código
- **Normalização**: Transforme JSON em tabelas relacionais
- **Sincronização Incremental**: Sincronize apenas dados novos/modificados
- **Monitoramento**: sincronização integrada de status de rastreamento

### Arquitetura

§§§CÓDIGO_1§§§

### Caso de uso

- **Pipelines ELT**: fluxos de trabalho extrair-carregar-transformar
- **Replicação de banco de dados**: mantenha os bancos de dados sincronizados
- **Integração de API**: extraia dados de APIs REST
- **Ingestão do Data Lake**: Carregar dados no S3/MinIO
- **Migração para a nuvem**: mova dados locais para a nuvem

### Configurar

§§§CÓDIGO_2§§§

### Pontos de Integração

- **Saídas para**: MinIO S3, PostgreSQL, Dremio
- **Orquestração**: Pode ser acionado por Airflow, Prefect
- **Monitoramento**: endpoint de métricas do Prometheus

---

## 2. Dremio – Plataforma Data Lakehouse

### Visão geral

Dremio fornece uma interface SQL unificada para todas as fontes de dados com aceleração de consulta.

**Versão**: OSS 26.0  
**Licença**: Apache 2.0  
**Site**: https://www.dremio.com

### Principais recursos

- **Data Lakehouse**: Combine a flexibilidade do lago com o desempenho do armazém
- **Reflexões**: Aceleração automática de consultas (até 100x mais rápida)
- **Arrow Flight**: transferência de dados de alto desempenho
- **Virtualização de dados**: consulte sem mover dados
- **Camada Semântica**: Definições de dados favoráveis ​​aos negócios
- **Viagem no Tempo**: Consulta de versões históricas

### Arquitetura

§§§CÓDIGO_3§§§

### Caso de uso

- **Análise de autoatendimento**: permite que usuários empresariais explorem dados
- **Data Mesh**: acesso federado aos dados
- **Aceleração de consultas**: acelere as consultas do painel
- **Catálogo de dados**: descubra e gerencie dados
- **Ativação de BI**: Power Tableau, Power BI, Superset

### Configurar

§§§CÓDIGO_4§§§

### Pontos de Integração

- **Lê de**: MinIO S3, PostgreSQL, Elasticsearch
- **Transformar com**: dbt
- **Usado para**: Superset, Tableau, Power BI

### Proxy PostgreSQL para Dremio

O Dremio pode emular um servidor PostgreSQL, permitindo que ferramentas compatíveis com PostgreSQL se conectem ao Dremio como se fosse um banco de dados PostgreSQL padrão.

#### Arquitetura de proxy PostgreSQL

§§§CÓDIGO_5§§§

#### Comparação dos 3 Portos Dremio

§§§CÓDIGO_6§§§

#### Configuração de proxy

§§§CÓDIGO_7§§§

#### Casos de uso de proxy

1. **Ferramentas legadas de BI**: conecte ferramentas que não oferecem suporte ao Arrow Flight
2. **Migração Fácil**: Substitua PostgreSQL por Dremio sem alterar o código
3. **Compatibilidade ODBC/JDBC**: Use drivers PostgreSQL padrão
4. **Desenvolvimento**: Teste com ferramentas familiares do PostgreSQL (psql, pgAdmin)

#### Exemplo de conexão

§§§CÓDIGO_8§§§

#### Limitações

- **Desempenho**: Arrow Flight (porta 32010) é 20-50x mais rápido
- **Recursos**: Algumas funções avançadas do PostgreSQL não são suportadas
- **Recomendação**: Use Arrow Flight para produção, proxy PostgreSQL para compatibilidade

#### Fluxo de conexão via proxy PostgreSQL

§§§CÓDIGO_9§§§

#### Comparação de protocolos

| Protocolo | Porto | Desempenho | Latência | Casos de uso |
|---------------|------|-------------|---------|--------|
| **API REST** | 9047 | Padrão | ~50-100ms | UI da Web, administração |
| **ODBC/JDBC (proxy PostgreSQL)** | 31010 | Bom | ~20-50ms | Ferramentas legadas de BI, compatibilidade |
| **Vôo de Flecha** | 32010 | Excelente (20-50x) | ~5-10ms | Produção, Superconjunto, dbt |

#### Desempenho Comparativo

§§§CÓDIGO_10§§§

---

## 3. dbt - Ferramenta de transformação de dados

### Visão geral

dbt (ferramenta de construção de dados) permite que engenheiros analíticos transformem dados usando SQL.

**Versão**: 1.10+  
**Licença**: Apache 2.0  
**Site**: https://www.getdbt.com

### Principais recursos

- **Baseado em SQL**: Gravar transformações em SQL
- **Controle de versão**: integração Git para colaboração
- **Testes**: testes integrados de qualidade de dados
- **Documentação**: geração automática de dicionários de dados
- **Modularidade**: macros e pacotes reutilizáveis
- **Modelos Incrementais**: processe apenas novos dados

### Arquitetura

§§§CÓDIGO_11§§§

### Caso de uso

- **Modelagem de dados**: crie diagramas estrela/floco
- **Qualidade dos dados**: valide a integridade dos dados
- **Dimensões que mudam lentamente**: acompanhe as alterações históricas
- **Agregação de dados**: crie tabelas de resumo
- **Documentação de dados**: Gere catálogos de dados

### Configurar

§§§CÓDIGO_12§§§

### Pontos de Integração

- **Leitura de**: Conjuntos de dados Dremio
- **Escrito para**: Dremio (via Arrow Flight)
- **Orquestrado por**: Airflow, cron, Airbyte pós-sincronização

---

## 4. Apache Superset – Plataforma de Business Intelligence

### Visão geral

Superset é uma plataforma moderna de exploração e visualização de dados.

**Versão**: 3.0  
**Licença**: Apache 2.0  
**Site**: https://superset.apache.org

### Principais recursos

- **SQL IDE**: editor SQL avançado com preenchimento automático
- **Visualizações avançadas**: mais de 50 tipos de gráficos
- **Painéis interativos**: detalhamento, filtros, filtragem cruzada
- **SQL Lab**: interface de consulta ad hoc
- **Alertas**: relatórios e alertas programados
- **Cache**: armazena em cache os resultados da consulta para desempenho

### Arquitetura

§§§CÓDIGO_13§§§

### Caso de uso

- **Painéis Executivos**: monitoramento de KPI
- **Análise operacional**: monitoramento em tempo real
- **Autoatendimento de BI**: capacitar analistas
- **Análise incorporada**: integração de iframe em aplicativos
- **Exploração de dados**: análise ad hoc

### Configurar

§§§CÓDIGO_14§§§

### Pontos de Integração

- **Pedidos**: Dremio (via Arrow Flight)
- **Autenticação**: LDAP, OAuth2, Banco de Dados
- **Alertas**: E-mail, Slack

---

## 5. PostgreSQL - Banco de Dados Relacional

### Visão geral

PostgreSQL é um sistema avançado de gerenciamento de banco de dados relacional de código aberto.

**Versão**: 16  
**Licença**: Licença PostgreSQL  
**Site**: https://www.postgresql.org

### Principais recursos

- **Conformidade ACID**: transações confiáveis
- **Suporte JSON**: tipos JSON/JSONB nativos
- **Pesquisa de texto completo**: recursos de pesquisa integrados
- **Extensões**: PostGIS, pg_stat_statements, TimescaleDB
- **Replicação**: replicação de streaming, replicação lógica
- **Particionamento**: particionamento de tabela nativa

### Arquitetura

§§§CÓDIGO_15§§§

### Caso de uso

- **Armazenamento de metadados**: armazena metadados do sistema
- **Cargas Transacionais**: Aplicações OLTP
- **Tabelas intermediárias**: processamento temporário de dados
- **Configuração de armazenamento**: configurações do aplicativo
- **Registros de auditoria**: rastreie alterações no sistema

### Configurar

§§§CÓDIGO_16§§§

### Pontos de Integração

- **Leitura por**: Dremio, Superset, Airbyte
- **Escrito por**: Airbyte, dbt, aplicativos
- **Gerenciado por**: backups automatizados, replicação

---

## 6. MinIO – Armazenamento de objetos compatível com S3

### Visão geral

MinIO é um sistema de armazenamento de objetos compatível com S3 de alto desempenho.

**Versão**: Mais recente  
**Licença**: AGPLv3  
**Site**: https://min.io

### Principais recursos

- **API S3**: 100% compatível com Amazon S3
**Alto desempenho**: taxa de transferência de vários GB/s
- **Erasure Coding**: dados de sustentabilidade e disponibilidade
- **Versionamento**: controle de versão do objeto
- **Criptografia**: lado do servidor e lado do cliente
- **Multinuvem**: implante em qualquer lugar

### Arquitetura

§§§CÓDIGO_17§§§

### Caso de uso

- **Data Lake**: Armazene dados brutos e processados
- **Armazenamento de objetos**: arquivos, imagens, vídeos
- **Backup de armazenamento**: backups de banco de dados e sistema
- **Arquivo**: retenção de dados a longo prazo
- **Data Staging**: armazenamento de processamento temporário

### Configurar

§§§CÓDIGO_18§§§

### Pontos de Integração

- **Escrito por**: Airbyte, dbt, aplicativos
- **Leitura por**: Dremio, cientistas de dados
- **Gerenciado por**: mc (Cliente MinIO), s3cmd

---

## 7. Elasticsearch - mecanismo de pesquisa e análise

### Visão geral

Elasticsearch é um mecanismo distribuído de pesquisa e análise desenvolvido no Apache Lucene.

**Versão**: 8.15  
**Licença**: Licença Elastic 2.0  
**Site**: https://www.elastic.co

### Principais recursos

- **Pesquisa de texto completo**: recursos de pesquisa avançados
- **Indexação em tempo real**: disponibilidade de dados quase em tempo real
- **Distribuído**: escalabilidade horizontal
- **Agregações**: análises complexas
- **API RESTful**: API HTTP simples
- **Aprendizado de máquina**: detecção de anomalias

### Arquitetura

§§§CÓDIGO_19§§§

### Caso de uso

- **Registros analíticos**: registro centralizado (pilha ELK)
- **Pesquisa de aplicativos**: catálogos de produtos, pesquisa de sites
- **Análise de segurança**: casos de uso de SIEM
- **Observabilidade**: métricas e rastreamentos
- **Text Analytics**: PNL e análise de sentimento

### Configurar

§§§CÓDIGO_20§§§

### Pontos de Integração

- **Indexado por**: Logstash, Filebeat
- **Solicitado por**: Dremio, Kibana
- **Monitorado por**: Elasticsearch Monitoring

---

## Comparação de componentes

| Componente | Tipo | Uso principal | Escalabilidade | Estado |
|---------------|------|-----------------|-------------|------|
| **Byte aéreo** | Integração | Ingestão de dados | Horizontal (trabalhadores) | Apátrida |
| **Drêmio** | Mecanismo de consulta | Acesso a dados | Horizontal (executores) | Apátrida |
| **dbt** | Transformação | Modelagem de dados | Vertical (corações) | Apátrida |
| **Superconjunto** | Plataforma de BI | Visualização | Horizontal (teia) | Apátrida |
| **PostgreSQL** | Banco de dados | Armazenamento de metadados | Vertical (+ replicação) | Com estado |
| **MínIO** | Armazenamento de objetos | Lago de dados | Horizontal (distribuído) | Com estado |
| **Elasticsearch** | Mecanismo de pesquisa | Pesquisa de texto completo | Horizontal (cluster) | Com estado |

---

## Requisitos de recursos

### Configuração Mínima (Desenvolvimento)

§§§CÓDIGO_21§§§

### Configuração recomendada (produção)

§§§CÓDIGO_22§§§

---

## Matriz de compatibilidade de versão

| Componente | Liberação | Compatível com |
|----------|------------|-----------|
| Byte aéreo | 0,50+ | Todos os destinos |
| Drêmio | 26,0 | dbt 1.8+, clientes Arrow Flight |
| dbt | 1,10+ | Drêmio 23.0+ |
| Superconjunto | 3.0+ | Dremio 22.0+, PostgreSQL 12+ |
| PostgreSQL | 16 | Todos os componentes |
| MinIO | Mais recentes | Clientes compatíveis com S3 |
| Elasticsearch | 8.15 | Dremio 26.0+, Logstash 8.x |

---

**Versão do guia de componentes**: 3.2.0  
**Última atualização**: 16/10/2025  
**Mantido por**: Equipe da plataforma de dados