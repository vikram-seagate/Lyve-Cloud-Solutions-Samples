"""Django:Cloud Views"""
# pylint: disable=no-member
from uuid import uuid4 as uuid
from copy import deepcopy
import json
from django.shortcuts import render

from .models import (
    CloudProvider,
    Task, 
    Bucket,
    Migration,
)

from .serializers import (
    CloudProviderListSerializer,
    TaskSerializer,
    BucketListSerializer,
    MigrationListSerializer,
)
from rest_framework import generics, permissions
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .permissions import IsOwner
from cstor.s3.tasks import secret_create, bucket_list, bucket_migrate
from cstor.s3.tasks.main import (
    secret_delete,
    secret_update,
    bucket_create_check,
    bucket_scan,
)
from .task_handlers import handle_task


channel_layer = get_channel_layer()


class ConnList(generics.ListCreateAPIView):
    def get_queryset(self):
        """Filter for owners"""
        return CloudProvider.objects.filter(created_by=self.request.user)

    serializer_class = CloudProviderListSerializer

    def perform_create(self, serializer):
        """ Save the created_by as the request.user """
        reqdata: dict = self.request.data
        access_key: str = reqdata["cloud_access_key"]
        secret_key: str = reqdata["cloud_secret_key"]

        #conn_name: str = reqdata["name"].replace(" ", "-")
        #conn_name: str = str(uuid())
        cred_uuid: uuid = uuid()

        task_params_save = {
            "AccessKey": access_key,
            "ConnName": str(cred_uuid),
            "Env": "dev",
        }

        # Create task to save to AWS Secrets Manager
        task: Task = Task(
            category="TaskSecretCreate",
            request_args=json.dumps(task_params_save),
            created_by=self.request.user,
        )
        task.save()
        task_params: dict = {
            **task_params_save,
            "SecretKey": secret_key,
        }
        task_mesg: dict = {
            "UUID": str(task.uuid),
            "UserId": task.created_by.id,
            "Params": task_params,
        }
        mesg: any = secret_create.send(task_mesg)

        # END
        serializer.save(
            cloud_cred_uuid=cred_uuid,
            created_by=self.request.user,
        )


class ConnDetail(generics.RetrieveUpdateDestroyAPIView):
    def get_queryset(self):
        """Filter for owners"""
        return CloudProvider.objects.filter(created_by=self.request.user)
    serializer_class = CloudProviderListSerializer
    permission_classes = (IsOwner,)

    def perform_update(self, serializer):
        """Before updating connection"""
        req_data: dict = self.request.data
        # Do not allow updates to cloud_cred_valid
        if req_data.get("cloud_cred_valid"):
            del req_data["cloud_cred_valid"]

        # Get List of Buckets
        if req_data.get("action"):
            action: str = req_data.get("action")
            if action == "list_buckets":
                pk: int = self.kwargs["pk"]
                conn: CloudProvider = CloudProvider.objects.get(pk=pk)
                task_params: dict = {
                    "TaskBucketList": "task",
                    "ARN": conn.cloud_cred_arn,
                    "CloudName": conn.cloud_name,
                    "Endpoint": conn.cloud_endpoint,
                }
                task: Task = Task(
                    category="TaskBucketList",
                    request_args=json.dumps(task_params),
                    created_by=self.request.user,
                )
                task.save()
                task_mesg: dict = {
                    "UUID": str(task.uuid),
                    "UserId": task.created_by.id,
                    "Params": task_params,
                }
                mesg: any = bucket_list.send(task_mesg)
                return

        # Update Secret Creds
        if req_data.get("cloud_access_key") and req_data.get("cloud_secret_key"):
            pk: int = self.kwargs["pk"]
            conn: CloudProvider = CloudProvider.objects.get(pk=pk)
            prev_arn: str = conn.cloud_cred_arn
            #conn_name: str = conn.name
            #conn_name: str = str(uuid())
            cred_uuid_new: uuid = uuid()
            access_key: str = req_data.get("cloud_access_key")
            secret_key: str = req_data.get("cloud_secret_key")
            # Create an update task
            task_params_save = {
                "PrevARN": prev_arn,
                "AccessKey": access_key,
                "ConnName": str(cred_uuid_new),
                "Env": "dev",
            }
            task: Task = Task(
                category="TaskSecretUpdate",
                request_args=json.dumps(task_params_save),
                created_by=self.request.user,
            )
            task.save()
            task_params: dict = {
                **task_params_save,
                "SecretKey": secret_key,
            }
            task_mesg: dict = {
                "UUID": str(task.uuid),
                "UserId": task.created_by.id,
                "Params": task_params,
            }
            mesg: any = secret_update.send(task_mesg)

        #
        # END
        serializer.save(
            cloud_cred_uuid=cred_uuid_new,
        )

    def perform_destroy(self, instance):
        """Before destroy delete the AWS Secret"""
        cred_arn: str = instance.cloud_cred_arn
        task_params: dict = {
            "ARN": cred_arn,
        }
        # Create task to save to AWS Secrets Manager
        task: Task = Task(
            category="TaskSecretDelete",
            request_args=json.dumps(task_params),
            created_by=self.request.user,
        )
        task.save()
        task_mesg: dict = {
            "UUID": str(task.uuid),
            "UserId": task.created_by.id,
            "Params": task_params,
        }
        mesg: any = secret_delete.send(task_mesg)

        # END
        instance.delete()


class TaskDetail(generics.RetrieveUpdateDestroyAPIView):
    def get_queryset(self):
        """No filters"""
        return Task.objects.all()
    serializer_class = TaskSerializer
    # permission_classes = (IsOwner,)
    lookup_field = "uuid"

    def perform_update(self, serializer):
        """Intercept task update"""
        req_data: dict = self.request.data
        task_uuid: str = self.kwargs["uuid"]
        # Handle Task Update
        handle_task(task_uuid, req_data)

        # current state
        current_task: Task = Task.objects.get(uuid=task_uuid)
        if current_task.status != Task.TaskStatus.COMPLETED:
            # Not paused or done
            # END
            serializer.save()



class BucketList(generics.ListCreateAPIView):
    def get_queryset(self):
        """Filter for owners"""
        return Bucket.objects.filter(created_by=self.request.user)

    serializer_class = BucketListSerializer

    def perform_create(self, serializer):
        """ Save the created_by as the request.user """
        reqdata: dict = self.request.data

        conn_id: int = int(reqdata["cloud_provider_id"])

        del reqdata["cloud_provider_id"]

        cloud_provider: CloudProvider = CloudProvider.objects.get(pk=conn_id)
        cred_arn: str = cloud_provider.cloud_cred_arn
        cloud_name: str = cloud_provider.cloud_name
        cloud_endpoint: str = cloud_provider.cloud_endpoint

        task_params = {
            "ARN": cred_arn,
            "Name": reqdata["name"],
            "CloudName": cloud_name,
            "Endpoint": cloud_endpoint,
        }

        # Create task to scan the bucket based on filters
        task: Task = Task(
            category="TaskBucketCreateCheck",
            request_args=json.dumps(task_params),
            created_by=self.request.user,
        )
        task.save()
        task_mesg: dict = {
            "UUID": str(task.uuid),
            "UserId": task.created_by.id,
            "Params": task_params,
        }
        mesg: any = bucket_create_check.send(task_mesg)

        # END
        serializer.save(
            cloud_provider=cloud_provider,
            created_by=self.request.user,
        )


class BucketDetail(generics.RetrieveUpdateDestroyAPIView):
    def get_queryset(self):
        """Filter for owners"""
        return Bucket.objects.filter(created_by=self.request.user)
    serializer_class = BucketListSerializer
    permission_classes = (IsOwner,)


class MigrationList(generics.ListCreateAPIView):
    def get_queryset(self):
        """Filter for owners"""
        return Migration.objects.filter(created_by=self.request.user)

    serializer_class = MigrationListSerializer

    def perform_create(self, serializer):
        """ Save the created_by as the request.user """
        reqdata: dict = self.request.data

        src_bucket_id: int = int(reqdata["src_bucket_id"])
        dest_bucket_id: int = int(reqdata["dest_bucket_id"])

        del reqdata["src_bucket_id"]
        del reqdata["dest_bucket_id"]

        #cloud_provider: CloudProvider = CloudProvider.objects.get(pk=conn_id)
        src_bucket: Bucket = Bucket.objects.get(pk=src_bucket_id)
        dest_bucket: Bucket = Bucket.objects.get(pk=dest_bucket_id)
        src_name: str = src_bucket.name
        src_cred_arn: str = src_bucket.cloud_provider.cloud_cred_arn
        src_cloud_name: str = src_bucket.cloud_provider.cloud_name
        src_cloud_endpoint: str = src_bucket.cloud_provider.cloud_endpoint

        migration_uuid: str = str(uuid())

        task_params = {
            "ARN": src_cred_arn,
            "MigrationUUID": migration_uuid,
            "Name": src_name,
            "CloudName": src_cloud_name,
            "Endpoint": src_cloud_endpoint,
            "Prefix": reqdata["src_prefix"],
            "DateBefore": reqdata.get("DateBefore"),
            "DateAfter": reqdata.get("DateAfter"),
            "SizeGTE": reqdata.get("filter_size_gte"),
            "SizeLTE": reqdata.get("filter_size_lte"),
        }

        # Create task to scan the bucket based on filters
        task: Task = Task(
            category="TaskBucketScan",
            request_args=json.dumps(task_params),
            created_by=self.request.user,
        )
        task.save()
        task_mesg: dict = {
            "UUID": str(task.uuid),
            "UserId": task.created_by.id,
            "Params": task_params,
        }
        mesg: any = bucket_scan.send(task_mesg)

        # END
        serializer.save(
            uuid=migration_uuid,
            src_bucket=src_bucket,
            dest_bucket=dest_bucket,
            created_by=self.request.user,
        )


class MigrationDetail(generics.RetrieveUpdateDestroyAPIView):
    def get_queryset(self):
        """Filter for owners"""
        return Migration.objects.filter(created_by=self.request.user)
    serializer_class = MigrationListSerializer
    permission_classes = (IsOwner,)

    def perform_update(self, serializer):
        """Before updating connection"""
        req_data: dict = self.request.data

        # Get List of Buckets
        if req_data.get("action"):
            action: str = req_data.get("action")
            if action == "migration_pause":
                migration_id: int = self.kwargs["pk"]
                # conn: CloudProvider = CloudProvider.objects.get(pk=pk)
                migration: Migration = Migration.objects.get(pk=migration_id)
                migration.status = Migration.MigrationStatus.PAUSED
                migration_uuid: str = str(migration.uuid)
                #print(f"We want {migration_uuid}")
                migration.save()
                progress_data: dict = {
                    "id": migration.id,
                    "progress": {
                        "status": 2,  # PAUSED
                    },
                }
                user_id: int = migration.created_by.id
                user_channel: str = f"user_{user_id}"
                async_to_sync(channel_layer.group_send)(user_channel, {
                    "type": "notify.user",
                    "data": {
                        "mesg_type": "migrationProgress",
                        "data": progress_data,
                        "status": "progress",
                    },
                })
                # Find the task that has MigrationUUID = this one and set it to
                # COMPLETED
                # CandidateTasks
                migration_tasks: any = Task.objects.filter(
                    category="TaskBucketMigrate",
                    status=Task.TaskStatus.PENDING,
                )
                #print(f"Found migrate tasks running: {len(migration_tasks)}")
                for migrate_task in migration_tasks:
                    #print(migrate_task)
                    req_args: dict = json.loads(migrate_task.request_args)
                    #print(req_args)
                    #print(req_args["MigrationUUID"])
                    if req_args["MigrationUUID"] == migration_uuid:
                        #print("Updating task status...")
                        migrate_task.status = Task.TaskStatus.COMPLETED
                        migrate_task.save()


            if action == "migration_start":
                migration_id: int = self.kwargs["pk"]
                # conn: CloudProvider = CloudProvider.objects.get(pk=pk)
                migration: Migration = Migration.objects.get(pk=migration_id)
                if migration.status == Migration.MigrationStatus.PAUSED:
                    src_bucket: Bucket = migration.src_bucket
                    src_provider: CloudProvider = src_bucket.cloud_provider

                    dest_bucket: Bucket = migration.dest_bucket
                    dest_provider: CloudProvider = dest_bucket.cloud_provider

                    task_params: dict = {
                        "MigrationUUID": str(migration.uuid),
                        "Src": {
                            "ARN": src_provider.cloud_cred_arn,
                            "Name": src_bucket.name,
                            "CloudName": src_provider.cloud_name,
                            "Endpoint": src_provider.cloud_endpoint,
                        },
                        "Dest": {
                            "ARN": dest_provider.cloud_cred_arn,
                            "Name": dest_bucket.name,
                            "CloudName": dest_provider.cloud_name,
                            "Endpoint": dest_provider.cloud_endpoint,
                        },
                        "DestPrefix": migration.dest_prefix,
                    }
                    progress_data: dict = {
                        "id": migration.id,
                        "progress": {
                            "status": 1,  # RUNNING
                        },
                    }
                    user_id: int = migration.created_by.id
                    user_channel: str = f"user_{user_id}"
                    async_to_sync(channel_layer.group_send)(user_channel, {
                        "type": "notify.user",
                        "data": {
                            "mesg_type": "migrationProgress",
                            "data": progress_data,
                            "status": "progress",
                        },
                    })
                    print("Migrate Task Params")
                    print(task_params)
                    task: Task = Task(
                        category="TaskBucketMigrate",
                        request_args=json.dumps(task_params),
                        created_by=self.request.user,
                    )
                    task.save()
                    task_mesg: dict = {
                        "UUID": str(task.uuid),
                        "UserId": task.created_by.id,
                        "Params": task_params,
                    }
                    # Hardcode 2 workers for now
                    bucket_migrate.send(task_mesg)
                    bucket_migrate.send(task_mesg)
                    # End hardcode
                    migration.status = Migration.MigrationStatus.RUNNING
                    migration.save()
                    return
