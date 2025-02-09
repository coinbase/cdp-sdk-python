from cdp.cdp import Cdp
from cdp.wallet import Wallet, Transfer, WalletData
import json

Cdp.configure_from_json("~/.apikeys/dev.json", base_path="http://localhost:8002", debugging=True)



wallet = Wallet.import_data(WalletData.from_dict(json.load(open("dev-wallet-test.json"))))

faucet_transaction = wallet.faucet("usdc")
faucet_transaction.wait()

balance = wallet.balance("usdc")

destination_wallet = Wallet.create()

invocation = wallet.invoke_contract(
        contract_address="0x036CbD53842c5426634e7929541eC2318f3dCF7e",
        method="transfer",
        args={"to": destination_wallet.default_address.address_id, "value": "1"}
    )

invocation.wait()

transaction_content = invocation.transaction.content.actual_instance
transaction_receipt = transaction_content.receipt

print(transaction_content)
print(transaction_receipt)