import boto3

from mimir.adapters.out.aws_queue import SqsQueueAdapter
from mimir.adapters.out.dynamodb_analysis_repository import DynamoDbAnalysisRepository
from mimir.adapters.out.s3_report_storage import S3ReportStorage
from mimir.application.services.worker_service import WorkerService
from mimir.application.use_cases.process_report import GenerateReportUseCase, ReportMessageParser
from mimir.config.settings import Settings


def build_worker() -> WorkerService:
    settings = Settings.from_env()
    endpoint_url = settings.aws_endpoint_url or None

    sqs_client = boto3.client("sqs", region_name=settings.aws_region, endpoint_url=endpoint_url)
    dynamodb = boto3.resource("dynamodb", region_name=settings.aws_region, endpoint_url=endpoint_url)
    s3_client = boto3.client("s3", region_name=settings.aws_region, endpoint_url=endpoint_url)

    repository = DynamoDbAnalysisRepository(
        dynamodb_table=dynamodb.Table(settings.analysis_table_name),
    )
    parser = ReportMessageParser(repository=repository)
    storage = S3ReportStorage(
        s3_client=s3_client,
        bucket=settings.reports_bucket_name,
        prefix=settings.reports_prefix,
    )
    use_case = GenerateReportUseCase(parser=parser, storage=storage)
    queue = SqsQueueAdapter(sqs_client=sqs_client, queue_url=settings.report_request_queue_url)

    return WorkerService(
        queue=queue,
        use_case=use_case,
        max_messages=settings.max_messages,
        poll_wait_seconds=settings.poll_wait_seconds,
    )
