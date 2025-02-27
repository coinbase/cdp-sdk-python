# CDP Python SDK Changelog

## Unreleased

## [0.20.0] - 2025-02-25

### Added
- Support for Ed25519 API keys.

## [0.19.0] - 2025-02-21

### Added
- Ability to create a SmartWallet and send a user operation.

## [0.18.1] - 2025-02-13

## Fixed

- Bug fix for Wallet.import_wallet() when addresses are not returned in order of their address_index.

## [0.18.0] - 2025-02-12

### Added

- Add `TransactionReceipt` and `TransactionLog` to contract invocation response.


## [0.17.0] - 2025-02-11

### Added

- Add `broadcast_external_transaction` to `Address` class.


## [0.16.0] - 2025-01-28

### Added

- Add E2E test for gasless transfers `Wallet.createTransfer({..., gasless: true})`

### Fixed

- Fixed a bug where non-checksummed asset IDs were throwing an error.

## [0.15.0] - 2025-01-17

### Added

- Add `deploy_contract` method to `WalletAddress` and `Wallet` to deploy an arbitrary contract.

## [0.14.1] - 2025-01-17

### Fixed

- Allow wallet mnemonic seed import to optionally accept `network_id` input argument.

## [0.14.0] - 2025-01-14

### Added

- Add `skip_batching` option to `Wallet.transfer` to allow for lower latency gasless transfers.
- Add `Webhook.delete_webhook` instance method to delete a webhook instance.
- Add `ExternalAddress` derived `Address` class.

### Deprecated

- Deprecate `Webhook.delete` static method in `Webhook` which deletes a webhook by its ID.

## [0.13.0] - 2024-12-19

### Added

- Add support for fetching address reputation
  - Add `reputation` method to `Address` to fetch the reputation of the address.
- Add support for registering, updating, and listing smart contracts that are
  deployed external to CDP.
- Add `network_id` to `WalletData` so that it is saved with the seed data and surfaced via the export function
- Add ability to import external wallets into CDP via a BIP-39 mnemonic phrase, as a 1-of-1 wallet
- Add ability to import WalletData files exported by the NodeJS CDP SDK

### Deprecated

- Deprecate `Wallet.load_seed` method in favor of `Wallet.load_seed_from_file`
- Deprecate `Wallet.save_seed` method in favor of `Wallet.save_seed_to_file`

## [0.12.1] - 2024-12-10

### Added

- Wallet address contract invocation input validation for payable contracts.

## [0.12.0] - 2024-12-06

### Added

- Use Poetry as the dependency manager
- Relax dependency version constraints

## [0.11.0] - 2024-11-27

### Added

- Add support for funding wallets (Alpha feature release)
  - Must reach out to CDP SDK Discord channel to be considered for this feature.
- Added create and update feature for `SmartContractEventActivity` webhook and its related event type filter.

### Fixed

- Fix bug in `Asset.from_model` where passed in asset ID was not used when creating a gwei or wei asset.

## [0.10.4] - 2024-11-25

### Added

- Wallet address key export

## [0.10.4] - 2024-11-25

### Added

- Wallet address key export

## [0.10.3] - 2024-11-07

### Added

- Adds `source` and `source_version` to correlation header for better observability.

### Fixed

- Fix bug in `WalletAddress` `invoke_contract` that failed to properly handle `amount` with type `str`

## [0.10.2] - 2024-11-06

### Added

- Support for reading int24, int56, and uint160 values from smart contracts.

## [0.10.1] - 2024-10-31

### Fixed

- Fix Faucet transaction_link to return the correct transaction link instead of transaction hash.

## [0.10.0] - 2024-10-31

### Changed

- Make faucet transactions async i.e. using `faucet_tx.wait()` to wait for the transaction to be confirmed.
  - This will make the SDK more consistent and make faucet transactions more reliable.

## [0.0.9] - 2024-10-29

### Fixed

- Fixed bug in gasless transfer that blocked sending the full asset balance.

## [0.0.8] - 2024-10-28

### Added

- Include correlation ID in API Errors.

## [0.0.7] - 2024-10-25

### Added

- Include ERC20 and ERC721 token transfer information into transaction content.
- Support for wallet and address webhooks to trigger based on onchain activities.

## [0.0.6] - 2024-10-17

### Added

- Support for read_contract to read from smart contracts

## [0.0.5] - 2024-10-3

### Added

- Support list historical balances and list transactions function for address.

## [0.0.4] - 2024-10-1

### Added

- Contract invocation support.
- Arbitrary message signing support.
- Deploy ERC20, ERC721, and ERC1155 smart contracts.
- Hashing utilities for EIP-191 / EIP-712 data messages.

### Fixed

- Fixed bug in `Wallet` `default_address` property for newly hydrated wallets.

## [0.0.3] - 2024-09-25

### Added

- Initial release of the CDP Python SDK.
