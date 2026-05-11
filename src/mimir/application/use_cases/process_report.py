import json
import logging
from typing import Any, Dict

from mimir.application.ports import AnalysisRepositoryPort, ReportStoragePort
from mimir.domain.entities import ReportArtifact, ReportRequest

LOGGER = logging.getLogger(__name__)


class ReportMessageParser:
    def __init__(self, repository: AnalysisRepositoryPort) -> None:
        self._repository = repository

    def parse(self, message_body: Dict[str, Any]) -> ReportRequest:
        upload_id = str(message_body.get("uploadId") or message_body.get("id") or "").strip()
        if not upload_id:
            raise ValueError("Mensagem precisa conter uploadId")

        source = message_body.get("source") or {}
        analysis = message_body.get("analysis") or {}

        if not analysis.get("text"):
            stored = self._repository.get_by_upload_id(upload_id)
            source = {
                "bucket": stored.get("sourceBucket", source.get("bucket", "")),
                "key": stored.get("sourceKey", source.get("key", "")),
                "mediaType": stored.get("mediaType", source.get("mediaType", "")),
            }
            analysis = {
                "text": stored.get("analysis", ""),
                "confidence": stored.get("confidence", "0"),
                "strategyUsed": stored.get("strategyUsed", ""),
                "createdAt": stored.get("createdAt", ""),
            }

        text = str(analysis.get("text", "")).strip()
        if not text:
            raise ValueError(f"Analise ausente para uploadId={upload_id}")

        return ReportRequest(
            upload_id=upload_id,
            source_bucket=str(source.get("bucket", "")),
            source_key=str(source.get("key", "")),
            media_type=str(source.get("mediaType", "")),
            analysis_text=text,
            confidence=float(analysis.get("confidence") or 0.0),
            strategy_used=str(analysis.get("strategyUsed", "")),
            analysis_created_at=str(analysis.get("createdAt", "")),
        )


class GenerateReportUseCase:
    def __init__(self, parser: ReportMessageParser, storage: ReportStoragePort) -> None:
        self._parser = parser
        self._storage = storage

    def execute(self, message_body: Dict[str, Any]) -> ReportArtifact:
        request = self._parser.parse(message_body)
        LOGGER.info(
            "Geracao de relatorio solicitada. uploadId=%s bucket=%s key=%s",
            request.upload_id,
            request.source_bucket,
            request.source_key,
        )
        markdown = self._build_markdown(request)
        payload = self._build_payload(request, markdown)
        return self._storage.save_report(request=request, markdown=markdown, payload=payload)

    @staticmethod
    def _build_markdown(request: ReportRequest) -> str:
        return "\n".join(
            [
                f"# Relatorio de Analise Arquitetural",
                "",
                f"Upload ID: `{request.upload_id}`",
                f"Origem: `{request.source_bucket}/{request.source_key}`",
                f"Tipo de midia: `{request.media_type}`",
                f"Estrategia: `{request.strategy_used}`",
                f"Confianca: `{request.confidence:.2f}`",
                "",
                "## Analise",
                "",
                request.analysis_text,
                "",
            ]
        )

    @staticmethod
    def _build_payload(request: ReportRequest, markdown: str) -> Dict[str, Any]:
        return {
            "uploadId": request.upload_id,
            "source": {
                "bucket": request.source_bucket,
                "key": request.source_key,
                "mediaType": request.media_type,
            },
            "analysis": {
                "confidence": request.confidence,
                "strategyUsed": request.strategy_used,
                "createdAt": request.analysis_created_at,
            },
            "report": {
                "format": "markdown",
                "content": markdown,
            },
        }


def dump_json(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)
