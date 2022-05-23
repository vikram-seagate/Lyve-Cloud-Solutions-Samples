"""Test Dramatiq"""
import os
import shutil
import dramatiq
import time
import pytest
from cstor.s3.tasks import (
    secret_create,
    bucket_scan,
    bucket_migrate,
)
from cstor.s3.tasks.middleware import TaskAPI
from cstor.s3.rocksdb.main import MigrationCache, MigrationItem


@pytest.mark.skip
def test_task_secret_create():
    """Test Task Secret Create"""
    mesg: any = secret_create.send({
        "UUID": "abc-12345",
        "UserId": "2",
        "Params": {
            "ConnName": "AWSConn4",
            "AccessKey": "xxx",
            "SecretKey" : "yyy",
            "Env": "dev",
        },
    })
    mesg_id: str = mesg.message_id
    mesg_timestamp: str = mesg.message_timestamp

    #print(mesg_id)
    #print(mesg_timestamp)


@pytest.mark.skip
def test_middleware_check_task():
    """Test Middleware TaskAPI _check_task"""

    task_uuid: str = "3fa6d0d6-b3e1-4687-bd6c-a9559235bcab"
    api: TaskAPI = TaskAPI(
        endpoint="http://128.199.125.233:8000",
        token="9fe5a7b70296be70a0c62b50ad30ca38dd763015"
    )

    api._check_task(task_uuid)
    # Sample Return
    """
     {
         'id': 1,
         'uuid': '3fa6d0d6-b3e1-4687-bd6c-a9559235bcab',
         'category': 'TaskSecretCreate',
         'retries': 0,
         'status': 1,
         'request_args': '{"AccessKey": "AWSCONN6", "ConnName": "AWS Conn 6", "Env": "dev"}',
         'result_ok': None,
         'result_error': None,
     }
     """

@pytest.mark.skip
def test_bucket_list_objects_nofilter():
    """Test Task bucket_list_objects"""

    task_uuid: str = "abc123"

    task_params = {
        "UUID": task_uuid,
        "UserId": 2,
        "Params": {
            "ARN": "arn:aws:secretsmanager:ap-southeast-1:204282492273:secret:/cstor/dev/2/secrets/654248d7-d0b9-4f13-a8e5-368f231d2181-mUuk9Q",
            "MigrationUUID": "defgh-456",
            "Name": "testvarchive",
            "CloudName": "AWS",
            "Endpoint": "",
            "Prefix": "",
        },
    }

    bucket_scan.send(task_params)


@pytest.mark.skip
def test_bucket_scan_objects_filter_size():
    """Test Task bucket_scan"""

    task_uuid: str = "abc123"

    task_params = {
        "UUID": task_uuid,
        "UserId": 2,
        "Params": {
            "MigrationUUID": "defgh-456",
            "ARN": "arn:aws:secretsmanager:ap-southeast-1:204282492273:secret:/cstor/dev/2/secrets/654248d7-d0b9-4f13-a8e5-368f231d2181-mUuk9Q",
            "Name": "testvarchive",
            "CloudName": "AWS",
            "Endpoint": "",
            "Prefix": "",
            "SizeGTE": 90,
            "SizeLTE": 200,
        },
    }

    bucket_scan.send(task_params)

    #time.sleep(10)

    cache: MigrationCache = MigrationCache(
        user_id=2,
        migration_uuid="defgh-456",
        is_readonly=True,
    )
    #migrate_itm: MigrationItem = cache.get_key("TEST_OUTLAY/large_files/large_8.txt")
    #print(migrate_itm)


@pytest.mark.skip
def test_bucket_migrate():
    """Test Task bucket_migrate"""

    muuid_orig: str = "defgh-456"
    muuid_test: str = "defgh-456-test"
    # Copy over sample from test above
    data_dir: str = os.environ["CSTOR_DATA_DIR"]
    db_dir: str = os.path.join(data_dir, "2")
    src_path: str = os.path.join(db_dir, f"{muuid_orig}.db")
    copy_path: str = os.path.join(db_dir, f"{muuid_test}.db")

    if os.path.exists(copy_path):
        shutil.rmtree(copy_path)
    shutil.copytree(src_path, copy_path)

    task_uuid: str = "abc123"

    task_params = {
        "UUID": task_uuid,
        "UserId": 2,
        "Params": {
            "MigrationUUID": muuid_test,
            "Src": {
                "ARN": "arn:aws:secretsmanager:ap-southeast-1:204282492273:secret:/cstor/dev/2/secrets/654248d7-d0b9-4f13-a8e5-368f231d2181-mUuk9Q",
                "Name": "testvarchive",
                "CloudName": "AWS",
                "Endpoint": "",
            },
            "Dest": {
                "ARN": "arn:aws:secretsmanager:ap-southeast-1:204282492273:secret:/cstor/dev/2/secrets/11156c35-f858-4f32-b5e1-7736a797b5fa-9WJVhf",
                "Name": "n-cstor-bucket",
                "CloudName": "LYC",
                "Endpoint": "https://s3.ap-southeast-1.lyvecloud.seagate.com",
            },
            "DestPrefix": "",
        },
    }

    bucket_migrate.send(task_params)
    bucket_migrate.send(task_params)
    #bucket_migrate.send(task_params)
    #bucket_migrate.send(task_params)
    #bucket_migrate.send(task_params)

    #time.sleep(10)

    #cache: MigrationCache = MigrationCache(
    #    user_id=2,
    #    migration_uuid="defgh-456",
    #    is_readonly=True,
    #)
    #migrate_itm: MigrationItem = cache.get_key("TEST_OUTLAY/large_files/large_8.txt")
    #print(migrate_itm)
