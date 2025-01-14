import os
import json
from decimal import Decimal
import pytest
import time

from cdp import Cdp
from cdp.wallet import Wallet, WalletData


@pytest.fixture(scope="module", autouse=True)
def configure_cdp():
    """Configure CDP once for all tests."""
    Cdp.configure(
        api_key_name=os.environ["CDP_API_KEY_NAME"],
        private_key=os.environ["CDP_API_PRIVATE_KEY"].replace("\\n", "\n")
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


class TestE2E:
    def test_env(self):
        """Test to ensure env."""
        assert "CDP_API_KEY_NAME" in os.environ
        assert "CDP_API_PRIVATE_KEY" in os.environ
        assert "WALLET_DATA" in os.environ

    # def test_wallet_create(self):
    #     """Test wallet creation."""
    #     wallet = Wallet.create()

    #     assert wallet is not None
    #     assert wallet.id is not None

    class TestWalletImport:
        @pytest.fixture(autouse=True)
        def setup(self, wallet_data):
            """Setup test environment before each test."""
            self.wallet_data = wallet_data

        def test_wallet_data_format(self):
            """Test wallet data format validation."""
            assert isinstance(self.wallet_data, dict)
            assert "wallet_id" in self.wallet_data
            assert "network_id" in self.wallet_data
            assert "seed" in self.wallet_data
            assert "default_address_id" in self.wallet_data

        def test_wallet_data_values(self):
            """Test wallet data required values."""
            wallet_id = self.wallet_data["wallet_id"]
            network_id = self.wallet_data["network_id"]
            seed = self.wallet_data["seed"]
            default_address_id = self.wallet_data["default_address_id"]

            assert wallet_id
            assert network_id
            assert seed
            assert default_address_id

        def test_wallet_import(self):
            """Test wallet import functionality."""
            wallet_id = self.wallet_data["wallet_id"]
            network_id = self.wallet_data["network_id"]
            default_address_id = self.wallet_data["default_address_id"]

            imported_wallet = Wallet.import_data(WalletData.from_dict(self.wallet_data))

            assert imported_wallet is not None
            assert imported_wallet.id == wallet_id
            assert imported_wallet.network_id == network_id
            assert imported_wallet.default_address is not None
            assert imported_wallet.default_address.address_id == default_address_id

    class TestWalletAddresses:
        @pytest.fixture(autouse=True)
        def setup(self, imported_wallet, wallet_data):
            """Setup wallet addresses tests."""
            self.wallet = imported_wallet
            self.wallet_data = wallet_data

        def test_wallet_default_address(self):
            """Test wallet addresses."""
            default_address_id = self.wallet_data["default_address_id"]

            assert self.wallet.default_address is not None
            assert self.wallet.default_address.address_id == default_address_id

        def test_wallet_addresses_list(self):
            """Test wallet addresses list."""
            addresses = self.wallet.addresses

            assert len(addresses) > 0
            assert self.wallet.default_address in addresses

    class TestWalletBalances:
        @pytest.fixture(autouse=True)
        def setup(self, imported_wallet):
            """Setup wallet balances tests."""
            self.wallet = imported_wallet

        def test_wallet_balances(self):
            """Test wallet balances."""
            assert self.wallet.balances() is not None

    class TestWalletFaucet:
        @pytest.fixture(autouse=True)
        def setup(self, imported_wallet):
            """Setup wallet faucet tests."""
            self.wallet = imported_wallet

        def test_wallet_faucet(self):
            """Test wallet transaction."""
            initial_balances = self.wallet.balances()
            initial_eth_balance = Decimal(str(initial_balances.get("eth", 0)))

            self.wallet.faucet()
            time.sleep(5)  # wait for balance to update

            final_balances = self.wallet.balances()
            final_eth_balance = Decimal(str(final_balances.get("eth", 0)))
            assert final_eth_balance > initial_eth_balance

        def test_wallet_faucet_usdc(self):
            """Test wallet transaction."""
            initial_balances = self.wallet.balances()
            initial_usdc_balance = Decimal(str(initial_balances.get("usdc", 0)))

            self.wallet.faucet(asset_id="usdc")
            time.sleep(5)  # wait for balance to update

            final_balances = self.wallet.balances()
            final_usdc_balance = Decimal(str(final_balances.get("usdc", 0)))
            assert final_usdc_balance > initial_usdc_balance

    class TestWalletExport:
        @pytest.fixture(autouse=True)
        def setup(self, imported_wallet):
            """Setup wallet export tests."""
            self.wallet = imported_wallet

        def test_wallet_export(self):
            """Test wallet export."""
            exported_wallet = self.wallet.export_data()
            assert exported_wallet.wallet_id is not None
            assert exported_wallet.seed is not None
            assert len(exported_wallet.seed) == 128

            self.wallet.save_seed_to_file("test_seed.json")
            assert os.path.exists("test_seed.json")

            saved_seed = json.loads(open("test_seed.json").read())
            assert saved_seed[exported_wallet.wallet_id] == {
                "seed": exported_wallet.seed,
                "encrypted": False,
                "auth_tag": "",
                "iv": "",
                "network_id": exported_wallet.network_id
            }

            os.unlink("test_seed.json")

    class TestWalletSeedFile:
        @pytest.fixture(autouse=True)
        def setup(self, imported_wallet, wallet_data):
            """Setup wallet seed file tests."""
            self.wallet = imported_wallet
            self.wallet_data = wallet_data

        def test_wallet_seed_file(self):
            """Test wallet seed file."""
            wallet_id = self.wallet_data["wallet_id"]
            wallet = Wallet.fetch(wallet_id)
            assert not wallet.can_sign

            self.wallet.save_seed_to_file("test_seed.json")
            assert os.path.exists("test_seed.json")

            wallet.load_seed_from_file("test_seed.json")
            assert wallet.can_sign
            assert wallet.id == wallet_id

            # cleanup
            os.unlink("test_seed.json")

    class TestWalletTransactions:
        @pytest.fixture(autouse=True)
        def setup(self, imported_wallet):
            """Setup wallet transaction tests."""
            self.wallet = imported_wallet

            # create a traceable transaction
            self.destination_wallet = Wallet.create()
            self.transfer = self.wallet.transfer(
                amount=Decimal("0.000000001"),
                asset_id="eth",
                destination=self.destination_wallet
            )
            self.transfer.wait()
            time.sleep(2)  # wait for transaction to be indexed

        def test_transaction_history(self):
            """Test transaction history retrieval."""
            # try up to 5 times to find our transaction
            for i in range(5):
                # get all transactions for this address
                transactions = list(self.wallet.default_address.transactions())

                if transactions:
                    # look for our specific transaction
                    matching_tx = None
                    for tx in transactions:
                        # match by from/to addresses and transaction hash
                        if (tx.from_address_id == self.wallet.default_address.address_id
                            and tx.to_address_id == self.destination_wallet.default_address.address_id
                                and tx.transaction_hash == self.transfer.transaction_hash):
                            matching_tx = tx
                            break

                    # if we found our transaction, verify its status
                    if matching_tx is not None:
                        assert matching_tx.status.value == "complete"
                        break
                else:
                    print(f"\nNo transactions found in attempt {i + 1}")

        def test_historical_balances(self):
            """Test historical balance retrieval."""
            balances = list(self.wallet.default_address.historical_balances("eth"))
            assert balances
            assert isinstance(balances[0].amount, (int, float, Decimal))

    class TestWalletTransfer:
        @pytest.fixture(autouse=True)
        def setup(self, imported_wallet):
            """Setup wallet transfer tests."""
            self.wallet = imported_wallet

        def test_wallet_transfer(self):
            """Test wallet transfer."""
            # create a new wallet to transfer to
            destination_wallet = Wallet.create()

            # get initial balances
            initial_source_balance = Decimal(str(self.wallet.balances().get("eth", 0)))
            initial_dest_balance = Decimal(str(destination_wallet.balances().get("eth", 0)))

            # transfer a small amount of ETH
            transfer = self.wallet.transfer(
                amount=Decimal("0.000000001"),
                asset_id="eth",
                destination=destination_wallet
            ).wait()
            time.sleep(2)  # wait for balances to update

            # verify transfer completed
            assert transfer is not None
            assert transfer.status.value == "complete"

            # verify balances changed
            final_source_balance = Decimal(str(self.wallet.balances().get("eth", 0)))
            final_dest_balance = Decimal(str(destination_wallet.balances().get("eth", 0)))

            assert final_source_balance < initial_source_balance
            assert final_dest_balance > initial_dest_balance
