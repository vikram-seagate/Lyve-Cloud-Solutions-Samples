"""AWS S3"""
from __future__ import annotations

# pylint: disable=too-few-public-methods, no-member, consider-using-with, too-many-locals
# from boto3.session import Session
# import datetime
import datetime as dt

# import io
import os
import tempfile

# import json
# import logging
# import time
from typing import Any, List, Union

import boto3
from boto3.s3.transfer import TransferConfig
from botocore.config import Config
from botocore.exceptions import ClientError, EndpointConnectionError

# pylint: disable=no-name-in-module
from pydantic import BaseModel

from cstor.s3.exceptions import (
    BucketAccessDeniedError,
    BucketNotFoundError,
    CloudClientError,
    CloudEndpointError,
    CredentialError,
)
from cstor.s3.rocksdb.main import MigrationLog, MigrationStatus

# FOR DEBUGGING
# logging.basicConfig(
#    level=logging.DEBUG,
#    format='%(asctime)s %(message)s',
#    handlers=[
#      logging.StreamHandler(),
#    ],
# )
#
# boto3.set_stream_logger("", logging.DEBUG)

BOTO_CONFIG = Config(
    connect_timeout=2,
    read_timeout=2,
)


class ListBucketItem(BaseModel):
    """List Bucket Item"""

    Name: str = ...
    CreationDate: dt.datetime = ...


class ListBucketOwner(BaseModel):
    """List Bucket Owner"""

    DisplayName: str = ...
    ID: str = ...


class ListBucketResult(BaseModel):
    """List Bucket Result"""

    Buckets: List[ListBucketItem]
    Owner: ListBucketOwner


class S3Object(BaseModel):
    """A single S3 Object"""

    Key: str = ...
    LastModified: dt.datetime = ...
    ETag: str = ...
    Size: int  # In bytes
    StorageClass: str


class S3Folder(BaseModel):
    """A single S3 Folder"""

    Prefix: str = ...


class S3ObjectIter(BaseModel):
    """S3ObjectIter"""

    data: Any = ...

    def __iter__(self):
        """For usage in for loops"""
        return self

    def __next__(self) -> List[S3Object]:
        try:
            page: Any = next(self.data)
            contents: List[S3Object] = list(
                map(
                    lambda raw: S3Object(**raw),
                    page["Contents"],
                )
            )
            return contents
        except StopIteration as error:
            raise StopIteration from error


class S3FolderIter(BaseModel):
    """S3FolderIter"""

    data: Any = ...

    def __iter__(self):
        """For usage in for loops"""
        return self

    def __next__(self) -> List[S3Folder]:
        try:
            page: Any = next(self.data)
            contents: List[S3Folder] = list(
                map(
                    lambda raw: S3Folder(**raw),
                    page["CommonPrefixes"],
                )
            )
            return contents
        except StopIteration as error:
            raise StopIteration from error


class Account(BaseModel):
    """
    AWS S3 Account
    """

    access_key: str = ...
    secret_key: str = ...
    region: str = None
    endpoint_s3: str = None
    session: Any = None  # Set on init
    client_s3: Any = None  # Set on init

    def _verify(self):
        """Verify Credentials"""
        sts: Any = self.session.client(
            "sts",
            config=BOTO_CONFIG,
        )
        try:
            sts.get_caller_identity()
        except EndpointConnectionError as error:
            # Unable to connect to the endpoint
            raise CloudEndpointError from error
        except ClientError as error:
            error_info: dict = error.response["Error"]
            if error_info["Code"] in [
                "SignatureDoesNotMatch",
                "InvalidClientTokenId",
            ]:
                raise CredentialError(
                    error_info["Message"],
                    error_info["Code"],
                ) from error
            # Unsupported ClientError
            raise CloudClientError(
                error_info["Message"],
                error_info["Code"],
            ) from error

    def __init__(self, **kwargs):
        """Constructor"""
        super().__init__(**kwargs)
        self.session: boto3.session.Session = boto3.session.Session(
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region,
        )
        self._verify()

        self.client_s3 = self.session.client(
            "s3",
            endpoint_url=self.endpoint_s3,
            region_name=self.region,
        )

    def list_buckets(self) -> ListBucketResult:
        """List all buckets accessible by the user"""
        try:
            resp: dict = self.client_s3.list_buckets()
            result: ListBucketResult = ListBucketResult(**resp)
            return result
        except EndpointConnectionError as error:
            # Unable to connect to the endpoint
            raise CloudEndpointError from error
        except ClientError as error:
            error_info: dict = error.response["Error"]
            error_meta: dict = error.response["ResponseMetadata"]
            # print(json.dumps(error.response))
            # For Lyvecloud, the code is empty
            if error_info["Code"] in [
                "SignatureDoesNotMatch",
                "InvalidClientTokenId",
            ]:
                raise CredentialError(
                    error_info["Message"],
                    error_info["Code"],
                ) from error
            # For Lyvecloud, when credentials are incorrect
            if error_meta["HTTPStatusCode"] == 403:
                raise CredentialError(
                    "403 Error",
                    "403 Error",
                ) from error
            # Unsupported ClientError
            raise CloudClientError(
                error_info["Message"],
                error_info["Code"],
            ) from error

    def get_bucket(self, name: str) -> None:
        """Authenticate and return a Bucket

        :param name: Name of the bucket
        """
        try:
            bucket_resp: dict = self.client_s3.head_bucket(Bucket=name)
            # Get region
            region: str = (
                bucket_resp.get("ResponseMetadata")
                .get("HTTPHeaders")
                .get("x-amz-bucket-region")
            )

            return Bucket(
                client_s3=self.client_s3,
                name=name,
                region=region,
            )
            # return result
        except EndpointConnectionError as error:
            # Unable to connect to the endpoint
            raise CloudEndpointError from error
        except ClientError as error:
            # print(json.dumps(error.response))
            error_info: dict = error.response["Error"]
            if error_info["Code"] in [
                "SignatureDoesNotMatch",
                "InvalidClientTokenId",
            ]:
                raise CredentialError(
                    error_info["Message"],
                    error_info["Code"],
                ) from error
            if error_info["Code"] == "404":
                raise BucketNotFoundError(
                    error_info["Message"],
                    error_info["Code"],
                ) from error
            if error_info["Code"] == "403":
                raise BucketAccessDeniedError(
                    error_info["Message"],
                    error_info["Code"],
                ) from error
            # Unsupported ClientError
            raise CloudClientError(
                error_info["Message"],
                error_info["Code"],
            ) from error


# reference:
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/customizations/s3.html#boto3.s3.transfer.TransferConfig
MB_SIZE: int = 1024 * 1024
MB_CONCUR: int = 100 * MB_SIZE
DEFAULT_CHUNKSIZE: int = 8388608
# AWS S3 smallest chunk allowed is 1/10000th of the file size
# Because multipart chunks are limited to 10000 in number
MAX_DEFAULT_SIZE: int = DEFAULT_CHUNKSIZE * 10000


def get_transfer_config(size: int) -> TransferConfig:
    """Get transfer config based on S3Object"""
    multipart_size: int = (
        DEFAULT_CHUNKSIZE if size < MAX_DEFAULT_SIZE else (int(size / 10000) + 1)
    )
    # For every 100mb we add 2 threads
    size_concur: int = ((size / MB_CONCUR) + 1) * 2
    max_concur: int = max(10, size_concur)
    max_concur = min(30, max_concur)
    return TransferConfig(
        multipart_threshold=multipart_size,
        num_download_attempts=1,
        # Default
        # max_concurrency=10,
        max_concurrency=max_concur,
    )


def get_utc_now() -> int:
    """Get UTC Timestamp Now"""
    dt_now: dt.datetime = dt.datetime.utcnow()
    return dt_now.timestamp()


class ProgressBar(BaseModel):
    """ProgressBar"""

    stage: str = ...
    migrate_key: Any = ...
    migrate_item: Any = ...
    done_bytes: int = 0
    done_percent: int = 0

    def __call__(self, update_bytes: int):
        self.done_bytes += update_bytes
        done_percent = int((self.done_bytes / self.migrate_item.Size) * 100)
        if done_percent % 5 == 0 and done_percent != self.done_percent:
            self.done_percent = int(done_percent)
            print(f"[{self.stage}] {self.migrate_key} {self.done_percent} %")


class Bucket(BaseModel):
    """S3 Compatible Bucket"""

    client_s3: Any = ...  # S3 Client from Session
    name: str = ...  # Name of the S3 Bucket
    # Bugfix that would enable DigitalOcean and Backblaze to work as endpoints.
    #region: str = ""
    region: str = None

    def list_objects(
        self,
        prefix: str = "",
        delimiter: str = None,
    ) -> Union[S3ObjectIter, S3FolderIter]:
        """List objects in the bucket as an Iterable

        Usage:
        # To search only a subpath
        TEST_OUTLAY/large_files

        list_objects(prefix="TEST_OUTLAY/large_files")

        # To not search recursively

        list_objects(prefix="TEST_OUTLAY/medium_files", delimiter="/")

        :param prefix: Prefix path to use for S3
        :param delimiter: Delimiter to use, "/" for not recursing into folders
        """
        try:
            op_args = dict(
                Bucket=self.name,
                Prefix=prefix,
                PaginationConfig={"PageSize": 1000},
            )

            if delimiter is not None:
                op_args["Delimiter"] = delimiter

            paginator = self.client_s3.get_paginator("list_objects_v2")
            page_iterator = iter(paginator.paginate(**op_args))

            if delimiter is not None:
                return S3FolderIter(data=page_iterator)
            return S3ObjectIter(data=page_iterator)

        except ClientError as error:
            # print(json.dumps(error.response))
            error_info: dict = error.response["Error"]
            if error_info["Code"] in [
                "SignatureDoesNotMatch",
                "InvalidClientTokenId",
            ]:
                raise CredentialError(
                    error_info["Message"],
                    error_info["Code"],
                ) from error
            if error_info["Code"] == "404":
                raise BucketNotFoundError(
                    error_info["Message"],
                    error_info["Code"],
                ) from error
            if error_info["Code"] == "403":
                raise BucketAccessDeniedError(
                    error_info["Message"],
                    error_info["Code"],
                ) from error
            # Unsupported ClientError
            raise CloudClientError(
                error_info["Message"],
                error_info["Code"],
            ) from error

    def _download(self, migrate_key: str, migrate_item: any) -> any:
        """Download raw object into temporary file"""
        log_prefix: str = "SRC"
        tmpfile: any = tempfile.NamedTemporaryFile(delete=False)
        config: any = get_transfer_config(migrate_item.Size)
        try:
            self.client_s3.download_file(
                self.name,
                migrate_key,
                tmpfile.name,
                Config=config,
                Callback=ProgressBar(
                    stage="DOWNLOAD",
                    migrate_key=migrate_key,
                    migrate_item=migrate_item,
                ),
            )
            return tmpfile.name
        except EndpointConnectionError:
            # Unable to connect to the endpoint
            fail_class: str = f"{log_prefix}:EndpointConnectionError"
            log_ts: int = get_utc_now()
            fail_log: MigrationLog = MigrationLog(
                PrevState=MigrationStatus.IN_PROGRESS,
                State=MigrationStatus.FAILED,
                Timestamp=log_ts,
                FailClass=fail_class,
            )
            migrate_item.State = MigrationStatus.FAILED
            migrate_item.Events = [fail_log] + migrate_item.Events
            # Cleanup
            os.remove(tmpfile.name)
            return None
        except ClientError as error:
            error_info: dict = error.response["Error"]
            fail_class: str = f"{log_prefix}:ClientError"
            fail_code = error_info["Code"]
            fail_mesg = error_info["Message"]
            log_ts: int = get_utc_now()

            if error_info["Code"] in [
                "SignatureDoesNotMatch",
                "InvalidClientTokenId",
            ]:
                fail_class = "CredentialError"
            if error_info["Code"] == "404":
                fail_class = "BucketNotFound"
            if error_info["Code"] == "403":
                fail_class = "BucketAccessDenied"

            fail_log: MigrationLog = MigrationLog(
                PrevState=MigrationStatus.IN_PROGRESS,
                State=MigrationStatus.FAILED,
                Timestamp=log_ts,
                FailClass=fail_class,
                FailCode=fail_code,
                FailMesg=fail_mesg,
            )
            migrate_item.State = MigrationStatus.FAILED
            migrate_item.Events = [fail_log] + migrate_item.Events
            # Cleanup
            os.remove(tmpfile.name)
            return None

    def upload(
        self,
        migrate_fpath: str,
        migrate_key: str,
        migrate_item: any,
        dest_prefix: str = "",
    ) -> any:
        """Upload from temporary file"""
        log_prefix: str = "DEST"
        #tmpfile: any = tempfile.NamedTemporaryFile(delete=False)
        config: any = get_transfer_config(migrate_item.Size)
        dest_key: str = str(migrate_key)

        if dest_prefix != "":
            dest_key = f"{dest_prefix}{migrate_key}"

        try:
            self.client_s3.upload_file(
                migrate_fpath,
                self.name,
                dest_key,
                Config=config,
                Callback=ProgressBar(
                    stage="UPLOAD",
                    migrate_key=migrate_key,
                    migrate_item=migrate_item,
                ),
            )
            # No exceptions means success
            migrate_item.State = MigrationStatus.SUCCESS
            log_ts: int = get_utc_now()
            success_log: MigrationLog = MigrationLog(
                PrevState=MigrationStatus.IN_PROGRESS,
                State=MigrationStatus.SUCCESS,
                Timestamp=log_ts,
            )
            migrate_item.Events = [success_log] + migrate_item.Events
        except EndpointConnectionError:
            # Unable to connect to the endpoint
            fail_class: str = f"{log_prefix}:EndpointConnectionError"
            log_ts: int = get_utc_now()
            fail_log: MigrationLog = MigrationLog(
                PrevState=MigrationStatus.IN_PROGRESS,
                State=MigrationStatus.FAILED,
                Timestamp=log_ts,
                FailClass=fail_class,
            )
            migrate_item.State = MigrationStatus.FAILED
            migrate_item.Events = [fail_log] + migrate_item.Events
        except ClientError as error:
            error_info: dict = error.response["Error"]
            fail_class: str = f"{log_prefix}:ClientError"
            fail_code = error_info["Code"]
            fail_mesg = error_info["Message"]
            log_ts: int = get_utc_now()

            if error_info["Code"] in [
                "SignatureDoesNotMatch",
                "InvalidClientTokenId",
            ]:
                fail_class = "CredentialError"
            if error_info["Code"] == "404":
                fail_class = "BucketNotFound"
            if error_info["Code"] == "403":
                fail_class = "BucketAccessDenied"

            fail_log: MigrationLog = MigrationLog(
                PrevState=MigrationStatus.IN_PROGRESS,
                State=MigrationStatus.FAILED,
                Timestamp=log_ts,
                FailClass=fail_class,
                FailCode=fail_code,
                FailMesg=fail_mesg,
            )
            migrate_item.State = MigrationStatus.FAILED
            migrate_item.Events = [fail_log] + migrate_item.Events
        finally:
            # Cleanup
            #os.remove(tmpfile.name)
            os.remove(migrate_fpath)

    def migrate(
        self,
        dest_bucket: Bucket,
        migrate_payload: dict,
        dest_prefix: str = "",
    ) -> dict:
        """Perform a migration between 2 S3 compatible buckets
        :param dest_bucket: Destination Bucket
        :param migrate_payload: Dict of SrcKey to MigrationItem
        :param dest_prefix: Prefix to prepend to destination key

        :return: Dict of SrcKey to MigrationItem
        """
        result: dict = {}
        for migrate_key in migrate_payload:
            migrate_item = migrate_payload[migrate_key]
            # Download
            migrate_fpath = self._download(
                migrate_key,
                migrate_item,
            )
            # Download successful
            if migrate_fpath:
                dest_bucket.upload(
                    migrate_fpath,
                    migrate_key,
                    migrate_item,
                    dest_prefix,
                )
                result[migrate_key] = migrate_item
            else:
                result[migrate_key] = migrate_item
                continue
        return result

    # def download_raw(
    #    self,
    #    s3obj: S3Object,
    # ) -> io.BytesIO:
    #    """Downloads an object from S3 Bucket and save into memory

    #    Usage: Only used for objects below 2 Gb, object needs to fit into
    #    memory comfortably.

    #    """

    #    raw_data: io.BytesIO = io.BytesIO()

    #    # Run operation
    #    self.client_s3.download_fileobj(
    #        self.name,
    #        s3obj.Key,
    #        raw_data,
    #        # Callback=ProgressBar(s3obj=s3obj),
    #        Config=get_transfer_config(s3obj),
    #    )

    #    return raw_data
