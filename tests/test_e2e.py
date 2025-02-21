import json
import os
import time
from decimal import Decimal

import pytest
from dotenv import load_dotenv

from cdp import Cdp
from cdp.errors import FaucetLimitReachedError
from cdp.wallet import Wallet
from cdp.wallet_data import WalletData

load_dotenv()


@pytest.fixture(scope="module", autouse=True)
def configure_cdp():
    """Configure CDP once for all tests."""
    Cdp.configure(
        api_key_name=os.environ["CDP_API_KEY_NAME"],
        private_key=os.environ["CDP_API_KEY_PRIVATE_KEY"].replace("\\n", "\n"),
    )


@pytest.fixture(scope="module")
def wallet_data():
    """Load wallet data once for all tests."""
    wallet_data_str = os.environ.get("WALLET_DATA")
    return json.loads(wallet_data_str)


@pytest.fixture(scope="module")
def imported_wallet(wallet_data):
    """Create imported wallet once for all tests."""
    return Wallet.import_data(WalletData.from_dict(wallet_data))


@pytest.mark.e2e
def test_wallet_data(wallet_data):
    """Test wallet data format and required values."""
    expected = {
        "wallet_id": wallet_data["wallet_id"],
        "network_id": wallet_data["network_id"],
        "seed": wallet_data["seed"],
        "default_address_id": wallet_data["default_address_id"],
    }

    for key, value in expected.items():
        assert key in wallet_data
        assert value is not None


@pytest.mark.e2e
def test_wallet_import(wallet_data):
    """Test wallet import functionality."""
    wallet_id = wallet_data["wallet_id"]
    network_id = wallet_data["network_id"]
    default_address_id = wallet_data["default_address_id"]

    imported_wallet = Wallet.import_data(WalletData.from_dict(wallet_data))

    assert imported_wallet is not None
    assert imported_wallet.id == wallet_id
    assert imported_wallet.network_id == network_id
    assert imported_wallet.default_address is not None
    assert imported_wallet.default_address.address_id == default_address_id


@pytest.mark.e2e
def test_wallet_transfer(imported_wallet):
    """Test wallet transfer."""
    destination_wallet = Wallet.create()

    initial_source_balance = imported_wallet.balance("eth")
    initial_dest_balance = destination_wallet.balance("eth")

    if initial_source_balance < 0.0001:
        try:
            imported_wallet.faucet().wait()
        except FaucetLimitReachedError:
            print("Faucet limit reached, continuing...")

    transfer = imported_wallet.transfer(
        amount=Decimal("0.000000001"), asset_id="eth", destination=destination_wallet
    ).wait()

    assert transfer.status.value == "complete"

    final_source_balance = imported_wallet.balance("eth")
    final_dest_balance = destination_wallet.balance("eth")

    assert final_source_balance < initial_source_balance
    assert final_dest_balance > initial_dest_balance


# CDPSDK-265: Flaky test
@pytest.mark.skip(reason="Flaky test")
def test_transaction_history(imported_wallet):
    """Test transaction history retrieval."""
    destination_wallet = Wallet.create()

    initial_source_balance = imported_wallet.balance("eth")
    if initial_source_balance < 0.0001:
        try:
            imported_wallet.faucet().wait()
        except FaucetLimitReachedError:
            print("Faucet limit reached, continuing...")

    transfer = imported_wallet.transfer(
        amount=Decimal("0.000000001"), asset_id="eth", destination=destination_wallet
    ).wait()

    time.sleep(10)

    transactions = imported_wallet.default_address.transactions()
    matching_tx = None

    for tx in transactions:
        if tx.transaction_hash == transfer.transaction_hash:
            matching_tx = tx
            break

    assert matching_tx is not None
    assert matching_tx.status.value == "complete"


@pytest.mark.e2e
def test_wallet_export(imported_wallet):
    """Test wallet export."""
    exported_wallet = imported_wallet.export_data()
    assert exported_wallet.wallet_id is not None
    assert exported_wallet.seed is not None
    assert len(exported_wallet.seed) == 128

    imported_wallet.save_seed_to_file("test_seed.json")
    assert os.path.exists("test_seed.json")

    with open("test_seed.json") as f:
        saved_seed = json.loads(f.read())

    assert saved_seed[exported_wallet.wallet_id] == {
        "seed": exported_wallet.seed,
        "encrypted": False,
        "auth_tag": "",
        "iv": "",
        "network_id": exported_wallet.network_id,
    }

    os.unlink("test_seed.json")


@pytest.mark.e2e
def test_wallet_addresses(imported_wallet):
    """Test wallet addresses retrieval."""
    addresses = imported_wallet.addresses
    assert addresses
    assert imported_wallet.default_address in addresses


@pytest.mark.e2e
def test_wallet_balances(imported_wallet):
    """Test wallet balances retrieval."""
    balances = imported_wallet.balances()
    assert balances.get("eth") > 0


@pytest.mark.e2e
def test_historical_balances(imported_wallet):
    """Test historical balance retrieval."""
    balances = list(imported_wallet.default_address.historical_balances("eth"))
    assert balances
    assert all(balance.amount > 0 for balance in balances)


# CDPSDK-265: Flaky test
@pytest.mark.skip(reason="Faucet can be unstable")
def test_invoke_contract_with_transaction_receipt(imported_wallet):
    """Test invoke contract with transaction receipt."""
    destination_wallet = Wallet.create()

    faucet_transaction = imported_wallet.faucet("usdc")
    faucet_transaction.wait()

    # Transfer 0.000001 USDC to the destination address.
    invocation = imported_wallet.invoke_contract(
        contract_address="0x036CbD53842c5426634e7929541eC2318f3dCF7e",
        method="transfer",
        args={"to": destination_wallet.default_address.address_id, "value": "1"},
    )

    invocation.wait()

    transaction_content = invocation.transaction.content.actual_instance
    transaction_receipt = transaction_content.receipt

    assert transaction_receipt.status == 1

    transaction_logs = transaction_receipt.logs
    assert len(transaction_logs) == 1

    transaction_log = transaction_logs[0]
    assert transaction_log.address == "0x036CbD53842c5426634e7929541eC2318f3dCF7e"
    assert transaction_log.topics[0] == "Transfer"
    assert transaction_log.topics[1] == f"from: {imported_wallet.default_address.address_id}"
    assert transaction_log.topics[2] == f"to: {destination_wallet.default_address.address_id}"


@pytest.mark.skip(reason="Gasless transfers have unpredictable latency")
def test_gasless_transfer(imported_wallet):
    """Test gasless transfer."""
    destination_wallet = Wallet.create()

    initial_source_balance = imported_wallet.balance("usdc")
    initial_dest_balance = destination_wallet.balance("usdc")

    transfer = imported_wallet.transfer(
        amount=Decimal("0.000001"), asset_id="usdc", gasless=True, destination=destination_wallet
    ).wait()

    time.sleep(20)

    assert transfer.status.value == "complete"

    final_source_balance = imported_wallet.balance("usdc")
    final_dest_balance = destination_wallet.balance("usdc")

    assert final_source_balance < initial_source_balance
    assert final_dest_balance > initial_dest_balance
    assert final_dest_balance == Decimal("0.000001")
