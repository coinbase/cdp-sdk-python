from cdp.hash_utils import hash_message, hash_typed_data_message


def test_hash_message():
    """Test hash_message utility method."""
    message_hash = hash_message("Hello, EIP-191!")
    assert message_hash == "0x54c2490066f5b62dd2e2ea2310c2b3d63039bbce5e3f96175a1b66a0c484e74f"


def test_hash_typed_data_message():
    """Test hash_typed_data_message utility method."""
    typed_data = {
        "types": {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"},
            ],
            "Person": [{"name": "name", "type": "string"}, {"name": "wallet", "type": "address"}],
            "Mail": [
                {"name": "from", "type": "Person"},
                {"name": "to", "type": "Person"},
                {"name": "contents", "type": "string"},
            ],
        },
        "primaryType": "Mail",
        "domain": {
            "name": "Ether Mail",
            "version": "1",
            "chainId": 1,
            "verifyingContract": "0xCcCCccccCCCCcCCCCCCcCcCccCcCCCcCcccccccC",
        },
        "message": {
            "from": {"name": "Alice", "wallet": "0xCD2a3d9F938E13CD947Ec05AbC7FE734Df8DD826"},
            "to": {"name": "Bob", "wallet": "0xbBbBBBBbbBBBbbbBbbBbbbbBBbBbbbbBbBbbBBbB"},
            "contents": "Hello, Bob!",
        },
    }
    typed_data_message_hash = hash_typed_data_message(typed_data)
    assert (
        typed_data_message_hash
        == "0x4644890d40a2ebb8cbf599801c4412c03f8027f04044d0dd12a0605fbd72bb8b"
    )
