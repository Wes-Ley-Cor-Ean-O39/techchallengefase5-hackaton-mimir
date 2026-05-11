from typing import Any, Dict, List, Protocol

from mimir.domain.entities import ReportArtifact, ReportRequest


class QueuePort(Protocol):
    def receive_messages(self, max_messages: int, wait_seconds: int) -> List[Dict[str, Any]]:
        ...

    def delete_message(self, receipt_handle: str) -> None:
        ...


class AnalysisRepositoryPort(Protocol):
    def get_by_upload_id(self, upload_id: str) -> Dict[str, Any]:
        ...


class ReportStoragePort(Protocol):
    def save_report(self, request: ReportRequest, markdown: str, payload: Dict[str, Any]) -> ReportArtifact:
        ...
