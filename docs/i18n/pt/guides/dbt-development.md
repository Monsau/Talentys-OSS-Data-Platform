# Guia de desenvolvimento do dbt

**Versão**: 3.2.0  
**Última atualização**: 16 de outubro de 2025  
**Idioma**: Francês

## Índice

1. [Visão geral](#visão geral)
2. [Configuração do Projeto](#configuração do projeto)
3. [Modelagem de dados](#modelagem de dados)
4. [Estrutura de teste](#estrutura de teste)
5. [Documentação](#documentação)
6. [Macros e pacotes](#macros-e-pacotes)
7. [Modelos incrementais](#modelos incrementais)
8. [Fluxo de trabalho de orquestração](#fluxo de trabalho de orquestração)
9. [Boas Práticas](#boas-práticas)
10. [Solução de problemas](#solução de problemas)

---

## Visão geral

dbt (ferramenta de construção de dados) permite que engenheiros analíticos transformem dados no warehouse usando SQL e práticas recomendadas de engenharia de software. Este guia cobre tudo, desde a inicialização do projeto até técnicas avançadas de desenvolvimento.

### O que é DBT?

O dbt transforma dados brutos em conjuntos de dados prontos para análise usando:

- **Transformações SQL**: escreve instruções SELECT, dbt cuida do resto
- **Controle de versão**: integração Git para colaboração
- **Testes**: estrutura integrada de testes de qualidade de dados
- **Documentação**: documentação autogerada com linhagem
- **Modularidade**: modelos e macros reutilizáveis

### Conceitos-chave

§§§CÓDIGO_0§§§

### fluxo de trabalho do dbt

§§§CÓDIGO_1§§§

---

## Configuração do Projeto

### Inicializar projeto dbt

§§§CÓDIGO_2§§§

### Configurar perfis.yml

§§§CÓDIGO_3§§§

### Configurar dbt_project.yml

§§§CÓDIGO_4§§§

### Variáveis ​​de Ambiente

§§§CÓDIGO_5§§§

### Testar conexão

§§§CÓDIGO_6§§§

---

## Modelagem de dados

### Modelos de teste

Os modelos de teste limpam e padronizam os dados brutos das fontes.

#### Definir fontes

§§§CÓDIGO_7§§§

#### Exemplo de modelo de teste

§§§CÓDIGO_8§§§

§§§CÓDIGO_9§§§

### Modelos Intermediários

Os modelos intermediários unem e enriquecem os dados.

§§§CÓDIGO_10§§§

### Tabelas feitas

§§§CÓDIGO_11§§§

### Tabelas de dimensões

§§§CÓDIGO_12§§§

### Modelos de mercado

§§§CÓDIGO_13§§§

---

## Estrutura de teste

### Testes Integrados

§§§CÓDIGO_14§§§

### Testes Personalizados

§§§CÓDIGO_15§§§

§§§CÓDIGO_16§§§

### Testes Genéricos

§§§CÓDIGO_17§§§

Usar:
§§§CÓDIGO_18§§§

### Executar testes

§§§CÓDIGO_19§§§

---

## Documentação

### Documentação do modelo

§§§CÓDIGO_20§§§

### Adicionar descrições

§§§CÓDIGO_21§§§

### Gerar documentação

§§§CÓDIGO_22§§§

**Documentação de recursos**:
- **Gráficos de linhagem**: representação visual das dependências do modelo
- **Detalhes da coluna**: descrições, tipos, testes
- **Fonte atualizada**: quando os dados foram carregados
- **Visualização do projeto**: conteúdo README
- **Pesquisa**: Encontre modelos, colunas, descrições

---

## Macros e Pacotes

### Macros personalizadas

§§§CÓDIGO_23§§§

Usar:
§§§CÓDIGO_24§§§

### Trechos SQL reutilizáveis

§§§CÓDIGO_25§§§

### Instalar pacotes

§§§CÓDIGO_26§§§

Instale pacotes:
§§§CÓDIGO_27§§§

### Usar pacote de macros

§§§CÓDIGO_28§§§

§§§CÓDIGO_29§§§

---

## Modelos Incrementais

### Modelo Incremental Básico

§§§CÓDIGO_30§§§

### Estratégias Incrementais

#### 1. Estratégia de acréscimo

§§§CÓDIGO_31§§§

#### 2. Estratégia de mesclagem

§§§CÓDIGO_32§§§

#### 3. Estratégia Excluir + Inserir

§§§CÓDIGO_33§§§

### Atualização completa

§§§CÓDIGO_34§§§

---

## Fluxo de trabalho de orquestração

### Comandos de execução do dbt

§§§CÓDIGO_35§§§

### Pipeline completo

§§§CÓDIGO_36§§§

### Integração do fluxo de ar

§§§CÓDIGO_37§§§

---

## Melhores práticas

### 1. Convenções de nomenclatura

§§§CÓDIGO_38§§§

### 2. Estrutura de pastas

§§§CÓDIGO_39§§§

### 3. Use CTEs

§§§CÓDIGO_40§§§

### 4. Adicione testes antecipadamente

§§§CÓDIGO_41§§§

### 5. Documente tudo

§§§CÓDIGO_42§§§

---

## Solução de problemas

### Problemas Comuns

#### Problema 1: Erro de compilação

**Erro**: `Compilation Error: Model not found`

**Solução**:
§§§CÓDIGO_44§§§

#### Problema 2: Dependências Circulares

**Erro**: `Compilation Error: Circular dependency detected`

**Solução**:
§§§CÓDIGO_46§§§

#### Problema 3: testes com falha

**Erro**: `ERROR test not_null_stg_customers_email (FAIL 15)`

**Solução**:
§§§CÓDIGO_48§§§

#### Problema 4: Modelo incremental não funciona

**Erro**: o modelo incremental é sempre reconstruído do zero

**Solução**:
§§§CÓDIGO_49§§§

---

## Resumo

Este guia completo de desenvolvimento de dbt cobriu:

- **Configuração do Projeto**: Inicialização, configuração, configuração do ambiente
- **Modelagem de dados**: modelos de teste, intermediário, fato, dimensão e mercado
- **Testes de estrutura**: testes integrados, testes personalizados, testes genéricos
- **Documentação**: documentação do modelo, documentos do site gerados automaticamente
- **Macros e Pacotes**: Código reutilizável, dbt_utils, expectativas
- **Modelos Incrementais**: Estratégias anexar, mesclar, excluir+inserir
- **Orquestração de fluxo de trabalho**: comandos dbt, scripts de pipeline, integração do Airflow
- **Boas Práticas**: Convenções de nomenclatura, estrutura de pastas, documentação
- **Solução de problemas**: problemas e soluções comuns

Pontos-chave a serem lembrados:
- Use instruções SQL SELECT, dbt gerencia DDL/DML
- Teste cedo e frequentemente com estrutura de teste integrada
- Modelos de documentos para análise de autoatendimento
- Use modelos incrementais para tabelas grandes
- Siga convenções de nomenclatura consistentes
- Aproveite pacotes para recursos comuns

**Documentação relacionada:**
- [Guia de configuração do Dremio](./dremio-setup.md)
- [Guia de qualidade de dados](./data-quality.md)
- [Arquitetura: Fluxo de Dados](../architecture/data-flow.md)
- [Tutorial de primeiros passos](../getting-started/first-steps.md)

---

**Versão**: 3.2.0  
**Última atualização**: 16 de outubro de 2025