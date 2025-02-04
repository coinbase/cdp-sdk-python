# CDP Python SDK

[![PyPI version](https://img.shields.io/pypi/v/cdp-sdk?style=flat-square&logo=python)](https://pypi.org/project/cdp-sdk/)
[![PyPI - Weekly Downloads](https://img.shields.io/pypi/dw/cdp-sdk?style=flat-square)](https://pypistats.org/packages/cdp-sdk)

The CDP Python SDK enables the simple integration of crypto into your app.
By calling Coinbase's CDP APIs, the SDK allows you to provision crypto wallets,
send crypto into/out of those wallets, track wallet balances, and trade crypto from
one asset into another.


*Note: As the SDK provides new capabilities and improves the developer experience, updates may occasionally include breaking changes. These will be documented in the [CHANGELOG.md](CHANGELOG.md) file.*

## Documentation

- [CDP API Documentation](https://docs.cdp.coinbase.com/platform-apis/docs/welcome)
- [CDP SDK Python Documentation](https://coinbase.github.io/cdp-sdk-python/)

## Requirements

- Python 3.10+
- Poetry for package management and tooling
  - [Poetry Installation Instructions](https://python-poetry.org/docs/#installation)

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

if you prefer to manage dependencies with Poetry:

```bash
poetry add cdp-sdk
```

### Starting a Python REPL

To start a Python REPL:

```bash
python
```

## Quickstart

### Creating a Wallet

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

If you are using a CDP [Server-Signer](https://docs.cdp.coinbase.com/wallet-api/docs/serversigners) to manage your private keys, enable it with

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

### Funding a Wallet

Wallets do not have funds on them to start. For Base Sepolia testnet, we provide a `faucet` method to fund your wallet with
testnet ETH. You are allowed one faucet claim per 24-hour window.

```python
# Fund the wallet with a faucet transaction.
faucet_tx = wallet1.faucet()

# Wait for the faucet transaction to complete.
faucet_tx.wait()

print(f"Faucet transaction successfully completed: {faucet_tx}")
```

### Transferring Funds

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

#### Gasless USDC Transfers

To transfer USDC without needing to hold ETH for gas, you can use the `transfer` method with the `gasless` option set to `True`.

```python
# Create a new wallet wallet3 to transfer funds to.
wallet3 = Wallet.create()

print(f"Wallet successfully created: {wallet3}")

# Fund the wallet with USDC with a faucet transaction.
usdc_faucet_tx = wallet1.faucet("usdc")

# Wait for the faucet transaction to complete.
usdc_faucet_tx.wait()

print(f"Faucet transaction successfully completed: {usdc_faucet_tx}")

transfer = wallet1.transfer(0.00001, "usdc", wallet3, gasless=True).wait()
```

By default, gasless transfers are batched with other transfers, and might take longer to submit. If you want to opt out of batching, you can set the `skip_batching` option to `True`, which will submit the transaction immediately.

```python
transfer = wallet1.transfer(0.00001, "usdc", wallet3, gasless=True, skip_batching=True).wait()
```

### Listing Transfers

```python
# Return list of all transfers. This will paginate and fetch all transfers for the address.
list(address.transfers())
```

### Trading Funds

See [Trades](https://docs.cdp.coinbase.com/wallets/docs/trades) for more information.

```python
wallet = Wallet.create("base-mainnet")

print(f"Wallet successfully created: {wallet}")
print(f"Send `base-mainnet` ETH to wallets default address: {wallet.default_address.address_id}")

trade = wallet.trade(0.00001, "eth", "usdc").wait()

print(f"Trade successfully completed: {trade}")
```

### Listing Trades

```python
# Return list of all trades. This will paginate and fetch all trades for the address.
list(address.trades())
```

### Re-Instantiating Wallets

The SDK creates wallets with [Developer-Managed (1-1)](https://docs.cdp.coinbase.com/wallet-api/docs/wallets#developer-managed-wallets) keys by default, which means you are responsible for securely storing the keys required to re-instantiate wallets. The below code walks you through how to export a wallet and store it in a secure location.

```python
# Export the data required to re-instantiate the wallet. The data contains the seed, the ID of the wallet, and the network ID.
data = wallet.export_data()
```

In order to persist the data for the wallet, you will need to implement a store method to store the data export in a secure location. If you do not store the wallet in a secure location you will lose access to the wallet and all of the funds on it.

```python
# You should implement the "store" method to securely persist the data object,
# which is required to re-instantiate the wallet at a later time. For ease of use,
# the data object is converted to a dictionary first.
store(data.to_dict())
```

For convenience during testing, we provide a `save_seed` method that stores the wallet's seed in your local file system. This is an insecure method of storing wallet seeds and should only be used for development purposes.

To encrypt the saved data, set encrypt to `True`. Note that your CDP API key also serves as the encryption key for the data persisted locally. To re-instantiate wallets with encrypted data, ensure that your SDK is configured with the same API key when invoking `save_seed` and `load_seed`.

```python
# Pick a file to which to save your wallet seed.
file_path = "my_seed.json"

# Set encrypt=True to encrypt the wallet seed with your CDP secret API key.
wallet.save_seed(file_path, encrypt=True)

print(f"Seed for wallet {wallet.id} successfully saved to {file_path}.")
```

The below code demonstrates how to re-instantiate a wallet from the data export.

```python
# You should implement the "fetch" method to retrieve the securely persisted data object,
# keyed by the wallet ID.
fetched_data = fetch(wallet.id)

# imported_wallet will be equivalent to wallet.
imported_wallet = Wallet.import_data(fetched_data)
```

To import Wallets that were persisted to your local file system using `save_seed`, use the below code.

```python
# Get the unhydrated wallet from the server.
fetched_wallet = Wallet.fetch(wallet.id)

# You can now load the seed into the wallet from the local file.
# fetched_wallet will be equivalent to imported_wallet.
fetched_wallet.load_seed(file_path)
```

### Creating a Webhook

A webhook is a way to provide other applications with real-time information from the blockchain. When an event occurs on a blockchain address, it can send a POST request to a URL you specify. You can create a webhook to receive notifications about events that occur in your wallet or crypto address, such as when a user makes a transfer.

```python
from cdp.client.models.webhook import WebhookEventType
from cdp.client.models.webhook import WebhookEventFilter

wh1 = Webhook.create(
    notification_uri="https://your-app.com/callback",
    event_type=WebhookEventType.ERC20_TRANSFER,
    event_filters=[WebhookEventFilter(from_address="0x71d4d7d5e9ce0f41e6a68bd3a9b43aa597dc0eb0")],
    network_id="base-mainnet"
)
print(wh1)
```

In the above example, parameter `network_id` is optional, if not provided, the default network is `base-sepolia`. Today we support Base mainnet and Base Sepolia networks.

### Creating a Webhook On A Wallet

A webhook can be attached to an existing wallet to monitor events that occur on the wallet, i.e. all addresses associated with this wallet. A list of supported blockchain events can be found [here](https://docs.cdp.coinbase.com/get-started/docs/webhooks/event-types).

```python
import cdp

wallet1 = Wallet.create()
wh1 = wallet1.create_webhook("https://your-app.com/callback")
print(wh1)
```

## Examples

Examples, demo apps, and further code samples can be found in the [CDP SDK Python Documentation](https://docs.cdp.coinbase.com/cdp-apis/docs/welcome).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for more information.