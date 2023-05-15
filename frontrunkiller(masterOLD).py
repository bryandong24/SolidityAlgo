import time
from web3 import Web3
from solcx import compile_source
import solcx

w3 = Web3(Web3.HTTPProvider("https://ropsten.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161"))

wethaddress="0xc778417E063141139Fce010982780140Aa0cD5Ab"
uniswapaddress="0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
lockaddress="0x801c424Be859d910CD19E5DB90f1d5665f298fA5"
deployer = w3.eth.account.privateKeyToAccount("0xf194e64772a4f14379229fe2fa9b635aa34120ca3dc6bf35e35dbd44e00d72ff")
buyer = w3.eth.account.privateKeyToAccount("0x5301a4681f4225ced659f78a584010d21ba975cb6d9d532d153f7d0fd9950b68")
freezer=w3.eth.account.privateKeyToAccount("0xe1ed8d29578898217104225969243974944221a44511bf9e5c59056f3345035e")

deployernonce=w3.eth.getTransactionCount(deployer.address)
buyernonce=w3.eth.getTransactionCount(buyer.address)
freezernonce=w3.eth.getTransactionCount(freezer.address)

with open('uniswapabi', 'r') as file:
    uniswapabi = file.read()
uniswapinstance =w3.eth.contract(address=uniswapaddress, abi=uniswapabi )
buytoken = uniswapinstance.get_function_by_name('swapExactETHForTokens')

solcx.set_solc_version_pragma("pragma solidity 0.6.12;")
compiled_sol = solcx.compile_files(['TestContract.sol', 'address.sol'])
contract_interface = compiled_sol.pop("TestContract.sol:"+"CakeToken")

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

txn_receipt = w3.eth.get_transaction_receipt(c1)
ContractAddress = txn_receipt['contractAddress']
print(ContractAddress)
deployernonce += 1

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

time.sleep(60)

unsignbuytx = buytoken(0,[wethaddress,ContractAddress],buyer.address,1639642056).buildTransaction({
    'from': buyer.address,
    'nonce': buyernonce,
    'gas': 4712388,
    'value':w3.toWei('0.1','ether'),
    'gasPrice': w3.toWei('20', 'gwei')})
signedbuy=buyer.signTransaction(unsignbuytx)

unsignfreezetx = {
    'from': freezer.address,
    'to': lockaddress,
    'gas': 4712388,
    'value':w3.toWei('0.1','ether'),
    'gasPrice': w3.toWei('25', 'gwei'),
    'nonce':freezernonce }
signedfreeze=freezer.signTransaction(unsignfreezetx)
w3.eth.sendRawTransaction(signedbuy.rawTransaction)
w3.eth.sendRawTransaction(signedfreeze.rawTransaction)