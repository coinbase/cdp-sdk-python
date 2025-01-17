from decimal import Decimal
from unittest.mock import ANY, Mock, PropertyMock, call, patch

import pytest
from eth_account import Account

from cdp.client.models.create_address_request import CreateAddressRequest
from cdp.client.models.create_wallet_request import CreateWalletRequest, CreateWalletRequestWallet
from cdp.client.models.create_wallet_webhook_request import CreateWalletWebhookRequest
from cdp.contract_invocation import ContractInvocation
from cdp.fund_operation import FundOperation
from cdp.fund_quote import FundQuote
from cdp.payload_signature import PayloadSignature
from cdp.smart_contract import SmartContract
from cdp.trade import Trade
from cdp.transfer import Transfer
from cdp.wallet import Wallet
from cdp.wallet_address import WalletAddress
from cdp.webhook import Webhook


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
            Decimal("1.0"), "eth", "0xdestination", False, False
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


@patch("cdp.Cdp.use_server_signer", True)
def test_wallet_invoke_contract_with_server_signer(wallet_factory):
    """Test the invoke_contract method of a Wallet with server-signer."""
    wallet = wallet_factory()
    mock_default_address = Mock(spec=WalletAddress)
    mock_contract_invocation_instance = Mock(spec=ContractInvocation)
    mock_default_address.invoke_contract.return_value = mock_contract_invocation_instance

    with patch.object(
        Wallet, "default_address", new_callable=PropertyMock
    ) as mock_default_address_prop:
        mock_default_address_prop.return_value = mock_default_address

        contract_invocation = wallet.invoke_contract(
            contract_address="0xcontractaddress",
            method="testMethod",
            abi=[{"abi": "data"}],
            args={"arg1": "value1"},
            amount=Decimal("1"),
            asset_id="wei",
        )

        assert isinstance(contract_invocation, ContractInvocation)
        mock_default_address.invoke_contract.assert_called_once_with(
            "0xcontractaddress",
            "testMethod",
            [{"abi": "data"}],
            {"arg1": "value1"},
            Decimal("1"),
            "wei",
        )


@patch("cdp.Cdp.use_server_signer", True)
def test_wallet_contract_invocation_no_default_address(wallet_factory):
    """Test the invoke_contract method of a Wallet with no default address."""
    wallet = wallet_factory()

    with patch.object(
        Wallet, "default_address", new_callable=PropertyMock
    ) as mock_default_address_prop:
        mock_default_address_prop.return_value = None

        with pytest.raises(ValueError, match="Default address does not exist"):
            wallet.invoke_contract(
                contract_address="0xcontractaddress",
                method="testMethod",
                abi=[{"abi": "data"}],
                args={"arg1": "value1"},
                amount=Decimal("1"),
                asset_id="wei",
            )


@patch("cdp.Cdp.use_server_signer", True)
def test_wallet_sign_payload_with_server_signer(wallet_factory):
    """Test the sign_payload method of a Wallet with server-signer."""
    wallet = wallet_factory()
    mock_default_address = Mock(spec=WalletAddress)
    mock_payload_signature_instance = Mock(spec=PayloadSignature)
    mock_default_address.sign_payload.return_value = mock_payload_signature_instance

    with patch.object(
        Wallet, "default_address", new_callable=PropertyMock
    ) as mock_default_address_prop:
        mock_default_address_prop.return_value = mock_default_address

        payload_signature = wallet.sign_payload(unsigned_payload="0xunsignedpayload")

        assert isinstance(payload_signature, PayloadSignature)
        mock_default_address.sign_payload.assert_called_once_with("0xunsignedpayload")


@patch("cdp.Cdp.use_server_signer", True)
def test_wallet_sign_payload_no_default_address(wallet_factory):
    """Test the sign_payload method of a Wallet with no default address."""
    wallet = wallet_factory()

    with patch.object(
        Wallet, "default_address", new_callable=PropertyMock
    ) as mock_default_address_prop:
        mock_default_address_prop.return_value = None

        with pytest.raises(ValueError, match="Default address does not exist"):
            wallet.sign_payload(unsigned_payload="0xunsignedpayload")


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


@patch("cdp.Cdp.use_server_signer", True)
def test_wallet_deploy_token(wallet_factory):
    """Test the deploy_token method of a Wallet."""
    wallet = wallet_factory()
    mock_default_address = Mock(spec=WalletAddress)
    mock_smart_contract = Mock(spec=SmartContract)
    mock_default_address.deploy_token.return_value = mock_smart_contract

    with patch.object(
        Wallet, "default_address", new_callable=PropertyMock
    ) as mock_default_address_prop:
        mock_default_address_prop.return_value = mock_default_address

        smart_contract = wallet.deploy_token(name="TestToken", symbol="TT", total_supply="1000000")

        assert isinstance(smart_contract, SmartContract)
        mock_default_address.deploy_token.assert_called_once_with("TestToken", "TT", "1000000")


@patch("cdp.Cdp.use_server_signer", True)
def test_wallet_deploy_nft(wallet_factory):
    """Test the deploy_nft method of a Wallet."""
    wallet = wallet_factory()
    mock_default_address = Mock(spec=WalletAddress)
    mock_smart_contract = Mock(spec=SmartContract)
    mock_default_address.deploy_nft.return_value = mock_smart_contract

    with patch.object(
        Wallet, "default_address", new_callable=PropertyMock
    ) as mock_default_address_prop:
        mock_default_address_prop.return_value = mock_default_address

        smart_contract = wallet.deploy_nft(
            name="TestNFT", symbol="TNFT", base_uri="https://example.com/nft/"
        )

        assert isinstance(smart_contract, SmartContract)
        mock_default_address.deploy_nft.assert_called_once_with(
            "TestNFT", "TNFT", "https://example.com/nft/"
        )


@patch("cdp.Cdp.use_server_signer", True)
def test_wallet_deploy_multi_token(wallet_factory):
    """Test the deploy_multi_token method of a Wallet."""
    wallet = wallet_factory()
    mock_default_address = Mock(spec=WalletAddress)
    mock_smart_contract = Mock(spec=SmartContract)
    mock_default_address.deploy_multi_token.return_value = mock_smart_contract

    with patch.object(
        Wallet, "default_address", new_callable=PropertyMock
    ) as mock_default_address_prop:
        mock_default_address_prop.return_value = mock_default_address

        smart_contract = wallet.deploy_multi_token(uri="https://example.com/multi-token/{id}.json")

        assert isinstance(smart_contract, SmartContract)
        mock_default_address.deploy_multi_token.assert_called_once_with(
            "https://example.com/multi-token/{id}.json"
        )


@patch("cdp.Cdp.use_server_signer", True)
def test_wallet_deploy_token_no_default_address(wallet_factory):
    """Test the deploy_token method of a Wallet with no default address."""
    wallet = wallet_factory()

    with patch.object(
        Wallet, "default_address", new_callable=PropertyMock
    ) as mock_default_address_prop:
        mock_default_address_prop.return_value = None

        with pytest.raises(ValueError, match="Default address does not exist"):
            wallet.deploy_token(name="TestToken", symbol="TT", total_supply="1000000")


@patch("cdp.Cdp.use_server_signer", True)
def test_wallet_deploy_nft_no_default_address(wallet_factory):
    """Test the deploy_nft method of a Wallet with no default address."""
    wallet = wallet_factory()

    with patch.object(
        Wallet, "default_address", new_callable=PropertyMock
    ) as mock_default_address_prop:
        mock_default_address_prop.return_value = None

        with pytest.raises(ValueError, match="Default address does not exist"):
            wallet.deploy_nft(name="TestNFT", symbol="TNFT", base_uri="https://example.com/nft/")


@patch("cdp.Cdp.use_server_signer", True)
def test_wallet_deploy_multi_token_no_default_address(wallet_factory):
    """Test the deploy_multi_token method of a Wallet with no default address."""
    wallet = wallet_factory()

    with patch.object(
        Wallet, "default_address", new_callable=PropertyMock
    ) as mock_default_address_prop:
        mock_default_address_prop.return_value = None

        with pytest.raises(ValueError, match="Default address does not exist"):
            wallet.deploy_multi_token(uri="https://example.com/multi-token/{id}.json")


@patch("cdp.Cdp.use_server_signer", True)
def test_wallet_deploy_token_with_server_signer(wallet_factory):
    """Test the deploy_token method of a Wallet with server-signer."""
    wallet = wallet_factory()
    mock_default_address = Mock(spec=WalletAddress)
    mock_smart_contract = Mock(spec=SmartContract)
    mock_default_address.deploy_token.return_value = mock_smart_contract

    with patch.object(
        Wallet, "default_address", new_callable=PropertyMock
    ) as mock_default_address_prop:
        mock_default_address_prop.return_value = mock_default_address

        smart_contract = wallet.deploy_token(name="TestToken", symbol="TT", total_supply="1000000")

        assert isinstance(smart_contract, SmartContract)
        mock_default_address.deploy_token.assert_called_once_with("TestToken", "TT", "1000000")


@patch("cdp.Cdp.use_server_signer", True)
def test_wallet_deploy_nft_with_server_signer(wallet_factory):
    """Test the deploy_nft method of a Wallet with server-signer."""
    wallet = wallet_factory()
    mock_default_address = Mock(spec=WalletAddress)
    mock_smart_contract = Mock(spec=SmartContract)
    mock_default_address.deploy_nft.return_value = mock_smart_contract

    with patch.object(
        Wallet, "default_address", new_callable=PropertyMock
    ) as mock_default_address_prop:
        mock_default_address_prop.return_value = mock_default_address

        smart_contract = wallet.deploy_nft(
            name="TestNFT", symbol="TNFT", base_uri="https://example.com/nft/"
        )

        assert isinstance(smart_contract, SmartContract)
        mock_default_address.deploy_nft.assert_called_once_with(
            "TestNFT", "TNFT", "https://example.com/nft/"
        )


@patch("cdp.Cdp.use_server_signer", True)
def test_wallet_deploy_multi_token_with_server_signer(wallet_factory):
    """Test the deploy_multi_token method of a Wallet with server-signer."""
    wallet = wallet_factory()
    mock_default_address = Mock(spec=WalletAddress)
    mock_smart_contract = Mock(spec=SmartContract)
    mock_default_address.deploy_multi_token.return_value = mock_smart_contract

    with patch.object(
        Wallet, "default_address", new_callable=PropertyMock
    ) as mock_default_address_prop:
        mock_default_address_prop.return_value = mock_default_address

        smart_contract = wallet.deploy_multi_token(uri="https://example.com/multi-token/{id}.json")

        assert isinstance(smart_contract, SmartContract)
        mock_default_address.deploy_multi_token.assert_called_once_with(
            "https://example.com/multi-token/{id}.json"
        )


@patch("cdp.Cdp.api_clients")
def test_create_webhook(mock_api_clients, wallet_factory, webhook_factory):
    """Test Wallet create_webhook method."""
    mock_api_clients.webhooks.create_wallet_webhook.return_value = webhook_factory()

    # Create a wallet instance using the factory
    wallet = wallet_factory()

    # Define the notification URI to pass into the create_webhook method
    notification_uri = "https://example.com/webhook"

    # Call the create_webhook method
    webhook = wallet.create_webhook(notification_uri)

    # Create the expected request object
    expected_request = CreateWalletWebhookRequest(notification_uri=notification_uri)

    # Assert that the API client was called with the correct parameters
    mock_api_clients.webhooks.create_wallet_webhook.assert_called_once_with(
        wallet_id=wallet.id, create_wallet_webhook_request=expected_request
    )

    # Assert that the returned webhook is an instance of Webhook
    assert isinstance(webhook, Webhook)

    # Additional assertions to check the returned webhook object
    assert webhook.notification_uri == notification_uri


@patch("cdp.Cdp.use_server_signer", True)
def test_wallet_fund(wallet_factory):
    """Test the fund method of a Wallet."""
    wallet = wallet_factory()
    mock_default_address = Mock(spec=WalletAddress)
    mock_fund_operation = Mock(spec=FundOperation)
    mock_default_address.fund.return_value = mock_fund_operation

    with patch.object(
        Wallet, "default_address", new_callable=PropertyMock
    ) as mock_default_address_prop:
        mock_default_address_prop.return_value = mock_default_address

        fund_operation = wallet.fund(amount="1.0", asset_id="eth")

        assert isinstance(fund_operation, FundOperation)
        mock_default_address.fund.assert_called_once_with("1.0", "eth")


@patch("cdp.Cdp.use_server_signer", True)
def test_wallet_fund_no_default_address(wallet_factory):
    """Test the fund method of a Wallet with no default address."""
    wallet = wallet_factory()

    with patch.object(
        Wallet, "default_address", new_callable=PropertyMock
    ) as mock_default_address_prop:
        mock_default_address_prop.return_value = None

        with pytest.raises(ValueError, match="Default address does not exist"):
            wallet.fund(amount="1.0", asset_id="eth")


@patch("cdp.Cdp.use_server_signer", True)
def test_wallet_quote_fund(wallet_factory):
    """Test the quote_fund method of a Wallet."""
    wallet = wallet_factory()
    mock_default_address = Mock(spec=WalletAddress)
    mock_fund_quote = Mock(spec=FundQuote)
    mock_default_address.quote_fund.return_value = mock_fund_quote

    with patch.object(
        Wallet, "default_address", new_callable=PropertyMock
    ) as mock_default_address_prop:
        mock_default_address_prop.return_value = mock_default_address

        fund_quote = wallet.quote_fund(amount="1.0", asset_id="eth")

        assert isinstance(fund_quote, FundQuote)
        mock_default_address.quote_fund.assert_called_once_with("1.0", "eth")


@patch("cdp.Cdp.use_server_signer", True)
def test_wallet_quote_fund_no_default_address(wallet_factory):
    """Test the quote_fund method of a Wallet with no default address."""
    wallet = wallet_factory()

    with patch.object(
        Wallet, "default_address", new_callable=PropertyMock
    ) as mock_default_address_prop:
        mock_default_address_prop.return_value = None

        with pytest.raises(ValueError, match="Default address does not exist"):
            wallet.quote_fund(amount="1.0", asset_id="eth")


@patch("cdp.Cdp.use_server_signer", False)
@patch("cdp.wallet.os")
@patch("cdp.wallet.Bip32Slip10Secp256k1")
def test_wallet_export_data(mock_bip32, mock_os, wallet_factory, master_key_factory):
    """Test Wallet export_data method."""
    seed = b"\x00" * 64
    mock_urandom = Mock(return_value=seed)
    mock_os.urandom = mock_urandom
    mock_from_seed = Mock(return_value=master_key_factory(seed))
    mock_bip32.FromSeed = mock_from_seed

    wallet = wallet_factory()

    exported = wallet.export_data()

    assert exported.wallet_id == wallet.id
    assert exported.seed == seed.hex()
    assert exported.network_id == wallet.network_id


@patch("cdp.Cdp.use_server_signer", False)
@patch("cdp.Cdp.api_clients")
@patch("cdp.wallet.Account")
def test_wallet_import_from_mnemonic_seed_phrase(
    mock_account,
    mock_api_clients,
    wallet_factory,
    address_model_factory,
):
    """Test importing a wallet from a mnemonic seed phrase."""
    # Valid 24-word mnemonic and expected address
    valid_mnemonic = "crouch cereal notice one canyon kiss tape employ ghost column vanish despair eight razor laptop keen rally gaze riot regret assault jacket risk curve"
    expected_address = "0x43A0477E658C6e05136e81C576CF02daCEa067bB"
    public_key = "0x037e6cbdd1d949f60f41d5db7ffa9b3ddce0b77eab35ef7affd3f64cbfd9e33a91"

    # Create mock address model
    mock_address = address_model_factory(
        address_id=expected_address,
        public_key=public_key,
        wallet_id="new-wallet-id",
        network_id="base-sepolia",
        index=0,
    )

    # Create mock wallet model with the address model
    mock_wallet = wallet_factory(
        id="new-wallet-id", network_id="base-sepolia", default_address=mock_address
    )._model

    # Add debug assertions
    assert mock_wallet.default_address is not None
    assert mock_wallet.default_address.address_id == expected_address

    # Mock Account.from_key to return an account with our expected address
    mock_account_instance = Mock(spec=Account)
    mock_account_instance.address = expected_address
    mock_account.from_key = Mock(return_value=mock_account_instance)

    # Mock both API calls to return the same wallet model
    mock_api_clients.wallets.create_wallet = Mock(return_value=mock_wallet)
    mock_api_clients.wallets.get_wallet = Mock(return_value=mock_wallet)
    mock_api_clients.addresses.create_address = Mock(return_value=mock_address)

    # Mock list_addresses call
    mock_address_list = Mock()
    mock_address_list.data = [mock_address]
    mock_api_clients.addresses.list_addresses = Mock(return_value=mock_address_list)

    # Import wallet using mnemonic
    from cdp.mnemonic_seed_phrase import MnemonicSeedPhrase

    wallet = Wallet.import_wallet(MnemonicSeedPhrase(valid_mnemonic))

    # Verify the wallet was created successfully
    assert isinstance(wallet, Wallet)

    # Verify the default address matches expected address
    assert wallet.default_address is not None
    assert wallet.default_address.address_id == expected_address
    assert wallet.default_address._model.public_key == public_key


@patch("cdp.Cdp.use_server_signer", False)
@patch("cdp.Cdp.api_clients")
@patch("cdp.wallet.Account")
def test_wallet_import_from_mnemonic_seed_phrase_specified_network_id(
    mock_account,
    mock_api_clients,
    wallet_factory,
    address_model_factory,
):
    """Test importing a wallet from a mnemonic seed phrase with network ID specified."""
    # Valid 24-word mnemonic and expected address
    valid_mnemonic = "crouch cereal notice one canyon kiss tape employ ghost column vanish despair eight razor laptop keen rally gaze riot regret assault jacket risk curve"
    expected_address = "0x43A0477E658C6e05136e81C576CF02daCEa067bB"
    public_key = "0x037e6cbdd1d949f60f41d5db7ffa9b3ddce0b77eab35ef7affd3f64cbfd9e33a91"

    # Create mock address model
    mock_address = address_model_factory(
        address_id=expected_address,
        public_key=public_key,
        wallet_id="new-wallet-id",
        network_id="base-mainnet",
        index=0,
    )

    # Create mock wallet model with the address model
    mock_wallet = wallet_factory(
        id="new-wallet-id", network_id="base-mainnet", default_address=mock_address
    )._model

    # Add debug assertions
    assert mock_wallet.default_address is not None
    assert mock_wallet.default_address.address_id == expected_address

    # Mock Account.from_key to return an account with our expected address
    mock_account_instance = Mock(spec=Account)
    mock_account_instance.address = expected_address
    mock_account.from_key = Mock(return_value=mock_account_instance)

    # Mock both API calls to return the same wallet model
    mock_api_clients.wallets.create_wallet = Mock(return_value=mock_wallet)
    mock_api_clients.wallets.get_wallet = Mock(return_value=mock_wallet)
    mock_api_clients.addresses.create_address = Mock(return_value=mock_address)

    # Mock list_addresses call
    mock_address_list = Mock()
    mock_address_list.data = [mock_address]
    mock_api_clients.addresses.list_addresses = Mock(return_value=mock_address_list)

    # Import wallet using mnemonic
    from cdp.mnemonic_seed_phrase import MnemonicSeedPhrase

    wallet = Wallet.import_wallet(MnemonicSeedPhrase(valid_mnemonic), network_id="base-mainnet")

    # Verify the wallet was created successfully
    assert isinstance(wallet, Wallet)

    # Verify the default address matches expected address
    assert wallet.default_address is not None
    assert wallet.default_address.address_id == expected_address
    assert wallet.default_address._model.public_key == public_key


def test_wallet_import_from_mnemonic_empty_phrase():
    """Test importing a wallet with an empty mnemonic phrase."""
    from cdp.mnemonic_seed_phrase import MnemonicSeedPhrase

    with pytest.raises(ValueError, match="BIP-39 mnemonic seed phrase must be provided"):
        Wallet.import_wallet(MnemonicSeedPhrase(""))


def test_wallet_import_from_mnemonic_invalid_phrase():
    """Test importing a wallet with an invalid mnemonic phrase."""
    from cdp.mnemonic_seed_phrase import MnemonicSeedPhrase

    with pytest.raises(ValueError, match="Invalid BIP-39 mnemonic seed phrase"):
        Wallet.import_wallet(MnemonicSeedPhrase("invalid mnemonic phrase"))
