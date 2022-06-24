"""AWS Secrets"""
# pylint: disable=no-name-in-module, too-few-public-methods
import json
from typing import Any

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, EndpointConnectionError
from pydantic import BaseModel

from cstor.s3.exceptions import (
    CloudClientError,
    CloudEndpointError,
    CredentialError,
    SecretManagerError,
)

BOTO_CONFIG = Config(
    connect_timeout=2,
    read_timeout=2,
)


class AWSCredential(BaseModel):
    """AWS Credential"""

    AWS_ACCESS_KEY_ID: str = ...
    AWS_SECRET_ACCESS_KEY: str = ...


class SecretCreateResult(BaseModel):
    """AWSSecretResult"""

    ARN: str = ...


class SecretGetResult(BaseModel):
    """AWSSecretResult"""

    ARN: str = ...
    Cred: AWSCredential = ...
    ConnName: str = ...
    UserId: int = ...


class SecretDeleteResult(BaseModel):
    """AWSSecretResult"""

    ARN: str = ...


class Account(BaseModel):
    """
    AWS Secrets Manager Account
    """

    access_key: str = ...
    secret_key: str = ...
    region: str = None
    session: Any = None  # Set on init
    client_secret: Any = None  # Set on init

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

        # AWS Secrets Manager is region specific
        # so self.region needs to be populated
        self.client_secret = self.session.client(
            "secretsmanager",
            region_name=self.region,
        )

    # pylint: disable=too-many-arguments
    def create_secret(
        self,
        user_id: int,
        conn_name: str,
        cred: AWSCredential,
        env: str = "dev",
    ) -> SecretCreateResult:
        """Create a new secret in AWS Secrets Manager
        :param user_id: Django user_id
        :param conn_name: CloudProvider.name field in Django
        :param cred: AWS Credentials, access and secret key
        :param env: Environment to use: dev/prod

        :return: AWS Secret result for storing in model
        """
        secret_name: str = f"/cstor/{env}/{user_id}/secrets/{conn_name}"

        try:
            resp: dict = self.client_secret.create_secret(
                Description="Created by cstor",
                Name=secret_name,
                SecretString=json.dumps(dict(cred)),
            )

            return SecretCreateResult(
                ARN=resp["ARN"],
            )

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
            if error_info["Code"] in [
                "InvalidParameterException",
                "InvalidRequestException",
                "EncryptionFailure",
                "InternalServiceError",
                "PreconditionNotMetException",
                "ResourceNotFoundException",
            ]:
                raise SecretManagerError(
                    error_info["Message"],
                    error_info["Code"],
                ) from error
            # Unsupported ClientError
            raise CloudClientError(
                error_info["Message"],
                error_info["Code"],
            ) from error

    def get_secret(
        self,
        arn: str,
    ) -> AWSCredential:
        """Retrieve a secret by ARN
        :param arn: Amazon Resource Number

        :return: AWSCredential with access_key and secret_key
        """

        try:
            resp: dict = self.client_secret.get_secret_value(
                SecretId=arn,
            )

            cred: AWSCredential = AWSCredential(
                **json.loads(resp["SecretString"]),
            )

            return cred
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
            if error_info["Code"] in [
                "InvalidParameterException",
                "InvalidRequestException",
                "EncryptionFailure",
                "InternalServiceError",
                "PreconditionNotMetException",
                "ResourceNotFoundException",
            ]:
                raise SecretManagerError(
                    error_info["Message"],
                    error_info["Code"],
                ) from error
            # Unsupported ClientError
            raise CloudClientError(
                error_info["Message"],
                error_info["Code"],
            ) from error

    def delete_secret(
        self,
        arn: str,
    ) -> SecretDeleteResult:
        """Delete a secret by ARN
        :param arn: Amazon Resource Number

        :return: Result
        """

        try:
            self.client_secret.delete_secret(
                SecretId=arn,
                ForceDeleteWithoutRecovery=True,
            )
            return SecretDeleteResult(ARN=arn)

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
            if error_info["Code"] in [
                "InvalidParameterException",
                "InvalidRequestException",
                "EncryptionFailure",
                "InternalServiceError",
                "PreconditionNotMetException",
                "ResourceNotFoundException",
            ]:
                raise SecretManagerError(
                    error_info["Message"],
                    error_info["Code"],
                ) from error
            # Unsupported ClientError
            raise CloudClientError(
                error_info["Message"],
                error_info["Code"],
            ) from error
