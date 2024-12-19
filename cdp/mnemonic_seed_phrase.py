from dataclasses import dataclass


@dataclass
class MnemonicSeedPhrase:
    """Class representing a BIP-39mnemonic seed phrase.

    Used to import external wallets into CDP as 1-of-1 wallets.

    Args:
        mnemonic_phrase (str): A valid BIP-39 mnemonic phrase (12, 15, 18, 21, or 24 words).

    """

    mnemonic_phrase: str
