# Arquitetura de fluxo de dados

**Versão**: 3.2.0  
**Última atualização**: 16 de outubro de 2025  
**Idioma**: Francês

## Índice

1. [Visão geral](#visão geral)
2. [Fluxo de dados ponta a ponta](#fluxo de dados ponta a ponta)
3. [Camada de ingestão](#camada de ingestão)
4. [Camada de armazenamento](#camada de armazenamento)
5. [Camada de processamento](#camada de processamento)
6. [Camada de apresentação](#camada de apresentação)
7. [Modelos de fluxo de dados](#dataflow-models)
8. [Considerações sobre desempenho](#considerações sobre desempenho)
9. [Monitoramento de fluxo de dados](#dataflow-monitoring)
10. [Boas Práticas](#boas-práticas)

---

## Visão geral

Este documento detalha a arquitetura completa do fluxo de dados da plataforma, desde a ingestão inicial de dados até o consumo final. Compreender esses fluxos é fundamental para otimizar o desempenho, solucionar problemas e projetar pipelines de dados eficazes.

### Princípios de Fluxo de Dados

Nossa arquitetura segue estes princípios fundamentais:

1. **Fluxo unidirecional**: os dados se movem em uma direção clara e previsível
2. **Processamento em camadas**: Cada camada tem uma responsabilidade específica
3. **Componentes dissociados**: os serviços se comunicam por meio de interfaces bem definidas
4. **Idempotência**: As operações podem ser repetidas com segurança
5. **Observabilidade**: Cada etapa é registrada e monitorada

### Camadas de Arquitetura

§§§CÓDIGO_0§§§

---

## Fluxo de dados ponta a ponta

### Sequência completa do pipeline

§§§CÓDIGO_1§§§

### Etapas do fluxo de dados

| Etapa | Componente | Entrada | Sair | Latência |
|-------|----------|--------|--------|---------|
| **Extrato** | Byte aéreo | APIs/BDs externos | JSON/CSV bruto | 1-60 minutos |
| **Carregando** | Camada de armazenamento | Arquivos brutos | Baldes selecionados | <1 minuto |
| **Catalogando** | Drêmio | Caminhos de armazenamento | Conjuntos de dados virtuais | <1 minuto |
| **Transformação** | dbt | Mesas de Bronze | Mesas Prata/Ouro | 5-30 minutos |
| **Otimização** | Pensamentos sobre Dremio | Consultas brutas | Resultados ocultos | Tempo real |
| **Visualização** | Superconjunto | Consultas SQL | Gráficos/Painéis | <5 seg |

---

## Camada de ingestão

### Extração de dados do Airbyte

Airbyte gerencia toda a ingestão de dados de fontes externas.

#### Fluxo de conexão de origem

§§§CÓDIGO_2§§§

#### Métodos de extração de dados

**1. Atualização completa**
§§§CÓDIGO_3§§§

**2. Sincronização incremental**
§§§CÓDIGO_4§§§

**3. Alterar captura de dados (CDC)**
§§§CÓDIGO_5§§§

### Integração API Airbyte

§§§CÓDIGO_6§§§

### Desempenho de extração

| Tipo de fonte | Fluxo | Frequência recomendada |
|----------------|-------|-----------|
| PostgreSQL | 50-100 mil linhas/seg | A cada 15-60 minutos |
| API REST | 1-10k necessidade/seg | A cada 5-30 minutos |
| Arquivos CSV | 100-500 MB/seg | Diariamente |
| MongoDB | 10-50 mil documentos/seg | A cada 15-60 minutos |
| CDC MySQL | Tempo real | Contínuo |

---

## Camada de armazenamento

### Armazenamento MinIO S3

MinIO armazena dados brutos e processados ​​em uma estrutura hierárquica.

#### Organização do intervalo

§§§CÓDIGO_7§§§

#### Estrutura do caminho de dados

§§§CÓDIGO_8§§§

### Estratégia de formato de armazenamento

| Camada | Formato | Compressão | Particionamento | Razão |
|----|--------|-------------|-----------------|--------|
| **Bronze** | Parquete | Rápido | Por data | Escrita rápida, boa compressão |
| **Prata** | Parquete | Rápido | Por chave de negócio | Consultas eficazes |
| **Ouro** | Parquete | ZSTD | Por período | Compressão Máxima |
| **Registros** | JSON | Gzip | Por serviço/data | Legível por humanos |

### Armazenamento de metadados PostgreSQL

Lojas PostgreSQL:
- Configuração e status do Airbyte
- Histórico de execução de metadados e dbt
- Superconjunto de painéis e usuários
- Logs e métricas de aplicativos

§§§CÓDIGO_9§§§

### Armazenamento de documentos do Elasticsearch

O Elasticsearch indexa logs e permite pesquisa de texto completo.

§§§CÓDIGO_10§§§

---

## Camada de Processamento

### Virtualização de dados Dremio

Dremio cria uma visão unificada em todas as fontes de armazenamento.

#### Criação de conjunto de dados virtual

§§§CÓDIGO_11§§§

#### Aceleração por Reflexos

As reflexões Dremio pré-calculam os resultados da consulta para desempenho instantâneo.

§§§CÓDIGO_12§§§

**Impacto das reflexões no desempenho:**

| Tipo de consulta | Sem Reflexão | Com Reflexão | Aceleração |
|-----------------|----------------|----------------|--------|
| SELECIONE Simples | 500ms | 50ms | 10x |
| Agregações | 5s | 100ms | 50x |
| JOINs complexos | 30 anos | 500ms | 60x |
| Varreduras grandes | 120 | 2s | 60x |

### transformações dbt

O dbt transforma dados brutos em modelos prontos para negócios.

#### Fluxo de Transformação

§§§CÓDIGO_13§§§

#### Exemplo de pipeline de transformação

§§§CÓDIGO_14§§§

§§§CÓDIGO_15§§§

§§§CÓDIGO_16§§§

#### Fluxo de execução do dbt

§§§CÓDIGO_17§§§

### Rastreabilidade da linhagem de dados

§§§CÓDIGO_18§§§

---

## Camada de apresentação

### Fluxo de execução de consulta

§§§CÓDIGO_19§§§

### Modelos de acesso API

#### 1. Painéis de superconjunto (BI interativo)

§§§CÓDIGO_20§§§

#### 2. API Arrow Flight (alto desempenho)

§§§CÓDIGO_21§§§

#### 3. API REST (integrações externas)

§§§CÓDIGO_22§§§

---

## Modelos de fluxo de dados

### Modelo 1: pipeline de lote ETL

§§§CÓDIGO_23§§§

### Modelo 2: streaming em tempo real

§§§CÓDIGO_24§§§

### Padrão 3: atualizações incrementais

§§§CÓDIGO_25§§§

### Modelo 4: Arquitetura Lambda (Lote + Stream)

§§§CÓDIGO_26§§§

---

## Considerações de desempenho

### Otimização de ingestão

§§§CÓDIGO_27§§§

### Otimização de armazenamento

§§§CÓDIGO_28§§§

### Otimização de consulta

§§§CÓDIGO_29§§§

### Otimização de Transformações

§§§CÓDIGO_30§§§

### Benchmarks de desempenho

| Operação | Conjunto de dados pequeno<br/>(1 milhão de linhas) | Conjunto de dados médio<br/>(100 milhões de linhas) | Grande conjunto de dados<br/>(1B linhas) |
|----------------------------|---------------------------|------------------------------------------|----------------------------|
| **Sincronizar Airbyte** | 2 minutos | 30 minutos | 5 horas |
| **execução de dbt** | 30 seg | 10 minutos | 2 horas |
| **Reflexão da Construção** | 10 seg | 5 minutos | 30 minutos |
| **Consulta no painel** | <100ms | <500ms | <2s |

---

## Monitoramento de fluxo de dados

### Principais métricas a serem rastreadas

§§§CÓDIGO_31§§§

### Painel de monitoramento

§§§CÓDIGO_32§§§

### Agregação de registros

§§§CÓDIGO_33§§§

---

## Melhores práticas

### Projeto de fluxo de dados

1. **Projeto para Idempotência**
   - Garantir que as operações possam ser repetidas com segurança
   - Use chaves exclusivas para desduplicação
   - Implementar tratamento de erros apropriado

2. **Implementar controles de qualidade de dados**
   §§§CÓDIGO_34§§§

3. **Particionar grandes conjuntos de dados**
   §§§CÓDIGO_35§§§

4. **Use modos de sincronização apropriados**
   - Atualização completa: tabelas de pequenas dimensões
   - Incremental: grandes tabelas de fatos
   - CDC: requisitos em tempo real

### Ajuste de desempenho

1. **Otimize o agendamento de sincronização do Airbyte**
   §§§CÓDIGO_36§§§

2. **Crie pensamentos estratégicos**
   §§§CÓDIGO_37§§§

3. **Otimizar modelos dbt**
   §§§CÓDIGO_38§§§

### Solução de problemas comuns

| Problema | Sintoma | Solução |
|--------|---------|----------|
| **Sincronização do Airbyte lenta** | Tempos para sincronizar | Aumente o tamanho do lote, use o modo incremental |
| **Falta de memória** | Modelos dbt com falha | Materialize de forma incremental, adicione particionamento |
| **Consultas lentas** | Painel de tempo limite | Crie reflexões, adicione índice |
| **Armazenamento cheio** | Falhas na escrita | Implementar retenção de dados, compactar dados antigos |
| **Dados Obsoletos** | Métricas antigas | Aumente a frequência de sincronização, verifique horários |

### Boas Práticas de Segurança

1. **Criptografar dados em trânsito**
   §§§CÓDIGO_39§§§

2. **Implementar controles de acesso**
   §§§CÓDIGO_40§§§

3. **Acesso a dados de auditoria**
   §§§CÓDIGO_41§§§

---

## Resumo

Este documento detalha a arquitetura completa do fluxo de dados:

- **Camada de ingestão**: Airbyte extrai dados de várias fontes por meio de atualização completa, incremental ou CDC
- **Camada de armazenamento**: MinIO, PostgreSQL e Elasticsearch armazenam dados brutos e processados ​​em camadas organizadas
- **Camada de processamento**: Dremio virtualiza os dados e dbt os transforma por meio de modelos de teste, intermediários e mart
- **Camada de apresentação**: painéis e APIs superconjuntos fornecem acesso a dados prontos para negócios

Pontos-chave a serem lembrados:
- Os dados fluem unidirecionalmente através de camadas claramente definidas
- Cada componente tem responsabilidades e interfaces específicas
- O desempenho é otimizado através de reflexões, particionamento e cache
- Monitoramento e observabilidade são integrados em cada camada
- Boas práticas garantem confiabilidade, desempenho e segurança

**Documentação relacionada:**
- [Visão geral da arquitetura](./overview.md)
- [Componentes](./components.md)
- [Implantação](./deployment.md)
- [Guia de integração Airbyte](../guides/airbyte-integration.md)
- [Guia de desenvolvimento dbt](../guides/dbt-development.md)

---

**Versão**: 3.2.0  
**Última atualização**: 16 de outubro de 2025