# 📄 Mimir · Fase 5 Hackaton

## TL;DR
- **O que é:** worker assíncrono de geração de relatórios.
- **O que faz:** consome `requested-report`, gera Markdown/JSON e salva no S3 de relatórios.
- **Comando rápido:** `docker compose up -d --build`.
- **Deploy:** roda como pod no EKS via `chart/mimir`.

Mimir é a última peça do fluxo assíncrono. Ele recebe o evento `ANALYSIS_COMPLETED` publicado pelo Heimdail, materializa o relatório e armazena os artefatos no bucket de relatórios.

## 🎯 Objetivo do repositório
- Consumir eventos da fila `requested-report`.
- Reusar a análise recebida ou buscar pelo `uploadId` no DynamoDB.
- Gerar relatório Markdown e payload JSON.
- Persistir artefatos em `techchallenge-fase5-reports`.

## 🧱 Estrutura
```txt
src/
  mimir/
    domain/
    application/
    adapters/
    config/
    main.py
chart/
  mimir/
    values.yaml
    templates/deployment.yaml
```

## 📨 Contrato de entrada
```json
{
  "eventType": "ANALYSIS_COMPLETED",
  "uploadId": "demo-arq-001",
  "source": {
    "bucket": "techchallenge-fase5-raw",
    "key": "uploads/demo-arq-001.png",
    "mediaType": "image/png"
  },
  "analysis": {
    "text": "...",
    "confidence": 0.82,
    "strategyUsed": "multimodal_openai",
    "createdAt": "..."
  }
}
```

## 📦 Saída
- `s3://techchallenge-fase5-reports/reports/<uploadId>/report.md`
- `s3://techchallenge-fase5-reports/reports/<uploadId>/report.json`

## ⚙️ Variáveis de ambiente
- `AWS_REGION` (`us-east-1`)
- `AWS_ENDPOINT_URL` (opcional; LocalStack)
- `REPORT_REQUEST_QUEUE_URL`
- `ANALYSIS_TABLE_NAME`
- `REPORTS_BUCKET_NAME`
- `REPORTS_PREFIX` (`reports`)
- `POLL_WAIT_SECONDS` (`20`)
- `MAX_MESSAGES` (`5`)

## 🧪 Execução local
```bash
docker compose up -d --build
docker compose logs -f mimir
docker exec tc5-mimir-localstack awslocal s3 ls s3://techchallenge-fase5-reports/reports/demo-arq-001/
```

## 🚀 Deploy (EKS)
Chart base: `chart/mimir`.

As configurações não secretas ficam em `chart/mimir/values.yaml`. As credenciais AWS em runtime devem vir da role do node/EKS (`LabRole`), sem `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` ou `AWS_SESSION_TOKEN` no pod.

```bash
aws eks update-kubeconfig --name tc-fase5-hackaton-eks --region us-east-1

IMAGE_TAG=<TAG>

helm upgrade --install hackaton-mimir chart/mimir \
  -n default \
  -f chart/mimir/values.yaml \
  --set image.tag="$IMAGE_TAG"

kubectl rollout status deployment/hackaton-mimir -n default --timeout=180s
```

## 🤖 CI/CD
Workflow: `.github/workflows/ci.yml`

- `build`: valida Python, executa testes com cobertura mínima de `80%`, roda `helm lint` e builda Docker.
- `deploy`: push da imagem no ECR + deploy via Helm no EKS (somente `main`).
- `open-pr`: abre PR automático para `main` em branches de feature.
- `sonar`: análise SonarCloud condicional por secrets.

## 🔗 Repositórios relacionados
- `techchallengefase5-hackaton-gatekeeper`
- `techchallengefase5-hackaton-heimdall`
- `techchallengefase5-hackaton-infra-k8s`
