"""Test Lyvecloud"""
# pylint: disable=unused-argument
import pytest
from cstor.s3.core.lyvecloud import Account
from cstor.s3.core.aws import ListBucketResult
from cstor.s3.exceptions import (
    CredentialError,
)


def test_lyc_list_buckets_ok(patch_lyc_s3_list_buckets_ok):
    """Test LYC List Buckets"""
    account: Account = Account(
        access_key="test123",
        secret_key="abc123",
        endpoint_s3="https://s3.ap-southeast-1.lyvecloud.seagate.com",
    )
    result: ListBucketResult = account.list_buckets()

    assert len(result.Buckets) == 1


def test_lyc_list_buckets_fail_403(patch_lyc_s3_list_buckets_fail_403):
    """Test LYC List Buckets Fail 403"""
    with pytest.raises(CredentialError):
        account: Account = Account(
            access_key="test123",
            secret_key="abc123",
            endpoint_s3="https://s3.ap-southeast-1.lyvecloud.seagate.com",
        )
        account.list_buckets()


def test_lyc_head_bucket_ok(patch_lyc_s3_head_bucket_ok):
    """Test LYC Head Bucket Ok"""
    account: Account = Account(
        access_key="test123",
        secret_key="abc123",
        endpoint_s3="https://s3.ap-southeast-00.lyvecloud.seagate.com",
    )
    account.get_bucket("n-auditlogs2")
