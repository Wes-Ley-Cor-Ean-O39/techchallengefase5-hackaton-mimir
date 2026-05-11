import pytest

from mimir.adapters.out.aws_queue import SqsQueueAdapter
from mimir.adapters.out.dynamodb_analysis_repository import DynamoDbAnalysisRepository
from mimir.adapters.out.s3_report_storage import S3ReportStorage
from mimir.config.settings import Settings
from mimir.domain.entities import ReportRequest


class SqsClient:
    def __init__(self):
        self.deleted = None

    def receive_message(self, **kwargs):
        self.kwargs = kwargs
        return {"Messages": [{"Body": "{}"}]}

    def delete_message(self, **kwargs):
        self.deleted = kwargs


class Table:
    def __init__(self, item=None):
        self.item = item

    def get_item(self, Key):
        self.key = Key
        return {"Item": self.item} if self.item else {}


class S3Client:
    def __init__(self):
        self.objects = []

    def put_object(self, **kwargs):
        self.objects.append(kwargs)


def _request():
    return ReportRequest(
        upload_id="u1",
        source_bucket="raw",
        source_key="uploads/a.png",
        media_type="image/png",
        analysis_text="analise",
        confidence=0.8,
        strategy_used="openai",
        analysis_created_at="now",
    )


def test_sqs_queue_adapter_receive_and_delete():
    client = SqsClient()
    adapter = SqsQueueAdapter(client, "queue-url")

    assert adapter.receive_messages(1, 2)
    adapter.delete_message("rh")

    assert client.kwargs["QueueUrl"] == "queue-url"
    assert client.deleted["ReceiptHandle"] == "rh"


def test_dynamodb_repository_gets_item_and_raises_when_missing():
    repo = DynamoDbAnalysisRepository(Table({"uploadId": "u1"}))
    assert repo.get_by_upload_id("u1")["uploadId"] == "u1"

    with pytest.raises(ValueError, match="nao encontrada"):
        DynamoDbAnalysisRepository(Table()).get_by_upload_id("u1")


def test_s3_report_storage_writes_markdown_and_json():
    client = S3Client()
    storage = S3ReportStorage(client, "reports-bucket", "reports")

    artifact = storage.save_report(_request(), "markdown", {"report": {"format": "markdown"}})

    assert artifact.markdown_key == "reports/u1/report.md"
    assert len(client.objects) == 2
    assert client.objects[0]["ContentType"].startswith("text/markdown")
    assert client.objects[1]["ContentType"].startswith("application/json")


def test_settings_validation(monkeypatch):
    monkeypatch.setenv("REPORT_REQUEST_QUEUE_URL", "queue")
    monkeypatch.setenv("ANALYSIS_TABLE_NAME", "table")
    monkeypatch.setenv("REPORTS_BUCKET_NAME", "bucket")

    settings = Settings.from_env()

    assert settings.aws_region == "us-east-1"


def test_settings_missing(monkeypatch):
    monkeypatch.delenv("REPORT_REQUEST_QUEUE_URL", raising=False)
    monkeypatch.delenv("ANALYSIS_TABLE_NAME", raising=False)
    monkeypatch.delenv("REPORTS_BUCKET_NAME", raising=False)

    with pytest.raises(ValueError, match="Missing required env vars"):
        Settings.from_env()
