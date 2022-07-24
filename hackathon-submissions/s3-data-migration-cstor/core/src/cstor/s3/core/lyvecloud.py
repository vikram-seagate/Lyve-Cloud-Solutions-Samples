"""LyveCloud S3"""
from cstor.s3.core.aws import Account as AWSAccount


class Account(AWSAccount):
    """LyveCloud Account"""

    def _verify(self) -> None:
        """Unsupported"""
