# Guia de painéis do Apache Superset

**Versão**: 3.2.0  
**Última atualização**: 16 de outubro de 2025  
**Idioma**: Francês

## Índice

1. [Visão geral](#visão geral)
2. [Configuração inicial](#configuração inicial)
3. [Conexão de fontes de dados](#data-sources-connection)
4. [Criação de gráficos](#criação de gráficos)
5. [Construção do painel](#construção do painel)
6. [Recursos avançados](#recursos avançados)
7. [Segurança e permissões](#segurança-e-permissões)
8. [Otimização de desempenho](#otimização de desempenho)
9. [Integração e Compartilhamento](#integração-e-compartilhamento)
10. [Boas Práticas](#boas-práticas)

---

## Visão geral

Apache Superset é um aplicativo da web de business intelligence moderno e pronto para empresas que permite aos usuários explorar e visualizar dados por meio de painéis e gráficos intuitivos.

### Principais recursos

| Recurso | Descrição | Lucro |
|----------------|---------|---------|
| **IDE SQL** | Editor SQL interativo com preenchimento automático | Análise ad hoc |
| **Visualizações ricas** | Mais de 50 tipos de gráficos | Representação de dados diversos |
| **Construtor de painel** | Interface de arrastar e soltar | Criação fácil de painel |
| **Cache** | Consultas de resultados de cache | Tempos de carregamento rápidos |
| **Segurança** | Segurança em nível de linha, acesso baseado em função | Governança de dados |
| **Alertas** | Notificações automatizadas por e-mail/Slack | Monitoramento proativo |

### Integração de Arquitetura

§§§CÓDIGO_0§§§

---

## Configuração inicial

### Primeira Conexão

Acesse o Superconjunto em `http://localhost:8088`:

§§§CÓDIGO_2§§§

**Nota de segurança**: Altere a senha padrão imediatamente após o primeiro login.

### Configuração inicial

§§§CÓDIGO_3§§§

### Arquivo de configuração

§§§CÓDIGO_4§§§

---

## Fontes de dados de conexão

### Faça login no Dremio

#### Etapa 1: Instale o driver de banco de dados Dremio

§§§CÓDIGO_5§§§

#### Etapa 2: Adicionar banco de dados Dremio

§§§CÓDIGO_6§§§

**Configuração**:
§§§CÓDIGO_7§§§

#### Etapa 3: testar a conexão

§§§CÓDIGO_8§§§

### Conectando-se ao PostgreSQL

§§§CÓDIGO_9§§§

### Conectando-se ao Elasticsearch

§§§CÓDIGO_10§§§

---

## Criação Gráfica

### Fluxo de trabalho de criação gráfica

§§§CÓDIGO_11§§§

### Tipo de gráfico de seleção

| Tipo gráfico | Melhor para | Exemplo de caso de uso |
|----------------|---------------|---------------------|
| **Gráfico Linear** | Tendências temporais | Tendência da renda diária |
| **Gráfico de barras** | Comparações | Receita por categoria de produto |
| **Gráfico de Setores** | Participação no total | Participação de mercado por região |
| **Tabela** | Dados detalhados | Lista de clientes com métricas |
| **Grande Número** | Métrica única | Receita total acumulada no ano |
| **Cartão de Calor** | Detecção de padrões | Vendas por dia/hora |
| **Nuvem de pontos** | Correlações | Valor do cliente versus frequência |
| **Diagrama de Sankey** | Análise de fluxo | Jornada do usuário |

### Exemplo: Gráfico Linear (Tendência de Renda)

#### Etapa 1: Criar conjunto de dados

§§§CÓDIGO_12§§§

**Configuração**:
- **Banco de dados**: Dremio
- **Diagrama**: Produção.Marts
- **Tabela**: mart_daily_revenue

#### Etapa 2: Criar gráfico

§§§CÓDIGO_13§§§

**Parâmetros**:
§§§CÓDIGO_14§§§

**SQL gerado**:
§§§CÓDIGO_15§§§

### Exemplo: gráfico de barras (principais clientes)

§§§CÓDIGO_16§§§

### Exemplo: Tabela Dinâmica

§§§CÓDIGO_17§§§

### Exemplo: Número Grande com Tendência

§§§CÓDIGO_18§§§

---

## Painéis de construção

### Processo de criação do painel

§§§CÓDIGO_19§§§

### Etapa 1: Criar painel

§§§CÓDIGO_20§§§

**Configurações do painel**:
§§§CÓDIGO_21§§§

### Etapa 2: Adicionar gráficos

Arraste e solte gráficos do painel esquerdo ou crie novos:

§§§CÓDIGO_22§§§

### Etapa 3: Layout do projeto

**Sistema de grade**:
- 12 colunas de largura
- Os gráficos se ajustam à grade
- Deslize para redimensionar e reposicionar

**Exemplo de layout**:
§§§CÓDIGO_23§§§

### Etapa 4: adicionar filtros ao painel

§§§CÓDIGO_24§§§

**Filtro de período**:
§§§CÓDIGO_25§§§

**Filtro de categoria**:
§§§CÓDIGO_26§§§

**Filtro Digital**:
§§§CÓDIGO_27§§§

### Etapa 5: Filtragem cruzada

Ative a filtragem cruzada do painel:

§§§CÓDIGO_28§§§

**Configuração**:
§§§CÓDIGO_29§§§

**Experiência do usuário**:
- Clique na barra → filtre todo o painel
- Clique em compartilhamento do setor → atualiza gráficos relacionados
- Limpar filtro → redefine a visualização padrão

---

## Recursos avançados

### Laboratório SQL

Editor SQL interativo para consultas ad hoc.

#### Executar consulta

§§§CÓDIGO_30§§§

**Características**:
- Preenchimento automático para tabelas e colunas
- Histórico de solicitações
- Várias guias
- Exportar resultados (CSV, JSON)
- Salvar consulta para reutilização

#### Criar tabela a partir de consulta (CTAS)

§§§CÓDIGO_31§§§

### Modelos Jinja

SQL dinâmico com modelos Jinja2:

§§§CÓDIGO_32§§§

**Variáveis ​​de modelo**:
- `{{ from_dttm }}` - Período de início
- `{{ to_dttm }}` - Fim do intervalo de datas
- `{{ filter_values('column') }}` - Valores de filtro selecionados
- `{{ current_username }}` - Usuário logado

### Alertas e Relatórios

#### Criar alerta

§§§CÓDIGO_37§§§

**Configuração**:
§§§CÓDIGO_38§§§

#### Criar relatório

§§§CÓDIGO_39§§§

### Plug-ins de visualização personalizados

Crie tipos gráficos personalizados:

§§§CÓDIGO_40§§§

Construir e instalar:
§§§CÓDIGO_41§§§

---

## Segurança e permissões

### Controle de acesso baseado em função (RBAC)

§§§CÓDIGO_42§§§

### Funções Integradas

| Função | Permissões | Casos de uso |
|------|-------------|-------------|
| **Administrador** | Todas as permissões | Administradores de sistema |
| **Alfa** | Criar, editar, excluir painéis/gráficos | Analistas de dados |
| **Gama** | Visualize painéis, execute consultas do SQL Lab | Usuários empresariais |
| **sql_lab** | Somente acesso ao SQL Lab | Cientistas de dados |
| **Público** | Visualizar apenas painéis públicos | Usuários anônimos |

### Criar função personalizada

§§§CÓDIGO_43§§§

**Exemplo: função de analista de marketing**
§§§CÓDIGO_44§§§

### Segurança em nível de linha (RLS)

Restrinja os dados de acordo com os atributos do usuário:

§§§CÓDIGO_45§§§

**Exemplo: RLS baseado em região**
§§§CÓDIGO_46§§§

**Exemplo: RLS baseado em cliente**
§§§CÓDIGO_47§§§

### Segurança de conexão com banco de dados

§§§CÓDIGO_48§§§

---

## Otimização de desempenho

### Consultas em cache

§§§CÓDIGO_49§§§

**Estratégia de cache**:
§§§CÓDIGO_50§§§

### Solicitações assíncronas

Habilite a execução de consulta assíncrona para consultas longas:

§§§CÓDIGO_51§§§

### Otimização de consulta de banco de dados

§§§CÓDIGO_52§§§

### Otimização de carregamento do painel

§§§CÓDIGO_53§§§

### Monitoramento de desempenho

§§§CÓDIGO_54§§§

---

## Integração e Compartilhamento

### Painéis públicos

Torne os painéis acessíveis sem conexão:

§§§CÓDIGO_55§§§

**URL público**:
§§§CÓDIGO_56§§§

### Integração com iframe

Integre painéis em aplicativos externos:

§§§CÓDIGO_57§§§

**Configurações de integração**:
- `standalone=1` - Ocultar navegação
- `show_filters=0` - Ocultar painel de filtro
- `show_title=0` - Ocultar título do painel

### Autenticação de token de convidado

Acesso programático para painéis integrados:

§§§CÓDIGO_61§§§

### Exportar painéis

§§§CÓDIGO_62§§§

---

## Melhores práticas

### Design do painel

1. **Hierarquia de layout**
   §§§CÓDIGO_63§§§

2. **Consistência de cores**
   - Use um esquema de cores consistente em todos os painéis
   - Verde para métricas positivas, vermelho para negativas
   - Cores da marca para categorias

3. **Desempenho**
   - Limite de gráficos por painel (<15)
   - Use níveis de agregação apropriados
   - Habilitar cache para dados estáticos
   - Defina limites de linha razoáveis

4. **Interatividade**
   - Adicione filtros significativos
   - Habilitar filtragem cruzada para exploração
   - Fornece recursos de detalhamento

### Seleção Gráfica

| Tipo de dados | Gráficos recomendados | Evite |
|--------------|----------------------------|--------|
| **Série Temporal** | Linear, Áreas | Setores, Anel |
| **Comparação** | Barras, Colunas | Linear (poucos pontos de dados) |
| **Participação no Total** | Setores, Anel, Treemap | Bares (também categorias) |
| **Distribuição** | Histograma, Box Plot | Setores |
| **Correlação** | Pontos de nuvem, bolhas | Barras |
| **Geográfico** | Mapa, Coropleto | Tabela |

### Otimização de consulta

§§§CÓDIGO_64§§§

### Segurança

1. **Controle de acesso**
   - Use RBAC para gerenciamento de usuários
   - Implementar RLS para isolamento de dados
   - Restringir conexões de banco de dados por função

2. **Governança de Dados**
   - Propriedade de conjuntos de dados de documentos
   - Definir cronogramas de atualização de dados
   - Monitore o desempenho da consulta

3. **Conformidade**
   - Ocultar PII nas visualizações
   - Acesso ao painel de auditoria
   - Implementar políticas de retenção de dados

---

## Resumo

Este guia abrangente do Superset cobriu:

- **Configuração**: Instalação, configuração, conexões de banco de dados
- **Gráficos**: Mais de 50 tipos de gráficos, configuração, geração de SQL
- **Painéis**: design de layout, filtros, filtragem cruzada
- **Recursos avançados**: SQL Lab, modelos Jinja, alertas, plug-ins personalizados
- **Segurança**: RBAC, RLS, segurança de conexão de banco de dados
- **Desempenho**: cache, consultas assíncronas, otimização de consultas
- **Integração**: painéis públicos, integração de iframe, tokens de convidados
- **Boas Práticas**: Princípios de design, seleção gráfica, segurança

Pontos-chave a serem lembrados:
- Superset se conecta ao Dremio para análises de alto desempenho
- Biblioteca de visualização rica que oferece suporte a vários casos de uso
- Cache integrado e consultas assíncronas garantem painéis rápidos
- RBAC e RLS permitem análises seguras de autoatendimento
- Os recursos de integração permitem a integração com aplicativos externos

**Documentação relacionada:**
- [Guia de configuração do Dremio](./dremio-setup.md)
- [Arquitetura: Fluxo de Dados](../architecture/data-flow.md)
- [Tutorial de primeiros passos](../getting-started/first-steps.md)
- [Guia de qualidade de dados](./data-quality.md)

---

**Versão**: 3.2.0  
**Última atualização**: 16 de outubro de 2025