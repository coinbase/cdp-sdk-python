# CDP Python SDK

The CDP Python SDK enables the simple integration of crypto into your app.
By calling Coinbase's CDP APIs, the SDK allows you to provision crypto wallets,
send crypto into/out of those wallets, track wallet balances, and trade crypto from
one asset into another.

**CDP SDK v0 is a pre-alpha release, which means that the APIs and SDK methods are subject to change. We will continuously release updates to support new capabilities and improve the developer experience.**

## Documentation

- [CDP API Documentation](https://docs.cdp.coinbase.com/platform-apis/docs/welcome)
- [CDP SDK Python Documentation](https://coinbase.github.io/cdp-sdk-python/)

## Requirements

- Python 3.10+

### Checking Python Version

Before using the SDK, ensure that you have the correct version of Python installed. The SDK requires Python 3.10 or higher. You can check your Python version by running the following code:

```bash
python --version
pip --version
```

If you need to upgrade your Python version, you can download and install the latest version of Python from the [official Python website](https://www.python.org/downloads/).
For `pip`, refer to the [official pip documentation](https://pip.pypa.io/en/stable/installation/) for installation instructions.

## Installation

```bash
pip install cdp-sdk
```

### Starting a Python REPL

To start a Python REPL:

```bash
python
```

## Creating a Wallet

To start, [create a CDP API key](https://portal.cdp.coinbase.com/access/api). Then, initialize the CDP SDK by passing your API key name and API key's private key via the `configure` method:

```python
from cdp import *

api_key_name = "Copy your API key name here."

api_key_private_key = "Copy your API key's private key here."

Cdp.configure(api_key_name, api_key_private_key)

print("CDP SDK has been successfully configured with CDP API key.")
```

Another way to initialize the SDK is by sourcing the API key from the JSON file that contains your API key,
downloaded from the CDP portal.

```python
Cdp.configure_from_json("~/Downloads/cdp_api_key.json")

print("CDP SDK has been successfully configured from JSON file.")
```

This will allow you to authenticate with the Platform APIs.

If you are using a CDP Server-Signer to manage your private keys, enable it with

```python
Cdp.use_server_signer = True
```

Now create a wallet. Wallets are created with a single default address.

```python
# Create a wallet with one address by default.
wallet1 = Wallet.create()

print(f"Wallet successfully created: {wallet1}")
```

Wallets come with a single default address, accessible via `default_address`:

```python
# A wallet has a default address.
address = wallet1.default_address
```

## Funding a Wallet

Wallets do not have funds on them to start. For Base Sepolia testnet, we provide a `faucet` method to fund your wallet with
testnet ETH. You are allowed one faucet claim per 24-hour window.

```python
# Fund the wallet with a faucet transaction.
faucet_tx = wallet1.faucet()

print(f"Faucet transaction successfully completed: {faucet_tx}")
```

## Transferring Funds

See [Transfers](https://docs.cdp.coinbase.com/wallets/docs/transfers) for more information.

Now that your faucet transaction has successfully completed, you can send the funds in your wallet to another wallet.
The code below creates another wallet, and uses the `transfer` function to send testnet ETH from the first wallet to
the second:

```python
# Create a new wallet wallet2 to transfer funds to.
wallet2 = Wallet.create()

print(f"Wallet successfully created: {wallet2}")

transfer = wallet1.transfer(0.00001, "eth", wallet2).wait()

print(f"Transfer successfully completed: {transfer}")
```

### Gasless USDC Transfers

To transfer USDC without needing to hold ETH for gas, you can use the `transfer` method with the `gasless` option set to `True`.

```python
# Create a new wallet wallet3 to transfer funds to.
wallet3 = Wallet.create()

print(f"Wallet successfully created: {wallet3}")

# Fund the wallet with USDC with a faucet transaction.
usdc_faucet_tx = wallet1.faucet("usdc")

print(f"Faucet transaction successfully completed: {usdc_faucet_tx}")

transfer = wallet1.transfer(0.00001, "usdc", wallet3, gasless=True).wait()
```

## Listing Transfers

```python
# Return list of all transfers. This will paginate and fetch all transfers for the address.
list(address.transfers())
```

## Trading Funds

See [Trades](https://docs.cdp.coinbase.com/wallets/docs/trades) for more information.

```python
wallet = Wallet.create("base-mainnet")

print(f"Wallet successfully created: {wallet}")
print(f"Send `base-mainnet` ETH to wallets default address: {wallet.default_address.address_id}")

trade = wallet.trade(0.00001, "eth", "usdc").wait()

print(f"Trade successfully completed: {trade}")
```

## Listing Trades

```python
# Return list of all trades. This will paginate and fetch all trades for the address.
list(address.trades())
```

## Creating a Webhook
A webhook is a way to provide other applications with real-time information from the blockchain. When an event occurs on a blockchain address, it can send a POST request to a URL you specify. You can create a webhook to receive notifications about events that occur in your wallet or crypto address, such as when a user makes a transfer.
```python
from cdp.client.models.webhook import WebhookEventType
from cdp.client.models.webhook import WebhookEventFilter

wh1 = Webhook.create(
    notification_uri="https://your-app.com/callback",
    event_type=WebhookEventType.ERC20_TRANSFER,
    event_filters=[WebhookEventFilter(from_address="0x71d4d7d5e9ce0f41e6a68bd3a9b43aa597dc0eb0")]
)
print(wh1)
```

## Creating a Webhook On A Wallet
A webhook can be attached to an existing wallet to monitor events that occur on the wallet, i.e. all addresses associated with this wallet. A list of supported blockchain events can be found [here](https://docs.cdp.coinbase.com/get-started/docs/webhooks/event-types).
```python
import cdp

wallet1 = Wallet.create()
wh1 = wallet1.create_webhook("https://your-app.com/callback")
print(wh1)
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for more information.

