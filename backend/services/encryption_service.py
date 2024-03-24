from cryptography.fernet import Fernet


class EncryptionService:
    """Service to encrypt and decrypt values using Fernet symmetric encryption algorithm."""

    def __init__(self, encryption_key: bytes):
        self._encryption_key = encryption_key

    def encrypt(self, value: str) -> str:
        f = Fernet(self._encryption_key)
        encrypted_bytes = f.encrypt(value.encode())
        return encrypted_bytes.decode()

    def decrypt(self, value: str) -> str:
        f = Fernet(self._encryption_key)
        encrypted_bytes = value.encode()
        return f.decrypt(encrypted_bytes).decode()
