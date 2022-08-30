"""Default S3"""
from cstor.s3.core.aws import Account as AWSAccount


class Account(AWSAccount):
    """
    Default S3 Account
    """
    # For compatability with Backblaze and DigitalOcean
    region: str = ""

    def _verify(self) -> None:
        """Unsupported"""
