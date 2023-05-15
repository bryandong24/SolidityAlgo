import time
from web3 import Web3
from solcx import compile_source
import solcx
import json

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
sellernonce = w3.eth.getTransactionCount(seller.address)

with open ('tokenname','r') as file:
    tokenname = file.read()

solcx.set_solc_version_pragma("pragma solidity 0.6.12;")
compiled_sol = solcx.compile_files(['TestContract.sol', 'address.sol'])
contract_interface = compiled_sol.pop("TestContract.sol:"+tokenname)

contract_ = w3.eth.contract(
    abi=contract_interface['abi'],
    bytecode=contract_interface['bin'])
abi = contract_.abi
with open('ContractAddress', 'r') as file:
    ContractAddress = file.read()
contract_instance = w3.eth.contract(address=ContractAddress, abi=abi)
RetrieveETH=contract_instance.get_function_by_name("_RetrieveETH")

with open('uniswapabi', 'r') as file:
    uniswapabi = file.read()
uniswapinstance = w3.eth.contract(address=uniswapaddress, abi=uniswapabi)



unsignfreezetx = {
    'from': freezer.address,
    'to': lockaddress,
    'gas': 210000,
    'value': 1,
    'gasPrice': w3.toWei('5.1', 'gwei'),
    'nonce': freezernonce
}
signedfreeze = freezer.signTransaction(unsignfreezetx)

unsignselltx = RetrieveETH().buildTransaction({
    'from':seller.address,
    'nonce':sellernonce,
    'gas':2100000,
    'gasPrice':w3.toWei('5','gwei')
})
signedsell = seller.signTransaction(unsignselltx)

w3.eth.sendRawTransaction(signedfreeze.rawTransaction)
w3.eth.sendRawTransaction(signedsell.rawTransaction)