"""Test Main"""
# pylint: disable=unused-argument, unused-variable
import datetime
from dateutil.tz import tzutc
import io
import pytest
from cstor.s3.core.aws import Account, ListBucketResult, S3Object
from cstor.s3.exceptions import (
    CredentialError,
    CloudEndpointError,
    CloudClientError,
    BucketNotFoundError,
)


def test_aws_auth_ok(patch_sts):
    """Test AWS auth ok"""
    Account(
        access_key="test123",
        secret_key="secret456",
    )


def test_aws_auth_fail_account(patch_sts_fail_account):
    """Test AWS auth fail account"""
    with pytest.raises(CredentialError):
        Account(
            access_key="test123",
            secret_key="secret456",
        )


def test_aws_auth_fail_secret(patch_sts_fail_secret):
    """Test AWS auth fail secret"""
    with pytest.raises(CredentialError):
        Account(
            access_key="test123",
            secret_key="secret456",
        )


def test_aws_auth_fail_conn(patch_sts_fail_conn):
    """Test AWS auth fail secret"""
    with pytest.raises(CloudEndpointError):
        Account(
            access_key="test123",
            secret_key="secret456",
        )


def test_aws_auth_fail_unk(patch_sts_fail_unk):
    """Test AWS auth fail clienterror unsupported"""
    with pytest.raises(CloudClientError):
        Account(
            access_key="test123",
            secret_key="secret456",
        )


def test_aws_list_buckets_ok(patch_s3_list_buckets_ok):
    """Test AWS List Buckets"""
    account: Account = Account(
        access_key="test123",
        secret_key="secret456",
    )
    result: ListBucketResult = account.list_buckets()

    assert len(result.Buckets) == 1
    assert result.Buckets[0].Name == "testvarchive"


def test_aws_head_bucket_ok(patch_s3_head_bucket_ok):
    """Test AWS Head Bucket"""
    account: Account = Account(
        access_key="test123",
        secret_key="secret456",
    )
    account.get_bucket("testvarchive2")


def test_aws_head_bucket_fail_404(patch_s3_head_bucket_fail_404):
    """Test AWS Head Bucket"""
    account: Account = Account(
        access_key="test123",
        secret_key="secret456",
    )
    with pytest.raises(BucketNotFoundError):
        account.get_bucket("testvarchive2")


def test_aws_bucket_list_objects_prefix(
    patch_s3_head_bucket_ok,
    patch_aws_bucket_list_objects_v2_prefix,
):
    """Test AWS Head Bucket"""
    account: Account = Account(
        access_key="test123",
        secret_key="secret456",
    )
    bucket = account.get_bucket("testvarchive")
    bucket_contents = bucket.list_objects(prefix="TEST_OUTLAY/large_files")
    for bucket_item in bucket_contents:
        bucket_out = list(map(lambda itm: itm.json(), bucket_item))


def test_aws_bucket_list_objects_no_recurse(
    patch_s3_head_bucket_ok,
    patch_aws_bucket_list_objects_v2_no_recurse,
):
    """Test AWS Head Bucket"""
    account: Account = Account(
        access_key="test123",
        secret_key="secret456",
    )
    bucket = account.get_bucket("testvarchive")
    bucket_contents = bucket.list_objects(
        prefix="TEST_OUTLAY/medium_files/",
        delimiter="/",
    )
    for bucket_item in bucket_contents:
        print(bucket_item)

@pytest.mark.skip
def test_aws_bucket_download_raw():
    """Test AWS Download Raw"""
    account: Account = Account(
        #access_key="test123",
        #secret_key="secret456",
        access_key=LIVE_KEY,
        secret_key=LIVE_SECRET,
    )
    bucket = account.get_bucket("testvarchive")

    s3obj_large: dict = {
        'Key': 'TEST_OUTLAY/large_files/large_0.txt',
        'LastModified': datetime.datetime(2022, 5, 7, 3, 41, 34, tzinfo=tzutc()),
        'ETag': '"50b52adb0eee4202821f2987f5b77f66-259"',
        'Size': 2166358016,
        'StorageClass': 'STANDARD',
    }

    data: io.BytesIO = bucket.download_raw(S3Object(**s3obj_large))

    del data


#def test_aws_head_bucket(patch_s3_head_bucket_ok):
#    """Test AWS Head Bucket"""
#    account: Account = Account(
#        access_key="AKIAS7EBPOVYRMO4WUGC",
#        secret_key="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",
#    )
#    account.get_bucket("testvarchive2")
