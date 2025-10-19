# Introdução à plataforma de dados

**Versão**: 3.2.0  
**Última atualização**: 16/10/2025  
**Idioma**: Francês

---

## Visão geral

Este tutorial orienta você em suas primeiras interações com a plataforma de dados, desde a conexão com serviços até a construção de seu primeiro pipeline de dados com Airbyte, Dremio, dbt e Superset.

§§§CÓDIGO_0§§§

**Tempo estimado**: 60-90 minutos

---

## Pré-requisitos

Antes de começar, certifique-se de que:

- ✅ Todos os serviços estão instalados e funcionando
- ✅ Você pode acessar interfaces web
- ✅ O ambiente virtual Python está habilitado
- ✅ Compreensão básica de SQL

**Verifique se os serviços estão funcionando:**
§§§CÓDIGO_1§§§

---

## Etapa 1: Acesse todos os serviços

### URLs de serviço

| Serviços | URL | Credenciais padrão |
|--------|----------|------------------------|
| **Byte aéreo** | http://localhost:8000 | airbyte@example.com/senha |
| **Drêmio** | http://localhost:9047 | administrador/admin123 |
| **Superconjunto** | http://localhost:8088 | administrador / administrador |
| **MínIO** | http://localhost:9001 | minioadmin/minioadmin123 |

### Primeira Conexão

**Byte aéreo:**
1. Abra http://localhost:8000
2. Conclua o assistente de configuração
3. Defina o nome do espaço de trabalho: “Produção”
4. Substituir preferências (possível configuração posterior)

**Drêmio:**
1. Abra http://localhost:9047
2. Crie um usuário administrador no primeiro acesso:
   - Nome de usuário: `admin`
   - E-mail: `admin@example.com`
   - Senha: `admin123`
3. Clique em “Começar”

**Superconjunto:**
1. Abra http://localhost:8088
2. Faça login com credenciais padrão
3. Alterar senha: Configurações → Informações do usuário → Redefinir senha

---

## Etapa 2: Configure sua primeira fonte de dados no Airbyte

### Crie uma fonte PostgreSQL

**Cenário**: Extraia dados de um banco de dados PostgreSQL.

1. **Navegue até Fontes**
   - Clique em “Fontes” no menu esquerdo
   - Clique em “+ Nova fonte”

2. **Selecione PostgreSQL**
   - Procure por “PostgreSQL”
   - Clique no conector “PostgreSQL”

3. **Configurar conexão**
   §§§CÓDIGO_5§§§

4. **Teste e economize**
   - Clique em “Configurar fonte”
   - Aguarde o teste de conexão
   - Fonte criada ✅

### Criar dados de amostra (opcional)

Se você ainda não possui dados, crie tabelas de exemplo:

§§§CÓDIGO_6§§§

---

## Etapa 3: Configurar destino MinIO S3

### Crie um destino

1. **Navegue até Destinos**
   - Clique em “Destinos” no menu esquerdo
   - Clique em “+ Novo destino”

2. **Selecione S3**
   - Procure por “S3”
   - Clique no conector “S3”

3. **Configurar MinIO como S3**
   §§§CÓDIGO_7§§§

4. **Teste e economize**
   - Clique em “Configurar destino”
   - O teste de conexão deve passar ✅

---

## Etapa 4: Crie sua primeira conexão

### Vincular origem ao destino

1. **Navegue até Conexões**
   - Clique em “Conexões” no menu esquerdo
   - Clique em “+ Nova conexão”

2. **Selecione a fonte**
   - Escolha “Produção PostgreSQL”
   - Clique em “Usar fonte existente”

3. **Selecione o destino**
   - Escolha “MinIO Data Lake”
   - Clique em “Usar destino existente”

4. **Configurar sincronização**
   §§§CÓDIGO_8§§§

5. **Normalização**
   §§§CÓDIGO_9§§§

6. **Fazer backup e sincronizar**
   - Clique em “Configurar conexão”
   - Clique em “Sincronizar agora” para executar a primeira sincronização
   - Monitore o progresso da sincronização

### Monitorar sincronização

§§§CÓDIGO_10§§§

**Verifique o status de sincronização:**
- O status deve mostrar "Sucesso" (verde)
- Registros sincronizados: ~11 (5 clientes + 6 pedidos)
- Veja os registros para obter detalhes

---

## Etapa 5: Conecte Dremio ao MinIO

### Adicione uma fonte S3 no Dremio

1. **Navegue até Fontes**
   - Abra http://localhost:9047
   - Clique em “Adicionar fonte” (+ ícone)

2. **Selecione S3**
   - Escolha “Amazon S3”
   - Configurar como MinIO:

§§§CÓDIGO_11§§§

3. **Teste e economize**
   - Clique em “Salvar”
   - Dremio analisará buckets MinIO

### Navegar pelos dados

1. **Navegue até a fonte MinIOLake**
   - Desenvolver “MinIOLake”
   - Desenvolva o balde "datalake"
   - Expanda a pasta "dados brutos"
   - Veja a pasta "production_public"

2. **Visualizar dados**
   - Clique na pasta “clientes”
   - Clique no arquivo Parquet
   - Clique em “Visualizar” para ver os dados
   - Os dados devem corresponder ao PostgreSQL ✅

### Crie um conjunto de dados virtual

1. **Consultar dados**
   §§§CÓDIGO_12§§§

2. **Salvar como VDS**
   - Clique em “Salvar visualização como”
   - Nome: `vw_customers`
   - Espaço: `@admin` (seu espaço)
   - Clique em “Salvar”

3. **Formatar dados** (opcional)
   - Clique em `vw_customers`
   - Use a interface para renomear colunas, alterar tipos
   - Exemplo: Renomear `customer_id` para `id`

---

## Etapa 6: Crie modelos dbt

### Inicialize o projeto dbt

§§§CÓDIGO_18§§§

### Criar definição de origem

**Arquivo**: `dbt/models/sources.yml`

§§§CÓDIGO_20§§§

### Crie um modelo de teste

**Arquivo**: `dbt/models/staging/stg_customers.sql`

§§§CÓDIGO_22§§§

**Arquivo**: `dbt/models/staging/stg_orders.sql`

§§§CÓDIGO_24§§§

### Crie um modelo de mercado

**Arquivo**: `dbt/models/marts/fct_customer_orders.sql`

§§§CÓDIGO_26§§§

### Executar modelos dbt

§§§CÓDIGO_27§§§

### Check-in Dremio

§§§CÓDIGO_28§§§

---

## Etapa 7: Crie um painel no Superset

### Adicionar banco de dados Dremio

1. **Navegue até bancos de dados**
   - Abra http://localhost:8088
   - Clique em “Dados” → “Bancos de dados”
   - Clique em “+ Banco de Dados”

2. **Selecione Dremio**
   §§§CÓDIGO_29§§§

3. **Clique em “Conectar”**

### Crie um conjunto de dados

1. **Navegue até Conjuntos de dados**
   - Clique em “Dados” → “Conjuntos de dados”
   - Clique em “+ Conjunto de dados”

2. **Configurar o conjunto de dados**
   §§§CÓDIGO_30§§§

3. **Clique em “Criar conjunto de dados e criar gráfico”**

### Criar gráficos

#### Gráfico 1: Segmentos de Clientes (Diagrama Circular)

§§§CÓDIGO_31§§§

#### Gráfico 2: Renda por país (gráfico de barras)

§§§CÓDIGO_32§§§

#### Gráfico 3: Métricas do cliente (grande número)

§§§CÓDIGO_33§§§

### Crie o painel

1. **Navegue até Painéis**
   - Clique em “Painéis”
   - Clique em “+ Painel”

2. **Configurar o Painel**
   §§§CÓDIGO_34§§§

3. **Adicionar gráficos**
   - Arraste e solte os gráficos criados
   - Organize em uma grade:
     §§§CÓDIGO_35§§§

4. **Adicionar filtros** (opcional)
   - Clique em “Adicionar Filtro”
   - Filtrar por: country_code
   - Aplicar a todos os gráficos

5. **Salve o painel**

---

## Etapa 8: Verifique o pipeline completo

### Teste ponta a ponta

§§§CÓDIGO_36§§§

### Adicionar novos dados

1. **Insira novos registros no PostgreSQL**
   §§§CÓDIGO_37§§§

2. **Acione a sincronização do Airbyte**
   - Abra a interface do Airbyte
   - Vá para a conexão "PostgreSQL → MinIO"
   - Clique em “Sincronizar agora”
   - Espere pelo fim ✅

3. **Execute o dbt**
   §§§CÓDIGO_38§§§

4. **Atualize o painel do Superset**
   - Abra o painel
   - Clique no botão “Atualizar”
   - Novos dados deverão aparecer ✅

### Verifique o fluxo de dados

§§§CÓDIGO_39§§§

---

## Etapa 9: Automatize o pipeline

### Agendar sincronização do Airbyte

Já configurado para funcionar a cada 24 horas às 02h00.

Para editar:
1. Abra a conexão no Airbyte
2. Vá para a aba “Configurações”
3. Atualize “Frequência de replicação”
4. Salvar

### Agendar execuções de dbt

**Opção 1: Cron Job (Linux)**
§§§CÓDIGO_40§§§

**Opção 2: Script Python**

**Arquivo**: `scripts/run_pipeline.py`
§§§CÓDIGO_42§§§

### Agendar com Docker Compose

**Arquivo**: `docker-compose.scheduler.yml`
§§§CÓDIGO_44§§§

---

## Próximas etapas

Parabéns! Você construiu um pipeline de dados completo de ponta a ponta. 🎉

### Saber mais

1. **Airbyte Advanced** - [Guia de integração Airbyte](../guides/airbyte-integration.md)
2. **Otimização Dremio** - [Guia de configuração Dremio](../guides/dremio-setup.md)
3. **Modelos dbt complexos** - [Guia de desenvolvimento dbt](../guides/dbt-development.md)
4. **Painéis Avançados** - [Guia de Painéis Superset](../guides/superset-dashboards.md)
5. **Qualidade de dados** - [Guia de qualidade de dados](../guides/data-quality.md)

### Solução de problemas

Se você tiver problemas, consulte:
- [Guia de solução de problemas](../guides/troubleshooting.md)
- [Guia de instalação](installation.md#troubleshooting)
- [Guia de configuração](configuration.md)

---

## Resumo

Você conseguiu:

- ✅ Acesse os 7 serviços da plataforma
- ✅ Configurar uma fonte Airbyte (PostgreSQL)
- ✅ Configurar um destino Airbyte (MinIO S3)
- ✅ Crie sua primeira conexão Airbyte
- ✅ Conecte Dremio ao MinIO
- ✅ Criar modelos dbt (staging + marts)
- ✅ Construa um painel de superconjunto
- ✅ Verifique o fluxo de dados ponta a ponta
- ✅ Automatizar a execução do pipeline

**Sua plataforma de dados agora está operacional!** 🚀

---

**Versão do Guia de Primeiros Passos**: 3.2.0  
**Última atualização**: 16/10/2025  
**Mantido por**: Equipe da plataforma de dados