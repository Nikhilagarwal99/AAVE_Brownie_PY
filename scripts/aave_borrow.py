from web3 import Web3
from scripts.get_weth import get_weth
from scripts.helpful_script import get_account
from brownie import accounts, config, network, interface

# COnverting ETH -> WETH
# The ERC20 version of ETH

# 0.1
amount = Web3.toWei(0.01, "ether")


def main():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    if network.show_active() in ["mainnet-fork-dev"]:
        get_weth()
    # ABI
    # Address
    lending_pool = get_lending_pool()
    # Apporve Sending our ERC20 Token
    approve_erc20(amount, lending_pool.address, erc20_address, account)
    # Deposit Function
    print("Deposting")
    tx = lending_pool.deposit(
        erc20_address, amount, account.address, 0, {"from": account}
    )
    tx.wait(1)
    print("Deposited")
    # ..How Much You Can Borrow?
    borrowable_eth, total_debt_eth = get_borrowable_data(lending_pool, account)

    print("Lets Borrow")
    # DAI in terms of ETH
    dai_eth_price = get_asset_price()
    amount_dai_to_borrow = (1 / dai_eth_price) * (borrowable_eth * 0.95)
    # We multiply by 0.95 as a buffer, to make sure that our Health factor is better
    # borrowable_eth -> borrowable_dai*0.95
    print(f"We are going to borrow{amount_dai_to_borrow} DAI")
    # Now we will borrow
    # First Getting the DAI Address
    dai_address = config["networks"][network.show_active()]["dai_token"]
    borrow_tx = lending_pool.borrow(
        dai_address,
        Web3.toWei(amount_dai_to_borrow, "ether"),
        1,
        0,
        account.address,
        {"from": account},
    )
    borrow_tx.wait(1)
    print("We Borrow Some DAI")
    get_borrowable_data(lending_pool, account)
    # REPAYING
    # repay_all(amount, lending_pool, account)
    # print("you just deposited borrowed and repayed with AAVE ,Brownie and Chainlink!!")


def repay_all(amount, lending_pool, account):
    approve_erc20(
        Web3.toWei(amount, "ether"),
        lending_pool,
        config["networks"][network.show_active()]["dai_token"],
        account,
    )
    repay_tx = lending_pool.repay(
        config["networks"][network.show_active()]["dai_token"],
        amount,
        1,
        account.address,
        {"from": account},
    )
    repay_tx.wait(1)
    print("Repayed")


def approve_erc20(amount, spender, erc20_address, account):
    # ABI
    # Addresses
    print("Approving ERC20 token..")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {"from": account})
    tx.wait(1)
    print("Approved")
    return tx


def get_lending_pool():
    # ABI
    # Address
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )
    lending_pool_address = lending_pool_addresses_provider.getLendingPool()
    # ABI
    # Addresses
    lending_pool = interface.ILendingPool(lending_pool_address)
    print(lending_pool)
    return lending_pool


def get_borrowable_data(lending_pool, account):
    (
        total_collateral_eth,
        total_debt_eth,
        available_borrow_eth,
        current_liguidation_threshold,
        ltv,
        health_factor,
    ) = lending_pool.getUserAccountData(account.address)
    available_borrow_eth = Web3.fromWei(available_borrow_eth, "ether")
    total_collateral_eth = Web3.fromWei(total_collateral_eth, "ether")
    total_debt_eth = Web3.fromWei(total_debt_eth, "ether")
    print(f"You have {total_collateral_eth} worth of  ETH depostied in Account")
    print(f"You have {total_debt_eth} worth of ETH Borrowed ")
    print(f"You can borrow {available_borrow_eth} in your ETH Account")
    return (float(available_borrow_eth), float(total_debt_eth))


def get_asset_price():
    # ABI
    # ADDRESS
    dai_eth_price_feed = interface.AggregatorV3Interface(
        config["networks"][network.show_active()]["dai_eth_price_feed"]
    )
    latest_price = Web3.fromWei(dai_eth_price_feed.latestRoundData()[1], "ether")
    print(f"The DAI/ETH price is {latest_price}")
    return float(latest_price)
