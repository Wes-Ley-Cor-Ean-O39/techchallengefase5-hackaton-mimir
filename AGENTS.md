# AGENTS.md · Mimir

## Contexto rápido
- Repo: `techchallengefase5-hackaton-mimir`
- Papel: worker assíncrono de geração de relatórios
- Runtime principal: container Python em pod no EKS
- Infra local: LocalStack (`s3`, `sqs`, `dynamodb`)

## Objetivo funcional
- Consumir mensagens da fila `requested-report`.
- Usar análise enviada pelo Heimdail ou buscar em `analises-arquitetura`.
- Gerar relatório Markdown/JSON.
- Persistir artefatos no bucket `techchallenge-fase5-reports`.

## Contratos e dados
- Fila entrada: `requested-report`
- Tabela de análise: `analises-arquitetura` (PK: `uploadId`)
- Bucket de relatórios: `techchallenge-fase5-reports`
- Prefixo padrão: `reports/<uploadId>/`

## Comandos úteis
```bash
cd /Users/wesleyazevedo/fiap/techchallengefase5-hackaton-mimir

# subir stack local
docker compose up -d --build

# logs worker
docker compose logs -f mimir

# validar relatorio
docker exec tc5-mimir-localstack awslocal s3 ls s3://techchallenge-fase5-reports/reports/demo-arq-001/
```

## CI/CD
- Workflow: `.github/workflows/ci.yml`
- Jobs: build, deploy (main), open-pr
- Deploy: build/push ECR + `helm upgrade --install` via `chart/mimir/values.yaml`
- Gates de qualidade: testes unitários com cobertura mínima de `80%` + `helm lint` + SonarCloud condicional.
- Runtime AWS no pod via role do node/EKS (`LabRole`); evitar credenciais `voclabs` em env vars do pod.

## Repositórios relacionados
- `techchallengefase5-hackaton-gatekeeper` (entrada/presign)
- `techchallengefase5-hackaton-heimdall` (análise IA)
- `techchallengefase5-hackaton-infra-k8s` (EKS/Kong/Datadog)

## Convenções desta pós
- README com `TL;DR`, contratos e guia de execução local.
- Arquitetura padrão do serviço: **Hexagonal (Ports and Adapters)**.
- Role padrão para infraestrutura/workloads AWS: **`LabRole`** (salvo exceção explícita).
- Qualidade mínima: cobertura unitária >= `80%` nos repos de app.
- Sempre registrar alterações de pipeline e variáveis no README.
