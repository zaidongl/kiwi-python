import logging
import os

from kiwi.security.crypto.aes_cipher import AESCipher


class SecurityHelper:
    """
    SecurityHelper provides utility methods for security-related operations.
    """
    _logger = logging.getLogger(__name__)

    @classmethod
    def process_authentication_field(cls, raw_field:str) -> str | None:
        """
        Process the authentication field to handle sensitive information.
        Args:
        :param raw_field: The raw authentication field value.
        :return: Processed authentication field or None if empty.
        """
        if raw_field and raw_field.strip():
            cls._logger.debug("Processing authentication field.")
            if raw_field.startswith('$'):
                result = os.getenv(raw_field[1:], None)
                if result is None:
                    cls._logger.warning(f"Environment variable for authentication field '{raw_field}' not found.")
                    return None
            else:
                result = AESCipher.get_instance().decrypt(raw_field)
            return result
        cls._logger.debug("Authentication field is empty or None.")
        return None