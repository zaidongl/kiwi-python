import logging
import os
import base64
import binascii
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

class AESCipher:
    """
    AES-128-ECB cipher for encryption and decryption of secrets.
    Implements singleton pattern to reuse cipher instance.
    """
    ALGORITHM = "AES"
    TRANSFORMATION = "AES/ECB/PKCS5Padding"
    CHARSET = "utf-8"
    ENV_VAR_AES_KEY = "KIWI_AES_KEY"
    PROPERTY_AES_KEY = "kiwi.aes.key"

    _instance = None
    _encrypt_cipher = None
    _decrypt_cipher = None
    _logger = logging.getLogger(__name__)

    def __init__(self):
        """
        Private constructor to prevent direct instantiation.
        Use get_instance() method to get the singleton instance.
        """
        s_key = os.getenv(self.PROPERTY_AES_KEY) or os.getenv(self.ENV_VAR_AES_KEY)
        if s_key is None  or s_key == "":
            raise ValueError("AES key not set. Please set it via system property 'aes.key'"
                             " or environment variable 'KIWI_AES_KEY'.")
        self._encrypt_cipher = self._get_cipher(AES.MODE_ECB, s_key)
        self._decrypt_cipher = self._get_cipher(AES.MODE_ECB, s_key)

    @classmethod
    def get_instance(cls):
        """
        Get the singleton instance of AESCipher.
        :return: AESCipher instance
        """
        if cls._instance is None:
            cls._instance = AESCipher()
        return cls._instance

    def _get_cipher(self, mode, s_key: str):
        """
        Create and initialize a cipher instance

        Args:
            mode: AES mode(ECB)
            s_key: The encryption key as a string.

        Return:
            AES cipher instance

        Raises:
            ValueError: If the key is invalid
        """
        if s_key is None:
            raise ValueError("Key must not be null")
        if len(s_key) != 16:
            raise ValueError("Key length must be 16 characters for AES-128")

        raw = s_key.encode(self.CHARSET)
        cipher = AES.new(raw, mode)
        return cipher

    def encrypt(self, plain_text: str) -> str:
        """
        Encrypt the given plain text using AES-128-ECB and return a hex-encoded string
        :param plain_text:
        :return:
        """
        plaintext_bytes = plain_text.encode(self.CHARSET)
        padded_plaintext = pad(plaintext_bytes, AES.block_size)
        encrypted = self._encrypt_cipher.encrypt(padded_plaintext)
        base64_encoded = base64.b64encode(encrypted)
        hex_string = binascii.hexlify(base64_encoded).decode(self.CHARSET)
        return hex_string

    def decrypt(self, hex_cipher_text: str) -> str:
        """
        Decrypt the given hex-encoded cipher text using AES-128-ECB and return the plain text
        :param hex_cipher_text:
        :return:
        """
        try:
            base64_bytes = binascii.unhexlify(hex_cipher_text.encode(self.CHARSET))
            encrypted_bytes = base64.b64decode(base64_bytes)
            decrypted_padded = self._decrypt_cipher.decrypt(encrypted_bytes)
            decrypted = unpad(decrypted_padded, AES.block_size)
            plain_text = decrypted.decode(self.CHARSET)
            return plain_text
        except (binascii.Error, ValueError) as e:
            self._logger.error("Error while decrypting %s, %s", hex_cipher_text, str(e))
            raise ValueError("Decryption failed. Invalid cipher text or key.") from e