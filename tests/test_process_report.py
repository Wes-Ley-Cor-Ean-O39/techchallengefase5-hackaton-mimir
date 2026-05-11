import pytest

from mimir.application.use_cases.process_report import GenerateReportUseCase, ReportMessageParser


class Repository:
    def __init__(self):
        self.item = {
            "uploadId": "u1",
            "sourceBucket": "raw",
            "sourceKey": "uploads/a.png",
            "mediaType": "image/png",
            "analysis": "analise persistida",
            "confidence": "0.7",
            "strategyUsed": "multimodal_openai",
            "createdAt": "now",
        }

    def get_by_upload_id(self, upload_id):
        assert upload_id == "u1"
        return self.item


class Storage:
    def __init__(self):
        self.saved = None

    def save_report(self, request, markdown, payload):
        self.saved = (request, markdown, payload)
        return type(
            "Artifact",
            (),
            {
                "upload_id": request.upload_id,
                "bucket": "reports",
                "markdown_key": "reports/u1/report.md",
                "json_key": "reports/u1/report.json",
            },
        )()


def test_parse_message_with_analysis_payload():
    parser = ReportMessageParser(repository=Repository())
    request = parser.parse(
        {
            "uploadId": "u1",
            "source": {"bucket": "raw", "key": "uploads/a.png", "mediaType": "image/png"},
            "analysis": {
                "text": "analise do evento",
                "confidence": 0.9,
                "strategyUsed": "openai",
                "createdAt": "now",
            },
        }
    )

    assert request.upload_id == "u1"
    assert request.analysis_text == "analise do evento"
    assert request.confidence == 0.9


def test_parse_message_fetches_from_repository_when_text_missing():
    parser = ReportMessageParser(repository=Repository())
    request = parser.parse({"uploadId": "u1"})

    assert request.analysis_text == "analise persistida"
    assert request.source_bucket == "raw"


def test_parse_message_requires_upload_id():
    parser = ReportMessageParser(repository=Repository())
    with pytest.raises(ValueError, match="uploadId"):
        parser.parse({})


def test_generate_report_use_case_saves_markdown_and_payload():
    storage = Storage()
    parser = ReportMessageParser(repository=Repository())
    use_case = GenerateReportUseCase(parser=parser, storage=storage)

    artifact = use_case.execute({"uploadId": "u1"})

    assert artifact.markdown_key == "reports/u1/report.md"
    request, markdown, payload = storage.saved
    assert request.upload_id == "u1"
    assert "# Relatorio de Analise Arquitetural" in markdown
    assert payload["uploadId"] == "u1"
