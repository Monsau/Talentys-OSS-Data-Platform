# Visão geral da arquitetura

**Versão**: 3.2.0  
**Última atualização**: 16/10/2025  
**Idioma**: Francês

---

## Introdução

A plataforma de dados é uma arquitetura moderna nativa da nuvem construída em tecnologias de código aberto. Ele fornece uma solução abrangente para ingestão, armazenamento, transformação e visualização de dados, projetada para cargas de trabalho analíticas em escala empresarial.

§§§CÓDIGO_0§§§

---

## Princípios de Design

### 1. Código aberto primeiro

**Filosofia**: Use tecnologias de código aberto para evitar a dependência de fornecedores e manter a flexibilidade.

**Benefícios**:
- Sem custos de licenciamento
- Desenvolvimento comunitário
- Capacidade total de personalização
- Auditoria de segurança transparente
- Ampla compatibilidade do ecossistema

### 2. Arquitetura em camadas

**Filosofia**: Separe as preocupações em camadas distintas para manutenção e escalabilidade.

**Camadas**:
§§§CÓDIGO_1§§§

### 3. ELT em vez de ETL

**Filosofia**: Carregue primeiro os dados brutos e transforme-os em destino (ELT).

**Por que ELT?**
- **Flexibilidade**: transforme dados de várias maneiras sem reextração
- **Desempenho**: use cálculo de destino para transformações
- **Auditabilidade**: dados brutos sempre disponíveis para verificação
- **Custo**: Reduza a carga de extração em sistemas de origem

**Fluxo**:
§§§CÓDIGO_2§§§

### 4. Modelo Data Lakehouse

**Filosofia**: Combine a flexibilidade do data lake com o desempenho do data warehouse.

**Características**:
- **Transações ACID**: operações de dados confiáveis
- **Aplicação de esquema**: garantias de qualidade de dados
- **Viagem no tempo**: consulte versões históricas
- **Formatos abertos**: Parquet, Iceberg, Delta Lake
- **Acesso direto a arquivos**: Sem bloqueio proprietário

### 5. Design nativo da nuvem

**Filosofia**: Design para ambientes distribuídos e em contêineres.

**Implementação**:
- Contêineres Docker para todos os serviços
- Escalabilidade horizontal
- Infraestrutura como código
- Apátridas sempre que possível
- Configuração via variáveis ​​de ambiente

---

## Modelos de Arquitetura

### Arquitetura Lambda (Lote + Stream)

§§§CÓDIGO_3§§§

**Camada de lote** (dados históricos):
- Grandes volumes de dados
- Tratamento periódico (de hora em hora/diário)
- Alta latência aceitável
- Reprocessamento completo possível

**Camada de velocidade** (dados em tempo real):
- Alterar captura de dados (CDC)
- Baixa latência necessária
- Somente atualizações incrementais
- Gerencia dados recentes

**Camada de serviço**:
- Mescla visualizações em lote e rápidas
- Interface de consulta única (Dremio)
- Seleção automática de visualização

### Medalhão de Arquitetura (Bronze → Prata → Ouro)

§§§CÓDIGO_4§§§

**Camada de bronze** (cru):
- Dados como são das fontes
- Sem transformação
- História completa preservada
- Airbyte carrega aqui

**Camada prateada** (limpa):
- Qualidade de dados aplicada
- Formatos padronizados
- modelos de teste dbt
- Análise pronta

**Camada Dourada** (Profissão):
- Métricas agregadas
- Lógica de negócios aplicada
- Modelos Marts dbt
- Otimizado para consumo

---

## Interações entre componentes

### Fluxo de ingestão de dados

§§§CÓDIGO_5§§§

### Pipeline de Transformação

§§§CÓDIGO_6§§§

### Executando consultas

§§§CÓDIGO_7§§§

---

## Modelos de escalabilidade

### Escala horizontal

**Serviços Stateless** (podem evoluir livremente):
- Airbyte Workers: Evolua para sincronizações paralelas
- Dremio Executors: Escala para desempenho de consulta
- Web Superset: Evolua para usuários concorrentes

**Serviços com estado** (requerem coordenação):
- PostgreSQL: replicação de réplica primária
- MinIO: modo distribuído (vários nós)
- Elasticsearch: Cluster com fragmentação

### Escala vertical

**Intensivo em memória**:
- Dremio: Aumente o heap JVM para consultas grandes
- PostgreSQL: Mais RAM para buffer de cache
- Elasticsearch: Mais heap para indexação

**Intenso CPU**:
- dbt: Mais núcleos para modelos de construção paralela
- Airbyte: transformações de dados mais rápidas

### Particionamento de dados

§§§CÓDIGO_8§§§

---

## Alta disponibilidade

### Redundância de Serviços

§§§CÓDIGO_9§§§

### Cenários de falha

| Componente | Repartição | Recuperação |
|---------------|-------|--------|
| **Trabalhador Airbyte** | Queda de contêiner | Reinicialização automática, retomada da sincronização |
| **Executor Dremio** | Falha no nó | Solicitação redirecionada para outros executores |
| **PostgreSQL** | Primário fora de serviço | Promova réplica no primário |
| **Nó MinIO** | Falha no disco | A codificação de eliminação reconstrói dados |
| **Superconjunto** | Serviço fora de serviço | Balanceador redireciona tráfego |

### Estratégia de backup

§§§CÓDIGO_10§§§

---

## Arquitetura de segurança

### Segurança de Rede

§§§CÓDIGO_11§§§

### Autenticação e Autorização

**Autenticação de serviço**:
- **Dremio**: integração LDAP/AD, OAuth2, SAML
- **Superconjunto**: Autenticação de banco de dados, LDAP, OAuth2
- **Airbyte**: autenticação básica, OAuth2 (empresa)
- **MinIO**: políticas IAM, tokens STS

**Níveis de autorização**:
§§§CÓDIGO_12§§§

### Criptografia de dados

**Em repouso**:
- MinIO: criptografia do lado do servidor (AES-256)
- PostgreSQL: criptografia transparente de dados (TDE)
- Elasticsearch: índices criptografados

**Em trânsito**:
- TLS 1.3 para todas as comunicações entre serviços
- Arrow Flight com TLS para Dremio ↔ Superset
- HTTPS para interfaces web

---

## Monitoramento e Observabilidade

### Coleção de métricas

§§§CÓDIGO_13§§§

**Métricas principais**:
- **Airbyte**: Taxa de sucesso de sincronização, gravações sincronizadas, bytes transferidos
- **Dremio**: latência de solicitação, taxa de acertos de cache, uso de recursos
- **dbt**: tempo de construção do modelo, falhas nos testes
- **Superconjunto**: tempo de carregamento do painel, usuários ativos
- **Infraestrutura**: CPU, memória, disco, rede

### Registro

**Registro centralizado**:
§§§CÓDIGO_14§§§

### Rastreamento

**Rastreamento distribuído**:
- Integração Jaeger ou Zipkin
- Rastrear solicitações entre serviços
- Identificar gargalos
- Problemas de desempenho de depuração

---

## Topologias de implantação

### Ambiente de Desenvolvimento

§§§CÓDIGO_15§§§

### Ambiente de preparação

§§§CÓDIGO_16§§§

### Ambiente de Produção

§§§CÓDIGO_17§§§

---

## Justificativa das Escolhas Tecnológicas

### Por que Airbyte?

- **Mais de 300 conectores**: integrações pré-construídas
- **Código aberto**: Sem dependência de fornecedor
- **Comunidade ativa**: mais de 12 mil estrelas do GitHub
- **Suporte CDC**: captura de dados em tempo real
- **Padronização**: Integração dbt integrada

### Por que Dremio?

- **Aceleração de consulta**: consultas 10 a 100x mais rápidas
- **Arrow Flight**: transferência de dados de alto desempenho
- **Compatibilidade com data lake**: sem movimentação de dados
- **Autoatendimento**: usuários empresariais exploram dados
- **Rentável**: Reduza os custos de armazenamento

### Por que DBT?

- **Baseado em SQL**: Familiar para analistas
- **Controle de versão**: integração com Git
- **Testes**: testes integrados de qualidade de dados
- **Documentação**: documentos gerados automaticamente
- **Comunidade**: mais de 5 mil pacotes disponíveis

### Por que Superconjunto?

- **UI moderna**: interface intuitiva
- **SQL IDE**: recursos avançados de consulta
- **Visualizações ricas**: mais de 50 tipos de gráficos
- **Extensível**: plug-ins personalizados
- **Código aberto**: Fundação Apache compatível

### Por que PostgreSQL?

- **Confiabilidade**: conformidade com ACID
- **Desempenho**: comprovado em escala
- **Recursos**: JSON, pesquisa de texto completo, extensões
- **Comunidade**: Ecossistema maduro
- **Custo**: Gratuito e de código aberto

### Por que MinIO?

- **Compatibilidade com S3**: API padrão do setor
**Desempenho**: Alta vazão
- **Codificação de eliminação**: Durabilidade dos dados
- **Multinuvem**: implante em qualquer lugar
- **Econômico**: alternativa auto-hospedada

---

## Evolução Futura da Arquitetura

### Melhorias planejadas

1. **Catálogo de Dados** (Integração OpenMetadata)
   - Gerenciamento de metadados
   - Rastreamento de linhagem
   - Descoberta de dados

2. **Qualidade dos dados** (grandes expectativas)
   - Validação automatizada
   - Detecção de anomalias
   - Painéis de qualidade

3. **Operações de ML** (MLflow)
   - Pipelines de treinamento de modelo
   - Cadastro de modelos
   - Automação de implantação

4. **Processamento de fluxo** (Apache Flink)
   - Transformações em tempo real
   - Processamento de eventos complexos
   - Análise de streaming

5. **Governança de Dados** (Apache Atlas)
   - Aplicação de política
   - Auditoria de acesso
   - Relatórios de conformidade

---

## Referências

- [Detalhes do componente](componentes.md)
- [Fluxo de dados](data-flow.md)
- [Guia de implantação](deployment.md)
- [Integração Airbyte](../guides/airbyte-integration.md)

---

**Versão Visão Geral da Arquitetura**: 3.2.0  
**Última atualização**: 16/10/2025  
**Mantido por**: Equipe da plataforma de dados