# Guia de configuração Dremio

**Versão**: 3.2.0  
**Última atualização**: 16 de outubro de 2025  
**Idioma**: Francês

## Índice

1. [Visão geral](#visão geral)
2. [Configuração inicial](#configuração inicial)
3. [Configuração da fonte de dados](#data-source-configuration)
4. [Conjuntos de dados virtuais](#conjuntos de dados virtuais)
5. [Pensamentos (consultas de aceleração)](#pensamentos-consultas de aceleração)
6. [Segurança e controle de acesso](#segurança-e-controle de acesso)
7. [Otimização de desempenho](#otimização de desempenho)
8. [Integração com dbt](#integração-com-dbt)
9. [Monitoramento e Manutenção](#monitoramento-e-manutenção)
10. [Solução de problemas](#solução de problemas)

---

## Visão geral

Dremio é a plataforma data lakehouse que fornece uma interface unificada para consultar dados em múltiplas fontes. Este guia cobre tudo, desde a configuração inicial até técnicas avançadas de otimização.

### O que é Dremio?

Dremio combina a flexibilidade de um data lake com o desempenho de um data warehouse:

- **Virtualização de dados**: consulte dados sem movê-los ou copiá-los
- **Aceleração de consulta**: cache automático com reflexões
- **Análise de autoatendimento**: os usuários empresariais podem explorar diretamente os dados
- **Padrão SQL**: nenhuma linguagem de consulta proprietária
- **Apache Arrow**: formato colunar de alto desempenho

### Principais recursos

| Recurso | Descrição | Lucro |
|----------------|---------|---------|
| **Pensamentos** | Aceleração de consulta inteligente | Consultas 10-100x mais rápidas |
| **Virtualização de dados** | Visão unificada das fontes | Sem duplicação de dados |
| **Vôo de Flecha** | Transferência de dados em alta velocidade | 20-50x mais rápido que ODBC/JDBC |
| **Camada Semântica** | Nomes de campos voltados para negócios | Análise de autoatendimento |
| **Git para dados** | Controle de versão do conjunto de dados | Colaboração e reversão |

---

## Configuração inicial

### Pré-requisitos

Antes de começar, certifique-se de ter:
- Contêiner Dremio em execução (consulte [Guia de instalação](../getting-started/installation.md))
- Acesso a fontes de dados (MinIO, PostgreSQL, etc.)
- Credenciais de administrador

### Primeira Conexão

§§§CÓDIGO_0§§§

#### Etapa 1: Acesse a interface do Dremio

Abra seu navegador e navegue até:
§§§CÓDIGO_1§§§

#### Etapa 2: Criar conta de administrador

Na primeira inicialização, você será solicitado a criar uma conta de administrador:

§§§CÓDIGO_2§§§

**Nota de segurança**: Use uma senha forte com pelo menos 12 caracteres, incluindo letras maiúsculas, minúsculas, números e caracteres especiais.

#### Etapa 3: configuração inicial

§§§CÓDIGO_3§§§

### Arquivos de configuração

A configuração do Dremio é gerenciada via `dremio.conf`:

§§§CÓDIGO_5§§§

### Variáveis ​​de Ambiente

§§§CÓDIGO_6§§§

### Conexão via proxy PostgreSQL

Dremio expõe uma interface compatível com PostgreSQL na porta 31010, permitindo que ferramentas compatíveis com PostgreSQL se conectem sem modificações.

#### Arquitetura de conexões Dremio

§§§CÓDIGO_7§§§

#### Fluxo de consulta via proxy PostgreSQL

§§§CÓDIGO_8§§§

#### Configuração de proxy

O proxy PostgreSQL é ativado automaticamente em `dremio.conf`:

§§§CÓDIGO_10§§§

#### Conexão com psql

§§§CÓDIGO_11§§§

#### Conexão com DBeaver/pgAdmin

Configuração de conexão:

§§§CÓDIGO_12§§§

#### Canais de conexão

**JDBC:**
§§§CÓDIGO_13§§§

**ODBC (DSN):**
§§§CÓDIGO_14§§§

**Python (psycopg2):**
§§§CÓDIGO_15§§§

#### Quando usar o proxy PostgreSQL

§§§CÓDIGO_16§§§

| Cenário | Use o proxy PostgreSQL | Usar voo de seta |
|--------|----------------------------|----------------------|
| **Ferramentas legadas de BI** (sem suporte para Arrow Flight) | ✅ Sim | ❌ Não |
| **Migração do PostgreSQL** (código JDBC/ODBC existente) | ✅ Sim | ❌ Não |
| **Produção de alto desempenho** | ❌ Não | ✅ Sim (20-50x mais rápido) |
| **Superset, dbt, ferramentas modernas** | ❌ Não | ✅ Sim |
| **Desenvolvimento/teste rápido** | ✅ Sim (familiar) | ⚠️ Ambos OK |

#### Comparação de desempenho das 3 portas

§§§CÓDIGO_17§§§

**Recomendação**: Use o proxy PostgreSQL (porta 31010) para **compatibilidade** e Arrow Flight (porta 32010) para **desempenho de produção**.

---

## Configurando fontes de dados

### Adicionar fonte MinIO S3

MinIO é o seu principal armazenamento de data lake.

#### Etapa 1: navegar até as fontes

§§§CÓDIGO_18§§§

#### Etapa 2: configurar a conexão S3

§§§CÓDIGO_19§§§

#### Etapa 3: testar a conexão

§§§CÓDIGO_20§§§

**Resultado esperado**:
§§§CÓDIGO_21§§§

### Adicionar fonte PostgreSQL

#### Configurar

§§§CÓDIGO_22§§§

§§§CÓDIGO_23§§§

### Adicionar fonte do Elasticsearch

§§§CÓDIGO_24§§§

### Organização das Fontes

§§§CÓDIGO_25§§§

---

## Conjuntos de dados virtuais

Os conjuntos de dados virtuais permitem criar visualizações transformadas e reutilizáveis ​​dos seus dados.

### Criar conjuntos de dados virtuais

#### Do Editor SQL

§§§CÓDIGO_26§§§

**Salvar localização**:
§§§CÓDIGO_27§§§

#### Da interface

§§§CÓDIGO_28§§§

**Passos**:
1. Navegue até a fonte MinIO
2. Navegue até `datalake/bronze/customers/`
3. Clique no botão “Formatar arquivos”
4. Examine o padrão detectado
5. Clique em “Salvar” para promover para o conjunto de dados

### Organização de conjuntos de dados

Crie estrutura lógica com Espaços e Pastas:

§§§CÓDIGO_30§§§

### Camada Semântica

Adicione nomes e descrições voltados para negócios:

§§§CÓDIGO_31§§§

**Adicionar descrições**:
§§§CÓDIGO_32§§§

---

## Reflexões (consultas de aceleração)

Reflexões são o mecanismo de cache inteligente do Dremio que melhora significativamente o desempenho da consulta.

### Tipos de reflexões

#### 1. Reflexões brutas

Armazene subconjunto de colunas para recuperação rápida:

§§§CÓDIGO_33§§§

**Caso de uso**:
- Painéis consultando colunas específicas
- Relatórios com subconjuntos de colunas
- Consultas exploratórias

#### 2. Reflexões de agregação

Pré-calcule agregações para resultados instantâneos:

§§§CÓDIGO_34§§§

**Caso de uso**:
- Painéis executivos
- Relatórios resumidos
- Análise de tendências

### Reflexão de configuração

§§§CÓDIGO_35§§§

#### Política de Refrescos

§§§CÓDIGO_36§§§

**Opções**:
- **Nunca atualizar**: dados estáticos (por exemplo, arquivos históricos)
- **Atualizar a cada [1 hora]**: atualizações periódicas
- **Atualizar quando o conjunto de dados for alterado**: sincronização em tempo real

§§§CÓDIGO_37§§§

#### Política de Expiração

§§§CÓDIGO_38§§§

### Boas Práticas para Reflexões

#### 1. Comece com consultas de alto valor

Identifique consultas lentas no histórico:

§§§CÓDIGO_39§§§

#### 2. Crie reflexões direcionadas

§§§CÓDIGO_40§§§

#### 3. Monitore o reflexo da cobertura

§§§CÓDIGO_41§§§

### Pensamentos sobre desempenho de impacto

| Tamanho do conjunto de dados | Digite Consulta | Sem Reflexão | Com Reflexão | Aceleração |
|----------------|------------|----------------|----------------|-------------|
| 1 milhão de linhas | SELECIONE Simples | 500ms | 50ms | 10x |
| 10 milhões de linhas | Agregação | 15 anos | 200ms | 75x |
| 100 milhões de linhas | Complexo JOIN | 2 minutos | 1s | 120x |
| Linhas 1B | AGRUPAR POR | 10 minutos | 5s | 120x |

---

## Segurança e Controle de Acesso

### Gerenciamento de usuários

#### Criar usuários

§§§CÓDIGO_42§§§

§§§CÓDIGO_43§§§

#### Funções do usuário

| Função | Permissões | Casos de uso |
|------|-------------|-------------|
| **Administrador** | Acesso completo | Administração do sistema |
| **Usuário** | Consultar, criar conjuntos de dados pessoais | Analistas, cientistas de dados |
| **Usuário Limitado** | Somente consulta, não criação de conjunto de dados | Usuários empresariais, visualizadores |

### Permissões de espaço

§§§CÓDIGO_44§§§

**Tipos de permissão**:
- **Visualizar**: pode visualizar e consultar conjuntos de dados
- **Modificar**: pode editar definições de conjunto de dados
- **Gerenciar concessões**: pode gerenciar permissões
- **Proprietário**: Controle total

**Exemplo**:
§§§CÓDIGO_45§§§

### Segurança em nível de linha

Implemente a filtragem em nível de linha:

§§§CÓDIGO_46§§§

### Coluna de nível de segurança

Ocultar colunas confidenciais:

§§§CÓDIGO_47§§§

### Integração OAuth

§§§CÓDIGO_48§§§

---

## Otimização de desempenho

### Técnicas de otimização de consulta

#### 1. Remoção de partição

§§§CÓDIGO_49§§§

#### 2. Poda de coluna

§§§CÓDIGO_50§§§

#### 3. Pushdown de predicado

§§§CÓDIGO_51§§§

#### 4. Otimização de adesão

§§§CÓDIGO_52§§§

### Configuração de memória

§§§CÓDIGO_53§§§

### Dimensionamento de cluster

| Tipo de carga | Coordenador | Executores | Cluster total |
|------------|---------|------------|-----------|
| **Pequeno** | 4 CPUs, 16 GB | 2x (8 CPUs, 32 GB) | 20 CPUs, 80 GB |
| **Médio** | 8 CPUs, 32 GB | 4x (16 CPUs, 64 GB) | 72 CPU, 288 GB |
| **Grande** | 16 CPUs, 64 GB | 8x (32 CPUs, 128 GB) | CPU 272, 1088 GB |

### Monitoramento de desempenho

§§§CÓDIGO_54§§§

---

## Integração com dbt

### Dremio como alvo dbt

Configurar `profiles.yml`:

§§§CÓDIGO_56§§§

### modelos dbt no Dremio

§§§CÓDIGO_57§§§

### Explorar reflexões em dbt

§§§CÓDIGO_58§§§

---

## Monitoramento e Manutenção

### Principais métricas a serem monitoradas

§§§CÓDIGO_59§§§

### Tarefas de Manutenção

#### 1. Atualizar pensamentos

§§§CÓDIGO_60§§§

#### 2. Limpe dados antigos

§§§CÓDIGO_61§§§

#### 3. Atualizar estatísticas

§§§CÓDIGO_62§§§

---

## Solução de problemas

### Problemas Comuns

#### Problema 1: desempenho lento de consulta

**Sintomas**: consultas demorando minutos em vez de segundos

**Diagnóstico**:
§§§CÓDIGO_63§§§

**Soluções**:
1. Crie pensamentos apropriados
2. Adicione filtros de remoção de partição
3. Aumente a memória do executor
4. Ativar fila de espera

#### Problema 2: A reflexão não constrói

**Sintomas**: Reflexo preso no estado “REFRESHING”

**Diagnóstico**:
§§§CÓDIGO_64§§§

**Soluções**:
1. Verifique os dados de origem para alterações de esquema
2. Verifique espaço em disco suficiente
3. Aumente a reflexão da construção do tempo limite
4. Desative e reative a reflexão

#### Problema 3: Tempo limite de conexão

**Sintomas**: erros de “tempo limite de conexão” ao consultar fontes

**Soluções**:
§§§CÓDIGO_65§§§

#### Problema 4: Falta de memória

**Sintomas**: "OutOfMemoryError" nos registros

**Soluções**:
§§§CÓDIGO_66§§§

### Consultas de diagnóstico

§§§CÓDIGO_67§§§

---

## Resumo

Este guia abrangente cobre:

- **Configuração inicial**: configuração inicial, criação de conta de administrador, arquivos de configuração
- **Fontes de dados**: Conexão MinIO, PostgreSQL e Elasticsearch
- **Conjuntos de dados virtuais**: Criação de visualizações transformadas reutilizáveis ​​com camada semântica
- **Reflexões**: reflexões brutas e agregação para aceleração de consulta de 10 a 100x
- **Segurança**: gerenciamento de usuários, permissões de espaço, segurança em nível de linha/coluna
- **Desempenho**: otimização de consulta, configuração de memória, dimensionamento de cluster
- **integração dbt**: use Dremio como alvo dbt com gerenciamento de reflexão
- **Monitoramento**: principais métricas, tarefas de manutenção, solicitações de diagnóstico
- **Solução de problemas**: problemas e soluções comuns

Pontos-chave a serem lembrados:
- Dremio fornece interface SQL unificada em todas as fontes de dados
- Pensamentos essenciais para o desempenho da produção
- A configuração de segurança adequada permite análises de autoatendimento
- O monitoramento regular garante um desempenho ideal

**Documentação relacionada:**
- [Componentes de arquitetura](../architecture/components.md)
- [Fluxo de dados](../architecture/data-flow.md)
- [Guia de desenvolvimento dbt](./dbt-development.md)
- [Integração Airbyte](./airbyte-integration.md)

---

**Versão**: 3.2.0  
**Última atualização**: 16 de outubro de 2025