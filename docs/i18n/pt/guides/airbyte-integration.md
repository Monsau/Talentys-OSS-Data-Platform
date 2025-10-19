# Guia de integração Airbyte

**Versão**: 3.2.0  
**Última atualização**: 16 de outubro de 2025  
**Idioma**: Francês

---

## Visão geral

Airbyte é uma plataforma de integração de dados de código aberto que simplifica a movimentação de dados de várias fontes para destinos. Este guia cobre a integração do Airbyte na plataforma de dados, configuração de conectores e estabelecimento de pipelines de dados.

§§§CÓDIGO_0§§§

---

## O que é Airbyte?

### Principais recursos

- **Mais de 300 conectores pré-construídos**: APIs, bancos de dados, arquivos, aplicativos SaaS
- **Código aberto**: auto-hospedado com controle total de dados
- **Change Data Capture (CDC)**: sincronização de dados em tempo real
- **Conectores personalizados**: crie conectores com Python ou CDK de baixo código
- **Normalização de dados**: transforme JSON bruto em tabelas estruturadas
- **Monitoramento e alertas**: rastreie o status de sincronização e a qualidade dos dados

### Arquitetura

§§§CÓDIGO_1§§§

---

## Instalação

### Início rápido

Airbyte está incluído na plataforma. Comece com:

§§§CÓDIGO_2§§§

### Serviços iniciados

| Serviços | Porto | Descrição |
|--------|------|-------------|
| **airbyte-webapp** | 8.000 | Interface de usuário da Web |
| **servidor airbyte** | 8001 | Servidor API |
| **trabalhador de airbyte** | - | Mecanismo de execução de trabalho |
| **airbyte-temporal** | 7233 | Orquestração de fluxo de trabalho |
| **airbyte-db** | 5432 | Banco de dados de metadados (PostgreSQL) |

### Primeiro acesso

**Interface Web:**
§§§CÓDIGO_3§§§

**Identificadores padrão:**
- **E-mail**: `airbyte@example.com`
- **Senha**: `password`

**Altere a senha** ao fazer login pela primeira vez por segurança.

---

## Configuração

### Assistente de configuração

No primeiro acesso, conclua o assistente de configuração:

1. **Preferências de e-mail**: configurar notificações
2. **Residência de Dados**: Selecione o local de armazenamento de dados
3. **Estatísticas de uso anônimo**: Aceitar/recusar telemetria

### Configurações do espaço de trabalho

Navegue até **Configurações > Espaço de trabalho**:

§§§CÓDIGO_6§§§

### Limites de recursos

**Arquivo**: `config/airbyte/config.yaml`

§§§CÓDIGO_8§§§

---

## Conectores

### Conectores de origem

#### Fonte PostgreSQL

**Caso de uso**: Extraia dados do banco de dados transacional

**Configuração:**

1. Navegue até **Fontes > Nova Fonte**
2. Selecione **PostgreSQL**
3. Configure a conexão:

§§§CÓDIGO_9§§§

**Teste de conexão** → **Configurar fonte**

#### Fonte da API REST

**Caso de uso**: extrair dados de APIs

**Configuração:**

§§§CÓDIGO_10§§§

#### Arquivo fonte (CSV)

**Caso de uso**: importar arquivos CSV

**Configuração:**

§§§CÓDIGO_11§§§

#### Fontes Comuns

| Fonte | Casos de uso | Suporte CDC |
|--------|--------|-------------|
| **PostgreSQL** | Quadrinhos transacionais | ✅ Sim |
| **MySQL** | Quadrinhos transacionais | ✅ Sim |
| **MongoDB** | Documentos NoSQL | ✅ Sim |
| **Força de Vendas** | Dados de CRM | ❌ Não |
| **Planilhas Google** | Planilhas | ❌ Não |
| **Faixa** | Dados de pagamento | ❌ Não |
| **API REST** | APIs personalizadas | ❌ Não |
| **S3** | Armazenamento de arquivos | ❌ Não |

### Conectores de destino

#### Destino MinIO S3

**Caso de uso**: Armazene dados brutos no data lake

**Configuração:**

1. Navegue até **Destinos > Novo destino**
2. Selecione **S3**
3. Configure a conexão:

§§§CÓDIGO_12§§§

**Testar conexão** → **Configurar destino**

#### Destino PostgreSQL

**Caso de uso**: Carregar dados transformados para análise

**Configuração:**

§§§CÓDIGO_13§§§

#### Destino Dremio

**Caso de uso**: carregamento direto no data lakehouse

**Configuração:**

§§§CÓDIGO_14§§§

---

## Conexões

### Crie uma conexão

Uma conexão liga uma origem a um destino.

§§§CÓDIGO_15§§§

#### Passo a passo

1. **Navegue até Conexões > Nova Conexão**

2. **Selecionar fonte**: Escolha a fonte configurada (ex: PostgreSQL)

3. **Selecione Destino**: Escolha o destino (ex: MinIO S3)

4. **Configurar sincronização**:

§§§CÓDIGO_16§§§

5. **Configurar normalização** (opcional):

§§§CÓDIGO_17§§§

6. **Testar conexão** → **Configurar conexão**

### Modos de sincronização

| Moda | Descrição | Casos de uso |
|------|-------------|-------------|
| **Atualização completa\| Substituir** | Substitua todos os dados | Tabelas de dimensões |
| **Atualização completa\| Anexar** | Adicione todos os registros | Acompanhamento histórico |
| **Incremental\| Anexar** | Adicionar registros novos/atualizados | Tabelas de fatos |
| **Incremental\| Deduplicado** | Atualizar registros existentes | SCD Tipo 1 |

### Planejamento

**Opções de frequência:**
- **Manual**: Aciona manualmente
- **De hora em hora**: A cada hora
- **Diariamente**: A cada 24 horas (especifique o horário)
- **Semanalmente**: dias específicos da semana
- **Cron**: agendamento personalizado (ex: `0 2 * * *`)

**Exemplos de horários:**
§§§CÓDIGO_19§§§

---

## Transformação de dados

### Normalização Básica

Airbyte inclui **Normalização Básica** usando dbt:

**O que ela faz:**
- Converte JSON aninhado em tabelas planas
- Criar tabelas `_airbyte_raw_*` (JSON bruto)
- Cria tabelas padronizadas (estruturadas)
- Adicionar colunas de metadados (`_airbyte_emitted_at`, `_airbyte_normalized_at`)

**Exemplo:**

**JSON bruto** (`_airbyte_raw_customers`):
§§§CÓDIGO_24§§§

**Tabelas Padronizadas:**

§§§CÓDIGO_25§§§:
§§§CÓDIGO_26§§§

§§§CÓDIGO_27§§§:
§§§CÓDIGO_28§§§

### Transformações Personalizadas (dbt)

Para transformações avançadas, use dbt:

1. **Desative a normalização do Airbyte**
2. **Criar modelos dbt** referenciando tabelas `_airbyte_raw_*`
3. **Execute dbt** após sincronizar o Airbyte

**Exemplo de modelo dbt:**
§§§CÓDIGO_30§§§

---

## Monitoramento

### Status de sincronização

**Interface Web do painel:**
- **Conexões**: Veja todas as conexões
- **Histórico de sincronização**: trabalhos de sincronização anteriores
- **Logs de sincronização**: registros detalhados por trabalho

**Indicadores de status:**
- 🟢 **Bem-sucedido**: sincronização concluída com sucesso
- 🔴 **Falha**: falha na sincronização (verifique os registros)
- 🟡 **Em execução**: sincronização em andamento
- ⚪ **Cancelado**: sincronização cancelada pelo usuário

### Registros

**Veja os registros de sincronização:**
§§§CÓDIGO_31§§§

### Métricas

**Principais métricas a serem monitoradas:**
- **Gravações Sincronizadas**: Número de gravações por sincronização
- **Bytes Sincronizados**: Volume de dados transferidos
- **Duração da sincronização**: tempo gasto por sincronização
- **Taxa de falhas**: porcentagem de sincronizações com falha

**Métricas de exportação:**
§§§CÓDIGO_32§§§

### Alertas

**Configure alertas** em **Configurações > Notificações**:

§§§CÓDIGO_33§§§

---

## Uso de API

### Autenticação

§§§CÓDIGO_34§§§

### Chamadas de API comuns

#### Listar fontes

§§§CÓDIGO_35§§§

#### Criar conexão

§§§CÓDIGO_36§§§

#### Sincronização de gatilho

§§§CÓDIGO_37§§§

#### Obter status do trabalho

§§§CÓDIGO_38§§§

---

## Integração com Dremio

### Fluxo de trabalho

§§§CÓDIGO_39§§§

### Etapas de configuração

1. **Configure o Airbyte para carregar no MinIO S3** (veja acima)

2. **Adicionar fonte S3 no Dremio:**

§§§CÓDIGO_40§§§

3. **Consulte dados do Airbyte no Dremio:**

§§§CÓDIGO_41§§§

4. **Criar conjunto de dados virtuais Dremio:**

§§§CÓDIGO_42§§§

5. **Uso em modelos dbt:**

§§§CÓDIGO_43§§§

---

## Melhores práticas

### Desempenho

1. **Use sincronizações incrementais** sempre que possível
2. **Programe sincronizações fora dos horários de pico**
3. **Use o formato Parquet** para melhor compactação
4. **Particionar tabelas grandes** por data
5. **Monitore o uso de recursos** e ajuste limites

### Qualidade dos dados

1. **Ativar validação de dados** nos conectores de origem
2. **Use chaves primárias** para detectar duplicatas
3. **Configurar alertas** para falhas de sincronização
4. **Monitore a atualização dos dados** métricas
5. **Implementar testes dbt** em dados brutos

### Segurança

1. **Use identificadores somente leitura** para fontes
2. **Armazenar segredos** em variáveis ​​de ambiente
3. **Ativar SSL/TLS** para conexões
4. **Renove seus identificadores** regularmente
5. **Auditoria de registros de acesso** periodicamente

### Otimização de custos

1. **Use compactação** (GZIP, SNAPPY)
2. **Desduplicar dados** na origem
3. **Arquivar dados antigos** em armazenamento frio
4. **Monitore a frequência de sincronização** versus requisitos
5. **Limpar dados de sincronização com falha**

---

## Solução de problemas

### Problemas Comuns

#### Falha na sincronização: tempo limite de conexão

**Sintoma:**
§§§CÓDIGO_44§§§

**Solução:**
§§§CÓDIGO_45§§§

#### Erro de falta de memória

**Sintoma:**
§§§CÓDIGO_46§§§

**Solução:**
§§§CÓDIGO_47§§§

#### Falha na normalização

**Sintoma:**
§§§CÓDIGO_48§§§

**Solução:**
§§§CÓDIGO_49§§§

#### Desempenho de sincronização lenta

**Diagnóstico:**
§§§CÓDIGO_50§§§

**Soluções:**
- Aumentar a frequência de sincronização incremental
- Adicionar índice aos campos do cursor
- Use CDC para fontes em tempo real
- Dimensionar recursos de trabalhadores

---

## Tópicos Avançados

### Conectores personalizados

Crie conectores personalizados com Airbyte CDK:

§§§CÓDIGO_51§§§

### Orquestração de APIs

Automatize Airbyte com Python:

§§§CÓDIGO_52§§§

---

## Recursos

### Documentação

- **Documentos Airbyte**: https://docs.airbyte.com
- **Catálogo de conectores**: https://docs.airbyte.com/integrations
- **Referência da API**: https://airbyte-public-api-docs.s3.us-east-2.amazonaws.com/rapidoc-api-docs.html

### Comunidade

- **Slack**: https://slack.airbyte.io
- **GitHub**: https://github.com/airbytehq/airbyte
- **Fórum**: https://discuss.airbyte.io

---

## Próximas etapas

Depois de configurar o Airbyte:

1. **Configurar o Dremio** - [Guia de configuração do Dremio](dremio-setup.md)
2. **Criar modelos dbt** - [Guia de desenvolvimento dbt](dbt-development.md)
3. **Criar painéis** - [Guia de painéis do Superset](superset-dashboards.md)
4. **Monitore a qualidade** - [Guia de qualidade de dados](data-quality.md)

---

**Versão do Guia de Integração Airbyte**: 3.2.0  
**Última atualização**: 16 de outubro de 2025  
**Mantido por**: Equipe da plataforma de dados