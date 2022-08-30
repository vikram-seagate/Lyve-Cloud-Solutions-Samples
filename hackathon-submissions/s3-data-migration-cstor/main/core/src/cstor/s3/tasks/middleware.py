"""Tasks Middleware"""
import json
from typing import Any

import dramatiq
from dramatiq.middleware.middleware import SkipMessage
import httpx


def get_max_retries(broker: Any, message: Any) -> int:
    """Get max retries for this message"""
    actor: Any = broker.get_actor(message.actor_name)
    max_retries: int = message.options.get("max_retries") or actor.options.get(
        "max_retries"
    )
    return max_retries


class TaskAPI(dramatiq.Middleware):
    """TaskAPI

    When a message has been processed, update the corresponding Task on Django
    """

    def __init__(self, endpoint: str, token: str):
        """CSTOR"""
        self.endpoint = endpoint
        self.token = token

    def _check_task(self, task_uuid: str):
        """Checks a task by uuid on Django
        :param task_uuid: The uuid of the task in Django
        """
        headers: dict = {
            "Authorization": f"Token {self.token}",
        }
        resource_url: str = f"/api/v1/cloud/tasks/{task_uuid}/"
        with httpx.Client(base_url=self.endpoint, headers=headers) as client:
            resp = client.get(
                resource_url,
            )
            if resp.status_code == 200:
                print(resp.json())

    def _update_task(
        self,
        task_uuid: str,
        task_data: dict,
    ):
        """Updates a task by uuid on Django
        :param task_uuid: The uuid of the task in Django
        :param retries: The number of retries
        :param status: The status of the task
        :param result: JSON encoded string of the result
        """
        headers: dict = {
            "Authorization": f"Token {self.token}",
        }
        resource_url: str = f"/api/v1/cloud/tasks/{task_uuid}/"
        with httpx.Client(base_url=self.endpoint, headers=headers) as client:
            resp: Any = client.patch(
                resource_url,
                data=task_data,
            )
            if resp.status_code == 200:
                print(resp.json())
            else:
                print(f"Warning got {resp.status_code} when updating task {task_uuid}")

    def update_progress_stat(
        self,
        task_uuid: str,
        result_data: any,
        task_status: int = 1,  # Pending
    ):
        """Update Progress of the Task"""
        task_data: dict = {
            "status": task_status,  # Pending
            "result_ok": result_data,
        }
        print("progress task_data")
        print(task_data)
        self._update_task(task_uuid, task_data)

    def before_process_message(
        self,
        broker: Any,
        message: Any,
    ):
        """Check if the migration is paused or task completed"""
        print("Before Process Message")
        msgdata: dict = message.asdict()
        task_args: dict = msgdata["args"][0]
        task_uuid: str = task_args["UUID"]
        headers: dict = {
            "Authorization": f"Token {self.token}",
        }
        resource_url: str = f"/api/v1/cloud/tasks/{task_uuid}/"
        with httpx.Client(base_url=self.endpoint, headers=headers) as client:
            resp: Any = client.get(
                resource_url,
            )
            if resp.status_code == 200:
                print("Before Message Task Info")
                #print(resp.json())
                task_info = resp.json()
                print(task_info)
                if (
                    task_info["category"] == "TaskBucketMigrate" and
                    task_info["status"] == 2
                ):
                    # Paused or alr succeeded
                    print(f"Skipping: {task_uuid}")
                    raise SkipMessage()

    def after_process_message(
        self,
        broker: Any,
        message: Any,
        *,
        result: Any = None,
        exception: Any = None,
    ):
        msgdata: dict = message.asdict()
        task_args: dict = msgdata["args"][0]
        task_uuid: str = task_args["UUID"]
        retries: int = message.options.get("retries", 0)
        max_retries: int = get_max_retries(broker, message)
        task_status: int = 2  # COMPLETED

        if exception:
            if retries < max_retries:
                task_status = 4  # RETRYING
            else:
                task_status = 3  # FAILED
            task_data: dict = {
                "retries": retries,
                "status": task_status,
                "result_error": exception,
            }
            self._update_task(task_uuid, task_data)
        elif result:
            result_ok: str = (
                json.dumps(result) if not isinstance(result, str) else result
            )
            task_data: dict = {
                "retries": retries,
                "status": task_status,
                "result_ok": result_ok,
            }
            print("task_data")
            print(task_data)
            self._update_task(task_uuid, task_data)
