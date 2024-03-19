from cryptography.fernet import Fernet

from nalgonda.services.encryption_service import EncryptionService


def test_encrypt():
    # Arrange
    encryption_key = Fernet.generate_key()
    encryption_service = EncryptionService(encryption_key)
    value = "Привет, Мир!"

    # Act
    encrypted_value = encryption_service.encrypt(value)

    # Assert
    assert encrypted_value != value
    assert encryption_service.decrypt(encrypted_value) == value


def test_decrypt():
    # Arrange
    encryption_key = Fernet.generate_key()
    encryption_service = EncryptionService(encryption_key)
    value = "Привет, Мир!"
    encrypted_value = encryption_service.encrypt(value)

    # Act
    decrypted_value = encryption_service.decrypt(encrypted_value)

    # Assert
    assert decrypted_value == value
