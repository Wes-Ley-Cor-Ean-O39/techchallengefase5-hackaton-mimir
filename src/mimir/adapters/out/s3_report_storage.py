from typing import Any, Dict

from mimir.application.use_cases.process_report import dump_json
from mimir.domain.entities import ReportArtifact, ReportRequest


class S3ReportStorage:
    def __init__(self, s3_client: Any, bucket: str, prefix: str) -> None:
        self._s3_client = s3_client
        self._bucket = bucket
        self._prefix = prefix.strip("/")

    def save_report(self, request: ReportRequest, markdown: str, payload: Dict[str, Any]) -> ReportArtifact:
        created_at = ReportArtifact.now_iso()
        base_key = f"{self._prefix}/{request.upload_id}" if self._prefix else request.upload_id
        markdown_key = f"{base_key}/report.md"
        json_key = f"{base_key}/report.json"

        self._s3_client.put_object(
            Bucket=self._bucket,
            Key=markdown_key,
            Body=markdown.encode("utf-8"),
            ContentType="text/markdown; charset=utf-8",
        )
        json_payload = {**payload, "report": {**payload["report"], "createdAt": created_at}}
        self._s3_client.put_object(
            Bucket=self._bucket,
            Key=json_key,
            Body=dump_json(json_payload).encode("utf-8"),
            ContentType="application/json; charset=utf-8",
        )

        return ReportArtifact(
            upload_id=request.upload_id,
            bucket=self._bucket,
            markdown_key=markdown_key,
            json_key=json_key,
            created_at=created_at,
        )
