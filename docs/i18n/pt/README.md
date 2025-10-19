# Plataforma de dados

<p align="center">
  <a href="https://talentys.eu" target="_blank">
    <img src="../../assets/images/talentys/original.png" alt="Talentys Data" width="200"/>
  </a>
  <br/>
  <em>Supported by <a href="https://talentys.eu">Talentys</a> | <a href="https://www.linkedin.com/company/talentysdata">LinkedIn</a> - Data Engineering & Analytics Excellence</em>
</p>


**Solução de data lakehouse empresarial**

**Idioma**: Francês (FR)  
**Versão**: 3.3.1  
**Última atualização**: 19 de outubro de 2025

---

## Visão geral

Plataforma de dados profissional que combina Dremio, dbt e Apache Superset para transformação de dados de nível empresarial, garantia de qualidade e inteligência de negócios.

Esta plataforma fornece uma solução completa para engenharia de dados moderna, incluindo pipelines de dados automatizados, testes de qualidade e painéis interativos.

§§§CÓDIGO_0§§§

---

## Principais recursos

- Arquitetura de data lakehouse com Dremio
- Transformações automatizadas com dbt
- Inteligência de negócios com Apache Superset
- Testes abrangentes de qualidade de dados
- Sincronização em tempo real via Arrow Flight

---

## Guia de início rápido

### Pré-requisitos

- Docker 20.10 ou superior
- Docker Compose 2.0 ou superior
- Python 3.11 ou superior
- Mínimo 8 GB de RAM

### Instalação

§§§CÓDIGO_1§§§

---

## Arquitetura

### Componentes do sistema

| Componente | Porto | Descrição |
|---------------|------|------------|
| Drêmio | 9047, 31010, 32010 | Plataforma data lakehouse |
| dbt | - | Ferramenta de transformação de dados |
| Superconjunto | 8088 | Plataforma de Inteligência de Negócios |
| PostgreSQL | 5432 | Banco de dados transacional |
| MinIO | 9.000, 9.001 | Armazenamento de objetos (compatível com S3) |
| Elasticsearch | 9200 | Motor de pesquisa e análise |

Consulte a [documentação da arquitetura](architecture/) para obter detalhes sobre o projeto do sistema.

---

## Documentação

### Comece
- [Guia de instalação](primeiros passos/)
- [Configuração](primeiros passos/)
- [Primeiros passos](primeiros passos/)

### Guias do usuário
- [Engenharia de dados](guias/)
- [Criação de dashboards](guias/)
- [Integração de API](guias/)

### Documentação da API
- [referência da API REST](api/)
- [Autenticação](api/)
- [Exemplos de código](api/)

### Documentação de arquitetura
- [Design do sistema](arquitetura/)
- [Fluxo de dados](arquitetura/)
- [Guia de implantação](arquitetura/)
- [🎯 Guia visual dos portos Dremio](architecture/dremio-ports-visual.md) ⭐ NOVO

---

## Idiomas disponíveis

| Idioma | Código | Documentação |
|--------|------|---------------|
| Inglês | PT | [README.md](../../../README.md) |
| Francês | PT | [docs/i18n/fr/](../fr/README.md) |
| Espanhol | ES | [docs/i18n/es/](../es/README.md) |
| Português | PT | [docs/i18n/pt/](../pt/README.md) |
| العربية | AR | [docs/i18n/ar/](../ar/README.md) |
| 中文 | NC | [docs/i18n/cn/](../cn/README.md) |
| 日本語 | JP | [docs/i18n/jp/](../jp/README.md) |
| Russo | Reino Unido | [docs/i18n/ru/](../ru/README.md) |

---

## Apoiar

Para assistência técnica:
- Documentação: [README principal](../../../README.md)
- Rastreador de problemas: problemas do GitHub
- Fórum da comunidade: Discussões do GitHub
- E-mail: suporte@example.com

---

**[Retornar à documentação principal](../../../README.md)**
