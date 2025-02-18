from decimal import Decimal

from eth_account import Account
from web3 import Web3

from cdp.cdp import Cdp
from cdp.evm_call_types import EVMCallDict
from cdp.external_address import ExternalAddress
from cdp.smart_wallet import SmartWallet, to_smart_wallet
from cdp.wallet import Wallet

Cdp.configure_from_json(
    file_path="~/.apikeys/dev.json",
    debugging=False,
    base_path="https://cloud-api-dev.cbhq.net/platform/",
)


def test_smart_wallet_operations():
    # Create a smart wallet with a new account as owner
    private_key = Account.create().key
    owner = Account.from_key(private_key)
    smart_wallet = SmartWallet.create(account=owner)

    # Create an external address
    external_address = ExternalAddress("base-sepolia", smart_wallet.address)

    print(f"External address: {external_address}")

    # Faucet the smart wallet using External Address
    faucet_tx = external_address.faucet()
    faucet_tx.wait()

    print(f"Faucet transaction: {faucet_tx}")

    # Create a wallet address to send to
    wallet = Wallet.create()
    wallet_address = wallet.default_address.address_id

    print(f"Wallet address: {wallet_address}")

    # Send first user operation
    value_in_wei = Web3.to_wei(Decimal("0.0000005"), "ether")

    print("Sending user operation")
    user_operation = smart_wallet.send_user_operation(
        calls=[
            EVMCallDict(
                to=wallet_address,
                value=value_in_wei,
                data="0x"
            )
        ],
        chain_id=84532,
        paymaster_url=None  # Optional paymaster URL if needed
    )

    print(f"User operation: {user_operation}")

    # Wait for the operation to complete
    user_operation.wait(
        interval_seconds=0.2,
        timeout_seconds=20
    )

    # Check operation status
    if user_operation.status == "failed":
        print("Operation failed")
    else:
        print(f"Transaction hash: {user_operation.transaction_hash}")

    # Use network-scoped smart wallet
    network_scoped_wallet = smart_wallet.use_network(chain_id=84532)

    print(f"Network scoped wallet: {network_scoped_wallet}")

    # Send second user operation through network-scoped wallet
    user_operation2 = network_scoped_wallet.send_user_operation(
        calls=[EVMCallDict(to=wallet_address, value=value_in_wei, data="0x")]
    )

    print(f"User operation 2: {user_operation2}")

    # Wait for the second operation with custom timeout
    user_operation2.wait(interval_seconds=1, timeout_seconds=10000)

    print(f"User operation 2 status: {user_operation2.status}")

    # Check operation status
    if user_operation2.status == "failed":
        print("Operation failed")
    else:
        print(f"Transaction hash: {user_operation2.transaction_hash}")

    # Get final balance
    final_balance = wallet.balance("eth")
    print(f"Final balance: {final_balance}")
    
    # Reconstructing the smart wallet using to_smart_wallet
    smart_wallet_2 = to_smart_wallet(smart_wallet.address, owner)
    print(f"Smart wallet: {smart_wallet_2}")


if __name__ == "__main__":
    test_smart_wallet_operations()
