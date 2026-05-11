#!/bin/sh
set -e

awslocal s3 mb s3://techchallenge-fase5-reports || true
awslocal sqs create-queue --queue-name requested-report >/dev/null

awslocal dynamodb create-table \
  --table-name analises-arquitetura \
  --attribute-definitions AttributeName=uploadId,AttributeType=S \
  --key-schema AttributeName=uploadId,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST >/dev/null 2>&1 || true

awslocal dynamodb put-item \
  --table-name analises-arquitetura \
  --item '{"uploadId":{"S":"demo-arq-001"},"sourceBucket":{"S":"techchallenge-fase5-raw"},"sourceKey":{"S":"uploads/demo-arq-001.png"},"mediaType":{"S":"image/png"},"analysis":{"S":"Componentes identificados: API Gateway, Kong, EKS, SQS, DynamoDB e S3. Recomendacoes: validar DLQ, observabilidade e politicas IAM minimas."},"confidence":{"S":"0.82"},"strategyUsed":{"S":"multimodal_openai"},"createdAt":{"S":"2026-05-10T00:00:00Z"}}' >/dev/null

QUEUE_URL=$(awslocal sqs get-queue-url --queue-name requested-report --query QueueUrl --output text)
awslocal sqs send-message \
  --queue-url "$QUEUE_URL" \
  --message-body '{"eventType":"ANALYSIS_COMPLETED","uploadId":"demo-arq-001","source":{"bucket":"techchallenge-fase5-raw","key":"uploads/demo-arq-001.png","mediaType":"image/png"},"analysis":{"text":"Componentes identificados: API Gateway, Kong, EKS, SQS, DynamoDB e S3. Recomendacoes: validar DLQ, observabilidade e politicas IAM minimas.","confidence":0.82,"strategyUsed":"multimodal_openai","createdAt":"2026-05-10T00:00:00Z"}}' >/dev/null
