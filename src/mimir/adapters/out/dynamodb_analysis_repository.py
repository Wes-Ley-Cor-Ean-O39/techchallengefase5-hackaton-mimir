from typing import Any, Dict


class DynamoDbAnalysisRepository:
    def __init__(self, dynamodb_table: Any) -> None:
        self._table = dynamodb_table

    def get_by_upload_id(self, upload_id: str) -> Dict[str, Any]:
        response = self._table.get_item(Key={"uploadId": upload_id})
        item = response.get("Item")
        if not item:
            raise ValueError(f"Analise nao encontrada para uploadId={upload_id}")
        return item
