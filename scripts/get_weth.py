from brownie import interface, network, config
from scripts.helpful_script import get_account


def get_weth():
    # Minth WETH by depositing ETH
    # ABI
    # Address
    account = get_account()
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    tx = weth.deposit({"from": account, "value": 0.01 * 10**18})
    tx.wait(1)
    print("Recieved Eth")
    return tx


def main():
    get_weth()
