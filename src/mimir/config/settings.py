import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    aws_region: str
    aws_endpoint_url: str
    report_request_queue_url: str
    analysis_table_name: str
    reports_bucket_name: str
    reports_prefix: str
    poll_wait_seconds: int
    max_messages: int

    @staticmethod
    def from_env() -> "Settings":
        settings = Settings(
            aws_region=os.getenv("AWS_REGION", "us-east-1"),
            aws_endpoint_url=os.getenv("AWS_ENDPOINT_URL", ""),
            report_request_queue_url=os.getenv("REPORT_REQUEST_QUEUE_URL", ""),
            analysis_table_name=os.getenv("ANALYSIS_TABLE_NAME", ""),
            reports_bucket_name=os.getenv("REPORTS_BUCKET_NAME", ""),
            reports_prefix=os.getenv("REPORTS_PREFIX", "reports"),
            poll_wait_seconds=int(os.getenv("POLL_WAIT_SECONDS", "20")),
            max_messages=int(os.getenv("MAX_MESSAGES", "5")),
        )
        settings.validate()
        return settings

    def validate(self) -> None:
        required = {
            "REPORT_REQUEST_QUEUE_URL": self.report_request_queue_url,
            "ANALYSIS_TABLE_NAME": self.analysis_table_name,
            "REPORTS_BUCKET_NAME": self.reports_bucket_name,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise ValueError(f"Missing required env vars: {', '.join(missing)}")
        if self.poll_wait_seconds < 0:
            raise ValueError("POLL_WAIT_SECONDS nao pode ser negativo")
        if self.max_messages <= 0:
            raise ValueError("MAX_MESSAGES deve ser maior que zero")
