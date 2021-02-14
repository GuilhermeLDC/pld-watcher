# Monitoramento de PLD

## Introduction 

O projeto consiste em um crawler simples do pld diário, a partir do site do ccee. 
Os preços são salvos em um bucket, no S3, como html (raw) para que se possa parsear 
e extrair os preços, futuramente. O pld é salvo como uma resposta direta da página
para se manter sempre os dados raw e, caso haja alguma mudança de estrutura que 
inviabilize a extração, não será necessário recrawlear.
Há também um tópico SNS, usado para enviar um alerta via email, caso o crawlear receba um
status diferente de 200.

## Technologies

### Serverless framework 
Toda a infraestrutura é definida usando serverless framework. Basicamente, 
são definidos um tópico SNS e uma lambda, responsável pela coleta de dados diária.

## Launch

To install the serverless framework and the plugin used here:

```bash
    npm init
    npm install -g serverless
    npm install serverless-python-requirements 
```

To deploy:

```bash
    serverless deploy --stage anystage --email anyemail@bla.com  
```

The email passed will receive notifications from SNS topic.


The watcher function receive a event like :

```json
{"since": "dd/mm/yyyy", "until": "dd/mm/yyyy", "bucket": "bucket_name"}
```

Currently, any of these arguments are required. If *since* and *until* are not 
passed, then the period used will be *since" = yesterday and *until* = today.
However, if the *bucket" is not passed a bucket named *watcher-energy* will 
be used. You can change the name of the bucket to another as long as
a permisson to this new resource had been configured in *serverless.yml* 
in *iamRoleStatements*.
