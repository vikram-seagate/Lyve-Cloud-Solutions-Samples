"""Fixtures, Mocks"""
import os
from typing import Any
from botocore.exceptions import ClientError, EndpointConnectionError
import pytest
from .fixtures.aws_static import (
    AWS_LIST_BUCKET_OK,
    AWS_HEAD_BUCKET_OK,
    AWS_LIST_OBJECT_NO_RECURSE,
    AWS_LIST_OBJECT_PREFIX,
)

from .fixtures.lyvecloud_static import (
    LYC_LIST_BUCKET_OK,
    LYC_HEAD_BUCKET_OK,
)

from .fixtures.secrets_static import (
    CREATE_SECRET_OK,
    GET_SECRET_OK,
    DELETE_SECRET_OK,
)



def get_sts_ok(mocker):
    """Return STS OK"""
    mock: Any  = mocker.MagicMock()
    mock.get_caller_identity.return_value = {}
    return mock


def get_sts_fail_account(mocker):
    """Return STS Fail Account Key"""
    mock: Any  = mocker.MagicMock()
    mock.get_caller_identity.side_effect = ClientError({
        "Error": {
            "Code": "InvalidClientTokenId",
            "Message": "",
        },
    }, "sts")
    return mock


def get_sts_fail_secret(mocker):
    """Return STS Fail Account Secret"""
    mock: Any  = mocker.MagicMock()
    mock.get_caller_identity.side_effect = ClientError({
        "Error": {
            "Code": "SignatureDoesNotMatch",
            "Message": "",
        },
    }, "sts")
    return mock


def get_sts_fail_conn(mocker):
    """Return STS Fail Endpoint"""
    mock: Any  = mocker.MagicMock()
    mock.get_caller_identity.side_effect = EndpointConnectionError(endpoint_url="XYZ")
    return mock


def get_sts_fail_unk(mocker):
    """Return STS Fail Unknown"""
    mock: Any  = mocker.MagicMock()
    mock.get_caller_identity.side_effect = ClientError({
        "Error": {
            "Code": "xyz",
            "Message": "",
        },
    }, "sts")
    return mock

def get_s3_list_buckets_ok(mocker):
    """Return s3.list_buckets Ok"""
    mock: Any  = mocker.MagicMock()
    mock.list_buckets.return_value = AWS_LIST_BUCKET_OK
    return mock


def get_s3_head_bucket_ok(mocker):
    """Return s3.head_bucket(Bucket="abc") Ok"""
    mock: Any  = mocker.MagicMock()
    mock.head_bucket.return_value = AWS_HEAD_BUCKET_OK
    return mock


def get_s3_head_bucket_fail_404(mocker):
    """Return s3.head_bucket(Bucket="abc") Fail (404)"""
    mock: Any  = mocker.MagicMock()
    mock.head_bucket.side_effect = ClientError({
        "Error": {
            "Code": "404",
            "Message": "",
        },
    }, "s3")
    return mock


def aws_bucket_list_objects_v2_prefix(mocker):
    """Return client_s3.list_objects_v2 Ok"""
    mock: Any  = mocker.MagicMock()
    mock.head_bucket.return_value = AWS_HEAD_BUCKET_OK
    mock.get_paginator.paginate.return_value([AWS_LIST_OBJECT_PREFIX])
    return mock

def aws_bucket_list_objects_v2_no_recurse(mocker):
    """Return client_s3.list_objects_v2 Ok"""
    mock: Any  = mocker.MagicMock()
    mock.head_bucket.return_value = AWS_HEAD_BUCKET_OK
    mock.get_paginator.paginate.return_value([AWS_LIST_OBJECT_NO_RECURSE])
    return mock


def lyc_s3_list_buckets_ok(mocker):
    """Return s3.list_buckets Ok"""
    mock: Any  = mocker.MagicMock()
    mock.list_buckets.return_value = LYC_LIST_BUCKET_OK
    return mock


def lyc_s3_head_bucket_ok(mocker):
    """Return LYC s3.head_bucket(Bucket="abc") Ok"""
    mock: Any  = mocker.MagicMock()
    mock.head_bucket.return_value = LYC_HEAD_BUCKET_OK
    return mock

#
def lyc_s3_list_buckets_fail_403(mocker):
    """Return lyc list buckets fail"""
    mock: Any  = mocker.MagicMock()
    mock.list_buckets.side_effect = ClientError({
        "Error": {
          "Message": "",
          "Code": ""
        },
        "ResponseMetadata": {
          "HTTPStatusCode": 403,
          "HTTPHeaders": {
            "content-type": "text/html",
            "content-length": "25",
            "connection": "keep-alive",
            "server": "nginx/1.21.3",
            "date": "Sat, 07 May 2022 02:33:16 GMT"
          },
          "RetryAttempts": 0
        }
    }, "s3")

    return mock


def secret_create_ok(mocker):
    """Return client.create_secret Ok"""
    mock: Any  = mocker.MagicMock()
    mock.create_secret.return_value = CREATE_SECRET_OK
    return mock


def secret_get_ok(mocker):
    """Return client.get_secret_value Ok"""
    mock: Any  = mocker.MagicMock()
    mock.get_secret_value.return_value = GET_SECRET_OK
    return mock

def secret_delete_ok(mocker):
    """Return client.delete_secret Ok"""
    mock: Any  = mocker.MagicMock()
    mock.delete_secret.return_value = DELETE_SECRET_OK
    return mock


def secret_get_fail_404(mocker):
    """Return client.get_secret_value Fail 404"""
    mock: Any  = mocker.MagicMock()
    mock.get_secret_value.side_effect = ClientError({
        "Error": {
            "Code": "ResourceNotFoundException",
            "Message": "Secrets Manager can't find the specified secret.",
        },
    }, "secretsmanager")
    return mock


EVENTS = {
    "sts_ok": get_sts_ok,
    "sts_fail_account": get_sts_fail_account,
    "sts_fail_secret": get_sts_fail_secret,
    "sts_fail_conn": get_sts_fail_conn,
    "sts_fail_unk": get_sts_fail_unk,
    "s3_list_buckets_ok": get_s3_list_buckets_ok,
    "s3_head_bucket_ok": get_s3_head_bucket_ok,
    "s3_head_bucket_fail_404": get_s3_head_bucket_fail_404,
    "aws_bucket_list_objects_v2_prefix": aws_bucket_list_objects_v2_prefix,
    "aws_bucket_list_objects_v2_no_recurse": aws_bucket_list_objects_v2_no_recurse,
    "lyc_s3_list_buckets_ok": lyc_s3_list_buckets_ok,
    "lyc_s3_list_buckets_fail_403": lyc_s3_list_buckets_fail_403,
    "lyc_s3_head_bucket_ok": lyc_s3_head_bucket_ok,
    "secret_create_ok": secret_create_ok,
    "secret_get_ok": secret_get_ok,
    "secret_delete_ok": secret_delete_ok,
    "secret_get_fail_404": secret_get_fail_404,
}


def patch_factory(mocker: Any, event: str) -> None:
    """Patch client returned from boto3.Session based on the event given
    :param event: The event to patch, must be one of keys in EVENTS

    :return:
    """

    class PatchSession:
        """Patched boto3.session.Session"""

        def __init__(self, *args, **kwargs):
            """CTOR"""

        def client(self, *args, **kwargs):
            """Returns a patched client"""
            return EVENTS[event](mocker)

    mocker.patch("boto3.session.Session", PatchSession)


@pytest.fixture()
def patch_sts(mocker):
    """
    Patch AWS S3 Session and STS
    """
    patch_factory(mocker, "sts_ok")


@pytest.fixture()
def patch_sts_fail_account(mocker):
    """
    Patch AWS S3 Session and STS
    """
    patch_factory(mocker, "sts_fail_account")


@pytest.fixture()
def patch_sts_fail_secret(mocker):
    """
    Patch AWS S3 Session and STS
    """
    patch_factory(mocker, "sts_fail_secret")


@pytest.fixture()
def patch_sts_fail_conn(mocker):
    """
    Patch AWS S3 Session and STS
    """
    patch_factory(mocker, "sts_fail_conn")


@pytest.fixture()
def patch_sts_fail_unk(mocker):
    """
    Patch AWS S3 Session and STS
    """
    patch_factory(mocker, "sts_fail_unk")


@pytest.fixture()
def patch_s3_list_buckets_ok(mocker):
    """
    Patch AWS s3.list_buckets() Ok
    """
    patch_factory(mocker, "s3_list_buckets_ok")


@pytest.fixture()
def patch_s3_head_bucket_ok(mocker):
    """
    Patch AWS s3.head_bucket(Bucket="abc") Ok
    """
    patch_factory(mocker, "s3_head_bucket_ok")


@pytest.fixture()
def patch_s3_head_bucket_fail_404(mocker):
    """
    Patch AWS s3.head_bucket(Bucket="abc") Fail 404
    """
    patch_factory(mocker, "s3_head_bucket_fail_404")


@pytest.fixture()
def patch_aws_bucket_list_objects_v2_prefix(mocker):
    """
    Patch
    """
    patch_factory(
        mocker,
        "aws_bucket_list_objects_v2_prefix",
    )


@pytest.fixture()
def patch_aws_bucket_list_objects_v2_no_recurse(mocker):
    """
    Patch
    """
    patch_factory(
        mocker,
        "aws_bucket_list_objects_v2_no_recurse",
    )


@pytest.fixture()
def patch_lyc_s3_list_buckets_ok(mocker):
    """
    Patch LYC s3.list_buckets() Ok
    """
    patch_factory(mocker, "lyc_s3_list_buckets_ok")


@pytest.fixture()
def patch_lyc_s3_list_buckets_fail_403(mocker):
    """
    Patch LYC s3.list_buckets() Fail (403)
    """
    patch_factory(mocker, "lyc_s3_list_buckets_fail_403")


@pytest.fixture()
def patch_lyc_s3_head_bucket_ok(mocker):
    """
    Patch LYC s3.head_bucket(Bucket="abc") Ok
    """
    patch_factory(mocker, "lyc_s3_head_bucket_ok")


@pytest.fixture()
def patch_secret_create_ok(mocker):
    """
    Patch Secret Create
    """
    patch_factory(mocker, "secret_create_ok")


@pytest.fixture()
def patch_secret_get_ok(mocker):
    """
    Patch Secret Get
    """
    patch_factory(mocker, "secret_get_ok")


@pytest.fixture()
def patch_secret_delete_ok(mocker):
    """
    Patch Secret Delete
    """
    patch_factory(mocker, "secret_delete_ok")


@pytest.fixture()
def patch_secret_get_fail_404(mocker):
    """
    Patch Secret Delete
    """
    patch_factory(mocker, "secret_get_fail_404")
