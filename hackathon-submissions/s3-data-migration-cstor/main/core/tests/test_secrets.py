"""Test Secrets"""
# pylint: disable=line-too-long
import pytest
from cstor.s3.secrets import Account, AWSCredential, SecretCreateResult
from cstor.s3.exceptions import SecretManagerError


def test_create_secret(patch_secret_create_ok):
    """Test Creating a Secret"""
    cred: AWSCredential = AWSCredential(
        AWS_ACCESS_KEY_ID="abc123",
        AWS_SECRET_ACCESS_KEY="Test123!",
    )
    account: Account = Account(
        access_key="test123",
        secret_key="secret456",
        region="ap-southeast-1",
    )
    result: SecretCreateResult = account.create_secret(
        1,
        "AWSConn1",
        cred,
    )

    assert result.ARN == "arn:aws:secretsmanager:ap-southeast-1:204282492273:secret:/cstor/dev/1/secrets/AWSConn1-T5zIxQ"


def test_get_secret_ok(patch_secret_get_ok):
    """Test getting a secret"""
    secret_arn: str = "arn:aws:secretsmanager:ap-southeast-1:204282492273:secret:/cstor/dev/1/secrets/AWSConn1-T5zIxQ"
    #secret_arn: str = "arn:aws:secretsmanager:ap-southeast-1:204282492273:secret:/cstor/dev/1/secrets/AWS1"

    account: Account = Account(
        access_key="test123",
        secret_key="secret456",
        region="ap-southeast-1",
    )

    cred: AWSCredential = account.get_secret(secret_arn)

    assert cred.AWS_ACCESS_KEY_ID == "abc123"
    assert cred.AWS_SECRET_ACCESS_KEY == "Test123!"


def test_get_secret_fail_404(patch_secret_get_fail_404):
    """Test getting a secret"""
    secret_arn: str = "arn:aws:secretsmanager:ap-southeast-1:204282492273:secret:/cstor/dev/1/secrets/AWS1"

    account: Account = Account(
        access_key="test123",
        secret_key="secret456",
        region="ap-southeast-1",
    )

    with pytest.raises(SecretManagerError):
        account.get_secret(secret_arn)


def test_delete_secret(patch_secret_delete_ok):
    """Test deleting a secret"""
    secret_arn: str = "arn:aws:secretsmanager:ap-southeast-1:204282492273:secret:/cstor/dev/1/secrets/AWSConn1-T5zIxQ"

    account: Account = Account(
        access_key="test123",
        secret_key="secret456",
        region="ap-southeast-1",
    )

    account.delete_secret(secret_arn)
