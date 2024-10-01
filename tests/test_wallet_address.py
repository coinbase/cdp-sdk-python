from decimal import Decimal
from unittest.mock import Mock, patch

import pytest
from eth_account.datastructures import SignedMessage
from eth_account.messages import encode_defunct
from eth_account.signers.local import LocalAccount
from eth_utils import to_bytes
from web3 import Web3

from cdp.client.models.address import Address as AddressModel
from cdp.client.models.asset import Asset as AssetModel
from cdp.client.models.balance import Balance as BalanceModel
from cdp.client.models.create_smart_contract_request import CreateSmartContractRequest
from cdp.client.models.multi_token_contract_options import MultiTokenContractOptions
from cdp.client.models.nft_contract_options import NFTContractOptions
from cdp.client.models.smart_contract_options import SmartContractOptions
from cdp.client.models.token_contract_options import TokenContractOptions
from cdp.contract_invocation import ContractInvocation
from cdp.errors import InsufficientFundsError
from cdp.payload_signature import PayloadSignature
from cdp.smart_contract import SmartContract
from cdp.trade import Trade
from cdp.transfer import Transfer
from cdp.wallet_address import WalletAddress


@pytest.fixture
def address_model():
    """Fixture for an AddressModel."""
    return AddressModel(
        network_id="base-sepolia",
        address_id="0x1234567890123456789012345678901234567890",
        wallet_id="test-wallet-id-1",
        public_key="0x1234567890123456789012345678901234567890",
        index=0,
    )


@pytest.fixture
def wallet_address(address_model):
    """Fixture for a WalletAddress."""
    return WalletAddress(address_model)


@pytest.fixture
def wallet_address_with_key(address_model):
    """Fixture for a WalletAddress with a key."""
    key = Mock(spec=LocalAccount)
    return WalletAddress(address_model, key)


@pytest.fixture
def asset_model():
    """Fixture for an AssetModel."""
    return AssetModel(network_id="base-sepolia", asset_id="eth", decimals=18)


@pytest.fixture
def balance_model(asset_model):
    """Fixture for a BalanceModel."""
    return BalanceModel(amount="5000000000000000000", asset=asset_model)


def test_wallet_address_initialization(wallet_address):
    """Test the initialization of a WalletAddress."""
    assert wallet_address.network_id == "base-sepolia"
    assert wallet_address.address_id == "0x1234567890123456789012345678901234567890"
    assert wallet_address.wallet_id == "test-wallet-id-1"
    assert wallet_address.key is None
    assert not wallet_address.can_sign


def test_wallet_address_initialization_with_key(wallet_address_with_key):
    """Test the initialization of a WalletAddress with a key."""
    assert wallet_address_with_key.network_id == "base-sepolia"
    assert wallet_address_with_key.address_id == "0x1234567890123456789012345678901234567890"
    assert wallet_address_with_key.wallet_id == "test-wallet-id-1"
    assert wallet_address_with_key.key is not None
    assert wallet_address_with_key.can_sign


def test_wallet_id_property(wallet_address):
    """Test the wallet_id property of a WalletAddress."""
    assert wallet_address.wallet_id == "test-wallet-id-1"


def test_key_property(wallet_address, wallet_address_with_key):
    """Test the key property of a WalletAddress."""
    assert wallet_address.key is None
    assert wallet_address_with_key.key is not None


def test_key_setter(wallet_address):
    """Test the key setter of a WalletAddress."""
    new_key = Mock(spec=LocalAccount)
    wallet_address.key = new_key
    assert wallet_address.key == new_key


def test_can_sign_property(wallet_address, wallet_address_with_key):
    """Test the can_sign property of a WalletAddress."""
    assert not wallet_address.can_sign
    assert wallet_address_with_key.can_sign


def test_key_setter_raises_error_when_already_set(wallet_address_with_key):
    """Test the key setter raises an error when already set."""
    new_key = Mock(spec=LocalAccount)
    with pytest.raises(ValueError, match="Private key is already set"):
        wallet_address_with_key.key = new_key


@patch("cdp.wallet_address.Transfer")
@patch("cdp.Cdp.api_clients")
@patch("cdp.Cdp.use_server_signer", True)
def test_transfer_with_server_signer(
    mock_api_clients, mock_transfer, wallet_address, balance_model
):
    """Test the transfer method with a server signer."""
    mock_transfer_instance = Mock(spec=Transfer)
    mock_transfer.create.return_value = mock_transfer_instance

    mock_get_balance = Mock()
    mock_get_balance.return_value = balance_model
    mock_api_clients.external_addresses.get_external_address_balance = mock_get_balance

    transfer = wallet_address.transfer(amount="1.0", asset_id="eth", destination="0xdestination")

    assert isinstance(transfer, Transfer)
    mock_get_balance.assert_called_once_with(
        network_id=wallet_address.network_id, address_id=wallet_address.address_id, asset_id="eth"
    )
    mock_transfer.create.assert_called_once_with(
        address_id=wallet_address.address_id,
        amount=Decimal("1.0"),
        asset_id="eth",
        destination="0xdestination",
        network_id=wallet_address.network_id,
        wallet_id=wallet_address.wallet_id,
        gasless=False,
    )
    mock_transfer_instance.sign.assert_not_called()
    mock_transfer_instance.broadcast.assert_not_called()


@patch("cdp.wallet_address.Transfer")
@patch("cdp.Cdp.api_clients")
@patch("cdp.Cdp.use_server_signer", False)
def test_transfer(mock_api_clients, mock_transfer, wallet_address_with_key, balance_model):
    """Test the transfer method."""
    mock_transfer_instance = Mock(spec=Transfer)
    mock_transfer.create.return_value = mock_transfer_instance

    mock_get_balance = Mock()
    mock_get_balance.return_value = balance_model
    mock_api_clients.external_addresses.get_external_address_balance = mock_get_balance

    transfer = wallet_address_with_key.transfer(
        amount="1.0", asset_id="eth", destination="0xdestination"
    )

    assert isinstance(transfer, Transfer)
    mock_get_balance.assert_called_once_with(
        network_id=wallet_address_with_key.network_id,
        address_id=wallet_address_with_key.address_id,
        asset_id="eth",
    )
    mock_transfer.create.assert_called_once_with(
        address_id=wallet_address_with_key.address_id,
        amount=Decimal("1.0"),
        asset_id="eth",
        destination="0xdestination",
        network_id=wallet_address_with_key.network_id,
        wallet_id=wallet_address_with_key.wallet_id,
        gasless=False,
    )
    mock_transfer_instance.sign.assert_called_once_with(wallet_address_with_key.key)
    mock_transfer_instance.broadcast.assert_called_once()


@patch("cdp.wallet_address.Transfer")
@patch("cdp.Cdp.api_clients")
@patch("cdp.Cdp.use_server_signer", False)
def test_transfer_create_api_error(
    mock_api_clients, mock_transfer, wallet_address_with_key, balance_model
):
    """Test the transfer method raises an error when the create API call fails."""
    mock_transfer.create.side_effect = Exception("API Error")

    mock_get_balance = Mock()
    mock_get_balance.return_value = balance_model
    mock_api_clients.external_addresses.get_external_address_balance = mock_get_balance

    with pytest.raises(Exception, match="API Error"):
        wallet_address_with_key.transfer(amount="1.0", asset_id="eth", destination="0xdestination")

    mock_get_balance.assert_called_once_with(
        network_id=wallet_address_with_key.network_id,
        address_id=wallet_address_with_key.address_id,
        asset_id="eth",
    )
    mock_transfer.create.assert_called_once_with(
        address_id=wallet_address_with_key.address_id,
        amount=Decimal("1.0"),
        asset_id="eth",
        destination="0xdestination",
        network_id=wallet_address_with_key.network_id,
        wallet_id=wallet_address_with_key.wallet_id,
        gasless=False,
    )


@patch("cdp.wallet_address.Transfer")
@patch("cdp.Cdp.api_clients")
@patch("cdp.Cdp.use_server_signer", False)
def test_transfer_broadcast_api_error(
    mock_api_clients, mock_transfer, wallet_address_with_key, balance_model
):
    """Test the transfer method raises an error when the broadcast API call fails."""
    mock_transfer_instance = Mock(spec=Transfer)
    mock_transfer_instance.broadcast.side_effect = Exception("API Error")
    mock_transfer.create.return_value = mock_transfer_instance

    mock_get_balance = Mock()
    mock_get_balance.return_value = balance_model
    mock_api_clients.external_addresses.get_external_address_balance = mock_get_balance

    with pytest.raises(Exception, match="API Error"):
        wallet_address_with_key.transfer(amount="1.0", asset_id="eth", destination="0xdestination")

    mock_get_balance.assert_called_once_with(
        network_id=wallet_address_with_key.network_id,
        address_id=wallet_address_with_key.address_id,
        asset_id="eth",
    )
    mock_transfer.create.assert_called_once_with(
        address_id=wallet_address_with_key.address_id,
        amount=Decimal("1.0"),
        asset_id="eth",
        destination="0xdestination",
        network_id=wallet_address_with_key.network_id,
        wallet_id=wallet_address_with_key.wallet_id,
        gasless=False,
    )
    mock_transfer_instance.sign.assert_called_once_with(wallet_address_with_key.key)
    mock_transfer_instance.broadcast.assert_called_once()


@patch("cdp.wallet_address.Trade")
@patch("cdp.Cdp.api_clients")
@patch("cdp.Cdp.use_server_signer", True)
def test_trade(mock_api_clients, mock_trade, wallet_address, balance_model):
    """Test the trade method with a server signer."""
    mock_trade.create.return_value = Mock(spec=Trade)

    mock_get_balance = Mock()
    mock_get_balance.return_value = balance_model
    mock_api_clients.external_addresses.get_external_address_balance = mock_get_balance

    trade = wallet_address.trade(amount="1.0", from_asset_id="eth", to_asset_id="usdc")

    assert isinstance(trade, Trade)
    mock_trade.create.assert_called_once_with(
        address_id=wallet_address.address_id,
        from_asset_id="eth",
        to_asset_id="usdc",
        amount=Decimal("1.0"),
        network_id=wallet_address.network_id,
        wallet_id=wallet_address.wallet_id,
    )


@patch("cdp.wallet_address.Trade")
@patch("cdp.Cdp.api_clients")
@patch("cdp.Cdp.use_server_signer", False)
def test_trade_with_client_signer(
    mock_api_clients, mock_trade, wallet_address_with_key, balance_model
):
    """Test the trade method."""
    mock_trade_instance = Mock(spec=Trade)
    mock_trade.create.return_value = mock_trade_instance

    mock_get_balance = Mock()
    mock_get_balance.return_value = balance_model
    mock_api_clients.external_addresses.get_external_address_balance = mock_get_balance

    trade = wallet_address_with_key.trade(amount="1.0", from_asset_id="eth", to_asset_id="usdc")

    assert isinstance(trade, Trade)
    mock_get_balance.assert_called_once_with(
        network_id=wallet_address_with_key.network_id,
        address_id=wallet_address_with_key.address_id,
        asset_id="eth",
    )
    mock_trade_instance.transaction.sign.assert_called_once_with(wallet_address_with_key.key)
    mock_trade_instance.approve_transaction.sign.assert_called_once_with(
        wallet_address_with_key.key
    )
    mock_trade_instance.broadcast.assert_called_once()


@patch("cdp.wallet_address.Transfer")
def test_transfers(mock_transfer, wallet_address):
    """Test the transfers method."""
    mock_transfer.list.return_value = iter([Mock(spec=Transfer), Mock(spec=Transfer)])

    transfers = wallet_address.transfers()

    assert len(list(transfers)) == 2
    assert all(isinstance(t, Transfer) for t in transfers)
    mock_transfer.list.assert_called_once_with(
        wallet_id=wallet_address.wallet_id, address_id=wallet_address.address_id
    )


@patch("cdp.wallet_address.Transfer")
def test_transfers_api_error(mock_transfer, wallet_address):
    """Test the transfers method raises an error when the API call fails."""
    mock_transfer.list.side_effect = Exception("API Error")

    with pytest.raises(Exception, match="API Error"):
        wallet_address.transfers()


@patch("cdp.wallet_address.Trade")
def test_trades(mock_trade, wallet_address):
    """Test the trades method."""
    mock_trade.list.return_value = iter([Mock(spec=Trade), Mock(spec=Trade)])

    trades = wallet_address.trades()

    assert len(list(trades)) == 2
    assert all(isinstance(t, Trade) for t in trades)
    mock_trade.list.assert_called_once_with(
        wallet_id=wallet_address.wallet_id, address_id=wallet_address.address_id
    )


@patch("cdp.wallet_address.Trade")
def test_trades_api_error(mock_trade, wallet_address):
    """Test the trades method raises an error when the API call fails."""
    mock_trade.list.side_effect = Exception("API Error")

    with pytest.raises(Exception, match="API Error"):
        wallet_address.trades()


@patch("cdp.wallet_address.ContractInvocation")
@patch("cdp.Cdp.api_clients")
@patch("cdp.Cdp.use_server_signer", True)
def test_invoke_contract_with_server_signer(
    mock_api_clients, mock_contract_invocation, wallet_address, balance_model
):
    """Test the invoke_contract method with a server signer."""
    mock_contract_invocation_instance = Mock(spec=ContractInvocation)
    mock_contract_invocation.create.return_value = mock_contract_invocation_instance

    mock_get_balance = Mock()
    mock_get_balance.return_value = balance_model
    mock_api_clients.external_addresses.get_external_address_balance = mock_get_balance

    contract_invocation = wallet_address.invoke_contract(
        contract_address="0xcontractaddress",
        method="testMethod",
        abi=[{"abi": "data"}],
        args={"arg1": "value1"},
        amount=Decimal("1"),
        asset_id="wei",
    )

    assert isinstance(contract_invocation, ContractInvocation)
    mock_get_balance.assert_called_once_with(
        network_id=wallet_address.network_id, address_id=wallet_address.address_id, asset_id="eth"
    )
    mock_contract_invocation.create.assert_called_once_with(
        address_id=wallet_address.address_id,
        wallet_id=wallet_address.wallet_id,
        network_id=wallet_address.network_id,
        contract_address="0xcontractaddress",
        method="testMethod",
        abi=[{"abi": "data"}],
        args={"arg1": "value1"},
        amount=Decimal("1"),
        asset_id="wei",
    )
    mock_contract_invocation_instance.sign.assert_not_called()
    mock_contract_invocation_instance.broadcast.assert_not_called()


@patch("cdp.wallet_address.ContractInvocation")
@patch("cdp.Cdp.api_clients")
@patch("cdp.Cdp.use_server_signer", False)
def test_invoke_contract(
    mock_api_clients, mock_contract_invocation, wallet_address_with_key, balance_model
):
    """Test the invoke_contract method."""
    mock_contract_invocation_instance = Mock(spec=ContractInvocation)
    mock_contract_invocation.create.return_value = mock_contract_invocation_instance

    mock_get_balance = Mock()
    mock_get_balance.return_value = balance_model
    mock_api_clients.external_addresses.get_external_address_balance = mock_get_balance

    contract_invocation = wallet_address_with_key.invoke_contract(
        contract_address="0xcontractaddress",
        method="testMethod",
        abi=[{"abi": "data"}],
        args={"arg1": "value1"},
        amount=Decimal("1"),
        asset_id="wei",
    )

    assert isinstance(contract_invocation, ContractInvocation)
    mock_get_balance.assert_called_once_with(
        network_id=wallet_address_with_key.network_id,
        address_id=wallet_address_with_key.address_id,
        asset_id="eth",
    )
    mock_contract_invocation.create.assert_called_once_with(
        address_id=wallet_address_with_key.address_id,
        wallet_id=wallet_address_with_key.wallet_id,
        network_id=wallet_address_with_key.network_id,
        contract_address="0xcontractaddress",
        method="testMethod",
        abi=[{"abi": "data"}],
        args={"arg1": "value1"},
        amount=Decimal("1"),
        asset_id="wei",
    )
    mock_contract_invocation_instance.sign.assert_called_once_with(wallet_address_with_key.key)
    mock_contract_invocation_instance.broadcast.assert_called_once()


@patch("cdp.wallet_address.ContractInvocation")
@patch("cdp.Cdp.api_clients")
@patch("cdp.Cdp.use_server_signer", False)
def test_invoke_contract_api_error(
    mock_api_clients, mock_contract_invocation, wallet_address_with_key, balance_model
):
    """Test the invoke_contract method raises an error when the create API call fails."""
    mock_contract_invocation.create.side_effect = Exception("API Error")

    mock_get_balance = Mock()
    mock_get_balance.return_value = balance_model
    mock_api_clients.external_addresses.get_external_address_balance = mock_get_balance

    with pytest.raises(Exception, match="API Error"):
        wallet_address_with_key.invoke_contract(
            contract_address="0xcontractaddress",
            method="testMethod",
            abi=[{"abi": "data"}],
            args={"arg1": "value1"},
            amount=Decimal("1"),
            asset_id="wei",
        )

    mock_get_balance.assert_called_once_with(
        network_id=wallet_address_with_key.network_id,
        address_id=wallet_address_with_key.address_id,
        asset_id="eth",
    )
    mock_contract_invocation.create.assert_called_once_with(
        address_id=wallet_address_with_key.address_id,
        wallet_id=wallet_address_with_key.wallet_id,
        network_id=wallet_address_with_key.network_id,
        contract_address="0xcontractaddress",
        method="testMethod",
        abi=[{"abi": "data"}],
        args={"arg1": "value1"},
        amount=Decimal("1"),
        asset_id="wei",
    )


@patch("cdp.wallet_address.ContractInvocation")
@patch("cdp.Cdp.api_clients")
@patch("cdp.Cdp.use_server_signer", False)
def test_invoke_contract_broadcast_api_error(
    mock_api_clients, mock_contract_invocation, wallet_address_with_key, balance_model
):
    """Test the invoke_contract method raises an error when the broadcast API call fails."""
    mock_contract_invocation_instance = Mock(spec=ContractInvocation)
    mock_contract_invocation.create.return_value = mock_contract_invocation_instance
    mock_contract_invocation_instance.broadcast.side_effect = Exception("API Error")

    mock_get_balance = Mock()
    mock_get_balance.return_value = balance_model
    mock_api_clients.external_addresses.get_external_address_balance = mock_get_balance

    with pytest.raises(Exception, match="API Error"):
        wallet_address_with_key.invoke_contract(
            contract_address="0xcontractaddress",
            method="testMethod",
            abi=[{"abi": "data"}],
            args={"arg1": "value1"},
            amount=Decimal("1"),
            asset_id="wei",
        )

    mock_get_balance.assert_called_once_with(
        network_id=wallet_address_with_key.network_id,
        address_id=wallet_address_with_key.address_id,
        asset_id="eth",
    )
    mock_contract_invocation.create.assert_called_once_with(
        address_id=wallet_address_with_key.address_id,
        wallet_id=wallet_address_with_key.wallet_id,
        network_id=wallet_address_with_key.network_id,
        contract_address="0xcontractaddress",
        method="testMethod",
        abi=[{"abi": "data"}],
        args={"arg1": "value1"},
        amount=Decimal("1"),
        asset_id="wei",
    )
    mock_contract_invocation_instance.sign.assert_called_once_with(wallet_address_with_key.key)
    mock_contract_invocation_instance.broadcast.assert_called_once()


@patch("cdp.wallet_address.PayloadSignature")
@patch("cdp.Cdp.use_server_signer", True)
def test_sign_payload_with_server_signer(mock_payload_signature, wallet_address):
    """Test the sign_payload method with a server signer."""
    mock_payload_signature_instance = Mock(spec=PayloadSignature)
    mock_payload_signature.create.return_value = mock_payload_signature_instance

    payload_signature = wallet_address.sign_payload(unsigned_payload="0xunsignedpayload")

    assert isinstance(payload_signature, PayloadSignature)
    mock_payload_signature.create.assert_called_once_with(
        wallet_id=wallet_address.wallet_id,
        address_id=wallet_address.address_id,
        unsigned_payload="0xunsignedpayload",
        signature=None,
    )


@patch("cdp.wallet_address.to_hex", Mock(return_value="0xsignature"))
@patch("cdp.wallet_address.PayloadSignature")
@patch("cdp.Cdp.use_server_signer", False)
def test_sign_payload(mock_payload_signature, wallet_address_with_key):
    """Test the sign_payload method."""
    mock_payload_signature_instance = Mock(spec=PayloadSignature)
    mock_payload_signature.create.return_value = mock_payload_signature_instance

    mock_signature = Mock(spec=SignedMessage)
    mock_signature.signature = "0xsignature"
    wallet_address_with_key.key.unsafe_sign_hash.return_value = mock_signature

    message_encoded = encode_defunct(text="eip-191 message")
    unsigned_payload = Web3.keccak(message_encoded.body).hex()

    payload_signature = wallet_address_with_key.sign_payload(unsigned_payload=unsigned_payload)

    assert isinstance(payload_signature, PayloadSignature)
    mock_payload_signature.create.assert_called_once_with(
        wallet_id=wallet_address_with_key.wallet_id,
        address_id=wallet_address_with_key.address_id,
        unsigned_payload=unsigned_payload,
        signature="0xsignature",
    )
    wallet_address_with_key.key.unsafe_sign_hash.assert_called_once_with(
        to_bytes(hexstr=unsigned_payload)
    )


@patch("cdp.wallet_address.to_hex", Mock(return_value="0xsignature"))
@patch("cdp.wallet_address.PayloadSignature")
@patch("cdp.Cdp.use_server_signer", False)
def test_sign_payload_api_error(mock_payload_signature, wallet_address_with_key):
    """Test the sign_payload method."""
    mock_signature = Mock(spec=SignedMessage)
    mock_signature.signature = "0xsignature"
    wallet_address_with_key.key.unsafe_sign_hash.return_value = mock_signature

    message_encoded = encode_defunct(text="eip-191 message")
    unsigned_payload = Web3.keccak(message_encoded.body).hex()

    mock_payload_signature.create.side_effect = Exception("API Error")

    with pytest.raises(Exception, match="API Error"):
        wallet_address_with_key.sign_payload(unsigned_payload=unsigned_payload)

    mock_payload_signature.create.assert_called_once_with(
        wallet_id=wallet_address_with_key.wallet_id,
        address_id=wallet_address_with_key.address_id,
        unsigned_payload=unsigned_payload,
        signature="0xsignature",
    )
    wallet_address_with_key.key.unsafe_sign_hash.assert_called_once_with(
        to_bytes(hexstr=unsigned_payload)
    )


@patch("cdp.Cdp.api_clients")
def test_ensure_sufficient_balance_sufficient(mock_api_clients, wallet_address, balance_model):
    """Test the ensure_sufficient_balance method with sufficient balance."""
    mock_get_balance = Mock()
    mock_get_balance.return_value = balance_model
    mock_api_clients.external_addresses.get_external_address_balance = mock_get_balance

    wallet_address._ensure_sufficient_balance(Decimal("1.5"), "eth")

    mock_get_balance.assert_called_once_with(
        network_id=wallet_address.network_id, address_id=wallet_address.address_id, asset_id="eth"
    )


@patch("cdp.Cdp.api_clients")
def test_ensure_sufficient_balance_insufficient(mock_api_clients, wallet_address, balance_model):
    """Test the ensure_sufficient_balance method with insufficient balance."""
    mock_get_balance = Mock()
    mock_get_balance.return_value = balance_model
    mock_api_clients.external_addresses.get_external_address_balance = mock_get_balance

    with pytest.raises(InsufficientFundsError):
        wallet_address._ensure_sufficient_balance(Decimal("100.0"), "eth")

    mock_get_balance.assert_called_once_with(
        network_id=wallet_address.network_id, address_id=wallet_address.address_id, asset_id="eth"
    )


def test_str_representation(wallet_address):
    """Test the str representation of a WalletAddress."""
    expected_str = "WalletAddress: (address_id: 0x1234567890123456789012345678901234567890, wallet_id: test-wallet-id-1, network_id: base-sepolia)"
    assert str(wallet_address) == expected_str


def test_repr(wallet_address):
    """Test the repr representation of a WalletAddress."""
    expected_repr = "WalletAddress: (address_id: 0x1234567890123456789012345678901234567890, wallet_id: test-wallet-id-1, network_id: base-sepolia)"
    assert repr(wallet_address) == expected_repr


@patch("cdp.Cdp.api_clients")
@patch("cdp.Cdp.use_server_signer", True)
def test_wallet_address_deploy_token_total_supply_string(mock_api_clients, wallet_address):
    """Test the deploy_token method of a WalletAddress with a string total_supply."""
    mock_smart_contract = Mock(spec=SmartContract)
    mock_api_clients.smart_contracts.create_smart_contract.return_value = mock_smart_contract

    smart_contract = wallet_address.deploy_token(
        name="TestToken", symbol="TT", total_supply="1000000"
    )

    assert isinstance(smart_contract, SmartContract)
    mock_api_clients.smart_contracts.create_smart_contract.assert_called_once_with(
        wallet_id=wallet_address.wallet_id,
        address_id=wallet_address.address_id,
        create_smart_contract_request=CreateSmartContractRequest(
            type="erc20",
            options=SmartContractOptions(
                actual_instance=TokenContractOptions(
                    name="TestToken", symbol="TT", total_supply="1000000"
                )
            ),
        ),
    )


@patch("cdp.Cdp.api_clients")
@patch("cdp.Cdp.use_server_signer", True)
def test_wallet_address_deploy_token_total_supply_number(mock_api_clients, wallet_address):
    """Test the deploy_token method of a WalletAddress with a number total_supply."""
    mock_smart_contract = Mock(spec=SmartContract)
    mock_api_clients.smart_contracts.create_smart_contract.return_value = mock_smart_contract

    smart_contract = wallet_address.deploy_token(
        name="TestToken", symbol="TT", total_supply=1000000
    )

    assert isinstance(smart_contract, SmartContract)
    mock_api_clients.smart_contracts.create_smart_contract.assert_called_once_with(
        wallet_id=wallet_address.wallet_id,
        address_id=wallet_address.address_id,
        create_smart_contract_request=CreateSmartContractRequest(
            type="erc20",
            options=SmartContractOptions(
                actual_instance=TokenContractOptions(
                    name="TestToken", symbol="TT", total_supply="1000000"
                )
            ),
        ),
    )


@patch("cdp.Cdp.api_clients")
@patch("cdp.Cdp.use_server_signer", True)
def test_wallet_address_deploy_token_total_supply_decimal(mock_api_clients, wallet_address):
    """Test the deploy_token method of a WalletAddress with a Decimal total_supply."""
    mock_smart_contract = Mock(spec=SmartContract)
    mock_api_clients.smart_contracts.create_smart_contract.return_value = mock_smart_contract

    smart_contract = wallet_address.deploy_token(
        name="TestToken", symbol="TT", total_supply=Decimal("1000000.5")
    )

    assert isinstance(smart_contract, SmartContract)
    mock_api_clients.smart_contracts.create_smart_contract.assert_called_once_with(
        wallet_id=wallet_address.wallet_id,
        address_id=wallet_address.address_id,
        create_smart_contract_request=CreateSmartContractRequest(
            type="erc20",
            options=SmartContractOptions(
                actual_instance=TokenContractOptions(
                    name="TestToken", symbol="TT", total_supply="1000000.5"
                )
            ),
        ),
    )


@patch("cdp.Cdp.api_clients")
@patch("cdp.Cdp.use_server_signer", True)
def test_wallet_address_deploy_nft(mock_api_clients, wallet_address):
    """Test the deploy_nft method of a WalletAddress."""
    mock_smart_contract = Mock(spec=SmartContract)
    mock_api_clients.smart_contracts.create_smart_contract.return_value = mock_smart_contract

    smart_contract = wallet_address.deploy_nft(
        name="TestNFT", symbol="TNFT", base_uri="https://example.com/nft/"
    )

    assert isinstance(smart_contract, SmartContract)
    mock_api_clients.smart_contracts.create_smart_contract.assert_called_once_with(
        wallet_id=wallet_address.wallet_id,
        address_id=wallet_address.address_id,
        create_smart_contract_request=CreateSmartContractRequest(
            type="erc721",
            options=SmartContractOptions(
                actual_instance=NFTContractOptions(
                    name="TestNFT", symbol="TNFT", base_uri="https://example.com/nft/"
                )
            ),
        ),
    )


@patch("cdp.Cdp.api_clients")
@patch("cdp.Cdp.use_server_signer", True)
def test_wallet_address_deploy_multi_token(mock_api_clients, wallet_address):
    """Test the deploy_multi_token method of a WalletAddress."""
    mock_smart_contract = Mock(spec=SmartContract)
    mock_api_clients.smart_contracts.create_smart_contract.return_value = mock_smart_contract

    smart_contract = wallet_address.deploy_multi_token(
        uri="https://example.com/multi-token/{id}.json"
    )

    assert isinstance(smart_contract, SmartContract)
    mock_api_clients.smart_contracts.create_smart_contract.assert_called_once_with(
        wallet_id=wallet_address.wallet_id,
        address_id=wallet_address.address_id,
        create_smart_contract_request=CreateSmartContractRequest(
            type="erc1155",
            options=SmartContractOptions(
                actual_instance=MultiTokenContractOptions(
                    uri="https://example.com/multi-token/{id}.json"
                )
            ),
        ),
    )


@patch("cdp.Cdp.api_clients")
@patch("cdp.Cdp.use_server_signer", True)
def test_wallet_address_deploy_token_with_server_signer(mock_api_clients, wallet_address):
    """Test the deploy_token method of a WalletAddress with server signer."""
    mock_smart_contract = Mock(spec=SmartContract)
    mock_api_clients.smart_contracts.create_smart_contract.return_value = mock_smart_contract

    smart_contract = wallet_address.deploy_token(
        name="TestToken", symbol="TT", total_supply="1000000"
    )

    assert isinstance(smart_contract, SmartContract)
    mock_api_clients.smart_contracts.create_smart_contract.assert_called_once_with(
        wallet_id=wallet_address.wallet_id,
        address_id=wallet_address.address_id,
        create_smart_contract_request=CreateSmartContractRequest(
            type="erc20",
            options=SmartContractOptions(
                actual_instance=TokenContractOptions(
                    name="TestToken", symbol="TT", total_supply="1000000"
                )
            ),
        ),
    )
    # Verify that sign and broadcast methods are not called when using server signer
    mock_smart_contract.sign.assert_not_called()
    mock_smart_contract.broadcast.assert_not_called()


@patch("cdp.Cdp.api_clients")
@patch("cdp.Cdp.use_server_signer", True)
def test_wallet_address_deploy_nft_with_server_signer(mock_api_clients, wallet_address):
    """Test the deploy_nft method of a WalletAddress with server signer."""
    mock_smart_contract = Mock(spec=SmartContract)
    mock_api_clients.smart_contracts.create_smart_contract.return_value = mock_smart_contract

    smart_contract = wallet_address.deploy_nft(
        name="TestNFT", symbol="TNFT", base_uri="https://example.com/nft/"
    )

    assert isinstance(smart_contract, SmartContract)
    mock_api_clients.smart_contracts.create_smart_contract.assert_called_once_with(
        wallet_id=wallet_address.wallet_id,
        address_id=wallet_address.address_id,
        create_smart_contract_request=CreateSmartContractRequest(
            type="erc721",
            options=SmartContractOptions(
                actual_instance=NFTContractOptions(
                    name="TestNFT", symbol="TNFT", base_uri="https://example.com/nft/"
                )
            ),
        ),
    )
    # Verify that sign and broadcast methods are not called when using server signer
    mock_smart_contract.sign.assert_not_called()
    mock_smart_contract.broadcast.assert_not_called()


@patch("cdp.Cdp.api_clients")
@patch("cdp.Cdp.use_server_signer", True)
def test_wallet_address_deploy_multi_token_with_server_signer(mock_api_clients, wallet_address):
    """Test the deploy_multi_token method of a WalletAddress with server signer."""
    mock_smart_contract = Mock(spec=SmartContract)
    mock_api_clients.smart_contracts.create_smart_contract.return_value = mock_smart_contract

    smart_contract = wallet_address.deploy_multi_token(
        uri="https://example.com/multi-token/{id}.json"
    )

    assert isinstance(smart_contract, SmartContract)
    mock_api_clients.smart_contracts.create_smart_contract.assert_called_once_with(
        wallet_id=wallet_address.wallet_id,
        address_id=wallet_address.address_id,
        create_smart_contract_request=CreateSmartContractRequest(
            type="erc1155",
            options=SmartContractOptions(
                actual_instance=MultiTokenContractOptions(
                    uri="https://example.com/multi-token/{id}.json"
                )
            ),
        ),
    )
    # Verify that sign and broadcast methods are not called when using server signer
    mock_smart_contract.sign.assert_not_called()
    mock_smart_contract.broadcast.assert_not_called()


@patch("cdp.wallet_address.SmartContract")
def test_deploy_token_api_error(mock_smart_contract, wallet_address_with_key):
    """Test the deploy_token method raises an error when the create API call fails."""
    mock_smart_contract.create.side_effect = Exception("API Error")

    with pytest.raises(Exception, match="API Error"):
        wallet_address_with_key.deploy_token(name="TestToken", symbol="TT", total_supply="1000000")

    mock_smart_contract.create.assert_called_once()


@patch("cdp.wallet_address.SmartContract")
def test_deploy_token_broadcast_api_error(mock_smart_contract, wallet_address_with_key):
    """Test the deploy_token method raises an error when the broadcast API call fails."""
    mock_smart_contract_instance = Mock(spec=SmartContract)
    mock_smart_contract.create.return_value = mock_smart_contract_instance
    mock_smart_contract_instance.broadcast.side_effect = Exception("API Error")

    with pytest.raises(Exception, match="API Error"):
        wallet_address_with_key.deploy_token(name="TestToken", symbol="TT", total_supply="1000000")

    mock_smart_contract.create.assert_called_once()
    mock_smart_contract_instance.sign.assert_called_once_with(wallet_address_with_key.key)
    mock_smart_contract_instance.broadcast.assert_called_once()


@patch("cdp.wallet_address.SmartContract")
def test_deploy_nft_api_error(mock_smart_contract, wallet_address_with_key):
    """Test the deploy_nft method raises an error when the create API call fails."""
    mock_smart_contract.create.side_effect = Exception("API Error")

    with pytest.raises(Exception, match="API Error"):
        wallet_address_with_key.deploy_nft(
            name="TestNFT", symbol="TNFT", base_uri="https://example.com/nft/"
        )

    mock_smart_contract.create.assert_called_once()


@patch("cdp.wallet_address.SmartContract")
def test_deploy_nft_broadcast_api_error(mock_smart_contract, wallet_address_with_key):
    """Test the deploy_nft method raises an error when the broadcast API call fails."""
    mock_smart_contract_instance = Mock(spec=SmartContract)
    mock_smart_contract.create.return_value = mock_smart_contract_instance
    mock_smart_contract_instance.broadcast.side_effect = Exception("API Error")

    with pytest.raises(Exception, match="API Error"):
        wallet_address_with_key.deploy_nft(
            name="TestNFT", symbol="TNFT", base_uri="https://example.com/nft/"
        )

    mock_smart_contract.create.assert_called_once()
    mock_smart_contract_instance.sign.assert_called_once_with(wallet_address_with_key.key)
    mock_smart_contract_instance.broadcast.assert_called_once()


@patch("cdp.wallet_address.SmartContract")
def test_deploy_multi_token_api_error(mock_smart_contract, wallet_address_with_key):
    """Test the deploy_multi_token method raises an error when the create API call fails."""
    mock_smart_contract.create.side_effect = Exception("API Error")

    with pytest.raises(Exception, match="API Error"):
        wallet_address_with_key.deploy_multi_token(uri="https://example.com/multi-token/{id}.json")

    mock_smart_contract.create.assert_called_once()


@patch("cdp.wallet_address.SmartContract")
def test_deploy_multi_token_broadcast_api_error(mock_smart_contract, wallet_address_with_key):
    """Test the deploy_multi_token method raises an error when the broadcast API call fails."""
    mock_smart_contract_instance = Mock(spec=SmartContract)
    mock_smart_contract.create.return_value = mock_smart_contract_instance
    mock_smart_contract_instance.broadcast.side_effect = Exception("API Error")

    with pytest.raises(Exception, match="API Error"):
        wallet_address_with_key.deploy_multi_token(uri="https://example.com/multi-token/{id}.json")

    mock_smart_contract.create.assert_called_once()
    mock_smart_contract_instance.sign.assert_called_once_with(wallet_address_with_key.key)
    mock_smart_contract_instance.broadcast.assert_called_once()
