# Guia de qualidade de dados

**Versão**: 3.2.0  
**Última atualização**: 16 de outubro de 2025  
**Idioma**: Francês

## Índice

1. [Visão geral](#visão geral)
2. [Estrutura de qualidade de dados](#estrutura de qualidade de dados)
3. [testes dbt](#testes-dbt)
4. [Integração de Grandes Expectativas](#integração de grandes expectativas)
5. [Regras de validação de dados](#data-validation-rules)
6. [Monitoramento e Alertas](#monitoramento-e-alertas)
7. [Métricas de qualidade de dados](#métricas de qualidade de dados)
8. [Estratégias de remediação](#estratégias de remediação)
9. [Boas Práticas](#boas-práticas)
10. [Estudos de caso](#estudos de caso)

---

## Visão geral

A qualidade dos dados é essencial para análises e tomadas de decisões confiáveis. Este guia cobre estratégias abrangentes para garantir, monitorar e melhorar a qualidade dos dados em toda a plataforma.

### Por que a qualidade dos dados é importante

§§§CÓDIGO_0§§§

### Dados de qualidade de dimensões

| Dimensões | Descrição | Verificação de exemplo |
|----------|-------------|-----------|
| **Precisão** | Os dados representam corretamente a realidade | Validação de formato de e-mail |
| **Completude** | Não são necessários valores ausentes | Verificações NOT NULL |
| **Consistência** | Correspondências de dados entre sistemas | Principais relações externas |
| **Notícias** | Dados atualizados e disponíveis quando necessário | Verificações de frescura |
| **Validade** | Dados em conformidade com as regras de negócio | Verificações de intervalo de valores |
| **Singularidade** | Não há registros duplicados | Exclusividade da chave primária |

---

## Estrutura de qualidade de dados

### Qualidade de Portas de Arquitetura

§§§CÓDIGO_1§§§

### Fraldas de qualidade

§§§CÓDIGO_2§§§

---

## testes dbt

### Testes Integrados

#### Testes Genéricos

§§§CÓDIGO_3§§§

#### Testes de relacionamento

§§§CÓDIGO_4§§§

### Testes Personalizados

#### Testes Singulares

§§§CÓDIGO_5§§§

§§§CÓDIGO_6§§§

§§§CÓDIGO_7§§§

#### Macros de teste genéricas

§§§CÓDIGO_8§§§

§§§CÓDIGO_9§§§

§§§CÓDIGO_10§§§

Usar:
§§§CÓDIGO_11§§§

### Execução de Teste

§§§CÓDIGO_12§§§

### Configuração de teste

§§§CÓDIGO_13§§§

---

## Integração Grandes Expectativas

### Instalação

§§§CÓDIGO_14§§§

### Configurar

§§§CÓDIGO_15§§§

Instale pacotes:
§§§CÓDIGO_16§§§

### Testa as expectativas

§§§CÓDIGO_17§§§

### Expectativas personalizadas

§§§CÓDIGO_18§§§

---

## Regras de validação de dados

### Validação de lógica de negócios

§§§CÓDIGO_19§§§

### Tabela de monitoramento de qualidade de dados

§§§CÓDIGO_20§§§

---

## Monitoramento e Alertas

### Painel de métricas de qualidade

§§§CÓDIGO_21§§§

### Alertas automatizados

§§§CÓDIGO_22§§§

### Verificações de qualidade de dados de fluxo de ar

§§§CÓDIGO_23§§§

---

## Métricas de qualidade de dados

### Principais indicadores de desempenho

§§§CÓDIGO_24§§§

### Análise de tendências

§§§CÓDIGO_25§§§

---

## Estratégias de remediação

### Regras de limpeza de dados

§§§CÓDIGO_26§§§

### Processo de quarentena

§§§CÓDIGO_27§§§

---

## Melhores práticas

### 1. Teste cedo e frequentemente

§§§CÓDIGO_28§§§

### 2. Use níveis de gravidade

§§§CÓDIGO_29§§§

### 3. Regras de qualidade de dados de documentos

§§§CÓDIGO_30§§§

### 4. Monitore tendências, não apenas pontos

§§§CÓDIGO_31§§§

### 5. Automatize a correção quando possível

§§§CÓDIGO_32§§§

---

## Estudos de caso

### Estudo de caso 1: Validação de e-mail

**Problema**: 15% dos e-mails de clientes eram inválidos (@missing, formato errado)

**Solução**:
§§§CÓDIGO_33§§§

**Remediação**:
§§§CÓDIGO_34§§§

**Resultado**: e-mails inválidos reduzidos de 15% para 2%

### Estudo de caso 2: Erros no cálculo de renda

**Problema**: 5% dos pedidos tinham total_amount ≠ valor + impostos + frete

**Solução**:
§§§CÓDIGO_35§§§

**Remediação**:
§§§CÓDIGO_36§§§

**Resultado**: Erros de cálculo reduzidos para <0,1%

---

## Resumo

Este guia abrangente de qualidade de dados cobriu:

- **Estrutura**: Portas, camadas e arquitetura de qualidade
- **testes dbt**: testes integrados, testes personalizados, testes macro genéricos
- **Grandes Expectativas**: Validação avançada com mais de 50 tipos de expectativas
- **Regras de validação**: lógica de negócios, pontuação de qualidade, tabelas de monitoramento
- **Monitoramento**: alertas automatizados, integração do Airflow, painéis
- **Métricas**: KPIs, análise de tendências, pontuação de qualidade
- **Remediação**: regras de limpeza, processo de quarentena, correções automáticas
- **Boas Práticas**: Teste antecipadamente, use níveis de severidade, monitore tendências
- **Estudos de caso**: exemplos reais e soluções

Pontos-chave a serem lembrados:
- Implementar verificações de qualidade em cada camada (Bronze → Prata → Ouro)
- Utilizar testes dbt para validação estrutural, Grandes Expectativas para validação estatística
- Monitore tendências temporais, não apenas métricas pontuais
- Automatize a correção de problemas comuns e previsíveis
- Alerta sobre degradação da qualidade antes do impacto nos negócios
- Documentar regras de qualidade e estratégias de remediação

**Documentação relacionada:**
- [Guia de desenvolvimento dbt](./dbt-development.md)
- [Arquitetura: Fluxo de Dados](../architecture/data-flow.md)
- [Guia de configuração do Dremio](./dremio-setup.md)
- [Guia de solução de problemas](./troubleshooting.md)

---

**Versão**: 3.2.0  
**Última atualização**: 16 de outubro de 2025