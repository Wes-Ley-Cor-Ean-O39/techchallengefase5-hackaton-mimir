# Playbook Operacional - Mimir

## Escopo
Worker assíncrono para geração de relatórios a partir de análises arquiteturais.

## Fluxo esperado
1. consumir evento de `requested-report`
2. validar `uploadId`
3. usar análise do evento ou buscar em `analises-arquitetura`
4. gerar relatório Markdown/JSON
5. salvar em `techchallenge-fase5-reports/reports/<uploadId>/`

## Comandos base
```bash
docker compose up -d --build
docker compose logs -f mimir
```

## CI/CD padrão
- build + testes + cobertura mínima
- `helm lint` em `chart/mimir`
- push ECR e deploy EKS apenas em `main`

## Guardrails
- Não processar arquivos brutos diretamente; usar resultado do Heimdail.
- AWS runtime usa Secret Kubernetes `mimir-aws` com credenciais temporarias do AWS Academy; atualizar o Secret quando o lab rotacionar credenciais.
