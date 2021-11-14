from solcx import compile_standard, install_solc
import os
import json
from web3 import Web3
from web3.types import SignedTx
from dotenv import load_dotenv

load_dotenv()

# Reading the simple storage file from the same directory
with open(".\SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()
    # print(simple_storage_file)

# Compile our solidity code
install_solc("0.6.0")
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    }
)

with open("sompiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# Connecting to ganache blockchain simulator
w3 = Web3(
    Web3.HTTPProvider("https://rinkeby.infura.io/v3/687adc831eb04b1e8412e2c269cbfbb7")
)
chain_id = 4
my_address = "0xbaC5d7309EE18C1E41729e9eE72f110143cD796c"
private_key = os.getenv("key")
print("private_key:",private_key)

# Create a contract in python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

# Get the latest transaction
nonce = w3.eth.getTransactionCount(my_address)
# print(nonce)

"""
1. Build a transaction
2. Sign a transaction
3. Send a transaction
"""
transaction = SimpleStorage.constructor().buildTransaction(
    {"chainId": chain_id, "from": my_address, "nonce": nonce}
)

signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key);

#Send the transaction
print("Deploying the contract")
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Deployed!!")

# Working with the contract, you always need 
# Contract ABI
# Contract Address
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
#Transact -> Actually make a state change
print("-----------")
print(simple_storage.functions.retrieve().call())
print("Updating the contract")
store_transaction = simple_storage.functions.store(15).buildTransaction(
    {"chainId": chain_id, "from": my_address, "nonce": nonce+1}
)
signed_store_tx = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key
)
send_store_tx = w3.eth.send_raw_transaction(signed_store_tx.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)
print("Updated!!")
print(simple_storage.functions.retrieve().call())