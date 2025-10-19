# Guia de solução de problemas

**Versão**: 3.2.0  
**Última atualização**: 16 de outubro de 2025  
**Idioma**: Francês

## Índice

1. [Visão geral](#visão geral)
2. [Abordagem geral de solução de problemas](#abordagem geral de solução de problemas)
3. [Problemas do Airbyte](#problemas do Airbyte)
4. [Problemas de Dremio](#dremio-problems)
5. [problemas de dbt](#problemas de dbt)
6. [Problemas de superconjunto](#problemas de superconjunto)
7. [Problemas do PostgreSQL](#problemas do postgresql)
8. [Problemas MinIO](#minio-problemas)
9. [Problemas do Elasticsearch](#problemas do Elasticsearch)
10. [Rede e conectividade](#rede e conectividade)
11. [Problemas de desempenho](#problemas de desempenho)
12. [Problemas de qualidade de dados](#problemas de qualidade de dados)

---

## Visão geral

Este guia abrangente de solução de problemas ajuda a diagnosticar e resolver problemas comuns em todos os componentes da plataforma. Os problemas são organizados por componentes com sintomas, diagnósticos e soluções claros.

### Metodologia de solução de problemas

§§§CÓDIGO_0§§§

---

## Abordagem geral de solução de problemas

### Etapa 1: Verifique o status dos serviços

§§§CÓDIGO_1§§§

### Etapa 2: verificar os registros

§§§CÓDIGO_2§§§

### Etapa 3: verifique a conectividade da rede

§§§CÓDIGO_3§§§

### Etapa 4: verifique o uso de recursos

§§§CÓDIGO_4§§§

### Correções rápidas comuns

§§§CÓDIGO_5§§§

---

## Problemas com Airbytes

### Problema 1: A interface do Airbyte não carrega

**Sintomas**:
- O navegador exibe "Não é possível conectar" ou tempo limite
- URL: `http://localhost:8000` não responde

**Diagnóstico**:
§§§CÓDIGO_7§§§

**Soluções**:

1. **Verifique se a porta não está em uso**:
   §§§CÓDIGO_8§§§

2. **Reinicie os contêineres Airbyte**:
   §§§CÓDIGO_9§§§

3. **Verifique se o servidor está íntegro**:
   §§§CÓDIGO_10§§§

### Problema 2: A sincronização falha com "Tempo limite de conexão"

**Sintomas**:
- A tarefa de sincronização falha ou trava imediatamente
- Erro: "Tempo limite de conexão" ou "Não é possível conectar à fonte"

**Diagnóstico**:
§§§CÓDIGO_11§§§

**Soluções**:

1. **Verifique os identificadores de origem**:
   §§§CÓDIGO_12§§§

2. **Aumente o tempo limite**:
   §§§CÓDIGO_13§§§

3. **Verifique a rede**:
   §§§CÓDIGO_14§§§

### Problema 3: Sem memória durante a sincronização

**Sintomas**:
- O trabalhador do contêiner trava durante grandes sincronizações
- Erro: "OutOfMemoryError" ou "Espaço de heap Java"

**Diagnóstico**:
§§§CÓDIGO_15§§§

**Soluções**:

1. **Aumente a memória do trabalhador**:
   §§§CÓDIGO_16§§§

2. **Reduza o tamanho do lote**:
   §§§CÓDIGO_17§§§

3. **Use sincronização incremental**:
   §§§CÓDIGO_18§§§

### Problema 4: os dados não aparecem no destino

**Sintomas**:
- A sincronização foi concluída com sucesso
- Sem erros nos logs
- Os dados não estão no MinIO/destino

**Diagnóstico**:
§§§CÓDIGO_19§§§

**Soluções**:

1. **Verifique a configuração do destino**:
   §§§CÓDIGO_20§§§

2. **Verifique a normalização**:
   §§§CÓDIGO_21§§§

3. **Verificação manual**:
   §§§CÓDIGO_22§§§

---

## Problemas Dremio

### Problema 1: Não é possível conectar-se à interface Dremio

**Sintomas**:
- O navegador mostra erro de conexão em `http://localhost:9047`

**Diagnóstico**:
§§§CÓDIGO_24§§§

**Soluções**:

1. **Aguarde a inicialização completa** (pode levar de 2 a 3 minutos):
   §§§CÓDIGO_25§§§

2. **Aumentar memória**:
   §§§CÓDIGO_26§§§

3. **Limpar dados do Dremio** (⚠️ redefine a configuração):
   §§§CÓDIGO_27§§§

### Problema 2: "Fonte off-line" para MinIO

**Sintomas**:
- A fonte MinIO exibe um indicador vermelho “Offline”
- Erro: "Não é possível conectar à fonte"

**Diagnóstico**:
§§§CÓDIGO_28§§§

**Soluções**:

1. **Verifique o endpoint MinIO**:
   §§§CÓDIGO_29§§§

2. **Verifique as credenciais**:
   §§§CÓDIGO_30§§§

3. **Atualizar metadados**:
   §§§CÓDIGO_31§§§

### Problema 3: desempenho lento da consulta

**Sintomas**:
- As consultas levam mais de 10 segundos
- Os painéis demoram para carregar

**Diagnóstico**:
§§§CÓDIGO_32§§§

**Soluções**:

1. **Crie reflexões**:
   §§§CÓDIGO_33§§§

2. **Adicionar filtros de partição**:
   §§§CÓDIGO_34§§§

3. **Aumentar a memória do executor**:
   §§§CÓDIGO_35§§§

### Problema 4: A reflexão não constrói

**Sintomas**:
- A reflexão permanece presa no estado "REFRESHING"
- Nunca acaba

**Diagnóstico**:
§§§CÓDIGO_36§§§

**Soluções**:

1. **Desativar e reativar**:
   §§§CÓDIGO_37§§§

2. **Verifique os dados de origem**:
   §§§CÓDIGO_38§§§

3. **Aumente o tempo limite**:
   §§§CÓDIGO_39§§§

---

## problemas de banco de dados

### Problema 1: "Erro de conexão" ao executar o dbt

**Sintomas**:
- `dbt debug` falha
- Erro: "Não foi possível conectar ao Dremio"

**Diagnóstico**:
§§§CÓDIGO_41§§§

**Soluções**:

1. **Verifique perfis.yml**:
   §§§CÓDIGO_42§§§

2. **Teste a conectividade do Dremio**:
   §§§CÓDIGO_43§§§

3. **Instale o adaptador Dremio**:
   §§§CÓDIGO_44§§§

### Problema 2: O modelo não é construído

**Sintomas**:
- `dbt run` falha para um modelo específico
- Erro de compilação ou execução SQL

**Diagnóstico**:
§§§CÓDIGO_46§§§

**Soluções**:

1. **Verifique a sintaxe do modelo**:
   §§§CÓDIGO_47§§§

2. **Teste primeiro em um SQL IDE**:
   §§§CÓDIGO_48§§§

3. **Verifique as dependências**:
   §§§CÓDIGO_49§§§

### Problema 3: os testes falham

**Sintomas**:
- `dbt test` relata falhas
- Problemas de qualidade de dados detectados

**Diagnóstico**:
§§§CÓDIGO_51§§§

**Soluções**:

1. **Corrija os dados de origem**:
   §§§CÓDIGO_52§§§

2. **Ajuste o limite de teste**:
   §§§CÓDIGO_53§§§

3. **Investigar a causa raiz**:
   §§§CÓDIGO_54§§§

### Problema 4: O modelo incremental não funciona

**Sintomas**:
- O modelo incremental é completamente reconstruído cada vez que é executado
- Nenhum comportamento incremental

**Diagnóstico**:
§§§CÓDIGO_55§§§

**Soluções**:

1. **Adicione requisitos de sistema**:
   §§§CÓDIGO_56§§§

2. **Adicionar lógica incremental**:
   §§§CÓDIGO_57§§§

3. **Forçar uma atualização completa uma vez**:
   §§§CÓDIGO_58§§§

---

## Problemas de superconjunto

### Problema 1: Não é possível conectar ao Superset

**Sintomas**:
- A página de login exibe "Credenciais inválidas"
- O par admin/admin padrão não funciona

**Diagnóstico**:
§§§CÓDIGO_59§§§

**Soluções**:

1. **Redefinir senha de administrador**:
   §§§CÓDIGO_60§§§

2. **Crie um usuário administrador**:
   §§§CÓDIGO_61§§§

3. **Redefinir superconjunto**:
   §§§CÓDIGO_62§§§

### Problema 2: falha na conexão com o banco de dados

**Sintomas**:
- O botão “Testar conexão” falha
- Erro: "Não é possível conectar ao banco de dados"

**Diagnóstico**:
§§§CÓDIGO_63§§§

**Soluções**:

1. **Use o URI SQLAlchemy correto**:
   §§§CÓDIGO_64§§§

2. **Instale os drivers necessários**:
   §§§CÓDIGO_65§§§

3. **Verifique a rede**:
   §§§CÓDIGO_66§§§

### Problema 3: os gráficos não carregam

**Sintomas**:
- O painel exibe um botão giratório de carregamento indefinidamente
- Gráficos exibem "Erro ao carregar dados"

**Diagnóstico**:
§§§CÓDIGO_67§§§

**Soluções**:

1. **Verifique o tempo limite da consulta**:
   §§§CÓDIGO_68§§§

2. **Ativar solicitações assíncronas**:
   §§§CÓDIGO_69§§§

3. **Limpar cache**:
   §§§CÓDIGO_70§§§

### Problema 4: erros de permissão

**Sintomas**:
- O usuário não pode ver os painéis
- Erro: "Você não tem acesso a este painel"

**Diagnóstico**:
§§§CÓDIGO_71§§§

**Soluções**:

1. **Adicione o usuário a uma função**:
   §§§CÓDIGO_72§§§

2. **Conceder acesso ao painel**:
   §§§CÓDIGO_73§§§

3. **Verifique as regras do RLS**:
   §§§CÓDIGO_74§§§

---

## Problemas do PostgreSQL

### Problema 1: Conexão recusada

**Sintomas**:
- Os aplicativos não podem se conectar ao PostgreSQL
- Erro: "Conexão recusada" ou "Não foi possível conectar"

**Diagnóstico**:
§§§CÓDIGO_75§§§

**Soluções**:

1. **Reinicie o PostgreSQL**:
   §§§CÓDIGO_76§§§

2. **Verifique o mapeamento da porta**:
   §§§CÓDIGO_77§§§

3. **Verifique as credenciais**:
   §§§CÓDIGO_78§§§

### Problema 2: Falta de conexões

**Sintomas**:
- Erro: "FATAL: os slots de conexão restantes estão reservados"
- Os aplicativos falham intermitentemente na conexão

**Diagnóstico**:
§§§CÓDIGO_79§§§

**Soluções**:

1. **Aumentar max_connections**:
   §§§CÓDIGO_80§§§

2. **Use pool de conexões**:
   §§§CÓDIGO_81§§§

3. **Elimine conexões inativas**:
   §§§CÓDIGO_82§§§

### Problema 3: consultas lentas

**Sintomas**:
- As consultas ao banco de dados demoram vários segundos
- Os aplicativos expiram

**Diagnóstico**:
§§§CÓDIGO_83§§§

**Soluções**:

1. **Criar índices**:
   §§§CÓDIGO_84§§§

2. **Execute ANALISAR**:
   §§§CÓDIGO_85§§§

3. **Aumentar buffers_compartilhados**:
   §§§CÓDIGO_86§§§

---

##Problemas de MinIO

### Problema 1: não é possível acessar o console MinIO

**Sintomas**:
- O navegador exibe um erro em `http://localhost:9001`

**Diagnóstico**:
§§§CÓDIGO_88§§§

**Soluções**:

1. **Verifique as portas**:
   §§§CÓDIGO_89§§§

2. **Acesse a URL correta**:
   §§§CÓDIGO_90§§§

3. **Reinicie o MinIO**:
   §§§CÓDIGO_91§§§

### Problema 2: Erros de acesso negado

**Sintomas**:
- Os aplicativos não podem ler/gravar no S3
- Erro: "Acesso negado" ou "403 Proibido"

**Diagnóstico**:
§§§CÓDIGO_92§§§

**Soluções**:

1. **Verifique as credenciais**:
   §§§CÓDIGO_93§§§

2. **Verifique a política do bucket**:
   §§§CÓDIGO_94§§§

3. **Crie uma chave de acesso para o aplicativo**:
   §§§CÓDIGO_95§§§

### Problema 3: Balde não encontrado

**Sintomas**:
- Erro: "O intervalo especificado não existe"

**Diagnóstico**:
§§§CÓDIGO_96§§§

**Soluções**:

1. **Crie o intervalo**:
   §§§CÓDIGO_97§§§

2. **Verifique o nome do bucket na configuração**:
   §§§CÓDIGO_98§§§

---

## Rede e conectividade

### Problema: os serviços não conseguem se comunicar

**Sintomas**:
- “Conexão recusada” entre containers
- Erros de “Host não encontrado”

**Diagnóstico**:
§§§CÓDIGO_99§§§

**Soluções**:

1. **Certifique-se de que todos os serviços estejam na mesma rede**:
   §§§CÓDIGO_100§§§

2. **Use nomes de contêiner, não localhost**:
   §§§CÓDIGO_101§§§

3. **Recriar a rede**:
   §§§CÓDIGO_102§§§

---

## Problemas de desempenho

### Problema: alto uso da CPU

**Diagnóstico**:
§§§CÓDIGO_103§§§

**Soluções**:

1. **Limitar solicitações concorrentes**:
   §§§CÓDIGO_104§§§

2. **Otimize consultas** (consulte [Problemas do Dremio](#dremio-issues))

3. **Aumentar a alocação de CPU**:
   §§§CÓDIGO_105§§§

### Problema: Alto uso de memória

**Diagnóstico**:
§§§CÓDIGO_106§§§

**Soluções**:

1. **Aumente o tamanho do heap**:
   §§§CÓDIGO_107§§§

2. **Ativar derramamento de disco**:
   §§§CÓDIGO_108§§§

---

## Problemas de qualidade de dados

Veja as soluções detalhadas no [Guia de qualidade de dados](./data-quality.md).

### Verificações rápidas

§§§CÓDIGO_109§§§

---

## Resumo

Este guia de solução de problemas abordou:

- **Abordagem geral**: Metodologia sistemática para diagnóstico de problemas
- **Problemas por componente**: Soluções para os 7 serviços da plataforma
- **Problemas de rede**: problemas de conectividade de contêineres
- **Problemas de desempenho**: otimização de CPU, memória e consulta
- **Problemas de qualidade de dados**: problemas e verificações comuns de dados

**Principais conclusões**:
- Sempre verifique os registros primeiro: `docker-compose logs [service]`
- Use nomes de contêineres, não localhost, para comunicação entre serviços
- Teste de conectividade: `docker exec [container] ping [target]`
- Monitorar recursos: `docker stats`
- Comece de forma simples: reinicie o serviço antes da depuração complexa

**Documentação relacionada:**
- [Guia de instalação](../getting-started/installation.md)
- [Guia de configuração](../getting-started/configuration.md)
- [Guia de qualidade de dados](./data-quality.md)
- [Arquitetura: Implantação](../architecture/deployment.md)

**Precisa de mais ajuda?**
- Verifique os logs do componente: `docker-compose logs -f [service]`
- Consulte a documentação do serviço
- Pesquise problemas do GitHub
- Entre em contato com a equipe de suporte

---

**Versão**: 3.2.0  
**Última atualização**: 16 de outubro de 2025