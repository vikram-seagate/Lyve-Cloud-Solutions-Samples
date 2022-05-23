"""Task Handlers"""
import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Task, CloudProvider, Bucket, Migration


channel_layer = get_channel_layer()


def handle_secret_create(req_args: dict, req_data: dict):
    """Handle Secret Create"""

    task_status: int = int(req_data["status"])
    if task_status == Task.TaskStatus.COMPLETED:
        task_data: dict = json.loads(req_data["result_ok"])
        # Update AWS ARN for CloudProvider
        conn_name: str = req_args["ConnName"]
        connection: CloudProvider = CloudProvider.objects.get(
            #name=conn_name,
            cloud_cred_uuid=conn_name,
        )
        connection.cloud_cred_arn = task_data["ARN"]
        connection.save()
    elif task_status == Task.TaskStatus.FAILED:
        conn_name: str = req_args["ConnName"]
        connection: CloudProvider = CloudProvider.objects.get(
            #name=conn_name,
            cloud_cred_uuid=conn_name,
        )
        connection.cloud_cred_valid = False
        connection.save()

def handle_secret_delete(req_args: dict, req_data: dict):
    """Handle Secret Delete"""


def handle_secret_update(req_args: dict, req_data: dict):
    """Handle Secret Update"""

    task_status: int = int(req_data["status"])
    if task_status == Task.TaskStatus.COMPLETED:
        task_data: dict = json.loads(req_data["result_ok"])
        # Update AWS ARN for CloudProvider
        #conn_name: str = req_args["ConnName"]
        prev_arn: str = task_data["PrevARN"]
        connection: CloudProvider = CloudProvider.objects.get(
            #name=conn_name,
            cloud_cred_arn=prev_arn,
        )
        connection.cloud_cred_arn = task_data["ARN"]
        connection.save()
    elif task_status == Task.TaskStatus.FAILED:
        conn_name: str = req_args["ConnName"]
        connection: CloudProvider = CloudProvider.objects.get(
            #name=conn_name,
            cloud_cred_uuid=conn_name,
        )
        connection.cloud_cred_valid = False
        connection.save()


def handle_bucket_list(req_args: dict, req_data: dict):
    """Handle Bucket List"""
    task_status: int = int(req_data["status"])
    if task_status == Task.TaskStatus.COMPLETED:
        task_data: dict = json.loads(req_data["result_ok"])
        # Update AWS ARN for CloudProvider
        connection: CloudProvider = CloudProvider.objects.get(
            cloud_cred_arn=req_args["ARN"],
        )
        conn_id: int = connection.id
        user_id: int = connection.created_by.id
        user_channel: str = f"user_{user_id}"
        async_to_sync(channel_layer.group_send)(user_channel, {
            "type": "notify.user",
            "data": {
                "mesg_type": "respListBuckets",
                "data": task_data,
                "status": "success",
            },
        })
    elif task_status == Task.TaskStatus.FAILED:
        pass


def handle_bucket_create_check(req_args: dict, req_data: dict):
    """Handle Bucket Create Check"""
    task_status: int = int(req_data["status"])
    if task_status == Task.TaskStatus.COMPLETED:
        task_data: dict = json.loads(req_data["result_ok"])
        # Update AWS ARN for CloudProvider
        connection: CloudProvider = CloudProvider.objects.get(
            cloud_cred_arn=req_args["ARN"],
        )
        bucket_name: str = task_data["Name"]
        bucket_region: str = task_data.get("Region", "")

        bucket: Bucket = Bucket.objects.get(
            name=bucket_name, 
            cloud_provider=connection,
        )

        bucket.is_valid = True
        if bucket_region != "":
            bucket.cloud_region = bucket_region

        bucket.save()
    elif task_status == Task.TaskStatus.FAILED:
        pass


def handle_bucket_scan(req_args: dict, req_data: dict):
    """Handle Bucket Scan"""
    task_status: int = int(req_data["status"])
    if task_status == Task.TaskStatus.COMPLETED:
        task_data: dict = json.loads(req_data["result_ok"])
        migration_uuid: str = req_args["MigrationUUID"]
        migration: Migration = Migration.objects.get(
            uuid=migration_uuid,
        )
        migration.status = Migration.MigrationStatus.PAUSED

        migration.total_size = task_data["total_size"]
        migration.total_count = task_data["total_count"]
        migration.save()
        user_id: int = migration.created_by.id
        user_channel: str = f"user_{user_id}"
        progress_data: dict = {
            "id": migration.id,
            "progress": {
                "status": 2,  # PAUSED
                "total_size": task_data["total_size"],
                "total_count": task_data["total_count"],
            },
        }
        async_to_sync(channel_layer.group_send)(user_channel, {
            "type": "notify.user",
            "data": {
                "mesg_type": "migrationProgress",
                "data": progress_data,
                "status": "progress",
            },
        })
    elif task_status == Task.TaskStatus.FAILED:
        pass


def handle_bucket_migrate(req_args: dict, req_data: dict):
    """Handle Bucket Scan"""
    task_status: int = int(req_data["status"])
    if task_status == Task.TaskStatus.PENDING:
        task_data: dict = json.loads(req_data["result_ok"])
        migration_uuid: str = req_args["MigrationUUID"]
        migration: Migration = Migration.objects.get(
            uuid=migration_uuid,
        )
        #if migration.status == Migration.MigrationStatus.RUNNING:
        migration.progress_size = task_data["ProgressSize"]
        migration.progress_count = task_data["ProgressCount"]
        migration.success_size = task_data["SuccessSize"]
        migration.success_count = task_data["SuccessCount"]
        migration.fail_size = task_data["FailSize"]
        migration.fail_count = task_data["FailCount"]
        migration.save()
        user_id: int = migration.created_by.id
        user_channel: str = f"user_{user_id}"
        progress_data: dict = {
            "id": migration.id,
            "progress": {
                "progress_size": task_data["ProgressSize"],
                "progress_count": task_data["ProgressCount"],
                "success_size": task_data["SuccessSize"],
                "success_count": task_data["SuccessCount"],
                "fail_size": task_data["FailSize"],
                "fail_count": task_data["FailCount"],
            },
        }
        async_to_sync(channel_layer.group_send)(user_channel, {
            "type": "notify.user",
            "data": {
                "mesg_type": "migrationProgress",
                "data": progress_data,
                "status": "progress",
            },
        })
    elif task_status == Task.TaskStatus.COMPLETED:
        task_data: dict = json.loads(req_data["result_ok"])
        migration_uuid: str = req_args["MigrationUUID"]
        migration: Migration = Migration.objects.get(
            uuid=migration_uuid,
        )
        migration.progress_size = task_data["ProgressSize"]
        migration.progress_count = task_data["ProgressCount"]
        migration.success_size = task_data["SuccessSize"]
        migration.success_count = task_data["SuccessCount"]
        migration.fail_size = task_data["FailSize"]
        migration.fail_count = task_data["FailCount"]
        prog_status: int = 2  # PAUSED
        if migration.status != Migration.MigrationStatus.PAUSED:
            prog_status = 3  # COMPLETED
            migration.status = Migration.MigrationStatus.COMPLETED
            migration.save()
        #
        user_id: int = migration.created_by.id
        user_channel: str = f"user_{user_id}"
        progress_data: dict = {
            "id": migration.id,
            "progress": {
                "status": prog_status,
                "progress_size": task_data["ProgressSize"],
                "progress_count": task_data["ProgressCount"],
                "success_size": task_data["SuccessSize"],
                "success_count": task_data["SuccessCount"],
                "fail_size": task_data["FailSize"],
                "fail_count": task_data["FailCount"],
            },
        }
        async_to_sync(channel_layer.group_send)(user_channel, {
            "type": "notify.user",
            "data": {
                "mesg_type": "migrationProgress",
                "data": progress_data,
                "status": "progress",
            },
        })




TASK_HANDLERS = {
    "TaskSecretCreate": handle_secret_create,
    "TaskSecretDelete": handle_secret_delete,
    "TaskSecretUpdate": handle_secret_update,
    "TaskBucketList": handle_bucket_list,
    "TaskBucketCreateCheck": handle_bucket_create_check,
    "TaskBucketScan": handle_bucket_scan,
    "TaskBucketMigrate": handle_bucket_migrate,
}

def handle_task(task_uuid: str, req_data: dict):
    """Handle Task"""
    task: Task = Task.objects.get(uuid=task_uuid)
    req_args: dict = json.loads(task.request_args)

    TASK_HANDLERS[task.category](req_args, req_data)
