# Referência da API do superconjunto

**Versão**: 3.2.0  
**Última atualização**: 16 de outubro de 2025  
**Idioma**: Francês

## Índice

1. [Visão geral](#visão geral)
2. [Autenticação](#autenticação)
3. [Painéis](#paineles)
4. [Gráficos](#gráficos)
5. [Conjuntos de dados](#conjuntos de dados)
6. [Laboratório SQL](#sql-lab)
7. [Segurança](#segurança)
8. [Exemplos Python](#python-examples)

---

## Visão geral

Apache Superset fornece uma API REST para acesso programático.

**URL base**: `http://localhost:8088/api/v1`

### Arquitetura de API

§§§CÓDIGO_1§§§

---

## Autenticação

### Conecte-se

**Ponto final**: `POST /api/v1/security/login`

§§§CÓDIGO_3§§§

**Responder** :
§§§CÓDIGO_4§§§

### Atualizar token

**Ponto final**: `POST /api/v1/security/refresh`

§§§CÓDIGO_6§§§

### Auxiliar de autenticação Python

§§§CÓDIGO_7§§§

---

## Painéis

### Listar painéis

**Ponto final**: `GET /api/v1/dashboard/`

§§§CÓDIGO_9§§§

**Responder** :
§§§CÓDIGO_10§§§

### Obtenha um painel

**Ponto final**: `GET /api/v1/dashboard/{id}`

§§§CÓDIGO_12§§§

**Responder** :
§§§CÓDIGO_13§§§

### Crie um painel

**Ponto final**: `POST /api/v1/dashboard/`

§§§CÓDIGO_15§§§

### Exemplo de Python

§§§CÓDIGO_16§§§

### Atualizar um painel

**Ponto final**: `PUT /api/v1/dashboard/{id}`

§§§CÓDIGO_18§§§

### Excluir um painel

**Ponto final**: `DELETE /api/v1/dashboard/{id}`

§§§CÓDIGO_20§§§

### Exportar um painel

**Ponto final**: `GET /api/v1/dashboard/export/`

§§§CÓDIGO_22§§§

### Importar um painel

**Ponto final**: `POST /api/v1/dashboard/import/`

§§§CÓDIGO_24§§§

---

## Gráficos

### Listar gráficos

**Ponto final**: `GET /api/v1/chart/`

§§§CÓDIGO_26§§§

### Obtenha um gráfico

**Ponto final**: `GET /api/v1/chart/{id}`

§§§CÓDIGO_28§§§

**Responder** :
§§§CÓDIGO_29§§§

### Crie um gráfico

**Ponto final**: `POST /api/v1/chart/`

§§§CÓDIGO_31§§§

### Obtenha dados de um gráfico

**Ponto final**: `POST /api/v1/chart/data`

§§§CÓDIGO_33§§§

**Responder** :
§§§CÓDIGO_34§§§

---

## Conjuntos de dados

### Listar conjuntos de dados

**Ponto final**: `GET /api/v1/dataset/`

§§§CÓDIGO_36§§§

### Obtenha um conjunto de dados

**Ponto final**: `GET /api/v1/dataset/{id}`

§§§CÓDIGO_38§§§

**Responder** :
§§§CÓDIGO_39§§§

### Crie um conjunto de dados

**Ponto final**: `POST /api/v1/dataset/`

§§§CÓDIGO_41§§§

### Adicione uma métrica calculada

**Ponto final**: `POST /api/v1/dataset/{id}/metric`

§§§CÓDIGO_43§§§

---

## Laboratório SQL

### Execute uma consulta SQL

**Ponto final**: `POST /api/v1/sqllab/execute/`

§§§CÓDIGO_45§§§

**Responder** :
§§§CÓDIGO_46§§§

### Execução SQL em Python

§§§CÓDIGO_47§§§

### Obtenha resultados da consulta

**Ponto final**: `GET /api/v1/sqllab/results/{query_id}`

§§§CÓDIGO_49§§§

---

## Segurança

### Token de convidado

**Ponto final**: `POST /api/v1/security/guest_token/`

§§§CÓDIGO_51§§§

### Listar funções

**Ponto final**: `GET /api/v1/security/roles/`

§§§CÓDIGO_53§§§

### Crie um usuário

**Ponto final**: `POST /api/v1/security/users/`

§§§CÓDIGO_55§§§

---

## Exemplos de Python

### Automação completa do painel

§§§CÓDIGO_56§§§

### Exportação em lote de painéis

§§§CÓDIGO_57§§§

---

## Resumo

Esta referência de API cobriu:

- **Autenticação**: Autenticação baseada em tokens JWT
- **Dashboards**: operações CRUD, exportação/importação
- **Gráficos**: crie, atualize e consulte dados
- **Conjuntos de dados**: gerenciamento de tabelas/visualizações, métricas
- **SQL Lab**: execute consultas programaticamente
- **Segurança**: tokens de convidados, usuários, funções
- **Exemplos de Python**: scripts de automação completos

**Pontos-chave**:
- Use a API para automação do painel
- Tokens de convidados permitem integração segura
- API SQL Lab para consultas ad hoc
- Exportação/importação para controle de versão
- Crie conjuntos de dados com métricas calculadas

**Documentação Relacionada**:
- [Guia de painéis do Superset](../guides/superset-dashboards.md)
- [Arquitetura: Fluxo de Dados](../architecture/data-flow.md)
- [Guia de solução de problemas](../guides/troubleshooting.md)

---

**Versão**: 3.2.0  
**Última atualização**: 16 de outubro de 2025