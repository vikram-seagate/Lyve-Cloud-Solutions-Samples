"""Tasks"""
# pylint: disable=no-name-in-module, too-few-public-methods
import datetime as dt
import gc
import os
import time
from functools import partial
from typing import List, Union

import dramatiq
import redis
from dramatiq.brokers.redis import RedisBroker

# from dramatiq.results import Results
from dramatiq.results.backends import RedisBackend
from pydantic import BaseModel

from cstor.s3.core.aws import Account as AccountAWS
from cstor.s3.core.aws import Bucket, ListBucketResult, S3Object
from cstor.s3.core.lyvecloud import Account as AccountLYC
from cstor.s3.rocksdb.main import MigrationCache, MigrationStat
from cstor.s3.secrets import (
    Account,
    AWSCredential,
    SecretCreateResult,
    SecretDeleteResult,
)
from cstor.s3.tasks.middleware import TaskAPI

WEBAPP_HOST: str = os.environ.get("WEBAPP_HOST")
WEBAPP_TOKEN: str = os.environ.get("WEBAPP_TOKEN")
REDIS_HOST: str = os.environ.get("REDIS_HOST", "127.0.0.1")
REDIS_PORT: str = int(os.environ.get("REDIS_PORT", 16379))
REDIS_PASSWD: str = os.environ.get("REDIS_PASSWD", "Test123!")

redis_broker = RedisBroker(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWD,
)
redis_backend = RedisBackend(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWD,
)

redis_client: redis.Redis = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWD,
)
# redis_broker.add_middleware(Results(backend=redis_backend))
# redis_broker.add_middleware(TaskStatusUpdater())
task_api: TaskAPI = TaskAPI(WEBAPP_HOST, WEBAPP_TOKEN)
redis_broker.add_middleware(task_api)
dramatiq.set_broker(redis_broker)


class TaskSecretCreate(BaseModel):
    """Task Secret Create"""

    ConnName: str = ...
    AccessKey: str = ...
    SecretKey: str = ...
    Env: str = "dev"


class TaskSecretDelete(BaseModel):
    """Task Secret Delete"""

    ARN: str = ...


class TaskSecretUpdate(BaseModel):
    """Task Secret Update"""

    PrevARN: str = ...
    ConnName: str = ...
    AccessKey: str = ...
    SecretKey: str = ...
    Env: str = "dev"


class TaskBucketList(BaseModel):
    """Task Bucket List"""

    TaskBucketList: str = ...
    ARN: str = ...
    CloudName: str = ...  # AWS, LYC
    Endpoint: str = ...


class TaskBucketCreateCheck(BaseModel):
    """Task BucketCreateCheck"""

    ARN: str = ...
    Name: str = ...  # Name of the Bucket
    CloudName: str = ...  # AWS, LYC
    Endpoint: str = ...


class TaskBucketListObjects(BaseModel):
    """Task BucketCreateCheck"""

    ARN: str = ...
    MigrationUUID: str = ...
    Name: str = ...  # Name of the Bucket
    CloudName: str = ...  # AWS, LYC
    Endpoint: str = ...
    Prefix: str = None  # Prefix argument of list_objects_v2
    DateBefore: str = None  # %Y%m%d , 20220510
    DateAfter: str = None  # %Y%m%d , 20220510
    SizeGTE: int = None  # Size in mb
    SizeLTE: int = None  # Size in mb


class MigrateBucket(BaseModel):
    """MigrateBucket"""

    ARN: str = ...
    Name: str = ...
    CloudName: str = ...
    Endpoint: str = ...


class TaskBucketMigrate(BaseModel):
    """Task BucketMigrate"""

    MigrationUUID: str = ...
    Src: MigrateBucket = ...
    Dest: MigrateBucket = ...
    DestPrefix: str = ""


class Task(BaseModel):
    """Task"""

    UUID: str = ...
    UserId: str = ...
    Params: Union[
        TaskSecretUpdate,
        TaskSecretCreate,
        TaskSecretDelete,
        TaskBucketList,
    ] = ...


ACCOUNT_MAP: dict = {
    "AWS": AccountAWS,
    "LYC": AccountLYC,
}


def acquire_lock(muuid: str, timeout: int = 10) -> bool:
    """Attempt to acquire the lock"""
    end_time: int = int(time.time()) + timeout
    while time.time() < end_time:
        # Attempt to acquire the lock
        print("Attempt to acquire lock")
        result: int = redis_client.setnx(f"MUUID:{muuid}", "1")
        print(result)
        if result == 1:
            return True
        time.sleep(1)
    return False


def release_lock(muuid: str) -> bool:
    """Attempt to acquire the lock"""
    r_key: str = f"MUUID:{muuid}"
    redis_client.delete(r_key)
    return True


# Time Limit
UNIT_MS: int = 1000
HOUR_MS: int = 60 * 60 * UNIT_MS
MIGRATE_TIME_LIMIT: int = 48 * HOUR_MS


@dramatiq.actor(
    max_retries=1,
    max_age=MIGRATE_TIME_LIMIT,
    time_limit=MIGRATE_TIME_LIMIT,
)
# pylint: disable=too-many-locals
def bucket_migrate(params: dict) -> None:
    """Bucket Migrate"""
    task_params: TaskBucketMigrate = TaskBucketMigrate.parse_obj(params["Params"])
    print("Task Params")
    print(task_params)
    task_access_key: str = os.environ.get("AWS_ACCESS_KEY_ID")
    task_secret_key: str = os.environ.get("AWS_SECRET_ACCESS_KEY")
    task_region: str = os.environ.get("AWS_REGION", "ap-southeast-1")

    account_admin: Account = Account(
        access_key=task_access_key,
        secret_key=task_secret_key,
        region=task_region,
    )

    src_creds: AWSCredential = account_admin.get_secret(task_params.Src.ARN)
    dest_creds: AWSCredential = account_admin.get_secret(task_params.Dest.ARN)

    # Get Src Bucket
    src_endpoint: str = None
    if task_params.Src.Endpoint != "" and task_params.Src.Endpoint is not None:
        src_endpoint = task_params.Src.Endpoint
    src_account: Union[AccountAWS, AccountLYC] = ACCOUNT_MAP[task_params.Src.CloudName](
        access_key=src_creds.AWS_ACCESS_KEY_ID,
        secret_key=src_creds.AWS_SECRET_ACCESS_KEY,
        endpoint_s3=src_endpoint,
    )
    src_bucket: Bucket = src_account.get_bucket(task_params.Src.Name)

    # Get Dest Bucket
    dest_endpoint: str = None
    if task_params.Dest.Endpoint != "" and task_params.Dest.Endpoint is not None:
        dest_endpoint = task_params.Dest.Endpoint

    dest_account: Union[AccountAWS, AccountLYC] = ACCOUNT_MAP[
        task_params.Dest.CloudName
    ](
        access_key=dest_creds.AWS_ACCESS_KEY_ID,
        secret_key=dest_creds.AWS_SECRET_ACCESS_KEY,
        endpoint_s3=dest_endpoint,
    )
    dest_bucket: Bucket = dest_account.get_bucket(task_params.Dest.Name)

    print("All Buckets in order!")

    # Attempt to acquire lock
    acquire_lock(task_params.MigrationUUID)

    cache_stat: MigrationStat = None

    try:
        # Get Work
        cache: MigrationCache = MigrationCache(
            user_id=params["UserId"],
            migration_uuid=task_params.MigrationUUID,
            is_readonly=False,
        )
        migrate_payload: dict = cache.get_work()
        print("Workload")
        print(migrate_payload)
        # cache.close()
        cache_stat = cache.get_stats()
        task_api.update_progress_stat(
            params["UUID"],
            cache_stat.json(),
        )

        del cache
        gc.collect()
    finally:
        # Always release the lock
        release_lock(task_params.MigrationUUID)

    if len(migrate_payload.keys()) == 0:
        # Nothing to do
        task_status: int = 1 # Pending
        if cache_stat.ProgressSize == 0:
            task_status = 2 # COMPLETED
        task_api.update_progress_stat(
            params["UUID"],
            cache_stat.json(),
            task_status=task_status,
        )
        return {}

    result: dict = src_bucket.migrate(
        dest_bucket,
        migrate_payload,
        task_params.DestPrefix,
    )
    print("Result")
    print(result)
    # Update Rocksdb
    acquire_lock(task_params.MigrationUUID)

    try:
        cache: MigrationCache = MigrationCache(
            user_id=params["UserId"],
            migration_uuid=task_params.MigrationUUID,
            is_readonly=False,
        )
        cache.update_work(result)
        cache_stat: MigrationStat = cache.get_stats()
        task_api.update_progress_stat(
            params["UUID"],
            cache_stat.json(),
        )
        del cache
        gc.collect()
    finally:
        # Always release the lock
        release_lock(task_params.MigrationUUID)

    print("Re-firing")
    bucket_migrate.send(params)
    return {}


@dramatiq.actor(max_retries=2)
# pylint: disable=too-many-locals
def bucket_scan(params: dict) -> None:
    """List objects v2
    :param params: A dict of BucketListObjects

    :return: The result of ListObjects
    """
    task_params: TaskBucketListObjects = TaskBucketListObjects(**params["Params"])

    task_access_key: str = os.environ.get("AWS_ACCESS_KEY_ID")
    task_secret_key: str = os.environ.get("AWS_SECRET_ACCESS_KEY")
    task_region: str = os.environ.get("AWS_REGION", "ap-southeast-1")

    account_admin: Account = Account(
        access_key=task_access_key,
        secret_key=task_secret_key,
        region=task_region,
    )

    creds: AWSCredential = account_admin.get_secret(task_params.ARN)

    endpoint_s3: str = None

    if task_params.Endpoint != "" and task_params.Endpoint is not None:
        endpoint_s3 = task_params.Endpoint

    account_s3: Union[AccountAWS, AccountLYC] = ACCOUNT_MAP[task_params.CloudName](
        access_key=creds.AWS_ACCESS_KEY_ID,
        secret_key=creds.AWS_SECRET_ACCESS_KEY,
        endpoint_s3=endpoint_s3,
    )

    bucket: Bucket = account_s3.get_bucket(task_params.Name)

    # Each Bucket Page has up to 1000 items
    bucket_pages: any = bucket.list_objects(
        prefix=task_params.Prefix,
    )

    dt_before: dt.datetime = None
    if task_params.DateBefore is not None:
        dt_before = dt.datetime.strptime(task_params.DateBefore, "%Y%m%d")

    dt_after: dt.datetime = None
    if task_params.DateBefore is not None:
        dt_after = dt.datetime.strptime(task_params.DateAfter, "%Y%m%d")

    size_gte: int = None
    if task_params.SizeGTE is not None:
        size_gte = task_params.SizeGTE

    size_lte: int = None
    if task_params.SizeLTE is not None:
        size_lte = task_params.SizeLTE

    # Assemble Filter
    def filter_s3_item(s3_item: S3Object) -> bool:
        """Filter for each item"""
        if dt_before is not None and s3_item.LastModified > dt_before:
            return False
        if dt_after is not None and s3_item.LastModified < dt_after:
            return False
        item_size: int = int(s3_item.Size / (1024 * 1024))
        if size_gte is not None and item_size < size_gte:
            return False
        if size_lte is not None and item_size > size_lte:
            return False
        return True

    # results: List[S3Object] = list(filter(filter_s3_item, bucket_objects))
    results: List[S3Object] = []

    scan_result: dict = {
        "total_count": 0,
        "total_size": 0,
    }

    def migrate_result_map(scan_result: dict, s3_item: S3Object) -> S3Object:
        """Add to histogram"""
        scan_result["total_count"] += 1
        scan_result["total_size"] += s3_item.Size

        return s3_item

    mapper: any = partial(migrate_result_map, scan_result)

    for bucket_page in bucket_pages:
        bucket_filtered = list(
            map(
                mapper,
                filter(filter_s3_item, bucket_page),
            ),
        )
        results += bucket_filtered

    # Save to RocksDB
    cache: MigrationCache = MigrationCache(
        user_id=params["UserId"],
        migration_uuid=task_params.MigrationUUID,
        is_readonly=False,
    )

    cache.save_scan(results)

    return scan_result


@dramatiq.actor(max_retries=1)
def bucket_create_check(params: dict) -> dict:
    """Check that the bucket is valid

    :param params: A dict of BucketCreateCheck

    :return:
    """
    task_params: TaskBucketCreateCheck = TaskBucketCreateCheck(**params["Params"])
    # uuid: str = params["UUID"]
    # user_id: str = params["UserId"]
    #
    task_access_key: str = os.environ.get("AWS_ACCESS_KEY_ID")
    task_secret_key: str = os.environ.get("AWS_SECRET_ACCESS_KEY")
    task_region: str = os.environ.get("AWS_REGION", "ap-southeast-1")
    #
    account_admin: Account = Account(
        access_key=task_access_key,
        secret_key=task_secret_key,
        region=task_region,
    )
    creds: AWSCredential = account_admin.get_secret(task_params.ARN)
    endpoint_s3: str = None

    if task_params.Endpoint != "" and task_params.Endpoint is not None:
        endpoint_s3 = task_params.Endpoint

    account_s3: Union[AccountAWS, AccountLYC] = ACCOUNT_MAP[task_params.CloudName](
        access_key=creds.AWS_ACCESS_KEY_ID,
        secret_key=creds.AWS_SECRET_ACCESS_KEY,
        endpoint_s3=endpoint_s3,
    )

    # Will call head_bucket for verification
    bucket: Bucket = account_s3.get_bucket(task_params.Name)

    result: dict = {
        "Name": task_params.Name,
        "Region": bucket.region,
    }

    # print(f"Result: {result}")

    return result


@dramatiq.actor(max_retries=2)
def bucket_list(params: dict) -> None:
    """List the bucket contents

    :param params: A dict of BucketListCreate

    :return: The result of ListBucketResult
    """
    task_params: TaskBucketList = TaskBucketList(**params["Params"])
    # uuid: str = params["UUID"]
    # user_id: str = params["UserId"]

    task_access_key: str = os.environ.get("AWS_ACCESS_KEY_ID")
    task_secret_key: str = os.environ.get("AWS_SECRET_ACCESS_KEY")
    task_region: str = os.environ.get("AWS_REGION", "ap-southeast-1")

    account_admin: Account = Account(
        access_key=task_access_key,
        secret_key=task_secret_key,
        region=task_region,
    )

    creds: AWSCredential = account_admin.get_secret(task_params.ARN)

    endpoint_s3: str = None

    if task_params.Endpoint != "" and task_params.Endpoint is not None:
        endpoint_s3 = task_params.Endpoint

    account_s3: Union[AccountAWS, AccountLYC] = ACCOUNT_MAP[task_params.CloudName](
        access_key=creds.AWS_ACCESS_KEY_ID,
        secret_key=creds.AWS_SECRET_ACCESS_KEY,
        endpoint_s3=endpoint_s3,
    )

    result: ListBucketResult = account_s3.list_buckets()
    # print(result)

    return result.json()


@dramatiq.actor(max_retries=1)
def secret_create(params: dict) -> SecretCreateResult:
    """Creates a secret on AWS Secrets Manager

    :param params: A dict of TaskSecretCreate

    :return: The result of SecretCreate
    """
    task: Task = Task.parse_obj(params)

    task_access_key: str = os.environ.get("AWS_ACCESS_KEY_ID")
    task_secret_key: str = os.environ.get("AWS_SECRET_ACCESS_KEY")
    task_region: str = os.environ.get("AWS_REGION", "ap-southeast-1")

    account: Account = Account(
        access_key=task_access_key,
        secret_key=task_secret_key,
        region=task_region,
    )
    cred: AWSCredential = AWSCredential(
        AWS_ACCESS_KEY_ID=task.Params.AccessKey,
        AWS_SECRET_ACCESS_KEY=task.Params.SecretKey,
    )

    result: SecretCreateResult = account.create_secret(
        task.UserId,
        task.Params.ConnName,
        cred,
        task.Params.Env,
    )

    return result.dict()


@dramatiq.actor(max_retries=1)
def secret_delete(params: dict) -> SecretCreateResult:
    """Deletes a secret on AWS Secrets Manager

    :param params: A dict of TaskSecretDelete

    :return: The result of SecretDelete
    """
    task: Task = Task.parse_obj(params)

    task_access_key: str = os.environ.get("AWS_ACCESS_KEY_ID")
    task_secret_key: str = os.environ.get("AWS_SECRET_ACCESS_KEY")
    task_region: str = os.environ.get("AWS_REGION", "ap-southeast-1")

    account: Account = Account(
        access_key=task_access_key,
        secret_key=task_secret_key,
        region=task_region,
    )

    result: SecretDeleteResult = account.delete_secret(
        task.Params.ARN,
    )

    return result.dict()


@dramatiq.actor(max_retries=1)
def secret_update(params: dict) -> SecretCreateResult:
    """Deletes and recreates a secret on AWS Secrets Manager

    :param params: A dict of TaskSecretUpdate

    :return: The result of SecretCreate
    """
    task: Task = Task.parse_obj(params)

    task_access_key: str = os.environ.get("AWS_ACCESS_KEY_ID")
    task_secret_key: str = os.environ.get("AWS_SECRET_ACCESS_KEY")
    task_region: str = os.environ.get("AWS_REGION", "ap-southeast-1")

    account: Account = Account(
        access_key=task_access_key,
        secret_key=task_secret_key,
        region=task_region,
    )

    account.delete_secret(
        task.Params.PrevARN,
    )

    cred: AWSCredential = AWSCredential(
        AWS_ACCESS_KEY_ID=task.Params.AccessKey,
        AWS_SECRET_ACCESS_KEY=task.Params.SecretKey,
    )

    result: SecretCreateResult = account.create_secret(
        task.UserId,
        task.Params.ConnName,
        cred,
        task.Params.Env,
    )

    update_res: dict = {
        **result.dict(),
        "PrevARN": task.Params.PrevARN,
    }

    return update_res
