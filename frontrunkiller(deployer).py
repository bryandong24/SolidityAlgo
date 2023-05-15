import time
from web3 import Web3
from solcx import compile_source
import json
import solcx
with open('FKconfig(Ropsten).json') as f:
    configf = json.load(f)
config=configf["AVALANCHE"]
w3 = Web3(Web3.HTTPProvider(config["RPC_URL"]))

wethaddress = config["WETH_ADDRESS"]
uniswapaddress = config["ROUTER_ADDRESS"]
lockaddress = config["LOCK_ADDRESS"]
deployer = w3.eth.account.privateKeyToAccount(config["DEPLOYER_KEY"])
buyer = w3.eth.account.privateKeyToAccount(config["BUYER_KEY"])
freezer = w3.eth.account.privateKeyToAccount(config["FREEZER_KEY"])
seller = w3.eth.account.privateKeyToAccount(config["SELLER_KEY"])
deployernonce = w3.eth.getTransactionCount(deployer.address)
buyernonce = w3.eth.getTransactionCount(buyer.address)
freezernonce = w3.eth.getTransactionCount(freezer.address)

with open ('tokenname','r') as file:
    tokenname = file.read()

with open('uniswapabi', 'r') as file:
    uniswapabi = file.read()
uniswapinstance =w3.eth.contract(address=uniswapaddress, abi=uniswapabi )
buytoken = uniswapinstance.get_function_by_name('swapExactETHForTokens')

solcx.set_solc_version_pragma("pragma solidity 0.6.12;")
compiled_sol = solcx.compile_files(['TestContract.sol', 'address.sol'])
contract_interface = compiled_sol.pop("TestContract.sol:"+tokenname)

contract_ = w3.eth.contract(
    abi=contract_interface['abi'],
    bytecode=contract_interface['bin'])
abi = contract_.abi

construct_txn = contract_.constructor().buildTransaction({
    'from': deployer.address,
    'nonce': deployernonce,
    'gas': 4712388,
    'gasPrice': w3.toWei('5', 'gwei')})
signed=deployer.signTransaction(construct_txn)
c1=w3.eth.sendRawTransaction(signed.rawTransaction)

time.sleep(60)
deployernonce+=1
txn_receipt = w3.eth.get_transaction_receipt(c1)
ContractAddress = txn_receipt['contractAddress']
print(ContractAddress)

contract_instance = w3.eth.contract(address=ContractAddress, abi=abi)
addLiquidity=contract_instance.get_function_by_name("addLiquidity")

unsignaddtx = addLiquidity().buildTransaction({
    'from': deployer.address,
    'nonce': deployernonce,
    'gas': 4712388,
    'gasPrice': w3.toWei('5', 'gwei'),
    'value':w3.toWei('0.1','ether')
})
signed=deployer.signTransaction(unsignaddtx)
c1=w3.eth.sendRawTransaction(signed.rawTransaction)

with open ('ContractAddress', 'w') as file:
    file.write(ContractAddress)