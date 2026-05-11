import json
import logging
import time
from typing import Any, Dict

from mimir.application.ports import QueuePort
from mimir.application.use_cases.process_report import GenerateReportUseCase

LOGGER = logging.getLogger(__name__)


class WorkerService:
    def __init__(
        self,
        queue: QueuePort,
        use_case: GenerateReportUseCase,
        max_messages: int,
        poll_wait_seconds: int,
    ) -> None:
        self._queue = queue
        self._use_case = use_case
        self._max_messages = max_messages
        self._poll_wait_seconds = poll_wait_seconds

    def run_forever(self) -> None:
        LOGGER.info(
            "Mimir iniciado. max_messages=%s poll_wait_seconds=%s",
            self._max_messages,
            self._poll_wait_seconds,
        )
        while True:
            try:
                messages = self._queue.receive_messages(self._max_messages, self._poll_wait_seconds)
            except Exception as exc:  # pragma: no cover
                LOGGER.exception("Falha ao ler fila de relatorios: %s", exc)
                time.sleep(2)
                continue
            for message in messages:
                self._process_message_safe(message)

    def _process_message_safe(self, message: Dict[str, Any]) -> None:
        receipt_handle = message.get("ReceiptHandle", "")
        try:
            body = json.loads(message.get("Body", "{}"))
            artifact = self._use_case.execute(body)
            LOGGER.info(
                "Relatorio gerado. upload_id=%s markdown=s3://%s/%s",
                artifact.upload_id,
                artifact.bucket,
                artifact.markdown_key,
            )
            if receipt_handle:
                self._queue.delete_message(receipt_handle)
        except Exception as exc:  # pragma: no cover
            LOGGER.exception("Falha ao gerar relatorio: %s", exc)
            time.sleep(1)
