# Projeto HowBootcamps
## Projeto do bootcamp de Engenharia de Dados

</p>

## 📝 Sumário

- [Objetivo](#objetivo)
- [Escopo](#escopo)
- [Arquitetura](#arquitetura)
- [Próximos passos](#next)

##  Objetivo <a name = "objetivo"></a>

Este projeto corresponde ao terceiro e último desafio do bootcamp de engenharia de dados da How bootcamps.

O objetivo consiste em prover, ao time de analistas de mídia, uma acesso rápido e unificado aos dados referentes a operação de mídia paga. Inlucindo, principalmente: investimento, resultado e histórico de KPIs internos.

No escopo atual, o projeto gera dois principais benefícios:
- Dados sob demanda: O analista pode solicitar dados de campanha através do Slack, sem restrições de permissões ou necessidade de lidar com interfaces de diferentes plataformas. Os dados obtidos través deste método são atuais e consolidados;
- Dados históricos de operação: O gestor pode acompanhar o histórico dos KPIs(de controle interno), em um visão consolidada com dados obtidos das plataformas. Isso gera a oportunidade de estimar a possibilidade de Churn, baseado no não atingimento de metas e baixa performance;  

##  Escopo <a name = "escopo"></a>

O escopo do projeto inclui a extração de dados de campanha nas plataforma de mídia Google Ads e Meta Ads. Dados referentes a operação, como KPIs internos, são obtidos na Monday.com(ferramenta de gestão de projetos). 
Os dados serão disponibilizados para consumo através de "Slash Commands" no Slack(ferramneta de comunicação interna), e em dashboard desenvolvido em Streamlit.



[Respositório referente ao dashboard em Streamlit](https://github.com/jgdemattos/adops_snapshot_front)

##  Arquitetura <a name = "arquitetura"></a>

![Untitled-2024-05-04-1043](https://github.com/jgdemattos/adops_snapshot_front/assets/4052149/9fac6b70-411e-4620-b181-be9d2697497d)

A arquitetura é composta de scripts python no Google Cloud Funcions, com dois principais endpoints: 
- "raiox" respondável por responder requisições geradas pelo Slack(via Slash Commands), acionado a partir de "tópicos" do Cloud pub/sub;
- "adsops_snapshot" reponsável por fazer a ingestão diária de dados no Bucket que alimentará o Dashboard, acionado a partir de um agendamento no Cloud Scheduler(Diariamente);

O uso de pub/sub se fez necessário para adequar ao modelo de resposta esperado pela API do Slack.

### Fluxo

Os dados referentes à operação, como KPIs dos clientes ou IDs das contas de anúncios a serem requisitadas, são obtidos através da "Monday.com". De modo a integrar com o fluxo de processos de onboarding da agência.
Com os IDs obtidos, é possível solicitar dados de campanha das contas Meta e Google de cada cliente. Dependendo do endpoint acionado, estes dados são armazenados em um Bucket, para serem posteriormente consumidos em dashboard, 
ou são estruturados em uma mensagem de resposta, a ser publicada no slack.

### Arquitetura de classes

Para ambos os fluxos, foi concebida uma arquitetura de classes, de modo a estruturar os dados de diferentes plataformas de mídia sob o padrão a ser disponibilizado no frontend.

``` mermaid
classDiagram
    MetaBusinessmanager *-- MetaAdaccount
    MetaAdaccount *-- MetaCampaign
    MetaCampaign *-- MetaAdset
    GoogleAccount *-- GoogleCampaign

    class MetaBusinessmanager{
      meta_businessmanager_name :str
      adaccounts : array
      meta_businessmanager_id:str
      set_meta_businessmanager_name()
      set_meta_adaccounts()
      calculate_total_spend()
      calculate_total_budget()
    }
    class MetaAdaccount{
      id:str
      name:str
      owned:boolean
      campaigns:array
    }
    class MetaCampaign{
      daily_results:array
      spend:float
      adsets:array
      id:str
      name:str
      cbo:boolean
      budget:float
      effectiveStatus:str
      setEffectiveStatus()
      add_spend()
      set_budget()
      get_budget()
      add_investment()
      get_total_spend_from_daily()
      get_total_spend()
      get_linear_projection()
      get_total_budget()
    }
    class MetaAdset{
        city  :  str
        set_budget()
        add_spend()
        setEffectiveStatus()
    }
    class GoogleAccount{
      account_id:str
      campaigns:array
      set_google_campaigns()
      get_total_budget()
      get_total_cost()
      calculate_spend_projection()
    }
    class GoogleCampaign{
      campaign_id:str
      campaign_name:str
      cost:float
      budget:float
      effectiveStatus:str
      get_total_budget()
      get_total_cost()
    }

    class MessageBuilder{
      client_name:str
      channel_id:str
      businessmanagers:array
      google_accounts:array
      CANAL_SLACK:str
      count_meta_adaccounts()
      count_meta_campaigns()
      count_google_campaigns()
      set_businessmanagers()
      set_google_accounts()
      calculate_total_projection()
      build_message()
    }

```
## Interfaces

### Mensagem no Slack
![Captura de tela 2024-05-04 125316](https://github.com/jgdemattos/adops_snapshot_front/assets/4052149/ff350771-dc80-4323-8c6d-c2e9415a72f2)

### Dashboard Streamlit
![Captura de tela 2024-05-04 124900](https://github.com/jgdemattos/adops_snapshot_front/assets/4052149/969eba46-13d3-49af-a2e9-f639dbf648ba)


##  Próximos Passos <a name = "next"></a>

- Próximos passos incluem a extensão dos dados de operação obtidos, de modo a contemplar também informações sobre o contrato(data de assinatura, tempo de fidelidade, valores negociados etc).
- Efetuar a ingestão dados históricos, anteriores ao início da extração via agendamento diário(Abr/24);
- Ampliar os dados extraídos das plataformas, de modo a incluir também Impressões, Cliques e Custo por mil impressões;
- Utilizar o histórico mais longo, e conjunto de dados mais amplo, para criar um modelo que identifique clientes sob maior risco de churn; 
