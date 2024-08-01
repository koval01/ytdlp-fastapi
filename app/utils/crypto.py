import json
from time import time

from cryptography.fernet import Fernet

from app.utils.config import settings


class Cryptography:
    """
    Provides encryption and decryption utilities using Fernet.
    """

    def __init__(self) -> None:
        """
        Initializes the Cryptography class.

        Loads the encryption key from the environment variable `CRYPT_KEY`.
        """
        key: bytes = settings.CRYPT_KEY.encode()
        self.fernet = Fernet(key)

    def encrypt(self, _input: str) -> str:
        """
        Encrypts the input string using Fernet.

        Args:
            _input: The input string to encrypt.

        Returns:
            The encrypted string.
        """
        return self.fernet.encrypt_at_time(
            _input.encode(), int(time())
        ).decode().replace("=", "")

    def encrypt_json(self, _input: dict) -> str:
        """
        Encrypts the input dictionary using Fernet.

        Adds a timestamp to the input dictionary before encryption.

        Args:
            _input: The input dictionary to encrypt.

        Returns:
            The encrypted string.
        """
        return self.encrypt(json.dumps(_input))

    def decrypt(self, _input: str) -> str:
        """
        Decrypts the input string using Fernet.

        Args:
            _input: The input string to decrypt.

        Returns:
            The decrypted string.
        """
        return self.fernet.decrypt(
            _input.encode() + b'=' * (-len(_input) % 4),
            ttl=3600
        ).decode()

    def decrypt_json(self, _input: str) -> dict:
        """
        Decrypts the input string using Fernet and loads the JSON data.

        Args:
            _input: The input string to decrypt.

        Returns:
            The decrypted JSON data.
        """
        return json.loads(self.decrypt(_input))
