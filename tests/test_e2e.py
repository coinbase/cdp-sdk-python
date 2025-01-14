import json
import os
import time
from decimal import Decimal

import pytest
from dotenv import load_dotenv

from cdp import Cdp
from cdp.wallet import Wallet
from cdp.wallet_data import WalletData

load_dotenv()


@pytest.fixture(scope="module", autouse=True)
def configure_cdp():
    """Configure CDP once for all tests."""
    Cdp.configure(
        api_key_name=os.environ["CDP_API_KEY_NAME"],
        private_key=os.environ["CDP_API_PRIVATE_KEY"].replace("\\n", "\n"),
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


def test_wallet_data(wallet_data):
    """Test wallet data format and required values."""
    expected = {
        "wallet_id": wallet_data["wallet_id"],
        "network_id": wallet_data["network_id"],
        "seed": wallet_data["seed"],
        "default_address_id": wallet_data["default_address_id"]
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
def test_wallet_faucet(imported_wallet):
    """Test wallet faucet with ETH."""
    initial_balances = imported_wallet.balances()
    initial_eth_balance = Decimal(str(initial_balances.get("eth", 0)))

    imported_wallet.faucet().wait()
    time.sleep(1)

    final_balances = imported_wallet.balances()
    final_eth_balance = Decimal(str(final_balances.get("eth", 0)))
    assert final_eth_balance > initial_eth_balance


@pytest.mark.e2e
def test_wallet_faucet_usdc(imported_wallet):
    """Test wallet faucet with USDC."""
    initial_balances = imported_wallet.balances()
    initial_usdc_balance = Decimal(str(initial_balances.get("usdc", 0)))

    imported_wallet.faucet(asset_id="usdc").wait()
    time.sleep(1)

    final_balances = imported_wallet.balances()
    final_usdc_balance = Decimal(str(final_balances.get("usdc", 0)))
    assert final_usdc_balance > initial_usdc_balance


@pytest.mark.e2e
def test_wallet_transfer(imported_wallet):
    """Test wallet transfer."""
    destination_wallet = Wallet.create()

    initial_source_balance = Decimal(str(imported_wallet.balances().get("eth", 0)))
    initial_dest_balance = Decimal(str(destination_wallet.balances().get("eth", 0)))

    transfer = imported_wallet.transfer(
        amount=Decimal("0.000000001"),
        asset_id="eth",
        destination=destination_wallet
    )

    transfer.wait()

    assert transfer is not None
    assert transfer.status.value == "complete"

    final_source_balance = Decimal(str(imported_wallet.balances().get("eth", 0)))
    final_dest_balance = Decimal(str(destination_wallet.balances().get("eth", 0)))

    assert final_source_balance < initial_source_balance
    assert final_dest_balance > initial_dest_balance


@pytest.mark.e2e
def test_transaction_history(imported_wallet):
    """Test transaction history retrieval."""
    # create a transaction
    destination_wallet = Wallet.create()
    transfer = imported_wallet.transfer(
        amount=Decimal("0.000000001"),
        asset_id="eth",
        destination=destination_wallet
    ).wait()

    print(f"transfer: {transfer.transaction_hash}")
    time.sleep(10)  # wait for the transaction to be indexed

    transactions = imported_wallet.default_address.transactions()
    matching_tx = None

    # look for our specific transaction
    for tx in transactions:
        if tx.transaction_hash == transfer.transaction_hash:
            matching_tx = tx
            break

    # verify that we found the transaction and it is complete
    assert matching_tx is not None
    assert matching_tx.status.value == "complete"


@pytest.mark.e2e
def test_wallet_export(imported_wallet):
    """Test wallet export."""
    exported_wallet = imported_wallet.export_data()
    assert exported_wallet.wallet_id is not None
    assert exported_wallet.seed is not None
    assert len(exported_wallet.seed) == 128

    # test seed file creation and format
    imported_wallet.save_seed_to_file("test_seed.json")
    assert os.path.exists("test_seed.json")

    # verify seed file contents
    with open("test_seed.json") as f:
        saved_seed = json.loads(f.read())

    assert saved_seed[exported_wallet.wallet_id] == {
        "seed": exported_wallet.seed,
        "encrypted": False,
        "auth_tag": "",
        "iv": "",
        "network_id": exported_wallet.network_id
    }

    # cleanup
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
