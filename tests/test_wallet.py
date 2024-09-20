from decimal import Decimal
from unittest.mock import ANY, Mock, PropertyMock, call, patch

import pytest
from bip_utils import Bip32Slip10Secp256k1
from eth_account import Account

from cdp.client.models.address import Address as AddressModel
from cdp.client.models.create_address_request import CreateAddressRequest
from cdp.client.models.create_wallet_request import CreateWalletRequest, CreateWalletRequestWallet
from cdp.client.models.feature_set import FeatureSet
from cdp.client.models.wallet import Wallet as WalletModel
from cdp.trade import Trade
from cdp.transfer import Transfer
from cdp.wallet import Wallet
from cdp.wallet_address import WalletAddress


@pytest.fixture
def address_model_factory():
    """Create and return a factory for AddressModel fixtures."""

    def _create_address_model(
        network_id="base-sepolia",
        address_id="0x1234567890123456789012345678901234567890",
        wallet_id="test-wallet-id",
        public_key="0xpublickey",
        index=0,
    ):
        return AddressModel(
            network_id=network_id,
            address_id=address_id,
            wallet_id=wallet_id,
            public_key=public_key,
            index=index,
        )

    return _create_address_model


@pytest.fixture
def wallet_model_factory(address_model_factory):
    """Create and return a factory for WalletModel fixtures."""

    def _create_wallet_model(
        id="test-wallet-id",
        network_id="base-sepolia",
        default_address=None,
        feature_set=None,
        server_signer_status="active_seed",
    ):
        if default_address is None:
            default_address = address_model_factory()
        if feature_set is None:
            feature_set = FeatureSet(
                faucet=True,
                server_signer=True,
                transfer=True,
                trade=True,
                stake=True,
                gasless_send=True,
            )
        return WalletModel(
            id=id,
            network_id=network_id,
            default_address=default_address,
            feature_set=feature_set,
            server_signer_status=server_signer_status,
        )

    return _create_wallet_model


@pytest.fixture
def master_key_factory():
    """Create and return a factory for master key fixtures."""

    def _create_master_key(seed=b"\x00" * 64):
        return Bip32Slip10Secp256k1.FromSeed(seed)

    return _create_master_key


@pytest.fixture
def wallet_factory(wallet_model_factory):
    """Create and return a factory for Wallet fixtures."""

    def _create_wallet(seed=None, **kwargs):
        model = wallet_model_factory(**kwargs)
        return Wallet(model, seed)

    return _create_wallet


@pytest.fixture
def wallet_address_factory(address_model_factory):
    """Create and return a factory for WalletAddress fixtures."""

    def _create_wallet_address(key=None, **kwargs):
        model = address_model_factory(**kwargs)
        return WalletAddress(model, key)

    return _create_wallet_address


@patch("cdp.Cdp.use_server_signer", False)
@patch("cdp.wallet.os")
@patch("cdp.wallet.Bip32Slip10Secp256k1")
def test_wallet_initialization(mock_bip32, mock_os, wallet_factory, master_key_factory):
    """Test Wallet initialization."""
    seed = b"\x00" * 64
    mock_urandom = Mock(return_value=seed)
    mock_os.urandom = mock_urandom
    mock_from_seed = Mock(return_value=master_key_factory(seed))
    mock_bip32.FromSeed = mock_from_seed

    wallet = wallet_factory()

    mock_urandom.assert_called_once_with(64)
    mock_from_seed.assert_called_once_with(seed)
    assert wallet.id == "test-wallet-id"
    assert wallet.network_id == "base-sepolia"
    assert wallet._seed == seed.hex()
    assert wallet.can_sign


@patch("cdp.Cdp.use_server_signer", True)
def test_wallet_initialization_with_server_signer(wallet_factory):
    """Test Wallet initialization with server-signer."""
    wallet = wallet_factory()

    assert wallet.id == "test-wallet-id"
    assert wallet.network_id == "base-sepolia"
    assert wallet.server_signer_status == "active_seed"
    assert wallet._seed is None
    assert not wallet.can_sign


@patch("cdp.Cdp.use_server_signer", False)
@patch("cdp.wallet.Account")
@patch("cdp.wallet.Bip32Slip10Secp256k1")
@patch("cdp.Cdp.api_clients")
def test_wallet_addresses(
    mock_api_clients, mock_bip32, mock_account, wallet_factory, address_model_factory
):
    """Test Wallet addresses method."""
    wallet = wallet_factory()
    mock_list_addresses = Mock()
    mock_list_addresses.return_value.data = [
        address_model_factory(address_id="0x1234"),
        address_model_factory(address_id="0x5678"),
    ]
    mock_api_clients.addresses.list_addresses = mock_list_addresses

    mock_from_key = Mock(
        side_effect=[Mock(spec=Account, address="0x1234"), Mock(spec=Account, address="0x5678")]
    )
    mock_account.from_key = mock_from_key

    mock_derive_path = Mock(spec=Bip32Slip10Secp256k1)
    mock_bip32.DerivePath = mock_derive_path

    addresses = wallet.addresses

    assert len(addresses) == 2
    assert all(isinstance(addr, WalletAddress) for addr in addresses)
    assert addresses[0].address_id == "0x1234"
    assert addresses[1].address_id == "0x5678"


@patch("cdp.Cdp.use_server_signer", True)
@patch("cdp.Cdp.api_clients")
def test_wallet_addresses_with_server_signer(
    mock_api_clients, wallet_factory, address_model_factory
):
    """Test Wallet addresses method with server-signer."""
    wallet = wallet_factory()
    mock_list_addresses = Mock()
    mock_list_addresses.return_value.data = [
        address_model_factory(address_id="0x1234"),
        address_model_factory(address_id="0x5678"),
    ]
    mock_api_clients.addresses.list_addresses = mock_list_addresses

    addresses = wallet.addresses

    assert len(addresses) == 2
    assert all(isinstance(addr, WalletAddress) for addr in addresses)
    assert addresses[0].address_id == "0x1234"
    assert addresses[1].address_id == "0x5678"


@patch("cdp.Cdp.use_server_signer", False)
@patch("cdp.Cdp.api_clients")
@patch("cdp.wallet.Bip32Slip10Secp256k1")
@patch("cdp.wallet.Account")
@patch("cdp.wallet.os")
@patch("cdp.wallet.coincurve.PrivateKey")
def test_wallet_create(
    mock_coincurve_private_key,
    mock_os,
    mock_account,
    mock_bip32,
    mock_api_clients,
    wallet_model_factory,
    address_model_factory,
    master_key_factory,
):
    """Test Wallet create method with server-signer."""
    mock_create_wallet = Mock(return_value=wallet_model_factory(id="new-wallet-id"))
    mock_api_clients.wallets.create_wallet = mock_create_wallet

    mock_get_wallet = Mock(return_value=wallet_model_factory(id="new-wallet-id"))
    mock_api_clients.wallets.get_wallet = mock_get_wallet

    seed = b"\x00" * 64
    mock_urandom = Mock(return_value=seed)
    mock_os.urandom = mock_urandom

    mock_master_key = master_key_factory(seed)
    mock_from_seed = Mock(return_value=mock_master_key)
    mock_bip32.FromSeed = mock_from_seed

    mock_create_address = Mock(return_value=address_model_factory(address_id="0xnewaddress"))
    mock_api_clients.addresses.create_address = mock_create_address

    mock_account_instance = Mock(spec=Account, address="0xnewaddress")
    mock_from_key = Mock(return_value=mock_account_instance)
    mock_account.from_key = mock_from_key

    mock_derive_path = Mock(
        return_value=Mock(
            PrivateKey=Mock(
                return_value=Mock(
                    Raw=Mock(
                        return_value=Mock(
                            ToHex=Mock(return_value="mock_private_key_hex"),
                            ToBytes=Mock(return_value=b"mock_private_key_bytes"),
                        )
                    )
                )
            ),
            PublicKey=Mock(
                return_value=Mock(
                    RawCompressed=Mock(
                        return_value=Mock(ToHex=Mock(return_value="mock_public_key_hex"))
                    )
                )
            ),
        )
    )
    mock_master_key.DerivePath = mock_derive_path

    # Mock for coincurve.PrivateKey
    mock_coincurve_private_key_instance = Mock()
    mock_coincurve_private_key_instance.sign_recoverable.return_value = b"\x00" * 65
    mock_coincurve_private_key.return_value = mock_coincurve_private_key_instance

    new_wallet = Wallet.create()

    assert isinstance(new_wallet, Wallet)
    assert new_wallet.id == "new-wallet-id"
    assert new_wallet._seed == seed.hex()
    mock_create_wallet.assert_called_once_with(
        CreateWalletRequest(
            wallet=CreateWalletRequestWallet(network_id="base-sepolia", use_server_signer=False)
        )
    )

    mock_urandom.assert_called_once_with(64)
    mock_from_seed.assert_called_once_with(seed)
    mock_derive_path.assert_has_calls([call("m/44'/60'/0'/0/0"), call("m/44'/60'/0'/0/0")])
    mock_from_key.assert_called_once_with("mock_private_key_hex")

    # Check that coincurve.PrivateKey was called correctly
    assert mock_coincurve_private_key.call_count == 3
    mock_coincurve_private_key.assert_any_call(b"mock_private_key_bytes")
    mock_coincurve_private_key_instance.sign_recoverable.assert_called_once_with(
        b'{"wallet_id":"new-wallet-id","public_key":"mock_public_key_hex"}'
    )

    # Check that create_address was called with the correct arguments
    mock_create_address.assert_called_once_with(
        wallet_id="new-wallet-id", create_address_request=ANY
    )
    create_address_request = mock_create_address.call_args[1]["create_address_request"]
    assert create_address_request.public_key == "mock_public_key_hex"
    assert create_address_request.address_index == 0
    assert len(create_address_request.attestation) == 130  # 65 bytes * 2 for hex

    mock_get_wallet.assert_called_once_with("new-wallet-id")


@patch("cdp.Cdp.use_server_signer", True)
@patch("cdp.Cdp.api_clients")
def test_wallet_create_with_server_signer(
    mock_api_clients, wallet_model_factory, address_model_factory
):
    """Test Wallet create method with server-signer."""
    mock_create_wallet = Mock(return_value=wallet_model_factory(id="new-wallet-id"))
    mock_api_clients.wallets.create_wallet = mock_create_wallet

    mock_get_wallet = Mock(return_value=wallet_model_factory(id="new-wallet-id"))
    mock_api_clients.wallets.get_wallet = mock_get_wallet

    mock_create_address = Mock(return_value=address_model_factory(address_id="0xnewaddress"))
    mock_api_clients.addresses.create_address = mock_create_address

    new_wallet = Wallet.create()

    assert isinstance(new_wallet, Wallet)
    assert new_wallet.id == "new-wallet-id"
    mock_create_wallet.assert_called_once_with(
        CreateWalletRequest(
            wallet=CreateWalletRequestWallet(network_id="base-sepolia", use_server_signer=True)
        )
    )

    mock_create_address.assert_called_once_with(
        wallet_id="new-wallet-id", create_address_request=CreateAddressRequest()
    )

    mock_get_wallet.assert_called_once_with("new-wallet-id")


@patch("cdp.Cdp.use_server_signer", True)
@patch("cdp.Cdp.api_clients")
def test_wallet_create_address_with_server_signer(
    mock_api_clients, wallet_factory, address_model_factory
):
    """Test Wallet create_address method with server-signer."""
    wallet = wallet_factory()
    mock_default_address = Mock(spec=WalletAddress)
    mock_create_address = Mock(return_value=address_model_factory(address_id="0xnewaddress"))
    mock_api_clients.addresses.create_address = mock_create_address

    with patch.object(
        Wallet, "default_address", new_callable=PropertyMock
    ) as mock_default_address_prop:
        mock_default_address_prop.return_value = mock_default_address

        new_address = wallet.create_address()

        assert isinstance(new_address, WalletAddress)
        assert new_address.address_id == "0xnewaddress"
        mock_create_address.assert_called_once_with(
            wallet_id=wallet.id, create_address_request=CreateAddressRequest()
        )


@patch("cdp.Cdp.use_server_signer", True)
def test_wallet_trade_with_server_signer(wallet_factory):
    """Test Wallet trade method with server-signer."""
    wallet = wallet_factory()
    mock_default_address = Mock(spec=WalletAddress)
    mock_trade_instance = Mock(spec=Trade)
    mock_default_address.trade.return_value = mock_trade_instance

    with patch.object(
        Wallet, "default_address", new_callable=PropertyMock
    ) as mock_default_address_prop:
        mock_default_address_prop.return_value = mock_default_address

        trade = wallet.trade(amount=Decimal("1.0"), from_asset_id="eth", to_asset_id="usdc")

        assert isinstance(trade, Trade)
        mock_default_address.trade.assert_called_once_with(Decimal("1.0"), "eth", "usdc")


@patch("cdp.Cdp.use_server_signer", True)
def test_wallet_trade_no_default_address(wallet_factory):
    """Test Wallet trade method with no default address."""
    wallet = wallet_factory()

    with patch.object(
        Wallet, "default_address", new_callable=PropertyMock
    ) as mock_default_address_prop:
        mock_default_address_prop.return_value = None

        with pytest.raises(ValueError, match="Default address does not exist"):
            wallet.trade(amount=Decimal("1.0"), from_asset_id="eth", to_asset_id="usdc")


@patch("cdp.Cdp.use_server_signer", True)
def test_wallet_transfer_with_server_signer(wallet_factory):
    """Test the transfer method of a Wallet with server-signer."""
    wallet = wallet_factory()
    mock_default_address = Mock(spec=WalletAddress)
    mock_transfer_instance = Mock(spec=Transfer)
    mock_default_address.transfer.return_value = mock_transfer_instance

    with patch.object(
        Wallet, "default_address", new_callable=PropertyMock
    ) as mock_default_address_prop:
        mock_default_address_prop.return_value = mock_default_address

        transfer = wallet.transfer(
            amount=Decimal("1.0"), asset_id="eth", destination="0xdestination", gasless=False
        )

        assert isinstance(transfer, Transfer)
        mock_default_address.transfer.assert_called_once_with(
            Decimal("1.0"), "eth", "0xdestination", False
        )


@patch("cdp.Cdp.use_server_signer", True)
def test_wallet_transfer_no_default_address(wallet_factory):
    """Test the transfer method of a Wallet with no default address."""
    wallet = wallet_factory()

    with patch.object(
        Wallet, "default_address", new_callable=PropertyMock
    ) as mock_default_address_prop:
        mock_default_address_prop.return_value = None

        with pytest.raises(ValueError, match="Default address does not exist"):
            wallet.transfer(
                amount=Decimal("1.0"), asset_id="eth", destination="0xdestination", gasless=False
            )


@patch("cdp.Cdp.api_clients")
def test_wallet_reload(mock_api_clients, wallet_factory):
    """Test the reload method of a Wallet."""
    wallet = wallet_factory(server_signer_status="pending_seed_creation")
    mock_get_wallet = Mock()
    mock_get_wallet.return_value = wallet_factory(server_signer_status="active_seed")._model
    mock_api_clients.wallets.get_wallet = mock_get_wallet

    wallet.reload()

    assert wallet.server_signer_status == "active_seed"
    mock_get_wallet.assert_called_once_with(wallet.id)


@patch("cdp.Cdp.api_clients")
def test_wallet_fetch(mock_api_clients, wallet_factory):
    """Test the fetch method of a Wallet."""
    mock_get_wallet = Mock()
    mock_get_wallet.return_value = wallet_factory(id="fetched-wallet-id")._model
    mock_api_clients.wallets.get_wallet = mock_get_wallet

    fetched_wallet = Wallet.fetch("fetched-wallet-id")

    assert isinstance(fetched_wallet, Wallet)
    assert fetched_wallet.id == "fetched-wallet-id"
    mock_get_wallet.assert_called_once_with("fetched-wallet-id")
