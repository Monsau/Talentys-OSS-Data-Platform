# Referência da API Airbyte

**Versão**: 3.2.0  
**Última atualização**: 16 de outubro de 2025  
**Idioma**: Francês

## Índice

1. [Visão geral](#visão geral)
2. [Autenticação](#autenticação)
3. [Espaços de trabalho](#espaços de trabalho)
4. [Fontes](#fontes)
5. [Destinos](#destinos)
6. [Conexões](#conexões)
7. [Trabalhos e sincronizações](#jobs-and-synchronizations)
8. [Exemplos Python](#python-examples)

---

## Visão geral

A API Airbyte permite o gerenciamento programático de pipelines de dados.

**URL base**: `http://localhost:8001/api/v1`

### Arquitetura de API

§§§CÓDIGO_1§§§

---

## Autenticação

Airbyte usa autenticação básica na implantação do Docker.

§§§CÓDIGO_2§§§

---

## Espaços de trabalho

### Listar espaços de trabalho

§§§CÓDIGO_3§§§

**Responder** :
§§§CÓDIGO_4§§§

### Obtenha um espaço de trabalho

§§§CÓDIGO_5§§§

---

## Fontes

### Listar definições de origem

§§§CÓDIGO_6§§§

**Resposta**: Lista de mais de 300 conectores de origem disponíveis

### Obtenha uma definição de origem

§§§CÓDIGO_7§§§

### Crie uma fonte

#### Fonte PostgreSQL

§§§CÓDIGO_8§§§

**Responder** :
§§§CÓDIGO_9§§§

#### fonte da API

§§§CÓDIGO_10§§§

### Testar conexão de origem

§§§CÓDIGO_11§§§

**Responder** :
§§§CÓDIGO_12§§§

### Listar fontes

§§§CÓDIGO_13§§§

---

## Destinos

### Crie um destino (S3/MinIO)

§§§CÓDIGO_14§§§

### Crie um destino (PostgreSQL)

§§§CÓDIGO_15§§§

### Teste a conexão de destino

§§§CÓDIGO_16§§§

---

## Conexões

### Descubra o diagrama

§§§CÓDIGO_17§§§

**Responder** :
§§§CÓDIGO_18§§§

### Crie uma conexão

§§§CÓDIGO_19§§§

### Ajudante Python

§§§CÓDIGO_20§§§

### Atualizar uma conexão

§§§CÓDIGO_21§§§

---

## Trabalhos e sincronizações

### Acione uma sincronização manual

§§§CÓDIGO_22§§§

**Responder** :
§§§CÓDIGO_23§§§

### Obtenha o status de um trabalho

§§§CÓDIGO_24§§§

**Responder** :
§§§CÓDIGO_25§§§

### Monitore o progresso de um trabalho

§§§CÓDIGO_26§§§

### Listar os jobs de uma conexão

§§§CÓDIGO_27§§§

### Cancelar um trabalho

§§§CÓDIGO_28§§§

---

## Exemplos de Python

### Configuração completa do pipeline

§§§CÓDIGO_29§§§

---

## Resumo

Esta referência de API cobriu:

- **Espaços de trabalho**: obtenha o contexto do espaço de trabalho
- **Fontes**: Mais de 300 conectores (PostgreSQL, APIs, bancos de dados)
- **Destinos**: S3/MinIO, PostgreSQL, data warehouses
- **Conexões**: Configuração de sincronização com agendamento
- **Trabalhos**: acione, monitore e gerencie sincronizações
- **Cliente Python**: exemplos de automação completa

**Principais conclusões**:
- Use API REST para automação completa
- Teste as conexões antes de criar a sincronização
- Monitore o status do trabalho para pipelines de produção
- Use sincronização incremental com campos de cursor
- Planeje sincronizações com base nas necessidades de atualização de dados

**Documentação relacionada:**
- [Guia de integração Airbyte](../guides/airbyte-integration.md)
- [Arquitetura: Fluxo de Dados](../architecture/data-flow.md)
- [Guia de solução de problemas](../guides/troubleshooting.md)

---

**Versão**: 3.2.0  
**Última atualização**: 16 de outubro de 2025