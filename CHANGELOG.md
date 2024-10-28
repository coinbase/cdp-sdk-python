# CDP Python SDK Changelog

## Unreleased

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
