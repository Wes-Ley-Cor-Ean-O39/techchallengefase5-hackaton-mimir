# Base de Conhecimento Local - Mimir

## Padrões reaproveitados
- Serviços desacoplados por SQS/eventos.
- Configuração de ambiente em `chart/*/values.yaml`.
- Segredos em Kubernetes Secret para workloads em EKS Academy.
- Testes unitários com cobertura mínima de 80%.
- CI com build, testes, `helm lint`, deploy em `main` e auto PR em branch.

## Guardrails
- Não chamar OpenAI neste serviço; a análise técnica é responsabilidade do Heimdail.
- Não gerar presign/upload aqui; entrada é responsabilidade do Gatekeeper.
- Mimir apenas materializa relatórios a partir do evento `ANALYSIS_COMPLETED`.
