from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class ReportRequest:
    upload_id: str
    source_bucket: str
    source_key: str
    media_type: str
    analysis_text: str
    confidence: float
    strategy_used: str
    analysis_created_at: str


@dataclass(frozen=True)
class ReportArtifact:
    upload_id: str
    bucket: str
    markdown_key: str
    json_key: str
    created_at: str

    @staticmethod
    def now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()
