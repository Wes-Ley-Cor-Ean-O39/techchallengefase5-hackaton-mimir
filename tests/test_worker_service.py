from mimir.application.services.worker_service import WorkerService


class Queue:
    def __init__(self):
        self.deleted = None
        self.calls = 0

    def receive_messages(self, max_messages, wait_seconds):
        self.calls += 1
        if self.calls > 1:
            raise KeyboardInterrupt()
        return [{"Body": '{"uploadId":"u1"}', "ReceiptHandle": "rh"}]

    def delete_message(self, receipt_handle):
        self.deleted = receipt_handle


class UseCase:
    def execute(self, body):
        assert body["uploadId"] == "u1"
        return type("Artifact", (), {"upload_id": "u1", "bucket": "b", "markdown_key": "k"})()


def test_worker_processes_message_and_deletes():
    queue = Queue()
    worker = WorkerService(queue=queue, use_case=UseCase(), max_messages=1, poll_wait_seconds=1)

    try:
        worker.run_forever()
    except KeyboardInterrupt:
        pass

    assert queue.deleted == "rh"
