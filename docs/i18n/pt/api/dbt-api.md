# referência da API dbt

**Versão**: 3.2.0  
**Última atualização**: 16 de outubro de 2025  
**Idioma**: Francês

## Índice

1. [Visão geral](#visão geral)
2. [Comandos CLI](#cli-commands)
3. [API Python](#api-python)
4. [Arquivos de metadados](#arquivos de metadados)
5. [API de nuvem dbt](#api-dbt-cloud)
6. [Macros personalizadas](#macros personalizadas)

---

## Visão geral

dbt fornece três interfaces principais:

| Interface | Casos de uso | Acesso |
|---------------|-------------|-------|
| CLI | Desenvolvimento, CI/CD | Linha de comando |
| API Python | Execução Programática | Código Python |
| API de nuvem dbt | Serviço Gerenciado | API REST |
| Metadados | Introspecção | Arquivos JSON |

---

## Comandos CLI

### Comandos principais

#### dbt executado

Execute os modelos para transformar os dados.

§§§CÓDIGO_0§§§

**Opções**:
§§§CÓDIGO_1§§§

#### teste dbt

Execute testes de qualidade de dados.

§§§CÓDIGO_2§§§

#### compilação dbt

Execute modelos, testes, sementes e instantâneos juntos.

§§§CÓDIGO_3§§§

#### documentos do dbt

Gerar e servir documentação.

§§§CÓDIGO_4§§§

### Comandos do desenvolvedor

#### compilações dbt

Compile modelos em SQL sem executá-los.

§§§CÓDIGO_5§§§

#### depuração de dbt

Teste a conexão e configuração do banco de dados.

§§§CÓDIGO_6§§§

####dbt ls (lista)

Liste os recursos do projeto.

§§§CÓDIGO_7§§§

### Comandos de dados

#### semente dbt

Carregue arquivos CSV no banco de dados.

§§§CÓDIGO_8§§§

#### instantâneo do dbt

Crie tabelas de dimensões do tipo 2 que mudam lentamente.

§§§CÓDIGO_9§§§

### Comandos utilitários

####dbt limpo

Exclua arquivos e artefatos compilados.

§§§CÓDIGO_10§§§

#### dependências dbt

Instale pacotes de packages.yml.

§§§CÓDIGO_11§§§

#### inicialização do dbt

Inicialize um novo projeto dbt.

§§§CÓDIGO_12§§§

---

##API Python

### Execução básica

§§§CÓDIGO_13§§§

### Wrapper Python completo

§§§CÓDIGO_14§§§

### Integração do fluxo de ar

§§§CÓDIGO_15§§§

---

## Arquivos de metadados

###manifesto.json

Contém os metadados completos do projeto.

**Localização**: `target/manifest.json`

§§§CÓDIGO_17§§§

### run_results.json

Contém os resultados da última execução.

**Localização**: `target/run_results.json`

§§§CÓDIGO_19§§§

### catálogo.json

Contém informações de esquema de banco de dados.

**Localização**: `target/catalog.json`

§§§CÓDIGO_21§§§

---

## API de nuvem dbt

Se você estiver usando o dbt Cloud (não aplicável para instalação local), a API estará disponível.

**URL base**: `https://cloud.getdbt.com/api/v2`

### Autenticação

§§§CÓDIGO_23§§§

### Acionar um trabalho

§§§CÓDIGO_24§§§

---

## Macros personalizadas

### Crie uma macro personalizada

**Arquivo**: `macros/custom_tests.sql`

§§§CÓDIGO_26§§§

### Uso em testes

**Arquivo**: `models/staging/schema.yml`

§§§CÓDIGO_28§§§

### Macro avançada com argumentos

§§§CÓDIGO_29§§§

### Chame uma macro

§§§CÓDIGO_30§§§

---

## Resumo

Esta referência de API cobriu:

- **Comandos CLI**: referência completa para todos os comandos dbt
- **API Python**: execução programática com wrapper Python
- **Arquivos de metadados**: manifest.json, run_results.json, catalog.json
- **dbt Cloud API**: aciona trabalhos (se estiver usando dbt Cloud)
- **Macros personalizadas**: crie e use recursos personalizados

**Pontos-chave**:
- Use a CLI para desenvolvimento e trabalho interativo
- Use a API Python para automação e orquestração
- Analisar arquivos de metadados para introspecção
- Crie macros personalizadas para lógica reutilizável
- Integrar com Airflow para planejamento de produção

**Documentação Relacionada**:
- [guia de desenvolvimento dbt](../guides/dbt-development.md)
- [Guia de qualidade de dados](../guides/data-quality.md)
- [Arquitetura: Fluxo de Dados](../architecture/data-flow.md)

---

**Versão**: 3.2.0  
**Última atualização**: 16 de outubro de 2025