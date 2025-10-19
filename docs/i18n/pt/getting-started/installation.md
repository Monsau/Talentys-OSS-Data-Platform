# Guia de instalação

**Versão**: 3.2.0  
**Última atualização**: 16/10/2025  
**Idioma**: Francês

---

## Visão geral

Este guia fornece instruções passo a passo para instalar e configurar a plataforma de dados completa, incluindo Airbyte, Dremio, dbt, Apache Superset e infraestrutura de suporte.

§§§CÓDIGO_0§§§

---

## Pré-requisitos

### Requisitos do sistema

**Requisitos mínimos:**
- **CPU**: 4 núcleos (8+ recomendado)
**RAM**: 8 GB (mais de 16 GB recomendado)
- **Espaço em disco**: 20 GB disponíveis (mais de 50 GB recomendados)
- **Rede**: conexão estável com a Internet para imagens Docker

**Sistemas operacionais:**
-Linux (Ubuntu 20.04+, CentOS 8+, Debian 11+)
- macOS (11.0+)
- Windows 10/11 com WSL2

### Software necessário

#### 1. Janela de encaixe

**Versão**: 20.10 ou superior

**Instalação:**

**Linux:**
§§§CÓDIGO_1§§§

**macOS:**
§§§CÓDIGO_2§§§

**Windows:**
§§§CÓDIGO_3§§§

#### 2. Docker Composição

**Versão**: 2.0 ou superior

**Instalação:**

§§§CÓDIGO_4§§§

**Observação**: Docker Desktop para macOS e Windows inclui Docker Compose.

####3.Píton

**Versão**: 3.11 ou superior

**Instalação:**

**Linux (Ubuntu/Debian):**
§§§CÓDIGO_5§§§

**macOS:**
§§§CÓDIGO_6§§§

**Windows:**
§§§CÓDIGO_7§§§

**Verificação:**
§§§CÓDIGO_8§§§

#### 4. Git

**Instalação:**

§§§CÓDIGO_9§§§

**Verificação:**
§§§CÓDIGO_10§§§

---

## Etapas de instalação

### Etapa 1: clonar o repositório

§§§CÓDIGO_11§§§

**Estrutura esperada:**
§§§CÓDIGO_12§§§

### Etapa 2: Configurar o ambiente

#### Criar arquivo de ambiente

§§§CÓDIGO_13§§§

#### Variáveis ​​de ambiente

**Configuração Básica:**
§§§CÓDIGO_14§§§

### Etapa 3: Instalar dependências do Python

#### Crie o ambiente virtual

§§§CÓDIGO_15§§§

#### Requisitos de instalação

§§§CÓDIGO_16§§§

**Principais pacotes instalados:**
- `pyarrow>=21.0.0` - Cliente Arrow Flight
- `pandas>=2.3.0` - Manipulação de dados
- `dbt-core>=1.10.0` - Transformação de dados
- `sqlalchemy>=2.0.0` - Conectividade de banco de dados
- `pyyaml>=6.0.0` - Gerenciamento de configuração

### Etapa 4: iniciar os serviços Docker

#### Iniciar serviços principais

§§§CÓDIGO_22§§§

**Serviços iniciados:**
- PostgreSQL (porta 5432)
- Dremio (portas 9047, 32010)
- Superconjunto Apache (porta 8088)
- MinIO (portas 9000, 9001)
- Elasticsearch (porta 9200)

#### Iniciar Airbyte (compor separadamente)

§§§CÓDIGO_23§§§

**Serviços Airbyte iniciados:**
- Servidor Airbyte (porta 8001)
- UI da Web Airbyte (porta 8000)
- Trabalhador Airbyte
- Byte Aéreo Temporal
- Banco de dados Airbyte

#### Verifique o status dos serviços

§§§CÓDIGO_24§§§

---

## Verificação

### Etapa 5: Verifique os serviços

#### 1. PostgreSQL

§§§CÓDIGO_25§§§

**Saída esperada:**
§§§CÓDIGO_26§§§

#### 2. Drêmio

**Interface Web:**
§§§CÓDIGO_27§§§

**Primeira conexão:**
- Nome de usuário: `admin`
- Senha: `admin123`
- Você será solicitado a criar uma conta de administrador no primeiro acesso

**Teste a conexão:**
§§§CÓDIGO_30§§§

#### 3. Byte aéreo

**Interface Web:**
§§§CÓDIGO_31§§§

**Identificadores padrão:**
- E-mail: `airbyte@example.com`
- Senha: `password`

**Teste a API:**
§§§CÓDIGO_34§§§

**Resposta esperada:**
§§§CÓDIGO_35§§§

#### 4. Superconjunto Apache

**Interface Web:**
§§§CÓDIGO_36§§§

**Identificadores padrão:**
- Nome de usuário: `admin`
- Senha: `admin`

**Teste a conexão:**
§§§CÓDIGO_39§§§

#### 5. MinIO

**IU do console:**
§§§CÓDIGO_40§§§

**Credenciais:**
- Nome de usuário: `minioadmin`
- Senha: `minioadmin123`

**Teste a API S3:**
§§§CÓDIGO_43§§§

#### 6. Elasticsearch

**Teste a conexão:**
§§§CÓDIGO_44§§§

**Resposta esperada:**
§§§CÓDIGO_45§§§

### Etapa 6: execute verificações de integridade

§§§CÓDIGO_46§§§

**Saída esperada:**
§§§CÓDIGO_47§§§

---

## Configuração pós-instalação

### 1. Inicialize o Dremio

§§§CÓDIGO_48§§§

**Cria:**
- Usuário administrador
- Fontes padrão (PostgreSQL, MinIO)
- Conjuntos de dados de exemplo

### 2. Inicializar Superconjunto

§§§CÓDIGO_49§§§

### 3. Configurar dbt

§§§CÓDIGO_50§§§

### 4. Configurar Airbyte

**Através da interface web (http://localhost:8000):**

1. Conclua o assistente de configuração
2. Configure a primeira fonte (ex: PostgreSQL)
3. Configure o destino (ex: MinIO S3)
4. Crie a conexão
5. Execute a primeira sincronização

**Via API:**
§§§CÓDIGO_51§§§

---

## Estrutura de diretório após instalação

§§§CÓDIGO_52§§§

---

## Solução de problemas

### Problemas Comuns

#### 1. Porta já usada

**Erro:**
§§§CÓDIGO_53§§§

**Solução:**
§§§CÓDIGO_54§§§

#### 2. Memória insuficiente

**Erro:**
§§§CÓDIGO_55§§§

**Solução:**
§§§CÓDIGO_56§§§

#### 3. Serviços não iniciam

**Verifique os registros:**
§§§CÓDIGO_57§§§

#### 4. Problemas de rede

**Redefinir rede Docker:**
§§§CÓDIGO_58§§§

#### 5. Problemas de permissões (Linux)

**Solução:**
§§§CÓDIGO_59§§§

---

## Desinstalação

### Pare os serviços

§§§CÓDIGO_60§§§

### Excluir dados (opcional)

§§§CÓDIGO_61§§§

### Excluir imagens do Docker

§§§CÓDIGO_62§§§

---

## Próximas etapas

Após instalação bem-sucedida:

1. **Configurar fontes de dados** - Consulte [Guia de configuração](configuration.md)
2. **Tutorial de primeiros passos** - Consulte [Primeiros passos](first-steps.md)
3. **Configuração do Airbyte** - Consulte [Guia de integração do Airbyte](../guides/airbyte-integration.md)
4. **Configuração Dremio** - Consulte [Guia de configuração Dremio](../guides/dremio-setup.md)
5. **Criar modelos dbt** - Consulte [Guia de desenvolvimento dbt](../guides/dbt-development.md)
6. **Criar painéis** - Consulte [Guia de painéis do Superset](../guides/superset-dashboards.md)

---

## Apoiar

Para problemas de instalação:

- **Documentação**: [Guia de solução de problemas](../guides/troubleshooting.md)
- **Problemas do GitHub**: https://github.com/your-org/dremiodbt/issues
- **Comunidade**: https://github.com/your-org/dremiodbt/discussions

---

**Versão do Guia de Instalação**: 3.2.0  
**Última atualização**: 16/10/2025  
**Mantido por**: Equipe da plataforma de dados