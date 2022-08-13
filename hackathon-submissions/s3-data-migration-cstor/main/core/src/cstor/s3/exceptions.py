"""CSTOR Exceptions"""


class SecretManagerError(Exception):
    """Secret Manager Error"""

    def __init__(self, msg: str, code: str):
        """CTOR"""
        super().__init__(msg)
        self.msg = msg
        self.code = code


class CredentialError(Exception):
    """Credential Error"""

    def __init__(self, msg: str, code: str):
        """CTOR"""
        super().__init__(msg)
        self.msg = msg
        self.code = code


class CloudEndpointError(Exception):
    """Unable to reach cloud endpoint"""


class CloudClientError(Exception):
    """Unsupported ClientError"""

    def __init__(self, msg: str, code: str):
        """CTOR"""
        super().__init__(msg)
        self.msg = msg
        self.code = code


class BucketNotFoundError(Exception):
    """(404) Bucket NotFound Error"""

    def __init__(self, msg: str, code: str):
        """CTOR"""
        super().__init__(msg)
        self.msg = msg
        self.code = code


class BucketAccessDeniedError(Exception):
    """(403) Bucket AccessDenied Error"""

    def __init__(self, msg: str, code: str):
        """CTOR"""
        super().__init__(msg)
        self.msg = msg
        self.code = code
