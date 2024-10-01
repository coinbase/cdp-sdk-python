from typing import Any

from eth_account.messages import _hash_eip191_message, encode_defunct, encode_typed_data
from eth_utils import to_hex


def hash_message(message_text: str) -> str:
    """Hashes a message according to EIP-191 and returns the hash as a 0x-prefixed hexadecimal string.

    This function prefixes the message with the standard Ethereum message prefix and hashes it using Keccak-256.

    Args:
        message_text (str): The message to hash.

    Returns:
        str: The 0x-prefixed hexadecimal string of the message hash.

    """
    message = encode_defunct(text=message_text)
    message_hash = _hash_eip191_message(message)

    return to_hex(message_hash)


def hash_typed_data_message(typed_data: dict[str, Any]) -> str:
    """Hashes typed data according to EIP-712 and returns the hash as a 0x-prefixed hexadecimal string.

    This function encodes the typed data as per EIP-712 and hashes it using Keccak-256.

    Args:
        typed_data (dict): The typed data to hash, following the EIP-712 specification.

    Returns:
        str: The 0x-prefixed hexadecimal string of the typed data hash.

    """
    typed_data_message = encode_typed_data(full_message=typed_data)
    typed_data_message_hash = _hash_eip191_message(typed_data_message)

    return to_hex(typed_data_message_hash)
