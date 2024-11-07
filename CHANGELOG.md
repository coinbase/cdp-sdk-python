# CDP Python SDK Changelog

## Unreleased

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
